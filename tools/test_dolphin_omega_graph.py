#!/usr/bin/env python3
"""v0.6 falsification-graph safety: references, gaps, cycles and no deployment."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import dolphin_omega_graph as graph


class FalsifiabilityGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(graph.DEFAULT_GRAPH.read_text(encoding="utf-8"))
        cls.papers = json.loads(graph.DEFAULT_PAPERS.read_text(encoding="utf-8"))
        cls.queue = json.loads(graph.DEFAULT_QUEUE.read_text(encoding="utf-8"))

    def compile(self, g=None, p=None, q=None):
        return graph.build_report(
            self.doc if g is None else g,
            self.papers if p is None else p,
            self.queue if q is None else q,
        )

    def test_counts_and_coverage(self):
        r = self.compile()
        self.assertEqual(r["node_counts"], {
            "paper": 2, "hypothesis": 2, "proposed_check": 2,
            "contrary_question": 2,
        })
        self.assertEqual(r["edge_count"], 7)
        self.assertEqual(r["covered_domains"], ["cross_species", "human"])
        self.assertEqual(len(r["uncovered_domains"]), 4)
        self.assertEqual(len(r["research_chains"]), 2)

    def test_bounded_graph_does_not_prove_anything(self):
        r = self.compile()
        self.assertTrue(r["verification"]["graph_structure_valid"])
        for key in ("bibliography_live_verified", "full_text_reviewed",
                    "human_review_complete", "tests_run",
                    "causal_inference_verified", "cross_species_transfer_verified",
                    "immortality_proven", "dolphin_formula_defined",
                    "global_optimum_computed"):
            self.assertFalse(r["verification"][key])
        self.assertFalse(r["execution"]["external_dispatch"])
        self.assertFalse(r["execution"]["production_deployed"])
        self.assertFalse(r["execution"]["approval_granted"])

    def test_falsification_chains_are_plans_only(self):
        r = self.compile()
        for chain in r["research_chains"]:
            self.assertTrue(chain["falsification_plan_structure_valid"])
            self.assertFalse(chain["outcome_observed"])
            self.assertFalse(chain["scientifically_validated"])
            self.assertTrue(chain["would_count_against"])
            self.assertTrue(chain["contrary_question"])
            self.assertEqual(chain["human_review_state"], "AWAITING_INDEPENDENT_HUMAN_REVIEW")

    def test_cross_domain_edge_is_question_only(self):
        r = self.compile()
        self.assertEqual(len(r["cross_domain_links"]), 1)
        self.assertEqual(r["cross_domain_links"][0]["relation"], "CROSS_DOMAIN_QUESTION_ONLY")
        self.assertFalse(r["cross_domain_links"][0]["evidence_transfer_verified"])

    def test_reject_unknown_paper(self):
        g = copy.deepcopy(self.doc)
        g["nodes"][0]["paper_id"] = "invented-paper"
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_duplicate_paper_reference(self):
        g = copy.deepcopy(self.doc)
        g["nodes"].append({**g["nodes"][0], "id": "paper-aging-copy"})
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_missing_paper(self):
        g = copy.deepcopy(self.doc)
        g["nodes"] = [n for n in g["nodes"] if n["id"] != "paper-aging"]
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_mismatched_paper_domain(self):
        g = copy.deepcopy(self.doc)
        g["nodes"][0]["domain"] = "cross_species"
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_duplicate_node_id(self):
        g = copy.deepcopy(self.doc)
        g["nodes"][1]["id"] = g["nodes"][0]["id"]
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_missing_falsification_edge(self):
        g = copy.deepcopy(self.doc)
        g["edges"] = [e for e in g["edges"] if e["relation"] != "ADDRESSES_COUNTEREVIDENCE" or e["from"] != "check-aging"]
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_missing_disconfirming_observation(self):
        g = copy.deepcopy(self.doc)
        g["nodes"][1]["would_count_against"] = ""
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_forged_observed_or_verified_state(self):
        for key, value in (("status", "VERIFIED"),):
            g = copy.deepcopy(self.doc)
            g["nodes"][1][key] = value
            with self.assertRaises(ValueError):
                self.compile(g)
        g = copy.deepcopy(self.doc)
        g["nodes"][2]["observed_outcome"] = "proved"
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_human_intervention(self):
        g = copy.deepcopy(self.doc)
        g["nodes"][2]["human_intervention"] = True
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_cross_domain_evidence_transfer(self):
        g = copy.deepcopy(self.doc)
        g["edges"][6] = {
            "from": "paper-axolotl", "to": "hyp-aging", "relation": "MOTIVATES_QUESTION"
        }
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_missing_bridge_qualification(self):
        g = copy.deepcopy(self.doc)
        del g["edges"][6]["qualification"]
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_same_domain_bridge(self):
        g = copy.deepcopy(self.doc)
        g["edges"][6]["from"] = "hyp-aging"
        g["edges"][6]["to"] = "hyp-aging"
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_cycle(self):
        g = copy.deepcopy(self.doc)
        g["edges"].append({
            "from": "hyp-aging", "to": "hyp-axolotl",
            "relation": "CROSS_DOMAIN_QUESTION_ONLY",
            "qualification": "No evidence transfer is asserted.",
        })
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_extra_claim_fields(self):
        g = copy.deepcopy(self.doc)
        g["nodes"][1]["scientific_approval"] = True
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_dangling_edge(self):
        g = copy.deepcopy(self.doc)
        g["edges"][0]["to"] = "not-registered"
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_duplicate_edge(self):
        g = copy.deepcopy(self.doc)
        g["edges"].append(copy.deepcopy(g["edges"][0]))
        with self.assertRaises(ValueError):
            self.compile(g)

    def test_reject_forged_human_review(self):
        q = copy.deepcopy(self.queue)
        q["items"][0]["roles"][0]["status"] = "approved"
        with self.assertRaises(ValueError):
            self.compile(q=q)

    def test_deterministic(self):
        self.assertEqual(self.compile(), self.compile())

    def test_cli_offline(self):
        p = subprocess.run([sys.executable, str(Path(graph.__file__))],
                           check=True, capture_output=True, text=True, timeout=10)
        r = json.loads(p.stdout)
        self.assertEqual(r["version"], "0.6-falsifiability-graph")
        self.assertFalse(r["execution"]["production_deployed"])
        self.assertFalse(r["verification"]["immortality_proven"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
