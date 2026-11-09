#!/usr/bin/env python3
"""Fail-closed v0.4 offline snapshot integrity and review metadata tests."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import dolphin_omega as planner
import dolphin_omega_review as review


class ReviewPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(review.DEFAULT_REVIEWS.read_text(encoding="utf-8"))
        cls.dossiers = json.loads(review.DEFAULT_DOSSIERS.read_text(encoding="utf-8"))
        cls.candidates = json.loads(review.DEFAULT_CANDIDATES.read_text(encoding="utf-8"))
        cls.nodes = planner.load_manifest(planner.DEFAULT_MANIFEST)

    def audit(self, packet=None, dossiers=None):
        return review.audit(
            self.packet if packet is None else packet,
            self.dossiers if dossiers is None else dossiers,
            self.candidates, self.nodes,
        )

    def test_sample_is_not_real_verification(self):
        result = self.audit()
        self.assertEqual(result["version"], "0.4-offline-review-packet")
        self.assertFalse(result["execution"]["production_deployed"])
        self.assertFalse(result["execution"]["external_dispatch"])
        self.assertFalse(result["execution"]["approval_granted"])
        self.assertFalse(result["verification"]["source_content_fetched"])
        self.assertFalse(result["verification"]["independent_reviewer_identities_verified"])
        self.assertFalse(result["verification"]["scientific_claims_verified"])
        self.assertFalse(result["verification"]["sha256_proves_source_authenticity"])
        self.assertTrue(result["verification"]["human_review_still_required"])

    def test_two_fictional_teams_are_only_recorded(self):
        row = self.audit()["packet_results"][0]
        self.assertEqual(row["review_state"], "MULTIPLE_SYNTHETIC_ATTESTATIONS_RECORDED")
        self.assertTrue(row["snapshot_byte_integrity"])
        self.assertEqual(row["review_count"], 2)
        self.assertEqual(row["distinct_declared_team_count"], 2)
        self.assertFalse(row["reviewer_identities_authenticated"])
        self.assertFalse(row["source_origin_authenticated"])
        self.assertFalse(row["scientific_claim_verified"])
        self.assertFalse(row["eligible_for_deployment"])

    def test_different_hash_prevents_clearance(self):
        packet = copy.deepcopy(self.packet)
        packet["snapshots"][0]["sha256"] = "0" * 64
        row = self.audit(packet)["packet_results"][0]
        self.assertEqual(row["review_state"], "SNAPSHOT_INTEGRITY_MISMATCH")
        self.assertFalse(row["snapshot_byte_integrity"])
        self.assertFalse(row["eligible_for_deployment"])

    def test_one_reviewer_not_enough(self):
        packet = copy.deepcopy(self.packet)
        packet["reviews"].pop()
        self.assertEqual(self.audit(packet)["packet_results"][0]["review_state"],
                         "INSUFFICIENT_RECORDED_REVIEWERS")

    def test_same_team_not_enough(self):
        packet = copy.deepcopy(self.packet)
        packet["reviews"][1]["team_id"] = packet["reviews"][0]["team_id"]
        self.assertEqual(self.audit(packet)["packet_results"][0]["review_state"],
                         "INSUFFICIENT_RECORDED_REVIEWERS")

    def test_conflict_of_interest_not_counted(self):
        packet = copy.deepcopy(self.packet)
        packet["reviews"][1]["conflict_declared"] = True
        row = self.audit(packet)["packet_results"][0]
        self.assertEqual(row["review_state"], "INSUFFICIENT_RECORDED_REVIEWERS")
        self.assertEqual(row["non_conflicted_review_count"], 1)

    def test_disagreement_flagged(self):
        packet = copy.deepcopy(self.packet)
        packet["reviews"][0]["verdict"] = "supports_claimed"
        packet["reviews"][1]["verdict"] = "contradicts_claimed"
        self.assertEqual(self.audit(packet)["packet_results"][0]["review_state"],
                         "DISAGREEMENT_REQUIRES_HUMAN_REVIEW")

    def test_prior_policy_hold_cannot_be_overridden(self):
        packet = copy.deepcopy(self.packet)
        dossier_doc = copy.deepcopy(self.dossiers)
        human = next(d for d in dossier_doc["dossiers"] if d["candidate_id"] == "human-unsafe-trial")
        human["sources"][0] = copy.deepcopy(
            next(d for d in dossier_doc["dossiers"] if d["candidate_id"] == "ai-basic-archive")["sources"][0]
        )
        packet["snapshots"][0]["candidate_id"] = "human-unsafe-trial"
        for item in packet["reviews"]:
            item["candidate_id"] = "human-unsafe-trial"
        row = self.audit(packet, dossier_doc)["packet_results"][0]
        self.assertEqual(row["review_state"], "PRIOR_POLICY_HOLD")
        self.assertFalse(row["eligible_for_deployment"])

    def test_reject_escape_paths(self):
        for value in (
            "/etc/passwd",
            "../review_snapshots/synthetic-context.txt",
            "dolphin_omega/review_snapshots/../README.md",
            "dolphin_omega/review_snapshots/../../private.txt",
            "dolphin_omega\\review_snapshots\\synthetic-context.txt",
        ):
            with self.subTest(value=value):
                packet = copy.deepcopy(self.packet)
                packet["snapshots"][0]["snapshot_path"] = value
                with self.assertRaises(ValueError):
                    self.audit(packet)

    def test_reject_nonmatching_quote(self):
        packet = copy.deepcopy(self.packet)
        packet["reviews"][0]["checked_excerpt"] = "a nonexistent line in snapshot"
        with self.assertRaises(ValueError):
            self.audit(packet)

    def test_reject_duplicate_review_id(self):
        packet = copy.deepcopy(self.packet)
        packet["reviews"][1]["review_id"] = packet["reviews"][0]["review_id"]
        with self.assertRaises(ValueError):
            self.audit(packet)

    def test_reject_duplicate_reviewers(self):
        packet = copy.deepcopy(self.packet)
        packet["reviews"][1]["reviewer_id"] = packet["reviews"][0]["reviewer_id"]
        with self.assertRaises(ValueError):
            self.audit(packet)

    def test_reject_unknown_dossier_source(self):
        packet = copy.deepcopy(self.packet)
        packet["snapshots"][0]["source_id"] = "unregistered-reference"
        with self.assertRaises(ValueError):
            self.audit(packet)

    def test_reject_forged_reviewer_verification(self):
        packet = copy.deepcopy(self.packet)
        packet["reviews"][1]["synthetic"] = False
        with self.assertRaises(ValueError):
            self.audit(packet)

    def test_reject_invalid_sha(self):
        packet = copy.deepcopy(self.packet)
        packet["snapshots"][0]["sha256"] = "not-sha"
        with self.assertRaises(ValueError):
            self.audit(packet)

    def test_reject_boolean_conflict_declaration_wrong_type(self):
        packet = copy.deepcopy(self.packet)
        packet["reviews"][0]["conflict_declared"] = 0
        with self.assertRaises(ValueError):
            self.audit(packet)

    def test_deterministic(self):
        self.assertEqual(self.audit(), self.audit())

    def test_cli_is_offline(self):
        run = subprocess.run(
            [sys.executable, str(Path(review.__file__))],
            check=True, capture_output=True, text=True, timeout=10,
        )
        output = json.loads(run.stdout)
        self.assertEqual(output["version"], "0.4-offline-review-packet")
        self.assertFalse(output["execution"]["external_dispatch"])
        self.assertFalse(output["execution"]["production_deployed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
