#!/usr/bin/env python3
"""Bounded, side-effect-free ICC reproducibility regression tests."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CORE = ROOT / "capsule" / "Immortality-Continuity-Capsule.sh"
NODE = HERE / "icc_node.py"
spec = importlib.util.spec_from_file_location("icc_node", NODE)
node = importlib.util.module_from_spec(spec)
spec.loader.exec_module(node)


class ICCNodeTests(unittest.TestCase):
    def test_core_size_reproducibility_and_self_encoding(self):
        source = CORE.read_bytes()
        self.assertLessEqual(len(source), 2048)
        a = subprocess.check_output(["bash", str(CORE)], text=True)
        b = subprocess.check_output(["bash", str(CORE)], text=True)
        self.assertEqual(a, b)
        obj = json.loads(a)
        self.assertEqual(node.D(int(obj["godel257_source_hex"], 16)), source)
        self.assertTrue(obj["godel_roundtrip"] and obj["prime_roundtrip"])
        self.assertEqual(obj["H_final_symbolic"], 0)
        self.assertFalse(obj["medical_effect_proven"] or obj["global_control"])

    def test_godel_roundtrip_and_invalid_digits(self):
        for value in (b"", b"\x00", b"\xff", bytes(range(256)), b"same machine"):
            self.assertEqual(node.D(node.G(value)), value)
        with self.assertRaises(ValueError):
            node.D(257)

    def test_resume_and_rewind(self):
        original = node.genesis()
        step_a = node.apply(copy.deepcopy(original), 50)
        step_b = node.apply(step_a, 974)
        one_shot = node.apply(node.genesis(), 1024)
        self.assertEqual(step_b, one_shot)
        self.assertEqual(node.inverse(copy.deepcopy(step_b), 1024), original)
        cp = node.checkpoint(step_b)
        self.assertEqual(node.decode_checkpoint(cp), step_b)
        self.assertEqual(node.checkpoint(node.decode_checkpoint(cp)), cp)

    def test_tampering_and_provenance_limit(self):
        cp = node.checkpoint(node.apply(node.genesis(), 64))
        bad = copy.deepcopy(cp)
        bad["state_g257_hex"] = "2" + bad["state_g257_hex"][1:]
        with self.assertRaises(ValueError):
            node.decode_checkpoint(bad)
        state = node.decode_checkpoint(cp)
        state["tape"][0] = (state["tape"][0] + 1) % 257
        with self.assertRaises(ValueError):
            node.decode_checkpoint(node.checkpoint(state))
        with self.assertRaises(ValueError):
            node.decode_checkpoint({**cp, "state_bytes": cp["state_bytes"] + 1})
        self.assertFalse(node.witness(cp, "volunteer-A")["identity_authenticated"])

    def test_two_nodes_and_disagreement(self):
        cp = node.checkpoint(node.apply(node.genesis(), 256))
        a = node.witness(cp, "local-github")
        b = node.witness(copy.deepcopy(cp), "remote-opt-in")
        self.assertNotEqual(a["node_label"], b["node_label"])
        self.assertEqual(a["checkpoint"], b["checkpoint"])
        node.validate_witness(a)
        node.validate_witness(b)
        altered = node.witness(node.checkpoint(node.apply(node.genesis(), 257)), "remote-opt-in")
        self.assertNotEqual(a["checkpoint"], altered["checkpoint"])
        with self.assertRaises(ValueError):
            node.validate_witness({**a, "identity_authenticated": True})

    def test_cli_independent_run_compare_rewind(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            def run(*args, success=True):
                p = subprocess.run([sys.executable, str(NODE), *map(str, args)], text=True, capture_output=True)
                if success:
                    self.assertEqual(p.returncode, 0, p.stderr)
                else:
                    self.assertNotEqual(p.returncode, 0)
                return p
            run("init", "--output", d / "genesis.json")
            run("advance", "--input", d / "genesis.json", "--steps", 600, "--output", d / "a.json")
            run("advance", "--input", d / "genesis.json", "--steps", 600, "--output", d / "b.json")
            self.assertEqual((d / "a.json").read_bytes(), (d / "b.json").read_bytes())
            run("verify", "--input", d / "a.json")
            run("witness", "--input", d / "a.json", "--node", "github", "--output", d / "wa.json")
            run("witness", "--input", d / "b.json", "--node", "volunteer", "--output", d / "wb.json")
            c = run("compare", "--left", d / "wa.json", "--right", d / "wb.json")
            self.assertEqual(json.loads(c.stdout)["status"], "CONSISTENT")
            run("rewind", "--input", d / "a.json", "--steps", 600, "--output", d / "restore.json")
            self.assertEqual((d / "genesis.json").read_bytes(), (d / "restore.json").read_bytes())
            run("advance", "--input", d / "genesis.json", "--steps", 601, "--output", d / "offbyone.json")
            run("witness", "--input", d / "offbyone.json", "--node", "volunteer", "--output", d / "wbad.json")
            run("compare", "--left", d / "wa.json", "--right", d / "wbad.json", success=False)
            (d / "a.json").write_text('{"format":"ICC-CHECKPOINT-G257-v1","state_g257_hex":"ff","state_bytes":1}')
            run("verify", "--input", d / "a.json", success=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
