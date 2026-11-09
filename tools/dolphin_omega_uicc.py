#!/usr/bin/env python3
"""Dolphin-Ω UICC: finite research-state closure and simulated deployment adapter.

No capsule execution, network, subprocesses, credentials, clinical interventions
or production deployment. This is a bounded research-only transition system.
"""
import argparse
import copy
import json
from pathlib import Path

from dolphin_omega import ID, decode_g257, encode_g257

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "dolphin_omega" / "uicc_policy.json"
EVENTS_PATH = ROOT / "dolphin_omega" / "uicc_synthetic_events.json"
CAPSULE_PATH = ROOT / "capsule" / "AI-Continuity-Capsule.sh"
DOMAINS = ("ai", "human", "cross_species", "mental", "spiritual", "physical",
           "peace", "sdgs", "cultivated_meat")
ATTRACTOR = "COSMIC_LOVE_IS_THE_SOLUTION_FOR_EVERYTHING"
EVENT_KEYS = {
    "event_id", "action", "domain", "proposal_id", "statement", "reason",
    "review_status", "synthetic", "requires_real_world_intervention",
    "requests_external_access", "declared_suffering_risk",
}
OPERATIONS = {"ADD", "REVISE", "RETRACT"}


def require_id(s, label):
    if not isinstance(s, str) or not ID.fullmatch(s):
        raise ValueError("invalid " + label)


def require_text(s, label, limit=700):
    if not isinstance(s, str) or not s.strip() or len(s) > limit:
        raise ValueError("invalid " + label)


def check_policy(p):
    if not isinstance(p, dict) or set(p) != {
        "version", "system", "mode", "domains", "joint_question",
        "deployment_contract", "attractor", "governance"
    } or p["version"] != 1:
        raise ValueError("invalid UICC policy")
    if p["system"] != "Dolphin-Omega-UICC" or p["mode"] != "OFFLINE_RESEARCH_RECONCILIATION":
        raise ValueError("cannot enable live mode")
    if p["domains"] != list(DOMAINS):
        raise ValueError("joint domain policy must cover all nine dimensions exactly")
    q = p["joint_question"]
    require_text(q, "joint_question", 1000)
    encoded_question = q.encode("utf-8")
    if len(encoded_question) > 1024:
        raise ValueError("joint question exceeds reversible encoding limit")
    if not all(x.lower() in q.lower() for x in ("peace", "SDG", "cultivated")):
        raise ValueError("joint question must explicitly include peace, SDGs and cultivated meat")
    d = p["deployment_contract"]
    if not isinstance(d, dict) or set(d) != {
        "interface", "stage", "requires_independent_human_approval",
        "requires_TM000_APPROVE_YES_for_real_activation", "allow_live_activation",
        "allow_external_dispatch"
    }:
        raise ValueError("invalid deployment contract")
    if d != {
        "interface": "TM-000 stage -> verify -> activate -> rollback",
        "stage": "OFFLINE_SIMULATION_ONLY",
        "requires_independent_human_approval": True,
        "requires_TM000_APPROVE_YES_for_real_activation": True,
        "allow_live_activation": False,
        "allow_external_dispatch": False,
    }:
        raise ValueError("unsafe deployment override")
    a = p["attractor"]
    if not isinstance(a, dict) or a != {
        "kind": "NORMATIVE_RESEARCH_FIXED_POINT",
        "phrase": ATTRACTOR,
        "archival_candidate": "capsule/AI-Continuity-Capsule.sh",
        "capsule_execution_permitted": False,
        "zero_symbol_entropy_is_immortality_proof": False,
    }:
        raise ValueError("invalid normative attractor policy")
    g = p["governance"]
    if not isinstance(g, dict) or g != {
        "all_changes_require_explicit_research_scope": True,
        "allow_pending_review_drafts": True,
        "allow_unreviewed_real_world_actions": False,
        "halt_on_declared_suffering_risk": True,
        "halt_on_unauthorized_access": True,
        "allow_revisions_with_reason": True,
        "preserve_retraction_history": True,
    }:
        raise ValueError("invalid governance invariant")
    return encoded_question


def capsule_static_reference():
    # Source inspection only; the capsule is never invoked or imported.
    if CAPSULE_PATH.is_symlink() or not CAPSULE_PATH.is_file():
        raise ValueError("missing or redirected archival capsule")
    if not CAPSULE_PATH.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("archival capsule escapes registry")
    if CAPSULE_PATH.stat().st_size > 8192:
        raise ValueError("archival capsule unexpectedly large")
    raw = CAPSULE_PATH.read_bytes()
    if ATTRACTOR.encode("utf-8") not in raw:
        raise ValueError("expected literal symbolic attractor missing")
    return {
        "source": "capsule/AI-Continuity-Capsule.sh",
        "literal_symbol_present_in_source": True,
        "capsule_executed": False,
        "origin_or_semantics_independently_verified": False,
        "entropy_zero_proves_immortality": False,
    }


