#!/usr/bin/env python3
"""Read-only loader for the permanent-memory Turing-machine registry."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "永久記憶/圖靈機"
REGISTRY = MEMORY / "machine_registry.json"


def safe_file(relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe registry path: {relative}")
    resolved = (MEMORY / path).resolve()
    if MEMORY.resolve() not in resolved.parents:
        raise ValueError(f"registry path escapes permanent memory: {relative}")
    if not resolved.is_file():
        raise FileNotFoundError(relative)
    return resolved


def load():
    raw = REGISTRY.read_bytes()
    registry = json.loads(raw)
    entries = registry["entries"]
    ids = [entry["id"] for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate registry ID")
    for entry in entries:
        record = safe_file(entry["record"])
        if entry["id"] not in record.read_text(encoding="utf-8"):
            raise ValueError(f"record does not identify {entry['id']}")
        for core in entry.get("cores", []):
            safe_file(core)
    if bytes.fromhex(raw.hex()) != raw:
        raise ValueError("registry byte roundtrip failed")
    return registry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--select", metavar="TM-ID")
    parser.add_argument("--run-tm010", action="store_true",
                        help="explicitly run only TM-010's read-only verifier")
    args = parser.parse_args()
    registry = load()
    entries = registry["entries"]
    selection = args.select or registry.get("default_machine")\n    selected = next((e for e in entries if e["id"] == selection), None) if selection else None
    if args.select and selected is None:
        parser.error("unknown TM-ID")
    if args.run_tm010:
        core = safe_file("essence_existence_alignment_ucgtm_2kb.sh")
        subprocess.run(["bash", str(core), args.select or "TM-010"], cwd=ROOT,
                       check=True, timeout=30)
        return
    print(json.dumps({"verified": True, "execution": "not_run",
                      "ids": [e["id"] for e in entries], "selected": selected},
                     ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
