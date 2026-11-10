#!/usr/bin/env python3
"""G13 synthetic evidence-contract, source-tampering and ethical-risk negative tests."""
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
from G13_Peace_SDG_CellFood_core import check, assess_candidate

G12 = "deployment/G12_claim_scope_ledger.json"
G13 = "deployment/G13_peace_sdgs_cultivated_meat_contract.json"
SCRIPT = "deployment/Universal_G_G13_Peace_SDG_CellFood_Plaintext_2KB.sh"
DAY = date(2026, 11, 10)

class G13Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for filename in (G12, G13, SCRIPT):
            source = ROOT / filename
            target = self.root / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    def tearDown(self):
        self.tmp.cleanup()

    def edit(self, name, change):
        file = self.root / name
        value = json.loads(file.read_text(encoding="utf-8"))
        change(value)
        file.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")

    def shell(self, optimize=False, date_str="2026-11-10"):
        environment = dict(os.environ)
        if optimize:
            environment["PYTHONOPTIMIZE"] = "2"
        return subprocess.run(["bash", str(self.root / SCRIPT), date_str],
                              capture_output=True, text=True, timeout=10, env=environment)

    def test_01_three_tracks_and_seven_sources(self):
        result = check(self.root, DAY)
        self.assertEqual((result["tracks"], result["source_records"]), (3, 7))
        self.assertEqual(result["status"], "TRIAD_RESEARCH_REVIEW_ONLY")
        self.assertFalse(result["deployed"])
        self.assertFalse(result["zero_suffering_proved"])

    def test_02_plaintext_equals_readable(self):
        result = self.shell()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), check(self.root, DAY))

    def test_03_optimize_does_not_bypass(self):
        result = self.shell(True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), check(self.root, DAY))

    def test_04_plaintext_under_two_kib_and_one_line(self):
        source = (self.root / SCRIPT).read_bytes()
        self.assertLessEqual(len(source), 2048)
        self.assertEqual(source.count(b"\n"), 1)
        for token in (b"zlib", b"base64", b"eval(", b"exec("):
            self.assertNotIn(token, source)

    def test_05_expired_180_days_rejected(self):
        with self.assertRaises(ValueError):
            check(self.root, date(2027, 5, 10))

    def test_06_future_dated_rejected(self):
        with self.assertRaises(ValueError):
            check(self.root, date(2026, 11, 9))

    def test_07_default_candidate_unknown_welfare(self):
        self.assertEqual(assess_candidate({"animal_serum": "UNKNOWN"}),
                         "NEEDS_ANIMAL_WELFARE_EVIDENCE")

    def test_08_documented_animal_free_still_needs_food_review(self):
        self.assertEqual(assess_candidate({"animal_serum":"ANIMAL_FREE_DOCUMENTED",
                                          "cell_source_traceable":True}),
                         "NEEDS_FOOD_SAFETY_AND_REGULATORY_REVIEW")

    def test_09_documented_safe_process_still_needs_lca(self):
        self.assertEqual(assess_candidate({"animal_serum":"ANIMAL_FREE_DOCUMENTED",
                                          "cell_source_traceable":True,
                                          "food_safety_review":True,
                                          "regulatory_review":True}),
                         "NEEDS_ENVIRONMENTAL_ASSESSMENT")

    def test_10_complete_mock_goes_to_human_review_only(self):
        self.assertEqual(assess_candidate({"animal_serum":"ANIMAL_FREE_DOCUMENTED",
                                          "cell_source_traceable":True,
                                          "food_safety_review":True,
                                          "regulatory_review":True,
                                          "independent_lca":True}),
                         "READY_FOR_HUMAN_REVIEW_ONLY")

    def test_11_fbs_flag_rejected(self):
        self.assertEqual(assess_candidate({"animal_serum":"FBS_CONFIRMED"}),
                         "BLOCKED_ANIMAL_DERIVED_INPUT_ETHICS")

    def test_12_false_zero_suffering_rejected(self):
        self.assertEqual(assess_candidate({"claims":["ZERO_SUFFERING_VERIFIED"]}),
                         "BLOCKED_UNSUPPORTED_CLAIM")

    def test_13_world_peace_achievement_rejected(self):
        self.assertEqual(assess_candidate({"claims":["WORLD_PEACE_ACHIEVED"]}),
                         "BLOCKED_UNSUPPORTED_CLAIM")

    def test_14_sdg_achievement_rejected(self):
        self.assertEqual(assess_candidate({"claims":["ALL_SDGS_ACHIEVED"]}),
                         "BLOCKED_UNSUPPORTED_CLAIM")

    def test_15_unapproved_deployment_rejected(self):
        self.assertEqual(assess_candidate({"production_deployment_requested":True}),
                         "BLOCKED_UNAUTHORIZED_DEPLOYMENT")

    def test_16_invalid_serum_assertion_rejected(self):
        self.assertEqual(assess_candidate({"animal_serum":"ANIMAL_FREE_PROVEN"}),
                         "BLOCKED_INVALID_SERUM_ATTESTATION")

