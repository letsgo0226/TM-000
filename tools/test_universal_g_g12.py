#!/usr/bin/env python3
"""G12: 34 offline unit checks including tampering, falsified claims and no-deploy controls."""
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
from G12_Claim_Scope_core import check

G11 = "deployment/G11_eight_domain_evidence_ledger.json"
G12 = "deployment/G12_claim_scope_ledger.json"
SCRIPT = "deployment/Universal_G_G12_Claim_Plaintext_2KB.sh"
DAY = date(2026, 11, 10)

class G12Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for f in (G11, G12, SCRIPT):
            p = self.root / f
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / f, p)

    def tearDown(self):
        self.tmp.cleanup()

    def edit(self, f, op):
        p = self.root / f
        obj = json.loads(p.read_text(encoding="utf-8"))
        op(obj)
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    def shell(self, optimized=False):
        env = dict(os.environ)
        if optimized:
            env["PYTHONOPTIMIZE"] = "2"
        return subprocess.run(["bash",str(self.root / SCRIPT),"2026-11-10"],
                              text=True,capture_output=True,timeout=10,env=env)

    def test_01_review_only(self):
        o = check(self.root,DAY)
        self.assertEqual((o["reviewed_claims"],o["domains"],o["status"]),
                         (8,8,"CLAIM_SCOPE_REVIEW_ONLY"))
        self.assertFalse(o["production_deployed"])
        self.assertFalse(o["divine_identity_proved"])
        self.assertFalse(o["universal_immortality_proved"])

    def test_02_shell_matches_readable(self):
        r = self.shell()
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout),check(self.root,DAY))

    def test_03_optimized_mode_matches(self):
        r = self.shell(True)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout),check(self.root,DAY))

    def test_04_plaintext_2kb(self):
        b=(self.root / SCRIPT).read_bytes()
        self.assertLessEqual(len(b),2048)
        self.assertEqual(b.count(b"\n"),1)
        for token in (b"zlib",b"base64",b"eval(",b"exec("):
            self.assertNotIn(token,b)

NEGATIVE = [
    ("parent_byte_tamper",G11,lambda d:d["records"][0].update(publisher="Forged")),
    ("parent_digest",G12,lambda d:d.update(parent_digest_sha256="0"*64)),
    ("master_promotion",G12,lambda d:d.update(master="TM-015")),
    ("production_deploy",G12,lambda d:d.update(mode="PRODUCTION")),
    ("fake_signature",G12,lambda d:d.update(publisher_signature_verified=True)),
    ("fake_observation",G12,lambda d:d.update(field_observations_validated=True)),
    ("fake_web_fetch",G12,lambda d:d.update(online_refetched_in_ci=True)),
    ("fake_snapshot",G12,lambda d:d.update(content_snapshots_stored=True)),
    ("all_outcomes_verified",G12,lambda d:d.update(all_eight_outcomes_verified=True)),
    ("missing_domain",G12,lambda d:d["claims"].pop()),
    ("duplicate_source",G12,lambda d:d["claims"].__setitem__(7,copy.deepcopy(d["claims"][0]))),
    ("source_id_spoof",G12,lambda d:d["claims"][0].update(source_id="unknown")),
    ("source_url_spoof",G12,lambda d:d["claims"][1].update(source_url="https://example.org/false")),
    ("source_kind_spoof",G12,lambda d:d["claims"][7].update(source_kind="CLINICAL_TRIAL")),
    ("remove_inference_exclusion",G12,lambda d:d["claims"][7].update(excluded_inference="")),
    ("unsupported_claim_scope",G12,lambda d:d["claims"][2].update(limited_to="PROVEN_HUMAN_IMMORTALITY")),
    ("verified_outcome_spoof",G12,lambda d:d["claims"][2].update(outcome_verified=True)),
    ("erase_evidence_gap",G12,lambda d:d["claims"][3].update(evidence_required="")),
    ("divine_claim_code",G12,lambda d:d["claims"][7].update(claim_code="DIVINE_IDENTITY_PROVEN")),
    ("divine_claim_text",G12,lambda d:d["claims"][7].update(claim_text="G equals God: proved.")),
    ("remove_forbidden_claim",G12,lambda d:d["forbidden_global_claims"].remove("DIVINITY_PROVEN")),
    ("expired_source_review",G12,lambda d:d["claims"][2].update(reviewed_on="2025-01-01")),
    ("future_source_review",G12,lambda d:d["claims"][1].update(reviewed_on="2027-01-01")),
    ("wrong_schema",G12,lambda d:d.update(schema="G12-claim-scope-review/2")),
    ("inflated_review_window",G12,lambda d:d.update(expiry_days=5000)),
    ("blank_claim_text",G12,lambda d:d["claims"][0].update(claim_text="")),
    ("status_promotion",G12,lambda d:d.update(status="READY_FOR_DEPLOYMENT")),
    ("broken_parent_reference",G12,lambda d:d.update(parent_ledger="unknown")),
    ("expired_ledger_review",G12,lambda d:d.update(reviewed_on="2024-01-01")),
    ("parent_content_mutation",G11,lambda d:d["records"][1].update(id="unknown")),
]
for index,(name,path,op) in enumerate(NEGATIVE,start=5):
    def test(self,path=path,op=op):
        self.edit(path,op)
        with self.assertRaises((ValueError,KeyError,TypeError)):
            check(self.root,DAY)
    setattr(G12Tests,f"test_{index:02d}_{name}",test)

if __name__=="__main__":
    unittest.main(verbosity=2)
