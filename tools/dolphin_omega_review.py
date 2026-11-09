#!/usr/bin/env python3
"""Dolphin-Ω v0.4 offline review-packet integrity and attestation checks.

Checks local snapshot bytes and recorded reviewer metadata, NOT the authenticity
of URLs, the identities of reviewers, or the truth of scientific claims.
No network, deployment, secrets, remote execution or mutations.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

from dolphin_omega import DEFAULT_MANIFEST, ID, load_manifest
from dolphin_omega_dossier import DEFAULT_DOSSIERS, compile_dossiers
from dolphin_omega_optimizer import DEFAULT_CANDIDATES

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVIEWS = ROOT / "dolphin_omega" / "synthetic_review_packets.json"
SNAPSHOT_FOLDER = ROOT / "dolphin_omega" / "review_snapshots"
SHA = re.compile(r"^[0-9a-f]{64}$")
ROLES = {"methods", "replication", "ethics"}
VERDICTS = {"supports_claimed", "contradicts_claimed", "context", "inconclusive"}


def require_string(value, label, limit=240):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError("invalid " + label)
    return value


def validate_snapshot_path(path):
    text = require_string(path, "snapshot_path", 180)
    # Never accept absolute paths, traversal, alternate separators, hidden paths,
    # or files outside the documented review_snapshots directory.
    pure = Path(text)
    if pure.is_absolute() or "\\" in text or pure.parts[:2] != ("dolphin_omega", "review_snapshots"):
        raise ValueError("snapshot must be inside dolphin_omega/review_snapshots")
    if len(pure.parts) != 3 or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}\.txt", pure.name):
        raise ValueError("snapshot filename is invalid")
    location = ROOT / pure
    if location.is_symlink() or location.parent.is_symlink():
        raise ValueError("symbolic links prohibited")
    if not location.resolve().is_relative_to(SNAPSHOT_FOLDER.resolve()):
        raise ValueError("snapshot escapes repository boundary")
    return location


def validate_packet(doc, compiled_dossiers):
    if not isinstance(doc, dict) or doc.get("version") != 1:
        raise ValueError("invalid review packet schema version")
    snapshots = doc.get("snapshots")
    reviews = doc.get("reviews")
    if not isinstance(snapshots, list) or not 1 <= len(snapshots) <= 32:
        raise ValueError("snapshot count must be 1..32")
    if not isinstance(reviews, list) or not 1 <= len(reviews) <= 128:
        raise ValueError("review count must be 1..128")
    dossiers = {d["candidate_id"]: d for d in compiled_dossiers["dossiers"]}
    keyed_sources = {(d["candidate_id"], s["source_id"]): s for d in dossiers.values()
                     for s in d["source_references"]}
    snapshots_by_key = {}
    for snapshot in snapshots:
        if not isinstance(snapshot, dict):
            raise ValueError("snapshot must be an object")
        candidate, source = snapshot.get("candidate_id"), snapshot.get("source_id")
        key = (candidate, source)
        if key not in keyed_sources or key in snapshots_by_key:
            raise ValueError("unknown or duplicate snapshot source")
        if keyed_sources[key]["kind"] != "https_reference":
            raise ValueError("v0.4 snapshots require a HTTPS reference from v0.3")
        expected = snapshot.get("sha256")
        if not isinstance(expected, str) or not SHA.fullmatch(expected):
            raise ValueError("invalid sha256 metadata")
        location = validate_snapshot_path(snapshot.get("snapshot_path"))
        # Snapshot content is operator-supplied and untrusted; no fetching occurs.
        if not location.is_file() or not 1 <= location.stat().st_size <= 16384:
            raise ValueError("missing/oversized snapshot")
        content = location.read_bytes()
        if b"\x00" in content:
            raise ValueError("binary snapshot not supported")
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("snapshot must be UTF-8 text") from exc
        actual = hashlib.sha256(content).hexdigest()
        snapshots_by_key[key] = {
            "candidate_id": candidate, "source_id": source,
            "path": snapshot["snapshot_path"],
            "sha256_declared": expected, "sha256_observed": actual,
            "snapshot_byte_integrity": actual == expected,
            "_content": text,
        }
    seen_review_ids, reviewers_by_key = set(), {}
    for review in reviews:
        if not isinstance(review, dict):
            raise ValueError("review must be an object")
        rid = review.get("review_id")
        cid = review.get("candidate_id")
        sid = review.get("source_id")
        if not isinstance(rid, str) or not ID.fullmatch(rid) or rid in seen_review_ids:
            raise ValueError("invalid/duplicate review_id")
        seen_review_ids.add(rid)
        key = (cid, sid)
        if key not in snapshots_by_key:
            raise ValueError("review must reference a local snapshot")
        reviewer = review.get("reviewer_id")
        team = review.get("team_id")
        if any(not isinstance(x, str) or not ID.fullmatch(x) for x in (reviewer, team)):
            raise ValueError("invalid reviewer/team identifier")
        if review.get("role") not in ROLES or review.get("verdict") not in VERDICTS:
            raise ValueError("invalid role/verdict")
        if type(review.get("conflict_declared")) is not bool:
            raise ValueError("conflict_declared must be boolean")
        if review.get("synthetic") is not True:
            raise ValueError("v0.4 allows synthetic reviewers only; no real identities claimed")
        excerpt = require_string(review.get("checked_excerpt"), "checked_excerpt", 300)
        require_string(review.get("reasoning"), "reasoning", 500)
        if excerpt not in snapshots_by_key[key]["_content"]:
            raise ValueError("review excerpt is absent from the pinned snapshot")
        bucket = reviewers_by_key.setdefault(key, [])
        if any(r["reviewer_id"] == reviewer for r in bucket):
            raise ValueError("duplicate reviewer for one snapshot")
        bucket.append(review)
    return dossiers, snapshots_by_key, reviewers_by_key


def audit(doc, dossiers_document, candidate_document, nodes):
    compiled = compile_dossiers(dossiers_document, candidate_document, nodes)
    dossiers, snapshots, review_groups = validate_packet(doc, compiled)
    rows = []
    for key in sorted(snapshots):
        rec = snapshots[key]
        candidate, source = key
        submitted = review_groups.get(key, [])
        usable = [r for r in submitted if not r["conflict_declared"]]
        teams = {r["team_id"] for r in usable}
        identities = {r["reviewer_id"] for r in usable}
        verdicts = {r["verdict"] for r in usable}
        if dossiers[candidate]["review_state"] == "PRIOR_POLICY_HOLD":
            state = "PRIOR_POLICY_HOLD"
        elif not rec["snapshot_byte_integrity"]:
            state = "SNAPSHOT_INTEGRITY_MISMATCH"
        elif len(usable) < 2 or len(teams) < 2 or len(identities) < 2:
            state = "INSUFFICIENT_RECORDED_REVIEWERS"
        elif "supports_claimed" in verdicts and "contradicts_claimed" in verdicts:
            state = "DISAGREEMENT_REQUIRES_HUMAN_REVIEW"
        else:
            state = "MULTIPLE_SYNTHETIC_ATTESTATIONS_RECORDED"
        rows.append({
            "candidate_id": candidate, "source_id": source,
            "snapshot_path": rec["path"], "sha256_declared": rec["sha256_declared"],
            "sha256_observed": rec["sha256_observed"],
            "snapshot_byte_integrity": rec["snapshot_byte_integrity"],
            "review_count": len(submitted), "non_conflicted_review_count": len(usable),
            "distinct_declared_team_count": len(teams), "review_state": state,
            "reviewer_identities_authenticated": False,
            "source_origin_authenticated": False,
            "scientific_claim_verified": False,
            "eligible_for_deployment": False,
        })
    return {
        "system": "Dolphin-Omega", "version": "0.4-offline-review-packet",
        "packet_results": rows,
        "uncovered_dossiers": sorted(set(dossiers) - {x["candidate_id"] for x in rows}),
        "verification": {
            "source_content_fetched": False, "snapshot_bytes_compared_to_declared_sha256": True,
            "sha256_proves_source_authenticity": False,
            "independent_reviewer_identities_verified": False,
            "scientific_claims_verified": False,
            "human_review_still_required": True,
        },
        "execution": {"mode": "OFFLINE_DRY_RUN", "external_dispatch": False,
                      "production_deployed": False, "approval_granted": False},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_REVIEWS)
    parser.add_argument("--dossiers", type=Path, default=DEFAULT_DOSSIERS)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    try:
        result = audit(
            json.loads(args.packet.read_text(encoding="utf-8")),
            json.loads(args.dossiers.read_text(encoding="utf-8")),
            json.loads(args.candidates.read_text(encoding="utf-8")),
            load_manifest(args.manifest),
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
