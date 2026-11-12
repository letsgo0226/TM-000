#!/usr/bin/env python3
"""125 bounded offline G27 tests: G26 formal-log math bridged to G24/G25 metadata."""
from copy import deepcopy
from pathlib import Path
import json, os, subprocess, sys, unittest

ROOT=Path(__file__).resolve().parents[1]
DEP=ROOT/'deployment'
sys.path.insert(0,str(DEP))
from G27_Exact_Log_Application_Bridge import DOMAINS,TOPICS,BASES,FORBIDDEN,run,decode_exact
from G27_Oneliner_Builder import build
from G26_Exact_Log_TM_Core import symbolic_log_product
from G24_Cross_Domain_Godel_Core import run as run24
from G25_Evidence_Core import run as run25

EXAMPLE=json.loads((DEP/'G27_example_request.json').read_text())
SHELL=DEP/'Universal_G_G27_Exact_Log_Audit_2KB.sh'
def sample(events=None,evidence=None):
 x=deepcopy(EXAMPLE)
 if events is not None:x['events']=events
 if evidence is not None:x['evidence']=evidence
 return x
def record(d,i,s):
 return [d,i,'provider_'+s,'reviewer_'+s,'record_'+s,'2026-09-01','2026-10-10']
def audit(o,opt=False):
 e={**os.environ}
 if opt:e['PYTHONOPTIMIZE']='2'
 return subprocess.run(['bash',str(SHELL)],input=json.dumps(o),text=True,capture_output=True,timeout=15,env=e)
def blocked(x):
 try:run(x)
 except (ValueError,TypeError,KeyError):return True
 return False

class G27Tests(unittest.TestCase):
 pass

def d01(t):t.assertEqual(run(EXAMPLE)['version'],'G27')
def d02(t):t.assertEqual(run(EXAMPLE)['status'],'SYNTHETIC_METADATA_UNVERIFIED')
def d03(t):t.assertEqual(len(DOMAINS),14)
def d04(t):t.assertEqual(len(TOPICS),43)
def d05(t):t.assertEqual(len(BASES),57)
def d06(t):t.assertEqual(len(set(BASES)),57)
def d07(t):t.assertEqual(BASES[0],5)
def d08(t):t.assertEqual(BASES[-1],277)
def d09(t):t.assertEqual(run(EXAMPLE)['combined_godel_integer'],120160600906782352207185858098135)
def d10(t):t.assertEqual(run(EXAMPLE)['distinct_topics_received'],6)
def d11(t):t.assertEqual(run(EXAMPLE)['events_replayed'],14)
def d12(t):t.assertEqual(run(EXAMPLE)['formal_log_terms'],20)
def d13(t):t.assertEqual(run(EXAMPLE)['exact_formal_log_additions'],20)
def d14(t):t.assertEqual(run(EXAMPLE)['integer_multiplicative_updates'],20)
def d15(t):t.assertTrue(run(EXAMPLE)['exact_log_product_identity'])
def d16(t):t.assertTrue(run(EXAMPLE)['direct_numeric_factorization_equal'])
def d17(t):t.assertFalse(run(EXAMPLE)['independent_evidence_authenticated'])
def d18(t):t.assertFalse(run(EXAMPLE)['independent_impact_proved'])
def d19(t):t.assertFalse(run(EXAMPLE)['world_peace_achieved'])
def d20(t):t.assertFalse(run(EXAMPLE)['all_sdgs_achieved'])
def d21(t):t.assertFalse(run(EXAMPLE)['all_dimensions_immortality_proved'])
def d22(t):t.assertFalse(run(EXAMPLE)['cultivated_meat_approved_or_cruelty_free_proved'])
def d23(t):t.assertFalse(run(EXAMPLE)['trader42_profit_validated'])
def d24(t):t.assertEqual(run(EXAMPLE)['orders_submitted'],0)
def d25(t):t.assertFalse(run(EXAMPLE)['production_deployed'])
def d26(t):t.assertEqual(len(SHELL.read_bytes()),1639)
def d27(t):t.assertEqual(SHELL.read_bytes().count(b'\n'),1)
def d28(t):t.assertEqual(subprocess.run(['bash','-n',str(SHELL)]).returncode,0)
def d29(t):t.assertEqual(build(),SHELL.read_bytes())
def d30(t):t.assertEqual(audit(run(EXAMPLE)).returncode,0)
def d31(t):t.assertEqual(audit(run(EXAMPLE),True).returncode,0)
def d32(t):t.assertEqual(decode_exact(1,BASES),(0,)*57)
def d33(t):
 with t.assertRaises(ValueError):decode_exact(BASES[0]**2,BASES)
