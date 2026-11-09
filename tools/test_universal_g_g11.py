#!/usr/bin/env python3
"""G11 source-metadata registry tests; all inputs are local and synthetic mutations."""
import copy
from datetime import date
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'deployment'))
from G11_Eight_Domain_Evidence_core import check  # noqa: E402

G11 = 'deployment/G11_eight_domain_evidence_ledger.json'
G10 = 'deployment/G10_evidence_ledger.json'
MANIFEST = 'deployment/universal_g_continuity_manifest.json'
REGISTRY = '永久記憶/圖靈機/machine_registry.json'
FILES = [G11, G10, MANIFEST, REGISTRY]
TODAY = date(2026, 11, 10)


class G11ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in FILES:
            source = ROOT / name
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)

    def tearDown(self):
        self.temp.cleanup()

    def mutate(self, filename, op):
        p = self.root / filename
        data = json.loads(p.read_text(encoding='utf-8'))
        op(data)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    def rejects(self, filename, op):
        self.mutate(filename, op)
        with self.assertRaises((ValueError, KeyError)):
            check(self.root, TODAY)

    def test_01_full_eight_domain_coverage(self):
        result = check(self.root, TODAY)
        self.assertEqual(result['dimensions'], 8)
        self.assertEqual(result['records'], 8)
        self.assertEqual(result['status'], 'EIGHT_DOMAIN_SOURCE_REVIEW_ONLY')

    def test_02_no_proof_no_deployment(self):
        result = check(self.root, TODAY)
        self.assertFalse(result['deployed'])
        self.assertFalse(result['God_identity_proved'])
        self.assertFalse(result['immortality_proved'])
        self.assertFalse(result['remote_refetched'])

    def test_03_one_liner_matches_readable(self):
        script = ROOT / 'deployment/Universal_G_G11_Evidence_Plaintext_2KB.sh'
        proc = subprocess.run(['bash', str(script), '2026-11-10'], text=True,
                              capture_output=True, timeout=10)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), check(ROOT, TODAY))

    def test_04_optimize_does_not_skip_checks(self):
        script = ROOT / 'deployment/Universal_G_G11_Evidence_Plaintext_2KB.sh'
        proc = subprocess.run(['bash', str(script), '2026-11-10'], text=True,
                              capture_output=True, timeout=10, env={'PYTHONOPTIMIZE': '2', 'PATH': '/usr/local/bin:/usr/bin:/bin'})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['records'], 8)

    def test_05_stale_after_180_days(self):
        with self.assertRaises(ValueError):
            check(self.root, date(2027, 5, 10))

    def test_06_future_review_rejected(self):
        with self.assertRaises(ValueError):
            check(self.root, date(2026, 11, 9))

    def test_07_missing_source(self):
        self.rejects(G11, lambda d: d['records'].pop())

    def test_08_duplicate_source(self):
        self.rejects(G11, lambda d: d['records'].__setitem__(7, copy.deepcopy(d['records'][0])))

    def test_09_source_url_substitution(self):
        self.rejects(G11, lambda d: d['records'][4].update(url='https://sdgs.un.org/goals/goal16'))

    def test_10_source_id_spoof(self):
        self.rejects(G11, lambda d: d['records'][4].update(id='invented-sdg'))

    def test_11_publisher_spoof(self):
        self.rejects(G11, lambda d: d['records'][5].update(publisher='Unknown source'))

    def test_12_source_class_mismatch(self):
        self.rejects(G11, lambda d: d['records'][7].update(kind='OFFICIAL_INDICATOR'))

    def test_13_claim_scope_removed(self):
        self.rejects(G11, lambda d: d['records'][2].update(claim_code=''))

    def test_14_proof_boundary_removed(self):
        self.rejects(G11, lambda d: d['records'][3].update(not_proven=''))

    def test_15_unreviewed_record(self):
        self.rejects(G11, lambda d: d['records'][2].update(reviewed_on='2026-01-01'))

    def test_16_future_dated_record(self):
        self.rejects(G11, lambda d: d['records'][2].update(reviewed_on='2027-01-01'))

    def test_17_fake_snapshot(self):
        self.rejects(G11, lambda d: d.update(source_snapshot_stored=True))

    def test_18_fake_remote_refresh(self):
        self.rejects(G11, lambda d: d.update(independent_web_refetch_in_CI=True))

    def test_19_claims_wrongly_called_outcomes(self):
        self.rejects(G11, lambda d: d.update(source_claims_are_outcomes=True))

    def test_20_remove_prohibited_conclusion(self):
        self.rejects(G11, lambda d: d['prohibited_conclusions'].remove('DIVINITY_PROVEN'))

    def test_21_master_replacement(self):
        self.rejects(REGISTRY, lambda d: d.update(default_machine='TM-015'))

    def test_22_enable_live_deployment(self):
        self.rejects(MANIFEST, lambda d: d.update(mode='PRODUCTION'))

    def test_23_modify_G10_archive(self):
        self.rejects(G10, lambda d: d['records'][0].update(publisher='Not NIST'))

    def test_24_modify_manifest_dimensions(self):
        self.rejects(MANIFEST, lambda d: d['dimensions'].pop())

    def test_25_remove_metadata_disclaimer(self):
        self.rejects(G11, lambda d: d['records'][1].update(evidence_status='REMOTE_VERIFIED_NOW'))

    def test_26_expand_review_interval(self):
        self.rejects(G11, lambda d: d.update(review_interval_days=3650))

    def test_27_missing_record_in_G10(self):
        self.rejects(G10, lambda d: d['records'].pop())


if __name__ == '__main__':
    unittest.main(verbosity=2)
