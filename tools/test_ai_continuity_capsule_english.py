#!/usr/bin/env python3
import json
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "capsule/AI-Continuity-Capsule-v0.2-English-2KB.sh"
source = TOOL.read_bytes()
assert len(source) <= 2048 and len(source.splitlines()) == 1
assert source.isascii()
tm000 = ROOT / "永久記憶/圖靈機/TM-000-2KB-transactional-bootstrap.sh"
utm = ROOT / "永久記憶/圖靈機/UTM-PLEIADES-v0.2-PTCA-2KB-one-liner.sh"
registry = ROOT / "永久記憶/圖靈機/machine_registry.json"
with tempfile.TemporaryDirectory() as d:
    capsule = pathlib.Path(d) / "capsule.json"
    with capsule.open("w") as out:
        subprocess.run(["bash", str(TOOL), "pack", str(tm000), str(utm), str(registry)], stdout=out, check=True, timeout=30)
    raw = capsule.read_bytes()
    assert raw.isascii()
    data = json.loads(raw)
    assert data["schema"] == "AI-Continuity-Capsule/2-English"
    assert data["language"] == "en"
    assert list(data["payload"]) == ["tm000_bootstrap.sh", "utm_pleiades_ptca.sh", "machine_registry.json"]
    assert data["research_memory"]["status"] == "HYPOTHESIS"
    assert data["evidence_ledger"] == []
    assert not any(data["unsupported_claims"].values())
    result = json.loads(subprocess.check_output(["bash", str(TOOL), "verify", str(capsule)], text=True, timeout=30))
    assert result["verified"] and result["payload_executed"] is False
print("AI-Continuity-Capsule v0.2 English: PASS")
