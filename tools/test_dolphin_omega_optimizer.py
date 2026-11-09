#!/usr/bin/env python3
"""Offline security and scoring regression for synthetic Dolphin-Ω v0.2."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import dolphin_omega as d
import dolphin_omega_optimizer as opt


class BoundedOptimizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = d.load_manifest(d.DEFAULT_MANIFEST)
        cls.fixture = json.loads(opt.DEFAULT_CANDIDATES.read_text(encoding="utf-8"))

    def evaluate(self, data=None, nodes=None):
        return opt.evaluate(self.fixture if data is None else data,
                            self.manifest if nodes is None else nodes)

    def test_expected_research_only_status(self):
        r = self.evaluate()
        self.assertEqual(r["execution"]["mode"], "OFFLINE_DRY_RUN")
        self.assertFalse(r["execution"]["production_deployed"])
        self.assertFalse(r["execution"]["external_dispatch"])
        self.assertFalse(r["execution"]["approval_granted"])
        self.assertFalse(r["claims"]["empirical_review_performed"])
        self.assertTrue(all(x["is_hypothetical"] and not x["independently_verified"]
                            for x in r["results"]))

    def test_pareto_dominance_and_within_domain_winner(self):
        r = self.evaluate()
        self.assertEqual(r["pareto_frontiers_by_domain"]["ai"], ["ai-version-snapshot"])
        self.assertEqual(r["synthetic_winners_by_domain"]["ai"], "ai-version-snapshot")
        self.assertEqual(r["synthetic_winners_by_domain"]["human"], None)
        self.assertEqual(r["synthetic_winners_by_domain"]["spiritual"], None)

    def test_safety_veto(self):
        r = self.evaluate()
        human = next(x for x in r["results"] if x["id"] == "human-unsafe-trial")
        self.assertEqual(human["status"], "HOLD")
        self.assertIn("SAFETY_VETO", human["hold_reasons"])
        self.assertIn("SUFFERING_LIMIT", human["hold_reasons"])
        self.assertIsNone(human["synthetic_priority_index"])

    def test_disabled_node_is_held(self):
        r = self.evaluate()
        remote = next(x for x in r["results"] if x["id"] == "spiritual-remote-node")
        self.assertIn("NODE_NOT_ELIGIBLE", remote["hold_reasons"])

    def test_opt_in_does_not_execute(self):
        nodes = copy.deepcopy(self.manifest)
        nodes[-1]["enabled"] = nodes[-1]["explicit_opt_in"] = True
        r = self.evaluate(nodes=nodes)
        self.assertEqual(r["synthetic_winners_by_domain"]["spiritual"], "spiritual-remote-node")
        self.assertFalse(r["execution"]["external_dispatch"])

    def test_unreviewed_or_unethical_is_held(self):
        data = copy.deepcopy(self.fixture)
        data["candidates"][0]["ethics_review"] = "pending"
        data["candidates"][0]["evidence_review"] = "pending"
        r = self.evaluate(data=data)
        first = r["results"][0]
        self.assertIn("ETHICS_REVIEW_NOT_CLEARED", first["hold_reasons"])
        self.assertIn("EVIDENCE_REVIEW_NOT_CLEARED", first["hold_reasons"])

    def test_fail_closed_bad_metrics_and_flags(self):
        data = copy.deepcopy(self.fixture)
        data["candidates"][0]["metrics"]["risk"] = True
        with self.assertRaises(ValueError):
            self.evaluate(data=data)
        data = copy.deepcopy(self.fixture)
        del data["candidates"][0]["safety_flags"]["unacceptable_harm"]
        with self.assertRaises(ValueError):
            self.evaluate(data=data)

    def test_reject_nonhypothetical_and_duplicate_ids(self):
        data = copy.deepcopy(self.fixture)
        data["candidates"][0]["hypothetical"] = False
        with self.assertRaises(ValueError):
            self.evaluate(data=data)
        data = copy.deepcopy(self.fixture)
        data["candidates"][1]["id"] = data["candidates"][0]["id"]
        with self.assertRaises(ValueError):
            self.evaluate(data=data)

    def test_determinism(self):
        self.assertEqual(self.evaluate(), self.evaluate())

    def test_cli_no_deployment(self):
        p = subprocess.run([sys.executable, str(Path(opt.__file__))],
                           capture_output=True, text=True, check=True, timeout=10)
        r = json.loads(p.stdout)
        self.assertEqual(r["version"], "0.2-hypothetical-prioritization")
        self.assertFalse(r["execution"]["production_deployed"])
        self.assertFalse(r["claims"]["general_or_global_optimum"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
