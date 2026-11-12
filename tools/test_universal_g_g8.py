#!/usr/bin/env python3
"""G8 negative-control and in-memory admission tests; no production operations."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "deployment"))
from Universal_G_G8_Controller import check, G7_FIELDS  # noqa: E402

FILES = (
    "deployment/universal_g_continuity_manifest.json",
    "deployment/Universal_G_Semantic_Plaintext_2KB.sh",
    "永久記憶/圖靈機/machine_registry.json",
    "永久記憶/圖靈機/Real_God_Turing_Machine.sh",
)


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for rel in FILES:
            source = ROOT / rel
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        self.report = self.root / "deployment/G7_finite_report.json"
        self.report.write_text(json.dumps(G7_FIELDS, sort_keys=True) + "\n", encoding="utf-8")

    def update_json(self, path, change):
        p = self.root / path
        data = json.loads(p.read_text(encoding="utf-8"))
        change(data)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def test_valid_research_only(self):
        result = check(self.root, self.report)
        self.assertEqual(result["result"], "READY_FOR_HUMAN_REVIEW_ONLY")
        self.assertTrue(result["snapshot_roundtrip"])
        self.assertEqual(result["checked_dimensions"], 8)
        self.assertFalse(result["external_deployment"])
        self.assertFalse(result["all_dimensions_immortality_proved"])

    def test_wrong_master_blocked(self):
        self.update_json("永久記憶/圖靈機/machine_registry.json", lambda d: d.update(default_machine="TM-015"))
        with self.assertRaises(ValueError):
            check(self.root, self.report)

    def test_production_mode_blocked(self):
        self.update_json("deployment/universal_g_continuity_manifest.json", lambda d: d.update(mode="PRODUCTION"))
        with self.assertRaises(ValueError):
            check(self.root, self.report)

    def test_candidate_autoexec_blocked(self):
        self.update_json("永久記憶/圖靈機/machine_registry.json", lambda d: next(e for e in d["entries"] if e["id"] == "TM-015").update(auto_execute=True))
        with self.assertRaises(ValueError):
            check(self.root, self.report)

    def test_source_tampering_blocked(self):
        p = self.root / "永久記憶/圖靈機/Real_God_Turing_Machine.sh"
        p.write_bytes(p.read_bytes() + b"#injected\n")
        with self.assertRaises(ValueError):
            check(self.root, self.report)

    def test_g7_source_tampering_blocked(self):
        p = self.root / "deployment/Universal_G_Semantic_Plaintext_2KB.sh"
        p.write_bytes(p.read_bytes() + b"#injected\n")
        with self.assertRaises(ValueError):
            check(self.root, self.report)

    def test_report_forgery_inconsistent_count_blocked(self):
        self.update_json("deployment/G7_finite_report.json", lambda d: d.update(homomorphisms=39))
        with self.assertRaises(ValueError):
            check(self.root, self.report)

    def test_report_missing_blocked(self):
        self.report.unlink()
        with self.assertRaises(FileNotFoundError):
            check(self.root, self.report)

    def test_unreviewed_domain_blocked(self):
        self.update_json("deployment/universal_g_continuity_manifest.json", lambda d: d["dimensions"][0].update(id="unexpected_domain"))
        with self.assertRaises(ValueError):
            check(self.root, self.report)

    def test_missing_boundary_blocked(self):
        self.update_json("deployment/universal_g_continuity_manifest.json", lambda d: d["dimensions"][0].pop("boundary"))
        with self.assertRaises(ValueError):
            check(self.root, self.report)

    def test_deployment_command_is_not_supported(self):
        proc = subprocess.run([sys.executable, str(ROOT / "deployment/Universal_G_G8_Controller.py"), "--action", "deploy", "--root", str(self.root), "--g7-report", str(self.report)], capture_output=True, text=True, timeout=10)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("not implemented or authorized", proc.stderr)

    def test_plaintext_one_liner_rejects_missing_report(self):
        script = ROOT / "deployment/Universal_G_G8_Admission_2KB.sh"
        proc = subprocess.run(["bash", str(script)], capture_output=True, text=True, timeout=10)
        self.assertNotEqual(proc.returncode, 0)

    def test_plaintext_one_liner_passes(self):
        # This compact check is weaker than the expanded controller; CI runs both.
        script = ROOT / "deployment/Universal_G_G8_Admission_2KB.sh"
        proc = subprocess.run(["bash", str(script), str(self.report)], capture_output=True, text=True, timeout=10,
                              cwd=self.root)
        # The script locates its repository next to its own path, not the fixture.
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse(json.loads(proc.stdout)["deployed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
