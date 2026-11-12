#!/usr/bin/env python3
"""G23: exact prime-power integer arithmetic over the full G22 blank-tape TM."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'deployment'))
from G23_Prime_Power_TM_core import (
    replay,zigzag,unzigzag,first_primes,exponent_at,prime_power_step,
    factor_tape,encode_configuration,decode_configuration,MAX_ABS_HEAD,ALPHABET)
from G22_Blank_Tape_TM_core import create_self_printer,machine_from_canonical_code,encode_full_table,simulate,extract_output

SHELL=ROOT/'deployment/Universal_G_G23_Prime_Power_2KB.sh'
BUILDER=ROOT/'deployment/G23_Oneliner_Builder.py'
G22_BITS=ROOT/'deployment/G22_canonical_table_bits.txt'
G22_RULES=ROOT/'deployment/G22_expanded_transition_table.json'

class PrimePowerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=replay()
        cls.runner=subprocess.run(['bash',str(SHELL)],capture_output=True,text=True,timeout=40,check=True)
        cls.shell=json.loads(cls.runner.stdout)
        cls.primes=first_primes(12)

    def test_01_g23_actual_replay_completed(self):
        self.assertEqual(self.result['status'],'PRIME_POWER_INTEGER_SELF_TABLE_VERIFIED')
    def test_02_three_and_half_million_steps(self):
        self.assertEqual(self.result['steps'],3505682)
    def test_03_canonical_1140_rules(self):
        self.assertEqual(self.result['original_rule_count'],1140)
    def test_04_2160_table_bits(self):
        self.assertEqual(self.result['final_canonical_code_bits'],2160)
    def test_05_updates_are_integer_arithmetic(self):
        self.assertTrue(self.result['actual_integer_arithmetic'])
    def test_06_arithmetic_symbol_updates_count(self):
        self.assertEqual(self.result['prime_power_writes'],4321)
    def test_07_true_integer_read_valuations(self):
        self.assertEqual(self.result['integer_read_checks'],4096)
    def test_08_big_integer_bit_length(self):
        self.assertEqual(self.result['integer_bit_length'],41137)
    def test_09_full_configuration_is_an_integer(self):
        self.assertEqual(self.result['final_configuration_integer_bit_length'],44568)
    def test_10_independent_integer_factorization(self):
        self.assertTrue(self.result['full_numeric_decode_matches_tape'])
    def test_11_integer_tape_equals_g22(self):
        self.assertTrue(self.result['entire_output_matches_g22'])
    def test_12_complete_rule_table_roundtrip(self):
        self.assertTrue(self.result['fully_reversible_rule_table'])
    def test_13_baseline_plain_tm_replayed(self):
        self.assertTrue(self.result['plain_tm_replay_matches'])
    def test_14_state_and_head_prime_power_encodable(self):
        self.assertTrue(self.result['state_and_head_encoded_with_prime_powers'])
    def test_15_blank_tape_initial_integer_is_one(self):
        self.assertEqual(encode_configuration(10,0,1),2**11*3)
    def test_16_full_configuration_decodes_q_head_tape(self):
        value=5**2*7**3*11
        c=encode_configuration(7,-1,value)
        self.assertEqual(decode_configuration(c,self.primes),(7,-1,{0:'1',-1:'E0',1:'0'}))
    def test_17_zigzag_small_points(self):
        self.assertEqual([zigzag(i) for i in (0,-1,1,-2,2)],[0,1,2,3,4])
    def test_18_zigzag_roundtrip(self):
        self.assertEqual([unzigzag(zigzag(i)) for i in range(-100,101)],list(range(-100,101)))
    def test_19_primes_start_at_two(self):
        self.assertEqual(first_primes(5),[2,3,5,7,11])
    def test_20_tape_reserves_2_and_3_for_q_h(self):
        self.assertEqual(factor_tape(5**2*7**3*11,self.primes),{0:'1',-1:'E0',1:'0'})
    def test_21_tape_empty_identity_one(self):
        self.assertEqual(factor_tape(1,self.primes),{})
    def test_22_numeric_exponents_correct(self):
        self.assertEqual((exponent_at(5**4*7**2,5),exponent_at(5**4*7**2,7),exponent_at(5**4*7**2,11)),(4,2,0))
    def test_23_prime_multiplication_changes_symbol(self):
        self.assertEqual(prime_power_step(5,5,1,2),25)
    def test_24_prime_division_changes_symbol(self):
        self.assertEqual(prime_power_step(125,5,3,1),5)
    def test_25_prime_power_write_same_is_identity(self):
        self.assertEqual(prime_power_step(125,5,3,3),125)
    def test_26_reject_incorrect_old_symbol_exponent(self):
        with self.assertRaises(ValueError):prime_power_step(25,5,1,4)
    def test_27_reject_composite_unknown_residue(self):
        with self.assertRaises(ValueError):factor_tape(13,self.primes[:5])
    def test_28_reject_out_of_alphabet_exponent(self):
        with self.assertRaises(ValueError):factor_tape(5**9,self.primes)
    def test_29_reject_nonpositive_integer(self):
        with self.assertRaises(ValueError):factor_tape(0,self.primes)
    def test_30_reject_negative_head_range(self):
        with self.assertRaises(ValueError):encode_configuration(0,MAX_ABS_HEAD+1,1)
    def test_31_reject_negative_state(self):
        with self.assertRaises(ValueError):encode_configuration(-1,0,1)
    def test_32_reject_tape_with_reserved_primes(self):
        with self.assertRaises(ValueError):encode_configuration(1,0,10)
    def test_33_reject_invalid_time_budget(self):
        with self.assertRaises(ValueError):replay(max_steps=0)
    def test_34_reject_incomplete_execution(self):
        with self.assertRaisesRegex(ValueError,'STEP_LIMIT'):replay(max_steps=1,integer_read_check_steps=1)
    def test_35_reject_invalid_strict_read_budget(self):
        with self.assertRaises(ValueError):replay(max_steps=100,integer_read_check_steps=101)
    def test_36_shell_plaintext_2kb_one_line(self):
        self.assertLessEqual(len(SHELL.read_bytes()),2048)
        self.assertEqual(SHELL.read_bytes().count(b'\n'),1)
    def test_37_shell_is_syntactically_valid_bash(self):
        self.assertEqual(subprocess.run(['bash','-n',str(SHELL)],capture_output=True).returncode,0)
    def test_38_shell_actual_integer_arithmetic(self):
        self.assertTrue(self.shell['prime_power_arithmetic'])
    def test_39_shell_same_full_numeric_metrics(self):
        self.assertEqual((self.shell['steps'],self.shell['rules'],self.shell['bits'],self.shell['integer_bits'],self.shell['full_configuration_integer_bits']),
                         (3505682,1140,2160,41137,44568))
    def test_40_shell_exact_numeric_decode(self):
        self.assertTrue(self.shell['exact_numeric_decode'])
    def test_41_shell_no_cryptographic_sha_functions(self):
        paths=[SHELL,BUILDER,ROOT/'deployment/G23_Prime_Power_TM_core.py']
        for p in paths:
            s=p.read_text()
            for text in ('hashlib','sha256(','sha1('):self.assertNotIn(text,s)
    def test_42_shell_no_trade_or_network(self):
        self.assertEqual(self.shell['orders'],0)
        s=SHELL.read_text()
        for word in ('urllib','socket','requests','Binance','open(','eval(','exec('):self.assertNotIn(word,s)
    def test_43_plain_replay_has_same_binary_output(self):
        m,reference=create_self_printer()
        self.assertEqual(reference,G22_BITS.read_text().strip())
        self.assertEqual(machine_from_canonical_code(reference),m)
        self.assertEqual(encode_full_table(m),reference)
    def test_44_original_g22_rules_still_1140(self):
        self.assertEqual(len(json.loads(G22_RULES.read_text())),1140)
    def test_45_machine_has_no_god_or_oracle_proof(self):
        self.assertFalse(self.result['god_identity_proved'])
        self.assertFalse(self.result['halting_oracle_proved'])
    def test_46_replay_has_no_live_orders(self):
        self.assertEqual(self.result['external_orders'],0)
        self.assertFalse(self.result['live_trading'])
    def test_47_no_hash_used_in_output(self):
        self.assertFalse(self.result['sha_functions_used'])
        self.assertFalse(self.shell['sha_used'])
    def test_48_reproducible_one_liner_builder(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            for name in ('G23_Oneliner_Builder.py','G22_Blank_Tape_TM_core.py'):
                (d/name).write_bytes((ROOT/'deployment'/name).read_bytes())
            proc=subprocess.run([sys.executable,str(d/'G23_Oneliner_Builder.py')],capture_output=True,text=True,timeout=10)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertEqual((d/SHELL.name).read_bytes(),SHELL.read_bytes())
    def test_49_unauthenticated_external_provenance_not_claimed(self):
        self.assertNotIn('authenticated_source',self.result)
    def test_50_101_next_prime_cannot_fake_tape_symbol(self):
        with self.assertRaises(ValueError):factor_tape(first_primes(100)[-1],first_primes(12))
    def test_51_reject_nonprime_base_argument(self):
        with self.assertRaises(ValueError):exponent_at(10,1)
    def test_52_reject_wrong_valuation_on_prime_division(self):
        with self.assertRaises(ValueError):prime_power_step(1,5,1,0)

# For each of the 8 valid symbol exponent values, three prime bases are tested
# using actual numerical operations rather than only symbolic exponent arrays.
for exponent in range(8):
    for prime in (5,7,11):
        def test(self,exponent=exponent,prime=prime):
            start=prime**exponent
            next_code=exponent+1
            shifted=prime_power_step(start,prime,exponent,next_code)
            self.assertEqual(shifted,prime**next_code)
            self.assertEqual(prime_power_step(shifted,prime,next_code,exponent),start)
            self.assertEqual(exponent_at(shifted,prime),next_code)
        setattr(PrimePowerTests,f'test_{53+3*exponent+(5,7,11).index(prime):02d}_numeric_prime_{prime}_exponent_{exponent}',test)

if __name__=='__main__':unittest.main(verbosity=2)
