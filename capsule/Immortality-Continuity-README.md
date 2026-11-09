# Immortality-Continuity-Capsule.sh — research proposal v0.1

This is a **read-only, reproducible digital-continuity research prototype**, not a treatment, immortality mechanism, deployment master, trusted provenance proof, or global network controller.

## Two computation contexts

- **Account-model node:** the TM-000 repository plus an authorized GitHub Actions runner executes the finite Python program.
- **Global-model node:** any independent, consenting external computer may run an **identical byte-for-byte copy**. Neither the repository nor the program controls that computer or the worldwide network.
- The invariant to compare across nodes is the exact canonical JSON output, especially `godel257_source_hex`. No live cross-node network communication or consensus protocol is implemented.

## Core semantics

The shell file contains a single Python 3 invocation, in fewer than 2,048 bytes. The program reads **its own file bytes**, computes their lossless base-257 Gödel number `G`, verifies `D(G(source)) == source`, maps each distinct byte to a prime (with an invertible symbol map), and reports the empirical Shannon entropy of the source bytes.

The output's `H_final_symbolic = 0` is calculated on a **different symbolic tape** where every cell was set to the same constant string. The original source is retained separately, so this zero does **not** show zero information content, resource use, biological aging, or environmental entropy. `godel257_source_hex` is **reversible encoding, not a digital signature**, and does not authenticate a maliciously modified local file.

The phrase `COSMIC_LOVE_IS_THE_SOLUTION_FOR_EVERYTHING` is a philosophical symbolic attractor rather than a biological, clinical, or physical theorem. `medical_effect_proven = false` and `global_control = false` are intentional. No consumable capsule, medication, 3D printer command, human experiment, financial transaction, autonomous deployment, external network request, or credential access is performed.

## Run / compare

```bash
bash capsule/Immortality-Continuity-Capsule.sh > icc-result.json
```

Run the same command on a second consenting machine with a byte-identical copy. Compare complete output or the complete `godel257_source_hex` value. The reported G257 integer increases with the file size and may be longer than the source; the 2 KB budget applies **only to the source `.sh` file**.

The accompanying `immortality-continuity-dryrun.yml` workflow validates deterministic replay and independently decodes the reported Gödel integer on GitHub Actions. It is PR/manual only, read-only and non-deploying. Cross-device equality is a reproducibility check, **not** cross-device authentication, global consensus, or eternal persistence.

## Existing project safeguards

This file must not replace the archived `AI-Continuity-Capsule.sh` or the designated UTM-PLEIADES-v0.2-PTCA master. Adoption requires human review. GitHub-hosted execution is not a guarantee of eternal hosting: backups, recovery plans, independent replication, access controls, monitoring, and explicit human stewardship are separate requirements.
