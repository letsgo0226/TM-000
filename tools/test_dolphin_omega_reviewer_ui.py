#!/usr/bin/env python3
"""v0.7 offline reviewer UI: safe HTML rendering and non-authoritative drafts."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import dolphin_omega_reviewer_ui as ui


class OfflineReviewerUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = json.loads(ui.DEFAULT_GRAPH.read_text(encoding="utf-8"))
        cls.papers = json.loads(ui.DEFAULT_PAPERS.read_text(encoding="utf-8"))
        cls.queue = json.loads(ui.DEFAULT_QUEUE.read_text(encoding="utf-8"))

    @staticmethod
    def draft():
        return {
            "record_type": "UNVERIFIED_REVIEW_DRAFT",
            "activity": "literature_review_only",
            "paper_id": "hallmarks-aging-2023",
            "role": "methodology",
            "assessment": "inconclusive",
            "reviewer_alias": "",
            "methodology_notes": "Methods and bias require independent assessment.",
            "limitations_notes": "A mechanism review cannot establish clinical immortality.",
            "contrary_findings": "Independent human outcome trials remain to be evaluated.",
            "source_read_declared": False,
            "conflict_declared": False,
            "reviewer_identity_authenticated": False,
            "source_provenance_authenticated": False,
            "scientifically_verified": False,
            "approved": False,
            "production_deployed": False
        }

    def validate(self, draft=None):
        return ui.validate_draft(self.draft() if draft is None else draft,
                                 self.papers, self.queue)

    def html(self, graph=None, papers=None, queue=None):
        return ui.render_html(self.graph if graph is None else graph,
                              self.papers if papers is None else papers,
                              self.queue if queue is None else queue)

    def test_rendered_html_has_two_papers_and_falsification(self):
        page = self.html()
        self.assertIn("Hallmarks of aging", page)
        self.assertIn("Dorsoventral-mediated Shh", page)
        self.assertIn("https://pubmed.ncbi.nlm.nih.gov/36599349/", page)
        self.assertIn("https://pubmed.ncbi.nlm.nih.gov/41642075/", page)
        self.assertIn("Would count against:", page)
        self.assertIn("Contrary-evidence question:", page)
        self.assertIn("Uncovered domains:", page)

    def test_html_includes_real_local_export(self):
        page = self.html()
        self.assertIn("new Blob(", page)
        self.assertIn("URL.createObjectURL(blob)", page)
        self.assertIn("link.download =", page)
        self.assertIn("UNVERIFIED_REVIEW_DRAFT", page)
        self.assertIn("form.addEventListener('submit'", page)

    def test_html_disallows_automatic_network_uploads(self):
        page = self.html()
        self.assertIn("connect-src 'none'", page)
        self.assertIn("form-action 'none'", page)
        self.assertNotIn("fetch(", page)
        self.assertNotIn("XMLHttpRequest", page)
        self.assertNotIn("WebSocket", page)
        self.assertNotIn('action="https:', page)

    def test_untrusted_html_escaped(self):
        papers = copy.deepcopy(self.papers)
        papers["papers"][0]["title"] = '<script>alert("x")</script>'
        page = self.html(papers=papers)
        self.assertIn("&lt;script&gt;alert(", page)
        self.assertNotIn('<script>alert("x")', page)

    def test_draft_accepted_only_as_unverified(self):
        result = self.validate()
        self.assertEqual(result["review_record_state"], "DRAFT_REQUIRES_INDEPENDENT_REVIEW")
        self.assertTrue(result["notes_structure_accepted"])
        self.assertFalse(result["scientific_claim_verified"])
        self.assertFalse(result["human_review_completed"])
        self.assertFalse(result["approved"])
        self.assertFalse(result["external_dispatch"])
        self.assertFalse(result["production_deployed"])

    def test_explicit_conflict_is_hold(self):
        d = self.draft()
        d["conflict_declared"] = True
        self.assertEqual(self.validate(d)["review_record_state"], "DECLARED_CONFLICT_HOLD")

    def test_source_read_is_untrusted_self_report(self):
        d = self.draft()
        d["source_read_declared"] = True
        result = self.validate(d)
        self.assertTrue(result["source_read_self_reported"])
        self.assertFalse(result["source_provenance_authenticated"])
        self.assertFalse(result["scientific_claim_verified"])

    def test_prohibit_forged_approval_and_identity(self):
        for field in ("reviewer_identity_authenticated", "source_provenance_authenticated",
                      "scientifically_verified", "approved", "production_deployed"):
            d = self.draft()
            d[field] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate(d)

    def test_prohibit_non_boolean_approval_flag(self):
        d = self.draft()
        d["approved"] = 0
        with self.assertRaises(ValueError):
            self.validate(d)

    def test_prohibit_external_activity(self):
        d = self.draft()
        d["activity"] = "activate_external_nodes"
        with self.assertRaises(ValueError):
            self.validate(d)

    def test_prohibit_finalized_record_type(self):
        d = self.draft()
        d["record_type"] = "APPROVED_REVIEW"
        with self.assertRaises(ValueError):
            self.validate(d)

    def test_prohibit_unexpected_field(self):
        d = self.draft()
        d["deployment_authorized"] = True
        with self.assertRaises(ValueError):
            self.validate(d)

    def test_unknown_paper_and_role(self):
        for field, value in (("paper_id", "unknown"), ("role", "admin"),
                             ("assessment", "scientifically-proven")):
            d = self.draft()
            d[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate(d)

    def test_notes_require_substantive_length(self):
        for field in ui.NOTE_FIELDS:
            for value in ("short", "", "X" * 1501):
                d = self.draft()
                d[field] = value
                with self.subTest(field=field, value=value[:10]), self.assertRaises(ValueError):
                    self.validate(d)

    def test_reject_control_char_in_notes(self):
        d = self.draft()
        d["methodology_notes"] = "Long notes text\x00injected."
        with self.assertRaises(ValueError):
            self.validate(d)

    def test_alias_length_and_control(self):
        for value in ("x" * 65, "bad\nname"):
            d = self.draft()
            d["reviewer_alias"] = value
            with self.assertRaises(ValueError):
                self.validate(d)

    def test_boolean_declarations_reject_strings(self):
        for field in ("source_read_declared", "conflict_declared"):
            d = self.draft()
            d[field] = "false"
            with self.assertRaises(ValueError):
                self.validate(d)

    def test_forged_upstream_review_queue_rejected(self):
        q = copy.deepcopy(self.queue)
        q["items"][0]["roles"][0]["status"] = "approved"
        with self.assertRaises(ValueError):
            ui.validate_draft(self.draft(), self.papers, q)

    def test_forged_graph_status_rejected(self):
        g = copy.deepcopy(self.graph)
        g["nodes"][1]["status"] = "PROVEN"
        with self.assertRaises(ValueError):
            self.html(graph=g)

    def test_deterministic_html_and_draft(self):
        self.assertEqual(self.html(), self.html())
        self.assertEqual(self.validate(), self.validate())

    def test_html_cli_offline(self):
        p = subprocess.run([sys.executable, str(Path(ui.__file__)), "--render-html"],
                           check=True, text=True, capture_output=True, timeout=10)
        self.assertIn("<!doctype html>", p.stdout)
        self.assertIn("No upload or account access occurs.", p.stdout)

    def test_invalid_cli_draft_exits_nonzero(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text('{"record_type":"APPROVED"}', encoding="utf-8")
            p = subprocess.run(
                [sys.executable, str(Path(ui.__file__)), "--validate-draft", str(path)],
                text=True, capture_output=True, timeout=10,
            )
            self.assertNotEqual(p.returncode, 0)

    def test_valid_cli_draft_never_approves(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "review.json"
            path.write_text(json.dumps(self.draft()), encoding="utf-8")
            p = subprocess.run(
                [sys.executable, str(Path(ui.__file__)), "--validate-draft", str(path)],
                text=True, capture_output=True, check=True, timeout=10,
            )
            x = json.loads(p.stdout)
            self.assertFalse(x["approved"])
            self.assertFalse(x["scientific_claim_verified"])
            self.assertFalse(x["production_deployed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
