#!/usr/bin/env python3
"""Dolphin-Omega v0.5: offline bibliography integrity and human-review queue.

Checks operator-curated PubMed citation metadata format and conservative scope,
NOT whether online records exist, sources are reproducible, or claims are true.
No network, credentials, review requests, external node execution or deployment.
"""
import argparse
import json
import re
from pathlib import Path

from dolphin_omega import DOMAINS, ID

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPERS = ROOT / "dolphin_omega" / "curated_literature.json"
DEFAULT_QUEUE = ROOT / "dolphin_omega" / "human_review_queue.json"
DOMAINS_SET = {d for d, _ in DOMAINS}
STUDY_TYPES = {"review", "original_research", "meta_analysis", "clinical_trial"}
EVIDENCE_SCOPES = {"mechanistic_background", "nonhuman_regeneration", "observational", "human_clinical"}
REVIEW_ROLES = {"methodology", "evidence_quality", "ethics"}
DOI = re.compile(r"^10\.[0-9]{4,9}/[A-Za-z0-9._;()/:+\-]{3,160}$")
PMID = re.compile(r"^[1-9][0-9]{0,11}$")
DATE = re.compile(r"^20[0-9]{2}-[01][0-9]-[0-3][0-9]$")


def require_text(v, name, length=500):
    if not isinstance(v, str) or not v.strip() or len(v) > length:
        raise ValueError("invalid " + name)
    return v


def validate_bibliography(doc):
    if not isinstance(doc, dict) or doc.get("version") != 1:
        raise ValueError("invalid bibliography version")
    papers = doc.get("papers")
    if not isinstance(papers, list) or not 1 <= len(papers) <= 24:
        raise ValueError("expected 1..24 papers")
    known, pmids, dois = {}, set(), set()
    for p in papers:
        if not isinstance(p, dict):
            raise ValueError("paper must be an object")
        pid = p.get("paper_id")
        if not isinstance(pid, str) or not ID.fullmatch(pid) or pid in known:
            raise ValueError("invalid or duplicate paper identifier")
        if p.get("domain") not in DOMAINS_SET:
            raise ValueError("unknown domain")
        for k in ("title", "first_author", "claim_summary", "contrary_evidence_question"):
            require_text(p.get(k), k)
        if type(p.get("year")) is not int or not 1900 <= p["year"] <= 2026:
            raise ValueError("invalid publication year")
        doi, pmid = p.get("doi"), p.get("pmid")
        if not isinstance(doi, str) or not DOI.fullmatch(doi) or doi.lower() in dois:
            raise ValueError("invalid or duplicate DOI")
        if not isinstance(pmid, str) or not PMID.fullmatch(pmid) or pmid in pmids:
            raise ValueError("invalid or duplicate PMID")
        if p.get("pubmed_url") != f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/":
            raise ValueError("PubMed URL must match the declared PMID")
        if p.get("doi_url") != f"https://doi.org/{doi}":
            raise ValueError("DOI URL must match the declared DOI")
        if p.get("study_type") not in STUDY_TYPES or p.get("evidence_scope") not in EVIDENCE_SCOPES:
            raise ValueError("unknown evidence category")
        # A review or nonhuman study must not be mislabeled as clinical validation.
        if p["study_type"] == "review" and p["evidence_scope"] == "human_clinical":
            raise ValueError("review is not a primary human clinical efficacy test")
        if p["domain"] == "cross_species" and p["evidence_scope"] == "human_clinical":
            raise ValueError("species study cannot be labeled human clinical evidence")
        if p.get("curation_method") != "public_pubmed_metadata_inspection":
            raise ValueError("unsupported curation method")
        if not isinstance(p.get("curation_date"), str) or not DATE.fullmatch(p["curation_date"]):
            raise ValueError("invalid curation date format")
        limitations = p.get("limitations")
        if not isinstance(limitations, list) or not 1 <= len(limitations) <= 8:
            raise ValueError("explicit limitations required")
        for limitation in limitations:
            require_text(limitation, "limitation")
        dois.add(doi.lower())
        pmids.add(pmid)
        known[pid] = p
    return known


