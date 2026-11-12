#!/usr/bin/env python3
"""Offline-only G15 policy and independent veto of synthetic G257 signal proposals.

Reference metadata is not an authenticated remote provenance proof. No network,
subprocess, upstream execution, account access, or order submission.
"""
import argparse
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import sys

MASTER = 'UTM-PLEIADES-v0.2-PTCA'
PARENT_BLOB = '7dbe542735d431176243c83b99023d7585dca228'
INVARIANTS = ['RiskSafe', 'CapitalSafe', 'ExecutionValid', 'Auditable',
              'TMVerified', 'DecreaseOnlySizing', 'ExchangeReconciled', 'IntrinsicCertificate']
RISK_LIMITS = {
    'max_order_quote_usdt': Decimal('10'),
    'max_total_quote_usdt': Decimal('50'),
    'max_base_exposure_btc': Decimal('0.001'),
    'daily_equity_loss_pct': Decimal('1'),
    'daily_realized_loss_review_usdt': Decimal('2'),
}
PROHIBITED = ('broker_api', 'market_api', 'exec_upstream_source', 'live_armed',
              'auto_deploy', 'write_orders', 'independent_alpha_validation', 'guaranteed_profit')


def require(cond, reason):
    if not cond:
        raise ValueError(reason)


def amount(x, label):
    try:
        val = Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError('invalid amount: ' + label) from exc
    require(val.is_finite(), 'nonfinite amount: ' + label)
    return val


def check(root: Path, today: date):
    root = root.resolve()
    raw = (root / 'deployment/G14_trader42_principle_contract.json').read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(blob == PARENT_BLOB, 'G14 policy bytes changed')
    parent = json.loads(raw)
    policy = json.loads((root / 'deployment/G15_godel_trading_contract.json').read_text())
    require(policy['schema'] == 'G15-godel-trading-policy/1' and
            policy['parent_file'] == 'deployment/G14_trader42_principle_contract.json' and
            policy['parent_git_blob_sha'] == blob, 'parent lineage')
    require(policy['master'] == parent['master'] == MASTER and
            policy['trader_repository'] == parent['upstream_repository'], 'source/master changed')
    require(policy['strategy_engine'] == 'G257_CONDITIONAL_RETURN' and
            policy['signal_source'] == 'G15_ONLY_NO_SMA_NO_QTM42' and
            policy['encoding'] == 'BASE257_BYTE_PLUS_ONE', 'not G15 original signal')
    require(policy['training_split_percent'] == 70 and
            policy['minimum_pattern_support'] == 6 and
            amount(policy['one_way_fee_slippage_stress_bps'], 'cost') >= 20,
            'training/cost stress weakened')
    require(all(policy[k] is True for k in
                ('train_only_model_fit', 'holdout_veto_only', 'paper_only', 'synthetic_data_only')),
            'offline/data-splitting policy removed')
    require(all(policy[k] is False for k in PROHIBITED), 'unsupported trading authority')
    require(policy['approval_status'] == 'GODEL_PAPER_REVIEW_ONLY', 'approval promoted')
    require(policy['invariants'] == INVARIANTS, 'missing invariant')
    require(policy['review_days'] == 180 and
            0 <= (today - date.fromisoformat(policy['created_on'])).days <= 180,
            'stale/future policy')
    for key, val in RISK_LIMITS.items():
        x = amount(policy['risk_ceiling'][key], key)
        require(0 < x <= val, 'risk ceiling relaxed: '+key)
    require(type(policy['risk_ceiling']['minimum_cooldown_seconds']) is int and
            policy['risk_ceiling']['minimum_cooldown_seconds'] >= 30, 'cooldown relaxed')
    # The strict G14 parent itself is a record, not an endorsement of trading outcomes.
    require(parent['trader_mode'] == 'paper' and
            parent['live_armed'] is False and parent['live_dry_run'] is True and
            parent['execution_allowed'] is False, 'G14 parent authority drift')
    return dict(version='G15', policy='GODEL_PAPER_REVIEW_ONLY', source_pinned=True,
                reference_only=True, source_executed=False,
                real_prices_fetched=False, paper_only=True, actual_orders=0,
                live_authorized=False, empirical_alpha_proved=False)


def veto_proposal(proposal, state, policy):
    """Return a review label, never a live order or executable trade intent."""
    if not isinstance(proposal, dict) or proposal.get('version') != 'G15' or (
            proposal.get('actual_orders') != 0 or proposal.get('live_allowed') is not False):
        return 'HALT_BAD_CERTIFICATE'
    if proposal.get('action') not in ('HOLD', 'SIMULATED_BUY_ONLY', 'SIMULATED_SELL_ONLY'):
        return 'HALT_BAD_CERTIFICATE'
    if not isinstance(state, dict):
        return 'HALT_BAD_STATE'
    if state.get('kill_active') is not False:
        return 'HALT_KILL_OR_UNKNOWN'
    if state.get('pending_order') is not False or state.get('reconciled') is not True:
        return 'HALT_ORDER_RECONCILIATION'
    if state.get('mode') != 'paper' or state.get('live_armed') is not False:
        return 'HALT_NONPAPER'
    if state.get('cooldown_elapsed') is not True:
        return 'HOLD_COOLDOWN'
    if any(state.get(key) is not True for key in INVARIANTS):
        return 'HOLD_MISSING_INVARIANT'
    if state.get('cost_stress_reviewed') is not True:
        return 'HOLD_COST_NOT_REVIEWED'
    if proposal['action'] == 'HOLD':
        return 'HOLD'
    try:
        caps = policy['risk_ceiling']
        realized = amount(state['realized_daily_loss_usdt'], 'realized')
        pct = amount(state['daily_equity_loss_pct'], 'daily_pct')
        require(realized >= 0 and pct >= 0, 'negative loss accounting')
        if realized >= amount(caps['daily_realized_loss_review_usdt'], 'loss_limit') or (
                pct >= amount(caps['daily_equity_loss_pct'], 'pct_limit')):
            return 'HALT_LOSS_REVIEW'
        held = amount(state['current_base_btc'], 'held')
        require(held >= 0, 'negative position')
        if proposal['action'] == 'SIMULATED_SELL_ONLY':
            return 'SIMULATED_SELL_REVIEW_ONLY' if held > 0 else 'HOLD_NO_POSITION'
        desired = amount(state['desired_quote_usdt'], 'desired')
        sized = amount(state['sized_quote_usdt'], 'sized')
        cash = amount(state['available_quote_usdt'], 'cash')
        exposure = amount(state['total_quote_exposure_usdt'], 'notional')
        price = amount(state['synthetic_last_price'], 'price')
        require(min(desired, sized, cash, exposure, price) >= 0 and price > 0,
                'negative size, cash or price')
        if not (0 < sized <= desired and sized <= cash and
                sized <= amount(caps['max_order_quote_usdt'], 'per_order') and
                sized + exposure <= amount(caps['max_total_quote_usdt'], 'total') and
                held + sized / price <= amount(caps['max_base_exposure_btc'], 'base')):
            return 'HOLD_DECREASE_ONLY_OR_EXPOSURE'
        return 'SIMULATED_BUY_REVIEW_ONLY'
    except (ValueError, TypeError, KeyError, ZeroDivisionError):
        return 'HALT_INVALID_RISK_DATA'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--as-of', type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    try:
        output = check(args.root, args.as_of)
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print('BLOCKED: ' + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
