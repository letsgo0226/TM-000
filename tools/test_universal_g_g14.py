#!/usr/bin/env python3
"""G14 synthetic paper-signal, unchanged-source and fail-closed risk tests."""
import copy
from datetime import date
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "deployment"))
from G14_Trader42_Principle_core import check, review_candidate, sma_signal, GATES

G13 = "deployment/G13_peace_sdgs_cultivated_meat_contract.json"
G14 = "deployment/G14_trader42_principle_contract.json"
SCRIPT = "deployment/Universal_G_G14_Trader42_Plaintext_2KB.sh"
DAY = date(2026, 11, 10)
BUYS = [50000] * 20 + [50001]
SELLS = [50000] * 20 + [49999]

def good_context():
    ctx = dict.fromkeys(GATES, True)
    ctx.update(mode="paper", live_armed=False, live_dry_run=True,
               reconciled=True, cooldown_elapsed=True, kill_active=False,
               pending_order=False, fees_and_slippage_stress_tested=True,
               realized_loss_usdt="0", daily_equity_loss_pct="0",
               current_base_btc="0", desired_quote_usdt="10",
               sized_quote_usdt="9", available_quote_usdt="100",
               current_notional_usdt="0")
    return ctx

class G14Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in (G13, G14, SCRIPT):
            out = self.root / name
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, out)
        self.policy = json.loads((self.root / G14).read_text(encoding="utf-8"))

    def tearDown(self):
        self.tmp.cleanup()

    def mutate(self, filename, operation):
        out = self.root / filename
        data = json.loads(out.read_text(encoding="utf-8"))
        operation(data)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    def run_shell(self, optimize=False):
        env = dict(os.environ)
        if optimize:
            env["PYTHONOPTIMIZE"] = "2"
        return subprocess.run(["bash", str(self.root / SCRIPT), "2026-11-10"],
                              capture_output=True, text=True, timeout=10, env=env)

    def test_01_policy_is_paper_and_nontrading(self):
        result = check(self.root, DAY)
        self.assertEqual((result["version"], result["strategy"], result["reference_files"]),
                         ("G14", "SMA_5_20", 8))
        self.assertFalse(result["live_armed"])
        self.assertEqual(result["exchange_orders_submitted"], 0)

    def test_02_one_liner_matches_readable(self):
        proc = self.run_shell()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), check(self.root, DAY))

    def test_03_optimize_cannot_skip(self):
        proc = self.run_shell(True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), check(self.root, DAY))

    def test_04_one_line_under_2048(self):
        data = (self.root / SCRIPT).read_bytes()
        self.assertLessEqual(len(data), 2048)
        self.assertEqual(data.count(b"\n"), 1)
        for forbidden in (b"base64", b"zlib", b"eval(", b"exec("):
            self.assertNotIn(forbidden, data)

    def test_05_future_review_is_rejected(self):
        with self.assertRaises(ValueError):
            check(self.root, date(2026, 11, 9))

    def test_06_expired_review_is_rejected(self):
        with self.assertRaises(ValueError):
            check(self.root, date(2027, 5, 10))

    def test_07_buy_cross_is_only_a_simulated_signal(self):
        self.assertEqual(sma_signal(BUYS), "BUY")
        self.assertEqual(review_candidate(BUYS, good_context(), self.policy),
                         "SIMULATED_BUY_SIGNAL_ONLY")

    def test_08_sell_cross_only_if_position_exists(self):
        ctx = good_context()
        ctx["current_base_btc"] = ".0003"
        self.assertEqual(sma_signal(SELLS), "SELL")
        self.assertEqual(review_candidate(SELLS, ctx, self.policy),
                         "SIMULATED_SELL_SIGNAL_ONLY")

    def test_09_no_position_no_sell(self):
        self.assertEqual(review_candidate(SELLS, good_context(), self.policy),
                         "HOLD_NO_POSITION")

    def test_10_no_change_in_signal(self):
        self.assertEqual(review_candidate([50000]*21, good_context(), self.policy),
                         "HOLD_NO_CROSSOVER")

    def test_11_kill_switch_overrides_all(self):
        ctx = good_context()
        ctx["kill_active"] = True
        self.assertEqual(review_candidate(BUYS, ctx, self.policy), "HALT_KILL")

    def test_12_pending_exchange_order_requires_reconciliation(self):
        ctx = good_context()
        ctx["pending_order"] = True
        self.assertEqual(review_candidate(BUYS, ctx, self.policy), "HALT_RECONCILIATION")

    def test_13_missing_reconciliation_halts(self):
        ctx = good_context()
        ctx["reconciled"] = False
        self.assertEqual(review_candidate(BUYS, ctx, self.policy), "HALT_RECONCILIATION")

    def test_14_cooldown_holds(self):
        ctx = good_context()
        ctx["cooldown_elapsed"] = False
        self.assertEqual(review_candidate(BUYS, ctx, self.policy), "HOLD_COOLDOWN")

    def test_15_live_mode_cannot_be_armed(self):
        ctx = good_context()
        ctx["mode"] = "live"
        self.assertEqual(review_candidate(BUYS, ctx, self.policy), "BLOCKED_NONPAPER")

    def test_16_bad_tm_certificate_holds(self):
        ctx = good_context()
        ctx["TMVerified"] = False
        self.assertEqual(review_candidate(BUYS, ctx, self.policy), "HOLD_INVARIANT")

    def test_17_bad_intrinsic_certificate_holds(self):
        ctx = good_context()
        ctx["IntrinsicCertificate"] = False
        self.assertEqual(review_candidate(BUYS, ctx, self.policy), "HOLD_INVARIANT")

    def test_18_missing_cost_model_holds(self):
        ctx = good_context()
        ctx["fees_and_slippage_stress_tested"] = False
        self.assertEqual(review_candidate(BUYS, ctx, self.policy),
                         "HOLD_MISSING_COST_MODEL")

    def test_19_two_usdt_loss_review_halts(self):
        ctx = good_context()
        ctx["realized_loss_usdt"] = "2"
        self.assertEqual(review_candidate(BUYS, ctx, self.policy), "HALT_LOSS_REVIEW")

    def test_20_one_pct_loss_review_halts(self):
        ctx = good_context()
        ctx["daily_equity_loss_pct"] = "1"
        self.assertEqual(review_candidate(BUYS, ctx, self.policy), "HALT_LOSS_REVIEW")

    def test_21_increase_only_sizing_holds(self):
        ctx = good_context()
        ctx["sized_quote_usdt"] = "11"
        self.assertEqual(review_candidate(BUYS, ctx, self.policy),
                         "HOLD_DECREASE_ONLY_OR_EXPOSURE")

    def test_22_sized_quote_cannot_exceed_requested(self):
        ctx = good_context()
        ctx["desired_quote_usdt"] = "5"
        self.assertEqual(review_candidate(BUYS, ctx, self.policy),
                         "HOLD_DECREASE_ONLY_OR_EXPOSURE")

    def test_23_total_exposure_is_capped(self):
        ctx = good_context()
        ctx["current_notional_usdt"] = "49"
        self.assertEqual(review_candidate(BUYS, ctx, self.policy),
                         "HOLD_DECREASE_ONLY_OR_EXPOSURE")

    def test_24_base_exposure_is_capped(self):
        ctx = good_context()
        ctx["current_base_btc"] = ".0009"
        self.assertEqual(review_candidate(BUYS, ctx, self.policy),
                         "HOLD_DECREASE_ONLY_OR_EXPOSURE")

    def test_25_balance_prevents_buy(self):
        ctx = good_context()
        ctx["available_quote_usdt"] = "1"
        self.assertEqual(review_candidate(BUYS, ctx, self.policy),
                         "HOLD_DECREASE_ONLY_OR_EXPOSURE")

    def test_26_missing_price_history_cannot_signal(self):
        self.assertEqual(review_candidate([50000]*4, good_context(), self.policy),
                         "HALT_INVALID_INPUT")

    def test_27_nan_price_cannot_signal(self):
        self.assertEqual(review_candidate([50000]*20 + ["NaN"], good_context(), self.policy),
                         "HALT_INVALID_INPUT")

    def test_28_missing_cash_data_halts(self):
        ctx = good_context()
        del ctx["available_quote_usdt"]
        self.assertEqual(review_candidate(BUYS, ctx, self.policy), "HALT_INVALID_INPUT")

