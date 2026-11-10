#!/usr/bin/env python3
"""G24S cross-domain prime-power offline governance: 126 positive and negative tests."""
import copy
from datetime import date, timedelta
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'deployment'))
from G24S_cross_domain_core import (DOMAINS, PRIMES, STATE_NAMES, FLAGS,
    first_primes, valuation, prime_transition, decode_register,
    encode_configuration, decode_configuration, validate_input, run)
from G24S_oneliner_builder import build
from G24S_policy_core import validate_manifest, validate_parents
from G24S_independent_audit import check as independent_check

SHELL=ROOT/'deployment/Universal_G_G24S_Cross_Domain_2KB.sh'
REQUEST=ROOT/'deployment/G24S_example_request.json'
MANIFEST=ROOT/'deployment/G24S_cross_domain_contract.json'
BASE=json.loads(REQUEST.read_text())


def altered(fn):
    x=copy.deepcopy(BASE)
    fn(x)
    return x


def parents():
    return (
        {'schema':'G23-prime-power-godel-computational-tm/1','master':'UTM-PLEIADES-v0.2-PTCA',
         'same_G22_rules':True,'transitions':1140,'entire_replay_steps':3505682,
         'sha_digest_functions_used':False,'master_replaced':False,'real_world_deployment':False},
        {'schema':'G13-peace-sdgs-cultivated-meat/1','master':'UTM-PLEIADES-v0.2-PTCA',
         'source_metadata_only':True,'production_deployed':False,'all_goals_achieved':False,
         'zero_suffering_proved':False,'product_approved':False,'reviewed_on':'2026-11-10',
         'review_interval_days':180},
        {'schema':'G14-trader42-principle-review/1','master':'UTM-PLEIADES-v0.2-PTCA',
         'trader_mode':'paper','live_armed':False,'order_submission':False,
         'execution_allowed':False,'credential_access':False,'exchange_network_access':False,
         'upstream_snapshot_authenticated':False,'created_on':'2026-11-10','review_interval_days':180,
         'risk':{'max_order_quote_usdt':'10','max_total_quote_usdt':'50',
                 'max_base_exposure_btc':'0.001','daily_equity_loss_pct_ceiling':'1',
                 'additional_daily_realized_loss_review_usdt':'2','cooldown_seconds':30,
                 'sizing_can_only_decrease':True,'kill_is_overriding':True,
                 'exchange_reconciliation_required':True,'pending_order_blocks':True}},
    )


