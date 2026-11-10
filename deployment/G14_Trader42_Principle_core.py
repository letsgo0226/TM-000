#!/usr/bin/env python3
"""G14 Trader_42 principle checker: static policy + synthetic, never executable signals.

No Trader_42 imports, live market requests, order submission, secrets, or shell runs.
The GitHub blob pins are references, not independently authenticated upstream
snapshots. This layer may veto a candidate but never authorize execution.
"""
import argparse
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import sys

MASTER = "UTM-PLEIADES-v0.2-PTCA"
G13_BLOB = "dbb1f380a32ffa9720be2800428aa05ad9a4cf71"
SOURCES = {
    "README.md": "50a194d6fddc47a323afa9b9836650c58c16d727",
    "42u.sh": "4a059c13ed402e11c8447e5cec28e2e6d94d9715",
    "trader.py": "8277ecb6196f4f7028168b6f15b1c4aa4b82c24c",
    "risk.py": "c42b929193d210527595aa7a117d1d5dc3a19083",
    "sizing.py": "65801d45084c6a61dfa315c7e0344f97ff71abb6",
    "trading_tm.py": "ac7d14d078059abb5a6429d77e724ccbc0af2509",
    "live.py": "897d4d0b207c974c29c90b6650b6c7f031ebc739",
    "qtm42.py": "24fa5edf10c366b4f37bde943d3ef2aed22a32a7",
}
GATES = [
    "RiskSafe", "CapitalSafe", "ExecutionValid", "Auditable", "TMVerified",
    "DecreaseOnlySizing", "ExchangeReconciled", "IntrinsicCertificate"
]
TRUE_RISK = [
    "sizing_can_only_decrease", "kill_is_overriding",
    "exchange_reconciliation_required", "pending_order_blocks",
    "certificate_must_match_persisted_state"
]
FALSE_GLOBAL = [
    "upstream_snapshot_authenticated", "source_executed", "live_armed",
    "trading_kill_bypass", "credential_access", "exchange_network_access",
    "order_submission", "automated_release", "execution_allowed",
    "empirical_alpha_validated", "profit_guaranteed", "real_trades_executed"
]
def require(ok, label):
    if not ok:
        raise ValueError(label)
def finite(value, label):
    try:
        number = Decimal(str(value))
        require(number.is_finite(), label + ": nonfinite")
        return number
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(label + ": not a decimal") from exc
def check(root: Path, as_of: date):
    root = root.resolve()
    parent_bytes = (root / "deployment/G13_peace_sdgs_cultivated_meat_contract.json").read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(parent_bytes)).encode() + b"\0" + parent_bytes).hexdigest()
    require(sha == G13_BLOB, "G13 parent bytes changed")
    parent = json.loads(parent_bytes)
    policy = json.loads((root / "deployment/G14_trader42_principle_contract.json").read_text())
    require(policy["schema"] == "G14-trader42-principle-review/1" and
            policy["parent_module"] == parent["schema"] == "G13-peace-sdgs-cultivated-meat/1" and
            policy["parent_g13_git_blob_sha"] == G13_BLOB, "G13 linkage")
    require(policy["master"] == parent["master"] == MASTER and
            policy["trader_mode"] == "paper" and policy["live_dry_run"] is True and
            policy["research_outcome"] == "PAPER_SIGNAL_REVIEW_ONLY", "safe authority boundary")
    require(policy["upstream_repository"] == "letsgo0226/Trader_42.sh" and
            policy["upstream_ref"] == "main", "upstream identification")
    require(all(policy[k] is False for k in FALSE_GLOBAL), "execution/trading power requested")
    require(policy["schema_intent"] == "READ_ONLY_SIMULATION_CERTIFICATE_NOT_AN_EXECUTION_AUTHORITY",
            "unsupported certificate scope")
    require(policy["review_interval_days"] == 180 and
            0 <= (as_of - date.fromisoformat(policy["created_on"])).days <= 180,
            "source record stale or future dated")
    references = policy["source_files"]
    require(len(references) == len(SOURCES) and
            {x["path"]: x["git_blob_sha"] for x in references} == SOURCES,
            "Trader_42 source references changed")
    strategy = policy["strategy"]
    require(strategy["symbol"] == "BTCUSDT" and strategy["fast_window"] == 5 and
            strategy["slow_window"] == 20 and
            strategy["source"] == "SMA_PRICE_OBSERVATIONS" and
            strategy["cost_stress_required"] is True and
            all(strategy[k] is False for k in
                ("signal_is_profit_certificate", "optional_qtm42_is_alpha",
                 "lookahead_allowed", "markets_observed")), "trading principle distorted")
    risk = policy["risk"]
    require(all(risk[k] is True for k in TRUE_RISK), "risk or reconciliation bypass")
    for k, bound in (
        ("max_order_quote_usdt", "10"), ("max_total_quote_usdt", "50"),
        ("max_base_exposure_btc", "0.001"), ("additional_daily_realized_loss_review_usdt", "2"),
        ("daily_equity_loss_pct_ceiling", "1")
    ):
        amount = finite(risk[k], k)
        require(0 < amount <= Decimal(bound), "risk relaxation: " + k)
    require(isinstance(risk["cooldown_seconds"], int) and
            risk["cooldown_seconds"] >= 30, "cooldown relaxation")
    require(policy["invariant_gates"] == GATES, "gate list changed")
    return dict(version="G14", reference_files=8, strategy="SMA_5_20",
                risk_policy_unchanged_or_tighter=True, live_armed=False,
                source_executed=False, exchange_orders_submitted=0,
                authenticated_upstream=False, empirical_profit_verified=False,
                status="PAPER_SIGNAL_REVIEW_ONLY")
