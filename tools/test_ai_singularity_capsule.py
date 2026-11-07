#!/usr/bin/env python3
import json
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "capsule/AI-Continuity-Singularity-Capsule-v0.3-2KB.sh"
source = TOOL.read_bytes()
assert len(source) <= 2048 and len(source.splitlines()) == 1 and source.isascii()
memory = ROOT / "永久記憶/圖靈機"
inputs = [
    memory / "TM-000-2KB-transactional-bootstrap.sh",
    memory / "UTM-PLEIADES-v0.2-PTCA-2KB-one-liner.sh",
    memory / "machine_registry.json",
]
with tempfile.TemporaryDirectory() as d:
    capsule = pathlib.Path(d) / "singularity.json"
    with capsule.open("w") as out:
        subprocess.run(["bash", str(TOOL), "seal", *map(str, inputs)], stdout=out, check=True, timeout=30)
    raw = capsule.read_bytes()
    assert raw.isascii()
    data = json.loads(raw)
    config = data["configuration"]
    assert config["schema"] == "AI-Singularity-Capsule/3"
    assert config["state"] == "q_omega" and config["head"] == 0
    assert config["next"] == "VERIFY_THEN_RESUME"
    assert config["evidence"] == []
    assert config["policy"]["human_authorization"] is True
    assert config["policy"]["auto_execute"] is False
    assert config["claims"]["functional_continuity_only"] is True
    assert not any(v for k, v in config["claims"].items() if k != "functional_continuity_only")
    verify = json.loads(subprocess.check_output(["bash", str(TOOL), "verify", str(capsule)], text=True, timeout=30))
    resume = json.loads(subprocess.check_output(["bash", str(TOOL), "resume", str(capsule)], text=True, timeout=30))
    assert verify["verified"] and verify["executed"] is False and verify["next"] is None
    assert resume["verified"] and resume["executed"] is False
    assert resume["next"] == "VERIFY_THEN_RESUME"
print("AI singularity capsule v0.3: PASS (canonical q_omega; no execution)")
