#!/usr/bin/env python3
"""Cross-domain manifest+parent review; validates *claims*, never authorizes action.

Reads local JSON documents only, has no service calls, no SHA functions,
and cannot publish, trade, deploy, approve food, or perform treatments.
"""
import argparse
from datetime import date, timedelta
import json
from pathlib import Path
import sys
from G24S_cross_domain_core import DOMAINS, FLAGS, run, require

EXPECTED_MASTER = 'UTM-PLEIADES-v0.2-PTCA'
PARENTS = {
    'g23': 'deployment/G23_prime_power_godel_contract.json',
    'g13': 'deployment/G13_peace_sdgs_cultivated_meat_contract.json',
    'g14': 'deployment/G14_trader42_principle_contract.json',
}


def validate_manifest(manifest):
    require(type(manifest) is dict and
            manifest.get('schema') == 'G24S-prime-power-cross-domain-governance/1' and
            manifest.get('designated_master') == EXPECTED_MASTER, 'G24S manifest identity')
    require(manifest.get('status') == 'CROSS_DOMAIN_SYNTHETIC_REVIEW_ONLY', 'research-only status')
    entries = manifest.get('domains')
    require(type(entries) is list and len(entries) == len(DOMAINS), '12 domains mandatory')
    require([x.get('id') if type(x) is dict else None for x in entries] == list(DOMAINS), 'domain registry order')
    require(all(type(x['research_goal']) is str and len(x['research_goal']) > 8 and
                type(x['independent_evidence_needed']) is str and len(x['independent_evidence_needed']) > 15 and
                type(x['prohibited_inference']) is str and len(x['prohibited_inference']) > 15
                for x in entries), 'independent claim scope missing')
    ep = manifest.get('execution_policy')
    require(type(ep) is dict and ep.get('source') == 'SYNTHETIC' and ep.get('mode') == 'offline' and
            ep.get('human_review') is True, 'bad execution policy')
    require(all(ep.get(key) is False for key in FLAGS), 'unsafe external authority')
    require(all(ep.get(key) is False for key in ('external_authority', 'source_authenticity_proved', 'real_outcomes_proved', 'immortality_proved')), 'unsupported authority or outcome')
    require(manifest.get('check_threshold') == 3 and
            manifest.get('allowed_transitions') == [[0,1],[1,1],[1,2],[1,3]] and
            manifest.get('completed_real_world_outcomes') == 0 and
            manifest.get('authorized_external_actions') == 0, 'gate escalation')
    require(manifest.get('no_sha_or_digest_calls_in_execution') is True, 'no-digest contract violated')
    require(manifest.get('parent_g23_contract_path') == PARENTS['g23'] and
            manifest.get('parent_g13_contract_path') == PARENTS['g13'] and
            manifest.get('parent_g14_contract_path') == PARENTS['g14'], 'parent path mismatch')
    return True


def validate_parents(g23, g13, g14, as_of):
    require(g23.get('schema') == 'G23-prime-power-godel-computational-tm/1' and
            g23.get('master') == EXPECTED_MASTER and
            g23.get('same_G22_rules') is True and
            g23.get('transitions') == 1140 and
            g23.get('entire_replay_steps') == 3505682 and
            g23.get('sha_digest_functions_used') is False and
            g23.get('master_replaced') is False and
            g23.get('real_world_deployment') is False, 'G23 parent model lacks safe baseline')
    require(g13.get('schema') == 'G13-peace-sdgs-cultivated-meat/1' and
            g13.get('master') == EXPECTED_MASTER and
            g13.get('source_metadata_only') is True and
            g13.get('production_deployed') is False and
            g13.get('all_goals_achieved') is False and
            g13.get('zero_suffering_proved') is False and
            g13.get('product_approved') is False, 'G13 parent outcome overclaim')
    require(g14.get('schema') == 'G14-trader42-principle-review/1' and
            g14.get('master') == EXPECTED_MASTER and
            g14.get('trader_mode') == 'paper' and
            g14.get('live_armed') is False and
            g14.get('order_submission') is False and
            g14.get('execution_allowed') is False and
            g14.get('credential_access') is False and
            g14.get('exchange_network_access') is False and
            g14.get('upstream_snapshot_authenticated') is False,
            'G14 paper-only parent breached')
    risk = g14.get('risk')
    require(type(risk) is dict and risk.get('max_order_quote_usdt') == '10' and
            risk.get('max_total_quote_usdt') == '50' and
            risk.get('max_base_exposure_btc') == '0.001' and
            risk.get('daily_equity_loss_pct_ceiling') == '1' and
            risk.get('additional_daily_realized_loss_review_usdt') == '2' and
            risk.get('cooldown_seconds') == 30 and
            all(risk.get(k) is True for k in ('sizing_can_only_decrease','kill_is_overriding','exchange_reconciliation_required','pending_order_blocks')),
            'G14 risk or KILL invariant modified')
    require(type(as_of) is date, 'invalid review date')
    for doc, field in ((g13,'reviewed_on'),(g14,'created_on')):
        reviewed = date.fromisoformat(doc[field])
        days = doc['review_interval_days']
        require(type(days) is int and days == 180 and reviewed <= as_of <= reviewed + timedelta(days=days), 'parent evidence review expired / future dated')
    return True


def check(root, as_of):
    def load(path):
        return json.loads((root/path).read_text(encoding='utf-8'))
    manifest = load(Path('deployment/G24S_cross_domain_contract.json'))
    validate_manifest(manifest)
    validate_parents(*(load(Path(PARENTS[k])) for k in ('g23','g13','g14')), as_of)
    sample = load(Path('deployment/G24S_example_request.json'))
    result = run(sample)
    require(result['approved_external_actions'] == 0 and not result['real_world_outcomes_proved'] and
            result['exact_numeric_roundtrip'] and result['domain_count'] == 12, 'G24S core mismatch')
    return {'version':'G24S','status':'CROSS_DOMAIN_PARENT_POLICY_REVIEW_ONLY',
            'manifest_valid':True,'parents_within_review_window':True,
            'domains_checked':result['domain_count'],'prime_power_math_verified':True,
            'live_orders':0,'production_deployments':0,'real_outcomes_proved':False}


def cli():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--as-of',type=date.fromisoformat,default=date.today())
    args=p.parse_args()
    try:
        r=check(args.root,args.as_of)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as err:
        print('BLOCKED: '+str(err),file=sys.stderr)
        return 1
    print(json.dumps(r,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(cli())
