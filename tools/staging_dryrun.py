#!/usr/bin/env python3
"""Local isolated staging dry run: no network, secrets, or production writes."""
import hashlib
import json
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[1]
core = root / "永久記憶/圖靈機/UTM-PLEIADES-v0.2-plaintext-one-liner.sh"
with tempfile.TemporaryDirectory(prefix="pleiades-staging-") as tmp:
    work = pathlib.Path(tmp)
    machine = {"start":"q","halt":["H"],"input":"111","rules":[["q","1","q","X",1],["q","_","H","_",0]]}
    config = work / "machine.json"
    config.write_text(json.dumps(machine))
    def execute():
        p = subprocess.run(["bash",str(core),str(config),"20"],cwd=work,text=True,capture_output=True,check=True,timeout=15)
        return json.loads(p.stdout)
    first = execute()
    second = execute()
    assert first == second, "non-deterministic staging result"
    assert first["status"] == "HALTED" and first["steps"] == 4
    assert first["physical_chronon_proven"] is False
    assert first["godel_roundtrip"] is True
    assert len(first["chronon_codes"]) == 4
    artifact = work / "result.json"
    artifact.write_text(json.dumps(first,sort_keys=True,separators=(",",":")))
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() == digest
    # Simulated rollback: delete only a temporary staging artifact.
    artifact.unlink()
    assert not artifact.exists()
    print(json.dumps({"staging":"PASS","health":"PASS","determinism":"PASS","rollback":"SIMULATED","artifact_sha256":digest,"production_deployed":False}))
