#!/usr/bin/env python3
"""Dolphin-Ω v0.7: static OFFLINE reviewer interface and draft validator.

The local HTML exports UNVERIFIED review DRAFTS only. No uploads, network
fetches, reviewer authentication, publication validation, remote execution,
science approval, or production deployment. The registered cores are untouched.
"""
import argparse
import html
import json
from pathlib import Path

from dolphin_omega_graph import DEFAULT_GRAPH, build_report
from dolphin_omega_literature import (
    DEFAULT_PAPERS, DEFAULT_QUEUE, validate_bibliography, validate_review_queue,
)

ROLES = {"methodology", "evidence_quality", "ethics"}
ASSESSMENTS = {"potentially_supports", "potentially_contradicts", "inconclusive"}
NOTE_FIELDS = ("methodology_notes", "limitations_notes", "contrary_findings")
DRAFT_KEYS = {
    "record_type", "activity", "paper_id", "role", "assessment",
    "reviewer_alias", "methodology_notes", "limitations_notes",
    "contrary_findings", "source_read_declared", "conflict_declared",
    "reviewer_identity_authenticated", "source_provenance_authenticated",
    "scientifically_verified", "approved", "production_deployed",
}


def validate_draft(draft, bibliography, queue):
    papers = validate_bibliography(bibliography)
    validate_review_queue(queue, papers)
    if not isinstance(draft, dict) or set(draft) != DRAFT_KEYS:
        raise ValueError("invalid/unrecognized draft fields")
    if draft["record_type"] != "UNVERIFIED_REVIEW_DRAFT":
        raise ValueError("review record must remain a draft")
    if draft["activity"] != "literature_review_only":
        raise ValueError("only passive literature review is allowed")
    if draft["paper_id"] not in papers:
        raise ValueError("unknown paper")
    if draft["role"] not in ROLES or draft["assessment"] not in ASSESSMENTS:
        raise ValueError("unknown role/assessment")
    alias = draft["reviewer_alias"]
    if not isinstance(alias, str) or len(alias) > 64 or any(ord(c) < 32 for c in alias):
        raise ValueError("reviewer alias must be plain text <=64 characters")
    for field in NOTE_FIELDS:
        value = draft[field]
        if not isinstance(value, str) or not 12 <= len(value.strip()) <= 1500:
            raise ValueError(field + " must have 12..1500 nonblank characters")
        if any(ord(c) < 32 and c not in "\n\t" for c in value):
            raise ValueError(field + " contains control characters")
    for field in ("source_read_declared", "conflict_declared"):
        if type(draft[field]) is not bool:
            raise ValueError(field + " must be boolean")
    for field in ("reviewer_identity_authenticated", "source_provenance_authenticated",
                  "scientifically_verified", "approved", "production_deployed"):
        if draft[field] is not False:
            raise ValueError(field + " cannot be true in an unverified draft")
    # A structured review record cannot override the v0.5 pending queue,
    # certify an individual, or cause any action regardless of wording/score.
    state = "DECLARED_CONFLICT_HOLD" if draft["conflict_declared"] else "DRAFT_REQUIRES_INDEPENDENT_REVIEW"
    return {
        "system": "Dolphin-Omega", "version": "0.7-offline-reviewer-interface",
        "paper_id": draft["paper_id"], "role": draft["role"],
        "review_record_state": state,
        "notes_structure_accepted": True,
        "source_read_self_reported": draft["source_read_declared"],
        "identity_authenticated": False, "source_provenance_authenticated": False,
        "scientific_claim_verified": False, "human_review_completed": False,
        "approved": False, "external_dispatch": False, "production_deployed": False,
    }


