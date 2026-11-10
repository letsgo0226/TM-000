#!/usr/bin/env python3
"""G24: finite, offline, fail-closed cross-domain prime-power research ledger.

This is a governance *representation and event interpreter*, not a reality oracle,
clinical validator, peace optimizer, trading engine or autonomous deployer.
"""
import json
import sys
from pathlib import Path

DOMAINS = (
    'master_tm', 'deployment', 'computational_continuity', 'ai_continuity',
    'human_longevity', 'interspecies_welfare', 'ecology', 'peace', 'sdgs',
    'cultivated_meat', 'trader42', 'culture_music', 'spirituality', 'food_security',
)
PRIMES = (5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53)
PHASE = ('BLOCKED', 'RESEARCH_ONLY')
FORBIDDEN = ('network', 'auto_deploy', 'live_armed', 'order_submission',
             'exchange_access', 'external_execution', 'release',
             'clinical_action', 'regulatory_approval_claim', 'human_override')
REQUIREMENTS = {
    'master_tm': ('fixed-master-check', 'formal-machine-execution'),
    'deployment': ('sandbox-ci', 'human-approval', 'rollback-proof'),
    'computational_continuity': ('state-integrity', 'bounded-recovery'),
    'ai_continuity': ('data-rights', 'reproducible-state', 'consent'),
    'human_longevity': ('clinical-endpoints', 'ethics-review', 'regulatory-oversight'),
    'interspecies_welfare': ('welfare-baseline', 'sentience-uncertainty'),
    'ecology': ('independent-lca', 'baseline-and-attribution'),
    'peace': ('conflict-death-timeseries', 'justice-access', 'nonviolent-governance'),
    'sdgs': ('2.1.2', '12.3.1', '13.2.2', '16.1.2'),
    'cultivated_meat': ('cell-source-and-fbs', 'welfare', 'food-safety', 'jurisdiction-approval', 'independent-lca'),
    'trader42': ('paper-only', 'kill-switch', 'independent-holdout', 'cost-and-slippage'),
    'culture_music': ('original-lyrics', 'vocal-consent', 'rights-audit'),
    'spirituality': ('symbolic-not-physical-proof', 'consent', 'critical-rationality'),
    'food_security': ('food-safety', 'nutrition', 'affordability', 'accessibility'),
}
PARENT_EXPECTED = {
    'G23_prime_power_godel_contract.json': ('schema', 'G23-prime-power-godel-computational-tm/1'),
    'G22_bitwise_no_sha_contract.json': ('no_cryptographic_digest_functions', True),
    'G14_trader42_principle_contract.json': ('order_submission', False),
    'G13_peace_sdgs_cultivated_meat_contract.json': ('all_goals_achieved', False),
}

def require(condition, explanation):
    if not condition:
        raise ValueError(explanation)

def primes_state_roundtrip(value):
    require(type(value) is int and value >= 1, 'invalid ledger integer')
    remain = value
    result = []
    for prime in PRIMES:
        exponent = 0
        while remain % prime == 0:
            remain //= prime
            exponent += 1
            require(exponent <= 1, 'out-of-policy research exponent')
        result.append(exponent)
    require(remain == 1, 'unknown factor or external state')
    return tuple(result)

def update(value, domain, current, next_phase):
    require(domain in DOMAINS, 'unregistered domain')
    require(current in (0, 1) and next_phase in (0, 1), 'invalid phase')
    prime = PRIMES[DOMAINS.index(domain)]
    require(primes_state_roundtrip(value)[DOMAINS.index(domain)] == current,
            'ledger drift at transition')
    if next_phase > current:
        value *= prime
    elif next_phase < current:
        require(value % prime == 0, 'non-exact division')
        value //= prime
    return value