NEGATIVES = [
 ("g12_tamper",G12,lambda x:x["claims"][0].update(claim_code="ALTERED")),
 ("parent_digest",G13,lambda x:x.update(parent_digest_sha256="0"*64)),
 ("wrong_schema",G13,lambda x:x.update(schema="G13/2")),
 ("wrong_master",G13,lambda x:x.update(master="TM-015")),
 ("live_mode",G13,lambda x:x.update(mode="PRODUCTION")),
 ("status_promotion",G13,lambda x:x.update(status="PRODUCTION_APPROVED")),
 ("no_human_review",G13,lambda x:x.update(requires_human_review=False)),
 ("fake_remote_fetch",G13,lambda x:x.update(remote_refetch=True)),
 ("fake_signed_proof",G13,lambda x:x.update(signed_source_proof=True)),
 ("world_peace_claim",G13,lambda x:x.update(all_goals_achieved=True)),
 ("zero_suffering_claim",G13,lambda x:x.update(zero_suffering_proved=True)),
 ("cultivated_meat_approval_claim",G13,lambda x:x.update(product_approved=True)),
 ("green_claim",G13,lambda x:x.update(environmental_benefit_proved=True)),
 ("source_misrepresented",G13,lambda x:x["sources"][0].update(publisher="Unknown")),
 ("source_url_changed",G13,lambda x:x["sources"][0].update(url="https://example.org")),
 ("duplicate_source",G13,lambda x:x["sources"].__setitem__(6,copy.deepcopy(x["sources"][0]))),
 ("source_snapshot_claim",G13,lambda x:x["sources"][0].update(content_snapshot=True)),
 ("source_review_expired",G13,lambda x:x["sources"][0].update(reviewed_on="2024-01-01")),
 ("source_review_future",G13,lambda x:x["sources"][0].update(reviewed_on="2028-01-01")),
 ("indicators_changed",G13,lambda x:x["tracks"][0].update(indicators=["16.0"])),
 ("sdg_indicators_missing",G13,lambda x:x["tracks"][1]["indicators"].pop()),
 ("track_missing",G13,lambda x:x["tracks"].pop()),
 ("track_duplicated",G13,lambda x:x["tracks"].__setitem__(2,copy.deepcopy(x["tracks"][0]))),
 ("claim_proved",G13,lambda x:x["tracks"][0].update(claim_proved=True)),
 ("mock_observations_promoted",G13,lambda x:x["tracks"][1].update(observations_present=True)),
 ("animal_risk_suddenly_resolved",G13,lambda x:x["tracks"][2].update(animal_suffering_risk="ZERO_RISK")),
 ("fbs_on_candidate",G13,lambda x:x["tracks"][2].update(animal_input="FBS_CONFIRMED")),
 ("missing_fbs_audit",G13,lambda x:x["tracks"][2]["audits"].remove("ANIMAL_INPUT_AND_FBS_PROVENANCE")),
 ("lca_promoted",G13,lambda x:x["tracks"][2].update(life_cycle_assessment="APPROVED")),
 ("food_safety_promoted",G13,lambda x:x["tracks"][2].update(food_safety_status="APPROVED")),
 ("forbidden_claim_removed",G13,lambda x:x["forbidden_claims"].remove("ZERO_SUFFERING_VERIFIED")),
 ("review_interval_inflated",G13,lambda x:x.update(review_interval_days=9999)),
 ("metadata_presented_as_outcomes",G13,lambda x:x.update(source_metadata_only=False)),
]
for i, (label, path, change) in enumerate(NEGATIVES, start=17):
    def test(self, path=path, change=change):
        self.edit(path, change)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            check(self.root, DAY)
    setattr(G13Tests, f"test_{i:02d}_{label}", test)

if __name__ == "__main__":
    unittest.main(verbosity=2)
