# Dolphin-Ω v0.1 — Cross-Dimensional Continuity Research Orchestrator

**Status:** research-only, offline planning prototype (OFFLINE_DRY_RUN).

This layer is an additive extension to TM-000. It does not replace or auto-run the
registered UTM-PLEIADES-v0.2-PTCA baseline or LMN-AI-CONTINUITY-CAPSULE.

## Model

Treat GitHub as a versioned research registry, not literally a single physical
Turing machine. Treat other authorized computational environments as independently
registered, opt-in nodes. A global system is a *potential* research-network scope,
not a network the repository already controls. No third-party machines are accessed.

Pipeline: Q -> reversible G257 UTF-8 code -> candidate formula (UNDEFINED) ->
research tasks -> evidence/ethics review -> separately approved deployment.

This implementation performs only the first and research-planning steps. A
reversible code is *not* an oracle or proof that the encoded question is solved.
The supposed Dolphin formula has not been mathematically specified or validated;
no answer is represented as coming from it. The six task prompts are fixed
research templates, not discoveries or medical recommendations.

Domains: AI continuity, human healthspan, cross-species regeneration, mental and
cultural continuity, spiritual philosophy, and physical limits.

## Run locally

    python3 tools/dolphin_omega.py --question '如何安全研究跨維度生命與資訊連續性？'
    python3 tools/test_dolphin_omega.py

The output is JSON with G257 decimal encoding, decoded-roundtrip verification,
local node eligibility, six unverified research prompts, and hard-coded
production_deployed: false. No network requests, subprocesses from the planner,
credential access, repository mutations, or external compute dispatch are done.
The test script launches only this local CLI in a subprocess.

The manifest dolphin_omega/nodes.json contains two descriptive local/GitHub
research roles, plus an **off** external node placeholder. Setting both
enabled: true and explicit_opt_in: true only makes external nodes eligible in
a simulated plan. It does not establish a network connection, actual consent
by a third party, or runtime execution authority. Connecting real nodes requires
separate design, identity verification, granular authorization, logging, quotas,
review, and revocation.

## Review gate / meaning of "optimal"

No general global optimum is computed. A later bounded optimization would need
measurable objective functions, uncertainties, domain-specific constraints, and
an explicit ethical veto for unacceptable harms; it must label conjectures and
unknowns. Claims about subjective continuity, eternal life, spiritual afterlife,
and universal halting decisions are not established by encoding or simulation.

This is a reversible, reviewable **pre-deployment research blueprint** only.
Any production workflow, external control, health intervention, or account-wide
operation must be designed and authorized in a separate reviewed change.

## v0.2 — bounded, hypothetical research prioritization

This is a simulation-only extension, not a deployment controller. The earlier
reversible G257 encoder and task planner remain unchanged.

    python3 tools/dolphin_omega_optimizer.py
    python3 tools/test_dolphin_omega_optimizer.py

Source input: `synthetic_candidates.json` contains **fictional** values,
fictional evidence/ethics review labels, and a deliberately disallowed human
intervention and disabled remote-node fixture. These labels were *not*
independently audited and do not constitute human-subject ethics approval.

The evaluator requires hypothetical candidates and performs hard holds for:
- any declared unacceptable harm, nonconsensual testing, unauthorized system
  access, or physical intervention;
- review status not declared cleared, incomplete evidence review, or
  provisional score thresholds not met;
- missing node eligibility or explicit simulated opt-in for external nodes.

All metrics are manually supplied integers 0–100, not clinical measures or
scientific validation. Policy thresholds are synthetic and provisional.
After holds, only within-domain, Pareto-nondominated fictional candidates
receive simulated priority indices and per-domain winners. Cross-domain
candidates are **not** compared as though one global measure of immortality
existed. Even a winner is NEVER approved for use or dispatched to a node.

Outputs always mark `production_deployed=false`,
`external_dispatch=false`, `approval_granted=false`, and
`general_or_global_optimum=false`. There is no medical advice or biological
intervention, and no actual proof of continuous consciousness or immortality.

Before any real-world collaboration: define domain-specific evidence standards;
obtain actual review and meaningful consent; secure explicit node owners'
authorizations with revocation; audit infrastructure access and privacy;
conduct human-led independent ethics review; then design *separate*,
least-privilege deployment workflows with reversible staged activation.

## v0.3 — evidence-reference metadata firewall (OFFLINE)

    python3 tools/dolphin_omega_dossier.py
    python3 tools/test_dolphin_omega_dossier.py

