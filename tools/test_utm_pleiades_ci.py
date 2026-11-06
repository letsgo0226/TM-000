#!/usr/bin/env python3
"""Read-only safety gate. Never deploys, executes remote code, or uses secrets."""
import json
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "永久記憶/圖靈機/UTM-PLEIADES-v0.2-plaintext-one-liner.sh"
REGISTRY = ROOT / "永久記憶/圖靈機/machine_registry.json"
source = CORE.read_text()
assert len(source.encode()) <= 2048, "2 KB limit exceeded"
assert len(source.splitlines()) == 1, "core must be one physical line"
assert "base64" not in source and "zlib" not in source, "not plaintext"
registry = json.loads(REGISTRY.read_text())
entries = {x["id"]: x for x in registry["entries"]}
assert "UTM-PLEIADES-v0.2" in entries
assert CORE.name in entries["UTM-PLEIADES-v0.2"]["cores"]

def invoke(machine=None, bound=20):
    args = ["bash", str(CORE)]
    with tempfile.TemporaryDirectory() as directory:
        if machine is not None:
            path = pathlib.Path(directory) / "machine.json"
            path.write_text(json.dumps(machine))
            args += [str(path), str(bound)]
        p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=15, check=True)
        return json.loads(p.stdout)

default = invoke()
assert default["status"] == "HALTED" and default["steps"] == 4
assert len(default["chronon_codes"]) == 4 and default["godel_roundtrip"] is True
loop = {"start":"q","halt":["H"],"input":"","rules":[["q","_","q","_",0]]}
cycle = invoke(loop)
assert cycle["status"] == "PROVEN_NONHALTING" and cycle["cycle"] == [0,1]
unknown = invoke({"start":"q","halt":["H"],"input":"111","rules":[["q","1","q","X",1]]}, 1)
assert unknown["status"] == "UNKNOWN" and unknown["steps"] == 1
invalid = invoke({"start":"q","halt":["H"],"rules":[["q","_","q","_",2]]})
assert invalid["status"] == "INVALID"
print("UTM-PLEIADES CI safety gate: PASS (no deployment)")
