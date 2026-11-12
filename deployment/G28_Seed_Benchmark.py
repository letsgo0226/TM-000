#!/usr/bin/env python3
"""Optional synthetic quality-diversity vs seeded random baseline study.

Both methods score an equal count of proposed hypotheses. G28 inspects more
metadata lookahead candidates; this is disclosed and means equal wall-clock
computation has NOT been demonstrated.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
from statistics import mean
from G28_Computational_Freedom_Field import explore

HERE = Path(__file__).resolve().parent


def benchmark(req, budgets=(16,24,64), seeds=range(30)):
    rows=[]
    for budget in budgets:
        for seed in seeds:
            case=copy.deepcopy(req)
            case.update(budget=budget,seed=seed)
            result=explore(case)
            rows.append(dict(budget=budget,seed=seed,
                diversity_cells=result['quality_diversity_occupied_cells'],
                random_cells=result['random_baseline_occupied_cells'],
                diversity_proxy=result['quality_diversity_sum_synthetic_priority'],
                random_proxy=result['random_baseline_sum_synthetic_priority'],
                diversity_metadata_lookaheads=result['surrogate_lookahead_inspections'],
                random_metadata_lookaheads=result['baseline_metadata_inspections']))
    summary=[]
    for budget in budgets:
        subset=[r for r in rows if r['budget']==budget]
        summary.append(dict(budget=budget,replicates=len(subset),
            mean_diversity_occupied_cells=round(mean(x['diversity_cells'] for x in subset),3),
            mean_random_occupied_cells=round(mean(x['random_cells'] for x in subset),3),
            mean_diversity_proxy=round(mean(x['diversity_proxy'] for x in subset),3),
            mean_random_proxy=round(mean(x['random_proxy'] for x in subset),3),
            mean_guided_lookahead=round(mean(x['diversity_metadata_lookaheads'] for x in subset),3),
            mean_random_lookahead=round(mean(x['random_metadata_lookaheads'] for x in subset),3)))
    return dict(version='G28_BENCHMARK',kind='SYNTHETIC_HEURISTIC_ONLY',
                candidate_universe=256,seed_range=[min(seeds),max(seeds)],
                independent_real_world_impact_measured=False,
                equal_compute_claimed=False,summary=summary,rows=rows)

if __name__=='__main__':
    request=json.loads((HERE/'G28_example_request.json').read_text())
    b=benchmark(request)
    (HERE/'G28_seed_benchmark_report.json').write_text(json.dumps(b,indent=2)+'\n')
    for row in b['summary']:
        print(row)
