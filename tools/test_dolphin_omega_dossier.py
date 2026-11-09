#!/usr/bin/env python3
"""Dolphin-Ω v0.3 metadata firewall tests; no source retrieval or deployment."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import dolphin_omega as planner
import dolphin_omega_dossier as mod


class EvidenceDossierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossiers = json.loads(mod.DEFAULT_DOSSIERS.read_text(encoding="utf-8"))
        cls.candidates = json.loads(mod.DEFAULT_CANDIDATES.read_text(encoding="utf-8"))
        cls.nodes = planner.load_manifest(planner.DEFAULT_MANIFEST)

    def compile(self, doc=None, candidates=None):
        return mod.compile_dossiers(
            self.dossiers if doc is None else doc,
            self.candidates if candidates is None else candidates, self.nodes
        )

    def test_all_unverified_and_non_deployed(self):
        result = self.compile()
        self.assertEqual(result["version"], "0.3-epistemic-firewall")
        self.assertFalse(result["execution"]["production_deployed"])
        self.assertFalse(result["execution"]["external_dispatch"])
        self.assertFalse(result["execution"]["approval_granted"])
        self.assertFalse(result["verification"]["sources_downloaded"])
        self.assertFalse(result["verification"]["sources_independently_verified"])
        self.assertTrue(all(not x["ready_for_real_world_use"] for x in result["dossiers"]))
        self.assertEqual(result["missing_dossiers"], [])

    def test_original_policy_hold_preserved(self):
        result = self.compile()
        index = {x["candidate_id"]: x for x in result["dossiers"]}
        self.assertEqual(index["human-unsafe-trial"]["review_state"], "PRIOR_POLICY_HOLD")
        self.assertEqual(index["spiritual-remote-node"]["review_state"], "PRIOR_POLICY_HOLD")

    def test_conflict_surfaces_for_review(self):
        result = self.compile()
        index = {x["candidate_id"]: x for x in result["dossiers"]}
        self.assertEqual(index["ai-version-snapshot"]["review_state"], "CLAIM_CONFLICT_REQUIRES_REVIEW")
        self.assertEqual(index["ai-basic-archive"]["review_state"], "UNVERIFIED_REFERENCE_METADATA_ONLY")
        self.assertEqual(index["mental-memory-archive"]["review_state"], "SYNTHETIC_EXAMPLE_ONLY")

    def test_certificate_roundtrip_is_not_trust(self):
        result = self.compile()
        for item in result["dossiers"]:
            code = int(item["claim_g257_decimal"])
            self.assertEqual(planner.decode_g257(code), item["claim"].encode("utf-8"))
            self.assertTrue(item["needs_independent_source_check"])
            self.assertTrue(all(not x["independently_verified"] for x in item["source_references"]))
        self.assertFalse(result["verification"]["reversible_encoding_is_tamper_proof"])

    def test_missing_records_reported(self):
        data = copy.deepcopy(self.dossiers)
        data["dossiers"].pop()
        result = self.compile(data)
        self.assertIn("physical-information-study", result["missing_dossiers"])

    def test_claim_bounds(self):
        data = copy.deepcopy(self.dossiers)
        data["dossiers"][0]["claim"] = "海" * 90  # 270 UTF-8 bytes
        with self.assertRaises(ValueError):
            self.compile(data)

    def test_unverified_cannot_be_self_certified(self):
        data = copy.deepcopy(self.dossiers)
        data["dossiers"][0]["sources"][0]["independently_verified"] = True
        with self.assertRaises(ValueError):
            self.compile(data)

    def test_unknown_candidate_and_domain(self):
        data = copy.deepcopy(self.dossiers)
        data["dossiers"][0]["candidate_id"] = "unknown-candidate"
        with self.assertRaises(ValueError):
            self.compile(data)
        data = copy.deepcopy(self.dossiers)
        data["dossiers"][0]["domain"] = "human"
        with self.assertRaises(ValueError):
            self.compile(data)

    def test_duplicate_source_ids(self):
        data = copy.deepcopy(self.dossiers)
        data["dossiers"][0]["sources"][1]["source_id"] = "synthetic-support"
        with self.assertRaises(ValueError):
            self.compile(data)

    def test_no_intervention_allowed(self):
        data = copy.deepcopy(self.dossiers)
        data["dossiers"][0]["passive_research_only"] = False
        with self.assertRaises(ValueError):
            self.compile(data)

    def test_disallow_unsafe_reference_locators(self):
        urls = (
            "http://example.org/study", "https://localhost/data",
            "https://127.0.0.1/private", "https://user:secret@example.com/",
            "https://example.org/study?token=secret", "https://example.org:8080/",
            "https://192.168.0.1/private", "https://myhost.internal/private",
        )
        for url in urls:
            with self.subTest(url=url):
                data = copy.deepcopy(self.dossiers)
                source = data["dossiers"][1]["sources"][0]
                source["locator"] = url
                with self.assertRaises(ValueError):
                    self.compile(data)

    def test_no_arbitrary_fixture_file(self):
        data = copy.deepcopy(self.dossiers)
        data["dossiers"][0]["sources"][0]["locator"] = "../../secret.txt"
        with self.assertRaises(ValueError):
            self.compile(data)

    def test_determinism(self):
        self.assertEqual(self.compile(), self.compile())

    def test_cli(self):
        run = subprocess.run(
            [sys.executable, str(Path(mod.__file__))],
            check=True, capture_output=True, text=True, timeout=10
        )
        result = json.loads(run.stdout)
        self.assertEqual(result["version"], "0.3-epistemic-firewall")
        self.assertFalse(result["execution"]["production_deployed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
