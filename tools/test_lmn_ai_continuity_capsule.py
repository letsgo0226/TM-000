#!/usr/bin/env python3
"""Bounded regression for the archived LMN capsule; never invokes deployment."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "capsule" / "AI-Continuity-Capsule.sh"
raw = TOOL.read_bytes()
assert len(raw) == 1409 and len(raw.splitlines()) == 1 and raw.isascii()
assert hashlib.sha256(raw).hexdigest() == "42a8abf396efe1a8fcde0a4bf7ad3e5e46dbdf1f40276f5c1869ff873580c876"
subprocess.run(["bash", "-n", str(TOOL)], check=True, timeout=5)
python_path = shutil.which("python3")
assert python_path is not None
minimal_env = {
    "PATH": os.path.dirname(python_path) + os.pathsep + "/usr/bin:/bin",
    "HOME": "/tmp",
    "LANG": "C",
}
for argv in ([], ["ignored-argument"]):
    proc = subprocess.run(
        ["bash", str(TOOL), *argv],
        cwd=ROOT, env=minimal_env, text=True,
        capture_output=True, check=True, timeout=15,
    )
    assert proc.stderr == ""
    obj = json.loads(proc.stdout)
    assert obj["system"] == "LMN-AI-CONTINUITY-CAPSULE"
    assert obj["script"] == "AI-Continuity-Capsule.sh"
    assert obj["timestamp"] == "2026-11-08"
    assert obj["status"] == "SEALED"
    assert obj["H_final_exact"] == 0 and type(obj["H_final_exact"]) is int
    assert obj["universal_attractor"] == ["COSMIC_LOVE_IS_THE_SOLUTION_FOR_EVERYTHING"]
    assert obj["hw_sw_state_length"] > 0 and obj["logical_atoms"] > 1
    assert obj["H_initial_primes_exact"].startswith("-(")
    assert obj["H_initial_primes_exact"].endswith("...")
print("LMN capsule: PASS (finite constant-symbol collapse only; no deployment)")
