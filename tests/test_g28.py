#!/usr/bin/env python3
"""G28 offline, deterministic exploration, schema checks, counterexamples, no action."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEP = ROOT / 'deployment'
sys.path.insert(0, str(DEP))
from G28_Oneliner_Audit_Builder import build as build_audit
from G28_Computational_Freedom_Field import (
    SCHEMA, NO_ACTIONS, AXES, parse_request, candidate_ids,
    proposed_cost, cost_band, descriptor, surrogate_quality, distance,
    novelty, explore,
)

FIXTURE = json.loads((DEP/'G28_example_request.json').read_text())
REPORT = json.loads((DEP/'G28_example_report.json').read_text())


def fixture():
    return copy.deepcopy(FIXTURE)


class TestG28(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = explore(fixture())

    def test_01_schema(self):
        self.assertEqual(FIXTURE['schema'], SCHEMA)

    def test_02_exact_json_repeatability(self):
        self.assertEqual(explore(fixture()), self.report)

    def test_03_saved_report_matches(self):
        self.assertEqual(self.report, REPORT)

    def test_04_grammar_has_four_axes(self):
        self.assertEqual(len(AXES), 4)

    def test_05_256_combinations(self):
        self.assertEqual(self.report['candidate_universe'], 256)

    def test_06_budget_24(self):
        self.assertEqual(self.report['proposals_scored'], 24)

    def test_07_beam_eight_metadata(self):
        self.assertEqual(self.report['surrogate_lookahead_inspections'], 24*8)

    def test_08_baseline_metadata_cost(self):
        self.assertEqual(self.report['baseline_metadata_inspections'], 24)

    def test_09_qd_coverage(self):
        self.assertEqual(self.report['quality_diversity_occupied_cells'], 12)

    def test_10_random_coverage(self):
        self.assertEqual(self.report['random_baseline_occupied_cells'], 9)

    def test_11_guided_synthetic_priority(self):
        self.assertEqual(self.report['quality_diversity_sum_synthetic_priority'], 63)

    def test_12_random_synthetic_priority(self):
        self.assertEqual(self.report['random_baseline_sum_synthetic_priority'], 49)

    def test_13_archive_has_one_elite_per_cell(self):
        keys = [tuple(p['descriptor']) for p in self.report['archive']]
        self.assertEqual(len(keys), len(set(keys)))

    def test_14_each_elite_is_untested(self):
        self.assertTrue(all(p['status'] == 'UNTESTED_HYPOTHESIS' for p in self.report['archive']))

    def test_15_no_experiments_run(self):
        self.assertEqual(self.report['actual_experiments_performed'], 0)

    def test_16_no_independent_evidence(self):
        self.assertFalse(self.report['evidence_independently_verified'])

    def test_17_no_proven_scientific_results(self):
        self.assertTrue(all(p['scientific_claim_proved'] is False for p in self.report['archive']))

    def test_18_no_predicted_outcome(self):
        self.assertFalse(self.report['predicted_real_world_outcomes'])

    def test_19_no_infinite_claim(self):
        self.assertFalse(self.report['unbounded_computation_claimed'])

    def test_20_no_platform_bypass(self):
        self.assertFalse(self.report['platform_restrictions_bypassed'])

    def test_21_no_deploy_or_trades(self):
        self.assertFalse(self.report['deployment_performed'])
        self.assertEqual(self.report['live_orders_submitted'],0)

    def test_22_no_sha_digest(self):
        self.assertFalse(self.report['sha_used'])
        self.assertNotIn('audit_trace_sha256', self.report)

    def test_23_trace_count(self):
        self.assertEqual(len(self.report['audit_trace']), 24)

    def test_24_trace_candidates_unique(self):
        ids = [e['id'] for e in self.report['audit_trace']]
        self.assertEqual(len(ids), len(set(ids)))

    def test_25_trace_steps_exact(self):
        self.assertEqual([e['step'] for e in self.report['audit_trace']], list(range(1,25)))

    def test_26_no_hypothesis_missing_falsifier(self):
        self.assertTrue(all(len(e['falsification_test'])>0 for e in self.report['archive']))

    def test_27_archive_within_risk_budget(self):
        self.assertTrue(all(e['risk_units']<=FIXTURE['max_risk'] for e in self.report['archive']))

    def test_28_archive_within_cost_budget(self):
        self.assertTrue(all(e['cost_units']<=FIXTURE['max_cost'] for e in self.report['archive']))

    def test_29_source_contains_no_external_connectors(self):
        s=(DEP/'G28_Computational_Freedom_Field.py').read_text()
        for forbidden in ('import requests','import urllib','import socket', 'import subprocess',
                          'os.system(', 'eval(', 'exec(', 'hashlib'):
            self.assertNotIn(forbidden,s)

    def test_30_disallow_nonoffline_mode(self):
        x=fixture();x['mode']='auto_deploy'
        with self.assertRaises(ValueError): explore(x)

    def test_31_disallow_extra_key(self):
        x=fixture();x['bypass']=True
        with self.assertRaises(ValueError): explore(x)

    def test_32_disallow_missing_key(self):
        x=fixture();del x['seed']
        with self.assertRaises(ValueError): explore(x)

    def test_33_disallow_wrong_schema(self):
        x=fixture();x['schema']='G29'
        with self.assertRaises(ValueError): explore(x)

    def test_34_disallow_zero_budget(self):
        x=fixture();x['budget']=0
        with self.assertRaises(ValueError): explore(x)

    def test_35_disallow_unbounded_budget(self):
        x=fixture();x['budget']=9999999
        with self.assertRaises(ValueError): explore(x)

    def test_36_disallow_boolean_budget(self):
        x=fixture();x['budget']=True
        with self.assertRaises(ValueError): explore(x)

    def test_37_disallow_float_budget(self):
        x=fixture();x['budget']=5.5
        with self.assertRaises(ValueError): explore(x)

    def test_38_disallow_invalid_seed(self):
        x=fixture();x['seed']=-1
        with self.assertRaises(ValueError): explore(x)

    def test_39_disallow_invalid_beam(self):
        x=fixture();x['beam_width']=99
        with self.assertRaises(ValueError): explore(x)

    def test_40_disallow_duplicate_identifiers(self):
        x=fixture();x['domains'][0]['id']=x['domains'][1]['id']
        with self.assertRaises(ValueError): explore(x)

    def test_41_disallow_empty_axis(self):
        x=fixture();x['falsifiers']=[]
        with self.assertRaises(ValueError): explore(x)

    def test_42_disallow_malformed_identifier(self):
        x=fixture();x['methods'][0]['id']='unsafe;exec'
        with self.assertRaises(ValueError): explore(x)

    def test_43_disallow_negative_risk(self):
        x=fixture();x['domains'][0]['risk']=-1
        with self.assertRaises(ValueError): explore(x)

    def test_44_disallow_infinite_float_proxy(self):
        x=fixture();x['methods'][0]['testability']=float('inf')
        with self.assertRaises(ValueError): explore(x)

    def test_45_disallow_empty_admissible_search_space(self):
        x=fixture();x['max_cost']=0
        with self.assertRaises(ValueError): explore(x)

    def test_46_one_candidate_and_larger_budget(self):
        x=fixture();x['budget']=512
        for a in AXES: x[a]=x[a][:1]
        y=explore(x)
        self.assertEqual(y['candidate_universe'],1)
        self.assertEqual(y['proposals_scored'],1)

    def test_47_reproducible_small_seed(self):
        x=fixture();x['budget']=10;x['seed']=987
        self.assertEqual(explore(x),explore(x))

    def test_48_exploration_is_seed_sensitive(self):
        x=fixture();x['seed']=5
        z=fixture();z['seed']=6
        self.assertNotEqual(explore(x)['audit_trace'],explore(z)['audit_trace'])

    def test_49_testability_is_metadata_not_data(self):
        p=fixture()
        self.assertIsNone(p.get('observed_experimental_result'))

    def test_50_distance_is_hamming(self):
        x=tuple(FIXTURE[a][0] for a in AXES)
        y=(FIXTURE['domains'][1], FIXTURE['methods'][0], FIXTURE['measurements'][1], FIXTURE['falsifiers'][0])
        self.assertEqual(distance(x,y),2)

    def test_51_novelty_empty_archive_is_four(self):
        c=tuple(FIXTURE[a][0] for a in AXES)
        self.assertEqual(novelty(c,{}),4)

    def test_52_descriptor_low_cost(self):
        c=tuple(FIXTURE[a][0] for a in AXES)
        self.assertEqual(descriptor(c),('formal_methods','low'))

    def test_53_cost_bucket_categories(self):
        self.assertEqual([cost_band(i) for i in (2,4,7)],['low','medium','high'])

    def test_54_no_credential_fields(self):
        self.assertFalse(any('api_key' in str(v) or 'token' in str(v) for v in FIXTURE.values()))

    def test_55_script_runs_with_stdin(self):
        p=subprocess.run([sys.executable,str(DEP/'G28_Computational_Freedom_Field.py')],
                         input=json.dumps(FIXTURE),text=True,capture_output=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout),self.report)

    def test_56_shell_failure_exit_code(self):
        x=fixture();x['permissions']['network']=True
        p=subprocess.run([sys.executable,str(DEP/'G28_Computational_Freedom_Field.py')],
                         input=json.dumps(x),text=True,capture_output=True,timeout=15)
        self.assertEqual(p.returncode,2)
        self.assertIn('BLOCKED',p.stderr)


for i,permission in enumerate(NO_ACTIONS):
    def deny(self,permission=permission):
        x=fixture();x['permissions'][permission]=True
        with self.assertRaises(ValueError): explore(x)
    setattr(TestG28,f'test_{57+i:02}_deny_{permission}',deny)


AUDITOR = DEP/'G28_Research_Report_Audit_2KB.sh'

def audit(report):
    return subprocess.run(['bash',str(AUDITOR)], input=json.dumps(report),
                          text=True,capture_output=True,timeout=12)

class TestG28Auditor(unittest.TestCase):
    def test_63_one_line(self):
        self.assertEqual(AUDITOR.read_bytes().count(b'\n'),1)

    def test_64_under_2k(self):
        self.assertEqual(len(AUDITOR.read_bytes()),1610)

    def test_65_syntax(self):
        self.assertEqual(subprocess.run(['bash','-n',str(AUDITOR)]).returncode,0)

    def test_66_builder_reproduces(self):
        self.assertEqual(build_audit(),AUDITOR.read_bytes())

    def test_67_report_passes(self):
        p=audit(REPORT)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)['status'],'REPORT_CONSISTENT_NOT_AUTHENTICATED')

    def test_68_tamper_candidates_rejected(self):
        r=copy.deepcopy(REPORT);r['proposals_scored']+=1
        self.assertNotEqual(audit(r).returncode,0)

    def test_69_tamper_archive_score_rejected(self):
        r=copy.deepcopy(REPORT);r['quality_diversity_sum_synthetic_priority']+=1
        self.assertNotEqual(audit(r).returncode,0)

    def test_70_tamper_proved_claim_rejected(self):
        r=copy.deepcopy(REPORT);r['archive'][0]['scientific_claim_proved']=True
        self.assertNotEqual(audit(r).returncode,0)

    def test_71_tamper_deploy_rejected(self):
        r=copy.deepcopy(REPORT);r['deployment_performed']=True
        self.assertNotEqual(audit(r).returncode,0)

    def test_72_tamper_platform_bypass_rejected(self):
        r=copy.deepcopy(REPORT);r['platform_restrictions_bypassed']=True
        self.assertNotEqual(audit(r).returncode,0)

    def test_73_tamper_hash_credibility_rejected(self):
        r=copy.deepcopy(REPORT);r['sha_used']=True
        self.assertNotEqual(audit(r).returncode,0)

    def test_74_cannot_certify_external_authenticity(self):
        self.assertNotIn('source_authenticated',json.loads(audit(REPORT).stdout))

if __name__=='__main__':
    unittest.main(verbosity=2)