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
