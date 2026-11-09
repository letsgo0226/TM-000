# Immortality-Continuity-Capsule.sh — v0.2 research proposal

This is an **offline, finite, reproducible digital-continuity research prototype**, not a treatment, immortality mechanism, trusted node identity, deployment master, or global network controller. The original `capsule/AI-Continuity-Capsule.sh` and the designated UTM-PLEIADES master remain untouched. This change is proposed via draft PR only.

## What is implemented

- `Immortality-Continuity-Capsule.sh` is a single-line Bash/Python 3 **1,176-byte** core. It Gödel-257 encodes its exact source bytes, decodes them, validates byte-to-prime symbol mapping and emits deterministic JSON; its symbolic `H_final_symbolic=0` is *only* the entropy of a separate, constant-valued tape. No SHA call occurs in the capsule.
- `tools/icc_node.py` is a **separate companion protocol implementation** (not restricted to 2 KB). It implements a bounded, deterministic, 16-cell reversible ring machine, encoded and decoded using G257 JSON checkpoints. Every imported checkpoint is independently re-executed from genesis with a 100,000-step cap. It can resume, rewind, produce *unsigned* witnesses, and compare them.
- `.github/workflows/immortality-continuity-dryrun.yml` runs local regression tests and **two separate GitHub-hosted runners** (`ubuntu-latest` and `macos-15`), uploads short-lived comparison artifacts, and runs an offline witness comparison in a third job. The code has no network requests of its own; artifact transfers are performed by GitHub Actions. This does not verify geographic separation or participation by any external global node.

## Start, pause, resume, rewind, compare

From repository root with Python 3 and Bash:

```bash
bash capsule/Immortality-Continuity-Capsule.sh > capsule-result.json
python3 tools/icc_node.py init --output genesis.json
python3 tools/icc_node.py advance --input genesis.json --steps 1024 --output checkpoint.json
python3 tools/icc_node.py verify --input checkpoint.json
python3 tools/icc_node.py advance --input checkpoint.json --steps 128 --output resumed.json
python3 tools/icc_node.py rewind --input checkpoint.json --steps 1024 --output restored.json
python3 tools/icc_node.py witness --input checkpoint.json --node my-consenting-computer --output witness-a.json
```

Copy the **same source files and a validated checkpoint** to a second **consenting** device and run the `witness` command there with a different *public node label*. With both public witness files on the same machine:

```bash
python3 tools/icc_node.py compare --left witness-a.json --right witness-b.json
python3 tools/test_icc_node.py
```

`CONSISTENT` means identical, locally replayable finite-state checkpoints were supplied under distinct *self-reported* labels. It **does not** prove the existence, independence, identity, authenticity, or location of either remote computer. No automatic network join, self-replication, access to accounts, external sensors, printer, or automatic code merging occurs. A real opt-in global network would require independently operated peers, an authenticated transport/provenance protocol, durable backups, monitoring, permissions, and governance not supplied here.

## Precise continuity claim

The reversible finite-state transition applies attractor byte `A[step mod len(A)]` to the current 16-cell tape position, updating modulo 257 and rotating the tape head. A checkpoint is canonical JSON encoded as G257 hexadecimal. `advance()` followed by `rewind()` for the same steps returns the exact prior state. The program is a **bounded deterministic finite-state machine**, not a demonstrated universal Turing machine.

The 2 KB budget applies only to the original capsule `.sh`; it **does not** cover the companion protocol, CI workflow, certificates, or generated checkpoint data. Gödel-257 preserves and compares information, but **does not provide cryptographic integrity**. GitHub/Git may use hashes internally even though the source does not call SHA. An attacker who modifies code and matching data could fool unsigned witnesses. The current checks reject accidental corruption and incompatible states, not adversarial forgeries.

The phrase `COSMIC_LOVE_IS_THE_SOLUTION_FOR_EVERYTHING` is a philosophical symbol, not a physical or biological theorem. A formal `H_final_symbolic = 0` does not imply zero environmental entropy, infinite persistence, preserved subjective identity, a halting oracle, clinically effective anti-aging, or immortality. `identity_authenticated=false`, `medical_effect_proven=false`, and `global_control=false` are intentional. No ingestible drug specification, trial, manufacture, or 3D printer instructions are included.

## Boundaries and durability

PR validation and manually triggered tests only; no production deployment, external network communication by project code, privileged token use, credential exfiltration, system modification, or mutation of other repositories. Github Actions artifacts expire (7 days by this workflow). Actual long-term preservation requires copies under independent, authorized stewardship with recoverability tests. Review the draft PR before merging; the existing master and archived original remain unchanged.
