#!/usr/bin/env python3
"""G16 bounded deterministic TM, prime Gödel, and no-trading regression checks."""
import copy
import json
import random
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "deployment"))
from G16_God_Source_TM_core import example, run, encode, decode, PRIMES

SHELL = ROOT / "deployment/Universal_G_G16_TM_Plaintext_2KB.sh"

def cli(x):
    return subprocess.run(["bash", str(SHELL)], input=json.dumps(x),
                          text=True, capture_output=True, timeout=12)

class Tests(unittest.TestCase):
    def test_01_unary_append(self):
        a=run(example())
        self.assertEqual((a["status"], a["steps"], a["head"]), ("HALTED",3,2))
        self.assertEqual(a["nonblank_cells"], [[0,"1"],[1,"1"],[2,"1"]])
    def test_02_compact_matches(self):
        p=cli(example())
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout),run(example()))
    def test_03_empty_unary(self):
        x=example();x["machine"]["input"]=[]
        self.assertEqual(run(x)["nonblank_cells"],[[0,"1"]])
    def test_04_step_limit(self):
        x=example();x["max_steps"]=1
        self.assertEqual(run(x)["status"],"STEP_LIMIT")
    def test_05_undefined_rule_stuck(self):
        x=example();x["machine"]["rules"]=x["machine"]["rules"][:1]
        self.assertEqual(run(x)["status"],"STUCK")
    def test_06_negative_head(self):
        x=example();x["machine"]["rules"]=[["scan","1","1","L","HALT"]]
        self.assertEqual(run(x)["head"],-1)
    def test_07_no_head_move(self):
        x=example();x["machine"]["rules"]=[["scan","1","1","S","HALT"]]
        self.assertEqual(run(x)["head"],0)
    def test_08_godel_empty_identity(self):
        self.assertEqual((encode(b""),decode(1)),(1,b""))
    def test_09_godel_all_byte_values(self):
        self.assertEqual(decode(encode(bytes(range(256)))),bytes(range(256)))
        self.assertEqual(len(PRIMES),256)
    def test_10_invalid_digit(self):
        for v in (-1,0,2048,2048+4,1.2):
            with self.subTest(v=v),self.assertRaises(ValueError):decode(v)
    def test_11_random_codes(self):
        r=random.Random(2026)
        for n in (1,5,17,64,128):
            b=bytes(r.randrange(256) for _ in range(n))
            self.assertEqual(decode(encode(b)),b)
    def test_12_true_plaintext_one_line(self):
        b=SHELL.read_bytes()
        self.assertLessEqual(len(b),2048)
        self.assertEqual(b.count(b"\n"),1)
        for bad in (b"base64",b"zlib",b"eval(",b"exec("):
            self.assertNotIn(bad,b)
    def test_13_unicode_symbols(self):
        x=example();m=x["machine"]
        m["alphabet"]=["_","愛"];m["input"]=["愛"]
        m["rules"]=[["scan","愛","愛","R","scan"],["scan","_","愛","S","HALT"]]
        self.assertEqual(run(x),json.loads(cli(x).stdout))
    def test_14_repeatable_interpreter(self):
        self.assertEqual(run(example()),run(example()))
    def test_15_epistemic_boundaries(self):
        x=run(example())
        for key in ("live_allowed","halting_oracle","god_identity_proved","certified_as_real_trading"):
            self.assertIs(x[key],False)
        self.assertEqual(x["orders_submitted"],0)
    def test_16_random_machine_agreement(self):
        r=random.Random(42)
        for i in range(8):
            x=example();x["max_steps"]=r.randrange(1,20)
            x["machine"]["input"]=["1"]*r.randrange(0,5)
            x["machine"]["rules"]=[
                ["scan","1",r.choice(["1","_"]),r.choice(["L","R","S"]),r.choice(["scan","HALT"])],
                ["scan","_",r.choice(["1","_"]),r.choice(["L","R","S"]),r.choice(["scan","HALT"])]]
            self.assertEqual(json.loads(cli(x).stdout),run(x))
    def test_17_compact_tape_halts(self):
        p=cli(example())
        self.assertEqual(json.loads(p.stdout)["status"],"HALTED")
    def test_18_nonhalting_cycle_bounded(self):
        x=example();x["machine"]["rules"]=[
            ["scan","1","1","R","scan"],["scan","_","_","R","scan"]]
        x["max_steps"]=9
        self.assertEqual(run(x)["status"],"STEP_LIMIT")

BAD = [
 ("network",lambda x:x.update(network=True)),
 ("orders",lambda x:x.update(order_submission=True)),
 ("live",lambda x:x.update(live_armed=True)),
 ("execute",lambda x:x.update(execute_external=True)),
 ("wrong_source",lambda x:x.update(source="MARKET")),
 ("wrong_mode",lambda x:x.update(mode="live")),
 ("network_missing",lambda x:x.pop("network")),
 ("orders_missing",lambda x:x.pop("order_submission")),
 ("live_missing",lambda x:x.pop("live_armed")),
 ("execute_missing",lambda x:x.pop("execute_external")),
 ("budget_zero",lambda x:x.update(max_steps=0)),
 ("budget_big",lambda x:x.update(max_steps=99999)),
 ("budget_float",lambda x:x.update(max_steps=1.2)),
 ("budget_bool",lambda x:x.update(max_steps=True)),
 ("missing_machine",lambda x:x.pop("machine")),
 ("non_dict_machine",lambda x:x.update(machine="machine")),
 ("extra_instruction",lambda x:x["machine"].update(command="BUY")),
 ("missing_alphabet",lambda x:x["machine"].pop("alphabet")),
 ("empty_alphabet",lambda x:x["machine"].update(alphabet=[])),
 ("duplicate_alphabet",lambda x:x["machine"].update(alphabet=["_","1","1"])),
 ("blank_not_alphabet",lambda x:x["machine"].update(blank="0")),
 ("equal_start_halt",lambda x:x["machine"].update(halt="scan")),
 ("empty_start",lambda x:x["machine"].update(start="")),
 ("long_start",lambda x:x["machine"].update(start="s"*40)),
 ("bad_input_symbol",lambda x:x["machine"].update(input=["2"])),
 ("long_input",lambda x:x["machine"].update(input=["1"]*65)),
 ("nonlist_input",lambda x:x["machine"].update(input="111")),
 ("no_rules",lambda x:x["machine"].update(rules=[])),
 ("duplicate_rule",lambda x:x["machine"]["rules"].append(list(x["machine"]["rules"][0]))),
 ("invalid_move",lambda x:x["machine"]["rules"][0].__setitem__(3,"UP")),
 ("read_outside_alphabet",lambda x:x["machine"]["rules"][0].__setitem__(1,"x")),
 ("write_outside_alphabet",lambda x:x["machine"]["rules"][0].__setitem__(2,"x")),
]
for idx,(name,mutator) in enumerate(BAD,19):
    def test(self,mutator=mutator,idx=idx):
        x=example();mutator(x)
        with self.assertRaises((ValueError,KeyError,TypeError)):run(x)
        if idx in (19,20,21,22,23,24,29,30,31,46,48,50):
            self.assertNotEqual(cli(x).returncode,0)
    setattr(Tests,f"test_{idx:02d}_{name}",test)

if __name__=="__main__":
    unittest.main(verbosity=2)
