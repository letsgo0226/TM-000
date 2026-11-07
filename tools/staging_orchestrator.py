#!/usr/bin/env python3
"""TM-000 offline, read-only staging planner. No subprocess or deployment authority."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    "UTM-PLEIADES-v0.2-PTCA": "永久記憶/圖靈機/UTM-PLEIADES-v0.2-PTCA-2KB-one-liner.sh",
    "LMN-AI-CONTINUITY-CAPSULE": "capsule/AI-Continuity-Capsule.sh",
}

def plan(machine: str) -> dict:
    if machine not in ALLOWED:
        raise ValueError("machine not allowlisted")
    path = (ROOT / ALLOWED[machine]).resolve(strict=True)
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError("path escapes repository")
    if not path.is_file():
        raise ValueError("not a regular file")
    payload = path.read_bytes()
    return {
        "schema_version": 1,
        "mode": "STAGING_DRY_RUN_ONLY",
        "machine": machine,
        "source": ALLOWED[machine],
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "executed": False,
        "production_authorized": False,
        "deployment_actions": [],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--machine", choices=sorted(ALLOWED), required=True)
    args = parser.parse_args()
    print(json.dumps(plan(args.machine), sort_keys=True))

if __name__ == "__main__":
    main()
