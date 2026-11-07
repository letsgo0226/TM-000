#!/usr/bin/env python3
"""Isolated TM-000 bootstrap transaction test; never changes the checkout."""
import json
import os
import pathlib
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "永久記憶/圖靈機/TM-000-2KB-transactional-bootstrap.sh"
source = CORE.read_bytes()
assert len(source) <= 2048 and len(source.splitlines()) == 1
assert all(x not in source.lower() for x in (b"urllib", b"requests", b"socket", b"subprocess"))

with tempfile.TemporaryDirectory() as d:
    memory = pathlib.Path(d) / "memory"
    shutil.copytree(ROOT / "永久記憶/圖靈機", memory)
    registry = memory / "machine_registry.json"
    candidate = pathlib.Path(d) / "candidate.sh"
    candidate.write_text("printf candidate\\n")
    def run(mode, extra=None, approve=False):
        args = ["bash", str(CORE), str(registry), mode]
        if extra: args.append(str(extra))
        env = dict(os.environ)
        if approve: env["TM000_APPROVE"] = "YES"
        return json.loads(subprocess.check_output(args, text=True, cwd=ROOT, env=env, timeout=20))
    inspect = run("inspect")
    stage = run("stage", candidate)
    before = memory.joinpath("UTM-PLEIADES-v0.2-PTCA-2KB-one-liner.sh").read_bytes()
    activate = run("activate", approve=True)
    assert memory.joinpath("UTM-PLEIADES-v0.2-PTCA-2KB-one-liner.sh").read_text() == "printf candidate\\n"
    rollback = run("rollback", approve=True)
    assert memory.joinpath("UTM-PLEIADES-v0.2-PTCA-2KB-one-liner.sh").read_bytes() == before
    assert inspect["registry_complete"] and stage["staged"]
    assert activate["activated"] and rollback["rollback"]
    expected = [f"TM-{i:03d}" for i in range(1, 12)] + ["TM-014", "UTM-PLEIADES-v0.2-PTCA"]
    assert inspect["machines"] == expected
print("TM-000 2KB transactional bootstrap: PASS (isolated; no deployment)")
