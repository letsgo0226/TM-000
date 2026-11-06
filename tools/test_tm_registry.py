#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ONE = ROOT / "永久記憶/圖靈機/essence_existence_alignment_ucgtm_2kb.sh"
LOADER = ROOT / "tools/load_turing_registry.py"


def main():
    assert ONE.stat().st_size <= 2048
    assert len(ONE.read_bytes().splitlines()) == 1
    view = json.loads(subprocess.check_output(["python3", str(LOADER)], text=True, cwd=ROOT))
    assert view["verified"] and view["execution"] == "not_run"
    assert view["ids"] == [f"TM-{n:03d}" for n in range(1, 11)]
    for machine in ("TM-008", "TM-009", "TM-010"):
        out = json.loads(subprocess.check_output(["bash", str(ONE), machine], text=True, cwd=ROOT))
        assert out["selected"] == machine
        assert out["predecessors"] == [f"TM-{n:03d}" for n in range(1, 10)]
        assert out["essence_existence_aligned"] is True
        assert out["conditional_entropy_bits"] == 0
        assert out["registered_cores_executed"] is False
        assert out["float_used"] is False and out["sha_used"] is False
    print(f"PASS: registry TM-001..TM-010; TM-008/009/010 exact load; {ONE.stat().st_size} bytes")


if __name__ == "__main__":
    main()
