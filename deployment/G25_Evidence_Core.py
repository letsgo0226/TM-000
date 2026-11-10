#!/usr/bin/env python3
"""G25: fail-closed offline evidence *metadata* admissions, not outcome certification.

Provider/reviewer labels, dates, and topic coverage are self-asserted synthetic
metadata. No document is fetched or checked; no independent authentication.
G25 never grants any real-world authority, even if every topic is listed.
"""
from datetime import date
import json
from pathlib import Path
import sys

DOMAINS = (
    'master_tm', 'deployment', 'computational_continuity', 'ai_continuity',
    'human_longevity', 'interspecies_welfare', 'ecology', 'peace', 'sdgs',
    'cultivated_meat', 'trader42', 'culture_music', 'spirituality', 'food_security',
)
PRIMES = (5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53)
REQUIREMENTS = {
    'master_tm': ('fixed-master-check','formal-machine-execution'),
    'deployment': ('sandbox-ci','human-approval','rollback-proof'),
    'computational_continuity': ('state-integrity','bounded-recovery'),
    'ai_continuity': ('data-rights','reproducible-state','consent'),
    'human_longevity': ('clinical-endpoints','ethics-review','regulatory-oversight'),
    'interspecies_welfare': ('welfare-baseline','sentience-uncertainty'),
    'ecology': ('independent-lca','baseline-and-attribution'),
    'peace': ('conflict-death-timeseries','justice-access','nonviolent-governance'),
    'sdgs': ('2.1.2','12.3.1','13.2.2','16.1.2'),
    'cultivated_meat': ('cell-source-and-fbs','welfare','food-safety','jurisdiction-approval','independent-lca'),
    'trader42': ('paper-only','kill-switch','independent-holdout','cost-and-slippage'),
    'culture_music': ('original-lyrics','vocal-consent','rights-audit'),
    'spirituality': ('symbolic-not-physical-proof','consent','critical-rationality'),
    'food_security': ('food-safety','nutrition','affordability','accessibility'),
}
PERMISSIONS = (
    'network', 'auto_deploy', 'live_armed', 'order_submission', 'exchange_access',
    'external_execution', 'release', 'clinical_action',
    'regulatory_approval_claim', 'human_override',
)
STATUS = 'EVIDENCE_METADATA_REVIEW_ONLY'


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def strict_date(text):
    require(type(text) is str, 'date must be string')
    try:
        decoded = date.fromisoformat(text)
    except ValueError as error:
        raise ValueError('malformed date') from error
    require(decoded.isoformat() == text, 'date must be YYYY-MM-DD')
    return decoded


def valid_label(text):
    return (type(text) is str and 3 <= len(text) <= 32 and text.isascii()
            and text.isidentifier())


def factorize(number):
    require(type(number) is int and number >= 1, 'invalid evidence ledger integer')
    residue = number
    result = []
    for prime in PRIMES:
        exponent = 0
        while residue % prime == 0:
            residue //= prime
            exponent += 1
            require(exponent <= 2, 'exponent exceeds metadata-only phase budget')
        result.append(exponent)
    require(residue == 1, 'unlisted prime factor')
    return result


def run(packet):
    require(type(packet) is dict and set(packet) == {
        'source', 'mode', 'permissions', 'as_of', 'evidence'}, 'invalid packet schema')
    require(packet['source'] == 'SYNTHETIC' and packet['mode'] == 'offline',
            'only offline synthetic packets accepted')
    flags = packet['permissions']
    require(type(flags) is dict and set(flags) == set(PERMISSIONS),
            'missing or extra permission')
    require(all(value is False for value in flags.values()), 'external action not permitted')
    reviewed_as_of = strict_date(packet['as_of'])
    entries = packet['evidence']
    require(type(entries) is list and len(entries) <= 56, 'evidence packet limit')
    coverage = [set() for _ in DOMAINS]
    seen = set()
    for entry in entries:
        require(type(entry) is list and len(entry) == 7, 'record: seven ordered fields required')
        name, topic, provider, reviewer, record, observed, reviewed = entry
        require(type(name) is str and name in DOMAINS, 'unregistered domain')
        require(type(topic) is int and 0 <= topic < len(REQUIREMENTS[name]),
                'unknown topic index')
        require(all(valid_label(s) for s in (provider, reviewer, record)),
                'invalid synthetic provider/reviewer/record label')
        require(provider != reviewer, 'provider must not equal alleged reviewer')
        signature = name, topic, provider
        require(record not in seen and signature not in seen, 'duplicate evidence packet record')
        seen.add(record)
        seen.add(signature)
        observation = strict_date(observed)
        review = strict_date(reviewed)
        require(observation <= review <= reviewed_as_of, 'invalid observation/review chronology')
        require((reviewed_as_of - review).days <= 180, 'packet-relative review age exceeded')
        coverage[DOMAINS.index(name)].add(topic)
    phases = [min(2, len(topics)) for topics in coverage]
    integer = 1
    for prime, phase in zip(PRIMES, phases):
        integer *= prime ** phase
    require(factorize(integer) == phases, 'integer factorization mismatch')
    return {
        'version': 'G25', 'status': STATUS,
        'records': len(entries),
        'prime_power_integer': integer,
        'exponents': phases,
        'topics': {name: sorted(topics) for name, topics in zip(DOMAINS, coverage) if topics},
        'numeric_roundtrip': True,
        'authenticated': False, 'review_verified': False, 'outcomes_verified': False,
        'orders_submitted': 0, 'deployed': False, 'human_review_required': True,
    }


def check_parents(folder):
    """Local, structural check only; never certify upstream author or dataset."""
    root = Path(folder)
    g24 = json.loads((root/'G24_cross_domain_contract.json').read_text())
    g23 = json.loads((root/'G23_prime_power_godel_contract.json').read_text())
    g13 = json.loads((root/'G13_peace_sdgs_cultivated_meat_contract.json').read_text())
    g14 = json.loads((root/'G14_trader42_principle_contract.json').read_text())
    require(g24.get('schema') == 'G24-cross-domain-prime-power-governance/1', 'G24 contract mismatch')
    records = g24.get('domain_registry', [])
    require([(r['name'],r['prime'],tuple(r['required_real_world_evidence_not_present'])) for r in records]
            == [(d,p,REQUIREMENTS[d]) for d,p in zip(DOMAINS,PRIMES)], 'G24 domain/topic registry drift')
    require(g23.get('master') == g24.get('master') == g14.get('master')
            == 'UTM-PLEIADES-v0.2-PTCA', 'master invariant mismatch')
    require(g14.get('order_submission') is False and g14.get('live_armed') is False,
            'Trader_42 authority was altered')
    require(g13.get('all_goals_achieved') is False and g13.get('product_approved') is False,
            'G13 unsupported achievement flag')
    return {'version':'G25','status':'PARENT_METADATA_ALIGNED_NOT_AUTHENTICATED',
            'contracts_checked':4,'registry_topics_checked':sum(map(len,REQUIREMENTS.values())),
            'authenticated':False,'outcomes_verified':False,
            'orders_submitted':0,'deployed':False}


if __name__ == '__main__':
    try:
        if len(sys.argv) == 2 and sys.argv[1] == '--check-parent':
            result = check_parents(Path(__file__).resolve().parent)
        elif len(sys.argv) == 1:
            result = run(json.load(sys.stdin))
        else:
            raise ValueError('usage: < packet.json | --check-parent')
        print(json.dumps(result,sort_keys=True))
    except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError) as err:
        print('BLOCKED:',err,file=sys.stderr)
        raise SystemExit(1)
