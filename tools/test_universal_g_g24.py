#!/usr/bin/env python3
"""112 offline tests for G24 finite cross-domain prime-power governance."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'deployment'))
from G24_Cross_Domain_Godel_Core import DOMAINS,PRIMES,PHASE,FORBIDDEN,REQUIREMENTS,run,update,primes_state_roundtrip
from G24_Oneliner_Builder import build

SHELL=ROOT/'deployment/Universal_G_G24_Cross_Domain_2KB.sh'
EXAMPLE=json.loads((ROOT/'deployment/G24_example_request.json').read_text(encoding='utf-8'))

def request(events=None):
    x=copy.deepcopy(EXAMPLE)
    x['events'] = [] if events is None else events
    return x

def run_shell(x,optimized=False):
    env=dict(os.environ)
    if optimized:env['PYTHONOPTIMIZE']='2'
    return subprocess.run(['bash',str(SHELL)],input=json.dumps(x),text=True,capture_output=True,timeout=10,env=env)

class G24Tests(unittest.TestCase):
    def test_01_domain_count(self):
        self.assertEqual(len(DOMAINS),14)

    def test_02_registry_complete(self):
        self.assertEqual((len(PRIMES),len(REQUIREMENTS),len(set(DOMAINS))), (14,14,14))

    def test_03_zero_state_one(self):
        self.assertEqual(run(request())['prime_power_integer'],1)

    def test_04_example_is_all_research(self):
        self.assertEqual(set(run(EXAMPLE)['domain_phases'].values()),{'RESEARCH_ONLY'})

    def test_05_all_prime_product(self):
        n=1
        for p in PRIMES:n*=p
        self.assertEqual(run(EXAMPLE)['prime_power_integer'],n)

    def test_06_full_numeric_roundtrip(self):
        self.assertTrue(run(EXAMPLE)['full_numeric_roundtrip'])

    def test_07_zero_unknown_prime_factors(self):
        with self.assertRaises(ValueError):primes_state_roundtrip(59)

    def test_08_zero_multiple_exponent(self):
        with self.assertRaises(ValueError):primes_state_roundtrip(5**2)

    def test_09_no_sha_or_network_runtime(self):
        for name in ('G24_Cross_Domain_Godel_Core.py','G24_Oneliner_Builder.py','Universal_G_G24_Cross_Domain_2KB.sh'):
            contents=(ROOT/'deployment'/name).read_text()
            for needle in ('hashlib','sha256(', 'sha1(', 'socket','urllib','requests'):
                self.assertNotIn(needle,contents)

    def test_10_no_false_outcomes(self):
        d=run(EXAMPLE)
        for k in ('machine_universality_proved','all_dimensions_immortality_proved',
                  'world_peace_achieved','all_sdgs_achieved',
                  'cultivated_meat_safe_or_cruelty_free_proved',
                  'trader42_alpha_validated','independent_impact_verified',
                  'external_data_authenticated','deployment_executed'):
            self.assertIs(d[k],False)
        self.assertEqual(d['orders_submitted'],0)

    def test_11_bash_syntax_valid(self):
        p=subprocess.run(['bash','-n',str(SHELL)],capture_output=True)
        self.assertEqual(p.returncode,0)

    def test_12_one_physical_line(self):
        self.assertEqual(SHELL.read_bytes().count(b'\n'),1)

    def test_13_less_than_two_kib(self):
        self.assertLessEqual(SHELL.stat().st_size,2048)

    def test_14_baseline_json_matches_readable_core(self):
        p=run_shell(EXAMPLE)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout),run(EXAMPLE))

    def test_15_optimized_and_standard_identical(self):
        self.assertEqual(run_shell(EXAMPLE).stdout,run_shell(EXAMPLE,True).stdout)

    def test_16_builder_reconstructs_source(self):
        self.assertEqual(build(),SHELL.read_bytes())

    def test_17_fail_closed_unknown_extra_top_level(self):
        x=request();x['superuser']=True
        with self.assertRaises(ValueError):run(x)
        self.assertNotEqual(run_shell(x).returncode,0)

    def test_18_fail_closed_live_source_and_mode(self):
        x=request();x['mode']='live'
        with self.assertRaises(ValueError):run(x)
        self.assertNotEqual(run_shell(x).returncode,0)

# Each domain: one actual multiplication, one exact division, one full integer
# decomposition, one complete JSON shell-vs-core equality, one duplicate-state
# refusal, and one simulated forbidden authorization event.
for i,name in enumerate(DOMAINS):
    def enter(self, i=i, name=name):
        r=run(request([[name,'ENTER_RESEARCH']]))
        self.assertEqual(r['prime_power_integer'],PRIMES[i])
        self.assertEqual(r['prime_factors'],[[PRIMES[i],1]])
    def reset(self, name=name):
        r=run(request([[name,'ENTER_RESEARCH'],[name,'RESET']]))
        self.assertEqual(r['prime_power_integer'],1)
        self.assertEqual(r['domain_phases'][name],'BLOCKED')
    def decode(self, name=name, i=i):
        n=update(1,name,0,1)
        self.assertEqual(primes_state_roundtrip(n)[i],1)
        self.assertEqual(update(n,name,1,0),1)
    def shell(self, name=name):
        x=request([[name,'ENTER_RESEARCH']])
        p=run_shell(x)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout),run(x))
    def duplicate(self, name=name):
        x=request([[name,'ENTER_RESEARCH'],[name,'ENTER_RESEARCH']])
        with self.assertRaises(ValueError):run(x)
        self.assertNotEqual(run_shell(x).returncode,0)
    def unauthorized(self, name=name):
        x=request([[name,'PRODUCTION_APPROVED']])
        with self.assertRaises(ValueError):run(x)
        self.assertNotEqual(run_shell(x).returncode,0)
    for j,(label,method) in enumerate([
        ('prime_multiply',enter),('prime_divide',reset),('int_decode',decode),
        ('shell_equal',shell),('duplicate_reject',duplicate),('deployment_reject',unauthorized)
    ]):
        setattr(G24Tests,f'test_{19+6*i+j:03}_{label}_{name}',method)

# Every forbidden switch independently fails in both readable and small core.
for i,flag in enumerate(FORBIDDEN):
    def blocked_permission(self,flag=flag):
        x=request();x['permissions'][flag]=True
        with self.assertRaises(ValueError):run(x)
        self.assertNotEqual(run_shell(x).returncode,0)
    setattr(G24Tests,f'test_{103+i:03}_permission_{flag}_blocked',blocked_permission)

if __name__=='__main__':
    unittest.main(verbosity=2)
