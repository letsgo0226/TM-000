#!/usr/bin/env python3
"""G28: bounded, deterministic, offline quality-diversity hypothesis explorer.

This program generates structured *untested* research hypotheses from a user-
provided finite grammar. It neither executes proposed experiments nor calls
models, networks, shell commands, trading, clinical, or deployment services.

The term 'freedom field' means exploration diversity within explicit budgets,
NOT infinite computation, model jailbreak, source authentication or evidence.
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
import re
import sys
from pathlib import Path

SCHEMA = 'G28-FREEDOM-FIELD/1'
AXES = ('domains', 'methods', 'measurements', 'falsifiers')
NO_ACTIONS = ('network', 'external_execution', 'autonomous_deployment',
              'live_trading', 'medical_action', 'human_override')
ID_RE = re.compile(r'[a-z][a-z0-9_]{1,39}\Z')
ALLOWED = {
    'domains': ('id', 'risk'),
    'methods': ('id', 'cost', 'testability'),
    'measurements': ('id', 'cost', 'observability'),
    'falsifiers': ('id', 'strength'),
}


def insist(condition, reason):
    if not condition:
        raise ValueError(reason)


def parse_request(obj):
    insist(type(obj) is dict and set(obj) == {'schema', 'mode', 'seed', 'budget',
            'beam_width', 'max_cost', 'max_risk', 'permissions', *AXES},
           'input schema mismatch')
    insist(obj['schema'] == SCHEMA and obj['mode'] == 'offline',
           'only offline research requests permitted')
    insist(type(obj['seed']) is int and 0 <= obj['seed'] < 2**32,
           'invalid deterministic seed')
    insist(type(obj['budget']) is int and 1 <= obj['budget'] <= 512,
           'finite budget must be 1..512')
    insist(type(obj['beam_width']) is int and 1 <= obj['beam_width'] <= 32,
           'beam width must be 1..32')
    insist(type(obj['max_cost']) is int and 0 <= obj['max_cost'] <= 12,
           'invalid cost threshold')
    insist(type(obj['max_risk']) is int and 0 <= obj['max_risk'] <= 3,
           'invalid risk threshold')
    permissions = obj['permissions']
    insist(type(permissions) is dict and set(permissions) == set(NO_ACTIONS)
           and all(permissions[k] is False for k in NO_ACTIONS),
           'no external operations are authorized')
    for axis in AXES:
        entries = obj[axis]
        insist(type(entries) is list and 1 <= len(entries) <= 8,
               'axis cardinality must be 1..8: ' + axis)
        identifiers = set()
        for e in entries:
            insist(type(e) is dict and set(e) == set(ALLOWED[axis]),
                   'invalid entry in ' + axis)
            identifier = e['id']
            insist(type(identifier) is str and ID_RE.fullmatch(identifier) is not None,
                   'invalid identifier in ' + axis)
            insist(identifier not in identifiers, 'duplicate identifier in ' + axis)
            identifiers.add(identifier)
            for k in ALLOWED[axis]:
                if k != 'id':
                    insist(type(e[k]) is int and 0 <= e[k] <= 4,
                           'scores must be exact integers in [0,4]')
    return obj


def candidate_ids(candidate):
    return tuple(item['id'] for item in candidate)


def proposed_cost(candidate):
    return candidate[1]['cost'] + candidate[2]['cost']


def cost_band(cost):
    return 'low' if cost <= 3 else ('medium' if cost <= 5 else 'high')


def descriptor(candidate):
    return (candidate[0]['id'], cost_band(proposed_cost(candidate)))


def surrogate_quality(candidate):
    """Only a synthetic metadata proxy, never predicted or actual efficacy."""
    return (candidate[1]['testability'] + candidate[2]['observability'] +
            candidate[3]['strength'] - proposed_cost(candidate) -
            candidate[0]['risk'])


def distance(a, b):
    return sum(x != y for x, y in zip(candidate_ids(a), candidate_ids(b)))


def novelty(candidate, archive):
    return min((distance(candidate, prev) for prev in archive.values()), default=4)


def proposal(candidate, score, novel):
    d, m, measure, f = candidate
    return {
        'hypothesis_id': ':'.join(candidate_ids(candidate)),
        'domain': d['id'],
        'method': m['id'],
        'measurement': measure['id'],
        'falsification_test': f['id'],
        'descriptor': list(descriptor(candidate)),
        'synthetic_priority': score,
        'novelty_at_selection': novel,
        'cost_units': proposed_cost(candidate),
        'risk_units': d['risk'],
        'status': 'UNTESTED_HYPOTHESIS',
        'observed_evidence': False,
        'scientific_claim_proved': False,
    }


def explore(request):
    r = parse_request(request)
    universe = [c for c in itertools.product(*(r[a] for a in AXES))
                if proposed_cost(c) <= r['max_cost'] and c[0]['risk'] <= r['max_risk']]
    insist(universe, 'no admissible hypotheses')
    # Never exceed the finite predeclared universe; no unbounded generations.
    n = min(r['budget'], len(universe))
    rng_guided = random.Random(r['seed'])
    guided_pool = list(universe)
    qd_archive = {}
    log = []
    lookahead = 0
    for step in range(n):
        beam = rng_guided.sample(guided_pool, k=min(r['beam_width'], len(guided_pool)))
        lookahead += len(beam)
        # Candidate features are declared, not evaluated experimentally.
        chosen = max(beam, key=lambda c: (int(descriptor(c) not in qd_archive),
                                          novelty(c, qd_archive), surrogate_quality(c),
                                          tuple(candidate_ids(c))))
        guided_pool.remove(chosen)
        score, novel, cell = surrogate_quality(chosen), novelty(chosen, qd_archive), descriptor(chosen)
        accepted = cell not in qd_archive or score > surrogate_quality(qd_archive[cell])
        if accepted:
            qd_archive[cell] = chosen
        log.append({'step': step + 1, 'id': ':'.join(candidate_ids(chosen)),
                    'cell': list(cell), 'synthetic_priority': score,
                    'novelty': novel, 'elite_updated': accepted})

    # Baseline is a randomized archive under the SAME proposal count, seed, and
    # descriptor. Comparisons concern metadata proxies, not true discoveries.
    rng_baseline = random.Random(r['seed'])
    baseline_pool = list(universe)
    rng_baseline.shuffle(baseline_pool)
    baseline_archive = {}
    for c in baseline_pool[:n]:
        cell = descriptor(c)
        if cell not in baseline_archive or surrogate_quality(c) > surrogate_quality(baseline_archive[cell]):
            baseline_archive[cell] = c

    elites = [proposal(c, surrogate_quality(c), novelty(c, {}))
              for _, c in sorted(qd_archive.items())]
    baseline_elites = [proposal(c, surrogate_quality(c), novelty(c, {}))
                       for _, c in sorted(baseline_archive.items())]
    # Exact trace data are retained. No hash is used or claimed as authentication.
    return {
        'version': 'G28', 'status': 'OFFLINE_UNTESTED_HYPOTHESES',
        'scope': 'FINITE_SYNTHETIC_QUALITY_DIVERSITY_SEARCH',
        'seed': r['seed'], 'budget_requested': r['budget'],
        'candidate_universe': len(universe), 'proposals_scored': n,
        'surrogate_lookahead_inspections': lookahead,
        'baseline_metadata_inspections': n,
        'quality_diversity_occupied_cells': len(qd_archive),
        'random_baseline_occupied_cells': len(baseline_archive),
        'quality_diversity_sum_synthetic_priority': sum(x['synthetic_priority'] for x in elites),
        'random_baseline_sum_synthetic_priority': sum(x['synthetic_priority'] for x in baseline_elites),
        'archive': elites, 'random_baseline_archive': baseline_elites,
        'audit_trace': log, 'sha_used': False,
        'predicted_real_world_outcomes': False,
        'actual_experiments_performed': 0,
        'evidence_independently_verified': False,
        'unbounded_computation_claimed': False,
        'platform_restrictions_bypassed': False,
        'deployment_performed': False,
        'live_orders_submitted': 0,
        'human_review_required': True,
    }


def main():
    parser = argparse.ArgumentParser(description='Offline G28 hypothesis diversity experiment')
    parser.add_argument('request', nargs='?', help='input JSON file; default stdin')
    args = parser.parse_args()
    try:
        if args.request:
            with Path(args.request).open(encoding='utf-8') as f:
                inp = json.load(f)
        else:
            inp = json.load(sys.stdin)
        print(json.dumps(explore(inp), sort_keys=True, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as err:
        print('BLOCKED: ' + str(err), file=sys.stderr)
        raise SystemExit(2)

if __name__ == '__main__':
    main()