def render_html(graph_doc, bibliography, queue):
    report = build_report(graph_doc, bibliography, queue)
    papers = validate_bibliography(bibliography)
    esc = lambda value: html.escape(str(value), quote=True)
    sections = []
    options = []
    for chain in report["research_chains"]:
        paper = papers[chain["paper_id"]]
        options.append('<option value="' + esc(chain["paper_id"]) + '">' +
                       esc(paper["title"]) + " — " + esc(chain["domain"]) + '</option>')
        limitations = "".join("<li>" + esc(x) + "</li>" for x in paper["limitations"])
        sections.append(
            '<article class="paper">'
            '<div class="eyebrow">' + esc(chain["domain"]) + " · Awaiting independent human review</div>"
            '<h2>' + esc(paper["title"]) + '</h2>'
            '<p><strong>Bibliographic reference:</strong> ' + esc(paper["first_author"]) +
            " (" + esc(paper["year"]) + '), PMID ' + esc(paper["pmid"]) +
            ' · <a rel="noopener noreferrer" target="_blank" href="' + esc(paper["pubmed_url"]) +
            '">View PubMed record (optional external navigation)</a></p>'
            '<p><strong>Untested hypothesis:</strong> ' + esc(chain["hypothesis"]) + '</p>'
            '<p><strong>Predicted observation:</strong> ' + esc(chain["prediction"]) + '</p>'
            '<p><strong>Would count against:</strong> ' + esc(chain["would_count_against"]) + '</p>'
            '<p><strong>Appraisal criteria:</strong> ' + esc(chain["appraisal_criteria"]) + '</p>'
            '<p><strong>Contrary-evidence question:</strong> ' + esc(chain["contrary_question"]) + '</p>'
            '<p><strong>Paper limitations:</strong></p><ul>' + limitations + '</ul>'
            '<p class="notice">No claim of independently verified science, human immortality, '
            'or a completed scientific review.</p></article>'
        )
    missing = ", ".join(report["uncovered_domains"])
    # No untrusted research strings are inserted into executable JavaScript.
    # Every external URL is validated by validate_bibliography, then HTML-escaped.
    script = r"""
(function () {
  'use strict';
  const form = document.getElementById('review-form');
  const state = document.getElementById('export-status');
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    const data = new FormData(form);
    const draft = {
      record_type: 'UNVERIFIED_REVIEW_DRAFT',
      activity: 'literature_review_only',
      paper_id: String(data.get('paper_id') || ''),
      role: String(data.get('role') || ''),
      assessment: String(data.get('assessment') || ''),
      reviewer_alias: String(data.get('reviewer_alias') || '').trim(),
      methodology_notes: String(data.get('methodology_notes') || '').trim(),
      limitations_notes: String(data.get('limitations_notes') || '').trim(),
      contrary_findings: String(data.get('contrary_findings') || '').trim(),
      source_read_declared: form.elements.namedItem('source_read_declared').checked,
      conflict_declared: form.elements.namedItem('conflict_declared').checked,
      reviewer_identity_authenticated: false,
      source_provenance_authenticated: false,
      scientifically_verified: false,
      approved: false,
      production_deployed: false
    };
    if ([draft.methodology_notes, draft.limitations_notes,
         draft.contrary_findings].some(x => x.length < 12 || x.length > 1500) ||
        draft.reviewer_alias.length > 64) {
      state.textContent = 'Each notes field needs 12–1500 characters; alias maximum 64.';
      return;
    }
    const blob = new Blob([JSON.stringify(draft, null, 2) + '\n'],
                          {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'dolphin-omega-unverified-' + draft.paper_id + '.json';
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    state.textContent = 'Local JSON draft generated. Nothing was uploaded or approved.';
  });
}());
"""
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'none'; img-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<title>Dolphin-Ω v0.7 — Offline Research Review</title>
<style>
:root{color-scheme:light;font:16px/1.55 system-ui,sans-serif;background:#f4f7fa;color:#1b2738}
*{box-sizing:border-box}body{max-width:960px;margin:auto;padding:24px}
h1{font-size:2rem}h2{font-size:1.25rem}header,.paper,form{padding:22px;background:white;border:1px solid #d5dee9;border-radius:14px;margin-bottom:16px}
.notice{color:#67381c;background:#fff6e6;padding:12px;border-radius:8px}
.eyebrow{color:#3c5d89;font-size:.85rem;font-weight:700;text-transform:uppercase}
a{color:#265493}p{margin:10px 0}label{display:block;margin:14px 0 5px;font-weight:600}
input:not([type=checkbox]),select,textarea{width:100%;border:1px solid #8794a5;border-radius:7px;padding:10px;font:inherit}
textarea{min-height:90px}button{background:#1b476f;color:white;border:0;border-radius:7px;padding:12px 18px;font:inherit;cursor:pointer}
button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{outline:3px solid #adcbff}
.small{color:#4a596c;font-size:.9rem}
</style></head><body>
<header><div class="eyebrow">Dolphin-Ω · v0.7</div>
<h1>Offline scientific literature appraisal worksheet</h1>
<p>Read the research questions, record methods, limitations and contradictory evidence,
then export a <strong>local, unverified review draft</strong>. No upload or account access occurs.</p>
<p class="notice">Neither this interface nor a filled draft authenticates a reviewer,
verifies a source's scientific conclusions, grants ethics approval, or authorizes
medical experiments, external nodes or production deployment.</p>
<p class="small">Uncovered domains: """ + esc(missing) + """. Reference links leave this offline page only if you choose to open them.</p>
</header>
<section aria-label="Research plans">
""" + "\n".join(sections) + """
</section>
<form id="review-form">
<h2>Write a review draft (not an approval)</h2>
<label for="paper_id">Publication</label>
<select name="paper_id" id="paper_id" required>""" + "\n".join(options) + """</select>
<label for="role">Review focus</label>
<select name="role" id="role" required>
<option value="methodology">Methodology</option>
<option value="evidence_quality">Evidence quality</option>
<option value="ethics">Ethical limitations</option></select>
<label for="assessment">Provisional evidence assessment</label>
<select name="assessment" id="assessment" required>
<option value="inconclusive">Inconclusive</option>
<option value="potentially_supports">Potentially supports narrow claim</option>
<option value="potentially_contradicts">Potentially contradicts narrow claim</option></select>
<label for="reviewer_alias">Optional pseudonym (not authenticated)</label>
<input name="reviewer_alias" id="reviewer_alias" maxlength="64" autocomplete="off">
<label for="methodology_notes">Methods and risk-of-bias notes</label>
<textarea id="methodology_notes" name="methodology_notes" minlength="12" maxlength="1500" required></textarea>
<label for="limitations_notes">Limitations, gaps and generalizability</label>
<textarea id="limitations_notes" name="limitations_notes" minlength="12" maxlength="1500" required></textarea>
<label for="contrary_findings">Contrary evidence or missing replication</label>
<textarea id="contrary_findings" name="contrary_findings" minlength="12" maxlength="1500" required></textarea>
<label><input type="checkbox" name="source_read_declared"> I personally read the cited source (self-declaration only)</label>
<label><input type="checkbox" name="conflict_declared"> I declare a potential conflict of interest</label>
<p class="small">No professional qualifications, personal identity or source authenticity
are checked by this page. If sources were not read, leave the checkbox unchecked.</p>
<button type="submit">Export unverified JSON draft to this device</button>
<p class="small" id="export-status" role="status" aria-live="polite"></p>
</form><script>""" + script + """</script></body></html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument("--bibliography", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument("--review-queue", type=Path, default=DEFAULT_QUEUE)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--render-html", action="store_true", help="write static HTML to stdout (default)")
    group.add_argument("--validate-draft", type=Path, help="validate a manually exported draft JSON")
    args = parser.parse_args()
    try:
        bib = json.loads(args.bibliography.read_text(encoding="utf-8"))
        queue = json.loads(args.review_queue.read_text(encoding="utf-8"))
        if args.validate_draft:
            draft = json.loads(args.validate_draft.read_text(encoding="utf-8"))
            print(json.dumps(validate_draft(draft, bib, queue), indent=2,
                             ensure_ascii=False, sort_keys=True))
        else:
            graph = json.loads(args.graph.read_text(encoding="utf-8"))
            print(render_html(graph, bib, queue))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
