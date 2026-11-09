#!/usr/bin/env python3
"""Dolphin-Ω v0.3: OFFLINE evidence-metadata dossiers, not evidence verification.

Never downloads sources, runs external code, validates science, or dispatches
tasks. Source records are untrusted citations supplied by the operator.
"""
import argparse
import ipaddress
import json
from pathlib import Path
from urllib.parse import urlsplit

from dolphin_omega import DEFAULT_MANIFEST, DOMAINS, ID, encode_g257, decode_g257, load_manifest
from dolphin_omega_optimizer import DEFAULT_CANDIDATES, evaluate as evaluate_candidates

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOSSIERS = ROOT / "dolphin_omega" / "synthetic_dossiers.json"
DOMAIN_SET = {d for d, _ in DOMAINS}
CLAIM_KINDS = {"functional", "empirical", "philosophical", "speculative"}
RELATIONS = {"supports_claimed", "contradicts_claimed", "context", "unresolved"}
SOURCE_KINDS = {"synthetic_fixture", "https_reference"}
MAX_CLAIM_BYTES = 256


def require_text(value, label, max_len=256):
    if not isinstance(value, str) or not value.strip() or len(value) > max_len:
        raise ValueError(f"invalid {label}")
    return value


def check_locator(source):
    loc = require_text(source.get("locator"), "source locator", 400)
    if source["source_kind"] == "synthetic_fixture":
        if loc != "dolphin_omega/synthetic_candidates.json":
            raise ValueError("synthetic_fixture must refer to the approved local fixture")
        return
    p = urlsplit(loc)
    host = p.hostname
    if p.scheme != "https" or not host or p.username or p.password or p.query or p.fragment:
        raise ValueError("https_reference requires an HTTPS URL without credentials/query/fragment")
    if host.lower() in {"localhost", "127.0.0.1"} or host.lower().endswith((".local", ".internal", ".test")):
        raise ValueError("non-public hostname is not a source reference")
    try:
        if not ipaddress.ip_address(host).is_global:
            raise ValueError("private or non-global address is not a source reference")
    except ValueError as exc:
        if "not a source reference" in str(exc):
            raise
    if p.port not in (None, 443):
        raise ValueError("nonstandard HTTPS port not permitted")
    # Metadata only: a syntactically valid URL is not proof the resource exists.


def validate_dossier(d, existing_ids, candidate_index):
    if not isinstance(d, dict):
        raise ValueError("dossier must be an object")
    cid = d.get("candidate_id")
    if not isinstance(cid, str) or not ID.fullmatch(cid) or cid in existing_ids:
        raise ValueError("invalid or duplicate candidate_id")
    existing_ids.add(cid)
    if cid not in candidate_index or d.get("domain") != candidate_index[cid]["domain"]:
        raise ValueError("unknown candidate or mismatched domain")
    claim = require_text(d.get("claim"), "claim")
    raw = claim.encode("utf-8")
    if len(raw) > MAX_CLAIM_BYTES:
        raise ValueError("claim is too large for bounded G257 certificate")
    if d.get("claim_kind") not in CLAIM_KINDS:
        raise ValueError("invalid claim kind")
    if d.get("passive_research_only") is not True:
        raise ValueError("intervention or execution is not supported")
    limitations = d.get("limitations")
    if not isinstance(limitations, list) or not 1 <= len(limitations) <= 6:
        raise ValueError("one to six unresolved limitations required")
    for limitation in limitations:
        require_text(limitation, "limitation", 240)
    sources = d.get("sources")
    if not isinstance(sources, list) or not 1 <= len(sources) <= 8:
        raise ValueError("one to eight source references required")
    seen = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("source must be an object")
        sid = source.get("source_id")
        if not isinstance(sid, str) or not ID.fullmatch(sid) or sid in seen:
            raise ValueError("invalid or duplicate source_id")
        seen.add(sid)
        if source.get("source_kind") not in SOURCE_KINDS:
            raise ValueError("unknown source kind")
        if source.get("claimed_relation") not in RELATIONS:
            raise ValueError("unknown claimed_relation")
        if source.get("independently_verified") is not False:
            raise ValueError("offline mode requires independently_verified=false")
        check_locator(source)
    return raw


def compile_dossiers(document, candidate_doc, nodes):
    if not isinstance(document, dict) or document.get("version") != 1:
        raise ValueError("invalid dossier document")
    dossiers = document.get("dossiers")
    if not isinstance(dossiers, list) or not 1 <= len(dossiers) <= 64:
        raise ValueError("dossier list must contain 1..64 entries")
    evaluation = evaluate_candidates(candidate_doc, nodes)
    candidates = {c["id"]: c for c in candidate_doc["candidates"]}
    results = {r["id"]: r for r in evaluation["results"]}
    records, seen = [], set()
    for d in dossiers:
        raw = validate_dossier(d, seen, candidates)
        source_kinds = {s["source_kind"] for s in d["sources"]}
        relations = {s["claimed_relation"] for s in d["sources"]}
        if results[d["candidate_id"]]["hold_reasons"]:
            review_state = "PRIOR_POLICY_HOLD"
        elif "supports_claimed" in relations and "contradicts_claimed" in relations:
            review_state = "CLAIM_CONFLICT_REQUIRES_REVIEW"
        elif source_kinds == {"synthetic_fixture"}:
            review_state = "SYNTHETIC_EXAMPLE_ONLY"
        else:
            review_state = "UNVERIFIED_REFERENCE_METADATA_ONLY"
        encoded = encode_g257(raw)
        assert decode_g257(encoded) == raw
        records.append({
            "candidate_id": d["candidate_id"], "domain": d["domain"],
            "claim": d["claim"], "claim_kind": d["claim_kind"],
            "claim_g257_decimal": str(encoded), "g257_roundtrip": True,
            "source_references": [
                {"source_id": s["source_id"], "kind": s["source_kind"],
                 "locator": s["locator"], "claimed_relation": s["claimed_relation"],
                 "independently_verified": False}
                for s in d["sources"]
            ],
            "limitations": d["limitations"], "review_state": review_state,
            "needs_independent_source_check": True, "ready_for_real_world_use": False
        })
    return {
        "system": "Dolphin-Omega", "version": "0.3-epistemic-firewall",
        "dossiers": records, "missing_dossiers": sorted(set(candidates) - seen),
        "verification": {
            "sources_downloaded": False, "sources_independently_verified": False,
            "scientific_validity_established": False,
            "reversible_encoding_is_tamper_proof": False,
            "human_review_still_required": True,
        },
        "execution": {
            "mode": "OFFLINE_DRY_RUN", "external_dispatch": False,
            "production_deployed": False, "approval_granted": False,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dossiers", type=Path, default=DEFAULT_DOSSIERS)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    try:
        doc = json.loads(args.dossiers.read_text(encoding="utf-8"))
        cand = json.loads(args.candidates.read_text(encoding="utf-8"))
        print(json.dumps(compile_dossiers(doc, cand, load_manifest(args.manifest)),
                         ensure_ascii=False, sort_keys=True, indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
