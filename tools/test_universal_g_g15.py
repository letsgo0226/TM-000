#!/usr/bin/env python3
"""G15 no-exchange policy/strategy/holdout anti-lookahead regression checks."""
import copy
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'deployment'))
from G15_Godel_Signal_core import run
from G15_Godel_Policy_core import check, veto_proposal, INVARIANTS

PARENT='deployment/G14_trader42_principle_contract.json'
POLICY='deployment/G15_godel_trading_contract.json'
SCRIPT=ROOT/'deployment/Universal_G_G15_Godel_Plaintext_2KB.sh'
DAY=date(2026, 11, 10)


def prices(regime='positive', count=200):
    result=[10000.0]
    for i in range(count-1):
        if regime=='positive': move=.015 if i%7!=6 else -.002
        elif regime=='negative': move=-.015 if i%7!=6 else .002
        elif regime=='reversal': move=.015 if i < 139 else -.015
        elif regime=='steady': move=0
        elif regime=='alternating': move=.003 if i%2==0 else -.003
        else: raise AssertionError('wrong regime')
        result.append(result[-1]*(1+move))
    return result


def example(regime='positive',position='FLAT'):
    return {'source':'SYNTHETIC','mode':'paper','position':position,'prices':prices(regime)}


def state():
    value=dict.fromkeys(INVARIANTS,True)
    value.update(kill_active=False,pending_order=False,reconciled=True,
                 mode='paper',live_armed=False,cooldown_elapsed=True,
                 cost_stress_reviewed=True,realized_daily_loss_usdt='0',
                 daily_equity_loss_pct='0',current_base_btc='0',
                 desired_quote_usdt='10',sized_quote_usdt='9',
                 available_quote_usdt='100',total_quote_exposure_usdt='0',
                 synthetic_last_price='10000')
    return value


