# TM-000 — 2 KB Transactional Bootstrap

Core: `TM-000-2KB-transactional-bootstrap.sh` (one physical line, 1831 bytes).

The bootstrap considers the complete current registry from TM-001 through TM-011, TM-014, and the designated UTM-PLEIADES master. It does not merge their independent semantics into one program.

Inherited roles:
- TM-007: stage, verify, activate, rollback pipeline.
- TM-008: no-SHA convention and reversible G257 self-description.
- TM-009: exact byte-level encoding closed loop.
- TM-011: ordered update journal as logical chronons.
- UTM-PLEIADES PTCA: designated bounded simulation core and resumable checkpoint.

Modes: `inspect`, `stage CANDIDATE`, `activate`, and `rollback`. Activation and rollback require `TM000_APPROVE=YES`. Updates are local and atomic; the core contains no network synchronization. GitHub Actions supplies read-only synchronization and PR validation. It does not auto-merge main or deploy production.

G257 proves reversible byte encoding, not trusted provenance or cryptographic tamper resistance. This prototype is not a halting oracle, physical singularity, time machine, consciousness transfer, or immortality mechanism.
