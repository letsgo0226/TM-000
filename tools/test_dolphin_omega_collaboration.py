#!/usr/bin/env python3
"""v0.8 offline-only collaboration authorization and audit regression."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import dolphin_omega as planner
import dolphin_omega_collaboration as collaboration


class CollaborationProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = json.loads(collaboration.DEFAULT_EVENTS.read_text(encoding="utf-8"))
        cls.nodes = planner.load_manifest(planner.DEFAULT_MANIFEST)

    def run_protocol(self, doc=None, nodes=None):
        return collaboration.audit_events(
            self.events if doc is None else doc,
            self.nodes if nodes is None else nodes,
        )

    def assert_event(self, i, decision, reason):
        row = self.run_protocol()["audit"][i - 1]
        self.assertEqual((row["decision"], row["reason"]), (decision, reason))
        self.assertFalse(row["executed"])
        self.assertFalse(row["identity_authenticated"])
        self.assertFalse(row["real_authorization_granted"])

    def test_fifteen_events_and_no_live_authorization(self):
        r = self.run_protocol()
        self.assertEqual(r["audit_entries"], 15)
        self.assertEqual(len(r["audit"]), 15)
        self.assertEqual(r["active_simulated_grant_ids"], [])
        for flag in ("external_dispatch", "production_deployed", "real_authorization_granted", "approval_granted"):
            self.assertFalse(r["execution"][flag])
        self.assertFalse(r["verification"]["owner_identities_authenticated"])
        self.assertFalse(r["verification"]["third_party_consent_authenticated"])
        self.assertFalse(r["verification"]["log_immutability_proven"])

    def test_simulation_grant_not_real_identity(self):
        self.assert_event(1, "RECORDED_SIMULATED_GRANT", "DECLARATION_ONLY_NOT_AUTHENTICATED")
        self.assert_event(2, "ALLOW_SIMULATION", "NO_REAL_EXECUTION_AUTHORITY")

    def test_out_of_scope_write_does_not_run(self):
        self.assert_event(3, "DENY", "SCOPE_MISMATCH")

    def test_wrong_grantee_denied(self):
        self.assert_event(4, "DENY", "WRONG_DECLARED_GRANTEE")

    def test_wrong_issuer_cannot_revoke(self):
        self.assert_event(5, "DENY", "WRONG_DECLARED_ISSUER")

    def test_correct_revoke_and_followup_denial(self):
        self.assert_event(6, "RECORDED_SIMULATED_REVOCATION", "IRREVERSIBLE_FOR_GRANT_ID")
        self.assert_event(7, "DENY", "REVOKED_GRANT")

    def test_boundary_expiry_denied(self):
        self.assert_event(9, "DENY", "EXPIRED_GRANT")

    def test_external_optin_placeholder_never_eligible(self):
        self.assert_event(10, "DENY", "EXTERNAL_NODE_UNSUPPORTED")
        self.assert_event(11, "DENY", "GRANT_NOT_ACTIVE")

    def test_missing_consent_denied(self):
        self.assert_event(12, "DENY", "MISSING_DECLARED_CONSENT")
        self.assert_event(13, "DENY", "GRANT_NOT_ACTIVE")

    def test_prohibited_action_denied(self):
        self.assert_event(14, "DENY", "ACTION_NOT_ALLOWED")

    def test_guessed_grant_denied(self):
        self.assert_event(15, "DENY", "UNKNOWN_GRANT")

    def test_rejected_grant_id_cannot_be_reused(self):
        d = copy.deepcopy(self.events)
        ev = copy.deepcopy(d["events"][0])
        ev.update(seq=16, event_id="event-16", at="2026-11-09T12:16:00Z")
        d["events"].append(ev)
        with self.assertRaises(ValueError):
            self.run_protocol(d)

    def test_replayed_event_id_denied(self):
        d = copy.deepcopy(self.events)
        d["events"][1]["event_id"] = d["events"][0]["event_id"]
        with self.assertRaises(ValueError):
            self.run_protocol(d)

    def test_gapped_sequence_denied(self):
        d = copy.deepcopy(self.events)
        d["events"][3]["seq"] = 999
        with self.assertRaises(ValueError):
            self.run_protocol(d)

    def test_out_of_order_event_denied(self):
        d = copy.deepcopy(self.events)
        d["events"][2]["at"] = "2026-11-09T12:00:00Z"
        with self.assertRaises(ValueError):
            self.run_protocol(d)

    def test_non_utc_or_noncanonical_timestamp_denied(self):
        for timestamp in ("2026-11-09T12:00:00+00:00", "2026-11-09T12:00:00",
                          "2026-02-31T12:00:00Z", "2026-11-09T12:00Z"):
            with self.subTest(timestamp=timestamp):
                d = copy.deepcopy(self.events)
                d["events"][0]["at"] = timestamp
                with self.assertRaises(ValueError):
                    self.run_protocol(d)

    def test_grant_expiry_in_past_denied(self):
        d = copy.deepcopy(self.events)
        d["events"][0]["expires_at"] = d["events"][0]["at"]
        row = self.run_protocol(d)["audit"][0]
        self.assertEqual(row["reason"], "EXPIRED_OR_INVALID_GRANT_WINDOW")
        self.assertEqual(self.run_protocol(d)["audit"][1]["decision"], "DENY")

    def test_fake_verified_identity_rejected(self):
        d = copy.deepcopy(self.events)
        d["events"][0]["owner_identity_authenticated"] = True
        with self.assertRaises(ValueError):
            self.run_protocol(d)

    def test_non_boolean_consent_rejected(self):
        d = copy.deepcopy(self.events)
        d["events"][0]["owner_consent_declared"] = "true"
        with self.assertRaises(ValueError):
            self.run_protocol(d)

    def test_surprise_event_fields_rejected(self):
        d = copy.deepcopy(self.events)
        d["events"][1]["execute_command"] = "rm -rf /"
        with self.assertRaises(ValueError):
            self.run_protocol(d)

    def test_unknown_node_rejected_with_audit_reason(self):
        d = copy.deepcopy(self.events)
        d["events"][0]["node_id"] = "unknown-node"
        r = self.run_protocol(d)
        self.assertEqual(r["audit"][0]["reason"], "UNKNOWN_NODE")
        self.assertEqual(r["audit"][1]["decision"], "DENY")

    def test_disabled_node_denied(self):
        nodes = copy.deepcopy(self.nodes)
        for n in nodes:
            if n["id"] == "local-research-simulator":
                n["enabled"] = False
        r = self.run_protocol(nodes=nodes)
        self.assertEqual(r["audit"][0]["reason"], "NODE_NOT_ELIGIBLE")
        self.assertEqual(r["audit"][1]["decision"], "DENY")

    def test_external_even_if_marked_optin_remains_simulation_blocked(self):
        nodes = copy.deepcopy(self.nodes)
        for n in nodes:
            if n["id"] == "external-future-node":
                n["enabled"] = True
                n["explicit_opt_in"] = True
        r = self.run_protocol(nodes=nodes)
        self.assertEqual(r["audit"][9]["reason"], "EXTERNAL_NODE_UNSUPPORTED")
        self.assertFalse(r["execution"]["external_dispatch"])

    def test_revoke_unknown_grant_denied(self):
        d = copy.deepcopy(self.events)
        d["events"][5]["grant_id"] = "not-a-grant"
        r = self.run_protocol(d)
        self.assertEqual(r["audit"][5]["reason"], "UNKNOWN_GRANT")
        self.assertEqual(r["audit"][6]["decision"], "ALLOW_SIMULATION")

    def test_audit_chain_is_deterministic(self):
        a = self.run_protocol()
        b = self.run_protocol()
        self.assertEqual(a, b)
        self.assertEqual(len(a["last_audit_digest"]), 64)
        self.assertEqual(a["audit"][-1]["audit_chain_digest"], a["last_audit_digest"])

    def test_audit_changes_if_event_changes_but_is_not_tamperproof(self):
        d = copy.deepcopy(self.events)
        d["events"][2]["action"] = "prepare_unverified_review_draft"
        changed = self.run_protocol(d)
        self.assertNotEqual(self.run_protocol()["last_audit_digest"], changed["last_audit_digest"])
        self.assertFalse(changed["verification"]["log_immutability_proven"])

    def test_cli_offline_non_deployment(self):
        process = subprocess.run(
            [sys.executable, str(Path(collaboration.__file__))],
            check=True, capture_output=True, text=True, timeout=10,
        )
        r = json.loads(process.stdout)
        self.assertEqual(r["version"], "0.8-simulated-consent-protocol")
        self.assertFalse(r["execution"]["real_authorization_granted"])
        self.assertFalse(r["execution"]["production_deployed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
