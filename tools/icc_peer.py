#!/usr/bin/env python3
"""ICC v0.3: opt-in offline peer key verification; not real-world identity proof."""
import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
import icc_node as node

ENROLL = "ICC-OPT-IN-ENROLL-v1"
SIGNED = "ICC-SIGNED-WITNESS-v1"
TRUST = "ICC-LOCAL-TRUST-v1"
CONSENT = "Opt in to offline research checkpoint comparisons only; no remote control."
ROOT = Path(__file__).resolve().parents[1]


def load(path):
    p = Path(path)
    if p.stat().st_size > 128000:
        raise ValueError("oversized input")
    return json.loads(p.read_text(encoding="utf-8"))


def write(path, payload):
    with open(path, "xb") as f:
        f.write(node.canonical(payload) + b"\n")


def b64(raw):
    return base64.b64encode(raw).decode("ascii")


def un64(value):
    if not isinstance(value, str) or len(value) > 2000:
        raise ValueError("invalid base64")
    return base64.b64decode(value, validate=True)


def good_label(label):
    if not isinstance(label, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,48}", label):
        raise ValueError("invalid public node label")
    return label


def public_pem(key):
    return key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode("ascii")


def get_private(path):
    p = Path(path).resolve()
    if p == ROOT or ROOT in p.parents:
        raise ValueError("private keys may not be stored inside the repository")
    if p.stat().st_mode & 0o077:
        raise ValueError("private key permissions must be owner-only")
    key = serialization.load_pem_private_key(p.read_bytes(), password=None)
    if not isinstance(key, ec.EllipticCurvePrivateKey) or not isinstance(key.curve, ec.SECP256R1):
        raise ValueError("expected P-256 private key")
    return key


def get_public(pem):
    if not isinstance(pem, str) or len(pem) > 2000:
        raise ValueError("invalid public key")
    key = serialization.load_pem_public_key(pem.encode("ascii"))
    if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(key.curve, ec.SECP256R1):
        raise ValueError("expected P-256 public key")
    return key


def sign(key, data):
    return b64(key.sign(node.canonical(data), ec.ECDSA(hashes.BLAKE2s(32))))


def check(pem, data, sig):
    get_public(pem).verify(un64(sig), node.canonical(data), ec.ECDSA(hashes.BLAKE2s(32)))


