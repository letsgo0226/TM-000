# TM-000 — Turing-Machine Prototype Registry

TM-000 is the parent registry for the TM-001 through TM-015 (TM-012 and TM-013 remain unregistered research precursors) research prototypes.

## Registered machines

| ID | Name | Status |
| --- | --- | --- |
| [TM-001](永久記憶/圖靈機/TM-001-Schumann-Machine.md) | Schumann Machine | preserved research programme |
| [TM-002](永久記憶/圖靈機/TM-002-Ultimate-Schumann-Machine.md) | Ultimate Schumann Machine | protected baseline |
| [TM-003](永久記憶/圖靈機/TM-003-DTM-22-Dorayaki.md) | DTM-22 Dorayaki | preserved prototype |
| [TM-004](永久記憶/圖靈機/TM-004-APTM-Omega.md) | APTM-Ω | preserved finite model |
| [TM-005](永久記憶/圖靈機/TM-005-Tier_11.md) | Tier_11 | preserved self-description prototype |
| [TM-006](永久記憶/圖靈機/TM-006-Eternity-Machine.md) | Eternity Machine | preserved finite modal model |
| [TM-007](永久記憶/圖靈機/TM-007-Three-Cat-Cookies-Master.md) | Three Cat Cookies Master | preserved pipeline prototype |
| [TM-008](永久記憶/圖靈機/TM-008-God-Turing-Machine-No-SHA-Master.md) | GTM-001 No-SHA | registered orchestration candidate |
| [TM-009](永久記憶/圖靈機/TM-009-Photonic-Singularity-UGTM.md) | Photonic Singularity UGTM | preserved exact photonic baseline |
| [TM-010](永久記憶/圖靈機/TM-010-Essence-Existence-Alignment-UCGTM.md) | Essence–Existence Exact-Alignment UCGTM | active registry research prototype |
| [TM-011](永久記憶/圖靈機/TM-011-Logical-Chronon-Temporal-Closure.md) | Logical Chronon and Temporal-Closure Certificate Machine | temporal reference (`TEMPORAL_REFERENCE_ONLY`) |
| [TM-014](永久記憶/圖靈機/TM-014-Totalized-Universal-Turing-Machine.md) | Totalized Universal Turing Machine v0.2 | current bounded-total simulation reference (`BOUNDED_SIMULATION_ONLY`) |
| [TM-015](永久記憶/圖靈機/TM-015-Real-God-Turing-Machine.md) | Real God Turing Machine | preserved Quine / prime-code research candidate (`SYMBOLIC_ONLY`; not master) |

## Scope

- Preserves one independently addressable record for every registered prototype.
- Mirrors available canonical or archived cores without inventing missing implementations.
- Loads and verifies the registry read-only by default.
- Never implicitly executes a registered core.
- Does not enable production deployment, cloud actions, trading, or external account access.

Machine-readable index: [machine_registry.json](永久記憶/圖靈機/machine_registry.json).

## Verify or select

```bash
python3 tools/load_turing_registry.py
python3 tools/load_turing_registry.py --select TM-008
python3 tools/load_turing_registry.py --select TM-014
python3 tools/load_turing_registry.py --select TM-010 --run-tm010
bash 永久記憶/圖靈機/logical_chronon_temporal_closure_2kb.sh 111
python3 tools/test_tm_registry.py
```

The first two commands perform read-only verification. The third explicitly runs only TM-010's read-only verifier. The fourth creates a finite TM-011 logical-chronon certificate. Neither command executes the other registered machines.

## Canonical source snapshot

