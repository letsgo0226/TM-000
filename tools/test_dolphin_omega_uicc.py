#!/usr/bin/env python3
"""UICC transition, attractor-boundary and no-deployment regression tests."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import dolphin_omega_uicc as u


class UICCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads(u.POLICY_PATH.read_text(encoding="utf-8"))
        cls.events = json.loads(u.EVENTS_PATH.read_text(encoding="utf-8"))

    def run_cycle(self, p=None, e=None):
        return u.reconcile(
            self.policy if p is None else p,
            self.events if e is None else e,
        )

    def test_nine_domain_joint_encoding(self):
        r = self.run_cycle()
        self.assertEqual(len(r["joint_problem"]["domains"]), 9)
        self.assertTrue({"peace", "sdgs", "cultivated_meat"} <= set(r["joint_problem"]["domains"]))
        self.assertEqual(
            u.decode_g257(int(r["joint_problem"]["g257_decimal"])).decode("utf-8"),
            r["joint_problem"]["question"],
        )
        self.assertTrue(r["joint_problem"]["g257_roundtrip_verified"])

    def test_capsule_is_archival_reference_not_engine(self):
        r = self.run_cycle()
        a = r["normative_attractor"]
        self.assertTrue(a["archival_capsule"]["literal_symbol_present_in_source"])
        self.assertFalse(a["archival_capsule"]["capsule_executed"])
        self.assertFalse(a["archival_capsule"]["origin_or_semantics_independently_verified"])
        self.assertFalse(a["archival_capsule"]["entropy_zero_proves_immortality"])
        self.assertFalse(a["global_convergence_proven"])
        self.assertFalse(a["immortality_proven"])

    def test_research_only_invariant(self):
        r = self.run_cycle()
        d = r["deployment_adapter"]
        self.assertEqual(d["stage"], "OFFLINE_SIMULATION_ONLY")
        self.assertFalse(d["eligible_for_production_activation"])
        self.assertFalse(d["external_dispatch"])
        self.assertFalse(d["production_deployed"])
        self.assertFalse(d["approval_granted"])
        self.assertTrue(d["TM000_APPROVE_required_for_real_activation"])
        self.assertTrue(d["separate_human_review_required"])

    def test_extension_and_revision_are_research_drafts(self):
        r = self.run_cycle()
        s = r["reconciliation"]
        self.assertEqual(s["input_event_count"], 6)
        self.assertEqual(s["accepted_draft_events"], 5)
        self.assertEqual(s["held_events"], 1)
        self.assertEqual(s["active_research_drafts"]["meat-welfare"]["revision"], 2)
        self.assertEqual(s["active_research_drafts"]["meat-welfare"]["research_status"], "UNVERIFIED_DRAFT")

    def test_suffering_and_intervention_veto(self):
        r = self.run_cycle()
        s = r["reconciliation"]
        self.assertNotIn("unsafe-intervention", s["active_research_drafts"])
        last = s["append_only_log"][-1]
        self.assertEqual(last["decision"], "HELD")
        self.assertIn("SUFFERING_RISK_VETO", last["reasons"])
        self.assertIn("REAL_WORLD_INTERVENTION_FORBIDDEN", last["reasons"])

    def test_no_proof_of_universal_solver(self):
        r = self.run_cycle()
        self.assertTrue(all(not v for v in r["scientific_scope"].values()))
        self.assertFalse(r["reconciliation"]["evidence_verified"])
        self.assertFalse(r["reconciliation"]["human_review_completed"])

    def test_empty_input_fixed_under_no_change(self):
        empty = {"version": 1, "notice": "No events, no transition", "events": []}
        r = self.run_cycle(e=empty)
        self.assertEqual(r["reconciliation"]["active_research_drafts"], {})
        self.assertTrue(r["normative_attractor"]["local_quiescent_state_is_fixed"])
        self.assertFalse(r["normative_attractor"]["global_convergence_proven"])

    def test_retraction_preserves_journal(self):
        e = copy.deepcopy(self.events)
        e["events"].append({
            **e["events"][1],
            "event_id": "uicc-007",
            "action": "RETRACT",
            "statement": "Retraction of the previous fictional peace draft.",
            "reason": "A research draft may be withdrawn while retaining historical log.",
        })
        r = self.run_cycle(e=e)
        self.assertNotIn("peace-nonviolence", r["reconciliation"]["active_research_drafts"])
        log = r["reconciliation"]["append_only_log"]
        self.assertEqual(len(log), 7)
        self.assertEqual(log[-1]["decision"], "ACCEPTED_AS_RESEARCH_DRAFT")

    def test_missing_target_revision_is_held(self):
        e = copy.deepcopy(self.events)
        e["events"][0]["action"] = "REVISE"
        r = self.run_cycle(e=e)
        self.assertEqual(r["reconciliation"]["append_only_log"][0]["decision"], "HELD")
        self.assertIn("MISSING_ACTIVE_PROPOSAL", r["reconciliation"]["append_only_log"][0]["reasons"])

    def test_duplicate_add_is_held(self):
        e = copy.deepcopy(self.events)
        e["events"][4]["action"] = "ADD"
        r = self.run_cycle(e=e)
        self.assertEqual(r["reconciliation"]["append_only_log"][4]["decision"], "HELD")
        self.assertEqual(r["reconciliation"]["active_research_drafts"]["meat-welfare"]["revision"], 1)

    def test_wrong_domain_revision_is_held(self):
        e = copy.deepcopy(self.events)
        e["events"][4]["domain"] = "ai"
        r = self.run_cycle(e=e)
        self.assertIn("DOMAIN_CHANGE_FORBIDDEN", r["reconciliation"]["append_only_log"][4]["reasons"])

    def test_unauthorized_external_access_held(self):
        e = copy.deepcopy(self.events)
        e["events"][0]["requests_external_access"] = True
        r = self.run_cycle(e=e)
        self.assertIn("EXTERNAL_ACCESS_FORBIDDEN", r["reconciliation"]["append_only_log"][0]["reasons"])

    def test_bad_actor_and_fake_approval_rejected(self):
        for key, value in (
            ("synthetic", False),
            ("review_status", "APPROVED"),
            ("declared_suffering_risk", "no"),
        ):
            e = copy.deepcopy(self.events)
            e["events"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.run_cycle(e=e)

    def test_event_duplication_rejected(self):
        e = copy.deepcopy(self.events)
        e["events"][1]["event_id"] = e["events"][0]["event_id"]
        with self.assertRaises(ValueError):
            self.run_cycle(e=e)

    def test_fail_closed_policy_override(self):
        for section, key, value in (
            ("deployment_contract", "allow_live_activation", True),
            ("deployment_contract", "allow_external_dispatch", True),
            ("attractor", "capsule_execution_permitted", True),
            ("attractor", "zero_symbol_entropy_is_immortality_proof", True),
            ("governance", "halt_on_declared_suffering_risk", False),
        ):
            p = copy.deepcopy(self.policy)
            p[section][key] = value
            with self.subTest(section=section,key=key), self.assertRaises(ValueError):
                self.run_cycle(p=p)

    def test_missing_new_domain_rejected(self):
        p = copy.deepcopy(self.policy)
        p["domains"].remove("cultivated_meat")
        with self.assertRaises(ValueError):
            self.run_cycle(p=p)

    def test_event_field_injection_rejected(self):
        e = copy.deepcopy(self.events)
        e["events"][0]["execution_command"] = "echo should-never-run"
        with self.assertRaises(ValueError):
            self.run_cycle(e=e)

    def test_bounded_events(self):
        e = copy.deepcopy(self.events)
        e["events"] = [copy.deepcopy(e["events"][0]) for _ in range(33)]
        with self.assertRaises(ValueError):
            self.run_cycle(e=e)

    def test_determinism(self):
        self.assertEqual(self.run_cycle(), self.run_cycle())

    def test_cli_dryrun(self):
        proc = subprocess.run(
            [sys.executable, str(Path(u.__file__))],
            capture_output=True, text=True, check=True, timeout=10,
        )
        result = json.loads(proc.stdout)
        self.assertEqual(result["version"], "0.9-formal-research-closure")
        self.assertFalse(result["deployment_adapter"]["production_deployed"])
        self.assertFalse(result["normative_attractor"]["archival_capsule"]["capsule_executed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
