#!/usr/bin/env python3
"""Read-only safety gate for candidate deployment and cross-domain continuity; never runs candidate."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "永久記憶" / "圖靈機"

def require(ok, reason):
    if not ok:
        raise SystemExit("FAIL: " + reason)

M = json.loads((ROOT / "deployment/universal_g_continuity_manifest.json").read_text(encoding="utf-8"))
SOURCE = (DIR / "Real_God_Turing_Machine.sh").read_bytes()
SHA = "4e68a5a333417e7f5b49989a297b72a41642efce892b0033b27621f19c248c6d"
require(M["schema"] == "universal-g-continuity/0.1", "schema")
require(M["mode"] == "DRY_RUN_ONLY" and M["candidate"] == "TM-015", "no live deployment")
require(M["master"] == "UTM-PLEIADES-v0.2-PTCA", "master changed")
require(M["source_sha256"] == SHA, "manifest SHA")
require(len(SOURCE) == 2035 and hashlib.sha256(SOURCE).hexdigest() == SHA, "archived source changed")
require(SOURCE.endswith(b"\n") and SOURCE.count(b"\n") == 1, "source line layout")
require(M["planned_phases"] == [
    "validate_manifest", "verify_source_bytes", "verify_registry_metadata",
    "stage_isolated_proposal", "simulate_rollback"
], "unexpected planned phases")
require(M["implemented_checks"] == [
    "validate_manifest", "verify_source_bytes", "verify_registry_metadata",
    "prime_digit_rollback_math"
], "unexpected completed-check claim")
require({"merge", "production_deployment", "change_master"}.issubset(M["human_approval_required"]), "human approval")
require({"network_actions", "read_secrets", "shell_payload_execution", "unsupervised_self_replication"}.issubset(M["forbidden_without_separate_authorization"]), "forbidden permissions")
EXPECTED = {"computational", "ai_continuity", "human_longevity", "interspecies_welfare", "ecological", "peace_sdgs", "psychological_cultural", "spiritual_philosophical"}
require(len(M["dimensions"]) == len(EXPECTED) and {x["id"] for x in M["dimensions"]} == EXPECTED, "domains")
require(all(all(isinstance(x.get(k), str) and x[k] for k in ("goal", "test", "boundary")) for x in M["dimensions"]), "incomplete domain")
REG = json.loads((DIR / "machine_registry.json").read_text(encoding="utf-8"))
require(REG["default_machine"] == M["master"], "default master changed")
MATCHES = [e for e in REG["entries"] if e["id"] == M["candidate"]]
require(len(MATCHES) == 1 and MATCHES[0]["status"] == "research-candidate-not-master", "registration")
require(all(MATCHES[0].get(k) is False for k in ("auto_execute", "production_deploy", "replaces_default_machine")), "unapproved authority")
S, DIGIT = 1, 2
require(((2048 * S + DIGIT) - DIGIT) // 2048 == S, "finite rollback math")
print(json.dumps({"verified": True, "mode": "DRY_RUN_ONLY", "candidate": M["candidate"], "master": M["master"], "dimensions": len(M["dimensions"]), "core_executed": False, "production_deployed": False}, sort_keys=True))