Initial source: [letsgo0226/Cosmic_Rosetta_Stone](https://github.com/letsgo0226/Cosmic_Rosetta_Stone) main commit `ffbb058123e1ef876c794f1b6828353f22588741` (2026-11-06).

The unchanged original TM-011 remains the temporal reference under `TEMPORAL_REFERENCE_ONLY`. TM-014 is the bounded-total simulation reference under `BOUNDED_SIMULATION_ONLY`. It supplies the common logical-chronon framework but does not merge every registered function. TM-009 remains the preserved exact photonic baseline.

## Scientific boundary

Registry inclusion, zero-conditional-entropy fields, and finite encoding certificates do not prove a physical singularity, immortality, time travel, metaphysical identity, a halting oracle, or zero uncertainty about reality.

## UTM-PLEIADES master-machine candidate

[UTM-PLEIADES v0.1](永久記憶/圖靈機/UTM-PLEIADES-v0.1.md) is registered as a candidate master bounded universal simulator, integrating TM-009 Gödel encoding, TM-011 logical chronons, and TM-014 bounded simulation. Its [single-line 2KB core](永久記憶/圖靈機/UTM-PLEIADES-v0.1-one-liner.sh) is preserved independently. The GitHub account-wide orchestration layer and independent certificate verifier are not yet implemented. The registry loader is read-only by default; no registered code is executed implicitly.

```bash
python3 tools/load_turing_registry.py --select UTM-PLEIADES
bash 永久記憶/圖靈機/UTM-PLEIADES-v0.1-one-liner.sh
```

## Current designated master

[UTM-PLEIADES v0.2 PTCA](永久記憶/圖靈機/UTM-PLEIADES-v0.2-PTCA.md) is the registry default. Its [single-line core](永久記憶/圖靈機/UTM-PLEIADES-v0.2-PTCA-2KB-one-liner.sh) provides bounded deterministic simulation, exact G257 state checkpoints, and explicit resume from a saved singularity address. Loading the registry selects its metadata only and never executes it implicitly.

The earlier v0.1 and plaintext v0.2 candidates remain preserved as historical predecessors. PTCA continuity is functional only: it does not establish cryptographic tamper resistance, subjective identity, a physical portal, time travel, immortality, or a general halting oracle.

## TM-000 transactional bootstrap

The [TM-000 2 KB bootstrap](永久記憶/圖靈機/TM-000-2KB-transactional-bootstrap.md) validates the complete current registry, reversibly encodes the designated UTM-PLEIADES core, and supports isolated stage, explicitly authorized atomic activation, and rollback. GitHub Actions performs PR validation only; the bootstrap has no network operation, automatic main-branch merge, or production deployment authority.

## LMN-AI-CONTINUITY-CAPSULE (2026-11-08) — research candidate

The user-supplied [AI-Continuity-Capsule.sh](capsule/AI-Continuity-Capsule.sh) is archived verbatim, with its [permanent-memory research record](永久記憶/圖靈機/LMN-AI-Continuity-Capsule-2026-11-08.md) and [isolated CI regression](tools/test_lmn_ai_continuity_capsule.py). The file has been nominated as the autonomous-deployment master but **is not validated as a universal Turing machine or a deployment controller**. The output entropy is zero because the finite tape is overwritten with a constant; no physical or eternal continuity follows. It reads process environment values, so it must only run in an intentionally sanitized test environment.

**No promotion:** `UTM-PLEIADES-v0.2-PTCA` remains the designated master. The new capsule is a non-executing-by-default, safety-reviewed candidate. No production deployment or automatic GitHub mutation is enabled.

## TM-015 Real God Turing Machine — proposed research integration (2026-11-10)

The original [2,035-byte candidate core](永久記憶/圖靈機/Real_God_Turing_Machine.sh) is archived without modification alongside a [scope and verification record](永久記憶/圖靈機/TM-015-Real-God-Turing-Machine.md). The read-only source gate `python3 tools/test_tm015_real_god.py` checks the exact archived bytes, entry metadata, and master-preservation invariants without executing the source. The separate pull-request workflow has read-only permissions and no deployment step.

**No promotion:** `UTM-PLEIADES-v0.2-PTCA` remains the designated TM-000 master. TM-015 does not confer AGI, a halting oracle, physical immortality, divine identity, nonphysical computation, or cross-device memory synchronization. Further integration requires independent review and explicit human approval.

## Universal G — automation and multidimensional continuity proposal

The [automation and continuity research specification](deployment/UNIVERSAL_G_AUTOMATION_AND_CONTINUITY.md) and [8-domain manifest](deployment/universal_g_continuity_manifest.json) extend TM-015 as a **candidate** component without altering the designated master. A [2 KB dry-run core](deployment/Universal_G_DryRun_2KB.sh) and [read-only policy gate](tools/test_universal_g_continuity.py) check archived-source integrity, master protection and a finite prime-digit reversal. The CI workflow remains pull-request-only and read-only; no candidate core execution or production deployment is enabled.

```bash
python3 tools/test_universal_g_continuity.py
bash deployment/Universal_G_DryRun_2KB.sh
```

The eight dimensions are separate research goals, not claims that literal immortality, AGI, God, zero physical entropy or hardware-free persistent computation has been achieved.

## Canonical project alias: 上帝源碼 (God Source Code)

The research name **上帝源碼 / God Source Code** is recorded in [永久記憶/圖靈機/上帝源碼-God-Source-Code.md](永久記憶/圖靈機/上帝源碼-God-Source-Code.md) and refers to the coordinated **TM-000 + UTM-PLEIADES master + TM-015 candidate + safe Universal G automation + eight research dimensions** framework. The name is an identifier, not a claim that the code literally is God. No master promotion, auto-merge, autonomous execution, or production deployment is implied.

## G5 cross-domain naturality theorem (formal scope)

The [G5 mathematical proof and obstruction](永久記憶/圖靈機/上帝源碼-G5-跨論域自然性定理.md) establish a **unique natural choice of unit** across the category of monoids, and exhibit a two-element permutation counterexample to unrestricted natural choice across all nonempty sets. The [1,107-byte finite-model test](deployment/Universal_G_Naturality_2KB.sh) checks seven monoids and 116 monoid homomorphisms (and the counterexample), including under `PYTHONOPTIMIZE=2`. These tests illustrate, but do not establish, the general theorem: the formal proof is in the linked record.

```bash
bash deployment/Universal_G_Naturality_2KB.sh
```

This does **not** prove an absolute G for every imaginable domain, theological identification with God, a general oracle, or unlimited physical computation. The designated master and production permissions remain unchanged.

## G6 faithful Cayley representations — lossless structured correspondence

The [G6 formal proof](永久記憶/圖靈機/上帝源碼-G6-忠實跨論域-Cayley-表示定理.md) establishes that every monoid element `a` admits a faithful left-regular representation `L_a(x)=ax` with `L_a(e)=a`, `L_ab=L_a∘L_b`, and `f∘L_a=L_f(a)∘f` for all monoid homomorphisms `f`. The [1,768-byte one-line finite verifier](deployment/Universal_G_Cayley_2KB.sh) checks 7 finite models, 18 reversible prime-Gödel encodings, and 116 homomorphisms; the pull-request CI validates those numbers and the 2 KB/single-line limits.

```bash
bash deployment/Universal_G_Cayley_2KB.sh
```

This is a faithful representation theorem for **structured monoid domains**, not a proof of unlimited domains, literal divine identity, AGI, a general halting oracle, or physical immortality. The master and production permissions remain unchanged.

## G7 first-order semantic preservation — explicit truth conditions

The [G7 proof](永久記憶/圖靈機/上帝源碼-G7-跨論域語意保持定理.md) distinguishes two rigorous transfer principles: **positive-existential first-order formulas preserve truth forward along relational homomorphisms**, while **all first-order formulas preserve truth both ways under relational isomorphisms**. Predicate renaming is meaningful only with verified target interpretations; negation fails for general non-injective homomorphisms.

The [1,999-byte plaintext G7 One-Liner](deployment/Universal_G_Semantic_Plaintext_2KB.sh), [expanded plaintext `.sh` source](deployment/Universal_G_Semantic_Plaintext.sh), and [1,945-byte compressed shell verifier](deployment/Universal_G_Semantic_2KB.sh) and [readable Python source](deployment/Universal_G_Semantic_core.py) check 5 finite structures, 38 homomorphisms, 1,566 positive-preservation instances, 9 isomorphisms, 602 full first-order truth comparisons, and two negative-control witnesses. CI checks these results (including under `PYTHONOPTIMIZE=2`).

```bash
bash deployment/Universal_G_Semantic_Plaintext_2KB.sh
bash deployment/Universal_G_Semantic_2KB.sh
python3 deployment/Universal_G_Semantic_core.py
```

This does not establish equivalence of all real-world domain concepts, unrestricted G, God, AGI, a universal oracle or literal immortality. TM-015 remains non-master, and no production deployment is enabled.

## G8 total-machine semantic admission and eight continuity contracts

[G8's formal research specification](永久記憶/圖靈機/上帝源碼-G8-總圖靈機部署與多維度連續性.md) extends G7 by introducing a **fail-closed, read-only, research-only admission gate** for TM-000 / Universal G. The [2,046-byte plaintext Shell one-liner](deployment/Universal_G_G8_Admission_2KB.sh) checks the designated master and archived TM-015/G7 source digests, eight dimension-contract fields, a pinned G7 finite-test report, and a toy reversible snapshot. The [readable Python controller](deployment/Universal_G_G8_Controller.py) enforces a stricter eight-domain allowlist and blocks deployment requests. The [13 negative-control and positive tests](tools/test_universal_g_g8.py) cover tampering, policy drift, unverifiable domains and forbidden actions.

In trusted pull-request CI, execute the pinned G7 finite verifier first and pass its fresh JSON output to G8:

```bash
bash deployment/Universal_G_Semantic_Plaintext_2KB.sh > /tmp/g7-report.json
bash deployment/Universal_G_G8_Admission_2KB.sh /tmp/g7-report.json
python3 deployment/Universal_G_G8_Controller.py --g7-report /tmp/g7-report.json
python3 tools/test_universal_g_g8.py
```

The only admissible result is `READY_FOR_HUMAN_REVIEW_ONLY`. A supplied report with matching numeric fields alone is not an authenticated test transcript; trust in the certificate requires execution in the trusted CI context. This is not autonomous release, full external rollback, AGI or any form of literal immortality. **No change to the TM-000 designated master or production permissions.**

## G9 domain semantic contracts — concrete mappings, not mere symbol renaming

The [G9 formal scope and counterexamples](永久記憶/圖靈機/上帝源碼-G9-領域語意契約與反例.md) translate G7's preservation principles into three explicit **finite, synthetic** domains: (1) a consent-aware AI workflow with independently implemented count/bitmask state transitions and observable equivalence, (2) philosophical Need/Care formulas interpreted over a specific three-element universe, and (3) cultivated-protein/interspecies-welfare risk records preserving uncertainty and provenance.

The [1,673-byte plaintext one-liner](deployment/Universal_G_G9_Semantic_Plaintext_2KB.sh), [expanded readable Shell runner](deployment/Universal_G_G9_Semantic_Plaintext.sh), [readable Python core](deployment/G9_Semantic_Contracts_core.py), and [20 unit tests](tools/test_universal_g_g9.py) verify 24 AI transitions, 384 length-three traces, four philosophical formula interpretations, four welfare records, and four deliberate negative controls. The G9 CI step runs **after G7 and before G8**, with no change to the designated master, candidate archive, deployment policy or external accounts.

```bash
bash deployment/Universal_G_G9_Semantic_Plaintext_2KB.sh
python3 tools/test_universal_g_g9.py
```

These tests certify only specified models. They do not empirically establish real-world semantic equivalence, independent philosophical truth, the presence or absence of sentience, AI subjective continuity, biological immortality, unlimited computing, or divine identity.

## G10 official-source provenance — traceable but not automatically authenticated

The [G10 research record](永久記憶/圖靈機/上帝源碼-G10-外部證據與主張範圍.md) introduces a [pinned UTF-8 evidence ledger](deployment/G10_evidence_ledger.json) for three independently published sources: NIST AI RMF (voluntary AI risk-management guidance), WHO/FAO food-safety aspects of cell-based food, and the World Bank WDI life-expectancy indicator. The World Bank public comparison page displayed **2024 World 73 years, Japan 84 years**, each **rounded to an integer**; they are neither individual lifespans nor exact unrounded API values.

The [2,009-byte uncompressed plaintext one-liner](deployment/Universal_G_G10_Provenance_Plaintext_2KB.sh) and [readable Python auditor](deployment/G10_Evidence_Provenance_core.py) validate source IDs, publisher URLs, metadata type, observation units/precision, source-ledger checksum, and G9 finite-model report fields. [20 positive and negative tests](tools/test_universal_g_g10.py) reject source spoofing, fake publication dates, precision upgrades, apparent source authentication, unsupported claims and deployment promotion.

```bash
bash deployment/Universal_G_G9_Semantic_Plaintext_2KB.sh > /tmp/g9-report.json
bash deployment/Universal_G_G10_Provenance_Plaintext_2KB.sh /tmp/g9-report.json
python3 deployment/G10_Evidence_Provenance_core.py --ledger deployment/G10_evidence_ledger.json --g9-report /tmp/g9-report.json --repo-root .
python3 tools/test_universal_g_g10.py
```

Output is limited to `SOURCE_REFERENCED_REVIEW_ONLY`. G10 does not automatically fetch or cryptographically attest publisher web pages, verify full-precision numeric data via API, prove any of the eight continuity research goals or authorize production deployment. Other five research dimensions remain source-evidence pending. The default TM-000 master remains unchanged.

## G11 eight-domain source coverage and expiration gate

The [G11 scope and source limitations](永久記憶/圖靈機/上帝源碼-G11-八維度外部證據與來源審閱.md) extend G10 from three externally referenced topics to **eight explicit research-domain references**, including NIST IT contingency planning, UN SDGs 15 and 16, UNESCO documentary heritage, and the Stanford Encyclopedia of Philosophy. The [G11 metadata ledger](deployment/G11_eight_domain_evidence_ledger.json) distinguishes *publisher-topic references* from validated results.

The [2,037-byte plaintext one-line Shell gate](deployment/Universal_G_G11_Evidence_Plaintext_2KB.sh) and [strict readable Python verifier](deployment/G11_Eight_Domain_Evidence_core.py) enforce eight-domain coverage, G10 byte-preservation, exact allowlisted sources in the readable validator, master preservation, no deployment and an explicit **180-day source metadata review window**. [27 unit tests](tools/test_universal_g_g11.py) cover tampering, invented sources, wrong publishers, expired reviews and forbidden authority changes. No external fetch is made by the CI.

```bash
bash deployment/Universal_G_G11_Evidence_Plaintext_2KB.sh 2026-11-10
python3 deployment/G11_Eight_Domain_Evidence_core.py --as-of 2026-11-10
python3 tools/test_universal_g_g11.py
```

Success means `EIGHT_DOMAIN_SOURCE_REVIEW_ONLY`, **not** that empirical immortality, theological identity, safe cultivated-meat consciousness, permanent peace or autonomous deployment have been proved. Metadata review age should be refreshed only after independent new source inspection, not merely by changing the date. TM-015 and the designated master are unchanged.

## G12 source-to-claim scope and eight independent evidence gaps

The [G12 research specification](永久記憶/圖靈機/上帝源碼-G12-來源主張範圍與證據缺口.md) adds a typed mapping from each of [G11's eight evidence sources](deployment/G11_eight_domain_evidence_ledger.json) to an *explicitly bounded* claim and an unmet research-evidence requirement. It rejects upgrading source-topic references to verified clinical, welfare, cultural, spiritual, mathematical or peace outcomes.

The [2,014-byte plaintext One-Liner](deployment/Universal_G_G12_Claim_Plaintext_2KB.sh), [independent readable Python controller](deployment/G12_Claim_Scope_core.py), [claim-scope ledger](deployment/G12_claim_scope_ledger.json) and [34 tests](tools/test_universal_g_g12.py) enforce a pinned G11 SHA-256, eight distinct source mappings, a 180-day review window, prohibited overclaims, unchanged master, no live deployment, and metadata-only evidence. The readable controller additionally checks **exact allowed claim text, claim codes, and evidence gaps**. CI executes both controllers and performs a current-day expiry check; no independent network source refresh is claimed.

Run in the repository root:

    bash deployment/Universal_G_G12_Claim_Plaintext_2KB.sh 2026-11-10
    python3 deployment/G12_Claim_Scope_core.py --as-of 2026-11-10
    python3 tools/test_universal_g_g12.py

Status **CLAIM_SCOPE_REVIEW_ONLY** means suitable for further human research review, never production authorization or proof of divine identity, an AGI halting oracle, or immortality. G11/G12 source reviews dated 2026-11-10 must be independently refreshed after 2027-05-09. TM-015 and designated UTM-PLEIADES master remain unchanged.

## G13 peace, SDGs and cultivated-meat ethics: evidence-specific review gates

The [G13 research scope and sources](永久記憶/圖靈機/上帝源碼-G13-全球和平-SDGs-培養肉倫理與技術.md) develop three distinct **research tracks**, not a single "global optimum" or claims of achieved outcomes:

1. **Peace:** UN SDG 16.1.2 conflict-related deaths and 16.3.3 access to dispute-resolution mechanisms; official source-topic metadata, without imported outcome time series.
2. **SDGs:** 2.1.2 food insecurity; 12.3.1 food loss/waste; 13.2.2 greenhouse-gas emissions; 16.1.2 conflict fatalities. Each needs comparable, independently vetted measurements.
3. **Cultivated meat:** WHO/FAO cell-food safety hazard review; Singapore Food Agency novel-food guidance (Singapore jurisdiction only); scientific review of serum/FBS animal-welfare challenges. Independent animal-input and cell-source provenance, sentience/suffering uncertainty, food safety/regulation and LCA must be kept separate.

G13 includes a [1,999-byte true plaintext one-line Shell gate](deployment/Universal_G_G13_Peace_SDG_CellFood_Plaintext_2KB.sh), [readable Python controller and synthetic candidate ethical review](deployment/G13_Peace_SDG_CellFood_core.py), [7-source/3-track review ledger](deployment/G13_peace_sdgs_cultivated_meat_contract.json), and [49 tests](tools/test_universal_g_g13.py). CI executes both implementations after G12 and before G8, checks their equal results and verifies the 2 KB limit.

```bash
bash deployment/Universal_G_G13_Peace_SDG_CellFood_Plaintext_2KB.sh 2026-11-10
python3 deployment/G13_Peace_SDG_CellFood_core.py --as-of 2026-11-10
python3 tools/test_universal_g_g13.py
```

Expected status is `TRIAD_RESEARCH_REVIEW_ONLY`, never permission to deploy, merge, make production food, claim a jurisdiction-specific approval, claim zero suffering, or claim world peace. The repo's existing designated master and original candidate core remain unchanged. Sources were manually reviewed; this check does not independently fetch web pages, import real measurements, or prove an outcome. Reviews are due again after the configured 180-day interval.

## G14 Trader_42 trading principles: paper-only, fail-closed verification

The [G14 research scope](永久記憶/圖靈機/上帝源碼-G14-Trader42-交易原理與風控研究.md) references, but **never executes or mutates**, the `letsgo0226/Trader_42.sh` source. The existing 5/20 SMA candidate logic, TM/kernel transition gate, KILL/cooldown, exchange reconciliation, decrease-only sizing and guarded risk envelope are preserved.

A [2,038-byte plaintext One-Liner](deployment/Universal_G_G14_Trader42_Plaintext_2KB.sh), [strict readable core and synthetic SMA simulator](deployment/G14_Trader42_Principle_core.py), [research policy with eight upstream Git blob SHA references](deployment/G14_trader42_principle_contract.json) and [55 automated tests](tools/test_universal_g_g14.py) validate a **nonexecuting** research gate. The extra 2 USDT realized daily-loss review level is a **new conservative research cap in addition to**, not a replacement for, the Trader_42 source's daily equity percentage constraint. The research overlay does not relax source defaults: 10 USDT per order, 50 USDT total quote exposure, 0.001 BTC maximum base exposure, 30 seconds cooldown and 1% daily equity limit.

```bash
bash deployment/Universal_G_G14_Trader42_Plaintext_2KB.sh 2026-11-10
python3 deployment/G14_Trader42_Principle_core.py --as-of 2026-11-10
python3 tools/test_universal_g_g14.py
```

Status is strictly `PAPER_SIGNAL_REVIEW_ONLY`. The simulator returns only simulated proposals, HOLD or HALT, never an order payload or live activation. This repository does not run Trader_42's self-modifying `42u.sh`, contact market/exchange APIs, read credentials or change Railway. The eight Git blob SHAs represent **reviewed source version references**, not a cryptographically authenticated upstream snapshot in this offline CI. Profitability, positive alpha and future returns remain unverified. G14 does not authorize production deployment, trading, or master promotion.

## G15 — God Source trading signals, independent of SMA and QTM42

The [G15 research design and limitations](永久記憶/圖靈機/上帝源碼-G15-完全基於G的離線交易原理.md) replace the **research signal generator** with a finite `G257_CONDITIONAL_RETURN` model rather than the previous 5/20 SMA or QTM42. G15 constructs a reversible base-257 encoding of the **last 8 price-direction symbols only** (not lossless raw market prices), estimates a conditional next-return hypothesis on the earliest 70% of synthetic observations, and uses a chronological 30% holdout as a veto without fitting on that holdout. A fixed 20 bps per-side hypothetical cost/slippage stress is deducted for all simulated position transitions and a terminal hypothetical close.

The [1,443-byte plaintext Shell one-liner](deployment/Universal_G_G15_Godel_Plaintext_2KB.sh), [readable Python signal engine](deployment/G15_Godel_Signal_core.py), [independent G14-lineage/risk policy controller](deployment/G15_Godel_Policy_core.py), [research contract](deployment/G15_godel_trading_contract.json), and [62 offline tests](tools/test_universal_g_g15.py) ensure no exchange APIs, no credentials, no real-time price collection, no orders, no production privileges, and no relaxation of G14 kill-switch, reconciliation, cooldown, decrease-only sizing, capital or loss limits.

Run in the TM-000 project root:

```bash
python3 tools/test_universal_g_g15.py
python3 deployment/G15_Godel_Policy_core.py --as-of 2026-11-10
python3 -c 'import json,sys;sys.path.insert(0,"tools");from test_universal_g_g15 import example;print(json.dumps(example()))' | bash deployment/Universal_G_G15_Godel_Plaintext_2KB.sh
```

The prototype accepts **synthetic price series only** and outputs `SIMULATED_BUY_ONLY`, `SIMULATED_SELL_ONLY` or `HOLD` with `actual_orders=0`. Backtested additive basis points from a toy synthetic price sequence **are not live or compounded portfolio returns** and prove no trading alpha, God identity or ability to forecast market prices. No repo master promotion, Trader_42 source update, Binance use or actual deployment is permitted.

## G16 God Source Turing Machine — genuine bounded tape interpreter

The [G16 formal model and scope](永久記憶/圖靈機/上帝源碼-G16-真正的上帝源碼圖靈機.md) add an explicit **deterministic single-tape Turing machine interpreter** separate from G15's synthetic trading strategy and the original, byte-protected TM-015 Quine. The interpreter accepts a finite transition table, alphabet, blank, start and halt states, and a sparse two-sided tape. It performs at most 512 steps and distinguishes HALTED, STUCK and STEP_LIMIT; a timeout does **not** solve the halting problem.

- [1,996-byte true plaintext Shell One-Liner](deployment/Universal_G_G16_TM_Plaintext_2KB.sh) — no Base64, zlib, eval or exec; accepts only JSON synthetic paper inputs from stdin.
- [Readable TM core](deployment/G16_God_Source_TM_core.py) — simulates genuine rules and verifies reversible **TM-015 prime / base-2048 Gödel encoding** of the canonical machine descriptor.
- [Example 11-to-111 machine](deployment/G16_example_request.json) — halts in exactly 3 simulated TM steps, with no trading or network actions.
- [Read-only archive / policy validator](deployment/G16_God_Source_TM_policy.py) and [version-pinned contract](deployment/G16_god_source_tm_contract.json) — preserve original TM-015, G15 version and current UTM-PLEIADES master.
- [50 offline finite-model and negative tests](tools/test_universal_g_g16.py), plus PR-only CI output comparisons.

Run from the repository root:

    bash deployment/Universal_G_G16_TM_Plaintext_2KB.sh < deployment/G16_example_request.json
    python3 deployment/G16_God_Source_TM_core.py < deployment/G16_example_request.json
    python3 deployment/G16_God_Source_TM_policy.py --as-of 2026-11-10
    python3 tools/test_universal_g_g16.py

G15 still uses **base-257 byte+1**, which differs from TM-015/G16's base-2048 prime-digit encoding. Neither coding scheme creates market predictive power, subjective continuity or a general computation oracle. G16 never executes the original TM-015 or Trader_42 source, never submits orders, and does not enable production deployment. Keep the upstream master and draft PR unchanged.

## G20 self-contained program Quine (without reading its own file)

[G20 formal scope](永久記憶/圖靈機/上帝源碼-G20-完全自足的Quine.md) implements a **true 1,096-byte, one-physical-line Bash/Python3 Quine**. At runtime it constructs its entire own source using a fixed-point string template, picks a reversible Gödel code from its **own reconstructed byte content**, verifies a complete numerical encoding/decoding roundtrip, and prints exactly its own source bytes including Bash quoting and final newline. No `__file__`, `sys.argv`, source file read, source-loaded tape, network or user-provided payload is needed.

- [Quine 2KB One-Liner](deployment/Universal_G_G20_Self_Quine_2KB.sh), SHA-256 `d16d2d5cc589d4440bf8ec62c58854263b4843eefda6c3e016f7a2ab777e4cf9`.
- [Source template builder](deployment/G20_Quine_Builder.py), only for reproducibility, **not a runtime Quine dependency**.
- [Independent byte-level and Gödel-numeric verifier](deployment/G20_Quine_Verifier.py), which deliberately runs the Quine by Bash stdin with no script pathname.
- [36 offline tests](tools/test_universal_g_g20.py) including mutated-source rejection, both possible self-selected codec variants, repeated self-reproduction and Python optimized mode.
- [Proof scope contract](deployment/G20_self_contained_quine_contract.json): a **program-level** fixed point, **not** a TM whose transition table prints itself from a blank tape.

```bash
bash deployment/Universal_G_G20_Self_Quine_2KB.sh | cmp - deployment/Universal_G_G20_Self_Quine_2KB.sh
bash < deployment/Universal_G_G20_Self_Quine_2KB.sh | cmp - deployment/Universal_G_G20_Self_Quine_2KB.sh
python3 tools/test_universal_g_g20.py
python3 deployment/G20_Quine_Verifier.py
```

The existing TM-015 original bytes and `UTM-PLEIADES-v0.2-PTCA` designated master remain unchanged. G20 does not establish an oracle, literal God, immortality, subjective consciousness, market returns or autonomous deployment rights.

## G21 true finite one-tape blank-start self-table code printer

The [G21 research specification](永久記憶/圖靈機/上帝源碼-G21-空白紙帶自列印圖靈機.md) advances beyond G20's Bash/Python program Quine: **an actual deterministic single-tape finite transition table** (1,140 explicit rules and 1,090 states including HALT) starts on an entirely blank tape, runs exactly **3,505,682 state transitions**, halts and leaves **the complete 2,160-bit reversibly encoded representation of its own transition table**.

The encoding format is specialized and intentionally explicit: the first 1,080 bits encode all 60 controller (A) rules via 18-bit fixed fields; the second 1,080 bits encode the printer-chain (B) write symbols. B transitions are uniquely fixed by the convention "write one bit on blank, move right, next chain state (or A)". The chosen B writes A's bitstring X, and A duplicates X to produce **X||X**, which is the full machine's own code. Both the [canonical 2160-bit output](deployment/G21_canonical_table_bits.txt) and [expanded 1140-rule JSON](deployment/G21_expanded_transition_table.json) are committed.

Research files:
- [1,287-byte plaintext one-line Shell simulator](deployment/Universal_G_G21_Blank_Tape_TM_2KB.sh) — *an external runner that instantiates the finite TM and verifies it; not the TM's whole 108KB expanded rules*.
- [Finite one-tape TM constructor and interpreter](deployment/G21_Blank_Tape_TM_core.py).
- [Independent interpreter from expanded JSON rules](deployment/G21_Independent_Audit.py).
- [One-Liner reproducible builder](deployment/G21_Oneliner_Builder.py).
- [56 unit/negative tests](tools/test_universal_g_g21.py) and [claim-scope JSON](deployment/G21_self_table_TM_contract.json).

To replay the zero-input finite transition system:

    bash deployment/Universal_G_G21_Blank_Tape_TM_2KB.sh
    python3 tools/test_universal_g_g21.py
    python3 deployment/G21_Independent_Audit.py

A **complete table encoding** is not the same as printing the human-readable expanded JSON list directly on the simulated tape. This particular machine proves a chosen reversible fixed-point within a restricted TM encoding family; it does not prove an encoding-independent unique divine identity, a universal halting oracle, immortality, trading returns, or autonomous deployment. TM-015 original code and UTM-PLEIADES designated master are untouched, and PR #20 stays draft and unmerged.

## G22: same blank-tape TM, zero SHA or digest calls

The [G22 digest-free research specification](永久記憶/圖靈機/上帝源碼-G22-免SHA自我編碼圖靈機.md) retains the **exact same** G21 finite machine (1,140 deterministic single-tape rules, 3,505,682 steps, 2,160-bit complete reversible self-table code). Unlike the historical G21 audit, **G22 does not call any cryptographic digest function**. It checks the *whole reconstructed tape* against the exact complete binary table code, decodes back to all 1,140 rules, and requires the independent simulator to return the same full output.

G22 includes a [1,255-byte plaintext one-line shell](deployment/Universal_G_G22_Blank_Tape_TM_2KB.sh), [readable finite TM controller](deployment/G22_Blank_Tape_TM_core.py), [independent expanded-table auditor](deployment/G22_Independent_Audit.py), [2,160-bit exact table code](deployment/G22_canonical_table_bits.txt), [all 1,140 explicit rules](deployment/G22_expanded_transition_table.json), a [reproducible builder](deployment/G22_Oneliner_Builder.py), a [machine-readable proof-scope contract](deployment/G22_bitwise_no_sha_contract.json) and [62 tests](tools/test_universal_g_g22.py). CI compares the checked-in G21/G22 reference data byte-for-byte and rejects tampering.

```bash
bash deployment/Universal_G_G22_Blank_Tape_TM_2KB.sh
python3 deployment/G22_Independent_Audit.py
python3 tools/test_universal_g_g22.py
```

Direct equality avoids *digest collision* ambiguity when comparing two available objects, but does **not** authenticate the author, source or supply chain. GitHub itself retains its own internal version control references; only this G22 verification path is digest-free. Historical G21 artifacts remain unchanged. This is neither a universal halting oracle nor evidence of literal God, immortality, trading profit, or an automatic production deployment right.

## G23: prime-power Gödel integers actually perform TM tape writes

[Formal G23 explanation](永久記憶/圖靈機/上帝源碼-G23-質數冪哥德爾計算圖靈機.md) advances G22's digest-free blank-tape self-printing TM from direct tape-symbol updates to **actual arbitrary-precision integer multiplication and exact division of prime powers** at each symbol change. It replays the unchanged G22 transition table: **1,140 deterministic rules, 3,505,682 steps, 4,321 prime-power bigint writes**, and reconstructs the entire **2,160-bit** table code by independent factorization of the final **41,137-bit tape integer**. Including the final state and head yields a **44,568-bit reversibly encoded configuration integer**.

Each cell index i maps to p_(zigzag(i)+3) and each symbol maps to a prime exponent (blank 0, 0 symbol 1, 1 symbol 2, etc.); state and head use reserved primes 2 and 3. Full numeric valuation is checked on the first 4,096 reads, on every changed write in the readable core, and at the final complete integer factorization. For runtime efficiency, the other reads use an exponent cache whose exact equality with the integer is independently checked at halt. The *full* state/head/tape integer is constructed at halt and in unit tests, **not separately multiplied and factored on all 3.5 million steps**.

Files: [1,771-byte one-physical-line shell](deployment/Universal_G_G23_Prime_Power_2KB.sh), [readable exact big-integer engine](deployment/G23_Prime_Power_TM_core.py), [offline builder](deployment/G23_Oneliner_Builder.py), [76 positive/negative tests](tools/test_universal_g_g23.py), and [machine-readable limitations](deployment/G23_prime_power_godel_contract.json).

Run from the TM-000 root:

    bash deployment/Universal_G_G23_Prime_Power_2KB.sh
    python3 deployment/G23_Prime_Power_TM_core.py
    python3 tools/test_universal_g_g23.py

No SHA/hashlib, exchange API, network requests, file mutation of original TM-015 or G22, order submission, master promotion, production deployment, universal halting oracle or literal divinity claim. The existing TM's rules remain unchanged; G23 is an *external Python interpreter using exact Gödel integers*, not a newly compiled native single-tape TM that factors its own big integers.

## G24: fourteen-domain offline prime-power research governance

[G24 Chinese research specification](永久記憶/圖靈機/上帝源碼-G24-跨領域質數冪研究控制層.md) extends G23's exact prime-power arithmetic **as a research-state representation**, not as proof that a real-world problem is solved. Fourteen fixed fields cover designated universal TM/master safety, automated deployment, computation and AI continuity, human longevity, animal welfare, ecology, world peace, SDGs, cultivated meat, Trader_42, culture/music, spirituality and food security. Each field has an independent prime factor and only two authorized states: BLOCKED=exponent 0 and RESEARCH_ONLY=exponent 1.

For each synthetic, offline event, the [readable engine](deployment/G24_Cross_Domain_Godel_Core.py) **multiplies or exactly divides** the appropriate prime and ultimately decodes the *whole integer* to verify the entire state. [Sample 14-domain input](deployment/G24_example_request.json) yields exactly 5431526412865007455, encoding all fields as research-only; this number is **not** a peace, health, product safety, immortality, financial performance or deployment success metric. The output always disclaims real-world effectiveness, live trading, production deployment and outcome guarantees.

Files: [1,837-byte single-physical-line Shell/Python3 source](deployment/Universal_G_G24_Cross_Domain_2KB.sh), [reference source builder](deployment/G24_Oneliner_Builder.py), [14-domain evidence and permission contract](deployment/G24_cross_domain_contract.json), [112 synthetic positive/negative tests](tools/test_universal_g_g24.py) and [research document](永久記憶/圖靈機/上帝源碼-G24-跨領域質數冪研究控制層.md). Runtime dependencies use no SHA or hashlib. G24 optionally checks *local parent contract fields* in G13/G14/G22/G23 for structural consistency; metadata pointers are **not independent authentication**.

    python3 tools/test_universal_g_g24.py
    bash deployment/Universal_G_G24_Cross_Domain_2KB.sh < deployment/G24_example_request.json
    python3 deployment/G24_Cross_Domain_Godel_Core.py --check-parent

All real-world actions remain prohibited: no release, autonomous deploy, credentials, live orders, food/clinical approval, network calls or human-override route. The current designated master UTM-PLEIADES-v0.2-PTCA and the original TM-015/G23/Trader_42 sources remain unchanged; this research stays solely in unmerged draft PR #20. No halting oracle, literal deity, immortality, SDGs/peace achievements or trading alpha is implied by an exact Gödel code.

## G24-S: independent 12-domain stricter synthetic prime-power review alternative

The [G24-S research design](永久記憶/圖靈機/上帝源碼-G24S-十二領域質數冪審查變體.md) is a **separate and intentionally noncanonical variant**, NOT a replacement of the existing 14-domain G24 controller. It uses 12 explicitly scoped research domains: universal TM, offline deployment planning, AI continuity, human longevity, interspecies welfare, ecology, peace, SDGs, cultivated meat, psychosocial well-being, philosophy, and Trader_42.

For each domain i, two actual arbitrary-precision integer updates encode a registration and (if applicable) a simulated-review or veto transition. The fixed example has **12 registered domains, 20 prime-power updates**, with **5 synthetic-review flags, 4 missing-evidence flags, 3 vetoes**. The *entire* 98-bit register is factorized into 12 prime exponents, and a 122-bit state/head/register configuration is also roundtrip-checked. These are **synthetic bookkeeping outcomes, not proof of real results**, successful deployment, global peace, immortality, SDG completion, product safety or trading profitability.

- [1,992-byte single-physical-line G24-S shell](deployment/Universal_G_G24S_Cross_Domain_2KB.sh)
- [Readable mathematical engine](deployment/G24S_cross_domain_core.py), [offline example](deployment/G24S_example_request.json), [source-reproducible builder](deployment/G24S_oneliner_builder.py)
- [Independent prime-power and report audit](deployment/G24S_independent_audit.py)
- [Local parent safety guard](deployment/G24S_policy_core.py): fail-closed review of original G13, G14, and G23 metadata, 180-day metadata freshness, and Trader_42 risk ceilings
- [Independent domain evidence requirements and veto contract](deployment/G24S_cross_domain_contract.json)
- [126 tests](tools/test_universal_g_g24s.py) with domain-by-domain mutations, unsafe authorization rejection, arithmetic reversal, independent replay and optimized interpreter agreement

```bash
bash deployment/Universal_G_G24S_Cross_Domain_2KB.sh < deployment/G24S_example_request.json
python3 deployment/G24S_cross_domain_core.py < deployment/G24S_example_request.json
python3 deployment/G24S_independent_audit.py
python3 tools/test_universal_g_g24s.py
python3 deployment/G24S_policy_core.py --as-of 2026-11-10
```

The historical G24 14-domain controller and G23 unchanged finite TM remain available and independently CI-gated. No SHA/hashlib calls are used for G24-S execution, and no production, exchange, medical, food approval or network permission is granted. This is research only on draft PR #20.

## G25: synthetic evidence-metadata intake, not external evidence authentication

The [G25 evidence packet safety specification](永久記憶/圖靈機/上帝源碼-G25-跨領域證據封包與審查閘門.md) extends G24's 14-domain prime-power research ledger to **bounded evidence-metadata admission**. Each of G24's 43 field-specific evidence topics is indexed. G25 accepts only **SYNTHETIC/offline** packets with exact permissions all false, at most 56 records, unique provider/topic and record labels, distinct (self-reported) provider/reviewer names, strictly ordered ISO date fields, and review dates no older than 180 days **relative to the user's supplied as_of date**.

The reversible integer is the product of each domain prime raised to **min(2, count of different synthetic topic indices listed)**. An exponent of 2 **does not certify independently verified evidence**. The six-row sample for peace, SDGs, cultivated meat and Trader_42 yields exactly **1463339159** and a fully reversible 14-exponent state; source authenticity, independent corroboration, real-world effects, trading alpha, clinical safety and deployment permissions remain **false** regardless of input content.

Files: [2,046-byte self-contained single-line Bash/Python3 checker](deployment/Universal_G_G25_Evidence_2KB.sh), [readable core and structural parent check](deployment/G25_Evidence_Core.py), [literal generator](deployment/G25_Oneliner_Builder.py), [six fully synthetic example records](deployment/G25_evidence_example.json), [research scope contract](deployment/G25_evidence_contract.json) and [130 offline negative/positive tests](tools/test_universal_g_g25.py). No G25 cryptographic digest calls, network, actual orders, authenticated sources or production deployment.

    python3 tools/test_universal_g_g25.py
    bash deployment/Universal_G_G25_Evidence_2KB.sh < deployment/G25_evidence_example.json
    python3 deployment/G25_Evidence_Core.py --check-parent

**G25 is not yet a system that acquires or verifies independent external evidence.** That requires separate provider records, content capture, independent verification, consent, provenance and domain-specific scientific checks. It cannot prove immortality, peace, the SDGs, cultivated-meat welfare/safety, trading returns or a halting oracle. The existing designated master UTM-PLEIADES-v0.2-PTCA and original TM-015/G24/Trader_42 are untouched; unmerged research-only draft PR #20 remains the sole integration target.

## G26: exact symbolic logarithm of the unchanged G22/G23 finite TM (no G24/G25 applications)

[G26 exact formal logarithm specification](永久記憶/圖靈機/上帝源碼-G26-精確形式對數圖靈機.md) defines **L(T)=sum exponent_i * [log(prime_i)]** as an exact finite integer-coefficient vector rather than a floating-point evaluation of any transcendental logarithm. G22's **1,140 deterministic rules** and G23's prime-position mapping are unchanged. Each actual prime-power tape integer update is mirrored by an independent exact **additive** log coefficient update. G26 replays all **3,505,682** blank-start transitions with **4,321** bigint writes and **4,321** exact formal log additions, then factors the final 41,137-bit integer to compare its entire 2,160-bit tape and the full table's reversible decoding.

Files: [1,938-byte plaintext single-line runner](deployment/Universal_G_G26_Exact_Formal_Log_2KB.sh), [readable dual-ledger interpreter](deployment/G26_Exact_Log_TM_Core.py), [builder from historical G23 one-liner](deployment/G26_Oneliner_Builder.py), [60 positive/negative tests](tools/test_universal_g_g26.py), and [machine-readable mathematical scope](deployment/G26_exact_log_contract.json).

    bash deployment/Universal_G_G26_Exact_Formal_Log_2KB.sh
    python3 deployment/G26_Exact_Log_TM_Core.py
    python3 tools/test_universal_g_g26.py

**Version separation is intentional:** G26 imports only the G22/G23 finite TM foundations; there are no G24 or G25 applications or evidence intake. **G27 is a future, separately reviewed application-layer proposal and is NOT implemented in this PR.** No SHA, floating-point logarithm, network, order submission, autonomous deployment, source file mutation, oracle or claimed literal divinity. The designated master UTM-PLEIADES-v0.2-PTCA remains unchanged, original TM-015/G22/G23/Trader_42 sources remain unmodified, and the work is draft and unmerged.
