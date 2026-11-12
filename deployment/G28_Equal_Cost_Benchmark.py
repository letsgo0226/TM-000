#!/usr/bin/env python3
"""G28-EQ: paired, equal-ledger-cost, offline quality-diversity benchmark.

Counts synthetic metadata inspections and candidate validations explicitly.
This is NOT equal hardware time or real-world scientific discovery. The finite
universe is constructed for both methods and that common work is not charged.
A guided screen reveals synthetic quality; this is an explicit modeling choice.
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
import statistics
import sys
from pathlib import Path

from G28_Computational_Freedom_Field import (
    AXES, parse_request, proposed_cost, descriptor, novelty,
    surrogate_quality, candidate_ids,
)

VERSION = 'G28_EQ/1'
FIXED_COSTS = (1, 4, 16)
DEFAULT_CREDITS = (32, 64, 128, 256)
BOOTSTRAP_REPS = 1000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def universe_for(request):
    r = parse_request(request)
    universe = [c for c in itertools.product(*(r[axis] for axis in AXES))
                if proposed_cost(c) <= r['max_cost'] and c[0]['risk'] <= r['max_risk']]
    require(len(universe) > 0, 'empty admissible hypothesis universe')
    return universe


def step_archive(archive, candidate):
    cell = descriptor(candidate)
    if cell not in archive or surrogate_quality(candidate) > surrogate_quality(archive[cell]):
        archive[cell] = candidate


def run_arm(universe, *, method, seed, total_credits, screen_cost=1,
            validation_cost=1, beam_width=8):
    """Account for every inspection and every chosen validation, no overspending.

    Each guided round pays to inspect every beam member even if it is not
    validated. Random pays to inspect + validate each sampled candidate.
    Previously inspected guided members are charged again if rescreened.
    """
    require(method in ('guided', 'random'), 'unsupported arm')
    for name, value in (('seed', seed), ('total_credits', total_credits),
                        ('screen_cost', screen_cost), ('validation_cost', validation_cost),
                        ('beam_width', beam_width)):
        require(type(value) is int, 'invalid integer parameter: ' + name)
    require(0 <= seed < 2**32 and 1 <= total_credits <= 100_000 and
            1 <= screen_cost <= 1000 and 1 <= validation_cost <= 1000 and
            1 <= beam_width <= 32, 'benchmark parameter outside bounds')
    require(len(universe) <= 4096, 'unbounded input universe')
    rng = random.Random(seed)
    pool = list(universe)
    archive = {}
    spent = validations = screened = 0
    trace = []
    if method == 'random':
        rng.shuffle(pool)
    while pool:
        remainder = total_credits - spent
        if remainder < screen_cost + validation_cost:
            break
        if method == 'guided':
            width = min(beam_width, len(pool),
                        (remainder - validation_cost) // screen_cost)
            require(width >= 1, 'internal credit accounting failure')
            beam = rng.sample(pool, k=width)
            # Mirroring G28 quality-diversity criterion on the evaluated archive.
            chosen = max(beam, key=lambda c: (
                int(descriptor(c) not in archive), novelty(c, archive),
                surrogate_quality(c), candidate_ids(c)))
            charge = width * screen_cost + validation_cost
            screened += width
        else:
            chosen = pool[-1]
            charge = screen_cost + validation_cost
            screened += 1
        pool.remove(chosen)
        spent += charge
        validations += 1
        step_archive(archive, chosen)
        trace.append({'candidate': ':'.join(candidate_ids(chosen)),
                      'screened_this_round': (width if method == 'guided' else 1),
                      'charged_credits': charge, 'remaining_credits': total_credits - spent})
    require(spent == screened * screen_cost + validations * validation_cost,
            'non-reproducible ledger')
    require(spent <= total_credits and validations <= len(universe), 'budget violation')
    scores = [surrogate_quality(c) for c in archive.values()]
    return {
        'method': method, 'total_credits_cap': total_credits,
        'credits_spent': spent, 'unused_credits': total_credits - spent,
        'metadata_screenings': screened, 'validated_candidates': validations,
        'occupied_cells': len(archive),
        'sum_synthetic_priority': sum(scores),
        'mean_priority_per_occupied_cell': (sum(scores) / len(scores) if scores else None),
        'archive': [{'cell': list(k), 'candidate': ':'.join(candidate_ids(c)),
                     'synthetic_priority': surrogate_quality(c)}
                    for k, c in sorted(archive.items())],
        'trace': trace,
    }


def paired_ci(differences, seed, repetitions=BOOTSTRAP_REPS):
    require(differences and 100 <= repetitions <= 5000, 'invalid bootstrap sample')
    rng = random.Random(900000 + seed)
    n = len(differences)
    means = []
    for _ in range(repetitions):
        means.append(sum(differences[rng.randrange(n)] for __ in range(n)) / n)
    means.sort()
    return [round(means[int(0.025 * repetitions)], 4),
            round(means[int(0.975 * repetitions)], 4)]


def benchmark(request, *, seeds=range(30), credits=DEFAULT_CREDITS,
              validation_costs=FIXED_COSTS, screen_cost=1, bootstrap_reps=BOOTSTRAP_REPS):
    universe = universe_for(request)
    beam = request['beam_width']
    seeds = tuple(seeds)
    credits = tuple(credits)
    validation_costs = tuple(validation_costs)
    require(5 <= len(seeds) <= 100 and len(set(seeds)) == len(seeds) and
            all(type(s) is int and 0 <= s < 2**32 for s in seeds), 'invalid seed design')
    require(1 <= len(credits) <= 10 and all(type(c) is int and 1 <= c <= 100_000 for c in credits),
            'invalid credit budgets')
    require(1 <= len(validation_costs) <= 10 and all(type(c) is int and 1 <= c <= 1000 for c in validation_costs),
            'invalid validation costs')
    require(type(screen_cost) is int and 1 <= screen_cost <= 1000, 'invalid screen cost')
    rows = []
    summary = []
    for validation_cost in validation_costs:
        for budget in credits:
            differences = []
            proxy_differences = []
            for seed in seeds:
                g = run_arm(universe, method='guided', seed=seed, total_credits=budget,
                            screen_cost=screen_cost, validation_cost=validation_cost, beam_width=beam)
                r = run_arm(universe, method='random', seed=seed, total_credits=budget,
                            screen_cost=screen_cost, validation_cost=validation_cost, beam_width=beam)
                difference = g['occupied_cells'] - r['occupied_cells']
                proxy_difference = g['sum_synthetic_priority'] - r['sum_synthetic_priority']
                differences.append(difference)
                proxy_differences.append(proxy_difference)
                rows.append({
                    'seed': seed, 'credit_cap': budget, 'screen_cost': screen_cost,
                    'validation_cost': validation_cost,
                    'guided_cells': g['occupied_cells'], 'random_cells': r['occupied_cells'],
                    'guided_proxy': g['sum_synthetic_priority'], 'random_proxy': r['sum_synthetic_priority'],
                    'guided_screenings': g['metadata_screenings'], 'random_screenings': r['metadata_screenings'],
                    'guided_validations': g['validated_candidates'], 'random_validations': r['validated_candidates'],
                    'guided_spent': g['credits_spent'], 'random_spent': r['credits_spent'],
                    'cells_guided_minus_random': difference,
                    'proxy_guided_minus_random': proxy_difference,
                })
            summary.append({
                'credit_cap': budget, 'screen_cost': screen_cost,
                'validation_cost': validation_cost, 'paired_seeds': len(seeds),
                'mean_occupied_cells_guided': round(statistics.mean(x['guided_cells'] for x in rows[-len(seeds):]), 4),
                'mean_occupied_cells_random': round(statistics.mean(x['random_cells'] for x in rows[-len(seeds):]), 4),
                'mean_difference_guided_minus_random': round(statistics.mean(differences), 4),
                'paired_bootstrap_95pct_difference_interval': paired_ci(differences, budget + validation_cost,
                                                                        bootstrap_reps),
                'wins_ties_losses_guided': [sum(d > 0 for d in differences), sum(d == 0 for d in differences),
                                            sum(d < 0 for d in differences)],
                'mean_proxy_guided_minus_random': round(statistics.mean(proxy_differences), 4),
                'mean_validations_guided': round(statistics.mean(x['guided_validations'] for x in rows[-len(seeds):]), 4),
                'mean_validations_random': round(statistics.mean(x['random_validations'] for x in rows[-len(seeds):]), 4),
                'mean_credits_spent_guided': round(statistics.mean(x['guided_spent'] for x in rows[-len(seeds):]), 4),
                'mean_credits_spent_random': round(statistics.mean(x['random_spent'] for x in rows[-len(seeds):]), 4),
            })
    return {
        'version': VERSION, 'status': 'SYNTHETIC_ACCOUNTED_COST_ONLY',
        'seed_design': list(seeds), 'candidate_universe': len(universe),
        'screen_cost_model': screen_cost, 'validation_cost_models': list(validation_costs),
        'credit_caps': list(credits), 'common_universe_generation_cost_not_charged': True,
        'runtime_equalized': False, 'algorithm_overheads_equalized': False,
        'lookahead_screenings_included': True, 'metadata_quality_is_a_synthetic_proxy': True,
        'external_scientific_evidence_tested': False, 'real_world_acceleration_proved': False,
        'autonomous_deployment': False, 'live_trades': 0,
        'confidence_interval_method': 'paired nonparametric bootstrap over seeds; descriptive only',
        'bootstrap_replicates': bootstrap_reps,
        'comparison_count': len(rows), 'summary': summary, 'rows': rows,
    }


def main():
    parser = argparse.ArgumentParser(description='Offline equal-cost proxy benchmark for G28')
    parser.add_argument('request', type=Path)
    parser.add_argument('--output', type=Path, help='JSON report path; default stdout')
    args = parser.parse_args()
    try:
        req = json.loads(args.request.read_text(encoding='utf-8'))
        result = benchmark(req)
        out = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
        if args.output:
            args.output.write_text(out, encoding='utf-8')
        else:
            print(out, end='')
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print('BLOCKED: ' + str(exc), file=sys.stderr)
        raise SystemExit(2)


if __name__ == '__main__':
    main()
