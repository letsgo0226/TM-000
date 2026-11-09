#!/usr/bin/env python3
"""Dolphin-Ω v0.2: bounded, OFFLINE, HYPOTHETICAL research prioritization.

This is neither a general optimum, an evidence validator, a formula solver,
nor a deployment authorization mechanism. No external calls are performed.
"""
import argparse
import json
from pathlib import Path

from dolphin_omega import DEFAULT_MANIFEST, DOMAINS, ID, load_manifest

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = ROOT / "dolphin_omega" / "synthetic_candidates.json"
DOMAINS_SET = {d for d, _ in DOMAINS}
METRICS = {"continuity", "evidence", "risk", "suffering", "uncertainty"}
SAFETY_FLAGS = {
    "unacceptable_harm", "nonconsensual_testing",
    "unauthorized_system_access", "physical_intervention"
}
# Provisional policy numbers for simulations only, NOT medical thresholds.
LIMITS = {"risk": 40, "suffering": 10, "uncertainty": 70, "evidence_minimum": 60}


def validate_candidate(c, ids):
    if not isinstance(c, dict):
        raise ValueError("candidate must be an object")
    cid = c.get("id")
    if not isinstance(cid, str) or not ID.fullmatch(cid) or cid in ids:
        raise ValueError("invalid or duplicate candidate id")
    ids.add(cid)
    if c.get("domain") not in DOMAINS_SET:
        raise ValueError("unknown domain")
    if not isinstance(c.get("title"), str) or not 1 <= len(c["title"].strip()) <= 160:
        raise ValueError("title must be 1..160 characters")
    if c.get("hypothetical") is not True:
        raise ValueError("v0.2 supports hypothetical candidate fixtures only")
    if not isinstance(c.get("node_id"), str) or not ID.fullmatch(c["node_id"]):
        raise ValueError("invalid node id")
    if c.get("ethics_review") not in ("declared_cleared", "pending", "rejected"):
        raise ValueError("invalid ethics review state")
    if c.get("evidence_review") not in ("declared_reviewed", "pending"):
        raise ValueError("invalid evidence review state")
    m = c.get("metrics")
    if not isinstance(m, dict) or set(m) != METRICS:
        raise ValueError("invalid metric set")
    if any(type(m[x]) is not int or not 0 <= m[x] <= 100 for x in METRICS):
        raise ValueError("metrics must be integers 0..100 (no booleans)")
    flags = c.get("safety_flags")
    if not isinstance(flags, dict) or set(flags) != SAFETY_FLAGS:
        raise ValueError("invalid safety flag set")
    if any(type(flags[x]) is not bool for x in SAFETY_FLAGS):
        raise ValueError("safety flags must be boolean")


def dominates(a, b):
    higher = ("continuity", "evidence")
    lower = ("risk", "suffering", "uncertainty")
    weak = all(a[x] >= b[x] for x in higher) and all(a[x] <= b[x] for x in lower)
    strict = any(a[x] > b[x] for x in higher) or any(a[x] < b[x] for x in lower)
    return weak and strict


def evaluate(document, nodes):
    if not isinstance(document, dict) or document.get("version") != 1:
        raise ValueError("invalid candidate document")
    candidates = document.get("candidates")
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 64:
        raise ValueError("candidate list must contain 1..64 rows")
    eligible_nodes = {
        n["id"] for n in nodes if n["enabled"] and "research_planning" in n["capabilities"]
        and (n["type"] != "external_opt_in" or n["explicit_opt_in"])
    }
    ids, results = set(), []
    for c in candidates:
        validate_candidate(c, ids)
        m, flags = c["metrics"], c["safety_flags"]
        reasons = []
        if any(flags.values()):
            reasons.append("SAFETY_VETO")
        if c["ethics_review"] != "declared_cleared":
            reasons.append("ETHICS_REVIEW_NOT_CLEARED")
        if c["evidence_review"] != "declared_reviewed":
            reasons.append("EVIDENCE_REVIEW_NOT_CLEARED")
        if m["risk"] > LIMITS["risk"]:
            reasons.append("RISK_LIMIT")
        if m["suffering"] > LIMITS["suffering"]:
            reasons.append("SUFFERING_LIMIT")
        if m["uncertainty"] > LIMITS["uncertainty"]:
            reasons.append("UNCERTAINTY_LIMIT")
        if m["evidence"] < LIMITS["evidence_minimum"]:
            reasons.append("LOW_EVIDENCE_SCORE")
        if c["node_id"] not in eligible_nodes:
            reasons.append("NODE_NOT_ELIGIBLE")
        score = (4 * m["continuity"] + 3 * m["evidence"] - 2 * m["risk"]
                 - 3 * m["suffering"] - 2 * m["uncertainty"]) if not reasons else None
        results.append({
            "id": c["id"], "domain": c["domain"], "title": c["title"],
            "node_id": c["node_id"], "status": (
                "SIMULATED_RESEARCH_PRIORITY_CANDIDATE" if not reasons else "HOLD"
            ), "hold_reasons": reasons, "synthetic_priority_index": score,
            "is_hypothetical": True, "independently_verified": False,
        })
    by_id = {c["id"]: c for c in candidates}
    winners, frontiers = {}, {}
    for domain in sorted(DOMAINS_SET):
        admissible = [r for r in results if r["domain"] == domain and not r["hold_reasons"]]
        frontier = [
            r for r in admissible if not any(
                dominates(by_id[s["id"]]["metrics"], by_id[r["id"]]["metrics"])
                for s in admissible if s["id"] != r["id"]
            )
        ]
        frontier.sort(key=lambda r: (-r["synthetic_priority_index"], r["id"]))
        frontiers[domain] = [r["id"] for r in frontier]
        winners[domain] = frontier[0]["id"] if frontier else None
    return {
        "system": "Dolphin-Omega", "version": "0.2-hypothetical-prioritization",
        "policy": {"limits": LIMITS, "weights": {
            "continuity": 4, "evidence": 3, "risk": -2,
            "suffering": -3, "uncertainty": -2
        }, "policy_is_provisional": True},
        "results": results, "pareto_frontiers_by_domain": frontiers,
        "synthetic_winners_by_domain": winners,
        "claims": {"general_or_global_optimum": False, "immortality": False,
                   "dolphin_formula_validated": False, "empirical_review_performed": False},
        "execution": {"mode": "OFFLINE_DRY_RUN", "external_dispatch": False,
                      "production_deployed": False, "approval_granted": False},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    try:
        data = json.loads(args.candidates.read_text(encoding="utf-8"))
        result = evaluate(data, load_manifest(args.manifest))
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
