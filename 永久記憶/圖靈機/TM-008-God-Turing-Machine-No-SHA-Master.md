# TM-008 — 上帝圖靈機 GTM-001（無 SHA）· 總控候選

**English:** GTM-001 No-SHA God Turing Machine — Master-Orchestration Candidate  
**Registry ID:** TM-008  
**Initial draft:** 2026-11-01  
**Main-registry reconciliation:** 2026-11-06  
**Status:** registered research candidate; not the canonical total-machine reference and not deployed.

## Preserved prototype

- [No-SHA 2 KB core](god_turing_machine_no_sha_2kb.sh)
- Quine-style self-reconstruction.
- Reversible base-257 byte+1 Gödel encoding.
- Finite unary-tape transition trace and internally checked certificate.
- No SHA function is used by the prototype. Git object identifiers are repository infrastructure, not part of its algorithm.

## Registry and orchestration role

TM-008 is restored from the historical draft registration without displacing TM-007 or TM-009. The shared `machine_registry.json` is its allowlisted, read-only prototype catalogue. `tools/load_turing_registry.py` verifies the catalogue and declared artifacts but never implicitly executes them.

In the TM-010 composition, TM-008 supplies the no-SHA orchestration convention; TM-007 supplies Encode–Simulate/Load–Verify staging; TM-009 supplies the exact encoding-closed-loop requirement.

## Safety and scientific boundary

- No automatic merge, deployment, network, cloud, trading, or registered-core execution.
- The finite certificate is not a proof of general program termination, metaphysical identity, physical existence, immortality, time travel, a photonic singularity, or a solution to the halting problem.
- Production use requires separate review and explicit authorization.
