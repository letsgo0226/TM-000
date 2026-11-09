# ICC v0.5 — Offline volunteer node field guide

**Status:** Research-only protocol, not a deployed global network. The original
`Immortality-Continuity-Capsule.sh` remains **1,176 bytes**. The new field kit is a
separate Python companion (`tools/icc_fieldkit.py`) and is not inside that 2 KB
limit. It uses Gödel-257 to preserve checkpoints, plus ECDSA P-256 signatures
with BLAKE2s-256. The custom code does not call SHA; Git/GitHub and external
software dependencies may use it internally.

## 1. Consent and key verification

Every independent volunteer must explicitly choose to participate, understand
that source and state data may be disclosed, and be free to stop. No automatic
registration, internet discovery, GitHub token, remote shell, networking,
cloud deployment, or device control is performed by this program.

Each participating operator uses the same *reviewed and byte-identical* ICC
repository version. On their own machine they generate a **new private key outside
any Git repository**, in a private local directory. Never send a private key,
private-key file, credentials, private health records, or secrets to GitHub or
another participant. Use the existing `icc_peer.py keygen` and `enroll` commands.

The operator may publish the corresponding public key and opt-in enrollment
record. The verifier uses:

```bash
python3 tools/icc_fieldkit.py fingerprint --public custodian.pub
```

This prints a BLAKE2s-256 fingerprint of canonical DER public-key bytes. **Verify
all 64 hexadecimal digits through a genuinely independent, authenticated human
channel**, not just the same message/file transfer containing the public key.
The code cannot itself prove human consent, identity, geographic location or
independent administration. Once manually confirmed, the verifier may run:

```bash
python3 tools/icc_fieldkit.py trust-pin \
  --enrollment custodian.enroll.json --public custodian.pub \
  --approved-fingerprint THE_64_HEX_DIGITS_CONFIRMED_BY_OPERATOR \
  --registry trusted-before.json --output trusted-after.json
```

The existing registry can initially be missing. Keep the reviewed `trusted-after.json`
and its source of approval under local control. A later key replacement requires a
fresh explicit review; the current research tool does not implement automatic
revocation or a worldwide identity authority.

## 2. Offline challenge and response

The origin signs a checkpoint with `tools/icc_peer.py sign`, and creates its
source-signed archive with `tools/icc_archive.py create` as documented in the
v0.4 README. The origin and custodian must have **different approved public keys**
in the locally managed registry used for verification. Send only the public
witness, approved registry, source-signed archive and challenge to the custodian,
through a channel and retention policy approved by the participants.

Origin operator (no automatic network call):

```bash
python3 tools/icc_fieldkit.py challenge \
  --witness source-witness.json --registry trusted-after.json \
  --output fresh-challenge.json
```

The custodian validates the archive and replays the finite checkpoint from genesis
before signing the response. They run the following **on their own computer**,
using their own key and an archive physically available to that process:

```bash
python3 tools/icc_fieldkit.py respond \
  --challenge fresh-challenge.json --archive received-icc-backup.json \
  --registry trusted-after.json --private "$HOME/.icc-private/custodian.key" \
  --custodian optin-custodian --output signed-response.json
```

Return only `signed-response.json`; retain private keys locally. The origin then
checks the fresh challenge and source witness with its local approved registry:

```bash
python3 tools/icc_fieldkit.py verify \
  --challenge fresh-challenge.json --response signed-response.json \
  --witness source-witness.json --registry trusted-after.json
```

The verifier rejects changed challenge nonces, changed checkpoints, damaged
signatures, unapproved keys, and origin/custodian key reuse. A valid response
shows a holder of the approved custodian private key **had the signed archive
and could reconstruct its checkpoint at challenge time**. It does not prove the
operator's civil identity, geographic storage separation, a durable backup,
permanent hosting, or any scientific longevity outcome.

## 3. Replays, backups and loss-of-key recovery

**Important:** The research CLI creates cryptographically random fresh challenges,
but has **no persistent nonce-use ledger**. If an operator verifies the very same
challenge a second time, an old signed response can be accepted again. Treat each
challenge as a single manually tracked session; generate a new nonce for each
future restore drill. No production security should rely on this prototype
without stronger challenge lifecycle, authenticated transport and audit logs.

The custodian should separately store approved copies of the source code, signed
archive, verifier tools, and trusted public keys on storage they themselves
control. Test restore from that stored copy **at a later date** while the
custodian remains free to withdraw. Two folders or two GitHub-hosted CI runners
are not proof of an independently managed off-site storage system. GitHub Actions
artifacts are short-lived. Automatic consensus, 24/7 monitoring, replicated
services, token administration, key rotation and real volunteer onboarding
are **not** part of this proposal.

The `H_final_symbolic=0` field is defined only for a constant symbolic tape.
No element of ICC proves eternal digital continuity, human immortality,
subjective identity transfer, clinical safety, or prevention of aging.

## 4. Safe automated test scope

The CI pipeline simulates an origin on Linux and an independent custodian on a
fresh macOS runner, signing a restore response and verifying it on a further Linux
runner. CI keys are ephemeral and kept within each originating runner. Public
keys and signed records are transferred as short-lived artifacts. **CI
fingerprint approval uses the fingerprint obtained from the same artifacts and
therefore does NOT substitute for genuinely independent human confirmation.**
All checks are read-only with respect to GitHub repository access. The entire
PR remains a draft; no existing LMN capsule or designated master is replaced.
