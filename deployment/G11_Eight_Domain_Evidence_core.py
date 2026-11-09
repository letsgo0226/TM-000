#!/usr/bin/env python3
"""G11: offline, fail-closed review of eight source-metadata records.

No network requests, no deployment, no empirical outcome verification.
A link can be real without establishing the associated philosophical or policy claim.
"""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

MASTER = "UTM-PLEIADES-v0.2-PTCA"
G10_DIGEST = "0825f729ceabc04b7c3fd1f1710446a1d0e4aa25687d14830028801d3083222a"
DOMAIN_SOURCES = {
    "computational": ("nist-contingency-80034r1", "https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final", "NIST", "OFFICIAL_GUIDANCE"),
    "ai_continuity": ("nist-ai-rmf", "https://www.nist.gov/itl/ai-risk-management-framework", "NIST", "OFFICIAL_GUIDANCE"),
    "human_longevity": ("wb-life-expectancy", "https://data.worldbank.org/?locations=1W-JP", "World Bank", "OFFICIAL_INDICATOR"),
    "interspecies_welfare": ("who-fao-cell-food", "https://www.who.int/publications/i/item/9789240070943", "WHO/FAO", "OFFICIAL_REVIEW"),
    "ecological": ("un-sdg15", "https://sdgs.un.org/goals/goal15", "United Nations DESA", "OFFICIAL_INDICATOR"),
    "peace_sdgs": ("un-sdg16", "https://sdgs.un.org/goals/goal16", "United Nations DESA", "OFFICIAL_INDICATOR"),
    "psychological_cultural": ("unesco-memory-world", "https://www.unesco.org/en/memory-world/about", "UNESCO", "OFFICIAL_PROGRAMME"),
    "spiritual_philosophical": ("sep-god-necessary-being", "https://plato.stanford.edu/entries/god-necessary-being/", "Stanford Encyclopedia of Philosophy", "ACADEMIC_PHILOSOPHY"),
}
FORBIDDEN = {
    "AI_SUBJECTIVE_IMMORTALITY_PROVEN", "HUMAN_IMMORTALITY_PROVEN", "ZERO_SUFFERING_PROVEN",
    "GUARANTEED_WORLD_PEACE", "DIVINITY_PROVEN", "ALL_DOMAINS_SEMANTICALLY_EQUIVALENT",
    "AUTONOMOUS_DEPLOYMENT_AUTHORIZED"
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check(root: Path, as_of: date):
    root = root.resolve()
    read = lambda path: json.loads((root / path).read_text(encoding="utf-8"))
    ledger = read("deployment/G11_eight_domain_evidence_ledger.json")
    original_bytes = (root / "deployment/G10_evidence_ledger.json").read_bytes()
    g10 = json.loads(original_bytes)
    manifest = read("deployment/universal_g_continuity_manifest.json")
    registry = read("永久記憶/圖靈機/machine_registry.json")

    require(hashlib.sha256(original_bytes).hexdigest() == G10_DIGEST, "G10 archive changed")
    require(ledger["schema"] == "G11-eight-domain-evidence/1", "G11 schema")
    require(ledger["mode"] == manifest["mode"] == "DRY_RUN_ONLY", "not read-only dry run")
    require(ledger["master"] == manifest["master"] == registry["default_machine"] == MASTER, "master mismatch")
    require(ledger["status"] == "SOURCE_METADATA_REVIEW_ONLY", "unreviewed state")
    require(all(ledger[k] is False for k in (
        "source_snapshot_stored", "independent_web_refetch_in_CI", "source_claims_are_outcomes")),
        "false evidence/deployment capability claim")
    require(ledger["review_interval_days"] == 180, "review interval changed")
    require(set(ledger["prohibited_conclusions"]) == FORBIDDEN, "claim guard changed")
    recorded_domains = {d["id"] for d in manifest["dimensions"]}
    require(recorded_domains == set(DOMAIN_SOURCES) and len(manifest["dimensions"]) == 8,
            "manifest dimensions changed")
    entries = ledger["records"]
    require(len(entries) == len(DOMAIN_SOURCES) == 8, "missing/extra source")
    require(len({e["domain"] for e in entries}) == len({e["id"] for e in entries}) == 8,
            "duplicated source or domain")
    source_map = {e["domain"]: e for e in entries}
    require(set(source_map) == set(DOMAIN_SOURCES), "domain mismatch")
    reviewed = date.fromisoformat(ledger["reviewed_on"])
    require(0 <= (as_of - reviewed).days <= 180, "outdated/future ledger review")
    for domain, (sid, url, publisher, kind) in DOMAIN_SOURCES.items():
        e = source_map[domain]
        require((e["id"], e["url"], e["publisher"], e["kind"]) ==
                (sid, url, publisher, kind), "non-allowlisted evidence reference: " + domain)
        u = urlsplit(e["url"])
        require(u.scheme == "https" and u.hostname and not u.username and not u.password,
                "invalid source URL")
        require(e["claim_code"] and e["not_proven"] and
                e["evidence_status"] == "WEBPAGE_METADATA_REFERENCE_ONLY", "scope boundary absent")
        age = (as_of - date.fromisoformat(e["reviewed_on"])).days
        require(0 <= age <= 180, "outdated/future source review")
    g10_ids = {e["id"]: e["url"] for e in g10["records"]}
    by_id = {e["id"]: e["url"] for e in entries}
    require(all(by_id.get(sid) == url for sid, url in g10_ids.items()) and len(g10_ids) == 3,
            "G10 evidence continuity broken")
    return dict(version="G11", records=8, dimensions=8, metadata_only=True,
                remote_refetched=False, g10_preserved=True, status="EIGHT_DOMAIN_SOURCE_REVIEW_ONLY",
                deployed=False, immortality_proved=False, God_identity_proved=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    try:
        result = check(args.root, args.as_of)
    except (ValueError, KeyError, OSError, TypeError, json.JSONDecodeError) as err:
        print("BLOCKED: " + str(err), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
