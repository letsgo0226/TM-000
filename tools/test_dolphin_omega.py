#!/usr/bin/env python3
"""No-network tests for Dolphin-Omega draft.

Only a local manifest is loaded, and no shell command or external node is run.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import dolphin_omega as d


class DolphinOmegaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes = d.load_manifest(d.DEFAULT_MANIFEST)

    def test_g257_roundtrip(self):
        for b in [b"", b"\x00", b"\xff\x00\xfe", b"Cosmic Love", "海豚型外星人公式".encode()]:
            self.assertEqual(d.decode_g257(d.encode_g257(b)), b)

    def test_invalid_g257(self):
        for n in [0, -1, 257, True, "123"]:
            with self.assertRaises(ValueError):
                d.decode_g257(n)

    def test_determinism_and_not_solver(self):
        a = d.plan("跨維度生命與資訊連續性", self.nodes)
        self.assertEqual(a, d.plan("跨維度生命與資訊連續性", self.nodes))
        self.assertEqual(a["dolphin_formula"]["status"], "UNDEFINED_NOT_EXECUTED")
        self.assertFalse(a["dolphin_formula"]["answer_generated"])
        self.assertFalse(a["deployment"]["production_deployed"])
        self.assertTrue(a["encoding"]["roundtrip_verified"])
        self.assertEqual(len(a["tasks"]), 6)

    def test_unapproved_external_node_is_not_used(self):
        a = d.plan("x", self.nodes)
        self.assertNotIn("external-future-node", a["node_selection"]["eligible_node_ids"])
        self.assertTrue(all(t["assigned_node"] != "external-future-node" for t in a["tasks"]))
        self.assertFalse(a["node_selection"]["dispatch_performed"])

    def test_opt_in_gate_rejects_unsafe_manifest(self):
        nodes = copy.deepcopy(self.nodes)
        nodes[-1]["enabled"] = True
        with tempfile.TemporaryDirectory() as temp:
            f = Path(temp) / "nodes.json"
            f.write_text(json.dumps({"version": 1, "nodes": nodes}), encoding="utf-8")
            with self.assertRaises(ValueError):
                d.load_manifest(f)

    def test_explicit_opt_in_does_not_dispatch(self):
        nodes = copy.deepcopy(self.nodes)
        nodes[-1]["enabled"] = nodes[-1]["explicit_opt_in"] = True
        result = d.plan("x", nodes)
        self.assertIn("external-future-node", result["node_selection"]["eligible_node_ids"])
        self.assertFalse(result["node_selection"]["external_execution"])
        self.assertFalse(result["node_selection"]["dispatch_performed"])

    def test_bounded_input(self):
        for q in ["", " ", "X" * 1025]:
            with self.assertRaises(ValueError):
                d.plan(q, self.nodes)

    def test_end_to_end_cli(self):
        p = subprocess.run([sys.executable, str(Path(d.__file__)), "--question", "跨維度永生研究"],
                           capture_output=True, text=True, check=True, timeout=10)
        r = json.loads(p.stdout)
        self.assertEqual(r["question"], "跨維度永生研究")
        self.assertTrue(r["encoding"]["roundtrip_verified"])
        self.assertFalse(r["deployment"]["production_deployed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
