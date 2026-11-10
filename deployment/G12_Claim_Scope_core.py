#!/usr/bin/env python3
"""G12 offline source-to-claim audit. No network, signing, deployment or proof of outcomes."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import sys

MASTER = "UTM-PLEIADES-v0.2-PTCA"
PARENT_SHA = "ed5086cba2e88cb5b9f67234d87230c5ed2c42e197a6917c1405e6495eec70e6"
EXPECTED = {
    "computational": ("DISASTER_RECOVERY_GUIDANCE", "NIST provides contingency-planning guidance for information systems.", "Independent recovery exercises, documented restore points, and observed reliability."),
    "ai_continuity": ("VOLUNTARY_AI_RISK_GUIDANCE", "NIST supplies a voluntary framework for managing AI risks.", "Audited state restoration, provenance and identity criteria; consciousness remains unresolved."),
    "human_longevity": ("DEMOGRAPHIC_PERIOD_INDICATOR", "World Bank provides a population-level period life-expectancy indicator.", "Independently evaluated longitudinal clinical evidence and informed consent."),
    "interspecies_welfare": ("CELL_FOOD_SAFETY_REVIEW", "WHO and FAO discuss hazards and safety oversight for cell-based foods.", "Independent welfare and sentience assessment, safety validation, ethics review."),
    "ecological": ("TERRESTRIAL_ECOSYSTEM_TARGETS", "UN SDG 15 specifies terrestrial biodiversity and ecosystem goals.", "Measured longitudinal ecological indicators and causal evaluation."),
    "peace_sdgs": ("PEACE_JUSTICE_TARGETS", "UN SDG 16 specifies peace, justice and institutional targets.", "Independent monitoring of peace and governance outcomes, with confounder analysis."),
    "psychological_cultural": ("DOCUMENTARY_HERITAGE_PROGRAMME", "UNESCO Memory of the World promotes documentary heritage preservation.", "Consent-governed, verifiable preservation and recovery; not personhood survival."),
    "spiritual_philosophical": ("PHILOSOPHICAL_GROUNDING_DEBATE", "Stanford Encyclopedia of Philosophy discusses competing views about God and necessary beings.", "Independent premises, argument validity, objection handling, and epistemic openness."),
}
def require(ok, reason):
    if not ok:
        raise ValueError(reason)
def check(root: Path, as_of: date) -> dict:
    root = root.resolve()
    raw = (root / "deployment/G11_eight_domain_evidence_ledger.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PARENT_SHA, "G11 digest changed")
    parent = json.loads(raw)
    ledger = json.loads((root / "deployment/G12_claim_scope_ledger.json").read_text(encoding="utf-8"))
    require(ledger["schema"] == "G12-claim-scope-review/1" and
            ledger["parent_ledger"] == parent["schema"] == "G11-eight-domain-evidence/1" and
            ledger["parent_digest_sha256"] == PARENT_SHA, "lineage mismatch")
    require(ledger["master"] == parent["master"] == MASTER and
            ledger["mode"] == parent["mode"] == "DRY_RUN_ONLY" and
            ledger["status"] == "CLAIM_SCOPE_REVIEW_ONLY", "authority/status changed")
    require(ledger["expiry_days"] == 180 and ledger["required_review_scope"] ==
            "SOURCE_TOPIC_REFERENCE" and
            ledger["forbidden_global_claims"] == parent["prohibited_conclusions"], "scope guard")
    require(all(ledger[k] is False for k in
            ("content_snapshots_stored", "online_refetched_in_ci", "publisher_signature_verified",
             "field_observations_validated", "all_eight_outcomes_verified")),
            "false evidence-acquisition claim")
    require(0 <= (as_of - date.fromisoformat(ledger["reviewed_on"])).days <= 180 and
            0 <= (as_of - date.fromisoformat(parent["reviewed_on"])).days <= 180,
            "ledger review expired/future")
    rows = ledger["claims"]
    parent_rows = {r["domain"]: r for r in parent["records"]}
    require(len(rows) == len(parent_rows) == len(EXPECTED) == 8 and
            {r["domain"] for r in rows} == set(EXPECTED) == set(parent_rows) and
            len({r["source_id"] for r in rows}) == 8, "missing/duplicate domain")
    for row in rows:
        domain = row["domain"]
        p = parent_rows[domain]
        require((row["source_id"], row["source_url"], row["source_kind"], row["excluded_inference"]) ==
                (p["id"], p["url"], p["kind"], p["not_proven"]), "provenance changed: " + domain)
        require((row["claim_code"], row["claim_text"], row["evidence_required"]) ==
                EXPECTED[domain], "scope/evidence requirement changed: " + domain)
        require(row["limited_to"] == "SOURCE_TOPIC_REFERENCE" and row["outcome_verified"] is False,
                "unverified outcome promoted: " + domain)
        require(0 <= (as_of - date.fromisoformat(row["reviewed_on"])).days <= 180,
                "source claim review expired/future: " + domain)
    return dict(version="G12", reviewed_claims=8, domains=8, exact_parent_digest_verified=True,
                scope="SOURCE_TOPIC_REFERENCE", new_empirical_outcomes=0,
                remote_sources_fetched=False, signed_evidence=False,
                status="CLAIM_SCOPE_REVIEW_ONLY", production_deployed=False,
                universal_immortality_proved=False, divine_identity_proved=False)
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    a = p.parse_args()
    try:
        result = check(a.root, a.as_of)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
