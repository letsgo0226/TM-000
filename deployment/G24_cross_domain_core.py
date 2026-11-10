#!/usr/bin/env python3
"""G24 offline twelve-domain prime-power review ledger. ZERO effect authority.

Real big-integer prime-power multiplication updates each domain register.
Integer factorization checks every register; the full state/head Gödel
configuration is also materialized and decoded. This is a finite registry
interpreter, not an implementation of real-world outcomes or a universal TM.
"""
import json
import sys

DOMAINS = (
    'universal_tm', 'automated_deployment', 'ai_continuity',
    'human_longevity', 'interspecies_welfare', 'ecological_continuity',
    'global_peace', 'sdgs', 'cultivated_meat', 'psychosocial',
    'philosophical', 'trader42',
)
FLAGS = ('network', 'deployment', 'trading', 'credentials', 'external_action')
KEYS = frozenset(('source', 'mode', 'human_review', 'domains') + FLAGS)
STATE_NAMES = {1: 'EVIDENCE_GAP', 2: 'SYNTHETIC_REVIEW_ONLY', 3: 'VETOED'}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def first_primes(count):
    require(type(count) is int and 1 <= count <= 32, 'prime budget')
    out, number = [], 2
    while len(out) < count:
        if all(number % p for p in out if p*p <= number):
            out.append(number)
        number += 1
    return out

PRIMES = first_primes(len(DOMAINS) + 2)

def valuation(value, prime):
    require(type(value) is int and value >= 1 and prime in PRIMES, 'bad integer/prime')
    count = 0
    while value % prime == 0:
        value //= prime
        count += 1
    return count

def prime_transition(value, prime, old, new):
    """Perform actual exact integer multiplication or division, with invariants."""
    require(prime in PRIMES[2:], 'reserved prime')
    require(type(old) is int and type(new) is int and 0 <= old <= 3 and 0 <= new <= 3, 'invalid state')
    require((old, new) in ((0, 1), (1, 1), (1, 2), (1, 3)), 'unauthorized transition')
    require(valuation(value, prime) == old, 'old state differs from prime valuation')
    delta = new - old
    if delta >= 0:
        return value * prime**delta
    divisor = prime**(-delta)
    require(value % divisor == 0, 'inexact prime division')
    return value // divisor

def decode_register(value):
    """Independent full division by each indexed prime; no state cache used."""
    require(type(value) is int and value > 0 and value % 2 and value % 3, 'invalid register integer')
    rem, states = value, []
    for prime in PRIMES[2:]:
        exponent = 0
        while rem % prime == 0:
            rem //= prime
            exponent += 1
            require(exponent <= 3, 'unknown register exponent')
        states.append(exponent)
    require(rem == 1, 'unknown prime factor in register')
    return states

def encode_configuration(control_state, head, register):
    require(type(control_state) is int and 0 <= control_state <= 2, 'control state')
    require(type(head) is int and 0 <= head <= len(DOMAINS), 'head index')
    require(type(register) is int and register > 0 and register % 2 and register % 3, 'bad register')
    return (2**(control_state + 1)) * (3**(head + 1)) * register

def decode_configuration(number):
    q = valuation(number, 2) - 1
    h = valuation(number, 3) - 1
    require(0 <= q <= 2 and 0 <= h <= len(DOMAINS), 'unrecognized encoded q/head')
    reg = number // (2**(q+1) * 3**(h+1))
    return q, h, decode_register(reg)

def validate_input(req):
    require(type(req) is dict and set(req) == KEYS, 'unknown/missing root field')
    require(req['source'] == 'SYNTHETIC' and req['mode'] == 'offline', 'real-world input denied')
    require(req['human_review'] is True, 'human review is mandatory')
    require(all(req[key] is False for key in FLAGS), 'external authority is forbidden')
    data = req['domains']
    require(type(data) is dict and set(data) == set(DOMAINS), 'exact domain coverage required')
    for name in DOMAINS:
        entry = data[name]
        require(type(entry) is list and len(entry) == 2, 'domain format')
        checks, veto = entry
        require(type(checks) is int and 0 <= checks <= 100 and type(veto) is bool, 'invalid synthetic checks/veto')
    return data

def run(req):
    data = validate_input(req)
    godel = 1
    states = []
    changes = 0
    events = []
    for index, name in enumerate(DOMAINS):
        prime = PRIMES[index+2]
        checks, veto = data[name]
        godel = prime_transition(godel, prime, 0, 1)
        changes += 1
        new = 3 if veto else 2 if checks >= 3 else 1
        if new != 1:
            godel = prime_transition(godel, prime, 1, new)
            changes += 1
        states.append(new)
        events.append({'domain': name, 'state': STATE_NAMES[new],
                       'synthetic_checks': checks, 'veto': veto})
    independently_decoded = decode_register(godel)
    require(independently_decoded == states, 'prime-power register roundtrip differs')
    full_configuration = encode_configuration(2, len(DOMAINS), godel)
    require(decode_configuration(full_configuration) == (2, len(DOMAINS), states), 'configuration roundtrip differs')
    return {
        'version': 'G24', 'status': 'CROSS_DOMAIN_SYNTHETIC_REVIEW_ONLY',
        'parent': 'G23_PRIME_POWER_TM', 'master': 'UTM-PLEIADES-v0.2-PTCA',
        'domains': events, 'domain_count': len(DOMAINS),
        'registered': len(DOMAINS), 'synthetic_reviewed': states.count(2),
        'evidence_gaps': states.count(1), 'vetoed': states.count(3),
        'prime_power_integer_bits': godel.bit_length(),
        'configuration_integer_bits': full_configuration.bit_length(),
        'prime_power_transition_count': changes,
        'exact_numeric_roundtrip': True, 'configuration_roundtrip': True,
        'approved_external_actions': 0, 'network_calls': 0,
        'deployment_allowed': False, 'trading_allowed': False,
        'real_world_outcomes_proved': False, 'all_dimensions_immortality_proved': False,
        'source_authenticity_proved': False, 'sha_used': False,
    }

def cli():
    try:
        raw = sys.stdin.buffer.read(16385)
        require(0 < len(raw) <= 16384, 'input byte limit')
        result = run(json.loads(raw))
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print('BLOCKED: ' + str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(',', ':')))
    return 0

if __name__ == '__main__':
    raise SystemExit(cli())