class G15Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        for item in (PARENT,POLICY):
            target=self.root/item
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/item,target)
        self.policy=json.loads((self.root/POLICY).read_text())

    def tearDown(self):self.temp.cleanup()

    def edit(self,filename,change):
        path=self.root/filename
        d=json.loads(path.read_text());change(d)
        path.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')

    def shell(self,x):
        return subprocess.run(['bash',str(SCRIPT)],input=json.dumps(x),
                              text=True,capture_output=True,timeout=10)

    def test_01_parent_pinned_no_order(self):
        report=check(self.root,DAY)
        self.assertEqual(report['policy'],'GODEL_PAPER_REVIEW_ONLY')
        self.assertEqual(report['actual_orders'],0)
        self.assertFalse(report['live_authorized'])

    def test_02_one_liner_is_plaintext_one_line(self):
        b=SCRIPT.read_bytes()
        self.assertLessEqual(len(b),2048)
        self.assertEqual(b.count(b'\n'),1)
        for s in (b'base64',b'zlib',b'eval(',b'exec(',b'http',b'Binance'):
            self.assertNotIn(s,b)

    def test_03_synthetic_positive_fixture_generates_only_paper_candidate(self):
        output=run(example())
        self.assertEqual(output['action'],'SIMULATED_BUY_ONLY')
        self.assertFalse(output['live_allowed'])
        self.assertFalse(output['profitability_proved'])
        self.assertEqual(output['actual_orders'],0)
        self.assertTrue(output['roundtrip'])

    def test_04_compact_matches_readable(self):
        for regime in ('positive','negative','reversal','steady','alternating'):
            for position in ('FLAT','LONG'):
                x=example(regime,position)
                proc=self.shell(x)
                self.assertEqual(proc.returncode,0,(regime,proc.stderr))
                self.assertEqual(json.loads(proc.stdout),run(x))

    def test_05_negative_regime_does_not_open_long(self):
        self.assertEqual(run(example('negative'))['action'],'HOLD')

    def test_06_long_with_bad_holdout_requests_only_paper_exit(self):
        self.assertEqual(run(example('reversal','LONG'))['action'],
                         'SIMULATED_SELL_ONLY')

    def test_07_out_of_sample_reversal_veto(self):
        outcome=run(example('reversal'))
        self.assertEqual(outcome['action'],'HOLD')
        self.assertLessEqual(outcome['heldout_net_bps'],0)

    def test_08_flat_prices_have_no_edge(self):
        self.assertEqual(run(example('steady'))['action'],'HOLD')

    def test_09_readable_is_deterministic(self):
        x=example()
        self.assertEqual(run(x),run(x))

    def test_10_no_sma_or_qtm_signal_inputs(self):
        a=example()
        b=copy.deepcopy(a)
        b['sma_signal']='SELL';b['qtm42_program']=55067263
        self.assertEqual(run(a),run(b))

    def test_11_paper_policy_can_veto_buy(self):
        self.assertEqual(veto_proposal(run(example()),state(),self.policy),
                         'SIMULATED_BUY_REVIEW_ONLY')

    def test_12_kill_overrides_buy(self):
        ctx=state();ctx['kill_active']=True
        self.assertEqual(veto_proposal(run(example()),ctx,self.policy),
                         'HALT_KILL_OR_UNKNOWN')

    def test_13_unreconciled_order_halts(self):
        ctx=state();ctx['pending_order']=True
        self.assertEqual(veto_proposal(run(example()),ctx,self.policy),
                         'HALT_ORDER_RECONCILIATION')

    def test_14_position_cap_vetoes(self):
        ctx=state();ctx['current_base_btc']='0.0009'
        self.assertEqual(veto_proposal(run(example()),ctx,self.policy),
                         'HOLD_DECREASE_ONLY_OR_EXPOSURE')

    def test_15_two_usdt_day_loss_halts(self):
        ctx=state();ctx['realized_daily_loss_usdt']='2'
        self.assertEqual(veto_proposal(run(example()),ctx,self.policy),
                         'HALT_LOSS_REVIEW')

    def test_16_one_percent_equity_day_loss_halts(self):
        ctx=state();ctx['daily_equity_loss_pct']='1'
        self.assertEqual(veto_proposal(run(example()),ctx,self.policy),
                         'HALT_LOSS_REVIEW')

    def test_17_cost_review_required(self):
        ctx=state();ctx['cost_stress_reviewed']=False
        self.assertEqual(veto_proposal(run(example()),ctx,self.policy),
                         'HOLD_COST_NOT_REVIEWED')

    def test_18_missing_invariant_holds(self):
        ctx=state();ctx['TMVerified']=False
        self.assertEqual(veto_proposal(run(example()),ctx,self.policy),
                         'HOLD_MISSING_INVARIANT')

    def test_19_missing_cooldown_holds(self):
        ctx=state();ctx['cooldown_elapsed']=False
        self.assertEqual(veto_proposal(run(example()),ctx,self.policy),'HOLD_COOLDOWN')

    def test_20_forged_live_certificate_halts(self):
        p=run(example());p['live_allowed']=True
        self.assertEqual(veto_proposal(p,state(),self.policy),'HALT_BAD_CERTIFICATE')

    def test_21_policy_expires(self):
        with self.assertRaises(ValueError):check(self.root,date(2027,5,10))

    def test_22_policy_future_dated_rejected(self):
        with self.assertRaises(ValueError):check(self.root,date(2026,11,9))