NEGATIVE_POLICIES = [
    ("g13_parent_tampered", G13, lambda d: d["tracks"][0].update(claim_proved=True)),
    ("g13_hash_replaced", G14, lambda d: d.update(parent_g13_git_blob_sha="0"*40)),
    ("master_changed", G14, lambda d: d.update(master="TM-015")),
    ("mode_live", G14, lambda d: d.update(trader_mode="live")),
    ("live_armed", G14, lambda d: d.update(live_armed=True)),
    ("dryrun_disabled", G14, lambda d: d.update(live_dry_run=False)),
    ("kill_bypassed", G14, lambda d: d.update(trading_kill_bypass=True)),
    ("credentials_enabled", G14, lambda d: d.update(credential_access=True)),
    ("order_submissions_enabled", G14, lambda d: d.update(order_submission=True)),
    ("source_run_claimed", G14, lambda d: d.update(source_executed=True)),
    ("profit_guaranteed", G14, lambda d: d.update(profit_guaranteed=True)),
    ("max_order_increased", G14, lambda d: d["risk"].update(max_order_quote_usdt="11")),
    ("max_total_increased", G14, lambda d: d["risk"].update(max_total_quote_usdt="51")),
    ("max_base_increased", G14, lambda d: d["risk"].update(max_base_exposure_btc=".002")),
    ("daily_loss_review_increased", G14, lambda d: d["risk"].update(additional_daily_realized_loss_review_usdt="3")),
    ("equity_loss_ceiling_increased", G14, lambda d: d["risk"].update(daily_equity_loss_pct_ceiling="2")),
    ("cooldown_reduced", G14, lambda d: d["risk"].update(cooldown_seconds=0)),
    ("decrease_only_removed", G14, lambda d: d["risk"].update(sizing_can_only_decrease=False)),
    ("reconciliation_removed", G14, lambda d: d["risk"].update(exchange_reconciliation_required=False)),
    ("sma_tampered", G14, lambda d: d["strategy"].update(fast_window=4)),
    ("cost_stress_removed", G14, lambda d: d["strategy"].update(cost_stress_required=False)),
    ("source_sha_forged", G14, lambda d: d["source_files"][0].update(git_blob_sha="0"*40)),
    ("insufficient_source_list", G14, lambda d: d["source_files"].pop()),
    ("risk_gate_omitted", G14, lambda d: d["invariant_gates"].remove("TMVerified")),
    ("false_authenticated_source", G14, lambda d: d.update(upstream_snapshot_authenticated=True)),
    ("release_authority_claimed", G14, lambda d: d.update(execution_allowed=True)),
    ("false_empirical_alpha", G14, lambda d: d.update(empirical_alpha_validated=True))
]
for index, (label, path, op) in enumerate(NEGATIVE_POLICIES, start=29):
    def test(self, path=path, op=op):
        self.mutate(path, op)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            check(self.root, DAY)
    setattr(G14Tests, f"test_{index:02d}_{label}", test)

if __name__ == "__main__":
    unittest.main(verbosity=2)
