#!/usr/bin/env python3
"""G27 exact formal-log bridge between G26 math and G24/G25 synthetic research.

This is NOT an external evidence verifier, deployment system, trading system,
medical intervention, universal machine, or an assessment of actual SDG results.
The 14 domain bits and 43 topic coverage bits occupy DISJOINT primes.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from G24_Cross_Domain_Godel_Core import DOMAINS, PRIMES as G24_PRIMES, FORBIDDEN, run as run_g24
from G25_Evidence_Core import REQUIREMENTS, run as run_g25
from G23_Prime_Power_TM_core import first_primes, exponent_at
from G26_Exact_Log_TM_Core import symbolic_log_product

TOPICS = tuple((domain, j, topic) for domain in DOMAINS
               for j, topic in enumerate(REQUIREMENTS[domain]))
BASES = tuple(first_primes(2 + len(DOMAINS) + len(TOPICS))[2:])
if len(DOMAINS) != 14 or len(TOPICS) != 43 or BASES[:14] != tuple(G24_PRIMES):
    raise RuntimeError('upstream domain/prime registry drift')
STATUS = 'SYNTHETIC_METADATA_UNVERIFIED'


def require(v, msg):
    if not v:
        raise ValueError(msg)


def decode_exact(value, primes):
    """Actual full integer factorization; all legal exponents are 0 or 1."""
    require(type(value) is int and value >= 1, 'bad Godel integer')
    residue = value
    exponents = []
    for p in primes:
        exponent = 0
        while residue % p == 0:
            residue //= p
            exponent += 1
            require(exponent <= 1, 'duplicate prime power')
        exponents.append(exponent)
    require(residue == 1, 'unexpected prime factor')
    return tuple(exponents)


def run(packet):
    require(type(packet) is dict and set(packet) == {
        'source', 'mode', 'permissions', 'as_of', 'events', 'evidence',
    }, 'invalid G27 request schema')
    require(packet['source'] == 'SYNTHETIC' and packet['mode'] == 'offline',
            'only synthetic offline requests accepted')
    require(type(packet['permissions']) is dict and set(packet['permissions']) == set(FORBIDDEN)
            and all(x is False for x in packet['permissions'].values()),
            'all external capabilities must be false')
    # Deliberate delegation to historical G24 and G25 application validators.
    g24 = run_g24({k: packet[k] for k in ('source', 'mode', 'permissions', 'events')})
    g25 = run_g25({k: packet[k] for k in ('source', 'mode', 'permissions', 'as_of', 'evidence')})
    require(g24['status'] == 'OFFLINE_CROSS_DOMAIN_RESEARCH_ONLY', 'G24 policy changed')
    require(g25['status'] == 'EVIDENCE_METADATA_REVIEW_ONLY', 'G25 review policy changed')
    require(g25['authenticated'] is False and g25['review_verified'] is False,
            'G25 unexpectedly claimed independent authentication')

    domain_state = tuple(int(g24['domain_phases'][d] == 'RESEARCH_ONLY') for d in DOMAINS)
    covered = {(d, j) for d, js in g25['topics'].items() for j in js}
    require(all(domain_state[DOMAINS.index(d)] == 1 for d, _ in covered),
            'evidence received outside research-only domain')
    topic_state = tuple(int((d, j) in covered) for d, j, _ in TOPICS)

    integer = 1
    formal_log = {}
    domain_work = [0] * len(DOMAINS)
    topic_work = [0] * len(TOPICS)
    numerical_writes = 0
    log_additions = 0

    def transition(bit_index, old, new):
        nonlocal integer, formal_log, numerical_writes, log_additions
        require(old in (0, 1) and new in (0, 1) and old != new,
                'invalid binary phase transition')
        p = BASES[bit_index]
        require(exponent_at(integer, p) == old, 'numeric and symbolic state diverged')
        delta = new - old
        if delta > 0:
            integer *= p
        else:
            require(integer % p == 0, 'non-exact prime division')
            integer //= p
        # Reuse G26's exact additive formal-log algebra (symbolic, no floats).
        formal_log = symbolic_log_product(formal_log, {p: delta})
        numerical_writes += 1
        log_additions += 1
        require(formal_log.get(p, 0) == new, 'formal-log transition drift')

    for domain, action in packet['events']:
        i = DOMAINS.index(domain)  # membership and exact action checked by G24
        new = int(action == 'ENTER_RESEARCH')
        transition(i, domain_work[i], new)
        domain_work[i] = new

    for record in packet['evidence']:
        domain, topic_index = record[:2]  # strict format & duplicate policy checked by G25
        j = next(k for k, (d, t, _) in enumerate(TOPICS)
                 if d == domain and t == topic_index)
        require(domain_work[DOMAINS.index(domain)] == 1,
                'evidence field requires research-only state')
        if topic_work[j] == 0:
            transition(len(DOMAINS) + j, 0, 1)
            topic_work[j] = 1

    expected = domain_state + topic_state
    decoded = decode_exact(integer, BASES)
    require(decoded == expected == tuple(domain_work + topic_work),
            'exact numeric decoding differs from G24/G25 states')
    require(formal_log == {p: 1 for p, e in zip(BASES, decoded) if e},
            'exact log coefficient mismatch')
    domain_product = 1
    for p, bit in zip(BASES[:14], domain_state):
        if bit:
            domain_product *= p
    require(domain_product == g24['prime_power_integer'], 'G24 factor mismatch')
    evidence_product = 1
    for j, bit in enumerate(topic_state):
        if bit:
            evidence_product *= BASES[14 + j]
    require(integer == g24['prime_power_integer'] * evidence_product,
            'G24/G25 separate prime families mismatched')
    expected_g25_exponents = [min(2, sum(topic_state[j] for j, (name, _, _)
                                                in enumerate(TOPICS) if name == domain))
                              for domain in DOMAINS]
    require(expected_g25_exponents == g25['exponents'],
            'G25 domain evidence coverage mismatch')
    return {
        'version': 'G27', 'status': STATUS,
        'master': 'UTM-PLEIADES-v0.2-PTCA',
        'domains': len(DOMAINS), 'evidence_topics': len(TOPICS),
        'events_replayed': len(packet['events']), 'synthetic_records_received': len(packet['evidence']),
        'distinct_topics_received': sum(topic_state),
        'domain_state_bits': list(domain_state), 'evidence_topic_bits': list(topic_state),
        'combined_godel_integer': integer,
        'g24_integer': g24['prime_power_integer'],
        'evidence_topic_integer': evidence_product,
        'formal_log_coefficients': [[p, 1] for p, bit in zip(BASES, decoded) if bit],
        'formal_log_terms': len(formal_log),
        'integer_multiplicative_updates': numerical_writes,
        'exact_formal_log_additions': log_additions,
        'direct_numeric_factorization_equal': True,
        'exact_log_product_identity': True,
        'g24_g25_synthetic_validation_passed': True,
        'metadata_present_not_authenticated': True,
        'independent_evidence_authenticated': False,
        'independent_impact_proved': False,
        'all_dimensions_immortality_proved': False,
        'world_peace_achieved': False,
        'all_sdgs_achieved': False,
        'cultivated_meat_approved_or_cruelty_free_proved': False,
        'trader42_profit_validated': False,
        'production_deployed': False,
        'orders_submitted': 0, 'sha_used': False,
        'network_access': False, 'human_review_required': True,
    }


if __name__ == '__main__':
    try:
        if len(sys.argv) != 1:
            raise ValueError('usage: < G27_example_request.json')
        print(json.dumps(run(json.load(sys.stdin)), sort_keys=True))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print('BLOCKED:', exc, file=sys.stderr)
        raise SystemExit(1)