def keygen(private_path, public_path):
    private_path = Path(private_path).resolve()
    if private_path == ROOT or ROOT in private_path.parents:
        raise ValueError("do not store private keys in a repository")
    key = ec.generate_private_key(ec.SECP256R1())
    secret = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    fd = os.open(private_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(secret)
    with open(public_path, "x", encoding="ascii") as f:
        f.write(public_pem(key))


def enrollment(private_path, label):
    key = get_private(private_path)
    record = {"protocol": ENROLL, "node": good_label(label), "consent": CONSENT, "public_key": public_pem(key)}
    return {**record, "signature": sign(key, record)}


def verify_enrollment(record):
    if not isinstance(record, dict) or set(record) != {"protocol", "node", "consent", "public_key", "signature"}:
        raise ValueError("bad enrollment format")
    if record["protocol"] != ENROLL or record["consent"] != CONSENT:
        raise ValueError("missing consent declaration")
    good_label(record["node"])
    payload = {k: v for k, v in record.items() if k != "signature"}
    check(record["public_key"], payload, record["signature"])
    return payload


def get_registry(path):
    p = Path(path)
    data = load(path) if p.exists() else {"protocol": TRUST, "peers": {}}
    if not isinstance(data, dict) or set(data) != {"protocol", "peers"} or data["protocol"] != TRUST or not isinstance(data["peers"], dict):
        raise ValueError("malformed trust registry")
    for label, pem in data["peers"].items():
        good_label(label)
        get_public(pem)
    return data


def trust(enrollment_file, confirmed_public_key_file, registry_file, output):
    record = load(enrollment_file)
    proof = verify_enrollment(record)
    expected = Path(confirmed_public_key_file).read_text(encoding="ascii")
    get_public(expected)
    if proof["public_key"] != expected:
        raise ValueError("public key does not match the separately confirmed key")
    data = get_registry(registry_file)
    peers = data["peers"]
    if proof["node"] in peers or expected in peers.values():
        raise ValueError("duplicate node or key")
    peers[proof["node"]] = expected
    write(output, data)


def signed_witness(private_path, node_name, checkpoint_file):
    key = get_private(private_path)
    cp = load(checkpoint_file)
    state = node.decode_checkpoint(cp)
    payload = {"protocol": SIGNED, "node": good_label(node_name), "checkpoint": cp, "step": state["step"]}
    return {**payload, "signature": sign(key, payload)}


def verify_signed(record, registry):
    if not isinstance(record, dict) or set(record) != {"protocol", "node", "checkpoint", "step", "signature"}:
        raise ValueError("invalid signed witness")
    if record["protocol"] != SIGNED:
        raise ValueError("bad signed witness protocol")
    name = good_label(record["node"])
    if name not in registry["peers"]:
        raise ValueError("untrusted node label")
    payload = {k: v for k, v in record.items() if k != "signature"}
    check(registry["peers"][name], payload, record["signature"])
    state = node.decode_checkpoint(record["checkpoint"])
    if type(record["step"]) is not int or record["step"] != state["step"]:
        raise ValueError("witness state-step mismatch")
    return payload


def main():
    p = argparse.ArgumentParser(description=__doc__)
    cmds = p.add_subparsers(dest="cmd", required=True)
    k = cmds.add_parser("keygen")
    k.add_argument("--private", required=True)
    k.add_argument("--public", required=True)
    e = cmds.add_parser("enroll")
    e.add_argument("--private", required=True)
    e.add_argument("--node", required=True)
    e.add_argument("--output", required=True)
    t = cmds.add_parser("trust")
    t.add_argument("--enrollment", required=True)
    t.add_argument("--expected-public-key", required=True)
    t.add_argument("--registry", required=True)
    t.add_argument("--output", required=True)
    s = cmds.add_parser("sign")
    s.add_argument("--private", required=True)
    s.add_argument("--node", required=True)
    s.add_argument("--checkpoint", required=True)
    s.add_argument("--output", required=True)
    for action in ("verify", "compare", "recover"):
        q = cmds.add_parser(action)
        q.add_argument("--registry", required=True)
        if action == "compare":
            q.add_argument("--left", required=True)
            q.add_argument("--right", required=True)
        else:
            q.add_argument("--witness", required=True)
        if action == "recover":
            q.add_argument("--output", required=True)
    a = p.parse_args()
    if a.cmd == "keygen":
        keygen(a.private, a.public)
        print(json.dumps({"status": "KEY_CREATED_LOCALLY", "private_key_not_exported": True}))
    elif a.cmd == "enroll":
        write(a.output, enrollment(a.private, a.node))
    elif a.cmd == "trust":
        trust(a.enrollment, a.expected_public_key, a.registry, a.output)
        print(json.dumps({"status": "LOCAL_TRUST_UPDATED", "no_global_enrollment": True}))
    elif a.cmd == "sign":
        write(a.output, signed_witness(a.private, a.node, a.checkpoint))
    elif a.cmd == "verify":
        proof = verify_signed(load(a.witness), get_registry(a.registry))
        print(json.dumps({"status": "SIGNATURE_VERIFIED", "node": proof["node"], "step": proof["step"], "real_world_identity_verified": False}))
    elif a.cmd == "compare":
        r = get_registry(a.registry)
        left, right = verify_signed(load(a.left), r), verify_signed(load(a.right), r)
        if left["node"] == right["node"] or left["checkpoint"] != right["checkpoint"]:
            raise ValueError("distinct enrolled signing keys did not agree")
        print(json.dumps({"status": "KEY_AUTHENTICATED_CONSISTENT", "nodes": [left["node"], right["node"]], "step": left["step"], "external_identity_verified": False, "global_control": False, "medical_effect_proven": False}))
    elif a.cmd == "recover":
        proof = verify_signed(load(a.witness), get_registry(a.registry))
        write(a.output, proof["checkpoint"])
        print(json.dumps({"status": "SIGNED_CHECKPOINT_RECOVERED", "step": proof["step"], "eternal_storage_proven": False}))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, InvalidSignature) as exc:
        print(json.dumps({"status": "DENY", "reason": str(exc)}), file=sys.stderr)
        sys.exit(1)
