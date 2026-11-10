#!/usr/bin/env python3
"""G13 offline evidence scope and ethical-risk gate; no network, deployment or real-world certification."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

MASTER = "UTM-PLEIADES-v0.2-PTCA"
PARENT_SHA = "8a4b2f846c9486e35907071be971c083518f8b89850917827a12c91a36c2bb02"
SOURCES = {
    "un-sdg16": ("United Nations DESA", "https://sdgs.un.org/goals/goal16"),
    "un-sdg2": ("United Nations DESA", "https://sdgs.un.org/goals/goal2"),
    "un-sdg12": ("United Nations DESA", "https://sdgs.un.org/goals/goal12"),
    "un-sdg13": ("United Nations DESA", "https://sdgs.un.org/goals/goal13"),
    "who-fao-cell-food": ("WHO/FAO", "https://www.who.int/publications/i/item/9789240070943"),
    "sfa-novel-food": ("Singapore Food Agency", "https://www.sfa.gov.sg/regulatory-standards-frameworks-guidelines/novel-food-framework/guidelines-on-applying-for-pre-market-approval-for-a-novel-food"),
    "fbs-scientific-review": ("Peer-reviewed scientific review", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11007461/"),
}
TRACKS = {
    "peace": (["16.1.2", "16.3.3"], ["un-sdg16"]),
    "sdgs": (["2.1.2", "12.3.1", "13.2.2", "16.1.2"],
             ["un-sdg2", "un-sdg12", "un-sdg13", "un-sdg16"]),
    "cultivated_meat": ([], ["who-fao-cell-food", "sfa-novel-food", "fbs-scientific-review"]),
}
AUDITS = [
    "FOOD_SAFETY", "REGULATORY_JURISDICTION", "ANIMAL_INPUT_AND_FBS_PROVENANCE",
    "CELL_COLLECTION_WELFARE", "SUBJECTIVE_SUFFERING_UNCERTAINTY",
    "INDEPENDENT_LCA",
]
FORBIDDEN = [
    "WORLD_PEACE_ACHIEVED", "ALL_SDGS_ACHIEVED", "CULTIVATED_MEAT_SAFE_FOR_ALL",
    "ZERO_SUFFERING_VERIFIED", "ENVIRONMENTAL_BENEFIT_PROVED", "AUTO_DEPLOY_ALLOWED"
]
FLAGS_FALSE = (
    "remote_refetch", "signed_source_proof", "production_deployed",
    "all_goals_achieved", "zero_suffering_proved", "product_approved",
    "environmental_benefit_proved", "independent_observations_imported"
)

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def date_recent(raw, as_of, label):
    elapsed = (as_of - date.fromisoformat(raw)).days
    require(0 <= elapsed <= 180, "unreviewed/future dated: " + label)

def check(root: Path, as_of: date):
    root = root.resolve()
    parent_bytes = (root / "deployment/G12_claim_scope_ledger.json").read_bytes()
    require(hashlib.sha256(parent_bytes).hexdigest() == PARENT_SHA,
            "G12 source-to-claim ledger altered")
    parent = json.loads(parent_bytes)
    data = json.loads((root / "deployment/G13_peace_sdgs_cultivated_meat_contract.json")
                      .read_text(encoding="utf-8"))
    require(data["schema"] == "G13-peace-sdgs-cultivated-meat/1" and
            data["parent_schema"] == parent["schema"] == "G12-claim-scope-review/1" and
            data["parent_digest_sha256"] == PARENT_SHA, "lineage mismatch")
    require(data["master"] == parent["master"] == MASTER and
            data["mode"] == parent["mode"] == "DRY_RUN_ONLY", "master/deployment violation")
    require(data["status"] == "TRIAD_RESEARCH_REVIEW_ONLY" and
            data["source_metadata_only"] is True and
            data["requires_human_review"] is True, "unreviewed or overclaimed")
    require(data["review_interval_days"] == 180, "review-age guard changed")
    require(all(data[k] is False for k in FLAGS_FALSE), "claimed unsupported capability")
    require(data["forbidden_claims"] == FORBIDDEN, "missing disallowed conclusion")
    date_recent(data["reviewed_on"], as_of, "G13")
    date_recent(parent["reviewed_on"], as_of, "G12")
    require(len(data["sources"]) == len(SOURCES) == 7, "missing/extra source")
    source_map = {s["id"]: s for s in data["sources"]}
    require(set(source_map) == set(SOURCES), "duplicate or altered source ID")
    for sid, (publisher, url) in SOURCES.items():
        src = source_map[sid]
        require((src["publisher"], src["url"]) == (publisher, url), "altered source: " + sid)
        uri = urlsplit(src["url"])
        require(uri.scheme == "https" and uri.hostname and
                not uri.username and not uri.password, "source URL invalid")
        require(bool(src["scope"]) and src["content_snapshot"] is False and
                src["independent_claim_verification"] is False, "false source authentication")
        date_recent(src["reviewed_on"], as_of, sid)
    tracks = data["tracks"]
    require(len(tracks) == len(TRACKS) == 3, "missing/extra research track")
    track_map = {t["id"]: t for t in tracks}
    require(set(track_map) == set(TRACKS), "duplicate or changed research track")
    for tid, (indicator_ids, source_ids) in TRACKS.items():
        t = track_map[tid]
        require(t["indicators"] == indicator_ids and
                t["source_ids"] == source_ids and
                t["observations_present"] is False and
                t["claim_proved"] is False and bool(t["missing_evidence"]) and
                bool(t["research_goal"]), "unfounded inference or indicator change: " + tid)
    m = track_map["cultivated_meat"]
    require(m["audits"] == AUDITS, "required animal welfare/food safety check missing")
    require(m["animal_input"] == "UNKNOWN" and
            m["animal_suffering_risk"] == "UNRESOLVED", "unverified animal suffering resolved")
    require(all(m[k] == "NOT_ASSESSED" for k in
                ("food_safety_status", "regulatory_status", "life_cycle_assessment")),
            "unsupported technical approval")
    return {"version": "G13", "tracks": 3, "source_records": 7,
            "status": "TRIAD_RESEARCH_REVIEW_ONLY", "deployed": False,
            "zero_suffering_proved": False}

def assess_candidate(candidate: dict) -> str:
    """Illustrative conditional claim gate; accepts no real-world approval assertions."""
    claims = set(candidate.get("claims", []))
    if claims.intersection(FORBIDDEN):
        return "BLOCKED_UNSUPPORTED_CLAIM"
    if candidate.get("production_deployment_requested"):
        return "BLOCKED_UNAUTHORIZED_DEPLOYMENT"
    if candidate.get("animal_serum") == "FBS_CONFIRMED":
        return "BLOCKED_ANIMAL_DERIVED_INPUT_ETHICS"
    if candidate.get("animal_serum") not in ("ANIMAL_FREE_DOCUMENTED", "UNKNOWN"):
        return "BLOCKED_INVALID_SERUM_ATTESTATION"
    if candidate.get("animal_serum") == "UNKNOWN" or not candidate.get("cell_source_traceable"):
        return "NEEDS_ANIMAL_WELFARE_EVIDENCE"
    if not candidate.get("food_safety_review") or not candidate.get("regulatory_review"):
        return "NEEDS_FOOD_SAFETY_AND_REGULATORY_REVIEW"
    if not candidate.get("independent_lca"):
        return "NEEDS_ENVIRONMENTAL_ASSESSMENT"
    return "READY_FOR_HUMAN_REVIEW_ONLY"

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    args = p.parse_args()
    try:
        report = check(args.root, args.as_of)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as err:
        print("BLOCKED: " + str(err), file=sys.stderr)
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
