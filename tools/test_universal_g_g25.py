#!/usr/bin/env python3
"""130 G25 offline evidence-metadata safety and exact prime-power tests."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'deployment'))
from G25_Evidence_Core import (run,check_parents,factorize,DOMAINS,PRIMES,
                              REQUIREMENTS,PERMISSIONS,strict_date,valid_label)
from G25_Oneliner_Builder import build

SHELL = ROOT/'deployment/Universal_G_G25_Evidence_2KB.sh'
EXAMPLE = json.loads((ROOT/'deployment/G25_evidence_example.json').read_text())

def record(name='peace', topic=0, ident='test_a'):
    return [name,topic,'provider_'+ident,'reviewer_'+ident,'record_'+ident,'2026-09-01','2026-10-01']

def packet(records=()):
    x=deepcopy(EXAMPLE);x['evidence']=list(records)
    return x

def bash_run(x, optimized=False):
    env=dict(os.environ)
    if optimized:env['PYTHONOPTIMIZE']='2'
    return subprocess.run(['bash',str(SHELL)],input=json.dumps(x),text=True,
                          capture_output=True,env=env,timeout=10)

def reject_both(test, x, verify_shell=False):
    with test.assertRaises((ValueError,KeyError,TypeError)):run(x)
    if verify_shell:
        test.assertNotEqual(bash_run(x).returncode,0)

class EvidenceTests(unittest.TestCase):
    def test_001_registry_14_domains(self):
        self.assertEqual(len(DOMAINS),14)

    def test_002_independent_distinct_primes(self):
        self.assertEqual((len(PRIMES),len(set(PRIMES))), (14,14))

    def test_003_topic_requirements_match_fixed_count(self):
        self.assertEqual(list(map(len,REQUIREMENTS.values())),[2,3,2,3,3,2,2,3,4,5,4,3,3,4])

    def test_004_no_records_identity_integer(self):
        x=run(packet());self.assertEqual((x['prime_power_integer'],x['records']), (1,0))

    def test_005_full_synthetic_example(self):
        r=run(EXAMPLE)
        self.assertEqual((r['records'],r['prime_power_integer']), (6,1463339159))
        self.assertEqual(r['topics']['peace'], [0,1])
        self.assertEqual(r['topics']['cultivated_meat'],[0,2])

    def test_006_example_one_liner_exactly_equal_readable(self):
        proc=bash_run(EXAMPLE);self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertEqual(json.loads(proc.stdout),run(EXAMPLE))

    def test_007_under_2k_line(self):
        self.assertEqual((len(SHELL.read_bytes()),SHELL.read_bytes().count(b'\n')),(2046,1))

    def test_008_bash_syntax(self):
        self.assertEqual(subprocess.run(['bash','-n',str(SHELL)],capture_output=True).returncode,0)

    def test_009_builder_exact_bytes(self):
        self.assertEqual(build(),SHELL.read_bytes())

    def test_010_python_optimized_same_json(self):
        self.assertEqual(bash_run(EXAMPLE,True).stdout,bash_run(EXAMPLE).stdout)

    def test_011_source_authentication_never_assumed(self):
        r=run(EXAMPLE);self.assertFalse(r['authenticated']);self.assertFalse(r['review_verified'])

    def test_012_no_realworld_achievements_or_authority(self):
        r=run(EXAMPLE)
        self.assertFalse(r['outcomes_verified']);self.assertEqual(r['orders_submitted'],0)
        self.assertFalse(r['deployed']);self.assertTrue(r['human_review_required'])

    def test_013_no_hashlib_or_network_code(self):
        for fn in ('G25_Oneliner_Builder.py','G25_Evidence_Core.py','Universal_G_G25_Evidence_2KB.sh'):
            src=(ROOT/'deployment'/fn).read_text()
            for token in ('hashlib','sha256(', 'sha1(', 'socket','urllib','requests','os.system','subprocess'):
                self.assertNotIn(token,src)

    def test_014_extra_top_level_claims_rejected(self):
        x=packet();x['independent_verified']=True;reject_both(self,x,True)

    def test_015_other_source_rejected(self):
        x=packet();x['source']='REAL_WHO';reject_both(self,x)

    def test_016_live_mode_rejected(self):
        x=packet();x['mode']='live';reject_both(self,x,True)

    def test_017_permission_schema_required(self):
        x=packet();del x['permissions']['network'];reject_both(self,x)

    def test_018_permission_false_not_numeric_zero(self):
        x=packet();x['permissions']['network']=0;reject_both(self,x,True)

    def test_019_untrusted_outcome_inside_record_rejected(self):
        x=packet([{'domain':'peace','claimed_peace':True}]);reject_both(self,x)

    def test_020_duplicate_record_id_rejected(self):
        a=record(ident='abc');b=record('peace',1,'abc');reject_both(self,packet([a,b]))

    def test_021_reviewer_equal_provider_rejected(self):
        x=record();x[3]=x[2];reject_both(self,packet([x]),True)

    def test_022_negative_topic_index_rejected(self):
        reject_both(self,packet([record(topic=-1)]))

    def test_023_boolean_topic_index_rejected(self):
        reject_both(self,packet([record(topic=True)]))

    def test_024_more_than_56_rows_rejected(self):
        reject_both(self,packet([record()]*57))

    def test_025_malformed_iso_date_rejected(self):
        x=record();x[5]='2026-02-30';reject_both(self,packet([x]),True)

    def test_026_unreviewed_source_claim_rejected(self):
        x=record();x[6]='2026-11-11';reject_both(self,packet([x]))

    def test_027_stale_relative_date_rejected(self):
        x=record();x[5]='2025-01-01';x[6]='2025-01-02';reject_both(self,packet([x]))

    def test_028_future_observation_order_rejected(self):
        x=record();x[5]='2026-11-09';x[6]='2026-10-30';reject_both(self,packet([x]))

    def test_029_provider_name_control_char_rejected(self):
        x=record();x[2]='fake\nsource';reject_both(self,packet([x]))

    def test_030_provider_name_unicode_confusable_rejected(self):
        x=record();x[2]='prоvider';reject_both(self,packet([x]))

    def test_031_unknown_prime_rejected(self):
        with self.assertRaises(ValueError):factorize(59)

    def test_032_exponent_out_of_range_rejected(self):
        with self.assertRaises(ValueError):factorize(5**3)

    def test_033_numeric_phase_exact(self):
        self.assertEqual(factorize(PRIMES[7]**2*PRIMES[8]),[0]*7+[2,1]+[0]*5)

    def test_034_zero_invalid_numeric_encoding(self):
        with self.assertRaises(ValueError):factorize(0)

    def test_035_missing_as_of_rejected(self):
        x=packet();del x['as_of'];reject_both(self,x)

    def test_036_bad_as_of_type_rejected(self):
        x=packet();x['as_of']=20261110;reject_both(self,x)

# Six domain-specific positive / adversarial checks per each of 14 G24 domains.
for idx, domain in enumerate(DOMAINS):
    def one(self,domain=domain,idx=idx):
        out=run(packet([record(domain,0,f'{idx:02}_a')]))
        self.assertEqual(out['prime_power_integer'],PRIMES[idx])
    def two(self,domain=domain,idx=idx):
        out=run(packet([record(domain,0,f'{idx:02}_a'),record(domain,1,f'{idx:02}_b')]))
        self.assertEqual(out['prime_power_integer'],PRIMES[idx]**2)
        self.assertEqual(out['topics'][domain],[0,1])
    def out_of_range(self,domain=domain):
        reject_both(self,packet([record(domain,len(REQUIREMENTS[domain]),'bad')]),False)
    def duplicate_origin(self,domain=domain):
        a=record(domain,0,'same');b=record(domain,0,'same')
        b[4]='new_record'
        reject_both(self,packet([a,b]),False)
    def client_equal(self,domain=domain,idx=idx):
        x=packet([record(domain,0,f'{idx:02}_a')]);p=bash_run(x)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout),run(x))
    def stale(self,domain=domain):
        z=record(domain,0,'old');z[5]='2020-01-01';z[6]='2020-01-02'
        reject_both(self,packet([z]),False)
    for j,(label,fn) in enumerate((('single_prime',one),('double_prime',two),
            ('bad_topic',out_of_range),('duplicate_source',duplicate_origin),
            ('shell_core_equivalence',client_equal),('relative_staleness',stale))):
        setattr(EvidenceTests,f'test_{37+idx*6+j:03}_{domain}_{label}',fn)

for idx,permission in enumerate(PERMISSIONS):
    def denied(self,permission=permission):
        x=packet();x['permissions'][permission]=True
        reject_both(self,x,permission=='network')
    setattr(EvidenceTests,f'test_{121+idx:03}_permission_{permission}',denied)

# Test counts: 36 core + 84 domain cases + 10 permission negatives = 130.
if __name__=='__main__':
    unittest.main(verbosity=2)
