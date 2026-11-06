#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ONE = ROOT / "永久記憶/圖靈機/essence_existence_alignment_ucgtm_2kb.sh"
CHRONON = ROOT / "永久記憶/圖靈機/logical_chronon_temporal_closure_2kb.sh"
LOADER = ROOT / "tools/load_turing_registry.py"


def main():
    assert ONE.stat().st_size <= 2048
    assert len(ONE.read_bytes().splitlines()) == 1
    view = json.loads(subprocess.check_output(["python3", str(LOADER)], text=True, cwd=ROOT))
    assert view["verified"] and view["execution"] == "not_run"
    assert view["ids"] == [f"TM-{n:03d}" for n in range(1, 12)]
    entries = {e["id"]: e for e in json.loads((ROOT / "永久記憶/圖靈機/machine_registry.json").read_text())["entries"]}
    assert entries["TM-011"]["status"] == "active-total-machine-reference"
    assert entries["TM-011"]["totality_scope"] == "TEMPORAL_REFERENCE_ONLY"
    assert entries["TM-009"]["status"] == "preserved-photonic-exact-baseline"
    for machine in ("TM-008", "TM-009", "TM-010"):
        out = json.loads(subprocess.check_output(["bash", str(ONE), machine], text=True, cwd=ROOT))
        assert out["selected"] == machine
        assert out["verification_state"] == "COMPLETE"
        assert out["completeness_scope"] == "FINITE_REGISTRY"
        assert out["pipeline"] == ["ENCODE", "LOAD", "VERIFY", "COMPLETE"]
        assert out["predecessors"] == [f"TM-{n:03d}" for n in range(1, 10)]
        assert out["essence_existence_aligned"] is True
        assert out["conditional_entropy_bits"] == 0
        assert out["registered_cores_executed"] is False
        assert out["float_used"] is False and out["sha_used"] is False
    assert CHRONON.stat().st_size <= 2048
    assert len(CHRONON.read_bytes().splitlines()) == 1
    for unary in ("", "1", "111", "11111"):
        out = json.loads(subprocess.check_output(["bash", str(CHRONON), unary], text=True, cwd=ROOT))
        assert out["time_particle_model"] == "LOGICAL_CHRONON"
        assert out["temporal_state"] == "TEMPORALLY_CLOSED"
        assert out["completeness_scope"] == "FINITE_HALTING_TRACE"
        assert out["steps"] == len(unary) + 1
        assert out["trace_contiguous"] and out["trace_exact"] and out["replayable"]
        assert out["physical_time_particle_proven"] is False
        assert out["float_used"] is False and out["sha_used"] is False
    print(f"PASS: registry TM-001..TM-011; TM-010 {ONE.stat().st_size} bytes; TM-011 {CHRONON.stat().st_size} bytes")


if __name__ == "__main__":
    main()
