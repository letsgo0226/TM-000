#!/usr/bin/env python3
"""Dolphin-Ω v0.8: simulated, revocable, least-privilege research permissions.

This is an OFFLINE POLICY EVALUATOR, not a login/identity service or runtime
authorization for real systems. Even ALLOW_SIMULATION does not execute work.
Every actor is fictional; no real-world permission is asserted or granted.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from dolphin_omega import DEFAULT_MANIFEST, ID, load_manifest

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = ROOT / "dolphin_omega" / "synthetic_collaboration_events.json"
ACTIONS = {"read_registered_bibliography", "prepare_unverified_review_draft"}
KINDS = {"GRANT", "REQUEST", "REVOKE"}
BASE_KEYS = {"seq", "event_id", "kind", "at", "grant_id"}
SCHEMAS = {
    "GRANT": BASE_KEYS | {"issuer_id", "grantee_id", "node_id", "action",
                          "expires_at", "owner_consent_declared", "owner_identity_authenticated"},
    "REQUEST": BASE_KEYS | {"grantee_id", "node_id", "action"},
    "REVOKE": BASE_KEYS | {"issuer_id"},
}


def identifier(value, label):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ValueError("invalid " + label)
    return value


def parse_utc(value):
    if not isinstance(value, str) or len(value) != 20 or not value.endswith("Z"):
        raise ValueError("timestamps must be YYYY-MM-DDTHH:MM:SSZ")
    try:
        instant = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError("invalid timestamp") from exc
    if instant.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise ValueError("noncanonical UTC timestamp")
    return instant


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def audit_events(doc, manifest):
    if not isinstance(doc, dict) or set(doc) != {"version", "notice", "events"} or doc["version"] != 1:
        raise ValueError("invalid collaboration event document")
    if not isinstance(doc["notice"], str) or not 5 <= len(doc["notice"]) <= 500:
        raise ValueError("event notice required")
    events = doc["events"]
    if not isinstance(events, list) or not 1 <= len(events) <= 128:
        raise ValueError("event count must be 1..128")
    nodes = {n["id"]: n for n in manifest}
    grants, seen_ids, audit = {}, set(), []
    last_time = None
    chain = "0" * 64
    for index, event in enumerate(events, 1):
        if not isinstance(event, dict) or event.get("kind") not in KINDS:
            raise ValueError("unknown event kind")
        kind = event["kind"]
        if set(event) != SCHEMAS[kind]:
            raise ValueError("event schema must match exact allowed keys")
        if type(event["seq"]) is not int or event["seq"] != index:
            raise ValueError("event sequence must be strictly contiguous")
        eid = identifier(event["event_id"], "event_id")
        gid = identifier(event["grant_id"], "grant_id")
        if eid in seen_ids:
            raise ValueError("duplicate event ID")
        seen_ids.add(eid)
        when = parse_utc(event["at"])
        if last_time is not None and when <= last_time:
            raise ValueError("events must be time ordered and strictly increasing")
        last_time = when
        decision, reason = None, None
        if kind == "GRANT":
            issuer = identifier(event["issuer_id"], "issuer_id")
            grantee = identifier(event["grantee_id"], "grantee_id")
            node_id = identifier(event["node_id"], "node_id")
            action = identifier(event["action"], "action")
            expires = parse_utc(event["expires_at"])
            if type(event["owner_consent_declared"]) is not bool or event["owner_identity_authenticated"] is not False:
                raise ValueError("simulated consent must be boolean; verified identities not supported")
            if gid in grants:
                raise ValueError("duplicate grant ID; grants cannot be resurrected or replaced")
            if expires <= when:
                decision, reason = "DENY", "EXPIRED_OR_INVALID_GRANT_WINDOW"
            elif not event["owner_consent_declared"]:
                decision, reason = "DENY", "MISSING_DECLARED_CONSENT"
            elif action not in ACTIONS:
                decision, reason = "DENY", "ACTION_NOT_ALLOWED"
            elif node_id not in nodes:
                decision, reason = "DENY", "UNKNOWN_NODE"
            elif nodes[node_id]["type"] == "external_opt_in":
                decision, reason = "DENY", "EXTERNAL_NODE_UNSUPPORTED"
            elif not nodes[node_id]["enabled"] or not nodes[node_id]["explicit_opt_in"]:
                decision, reason = "DENY", "NODE_NOT_ELIGIBLE"
            else:
                decision, reason = "RECORDED_SIMULATED_GRANT", "DECLARATION_ONLY_NOT_AUTHENTICATED"
            grants[gid] = {
                "issuer": issuer, "grantee": grantee, "node": node_id,
                "action": action, "expires": expires, "revoked": False,
                "accepted": decision == "RECORDED_SIMULATED_GRANT",
            }
        elif kind == "REVOKE":
            issuer = identifier(event["issuer_id"], "issuer_id")
            grant = grants.get(gid)
            if grant is None:
                decision, reason = "DENY", "UNKNOWN_GRANT"
            elif issuer != grant["issuer"]:
                decision, reason = "DENY", "WRONG_DECLARED_ISSUER"
            elif grant["revoked"]:
                decision, reason = "DENY", "ALREADY_REVOKED"
            else:
                grant["revoked"] = True
                decision, reason = "RECORDED_SIMULATED_REVOCATION", "IRREVERSIBLE_FOR_GRANT_ID"
        else:
            grantee = identifier(event["grantee_id"], "grantee_id")
            node_id = identifier(event["node_id"], "node_id")
            action = identifier(event["action"], "action")
            grant = grants.get(gid)
            if grant is None:
                decision, reason = "DENY", "UNKNOWN_GRANT"
            elif not grant["accepted"]:
                decision, reason = "DENY", "GRANT_NOT_ACTIVE"
            elif grant["revoked"]:
                decision, reason = "DENY", "REVOKED_GRANT"
            elif when >= grant["expires"]:
                decision, reason = "DENY", "EXPIRED_GRANT"
            elif grantee != grant["grantee"]:
                decision, reason = "DENY", "WRONG_DECLARED_GRANTEE"
            elif node_id != grant["node"] or action != grant["action"]:
                decision, reason = "DENY", "SCOPE_MISMATCH"
            elif node_id not in nodes or nodes[node_id]["type"] == "external_opt_in":
                decision, reason = "DENY", "EXTERNAL_OR_UNKNOWN_NODE"
            elif not nodes[node_id]["enabled"] or not nodes[node_id]["explicit_opt_in"]:
                decision, reason = "DENY", "NODE_NOT_ELIGIBLE"
            else:
                decision, reason = "ALLOW_SIMULATION", "NO_REAL_EXECUTION_AUTHORITY"
        row = {"seq": index, "event_id": eid, "kind": kind, "at": event["at"],
               "grant_id": gid, "decision": decision, "reason": reason,
               "executed": False, "identity_authenticated": False,
               "real_authorization_granted": False}
        # Detect accidental log changes between separately preserved copies.
        # Without a trusted external anchor or signatures, this is NOT tamperproof.
        chain = hashlib.sha256(chain.encode("ascii") + canonical(event) + canonical(row)).hexdigest()
        row["audit_chain_digest"] = chain
        audit.append(row)
    return {
        "system": "Dolphin-Omega", "version": "0.8-simulated-consent-protocol",
        "audit": audit, "audit_entries": len(audit), "last_audit_digest": chain,
        "active_simulated_grant_ids": sorted(
            gid for gid, g in grants.items() if g["accepted"] and not g["revoked"]
            and last_time is not None and last_time < g["expires"]
        ),
        "verification": {
            "least_privilege_policy_simulated": True,
            "revocation_policy_simulated": True,
            "audit_digest_checks_accidental_changes_only": True,
            "log_immutability_proven": False,
            "owner_identities_authenticated": False,
            "third_party_consent_authenticated": False,
            "real_node_connections_established": False,
        },
        "execution": {
            "mode": "OFFLINE_DRY_RUN", "external_dispatch": False,
            "production_deployed": False, "real_authorization_granted": False,
            "approval_granted": False,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    try:
        doc = json.loads(args.events.read_text(encoding="utf-8"))
        print(json.dumps(audit_events(doc, load_manifest(args.manifest)),
                         sort_keys=True, ensure_ascii=False, indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
