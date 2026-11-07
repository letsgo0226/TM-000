#!/usr/bin/env python3
import json
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "capsule/AI-Continuity-Capsule-v0.1-2KB.sh"
source = TOOL.read_bytes()
assert len(source) <= 2048 and len(source.splitlines()) == 1
with tempfile.TemporaryDirectory() as d:
    capsule = pathlib.Path(d) / "capsule.json"
    with capsule.open("w") as out:
        subprocess.run(["bash", str(TOOL), "pack", str(ROOT)], stdout=out, check=True, timeout=30)
    data = json.loads(capsule.read_text())
    assert data["schema"] == "AI-Continuity-Capsule/1"
    assert len(data["payload"]) == 3
    assert data["checkpoint"]["type"] == "FUNCTIONAL_CONTINUITY"
    assert data["research_memory"]["status"] == "HYPOTHESIS"
    assert data["evidence_ledger"] == []
    assert data["policy"]["human_authorization"] is True
    assert data["policy"]["auto_merge"] is False
    assert not any(data["claims"].values())
    verified = json.loads(subprocess.check_output(["bash", str(TOOL), "verify", str(capsule)], text=True, timeout=30))
    assert verified["verified"] and verified["executed"] is False
print("AI-Continuity-Capsule v0.1: PASS (pack/verify; no execution)")
