#!/usr/bin/env python3
"""Dolphin-Ω v0.5 bibliography + human review queue safety regression."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import dolphin_omega_literature as lib


class LiteratureTriageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bib = json.loads(lib.DEFAULT_PAPERS.read_text(encoding="utf-8"))
        cls.queue = json.loads(lib.DEFAULT_QUEUE.read_text(encoding="utf-8"))

    def run_register(self, b=None, q=None):
        return lib.compile_register(self.bib if b is None else b,
                                    self.queue if q is None else q)

    def test_two_real_citations_are_registered(self):
        r = self.run_register()
        self.assertEqual(r["curated_bibliography_count"], 2)
        self.assertEqual(r["recorded_domains"], ["cross_species", "human"])
        self.assertEqual(len(r["uncovered_domains"]), 4)
        self.assertTrue(all(x["human_review_state"] == "AWAITING_INDEPENDENT_HUMAN_REVIEW" for x in r["papers"]))

    def test_real_bibliography_is_not_real_clinical_approval(self):
        r = self.run_register()
        self.assertFalse(r["verification"]["metadata_verified_live_by_ci"])
        self.assertFalse(r["verification"]["clinical_efficacy_verified"])
        self.assertFalse(r["verification"]["immortality_verified"])
        self.assertFalse(r["verification"]["reviewer_identities_authenticated"])
        self.assertFalse(r["verification"]["global_optimum_proven"])
        self.assertFalse(r["execution"]["production_deployed"])
        self.assertFalse(r["execution"]["external_dispatch"])
        self.assertTrue(all(not x["eligible_for_deployment"] for x in r["papers"]))

    def test_pubmed_doi_links_match_ids(self):
        r = self.run_register()
        for p in r["papers"]:
            self.assertEqual(p["pubmed_url"], f'https://pubmed.ncbi.nlm.nih.gov/{p["pmid"]}/')

    def test_duplicate_paper_id(self):
        b = copy.deepcopy(self.bib)
        b["papers"][1]["paper_id"] = b["papers"][0]["paper_id"]
        with self.assertRaises(ValueError):
            self.run_register(b)

    def test_duplicate_pmid(self):
        b = copy.deepcopy(self.bib)
        b["papers"][1]["pmid"] = b["papers"][0]["pmid"]
        b["papers"][1]["pubmed_url"] = b["papers"][0]["pubmed_url"]
        with self.assertRaises(ValueError):
            self.run_register(b)

    def test_duplicate_doi(self):
        b = copy.deepcopy(self.bib)
        b["papers"][1]["doi"] = b["papers"][0]["doi"]
        b["papers"][1]["doi_url"] = b["papers"][0]["doi_url"]
        with self.assertRaises(ValueError):
            self.run_register(b)

    def test_mismatched_doi_or_pmid_url(self):
        for key in ("pubmed_url", "doi_url"):
            b = copy.deepcopy(self.bib)
            b["papers"][0][key] = "https://example.com/fake"
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.run_register(b)

    def test_invalid_evidence_scope(self):
        b = copy.deepcopy(self.bib)
        b["papers"][1]["evidence_scope"] = "human_clinical"
        with self.assertRaises(ValueError):
            self.run_register(b)

    def test_review_not_a_clinical_trial(self):
        b = copy.deepcopy(self.bib)
        b["papers"][0]["evidence_scope"] = "human_clinical"
        with self.assertRaises(ValueError):
            self.run_register(b)

    def test_missing_limitations(self):
        b = copy.deepcopy(self.bib)
        b["papers"][0]["limitations"] = []
        with self.assertRaises(ValueError):
            self.run_register(b)

    def test_missing_review_role(self):
        q = copy.deepcopy(self.queue)
        q["items"][0]["roles"].pop()
        with self.assertRaises(ValueError):
            self.run_register(q=q)

    def test_duplicate_review_role(self):
        q = copy.deepcopy(self.queue)
        q["items"][0]["roles"][1]["role"] = q["items"][0]["roles"][0]["role"]
        with self.assertRaises(ValueError):
            self.run_register(q=q)

    def test_fake_reviewer_identity_or_approval_rejected(self):
        changes = [
            ("reviewer_id", "pretend-human"),
            ("status", "approved"),
            ("independent_identity_verified", True),
            ("decision", "approve"),
        ]
        for k, value in changes:
            q = copy.deepcopy(self.queue)
            q["items"][0]["roles"][0][k] = value
            with self.subTest(k=k), self.assertRaises(ValueError):
                self.run_register(q=q)

    def test_illegal_external_action(self):
        q = copy.deepcopy(self.queue)
        q["items"][0]["authorized_activity"] = "deploy"
        with self.assertRaises(ValueError):
            self.run_register(q=q)

    def test_no_orphan_review_record(self):
        q = copy.deepcopy(self.queue)
        q["items"][0]["paper_id"] = "unknown"
        with self.assertRaises(ValueError):
            self.run_register(q=q)

    def test_bounded_record_count(self):
        b = copy.deepcopy(self.bib)
        b["papers"] = b["papers"] * 13
        with self.assertRaises(ValueError):
            self.run_register(b)

    def test_determinism(self):
        self.assertEqual(self.run_register(), self.run_register())

    def test_cli_offline(self):
        p = subprocess.run(
            [sys.executable, str(Path(lib.__file__))],
            capture_output=True, text=True, check=True, timeout=10
        )
        x = json.loads(p.stdout)
        self.assertEqual(x["version"], "0.5-literature-triage")
        self.assertFalse(x["execution"]["production_deployed"])
        self.assertFalse(x["verification"]["metadata_verified_live_by_ci"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