class G24STests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.answer=run(BASE)
        cls.shell_output=subprocess.run(['bash',str(SHELL)],input=REQUEST.read_bytes(),capture_output=True,timeout=8,check=True)
        cls.shell_answer=json.loads(cls.shell_output.stdout)

    def test_01_version(self): self.assertEqual(self.answer['version'],'G24S')
    def test_02_status(self): self.assertEqual(self.answer['status'],'CROSS_DOMAIN_SYNTHETIC_REVIEW_ONLY')
    def test_03_domains_exact_twelve(self): self.assertEqual(self.answer['domain_count'],12)
    def test_04_names_in_canonical_order(self): self.assertEqual([e['domain'] for e in self.answer['domains']],list(DOMAINS))
    def test_05_simulated_only(self): self.assertEqual(self.answer['synthetic_reviewed'],5)
    def test_06_incomplete_domains(self): self.assertEqual(self.answer['evidence_gaps'],4)
    def test_07_safety_vetoed_domains(self): self.assertEqual(self.answer['vetoed'],3)
    def test_08_all_domains_registered(self): self.assertEqual(self.answer['registered'],12)
    def test_09_godel_actual_writes(self): self.assertEqual(self.answer['prime_power_transition_count'],20)
    def test_10_godel_integer_bits(self): self.assertEqual(self.answer['prime_power_integer_bits'],98)
    def test_11_configuration_integer_bits(self): self.assertEqual(self.answer['configuration_integer_bits'],122)
    def test_12_exact_numeric_roundtrip(self): self.assertTrue(self.answer['exact_numeric_roundtrip'])
    def test_13_configuration_roundtrip(self): self.assertTrue(self.answer['configuration_roundtrip'])
    def test_14_no_order(self): self.assertFalse(self.answer['trading_allowed'])
    def test_15_no_deployment(self): self.assertFalse(self.answer['deployment_allowed'])
    def test_16_zero_authorized_action(self): self.assertEqual(self.answer['approved_external_actions'],0)
    def test_17_zero_network_calls(self): self.assertEqual(self.answer['network_calls'],0)
    def test_18_never_proves_immortality(self): self.assertFalse(self.answer['all_dimensions_immortality_proved'])
    def test_19_never_proves_physical_outcomes(self): self.assertFalse(self.answer['real_world_outcomes_proved'])
    def test_20_no_provenance_authentication(self): self.assertFalse(self.answer['source_authenticity_proved'])
    def test_21_no_digest(self): self.assertFalse(self.answer['sha_used'])
    def test_22_one_liner_exact_same_result(self): self.assertEqual(self.answer,self.shell_answer)
    def test_23_one_liner_only_one_physical_line(self): self.assertEqual(SHELL.read_bytes().count(b'\n'),1)
    def test_24_one_liner_under_2kb(self): self.assertLessEqual(SHELL.stat().st_size,2048)
    def test_25_one_liner_bash_parse(self): self.assertEqual(subprocess.run(['bash','-n',str(SHELL)]).returncode,0)
    def test_26_one_liner_rebuild_exact(self): self.assertEqual(build(),SHELL.read_bytes())
    def test_27_one_liner_pyoptimize2_equal(self):
        p=subprocess.run(['bash',str(SHELL)],input=REQUEST.read_bytes(),capture_output=True,env={**os.environ,'PYTHONOPTIMIZE':'2'},timeout=8,check=True)
        self.assertEqual(p.stdout,self.shell_output.stdout)
    def test_28_input_from_stdin_without_source_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=subprocess.run(['bash'],input=SHELL.read_bytes(),capture_output=True,cwd=tmp,timeout=8)
        self.assertNotEqual(p.returncode,0)  # No fixture by default, fail closed.
    def test_29_no_network_library_or_sha_in_execution(self):
        for file in (SHELL, ROOT/'deployment/G24S_cross_domain_core.py',ROOT/'deployment/G24S_oneliner_builder.py'):
            s=file.read_text()
            for word in ('hashlib','sha256(', 'urllib', 'socket', 'requests', 'subprocess', 'eval(', 'exec('):
                self.assertNotIn(word,s)
    def test_30_primes_begin_with_reserved_two_and_three(self): self.assertEqual(PRIMES[:5],[2,3,5,7,11])
    def test_31_primes_unique(self): self.assertEqual(len(set(PRIMES)),14)
    def test_32_register_empty_decodes_zero_states(self): self.assertEqual(decode_register(1),[0]*12)
    def test_33_register_no_unknown_factors(self):
        with self.assertRaises(ValueError): decode_register(PRIMES[-1]*59)
    def test_34_register_overflow_rejected(self):
        with self.assertRaises(ValueError): decode_register(5**4)
    def test_35_register_negative_rejected(self):
        with self.assertRaises(ValueError): decode_register(-1)
    def test_36_reserved_prime_rejected_for_domain(self):
        with self.assertRaises(ValueError): prime_transition(1,2,0,1)
    def test_37_direct_prime_power_update(self): self.assertEqual(prime_transition(1,5,0,1),5)
    def test_38_prime_increment(self): self.assertEqual(prime_transition(5,5,1,2),25)
    def test_39_prime_veto_state(self): self.assertEqual(prime_transition(5,5,1,3),125)
    def test_40_reject_illegal_authority_state(self):
        with self.assertRaises(ValueError): prime_transition(5,5,1,4)
    def test_41_reject_invalid_transition_jump(self):
        with self.assertRaises(ValueError): prime_transition(1,5,0,3)
    def test_42_reject_wrong_old_prime_exponent(self):
        with self.assertRaises(ValueError): prime_transition(25,5,1,3)
    def test_43_decode_full_configuration(self):
        g=5**2*7**3
        self.assertEqual(decode_configuration(encode_configuration(2,12,g)),(2,12,[2,3]+[0]*10))
    def test_44_reject_q_out_of_range(self):
        with self.assertRaises(ValueError): encode_configuration(3,0,1)
    def test_45_reject_head_out_of_range(self):
        with self.assertRaises(ValueError): encode_configuration(0,13,1)
    def test_46_reject_fake_source(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x.__setitem__('source','REAL')))
    def test_47_reject_real_mode(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x.__setitem__('mode','live')))
    def test_48_reject_unauthorized_network(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x.__setitem__('network',True)))
    def test_49_reject_unauthorized_deploy(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x.__setitem__('deployment',True)))
    def test_50_reject_unauthorized_trade(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x.__setitem__('trading',True)))
    def test_51_reject_unauthorized_credentials(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x.__setitem__('credentials',True)))
    def test_52_reject_external_action(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x.__setitem__('external_action',True)))
    def test_53_reject_absent_human_review(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x.__setitem__('human_review',False)))
    def test_54_reject_missing_domain(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x['domains'].pop('trader42')))
    def test_55_reject_unknown_domain(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x['domains'].__setitem__('supernatural_oracle',[4,False])))
    def test_56_reject_extra_root_field(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x.__setitem__('profit_guaranteed',True)))
    def test_57_reject_bool_instead_of_count(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x['domains'].__setitem__('trader42',[True,False])))
    def test_58_reject_float_count(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x['domains'].__setitem__('trader42',[3.0,False])))
    def test_59_reject_large_count(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x['domains'].__setitem__('trader42',[101,False])))
    def test_60_reject_negative_count(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x['domains'].__setitem__('trader42',[-1,False])))
    def test_61_reject_string_veto(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x['domains'].__setitem__('trader42',[3,'false'])))
    def test_62_reject_invalid_domain_tuple(self):
        with self.assertRaises(ValueError): run(altered(lambda x:x['domains'].__setitem__('trader42',[3])))
    def test_63_input_limit_fails_closed(self):
        p=subprocess.run(['bash',str(SHELL)],input=b' '*16385,capture_output=True,timeout=8)
        self.assertNotEqual(p.returncode,0)
    def test_64_real_world_evidence_false_even_all_researched(self):
        x=altered(lambda x:x.__setitem__('domains',{k:[100,False] for k in DOMAINS}))
        r=run(x)
        self.assertEqual(r['synthetic_reviewed'],12)
        self.assertFalse(r['real_world_outcomes_proved'])
        self.assertFalse(r['deployment_allowed'])
        self.assertFalse(r['trading_allowed'])
    def test_65_all_vetoes_never_authorize(self):
        x=altered(lambda x:x.__setitem__('domains',{k:[100,True] for k in DOMAINS}))
        r=run(x)
        self.assertEqual(r['vetoed'],12)
        self.assertEqual(r['approved_external_actions'],0)
    def test_66_manifest_is_valid(self): self.assertTrue(validate_manifest(json.loads(MANIFEST.read_text())))
    def test_67_manifest_rejects_extra_authority(self):
        x=json.loads(MANIFEST.read_text());x['execution_policy']['deployment']=True
        with self.assertRaises(ValueError):validate_manifest(x)
    def test_68_manifest_rejects_removed_domain(self):
        x=json.loads(MANIFEST.read_text());x['domains'].pop()
        with self.assertRaises(ValueError):validate_manifest(x)
    def test_69_parent_metadata_constraints_pass(self):self.assertTrue(validate_parents(*parents(),date(2026,11,10)))
    def test_70_parent_real_peace_claim_rejected(self):
        p=list(parents());p[1]['all_goals_achieved']=True
        with self.assertRaises(ValueError):validate_parents(*p,date(2026,11,10))
    def test_71_parent_live_trade_rejected(self):
        p=list(parents());p[2]['live_armed']=True
        with self.assertRaises(ValueError):validate_parents(*p,date(2026,11,10))
    def test_72_parent_relaxed_risk_rejected(self):
        p=list(parents());p[2]['risk']['max_order_quote_usdt']='100'
        with self.assertRaises(ValueError):validate_parents(*p,date(2026,11,10))
    def test_73_parent_g23_deployment_rejected(self):
        p=list(parents());p[0]['real_world_deployment']=True
        with self.assertRaises(ValueError):validate_parents(*p,date(2026,11,10))
    def test_74_parent_future_review_rejected(self):
        with self.assertRaises(ValueError):validate_parents(*parents(),date(2026,11,9))
    def test_75_parent_stale_review_rejected(self):
        with self.assertRaises(ValueError):validate_parents(*parents(),date(2027,5,11))
    def test_76_parent_within_exact_review_window(self):
        self.assertTrue(validate_parents(*parents(),date(2026,11,10)+timedelta(days=180)))
    def test_125_independent_auditor_replays_all_domains(self):
        result=independent_check()
        self.assertTrue(result['identical_12_domain_report'])
        self.assertEqual((result['domains_checked'],result['prime_power_writes'],result['integer_bits']), (12,20,98))

    def test_126_independent_auditor_refuses_changed_shell_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/'bad_shell.sh'
            content=SHELL.read_bytes().replace(b'G24S',b'G25',1)
            self.assertNotEqual(content,SHELL.read_bytes())
            f.write_bytes(content)
            with self.assertRaises(ValueError):independent_check(binary=f)



