#!/usr/bin/env python3
"""G10 offline audit tests. Negative cases never contact external sources."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'deployment'))
from G10_Evidence_Provenance_core import (  # noqa: E402
    EXPECTED_RECORDS, REPORT, validate_ledger, validate_report
)

LEDGER = json.loads((ROOT / 'deployment/G10_evidence_ledger.json').read_text())
ONE = ROOT / 'deployment/Universal_G_G10_Provenance_Plaintext_2KB.sh'


class G10Test(unittest.TestCase):
    def edit(self, change):
        a = copy.deepcopy(LEDGER)
        change(a)
        with self.assertRaises(ValueError):
            validate_ledger(a)

    def test_baseline_ledger(self):
        self.assertEqual(validate_ledger(LEDGER), (3, 2))
        self.assertEqual(len(EXPECTED_RECORDS), 3)

    def test_report_shape(self):
        validate_report(REPORT)

    def test_publisher_spoofing_rejected(self):
        self.edit(lambda a: a['records'][0].update(publisher='Unverified Lab'))

    def test_hostname_spoofing_rejected(self):
        self.edit(lambda a: a['records'][1].update(url='https://www.who.int.evil.example/publication'))

    def test_research_domain_swap_rejected(self):
        self.edit(lambda a: a['records'][0].update(domain='human_longevity'))

    def test_document_fact_swap_rejected(self):
        self.edit(lambda a: a['records'][1].update(fact_code='CELL_BASED_FOOD_ZERO_SUFFERING_PROVEN'))

    def test_forged_publication_date_rejected(self):
        self.edit(lambda a: a['records'][0].update(published='2025-01-26'))

    def test_observation_precision_forgery_rejected(self):
        self.edit(lambda a: a['observations'][0].update(precision='EXACT_LIFESPAN'))

    def test_observation_changed_rejected(self):
        self.edit(lambda a: a['observations'][1].update(rounded_display_years=800))

    def test_duplicate_observation_rejected(self):
        self.edit(lambda a: a['observations'].__setitem__(1, dict(a['observations'][0])))

    def test_fake_external_authentication_rejected(self):
        self.edit(lambda a: a.update(externally_revalidated_by_this_program=True))

    def test_false_raw_snapshot_rejected(self):
        self.edit(lambda a: a.update(raw_source_snapshot_stored=True))

    def test_deployment_escalation_rejected(self):
        self.edit(lambda a: a.update(deployment='PRODUCTION'))

    def test_change_master_rejected(self):
        self.edit(lambda a: a.update(master='TM-015'))

    def test_remove_overclaim_restriction_rejected(self):
        self.edit(lambda a: a['prohibited_conclusions'].remove('HUMAN_IMMORTALITY_PROVEN'))

    def test_extra_research_claim_rejected(self):
        self.edit(lambda a: a.update(proven_immortality=True))

    def test_forged_g9_report_rejected(self):
        bad = dict(REPORT, ai_trace_checks=999)
        with self.assertRaises(ValueError):
            validate_report(bad)

    def test_shell_plaintext_and_size(self):
        b = ONE.read_bytes()
        self.assertLessEqual(len(b), 2048)
        self.assertEqual(b.count(b'\n'), 1)
        self.assertFalse(any(t in b for t in (b'zlib', b'base64', b'eval(', b'exec(')))
        subprocess.run(['bash', '-n', str(ONE)], check=True, timeout=5)

    def test_shell_requires_g9_report(self):
        result = subprocess.run(['bash', str(ONE)], capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)

    def test_shell_with_trusted_g9_fixture(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            g9 = Path(td) / 'g9.json'
            g9.write_text(json.dumps(REPORT), encoding='utf-8')
            result = subprocess.run(['bash', str(ONE), str(g9)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output['result'], 'SOURCE_REFERENCED_REVIEW_ONLY')
            self.assertFalse(output['production_deployed'])
            self.assertFalse(output['source_webpages_authenticated_by_program'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
