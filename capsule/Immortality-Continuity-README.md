# Immortality-Continuity-Capsule — v0.4 offline continuity research

This is a **bounded, finite digital reproducibility and recovery experiment**, not an immortality treatment, global Turing machine, distributed consensus system, or AI self-preservation mechanism. The core `Immortality-Continuity-Capsule.sh` remains the original **1,176-byte** One-Liner in this PR; opt-in proof is deliberately implemented in separate companion software.

## Layer 1 — reversible finite state

`tools/icc_node.py` runs a deterministic 16-cell finite machine (maximum 100,000 steps), losslessly encodes and checks Gödel-257 checkpoints, and can advance, resume, rewind, and replay checkpoints from genesis. Every checkpoint is bound to the exact core source via its G257 value. G257 is **not** cryptographic authentication; `H_final_symbolic=0` is only the entropy of a separate constant symbolic tape, not reduced physical entropy.

```bash
bash capsule/Immortality-Continuity-Capsule.sh
python3 tools/icc_node.py init --output genesis.json
python3 tools/icc_node.py advance --input genesis.json --steps 1024 --output checkpoint.json
python3 tools/icc_node.py verify --input checkpoint.json
python3 tools/icc_node.py rewind --input checkpoint.json --steps 1024 --output restored-genesis.json
```

## Layer 2 — manually enrolled, opt-in peer keys

Install Python 3 and `cryptography==46.0.4`. The **new** `tools/icc_peer.py` uses the established cryptography library's ECDSA on NIST P-256 with BLAKE2s-256; the project does not directly invoke SHA. Git/GitHub and package installation may use hashes including SHA internally, so this is not a universal no-SHA guarantee.

Each node generates a private key **outside the repository**, with owner-only permissions (0600), and shares only a public key and signed opt-in enrollment request. Never upload private keys to GitHub or CI artifacts. On node A, replace the sample private-key path with a secure directory outside any repository:

```bash
python3 tools/icc_peer.py keygen --private /secure-private/icc-A.key --public public-A.pem
python3 tools/icc_peer.py enroll --private /secure-private/icc-A.key --node optin-A --output enroll-A.json
python3 tools/icc_peer.py sign --private /secure-private/icc-A.key --node optin-A --checkpoint checkpoint.json --output signed-A.json
```

A second **independently operated, consenting** machine may do the equivalent using its own key and label `optin-B`, producing `public-B.pem`, `enroll-B.json` and `signed-B.json`. The verifier MUST independently confirm the **exact** public key through a trusted channel with the real operator before accepting it. Receiving an enrollment and public key from the same untrusted source cannot establish identity or meaningful human consent.

After that human approval, on the verifier's machine:

```bash
python3 tools/icc_peer.py trust --enrollment enroll-A.json --expected-public-key public-A.pem --registry trusted0.json --output trusted1.json
python3 tools/icc_peer.py trust --enrollment enroll-B.json --expected-public-key public-B.pem --registry trusted1.json --output trusted2.json
python3 tools/icc_peer.py verify --registry trusted2.json --witness signed-A.json
python3 tools/icc_peer.py compare --registry trusted2.json --left signed-A.json --right signed-B.json
python3 tools/icc_peer.py recover --registry trusted2.json --witness signed-A.json --output recovered.json
python3 tools/icc_node.py verify --input recovered.json
```

The local trust operation **does not connect to or enroll anyone globally**. `trusted0.json` may initially be absent. The local registry represents a verifier-controlled acceptance decision, not a global identity authority; if an attacker controls it, signatures alone cannot preserve trust. Compromised keys must be revoked manually and independently replaced. Checkpoint keys are version-specific.

## Layer 3 — independent preservation and recovery

`recover` reconstructs the original canonical checkpoint after verifying a signed witness from a locally trusted key. Save source code, signed checkpoint, locally approved public-key registry and protocol versions on **independently administered storage**, with offline backups, access controls and periodic restore tests. Do not mistake 7-day GitHub Actions artifacts for permanent backups. The finite system has an explicit replay bound and depends on the continued availability of compatible code.

## Evidence and CI

`tools/test_icc_node.py` executes six finite-state regression tests; `tools/test_icc_peer.py` adds five opt-in signature/key tests. CI runs two separate GitHub-managed Ubuntu/macOS runners, generates throwaway private keys under runner-private temporary directories, uploads only signed material and public keys, and restores matching checkpoints. **The CI comparator simulates trust by reading both public keys from these artifacts; this is not independent out-of-band identity authentication**. It establishes correct protocol wiring under controlled conditions, not active participation by real external volunteer nodes.

The workflow is read-only (`permissions: contents: read`), PR/manual only; no automatic merge, production deployment, external-device control, medicine, 3D printing, or global account access is implemented. Existing `AI-Continuity-Capsule.sh` and UTM-PLEIADES master are preserved. Digital recurrence does not demonstrate reduced biological aging, preserved consciousness, eternal hosting, or immortality.

## Layer 4 — signed backups and simulated disaster recovery (v0.4)

The new companion program `tools/icc_archive.py` accepts only signed checkpoints verified against locally trusted public keys. It writes two byte-identical canonical JSON backups to two EXISTING directories that the operator explicitly supplies. It never uploads, provisions, discovers, or controls another host, and it will not overwrite an existing backup. It rejects corrupted/tampered records, unsigned or untrusted nodes, duplicate paths, hard links counted as two independent copies, and conflicting valid signed checkpoint states. Two separate directories do NOT prove physically or geographically independent storage.

After generating `signed-A.json` and approved `trusted2.json` through Layers 1–2:

```bash
mkdir -p local-copy-1 local-copy-2
python3 tools/icc_archive.py create --witness signed-A.json --registry trusted2.json --dest local-copy-1 --dest local-copy-2
python3 tools/icc_archive.py audit --registry trusted2.json --source local-copy-1/icc-backup.json --source local-copy-2/icc-backup.json --min-valid 2
```

To test restoration WITHOUT damaging any real backup, make disposable copies in separate temporary test directories, deliberately corrupt one *test copy*, and run:

```bash
python3 tools/icc_archive.py recover --registry trusted2.json --source bad-test-copy/icc-backup.json --source good-test-copy/icc-backup.json --min-valid 1 --output recovered-checkpoint.json
python3 tools/icc_node.py verify --input recovered-checkpoint.json
```

`RECOVERED_DEGRADED` indicates a valid signed copy was recovered but another supplied copy failed validation. Set `--min-valid 2` to require two distinct valid copies. Conflicting *valid* states are always rejected; they require human review. Writing can fail midway; independently audit backups after creation. Output paths must not already exist.

### Actual off-site durability is NOT completed

A human custodian must independently copy the archives to genuinely separate permissioned storage, retain compatible source code/verification tools and the locally approved public-key trust registry, verify remote operators by a separate trusted channel, implement key revocation, and repeat restore drills. The archival JSON stores the signed checkpoint, not the entire companion program or a trusted authority. Backups may expose source and computation state, so do not share confidential information. CI produces 7-day artifacts only.

CI now performs **18 unit/regression tests** (6 finite-state + 5 peer verification + 7 archival-resilience tests), plus a simulated one-copy-loss and signed recovery drill. GitHub Ubuntu and macOS runners are independent test jobs, NOT a verified international set of consenting peer operators. Neither longevity therapeutics nor subjective identity preservation nor eternal hosting is proven. This change remains a DRAFT research PR without production deployment or global authority.