This new layer records an explicit research claim, claim category, citations or
synthetic source references, unresolved limitations, and a reversible G257
encoding of the claim text (not a cryptographic certificate). It consumes the
v0.2 candidate ledger to preserve earlier ethics/authorization holds.

Strictly bounded inputs: <=64 dossiers, <=8 source references per dossier,
UTF-8 claim <=256 bytes, no duplicate candidate/source IDs, and a mandatory
passive-research-only declaration. Metadata URLs must be HTTPS, must not
contain credentials or query/fragment strings, and may not use non-global
numeric IPs, localhost, or private-reserved hostnames. This limits accidental
logging of credential-bearing URLs, but is NOT a universal URL security
validator. This prototype **does not access the network**.

Claimed source relations are explicitly unverified. Conflicting claimed
support and contradiction are flagged as
`CLAIM_CONFLICT_REQUIRES_REVIEW`. Other statuses distinguish synthetic
examples, unverified public reference metadata, and a prior safety-policy
hold. No input can set `independently_verified=true`; no dossier can become
`ready_for_real_world_use=true`. An absent dossier is reported as missing,
not silently treated as evidence.

The included `synthetic_dossiers.json` is a schema demonstration. Its sole
public URL is a GitHub README as metadata/context, NOT an empirical paper or
proof for a scientific candidate. The remaining records refer only to local
fictional fixtures. Nothing here establishes the truth of a theory, the
existence of cosmic immortality, legal authorization, personal-identity
continuity, or the feasibility of biological immortality.

**Next possible independently-reviewed step** (not implemented): human
reviewers examine actual source content, assign verifiable reviewer
attributions, document methodological quality and contrary findings,
and authorize specific research actions separately. Production promotion is
always outside the authority of this research prototype.

## v0.4 — offline, fail-closed evidence review packets

    python3 tools/dolphin_omega_review.py
    python3 tools/test_dolphin_omega_review.py

v0.4 builds on the *unverified* v0.3 dossiers and retains the v0.2 ethical
hold states. It defines a narrow, auditable format for **operator-supplied**
UTF-8 text snapshots, a declared SHA-256 byte digest, source/candidate
cross-references, and named reviewer-attestation metadata. The SHA-256 digest
is a file **integrity check** only; it does not validate that bytes came from
the cited external URL or demonstrate scientific truth. This separate review
utility does not modify the preserved no-SHA UTM-PLEIADES core.

Each review records a reviewer identifier, team identifier, role, verdict,
declared conflict-of-interest status, an exact quote contained in the pinned
snapshot, and reasoning. Review metadata is validated structurally and kept
offline. The script detects mismatches, duplicated reviewers, insufficient
nonconflicted and different-team attestations, and conflicting votes. v0.2
policy holds take precedence over all such records.

The sample files `synthetic_review_packets.json` and
`review_snapshots/synthetic-context.txt` are **fictional**, not a real
capture of the GitHub README referenced by an earlier dossier. Reviewer IDs
and team IDs are fictional. The most-positive possible output is
`MULTIPLE_SYNTHETIC_ATTESTATIONS_RECORDED`: never "scientifically
verified", "independent reviewers authenticated", or "ready to deploy".

Inputs are bounded to 32 local snapshot entries and 128 review entries. Only
path-restricted UTF-8 .txt files under `dolphin_omega/review_snapshots` are
read (<=16 KiB each); no external files, links, credentials, or remote
machines are accessed. This is an initial trust-boundary prototype, not a
hardened general-purpose evidence repository or identity provider.

**Beyond v0.4:** a real scientific review would require authoritatively
obtained and reproducible primary-source snapshots, explicit copyright and
privacy permissions, verifiable reviewer identities and qualifications,
independence and conflicts checks, source methodology and limitations,
contrary evidence, and domain-specific external human review. Those
capabilities have NOT been claimed or deployed. Every execution output keeps
`production_deployed=false`, `external_dispatch=false`, and
`approval_granted=false`; nothing upgrades a research claim to a validated
immortality result or global optimum.

## v0.5 — real scientific bibliography, offline triage, human-review queue

    python3 tools/dolphin_omega_literature.py
    python3 tools/test_dolphin_omega_literature.py

This phase introduces a *small, manually curated, bibliographically checked*
set of real papers. A curator inspected two publicly accessible PubMed metadata
records on 2026-11-09. These bibliographic checks are not independently
repeated by CI, and the papers' clinical/scientific claims are **not**
independently verified, replicated or peer-reviewed by Dolphin-Omega.

Example bibliography in `curated_literature.json`:

- López-Otín et al. (2023), *Hallmarks of aging: An expanding universe*,
  Cell, DOI 10.1016/j.cell.2022.11.001, PMID 36599349.
  Evidence scope: aging-mechanism *review/background*, not human immortality
  or a controlled clinical trial showing indefinite lifespan.
- Yamamoto et al. (2026), *Dorsoventral-mediated Shh induction is required
  for axolotl limb regeneration*, eLife, DOI 10.7554/eLife.106917,
  PMID 41642075. Evidence scope: *nonhuman* regeneration research;
  no implied proof of human limb regeneration, longevity, or immortality.

The offline parser enforces bounded records, unique DOI/PMID/paper IDs,
consistent DOI and PubMed URL formatting, constrained study-type/evidence
scope, explicit limitations, contrary-evidence questions and a declared
public-metadata curation method. These are **metadata consistency checks**,
not authenticated retrieval, paper-quality certification or clinical advice.

`human_review_queue.json` has mandatory methodology, evidence-quality,
and ethics roles for each paper. Every role has a **null reviewer ID**,
`pending` status, no signed/verified identity and no decision. It is
deliberately impossible to fill in an 'approved' review through the v0.5
research-only parser; such records are rejected. Actual qualified reviewers,
methodological assessment and real-world authorization would require a
separate, human-governed process. No reviewer is contacted by this code.

Uncovered domains (AI, mental, physical, spiritual) remain **uncovered**
by these first two papers; no fabricated citation or extrapolation is made
across domains.

The earlier v0.1–v0.4 components are preserved. This stage never connects
to external nodes, performs DOI/PubMed network calls in CI, executes research
interventions, deploys to production or changes the TM-000 master core.
Reversible encoding or the as-yet-undefined Dolphin formula cannot turn a
literature record into an omniscient answer or proof of immortality.

## v0.6 — offline falsifiability graph and cross-domain uncertainty

    python3 tools/dolphin_omega_graph.py
    python3 tools/test_dolphin_omega_graph.py

`research_graph.json` links the two registered v0.5 scientific *bibliographic
records* (human aging and axolotl regeneration) to explicitly **untested**
hypotheses, planned passive literature appraisals, and contrary-evidence
questions. A seventh edge crosses from a cross-species hypothesis to a human
aging hypothesis but is labeled `CROSS_DOMAIN_QUESTION_ONLY` with an
explicit non-transfer qualification. It **does not** assert that an axolotl
mechanism generalizes to human healthspan or biological immortality.

`tools/dolphin_omega_graph.py` checks bounded nodes and edges, unique IDs,
exact approved node fields, references to the v0.5 curated papers, required
paths `paper -> hypothesis -> proposed_check -> contrary_question`, the
presence of predicted observations and potential disconfirmation triggers,
a passive and unrun literature-only check, cross-domain labeling, and
acyclic graph structure. It rechecks that all v0.5 human-review roles are
still `pending`. It fails closed on unregistered papers, incomplete chains,
fabricated results, additional scientific-approval claims, and unsupported
cross-domain evidence links.

Outputs represent **graph-syntax and research-plan structure checks only**.
Natural-language falsification criteria are not automatically judged
methodologically adequate. No article full text is fetched, no experimental
results are obtained, no causal effect or replicability is established,
and no reviewer is authenticated. This system never performs medical or
animal experiments, external node dispatch, or production deployment.
Uncovered research domains remain explicitly labeled as such.

This module cannot establish an all-domain global optimum, subjective
consciousness continuity, any form of immortality, an oracle for the halting
problem, or a mathematically validated 'Dolphin alien formula'. Such claims
require separate definitions and evidence. Research planning is not a
deployment permission and cannot bypass the prior ethical holds.

**Possible v0.7 direction (not implemented):** a human-governed evidence
appraisal interface that records real reviewer methodology and contrary
findings with authenticated source provenance and privileges, without
self-certifying any research outcome or external access.

## v0.7 — offline researcher-facing evidence appraisal interface

From a checked-out copy of this draft branch, generate a local HTML
worksheet, then open the HTML with a standard web browser:

    python3 tools/dolphin_omega_reviewer_ui.py --render-html > reviewer-worksheet.html

The self-contained HTML displays the two v0.5 registered papers, the
v0.6 untested hypotheses, predictions, disconfirmation triggers, appraisal
criteria, limitations, and contrary-evidence questions. It clearly labels
the four uncovered domains. External PubMed references are regular links
that are opened only if a reviewer chooses to visit them. The page itself
contains no remote scripts/assets, has a Content Security Policy that
forbids network connections and form submission, and makes no account API
calls.