def run(request):
    require(type(request) is dict, 'JSON object required')
    require(set(request) == {'source', 'mode', 'permissions', 'events'}, 'invalid top-level schema')
    require(request['source'] == 'SYNTHETIC' and request['mode'] == 'offline',
            'only synthetic offline research permitted')
    flags = request['permissions']
    require(type(flags) is dict and set(flags) == set(FORBIDDEN), 'invalid permissions schema')
    require(all(flags[name] is False for name in FORBIDDEN), 'external action capability blocked')
    events = request['events']
    require(type(events) is list and len(events) <= 56, 'event budget exceeded')
    value = 1
    phases = [0] * len(DOMAINS)
    for event in events:
        require(type(event) is list and len(event) == 2, 'invalid event')
        name, action = event
        require(type(name) is str and name in DOMAINS, 'unknown domain')
        require(action in ('ENTER_RESEARCH', 'RESET'), 'unknown transition')
        j = DOMAINS.index(name)
        next_phase = 1 if action == 'ENTER_RESEARCH' else 0
        require(phases[j] != next_phase, 'redundant/uncertified transition')
        value = update(value, name, phases[j], next_phase)
        phases[j] = next_phase
    decoded = primes_state_roundtrip(value)
    require(decoded == tuple(phases), 'prime-power integer / state mismatch')
    return {
        'version': 'G24',
        'status': 'OFFLINE_CROSS_DOMAIN_RESEARCH_ONLY',
        'prime_power_integer': value,
        'prime_factors': [[p, e] for p, e in zip(PRIMES, decoded) if e],
        'domain_phases': {k: PHASE[v] for k, v in zip(DOMAINS, decoded)},
        'domains': len(DOMAINS), 'events_replayed': len(events),
        'full_numeric_roundtrip': True, 'digest_used': False,
        'external_data_authenticated': False, 'independent_impact_verified': False,
        'machine_universality_proved': False, 'all_dimensions_immortality_proved': False,
        'world_peace_achieved': False, 'all_sdgs_achieved': False,
        'cultivated_meat_safe_or_cruelty_free_proved': False,
        'trader42_alpha_validated': False, 'orders_submitted': 0,
        'deployment_executed': False, 'human_review_required': True,
    }

def verify_parents(root):
    """Local structured compatibility check, NOT publisher or Git authenticity proof."""
    checked = {}
    for name, (key, value) in PARENT_EXPECTED.items():
        doc = json.loads((Path(root) / name).read_text(encoding='utf-8'))
        require(doc.get(key) == value, 'upstream research contract changed: ' + name)
        checked[name] = True
    g23 = json.loads((Path(root) / 'G23_prime_power_godel_contract.json').read_text(encoding='utf-8'))
    g22 = json.loads((Path(root) / 'G22_bitwise_no_sha_contract.json').read_text(encoding='utf-8'))
    g14 = json.loads((Path(root) / 'G14_trader42_principle_contract.json').read_text(encoding='utf-8'))
    require(g23['master'] == g14['master'] == 'UTM-PLEIADES-v0.2-PTCA', 'master changed')
    require(g22['transition_rules'] == g23['transitions'] == 1140, 'source TM mismatch')
    require(g14['trader_mode'] == 'paper' and g14['live_armed'] is False, 'trading armed')
    require(len(DOMAINS) == len(PRIMES) == len(REQUIREMENTS), 'domain registry inconsistent')
    return {'version':'G24', 'status':'PARENT_METADATA_COMPATIBLE_NOT_AUTHENTICATED',
            'contracts_checked':len(checked), 'source_authenticity_proved':False,
            'trading_live_allowed':False, 'deployment_allowed':False}

if __name__ == '__main__':
    try:
        if len(sys.argv) == 2 and sys.argv[1] == '--check-parent':
            print(json.dumps(verify_parents(Path(__file__).resolve().parent), sort_keys=True))
        elif len(sys.argv) == 1:
            print(json.dumps(run(json.load(sys.stdin)), sort_keys=True))
        else:
            raise ValueError('usage: < request.json | --check-parent')
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as ex:
        print('BLOCKED: ' + str(ex), file=sys.stderr)
        sys.exit(1)
