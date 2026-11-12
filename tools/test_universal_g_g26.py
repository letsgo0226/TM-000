#!/usr/bin/env python3
"""G26: exact symbolic logarithm of G22/G23 finite TM, never G24/G25."""
import json
from pathlib import Path
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEP = ROOT / 'deployment'
sys.path.insert(0, str(DEP))
from G26_Exact_Log_TM_Core import (
    run_g26, formal_add, symbolic_log_product, integer_from_formal,
)
from G23_Prime_Power_TM_core import (
    first_primes, factor_tape, exponent_at, zigzag, encode_configuration,
    decode_configuration, prime_power_step,
)
from G22_Blank_Tape_TM_core import (
    create_self_printer, machine_from_canonical_code, encode_full_table,
)
from G26_Oneliner_Builder import build

G23 = DEP / 'Universal_G_G23_Prime_Power_2KB.sh'
SHELL = DEP / 'Universal_G_G26_Exact_Formal_Log_2KB.sh'


class G26Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = run_g26()
        cls.shell_proc = subprocess.run(['bash', str(SHELL)], text=True,
                                        capture_output=True, timeout=30, check=True)
        cls.shell = json.loads(cls.shell_proc.stdout)
        cls.primes = first_primes(26)

    def test_01_correct_status(self):
        self.assertEqual(self.core['status'], 'EXACT_FORMAL_LOG_G22_G23_TM_VERIFIED')

    def test_02_rules_unchanged(self):
        self.assertEqual(self.core['original_rules'], 1140)

    def test_03_all_transitions_executed(self):
        self.assertEqual(self.core['steps'], 3505682)

    def test_04_true_integer_writes(self):
        self.assertEqual(self.core['prime_power_writes'], 4321)

    def test_05_every_write_has_log_addition(self):
        self.assertEqual(self.core['formal_log_additions'], 4321)

    def test_06_2160_output_bits(self):
        self.assertEqual(self.core['canonical_table_bits'], 2160)

    def test_07_log_terms_equal_nonblank_cells(self):
        self.assertEqual(self.core['formal_log_terms'], 2160)

    def test_08_final_exact_integer_size(self):
        self.assertEqual(self.core['tape_integer_bits'], 41137)

    def test_09_full_configuration_integer_size(self):
        self.assertEqual(self.core['full_configuration_integer_bits'], 44568)

    def test_10_actual_integer_updates(self):
        self.assertTrue(self.core['actual_prime_power_integer_updated'])

    def test_11_exact_formal_additive_proof(self):
        self.assertTrue(self.core['exact_log_addition'])

    def test_12_independent_integer_factorization(self):
        self.assertTrue(self.core['independent_full_integer_factorization'])

    def test_13_log_to_integer_roundtrip(self):
        self.assertTrue(self.core['exact_log_integer_roundtrip'])

    def test_14_g22_result_equal(self):
        self.assertTrue(self.core['g22_output_equal'])

    def test_15_g23_prime_mapping_equal(self):
        self.assertTrue(self.core['g23_prime_mapping_equal'])

    def test_16_reserved_prime_log_basis(self):
        self.assertEqual(self.core['full_configuration_log_symbols'], 2162)

    def test_17_no_floating_point_logarithm(self):
        self.assertFalse(self.core['numerical_floating_logs_used'])

    def test_18_strict_numeric_read_checks(self):
        self.assertEqual(self.core['integer_read_checks'], 4096)

    def test_19_no_cryptographic_digests(self):
        self.assertFalse(self.core['sha_used'])

    def test_20_no_applications_in_g26(self):
        self.assertIs(self.core['applications_integrated'], False)
        self.assertIs(self.core['future_g27_applications_integrated'], False)

    def test_21_only_offline_paper(self):
        self.assertTrue(self.core['paper_only'])
        self.assertFalse(self.core['network_access'])
        self.assertFalse(self.core['autonomous_deployment'])
        self.assertEqual(self.core['live_trades'], 0)

    def test_22_no_oracle_or_divinity_claim(self):
        self.assertFalse(self.core['halting_oracle'])
        self.assertFalse(self.core['literal_divinity_proved'])

    def test_23_shell_matches_key_metrics(self):
        s = self.shell
        self.assertEqual((s['version'],s['steps'],s['rules'],s['bits'],
                          s['integer_bits'],s['full_configuration_integer_bits']),
                         ('G26',3505682,1140,2160,41137,44568))

    def test_24_shell_exact_formal_log_and_numeric_decode(self):
        self.assertTrue(self.shell['formal_log_exact'])
        self.assertTrue(self.shell['exact_numeric_decode'])
        self.assertTrue(self.shell['prime_power_arithmetic'])

    def test_25_shell_has_no_application_layer(self):
        self.assertFalse(self.shell['application_layer'])
        self.assertFalse(self.shell['g27_integrated'])

    def test_26_shell_is_under_2kb(self):
        self.assertLessEqual(len(SHELL.read_bytes()),2048)
        self.assertEqual(len(SHELL.read_bytes()),1938)

    def test_27_shell_is_one_line(self):
        self.assertEqual(SHELL.read_bytes().count(b'\n'),1)

    def test_28_bash_syntax(self):
        self.assertEqual(subprocess.run(['bash','-n',str(SHELL)],capture_output=True).returncode,0)

    def test_29_builder_byte_exact_reproduction(self):
        self.assertEqual(build(G23.read_bytes()),SHELL.read_bytes())

    def test_30_source_has_no_application_import(self):
        for f in ('G26_Exact_Log_TM_Core.py','Universal_G_G26_Exact_Formal_Log_2KB.sh'):
            src=(DEP/f).read_text()
            for banned in ('G24_', 'G25_', 'G27_', 'hashlib', 'sha256(', 'math.log(', 'log10('):
                self.assertNotIn(banned,src)

    def test_31_wrong_step_budget_refused(self):
        with self.assertRaises(ValueError):run_g26(step_budget=0)

    def test_32_incomplete_execution_refused(self):
        with self.assertRaisesRegex(ValueError,'STEP_LIMIT'):
            run_g26(step_budget=1,strict_reads=1)

    def test_33_wrong_strict_read_budget_refused(self):
        with self.assertRaises(ValueError):run_g26(step_budget=20,strict_reads=21)

    def test_34_blank_log_identity_is_zero(self):
        self.assertEqual(integer_from_formal({},self.primes),(1,1))
        self.assertEqual(symbolic_log_product({},{}),{})

    def test_35_log_product_equals_integer_product(self):
        a={0:2,-1:1}
        b={0:-1,1:3}
        c=symbolic_log_product(a,b)
        self.assertEqual(c,{0:1,-1:1,1:3})
        na,da=integer_from_formal(a,self.primes)
        nb,db=integer_from_formal(b,self.primes)
        nc,dc=integer_from_formal(c,self.primes)
        self.assertEqual(na*nb*dc,da*db*nc)

    def test_36_inverse_log_addition_is_zero(self):
        a={0:2,-1:1}
        self.assertEqual(symbolic_log_product(a,{k:-v for k,v in a.items()}),{})

    def test_37_reject_invalid_additive_delta(self):
        with self.assertRaises(ValueError):formal_add({},0,9)

    def test_38_reject_negative_tape_exponent(self):
        with self.assertRaises(ValueError):formal_add({},0,-1)

    def test_39_reject_overflow_tape_exponent(self):
        with self.assertRaises(ValueError):formal_add({0:8},0,1)

    def test_40_reject_float_log_coefficient(self):
        with self.assertRaises(ValueError):symbolic_log_product({}, {0:0.5})

    def test_41_reject_float_position(self):
        with self.assertRaises(ValueError):integer_from_formal({0.0:1},self.primes)

    def test_42_reject_invalid_position_budget(self):
        with self.assertRaises(ValueError):integer_from_formal({3001:1},self.primes)

    def test_43_unchanged_transition_preserves_log(self):
        self.assertEqual(formal_add({0:3},0,0),{0:3})

    def test_44_deletion_of_last_exponent(self):
        self.assertEqual(formal_add({0:3},0,-3),{})

    def test_45_integer_log_maps_negative_tape_coordinates(self):
        self.assertEqual(integer_from_formal({-1:2},self.primes),(49,1))

    def test_46_symbolic_log_allows_exact_rational_inverse(self):
        self.assertEqual(integer_from_formal({0:-2},self.primes),(1,25))

    def test_47_integer_multiply_and_divide_inverse(self):
        self.assertEqual(prime_power_step(prime_power_step(5,5,1,3),5,3,1),5)

    def test_48_reject_wrong_godel_power_update(self):
        with self.assertRaises(ValueError):prime_power_step(25,5,1,0)

    def test_49_no_unauthorized_shell_side_effect_primitives(self):
        src=SHELL.read_text()
        for banned in ('open(', 'socket', 'urllib', 'requests', 'subprocess', 'eval(', 'exec(', 'os.system'):
            self.assertNotIn(banned,src)

    def test_50_shell_optimized_mode_equivalent(self):
        env=dict(os.environ,PYTHONOPTIMIZE='2')
        p=subprocess.run(['bash',str(SHELL)],text=True,capture_output=True,timeout=30,env=env,check=True)
        self.assertEqual(p.stdout,self.shell_proc.stdout)


# Ten independent negative/positive additive identities across distinct prime positions.
for j in range(10):
    def test_roundtrip(self,j=j):
        start = {j:1}
        after = formal_add(start,j,1)
        self.assertEqual(after,{j:2})
        self.assertEqual(formal_add(after,j,-1),start)
        numerator,denominator=integer_from_formal(after,self.primes)
        self.assertEqual((numerator,denominator),(self.primes[2+zigzag(j)]**2,1))
    setattr(G26Tests,f'test_{51+j:02}_formal_log_prime_basis_position_{j}',test_roundtrip)


if __name__=='__main__':
    unittest.main(verbosity=2)