def d34(t):
 with t.assertRaises(ValueError):decode_exact(281,BASES)
def d35(t):t.assertEqual(symbolic_log_product({5:1},{5:-1,7:1}),{7:1})
def d36(t):
 x=sample([],[])
 t.assertEqual(run(x)['combined_godel_integer'],1)
 t.assertEqual(audit(run(x)).returncode,0)

for i,fun in enumerate((d01,d02,d03,d04,d05,d06,d07,d08,d09,d10,d11,d12,
 d13,d14,d15,d16,d17,d18,d19,d20,d21,d22,d23,d24,d25,d26,d27,d28,
 d29,d30,d31,d32,d33,d34,d35,d36),1):
 setattr(G27Tests,f'test_{i:03}_base_{fun.__name__}',fun)

for i,d in enumerate(DOMAINS):
 def enter(t,i=i,d=d):
  x=run(sample([[d,'ENTER_RESEARCH']],[]))
  t.assertEqual(x['combined_godel_integer'],BASES[i])
  t.assertEqual(x['exact_formal_log_additions'],1)
 def reset(t,d=d):
  x=run(sample([[d,'ENTER_RESEARCH'],[d,'RESET']],[]))
  t.assertEqual(x['combined_godel_integer'],1)
  t.assertEqual(x['exact_formal_log_additions'],2)
 setattr(G27Tests,f'test_{37+i:03}_domain_{d}',enter)
 setattr(G27Tests,f'test_{51+i:03}_reset_{d}',reset)

for i,(d,j,_) in enumerate(TOPICS):
 def topic(t,i=i,d=d,j=j):
  x=run(sample([[d,'ENTER_RESEARCH']],[record(d,j,'id_'+str(i))]))
  t.assertEqual(x['combined_godel_integer'],BASES[DOMAINS.index(d)]*BASES[14+i])
  t.assertEqual(x['formal_log_terms'],2)
 setattr(G27Tests,f'test_{65+i:03}_topic_{d}_{j}',topic)

for i,flag in enumerate(FORBIDDEN):
 def denied(t,flag=flag):
  x=sample([],[]);x['permissions'][flag]=True
  t.assertTrue(blocked(x))
 setattr(G27Tests,f'test_{108+i:03}_forbidden_{flag}',denied)

for i,key in enumerate(('combined_godel_integer','g24_integer','evidence_topic_integer',
  'domain_state_bits','evidence_topic_bits','formal_log_coefficients',
  'production_deployed','orders_submitted')):
 def tamper(t,key=key):
  x=run(EXAMPLE)
  if key in ('combined_godel_integer','g24_integer','evidence_topic_integer'):
   x[key]+=1
  elif key in ('domain_state_bits','evidence_topic_bits'):
   x[key][0]=1-x[key][0]
  elif key=='formal_log_coefficients':
   x[key][0][1]=2
  elif key=='production_deployed':
   x[key]=True
  else:
   x[key]=1
  t.assertNotEqual(audit(x).returncode,0)
 setattr(G27Tests,f'test_{118+i:03}_report_tamper_{key}',tamper)

if __name__=='__main__':
 unittest.main(verbosity=2)
