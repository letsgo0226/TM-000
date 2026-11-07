#!/usr/bin/env python3
"""Read-only PTCA safety gate. No deployment, secrets, or remote execution."""
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "永久記憶/圖靈機/UTM-PLEIADES-v0.2-PTCA-2KB-one-liner.sh"
REGISTRY = ROOT / "永久記憶/圖靈機/machine_registry.json"
source = CORE.read_text()
assert len(source.encode()) <= 2048
assert len(source.splitlines()) == 1
assert all(x not in source.lower() for x in ("sha", "hashlib", "base64", "zlib"))
registry = json.loads(REGISTRY.read_text())
entries = {x["id"]: x for x in registry["entries"]}
assert registry["default_machine"] == "UTM-PLEIADES-v0.2-PTCA"
assert CORE.name in entries[registry["default_machine"]]["cores"]

def invoke(argument=None, bound=20):
    args = ["bash", str(CORE)]
    if argument is not None:
        args += [argument, str(bound)]
    return json.loads(subprocess.check_output(args, text=True, cwd=ROOT, timeout=15))

default = invoke()
assert default["status"] == "HALTED" and default["steps"] == 3
assert default["roundtrip"] is True and default["integrity"] == "G257_ROUNDTRIP"
assert default["continuity"] == "functional"
assert default["tamper_resistance"] is False and default["physical_portal"] is False
loop = invoke('{"rules":[["q","_","q","_",0]],"start":"q","halt":["H"]}', 10)
assert loop["status"] == "PROVEN_NONHALTING" and loop["steps"] == 1
first = invoke('{"rules":[["q","_","q","1",1]],"start":"q","halt":["H"]}', 2)
resumed = invoke("G:" + first["singularity"], 3)
assert first["steps"] == 2 and resumed["steps"] == 5
print("UTM-PLEIADES PTCA safety gate: PASS (no deployment)")
