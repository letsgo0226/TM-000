#!/usr/bin/env python3
"""G28-EQ: 60 offline regression, accounting, fair-budget and tamper tests."""
from __future__ import annotations
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEP = ROOT/'deployment'
sys.path.insert(0, str(DEP))
from G28_Computational_Freedom_Field import explore
from G28_Equal_Cost_Benchmark import (
    VERSION, universe_for, run_arm, benchmark, paired_ci, DEFAULT_CREDITS,
    FIXED_COSTS, step_archive, descriptor, surrogate_quality,
)

REQUEST = json.loads((DEP/'G28_example_request.json').read_text())
REFERENCE = json.loads((DEP/'G28_equal_cost_expected_summary.json').read_text())


class EqualCostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.universe = universe_for(REQUEST)
        cls.report = benchmark(REQUEST)

    def test_01_version(self):
        self.assertEqual(self.report['version'], VERSION)
    def test_02_historical_g28_unchanged(self):
        old = explore(REQUEST)
        self.assertEqual((old['quality_diversity_occupied_cells'],
                          old['random_baseline_occupied_cells']), (12,9))
    def test_03_universe_size(self):
        self.assertEqual(len(self.universe), 256)
    def test_04_all_comparisons_present(self):
        self.assertEqual(self.report['comparison_count'], 360)
    def test_05_all_seed_ids_present(self):
        self.assertEqual(self.report['seed_design'], list(range(30)))
    def test_06_12_scenarios(self):
        self.assertEqual(len(self.report['summary']),12)
    def test_07_full_report_deterministic(self):
        self.assertEqual({'version':self.report['version'],
                          'comparison_count':self.report['comparison_count'],
                          'mean_coverage_by_case':[[x['validation_cost'],x['credit_cap'],
                          x['mean_occupied_cells_guided'],x['mean_occupied_cells_random'],
                          x['mean_difference_guided_minus_random']]
                          for x in self.report['summary']]}, REFERENCE)
    def test_08_data_are_synthetic(self):
        self.assertTrue(self.report['metadata_quality_is_a_synthetic_proxy'])
        self.assertFalse(self.report['external_scientific_evidence_tested'])
    def test_09_no_real_world_claim(self):
        self.assertFalse(self.report['real_world_acceleration_proved'])
    def test_10_no_wall_clock_equalization_claim(self):
        self.assertFalse(self.report['runtime_equalized'])
        self.assertFalse(self.report['algorithm_overheads_equalized'])
    def test_11_common_universe_cost_excluded(self):
        self.assertTrue(self.report['common_universe_generation_cost_not_charged'])
    def test_12_cost_model_sensitivity(self):
        a={ (x['validation_cost'],x['credit_cap']):x for x in self.report['summary'] }
        self.assertLess(a[(1,32)]['mean_difference_guided_minus_random'],0)
        self.assertGreater(a[(16,256)]['mean_difference_guided_minus_random'],0)
    def test_13_fair_cap_each_row(self):
        for x in self.report['rows']:
            self.assertLessEqual(x['guided_spent'],x['credit_cap'])
            self.assertLessEqual(x['random_spent'],x['credit_cap'])
    def test_14_cost_ledger_each_row(self):
        for x in self.report['rows']:
            v=x['validation_cost'];s=x['screen_cost']
            self.assertEqual(x['guided_spent'],x['guided_screenings']*s+x['guided_validations']*v)
            self.assertEqual(x['random_spent'],x['random_screenings']*s+x['random_validations']*v)
    def test_15_baseline_screen_equals_validation(self):
        self.assertTrue(all(x['random_screenings']==x['random_validations'] for x in self.report['rows']))
    def test_16_guided_screen_at_least_validation(self):
        self.assertTrue(all(x['guided_screenings']>=x['guided_validations'] for x in self.report['rows']))
    def test_17_paired_results_all_have_30_repeats(self):
        self.assertTrue(all(x['paired_seeds']==30 for x in self.report['summary']))
    def test_18_win_loss_counts_30(self):
        self.assertTrue(all(sum(x['wins_ties_losses_guided'])==30 for x in self.report['summary']))
    def test_19_bootstrap_interval_ordered(self):
        for s in self.report['summary']:
            lo,hi=s['paired_bootstrap_95pct_difference_interval']
            self.assertLessEqual(lo,hi)
    def test_20_bootstrap_deterministic(self):
        self.assertEqual(paired_ci([0,0,1,-1],17),paired_ci([0,0,1,-1],17))
    def test_21_archive_has_at_most_12_cells(self):
        for method in ('guided','random'):
            arm=run_arm(self.universe,method=method,seed=28,total_credits=512)
            self.assertLessEqual(arm['occupied_cells'],12)
            self.assertEqual(arm['occupied_cells'],len(arm['archive']))
    def test_22_all_selected_ids_unique(self):
        for method in ('guided','random'):
            arm=run_arm(self.universe,method=method,seed=28,total_credits=128)
            ids=[i['candidate'] for i in arm['trace']]
            self.assertEqual(len(ids),len(set(ids)))

# Validate scenario accounting and measurement across all 3 cost models x 4 caps.
for i,(validation_cost,credits) in enumerate((v,c) for v in FIXED_COSTS for c in DEFAULT_CREDITS):
    def case(self,validation_cost=validation_cost,credits=credits):
        scenario=next(s for s in self.report['summary'] if s['credit_cap']==credits
                      and s['validation_cost']==validation_cost)
        self.assertEqual(scenario['screen_cost'],1)
        self.assertTrue(-12<=scenario['mean_difference_guided_minus_random']<=12)
        self.assertLessEqual(scenario['mean_validations_guided'],credits/(1+validation_cost))
        self.assertLessEqual(scenario['mean_validations_random'],credits/(1+validation_cost))
    setattr(EqualCostTests,f'test_{23+i:02d}_scenario_cost_{validation_cost}_budget_{credits}',case)

# Paired deterministic replay across 14 independent seeds.
for i in range(14):
    def replay(self,i=i):
        for method in ('guided','random'):
            first=run_arm(self.universe,method=method,seed=i,total_credits=97,validation_cost=4)
            second=run_arm(self.universe,method=method,seed=i,total_credits=97,validation_cost=4)
            self.assertEqual(first,second)
            self.assertEqual(sum(z['charged_credits'] for z in first['trace']),first['credits_spent'])
    setattr(EqualCostTests,f'test_{35+i:02d}_replay_seed_{i}',replay)

# Twelve fail-closed invalid parameters (no hidden bool or negative budgets).
INVALID=[
 {'total_credits':0}, {'total_credits':100001},
 {'screen_cost':0}, {'screen_cost':1001},
 {'validation_cost':0}, {'validation_cost':1001},
 {'seed':-1}, {'seed':2**32},
 {'beam_width':0}, {'beam_width':33},
 {'total_credits':False}, {'validation_cost':True},
]
for i,override in enumerate(INVALID):
    def invalid(self,override=override):
        inp=dict(method='guided',seed=28,total_credits=128,
                 screen_cost=1,validation_cost=4,beam_width=8)
        inp.update(override)
        with self.assertRaises(ValueError):run_arm(self.universe,**inp)
    setattr(EqualCostTests,f'test_{49+i:02d}_invalid_parameter_{i}',invalid)

if __name__=='__main__':unittest.main(verbosity=2)