def validate_review_queue(doc, papers):
    if not isinstance(doc, dict) or doc.get("version") != 1:
        raise ValueError("invalid review queue version")
    items = doc.get("items")
    if not isinstance(items, list) or len(items) != len(papers):
        raise ValueError("one review entry required for every curated paper")
    seen, results = set(), {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("review item must be an object")
        pid = item.get("paper_id")
        if pid not in papers or pid in seen:
            raise ValueError("unknown or duplicate review item")
        seen.add(pid)
        if item.get("authorized_activity") != "literature_review_only":
            raise ValueError("external action or clinical intervention is forbidden")
        roles = item.get("roles")
        if not isinstance(roles, list) or len(roles) != len(REVIEW_ROLES):
            raise ValueError("all three review roles must be present")
        names = set()
        for r in roles:
            if not isinstance(r, dict):
                raise ValueError("review role must be an object")
            role = r.get("role")
            if role not in REVIEW_ROLES or role in names:
                raise ValueError("unknown or duplicate review role")
            names.add(role)
            if r.get("status") != "pending" or r.get("reviewer_id") is not None:
                raise ValueError("no actual independent review or identity is recorded")
            if r.get("independent_identity_verified") is not False or r.get("decision") is not None:
                raise ValueError("no review decision or identity attestation accepted")
        if names != REVIEW_ROLES:
            raise ValueError("missing mandatory review role")
        results[pid] = "AWAITING_INDEPENDENT_HUMAN_REVIEW"
    if seen != set(papers):
        raise ValueError("incomplete review queue")
    return results


def compile_register(bibliography, queue):
    papers = validate_bibliography(bibliography)
    statuses = validate_review_queue(queue, papers)
    rows = []
    for pid, p in sorted(papers.items()):
        rows.append({
            "paper_id": pid, "domain": p["domain"], "title": p["title"],
            "doi": p["doi"], "pmid": p["pmid"], "pubmed_url": p["pubmed_url"],
            "study_type": p["study_type"], "evidence_scope": p["evidence_scope"],
            "claim_summary": p["claim_summary"], "limitations": p["limitations"],
            "contrary_evidence_question": p["contrary_evidence_question"],
            "bibliographic_record": "MANUALLY_CURATED_PUBLIC_METADATA",
            "metadata_syntax_checked": True,
            "online_retrieval_by_ci": False, "article_independently_replicated": False,
            "human_review_state": statuses[pid], "scientifically_established_by_system": False,
            "eligible_for_intervention": False, "eligible_for_deployment": False,
        })
    return {
        "system": "Dolphin-Omega", "version": "0.5-literature-triage",
        "curated_bibliography_count": len(rows),
        "recorded_domains": sorted({r["domain"] for r in rows}),
        "uncovered_domains": sorted(DOMAINS_SET - {r["domain"] for r in rows}),
        "papers": rows,
        "verification": {
            "metadata_format_checked": True, "metadata_verified_live_by_ci": False,
            "full_text_reviewed": False, "reviewer_identities_authenticated": False,
            "clinical_efficacy_verified": False, "immortality_verified": False,
            "dolphin_formula_validated": False, "global_optimum_proven": False,
        },
        "execution": {
            "mode": "OFFLINE_DRY_RUN", "external_dispatch": False,
            "production_deployed": False, "approval_granted": False,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bibliography", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument("--review-queue", type=Path, default=DEFAULT_QUEUE)
    args = parser.parse_args()
    try:
        papers = json.loads(args.bibliography.read_text(encoding="utf-8"))
        queue = json.loads(args.review_queue.read_text(encoding="utf-8"))
        print(json.dumps(compile_register(papers, queue), indent=2, ensure_ascii=False, sort_keys=True))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
