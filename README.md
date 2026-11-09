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
