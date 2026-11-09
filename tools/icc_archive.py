#!/usr/bin/env python3
"""ICC v0.4 offline signed-checkpoint backups; no remote or autonomous actions.

Only a trusted signer authenticates the contents; merely copying to two folders
is NOT evidence of independent geographical/administrative storage.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import icc_node as node
import icc_peer as peer
from cryptography.exceptions import InvalidSignature

FORMAT = "ICC-OFFLINE-ARCHIVE-v1"
FILENAME = "icc-backup.json"
LIMIT = 128000


def canonical_file(path):
    p = Path(path)
    if p.stat().st_size > LIMIT:
        raise ValueError("oversize archive")
    raw = p.read_bytes()
    value = json.loads(raw)
    if raw != node.canonical(value) + b"\n":
        raise ValueError("archive must have canonical JSON encoding")
    return value


def bundle_for(witness, registry):
    payload = peer.verify_signed(witness, registry)
    cp = payload["checkpoint"]
    state = node.decode_checkpoint(cp)
    return {
        "format": FORMAT,
        "signed_witness": witness,
        "source_g257_hex": state["source_g257_hex"],
        "self_healing": False,
        "medical_effect_proven": False,
        "backup_is_geographically_independent": False,
    }


def validate_bundle(bundle, registry):
    if not isinstance(bundle, dict) or set(bundle) != {
        "format", "signed_witness", "source_g257_hex", "self_healing",
        "medical_effect_proven", "backup_is_geographically_independent",
    }:
        raise ValueError("unexpected backup schema")
    if bundle["format"] != FORMAT or any(bundle[x] is not False for x in (
        "self_healing", "medical_effect_proven", "backup_is_geographically_independent"
    )):
        raise ValueError("unsupported backup claims")
    expected = bundle_for(bundle["signed_witness"], registry)
    if expected != bundle:
        raise ValueError("signed source does not match archive")
    return bundle["signed_witness"]["checkpoint"]


def create(witness_path, registry_path, destinations):
    if len(destinations) < 2:
        raise ValueError("at least two explicitly named destinations are required")
    registry = peer.get_registry(registry_path)
    bundle = bundle_for(peer.load(witness_path), registry)
    files = [Path(directory).resolve(strict=True) / FILENAME for directory in destinations]
    if any(not file.parent.is_dir() for file in files) or len(set(file.parent for file in files)) != len(files):
        raise ValueError("archive destinations must be different existing directories")
    if any(file.exists() or file.is_symlink() for file in files):
        raise ValueError("refuse to overwrite existing backup")
    raw = node.canonical(bundle) + b"\n"
    for file in files:
        fd = os.open(file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
    return {"status": "LOCAL_COPIES_WRITTEN", "copies": len(files), "bytes_each": len(raw), "geographic_independence_proven": False}


def examine(paths, registry_path):
    if not paths or len(set(Path(p).resolve() for p in paths)) != len(paths):
        raise ValueError("supply distinct explicit archive paths")
    registry = peer.get_registry(registry_path)
    accepted = []
    rejected = []
    valid_inodes = set()
    for path in paths:
        try:
            cp = validate_bundle(canonical_file(path), registry)
            stat = Path(path).stat()
            inode = (stat.st_dev, stat.st_ino)
            if inode in valid_inodes:
                raise ValueError("hard-linked duplicate archive is not a separate copy")
            valid_inodes.add(inode)
            accepted.append((path, cp))
        except (OSError, UnicodeError, ValueError, TypeError, KeyError, InvalidSignature, json.JSONDecodeError):
            rejected.append(str(path))
    if not accepted:
        raise ValueError("no valid trusted signed backups")
    if any(cp != accepted[0][1] for _, cp in accepted[1:]):
        raise ValueError("conflicting valid signed states; explicit human adjudication required")
    state = node.decode_checkpoint(accepted[0][1])
    return accepted[0][1], {"accepted": len(accepted), "rejected": len(rejected), "step": state["step"], "geographic_independence_proven": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    cmds = parser.add_subparsers(dest="command", required=True)
    put = cmds.add_parser("create")
    put.add_argument("--witness", required=True)
    put.add_argument("--registry", required=True)
    put.add_argument("--dest", action="append", required=True, help="an existing directory, repeat twice or more")
    for name in ("audit", "recover"):
        sub = cmds.add_parser(name)
        sub.add_argument("--registry", required=True)
        sub.add_argument("--source", action="append", required=True, help="backup file, repeat for multiple copies")
        sub.add_argument("--min-valid", type=int, default=1)
        if name == "recover":
            sub.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "create":
        result = create(args.witness, args.registry, args.dest)
    else:
        if not 1 <= args.min_valid <= len(args.source):
            raise ValueError("invalid min-valid setting")
        checkpoint, info = examine(args.source, args.registry)
        if info["accepted"] < args.min_valid:
            raise ValueError("verified replica threshold not met")
        if args.command == "recover":
            peer.write(args.output, checkpoint)
        result = {
            "status": ("RECOVERED" if args.command == "recover" else "AUDITED") + ("_DEGRADED" if info["rejected"] else ""),
            **info,
            "key_authenticity_verified": True,
            "physical_independence_verified": False,
            "medical_effect_proven": False,
        }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, InvalidSignature, json.JSONDecodeError) as error:
        print(json.dumps({"status": "DENY", "reason": str(error)}), file=sys.stderr)
        sys.exit(1)