INVALIDS=[
 ('wrong_source',lambda x:x.update(source='LIVE')),
 ('live_mode',lambda x:x.update(mode='live')),
 ('no_position',lambda x:x.pop('position')),
 ('invalid_position',lambda x:x.update(position='SHORT')),
 ('missing_prices',lambda x:x.pop('prices')),
 ('prices_not_list',lambda x:x.update(prices='abc')),
 ('too_few_prices',lambda x:x.update(prices=x['prices'][:90])),
 ('too_many_prices',lambda x:x.update(prices=[100.0]*2001)),
 ('nan_price',lambda x:x['prices'].__setitem__(25,float('nan'))),
 ('inf_price',lambda x:x['prices'].__setitem__(10,float('inf'))),
 ('zero_price',lambda x:x['prices'].__setitem__(1,0)),
 ('negative_price',lambda x:x['prices'].__setitem__(10,-50)),
 ('shock_over_threshold',lambda x:x['prices'].__setitem__(30,x['prices'][29]*2)),
 ('boolean_price',lambda x:x['prices'].__setitem__(3,True)),
 ('text_price',lambda x:x['prices'].__setitem__(3,'12.34')),
]
for i,(name,mutation) in enumerate(INVALIDS,start=23):
    def test(self,mutation=mutation):
        x=example();mutation(x)
        with self.assertRaises((ValueError,KeyError,TypeError,OverflowError)):
            run(x)
        proc=self.shell(x)
        self.assertNotEqual(proc.returncode,0)
    setattr(G15Tests,f'test_{i:02d}_{name}',test)

MUTATIONS=[
 ('parent_policy_tamper',PARENT,lambda x:x['strategy'].update(fast_window=4)),
 ('incorrect_parent_pin',POLICY,lambda x:x.update(parent_git_blob_sha='0'*40)),
 ('wrong_master',POLICY,lambda x:x.update(master='TM-015')),
 ('trader_source_spoof',POLICY,lambda x:x.update(trader_repository='example/spoof')),
 ('forbid_sma_removed',POLICY,lambda x:x.update(signal_source='SMA')),
 ('G257_removed',POLICY,lambda x:x.update(encoding='HASH_ONLY')),
 ('live_armed',POLICY,lambda x:x.update(live_armed=True)),
 ('read_broker_API',POLICY,lambda x:x.update(broker_api=True)),
 ('read_market_API',POLICY,lambda x:x.update(market_api=True)),
 ('execute_upstream',POLICY,lambda x:x.update(exec_upstream_source=True)),
 ('order_submission',POLICY,lambda x:x.update(write_orders=True)),
 ('auto_deploy',POLICY,lambda x:x.update(auto_deploy=True)),
 ('false_alpha',POLICY,lambda x:x.update(independent_alpha_validation=True)),
 ('guaranteed_profit',POLICY,lambda x:x.update(guaranteed_profit=True)),
 ('train_split_changed',POLICY,lambda x:x.update(training_split_percent=100)),
 ('future_leak',POLICY,lambda x:x.update(train_only_model_fit=False)),
 ('holdout_reused',POLICY,lambda x:x.update(holdout_veto_only=False)),
 ('pattern_support_relaxed',POLICY,lambda x:x.update(minimum_pattern_support=1)),
 ('cost_zeroed',POLICY,lambda x:x.update(one_way_fee_slippage_stress_bps=0)),
 ('daily_loss_relaxed',POLICY,lambda x:x['risk_ceiling'].update(daily_realized_loss_review_usdt='3')),
 ('order_cap_relaxed',POLICY,lambda x:x['risk_ceiling'].update(max_order_quote_usdt='20')),
 ('base_exposure_relaxed',POLICY,lambda x:x['risk_ceiling'].update(max_base_exposure_btc='0.002')),
 ('cooldown_relaxed',POLICY,lambda x:x['risk_ceiling'].update(minimum_cooldown_seconds=0)),
 ('source_real_requested',POLICY,lambda x:x.update(synthetic_data_only=False)),
 ('missing_gate',POLICY,lambda x:x['invariants'].pop()),
]
for i,(name,filename,change) in enumerate(MUTATIONS,start=38):
    def test(self,filename=filename,change=change):
        self.edit(filename,change)
        with self.assertRaises((ValueError,TypeError,KeyError)):
            check(self.root,DAY)
    setattr(G15Tests,f'test_{i:02d}_{name}',test)

if __name__ == '__main__':
    unittest.main(verbosity=2)
