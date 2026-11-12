#!/usr/bin/env python3
"""G9 contract and negative-control tests. No external services or live payloads."""
import importlib.util
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / 'deployment/G9_Semantic_Contracts_core.py'
COMPACT = ROOT / 'deployment/Universal_G_G9_Semantic_Plaintext_2KB.sh'
READABLE = ROOT / 'deployment/Universal_G_G9_Semantic_Plaintext.sh'

spec = importlib.util.spec_from_file_location('g9_semantic_core', MODULE)
g9 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g9)


def run(command, optimized=False):
    env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'HOME': '/tmp',
           'PYTHONOPTIMIZE': '2' if optimized else '0', 'LANG': 'C.UTF-8'}
    return subprocess.run(command, capture_output=True, text=True, timeout=20,
                          env=env, cwd=ROOT, check=True)


class G9Tests(unittest.TestCase):
    def test_ai_transition_all_states(self):
        self.assertEqual(g9.verify_ai()[0], 24)

    def test_ai_trace_all_length_three(self):
        self.assertEqual(g9.verify_ai()[1], 384)

    def test_ai_representation_is_injective(self):
        states = [g9.encode_ai(s) for s in g9.STATES]
        self.assertEqual(len(states), len(set(states)))

    def test_ai_observation_equivalence(self):
        for state in g9.STATES:
            self.assertEqual(g9.observe_source(state), g9.observe_target(g9.encode_ai(state)))

    def test_ai_blocks_unconsented_processing(self):
        state = (1, False)
        expected = g9.encode_ai(g9.source_step(state, 'execute'))
        mask, auth = g9.encode_ai(state)
        self.assertNotEqual(expected, (mask // 2, auth))

    def test_ai_broken_transition_rejected(self):
        def wrong(s, a):
            return (s[0] // 2, s[1]) if a == 'execute' else g9.target_step(s, a)
        with self.assertRaises(ValueError):
            g9.verify_ai(wrong)

    def test_philosophy_four_quantified_formulas(self):
        self.assertEqual(g9.verify_philosophy(), 4)

    def test_philosophy_interpretation_matched(self):
        for source, target in g9.PRED_TRANSLATION.items():
            self.assertEqual({g9.NAME[i] for i in g9.SRC_PRED[source]}, g9.TGT_PRED[target])

    def test_philosophy_wrong_care_extension_rejected(self):
        bad = {**g9.TGT_PRED, 'ProvidesCare': {'reader', 'friend'}}
        with self.assertRaises(ValueError):
            g9.verify_philosophy(bad)

    def test_philosophy_wrong_need_extension_rejected(self):
        bad = {**g9.TGT_PRED, 'NeedsHelp': {'reader'}}
        with self.assertRaises(ValueError):
            g9.verify_philosophy(bad)

    def test_welfare_four_records(self):
        self.assertEqual(g9.verify_welfare(), 4)

    def test_welfare_uncertainty_not_safe(self):
        record = next(x for x in g9.WELFARE if x['risk'] == 'uncertain')
        self.assertTrue(g9.target_welfare(record)['requires_review'])

    def test_welfare_wrong_uncertainty_rejected(self):
        def wrong(record):
            result = g9.target_welfare(record)
            if record['risk'] == 'uncertain':
                result['requires_review'] = False
            return result
        with self.assertRaises(ValueError):
            g9.verify_welfare(mapper=wrong)

    def test_welfare_missing_provenance_rejected(self):
        def wrong(record):
            d = g9.target_welfare(record)
            d.pop('provenance')
            return d
        with self.assertRaises(ValueError):
            g9.verify_welfare(mapper=wrong)

    def test_welfare_wrong_provenance_rejected(self):
        def wrong(record):
            d = g9.target_welfare(record)
            d['provenance'] = 'tampered'
            return d
        with self.assertRaises(ValueError):
            g9.verify_welfare(mapper=wrong)

    def test_welfare_duplicate_records_rejected(self):
        with self.assertRaises(ValueError):
            g9.verify_welfare(records=(g9.WELFARE[0], g9.WELFARE[0]))

    def test_welfare_unsupported_risk_rejected(self):
        bad = ({**g9.WELFARE[0], 'risk': 'certified_immortal'},)
        with self.assertRaises(ValueError):
            g9.verify_welfare(records=bad)

    def test_compact_is_plaintext_single_line_under_2kb(self):
        b = COMPACT.read_bytes()
        self.assertLessEqual(len(b), 2048)
        self.assertEqual(b.count(b'\n'), 1)
        self.assertTrue(b.endswith(b'\n'))
        for forbidden in (b'zlib', b'base64', b'eval(', b'exec('):
            self.assertNotIn(forbidden, b)
        subprocess.run(['bash', '-n', str(COMPACT)], check=True, timeout=10)

    def test_all_three_implementations_match(self):
        target = json.loads(run([sys.executable, str(MODULE)]).stdout)
        self.assertEqual(target, json.loads(run(['bash', str(COMPACT)]).stdout))
        self.assertEqual(target, json.loads(run(['bash', str(READABLE)]).stdout))
        self.assertEqual(target['negative_controls'], 4)
        self.assertFalse(target['production_deployed'])
        self.assertFalse(target['real_world_semantics_proved'])
        self.assertFalse(target['human_or_ai_immortality_proved'])
        self.assertFalse(target['divine_identity_proved'])

    def test_python_optimization_cannot_skip_checks(self):
        target = json.loads(run(['bash', str(COMPACT)], optimized=True).stdout)
        self.assertEqual(target['ai_trace_checks'], 384)
        self.assertEqual(target, json.loads(run([sys.executable, str(MODULE)], optimized=True).stdout))


if __name__ == '__main__':
    unittest.main(verbosity=2)