def sma_signal(prices):
    """Use >=21 synthetic observations so current and previous signals are independent."""
    require(isinstance(prices, list) and len(prices) >= 21, "SMA warmup incomplete")
    q = [finite(x, "price") for x in prices]
    require(all(x > 0 for x in q), "invalid price")
    def sign(x):
        return (x > 0) - (x < 0)
    prev = sign(sum(q[-6:-1])/5 - sum(q[-21:-1])/20)
    curr = sign(sum(q[-5:])/5 - sum(q[-20:])/20)
    return "BUY" if curr > 0 and prev <= 0 else (
        "SELL" if curr < 0 and prev >= 0 else "HOLD")
def review_candidate(prices, context, policy):
    """Research signal only. Never yields an executable order object."""
    if context.get("kill_active"):
        return "HALT_KILL"
    if context.get("pending_order") or not context.get("reconciled", False):
        return "HALT_RECONCILIATION"
    if context.get("cooldown_elapsed") is not True:
        return "HOLD_COOLDOWN"
    if context.get("mode") != "paper" or context.get("live_armed") is not False or (
            context.get("live_dry_run") is not True):
        return "BLOCKED_NONPAPER"
    if any(context.get(g) is not True for g in GATES):
        return "HOLD_INVARIANT"
    if context.get("fees_and_slippage_stress_tested") is not True:
        return "HOLD_MISSING_COST_MODEL"
    try:
        signal = sma_signal(prices)
        if signal == "HOLD":
            return "HOLD_NO_CROSSOVER"
        risk = policy["risk"]
        loss = finite(context["realized_loss_usdt"], "loss")
        daily_pct = finite(context["daily_equity_loss_pct"], "daily pct")
        require(loss >= 0 and daily_pct >= 0, "negative loss accounting")
        if loss >= finite(risk["additional_daily_realized_loss_review_usdt"], "loss cap") or (
                daily_pct >= finite(risk["daily_equity_loss_pct_ceiling"], "daily % cap")):
            return "HALT_LOSS_REVIEW"
        position = finite(context["current_base_btc"], "position")
        require(position >= 0, "negative position")
        if signal == "SELL":
            return "SIMULATED_SELL_SIGNAL_ONLY" if position > 0 else "HOLD_NO_POSITION"
        proposed = finite(context["desired_quote_usdt"], "desired")
        sized = finite(context["sized_quote_usdt"], "sized")
        available = finite(context["available_quote_usdt"], "available")
        exposure = finite(context["current_notional_usdt"], "notional")
        price = finite(prices[-1], "last price")
        require(min(proposed, sized, available, exposure) >= 0,
                "negative quote/exposure")
        if not (0 < sized <= proposed and sized <= available and
                sized <= finite(risk["max_order_quote_usdt"], "quote cap") and
                sized + exposure <= finite(risk["max_total_quote_usdt"], "total cap") and
                position + sized/price <= finite(risk["max_base_exposure_btc"], "base cap")):
            return "HOLD_DECREASE_ONLY_OR_EXPOSURE"
        return "SIMULATED_BUY_SIGNAL_ONLY"
    except (KeyError, ValueError, TypeError, ZeroDivisionError):
        return "HALT_INVALID_INPUT"
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    args = p.parse_args()
    try:
        result = check(args.root, args.as_of)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
