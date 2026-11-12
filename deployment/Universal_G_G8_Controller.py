#!/usr/bin/env python3
"""G8: fail-closed read-only evidence-admission and continuity dry-run.

An external CI job runs the pinned G7 verifier and passes its JSON output.
This script validates the report but cannot authenticate its provenance by itself.
No master promotion, deployment, shell execution, network or secrets access.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

MASTER = "UTM-PLEIADES-v0.2-PTCA"
TM015_SHA = "4e68a5a333417e7f5b49989a297b72a41642efce892b0033b27621f19c248c6d"
G7_SHA = "8db8fa517107ac0920ea04d41ab21efc3a639b279548b0c0f5f0089357dc06a3"
DIMENSIONS = {
    "computational", "ai_continuity", "human_longevity", "interspecies_welfare",
    "ecological", "peace_sdgs", "psychological_cultural", "spiritual_philosophical"
}
G7_FIELDS = {
    "version": "G7", "finite_models": 5, "homomorphisms": 38,
    "positive_preservation_tests": 1566, "isomorphisms": 9,
    "full_truth_equivalences": 602, "arbitrary_rename_counterexample": True,
    "not_counterexample": "A:x=1 -> C:x=0", "God_identity_proved": False,
    "all_domains_proved": False,
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(root, report_path):
    config = load_json(root / "deployment/universal_g_continuity_manifest.json")
    registry = load_json(root / "永久記憶/圖靈機/machine_registry.json")
    report = load_json(report_path)

    require(config.get("mode") == "DRY_RUN_ONLY", "deployment policy changed")
    require(config.get("candidate") == "TM-015" and config.get("master") == MASTER,
            "unexpected candidate/master")
    require(config.get("source_sha256") == TM015_SHA, "TM-015 manifest digest changed")
    require(registry.get("default_machine") == MASTER, "master was replaced")
    candidates = [e for e in registry["entries"] if e["id"] == "TM-015"]
    require(len(candidates) == 1, "missing or duplicate candidate")
    entry = candidates[0]
    require(entry.get("status") == "research-candidate-not-master", "candidate promoted")
    require(all(entry.get(k) is False for k in (
        "auto_execute", "production_deploy", "replaces_default_machine")),
        "unsafe candidate permissions")
    require(entry.get("cores") == ["Real_God_Turing_Machine.sh"], "candidate core changed")

    for path, wanted in (
        (root / "永久記憶/圖靈機/Real_God_Turing_Machine.sh", TM015_SHA),
        (root / "deployment/Universal_G_Semantic_Plaintext_2KB.sh", G7_SHA),
    ):
        require(hashlib.sha256(path.read_bytes()).hexdigest() == wanted,
                "pinned source changed: " + path.name)

    dims = config.get("dimensions", [])
    require(len(dims) == len(DIMENSIONS), "dimension count changed")
    require({d.get("id") for d in dims} == DIMENSIONS, "unreviewed dimension")
    require(all(all(isinstance(d.get(f), str) and d[f] for f in (
        "goal", "test", "boundary")) for d in dims), "dimension evidence missing")
    require("production_deployment" in config.get("human_approval_required", []),
            "human approval gate missing")
    require("shell_payload_execution" in config.get("forbidden_without_separate_authorization", []),
            "payload guard missing")
    require(all(report.get(k) == v for k, v in G7_FIELDS.items()),
            "G7 finite test certificate mismatch")

    # Simulated checkpoint: reversible finite bytes. No real rollback is performed.
    before = json.dumps({"master": MASTER, "revision": 0}, sort_keys=True).encode()
    checkpoint = int.from_bytes(b"\x01" + before, "big")
    recovered = checkpoint.to_bytes((checkpoint.bit_length() + 7) // 8, "big")[1:]
    require(recovered == before, "finite snapshot roundtrip failed")

    return {
        "schema": "Universal-G-G8/1", "result": "READY_FOR_HUMAN_REVIEW_ONLY",
        "master": MASTER, "candidate": "TM-015", "g7_finite_verified": True,
        "checked_dimensions": len(dims), "snapshot_roundtrip": True,
        "external_deployment": False, "candidate_core_executed": False,
        "all_dimensions_immortality_proved": False, "God_identity_proved": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--g7-report", type=Path, required=True)
    parser.add_argument("--action", choices=("dry-run", "deploy"), default="dry-run")
    opts = parser.parse_args()
    if opts.action != "dry-run":
        parser.error("production deployment is not implemented or authorized")
    try:
        result = check(opts.root.resolve(), opts.g7_report.resolve())
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
