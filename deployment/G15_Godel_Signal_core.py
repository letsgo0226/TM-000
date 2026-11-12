#!/usr/bin/env python3
"""Pure, no-order G15 Gödel state and heldout evaluation engine.

No live market access, secrets, broker APIs, SMA, or QTM42.
"""
import json
import math
import sys


def run(x):
    def need(c):
        if not c:
            raise ValueError('BLOCKED')
    need(isinstance(x, dict) and x.get('source') == 'SYNTHETIC' and
         x.get('mode') == 'paper' and x.get('position') in ('FLAT', 'LONG'))
    prices = x.get('prices')
    need(isinstance(prices, list) and 100 <= len(prices) <= 2000)
    need(all(type(v) in (int, float) and math.isfinite(v) and v > 0 for v in prices))
    prices = [float(v) for v in prices]
    returns = [10000 * (b / a - 1) for a, b in zip(prices, prices[1:])]
    need(all(math.isfinite(v) and abs(v) <= 2500 for v in returns))
    states = [2 if v > 0 else 0 if v < 0 else 1 for v in returns]
    n = len(states)
    cut = n * 7 // 10
    need(cut >= 30 and n-cut >= 20)
    groups = [[returns[i] for i in range(1, cut) if states[i-1] == k] for k in range(3)]
    edge = [sum(g)/len(g) if len(g) >= 6 else 0 for g in groups]
    cost = 20.0  # bps per turnover, deliberately fixed paper stress
    pos = 0
    pnl = 0.0
    changes = 0
    for i in range(cut, n):
        next_pos = int(edge[states[i-1]] > 2 * cost + 30 / math.sqrt(max(1, len(groups[states[i-1]]))))
        changes += abs(next_pos-pos)
        pnl += next_pos * returns[i] - abs(next_pos-pos) * cost
        pos = next_pos
    pnl -= pos * cost  # terminal hypothetical exit
    changes += pos
    last = states[-1]
    favorable = len(groups[last]) >= 6 and edge[last] > 2*cost + 30/math.sqrt(len(groups[last]))
    current = 1 if x['position'] == 'LONG' else 0
    # Historical heldout success is an optional veto, never proof of profitable trading.
    target = int(favorable and pnl > 0 and changes >= 2)
    action = 'BUY' if target and not current else 'SELL' if current and not target else 'HOLD'
    # 257-base, byte+1 representation; unique empty-word identity G(ε)=1.
    b = bytes(states[-8:])
    code = 1
    for v in b:
        code = 257 * code + v + 1
    original = code
    recovered = []
    while code > 1:
        code, rem = divmod(code, 257)
        need(rem > 0)
        recovered.insert(0, rem-1)
    need(bytes(recovered) == b)
    return dict(version='G15', action='SIMULATED_'+action+'_ONLY' if action != 'HOLD' else 'HOLD',
                godel=original, roundtrip=True, train_events=cut, heldout_events=n-cut,
                heldout_net_bps=round(pnl, 3), heldout_turnovers=changes,
                model='G257_CONDITIONAL_RETURN', fee_slippage_bps_per_side=cost,
                live_allowed=False, actual_orders=0, profitability_proved=False)


if __name__ == '__main__':
    try:
        print(json.dumps(run(json.load(sys.stdin)), sort_keys=True))
    except (ValueError, KeyError, TypeError, OverflowError, json.JSONDecodeError):
        print('BLOCKED', file=sys.stderr)
        raise SystemExit(1)