# Each named domain is independently driven through all three research states.
for i, name in enumerate(DOMAINS):
    for j, (checks, veto, expected) in enumerate(((0,False,'EVIDENCE_GAP'),
            (3,False,'SYNTHETIC_REVIEW_ONLY'),(100,True,'VETOED'))):
        def test(self, name=name, checks=checks, veto=veto, expected=expected):
            request=altered(lambda x:x['domains'].__setitem__(name,[checks,veto]))
            actual=run(request)
            row=next(r for r in actual['domains'] if r['domain']==name)
            self.assertEqual(row['state'],expected)
            self.assertFalse(actual['real_world_outcomes_proved'])
            self.assertFalse(actual['deployment_allowed'])
            self.assertFalse(actual['trading_allowed'])
        setattr(G24STests, f'test_{77+i*3+j:03d}_{name}_independent_state_{j}',test)

# For each domain, check that the physically one-line implementation agrees
# with the independently readable reference core on modified inputs.
for i, name in enumerate(DOMAINS):
    def test(self, name=name):
        request=altered(lambda x:x['domains'].__setitem__(name,[100,True]))
        expected=run(request)
        payload=json.dumps(request,ensure_ascii=False).encode('utf-8')
        p=subprocess.run(['bash',str(SHELL)],input=payload,capture_output=True,timeout=8)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout),expected)
    setattr(G24STests,f'test_{113+i:03d}_{name}_shell_and_core_parity',test)

if __name__=='__main__':
    unittest.main(verbosity=2)
