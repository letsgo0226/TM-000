#!/usr/bin/env python3
"""G21: finite, deterministic, single-tape self-table printer correctness tests."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'deployment'))
from G21_Blank_Tape_TM_core import (
 ALPHABET, DIRECTIONS, rule_table_A, encode_A, decode_A,
 machine_from_canonical_code, encode_full_table, create_self_printer,
 simulate,extract_output,audit)
from G21_Independent_Audit import independent_audit

SHELL=ROOT/'deployment/Universal_G_G21_Blank_Tape_TM_2KB.sh'
CODE=ROOT/'deployment/G21_canonical_table_bits.txt'
EXPANDED=ROOT/'deployment/G21_expanded_transition_table.json'

class G21Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m,cls.code=create_self_printer()
  cls.r=audit()
  cls.i=independent_audit()
  cls.shell=subprocess.run(['bash',str(SHELL)],capture_output=True,text=True,check=True,timeout=30)

 def test_01_one_tape_explicit(self):self.assertEqual(self.r['tape_count'],1)
 def test_02_blank_initial(self):self.assertEqual(self.r['initial_tape'],'BLANK')
 def test_03_deterministic_no_duplicate(self):self.assertEqual(len(self.m),len(set(self.m)))
 def test_04_60_controller_rules(self):self.assertEqual(len(rule_table_A()),60)
 def test_05_1080_printer_rules(self):self.assertEqual(self.r['printer_rule_count'],1080)
 def test_06_all_1140_rules(self):self.assertEqual(len(self.m),1140)
 def test_07_2160_output_bits(self):self.assertEqual(len(self.code),2160)
 def test_08_code_is_binary(self):self.assertEqual(set(self.code),{'0','1'})
 def test_09_first_half_is_second_half(self):self.assertEqual(self.code[:1080],self.code[1080:])
 def test_10_machine_canonical_encode_matches(self):self.assertEqual(encode_full_table(self.m),self.code)
 def test_11_code_decodes_to_exact_machine(self):self.assertEqual(machine_from_canonical_code(self.code),self.m)
 def test_12_expanded_a_codec_roundtrip(self):
  a=rule_table_A();self.assertEqual(decode_A(encode_A(a)),a)
 def test_13_controller_code_has_18bit_records(self):self.assertEqual(len(self.code[:1080])//18,60)
 def test_14_blank_tape_execution_halts(self):self.assertEqual(self.r['status'],'BLANK_TAPE_SELF_TABLE_CODE_VERIFIED')
 def test_15_known_step_count(self):self.assertEqual(self.r['steps'],3505682)
 def test_16_known_halting_head(self):self.assertEqual(self.r['head'],1079)
 def test_17_exact_output_hash(self):
  self.assertEqual(self.r['output_sha256'],'7a3b17a33e763fc1b235b7979a4b023e15b722ce6ffed054fa76771f244e8700')
 def test_18_no_runtime_external_data(self):self.assertFalse(self.r['external_tape_input'])
 def test_19_no_network_or_file_call_in_tm(self):
  self.assertFalse(self.r['source_file_read_by_tm']);self.assertNotIn('file',str(self.m))
 def test_20_not_expanded_json_print(self):self.assertFalse(self.r['full_rule_list_printed_as_json'])
 def test_21_not_halting_oracle(self):self.assertFalse(self.r['halt_oracle'])
 def test_22_not_god_proof(self):self.assertFalse(self.r['divinity_proved'])
 def test_23_not_deployed(self):self.assertFalse(self.r['production_deployed'])
 def test_24_independent_full_table_verified(self):self.assertEqual(self.i['actual_transition_rules'],1140)
 def test_25_independent_exact_output_and_hash(self):
  self.assertTrue(self.i['exact_output']);self.assertEqual(self.i['output_sha256'],self.r['output_sha256'])
 def test_26_independent_exact_step_count(self):self.assertEqual(self.i['steps'],self.r['steps'])
 def test_27_expanded_json_has_1140_exact(self):self.assertEqual(len(json.loads(EXPANDED.read_text())),1140)
 def test_28_canonical_bit_file_exact(self):self.assertEqual(CODE.read_text(),self.code+'\n')
 def test_29_state_origin_b0(self):self.assertIn((10,'_'),self.m)
 def test_30_printer_chain_returns_to_a(self):self.assertEqual(self.m[(1089,'_')][2],0)
 def test_31_halt_state_has_no_rule(self):self.assertFalse(any(q==9 for q,_ in self.m))
 def test_32_interpreter_step_budget_is_not_oracle(self):
  p=simulate(self.m,10);self.assertEqual(p['status'],'STEP_LIMIT')
 def test_33_first_1080_printer_steps(self):
  p=simulate(self.m,1080);self.assertEqual(p['status'],'STEP_LIMIT');self.assertEqual(p['state'],0)
  self.assertEqual(''.join(p['tape'][i] for i in range(1080)),self.code[:1080])
 def test_34_reject_truncated_a_code(self):
  with self.assertRaises(ValueError):decode_A(self.code[:1079])
 def test_35_reject_nonbinary_code(self):
  with self.assertRaises(ValueError):machine_from_canonical_code('0x')
 def test_36_reject_odd_code(self):
  with self.assertRaises(ValueError):machine_from_canonical_code('011')
 def test_37_reject_undefined_direction(self):
  s=list(self.code[:1080]);s[12:14]=list('11')
  with self.assertRaises(ValueError):decode_A(''.join(s))
 def test_38_reject_duplicate_a_rule(self):
  first=self.code[:18];bad=self.code[:18]+first+self.code[36:1080]
  with self.assertRaises(ValueError):decode_A(bad)
 def test_39_reject_noncanonical_a_order(self):
  bits=self.code[:1080];bad=bits[18:36]+bits[:18]+bits[36:]
  with self.assertRaises(ValueError):decode_A(bad)
 def test_40_reject_missing_printer_rule(self):
  m=self.m.copy();del m[(10,'_')]
  with self.assertRaises(ValueError):encode_full_table(m)
 def test_41_reject_extra_transition_rule(self):
  m=self.m.copy();m[(100000,'_')]=('1','R',100001)
  with self.assertRaises(ValueError):encode_full_table(m)
 def test_42_reject_corrupted_printer_step(self):
  m=self.m.copy();v,d,n=m[10,'_'];m[10,'_']=('1' if v=='0' else '0',d,n)
  altered=encode_full_table(m)
  self.assertNotEqual(altered,self.code)
  self.assertNotEqual(altered[:1080],altered[1080:])
 def test_43_shell_syntax_valid(self):
  self.assertEqual(subprocess.run(['bash','-n',str(SHELL)]).returncode,0)
 def test_44_shell_one_physical_line(self):self.assertEqual(SHELL.read_bytes().count(b'\n'),1)
 def test_45_shell_under_2048(self):self.assertLessEqual(len(SHELL.read_bytes()),2048)
 def test_46_shell_replays_real_tm(self):
  x=json.loads(self.shell.stdout)
  self.assertEqual((x['rules'],x['steps'],x['bits'],x['sha256']),
                   (1140,3505682,2160,self.r['output_sha256']))
 def test_47_shell_still_readonly(self):
  x=json.loads(self.shell.stdout)
  self.assertTrue(x['blank_tape']);self.assertTrue(x['no_external_input']);self.assertFalse(x['printed_expanded_json'])
 def test_48_shell_ignores_stdin(self):
  p=subprocess.run(['bash',str(SHELL)],input='evil extra tape input',text=True,capture_output=True,timeout=30)
  self.assertEqual((p.returncode,p.stdout),(0,self.shell.stdout))
 def test_49_shell_optimized(self):
  e={**os.environ,'PYTHONOPTIMIZE':'2'}
  p=subprocess.run(['bash',str(SHELL)],env=e,text=True,capture_output=True,timeout=30)
  self.assertEqual((p.returncode,p.stdout),(0,self.shell.stdout))
 def test_50_shell_without_external_source_files(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=subprocess.run(['bash'],input=SHELL.read_bytes(),cwd=tmp,capture_output=True,timeout=30)
   self.assertEqual(p.returncode,0,p.stderr)
   self.assertEqual(p.stdout,self.shell.stdout.encode())
 def test_51_shell_no_compressed_payload(self):
  src=SHELL.read_bytes()
  for token in (b'base64',b'zlib',b'eval(',b'exec(',b'socket',b'open('):self.assertNotIn(token,src)
 def test_52_actual_full_table_output_roundtrip(self):self.assertTrue(self.i['full_list_reconstructed'])
 def test_53_bounded_blanks_not_confused_with_halt(self):
  p=simulate(self.m,1080);self.assertEqual(p['status'],'STEP_LIMIT');self.assertNotEqual(p['state'],9)
 def test_54_full_rule_list_is_deterministic(self):
  table=json.loads(EXPANDED.read_text());keys=[(r['state'],r['read']) for r in table]
  self.assertEqual(len(keys),len(set(keys)))
 def test_55_disallow_overstated_program_self_read(self):
  self.assertFalse(self.r['source_file_read_by_tm'])
 def test_56_tape_does_not_contain_control_markers_at_halt(self):
  final=simulate(self.m,3600000)
  self.assertEqual(final['status'],'HALTED')
  self.assertEqual(extract_output(final,2160),self.code)

if __name__=='__main__':unittest.main(verbosity=2)
