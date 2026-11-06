# TM-014 — Totalized Universal Turing Machine (bounded simulator)

- **Registered version:** v0.2, 1540-byte POSIX Shell/Python one-liner.
- **Core:** [TM-014-v0.2-2KB.sh](TM-014-v0.2-2KB.sh)
- **Designation:** current bounded-total universal-simulation reference.
- **Totality scope:** `BOUNDED_SIMULATION_ONLY`; for well-formed finite inputs and finite N the mathematical algorithm terminates, assuming idealized resources. Real Python can exhaust resources.
- **Universality scope:** finite-step simulation of arbitrary finite deterministic single-tape transition tables, with an idealized two-way unbounded tape.
- **Statuses:** `HALTED`, `PROVEN_NONHALTING` (repeated full configuration), `UNKNOWN`, `INVALID`.
- **Certificate:** optional `--cert` output includes pre-transition states and cycle indices. Independent verifier was developed separately; it is not part of the 1540-byte registered core.
- **Relationship:** TM-009 and TM-011 remain immutable reference prototypes. TM-012/TM-013 are research precursors, not automatically registered by this entry.
- **Safety:** metadata loading never executes the core; explicitly invoke `sh` to run it. Uses Python `assert`; do not enable `-O` or `PYTHONOPTIMIZE`.
- **Scientific boundary:** neither a total universal halting decider nor a proof of physical energy conversion or hypercomputation.

## Explicit run

```sh
sh 永久記憶/圖靈機/TM-014-v0.2-2KB.sh
sh 永久記憶/圖靈機/TM-014-v0.2-2KB.sh machine.json 20 --cert
```