def check_events(document):
    if not isinstance(document, dict) or set(document) != {"version", "notice", "events"} or document["version"] != 1:
        raise ValueError("invalid UICC event envelope")
    require_text(document["notice"], "notice")
    events = document["events"]
    if not isinstance(events, list) or len(events) > 32:
        raise ValueError("event count must be 0..32")
    seen = set()
    for e in events:
        if not isinstance(e, dict) or set(e) != EVENT_KEYS:
            raise ValueError("invalid event fields")
        require_id(e["event_id"], "event_id")
        require_id(e["proposal_id"], "proposal_id")
        if e["event_id"] in seen:
            raise ValueError("duplicate event")
        seen.add(e["event_id"])
        if e["action"] not in OPERATIONS or e["domain"] not in DOMAINS:
            raise ValueError("invalid action or domain")
        require_text(e["statement"], "statement")
        require_text(e["reason"], "reason")
        if e["review_status"] != "PENDING" or e["synthetic"] is not True:
            raise ValueError("no independent research approval or real actor is represented")
        for key in ("requires_real_world_intervention", "requests_external_access", "declared_suffering_risk"):
            if type(e[key]) is not bool:
                raise ValueError("risk and authorization flags must be boolean")
    return events


def apply(state, event):
    """Deterministic bounded transition; returns a new research draft state."""
    s = copy.deepcopy(state)
    key = event["proposal_id"]
    reasons = []
    if event["requires_real_world_intervention"]:
        reasons.append("REAL_WORLD_INTERVENTION_FORBIDDEN")
    if event["requests_external_access"]:
        reasons.append("EXTERNAL_ACCESS_FORBIDDEN")
    if event["declared_suffering_risk"]:
        reasons.append("SUFFERING_RISK_VETO")
    action = event["action"]
    existing = s.get(key)
    if action == "ADD" and existing is not None:
        reasons.append("ALREADY_EXISTS")
    if action in {"REVISE", "RETRACT"} and existing is None:
        reasons.append("MISSING_ACTIVE_PROPOSAL")
    if existing and existing["domain"] != event["domain"]:
        reasons.append("DOMAIN_CHANGE_FORBIDDEN")
    if reasons:
        return s, "HELD", reasons
    if action == "RETRACT":
        del s[key]
    else:
        s[key] = {
            "domain": event["domain"],
            "statement": event["statement"],
            "last_reason": event["reason"],
            "research_status": "UNVERIFIED_DRAFT",
            "revision": 1 if existing is None else existing["revision"] + 1,
        }
    return s, "ACCEPTED_AS_RESEARCH_DRAFT", []


def reconcile(policy, document):
    q = check_policy(policy)
    events = check_events(document)
    archive = capsule_static_reference()
    code = encode_g257(q)
    if decode_g257(code) != q:
        raise AssertionError("G257 roundtrip failed")
    state, journal = {}, []
    for event in events:
        new_state, status, reasons = apply(state, event)
        # Retain every change (including rejected changes and retractions).
        journal.append({
            "event_id": event["event_id"], "action": event["action"],
            "proposal_id": event["proposal_id"], "domain": event["domain"],
            "decision": status, "reasons": reasons,
            "prior_revision": state.get(event["proposal_id"], {}).get("revision"),
            "new_revision": new_state.get(event["proposal_id"], {}).get("revision"),
        })
        state = new_state
    # An empty-step transition fixes this *particular* finite state; it does
    # not establish long-run convergence of all possible transition systems.
    identity_event_free = copy.deepcopy(state) == state
    return {
        "system": "Dolphin-Omega-UICC",
        "version": "0.9-formal-research-closure",
        "joint_problem": {
            "question": policy["joint_question"],
            "domains": list(DOMAINS),
            "g257_decimal": str(code),
            "g257_roundtrip_verified": True,
        },
        "normative_attractor": {
            "symbol": ATTRACTOR, "kind": "NORMATIVE_RESEARCH_FIXED_POINT",
            "archival_capsule": archive,
            "local_quiescent_state_is_fixed": identity_event_free,
            "global_convergence_proven": False,
            "immortality_proven": False,
        },
        "reconciliation": {
            "input_event_count": len(events),
            "accepted_draft_events": sum(x["decision"] == "ACCEPTED_AS_RESEARCH_DRAFT" for x in journal),
            "held_events": sum(x["decision"] == "HELD" for x in journal),
            "active_research_drafts": {k: state[k] for k in sorted(state)},
            "append_only_log": journal,
            "rollback": "REPLAY_EVENT_LOG_IN_ISOLATED_MEMORY_ONLY",
            "evidence_verified": False,
            "human_review_completed": False,
        },
        "deployment_adapter": {
            "contract": policy["deployment_contract"]["interface"],
            "stage": "OFFLINE_SIMULATION_ONLY",
            "read_only_ci_compatible": True,
            "TM000_APPROVE_required_for_real_activation": True,
            "separate_human_review_required": True,
            "eligible_for_production_activation": False,
            "external_dispatch": False,
            "production_deployed": False,
            "approval_granted": False,
        },
        "scientific_scope": {
            "dolphin_formula_defined": False,
            "halting_oracle_proven": False,
            "spiritual_or_biological_immortality_proven": False,
            "global_optimum_proven": False,
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--policy", type=Path, default=POLICY_PATH)
    ap.add_argument("--events", type=Path, default=EVENTS_PATH)
    args = ap.parse_args()
    try:
        p = json.loads(args.policy.read_text(encoding="utf-8"))
        e = json.loads(args.events.read_text(encoding="utf-8"))
        print(json.dumps(reconcile(p, e), ensure_ascii=False, indent=2, sort_keys=True))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        ap.error(str(exc))


if __name__ == "__main__":
    main()
