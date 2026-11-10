#!/usr/bin/env python3
"""Offline, read-only compatibility gate for G16 simulator, TM-015 and G15 policy."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import sys


G15_BLOB = 'abc3c497e142d72d20bf41326f00dbf57c404dc1'
TM015_SHA = '4e68a5a333417e7f5b49989a297b72a41642efce892b0033b27621f19c248c6d'
MASTER = 'UTM-PLEIADES-v0.2-PTCA'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def check(root, as_of):
    root = Path(root).resolve()
    policy = json.loads((root/'deployment/G16_god_source_tm_contract.json').read_text())
    parent = (root/'deployment/G15_godel_trading_contract.json').read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(parent)).encode()+b'\0'+parent).hexdigest()
    tm015 = (root/'永久記憶/圖靈機/Real_God_Turing_Machine.sh').read_bytes()
    registry = json.loads((root/'永久記憶/圖靈機/machine_registry.json').read_text())
    require(blob == policy['parent_g15_git_blob_sha'] == G15_BLOB, 'G15 policy version mismatch')
    require(hashlib.sha256(tm015).hexdigest() == policy['original_tm015_sha256'] == TM015_SHA,
            'protected TM-015 source changed')
    require(policy['schema'] == 'G16-god-source-tm-simulator/1', 'wrong schema')
    require(policy['actual_master'] == registry['default_machine'] == MASTER, 'master mismatch')
    require(policy['mode'] == 'SYNTHETIC_PAPER_SIMULATION_ONLY' and
            policy['review_status'] == 'TM_SIMULATION_REVIEW_ONLY', 'execution authority requested')
    require(policy['interpretation'] == 'BOUNDED_DETERMINISTIC_SINGLE_TAPE_TM', 'model changed')
    require(policy['original_tm015_coding'] == 'PRIME_DIGITS_BASE2048_BYTE_TO_FIRST_256_PRIMES'
            and policy['g15_coding'] == 'BASE257_BYTE_PLUS_ONE' and
            policy['identity_empty_word_code'] == 1, 'coding or identity mislabeled')
    require(policy['max_steps'] == 512 and policy['max_initial_tape_cells'] == 64 and
            policy['max_rules'] == 128 and policy['max_states_claimed_unbounded'] is False,
            'resource limits removed')
    require(policy['preserves_archive_without_execution'] is True, 'archive execution attempted')
    for key in ('network_access','market_access','orders_allowed','secrets_access',
                'production_deployed','auto_merge','profitability_proved','god_identity_proved',
                'general_halting_oracle'):
        require(policy[key] is False, 'unsafe claim: '+key)
    age = (as_of-date.fromisoformat(policy['created_on'])).days
    require(0 <= age <= 180, 'source review expired or future dated')
    for name, key in [('G16_God_Source_TM_core.py', 'core_sha256'),
                      ('Universal_G_G16_TM_Plaintext_2KB.sh', 'oneliner_sha256')]:
        data=(root/'deployment'/name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == policy[key], 'G16 code modified: '+name)
    return dict(version='G16', status='TM_SIMULATION_REVIEW_ONLY',
                master_unchanged=True, original_tm015_preserved=True,
                g15_separate_codec_preserved=True, bounded_tape=True,
                actual_orders=0, network_access=False, halting_oracle=False, god_identity_proved=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--as-of',type=date.fromisoformat,default=date.today())
    args=parser.parse_args()
    try:
        report=check(args.root,args.as_of)
    except (ValueError, KeyError, OSError, TypeError, json.JSONDecodeError) as exc:
        print('BLOCKED: '+str(exc), file=sys.stderr)
        return 1
    print(json.dumps(report,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
