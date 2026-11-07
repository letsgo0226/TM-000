import unittest
from pathlib import Path
from staging_orchestrator import ALLOWED, plan

class PlannerTests(unittest.TestCase):
    def test_allowlist(self):
        for machine in ALLOWED:
            result = plan(machine)
            self.assertEqual(result["mode"], "STAGING_DRY_RUN_ONLY")
            self.assertFalse(result["executed"])
            self.assertFalse(result["production_authorized"])
            self.assertEqual(result["deployment_actions"], [])
            self.assertEqual(len(result["sha256"]), 64)
            self.assertGreater(result["bytes"], 0)

    def test_reject_unknown(self):
        with self.assertRaises(ValueError):
            plan("../unsafe")

if __name__ == "__main__":
    unittest.main()