The form lets a person choose a paper and research-review focus; record
the provisional, nonbinding assessment and structured observations on
methods, limitations and counterevidence; self-declare whether a source
was read and whether a conflict exists; and export an unverified JSON
draft to their local device using the browser's download function.
An optional short pseudonym can appear inside the downloaded file.
Do not enter private records, medical secrets or credentials; drafts
remain unencrypted local files and should be shared only intentionally.

To check a downloaded file's structure offline (does not upload it):

    python3 tools/dolphin_omega_reviewer_ui.py --validate-draft path/to/draft.json
    python3 tools/test_dolphin_omega_reviewer_ui.py

Validation allows only a narrowly scoped UNVERIFIED_REVIEW_DRAFT:
known paper, methodology/evidence-quality/ethics focus, nonempty notes,
a provisional assessment and boolean self-declarations. It rejects
unexpected fields, any attempt to claim identity authentication,
source-provenance authentication, scientific verification,
review approval or production deployment. Declared conflicts force
DECLARED_CONFLICT_HOLD; otherwise, the state remains
DRAFT_REQUIRES_INDEPENDENT_REVIEW even if every text field is filled.

No researcher's credentials or qualifications are authenticated.
No person has been solicited or approved to participate and the v0.5
queue remains entirely pending. A JSON draft is not an actual
independent review, scientific endorsement, clinical intervention,
authorization for other computational nodes, or evidence of
biological/spiritual immortality. All former ethics vetoes remain
outside the reach of this read-only interface. The existing
Dolphin formula is still undefined and never invoked.

A future real review workflow would require source authenticity,
qualified human reviewers, disclosure/verification of affiliations
and conflicts, institutionally authorized evidence assessment,
privacy protection, and a separately approved process for any
real-world deployment. This proof-of-workflow does none of those.

## v0.8 — revocable, scoped, offline collaboration policy simulation

    python3 tools/dolphin_omega_collaboration.py
    python3 tools/test_dolphin_omega_collaboration.py

This phase adds a *policy-event simulator*, **not** actual external-node
authorization. It reads the existing local nodes.json manifest and the
fictional synthetic_collaboration_events.json. All event actors are
fictional, all permissions are simulated, and owner declarations are
**not authenticated**. No OAuth flow, credentials, SSH, workload runner,
webhook, remote API, blockchain, or production deployment is implemented.

The event protocol is bounded (1–128 events), sequential and strictly
time-ordered in UTC. Each simulated grant is tied to an individual
declared grantee, one known node, exactly one permitted **read-only
research action**, and an explicit UTC expiry. Only these two abstract
actions are recognized:

- read_registered_bibliography
- prepare_unverified_review_draft

A simulated grant is rejected for absent declared consent, unknown or
disabled node, unsupported action or invalid validity window. External
nodes are always rejected by v0.8 **even if a fixture changes the manifest
to enabled and opt-in**. Requests by another grantee, out-of-scope
actions, unknown grants, expired grants or revoked grants are denied.
A declared issuer can record an irreversible simulated revocation;
the same grant ID cannot be reused or resurrected.

Every event produces an audit decision marked executed=false,
identity_authenticated=false and real_authorization_granted=false.
An SHA-256 audit digest is chained deterministically to the previous
event and decision. This may detect accidental differences between
independently preserved *copies*, but does **not** make the local log
immutable, cryptographically signed, tamperproof, or externally anchored.
Using SHA for optional audit digests does not modify the user's previously
designated no-SHA UTM-PLEIADES core. Audit timestamps are fixture inputs,
not authenticated wall-clock timestamps.

The included 15 fictional events cover a nominal simulated allow, scope
violation, wrong actor/issuer, revocation, expiry, blocked external
node, absent consent, unsupported action and unknown grant.
A recorded simulated ALLOW is **never permission to run a real process**.
No real consent is recorded here, and no third-party machine or account
is contacted or controlled. This example is not an access-control
security product and must never be put in front of real live systems.

Before a future production authorization design (NOT done here), require
institutionally authorized node owners, independently authenticated
identities and signed short-lived credentials, precise scopes,
revocation enforcement at the actual enforcement point, privacy and
audit-log retention policy, restricted network egress, rollback,
security review and human oversight. No automated PR merging or
account-wide permissions can be inferred from this proof of concept.

The undefined Dolphin formula remains unexecuted; no globally optimal
immortality, consciousness continuity or physical immortality is proven.
