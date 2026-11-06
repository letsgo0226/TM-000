# TM-011 — Logical Chronon and Temporal-Closure Certificate Machine

**Registry ID:** TM-011  
**Registration date:** 2026-11-06  
**Status:** current total-machine reference for the finite registered orchestration; not a physical time-particle detector.

## Total-machine designation

TM-011 is the registry's current **total-machine reference**. Its executable first verifies the complete TM-001 through TM-011 catalogue and declared artifacts, then emits a temporally closed finite computation certificate. The designation is explicitly scoped as `FINITE_REGISTERED_ORCHESTRATION`: it is a project-level composition and verification role, not a mathematical claim that the machine halts on every possible input, decides the halting problem, or executes every registered core.

TM-009 remains preserved as the photonic exact-arithmetic/encoding-closed-loop baseline. TM-011 does not replace TM-009's equations or experimental boundaries.

### Canonical composite entrypoint

[tm011_composite_total_machine_2kb.sh](tm011_composite_total_machine_2kb.sh) is the strict one-line total-machine controller. When explicitly invoked, it locally executes and validates three preserved subcores:

1. **TM-009:** exact symbolic photonic, Lorentz and encoding-closed-loop certificate;
2. **TM-010:** finite registry and essence–existence alignment certificate;
3. **TM-011 temporal core:** logical-chronon finite halting-trace certificate.

It emits the three complete child certificates inside one composite JSON certificate. This is functional composition rather than source-code flattening; the child cores remain independently auditable. Default registry loading remains read-only and never invokes this controller.

## Purpose

TM-011 defines an **effective computational time particle** as one verified transition event:

```text
chronon = (machine, run, step, pre-configuration, action, post-configuration)
```

For the included deterministic unary machine, every `1` is changed to `X`; the first blank cell then moves the machine into its halt state. The finite trace contains the complete initial configuration, every locally valid transition, and the terminal configuration.

## Temporal states

- `TEMPORALLY_CLOSED`: the supplied finite computation reaches HALT, every adjacent configuration is continuous, every action follows the transition table, and every chronon survives exact reversible byte encoding.
- `PREFIX_COMPLETE`: reserved for a separately certified finite prefix of a computation that has not reached HALT. The canonical one-liner emits only `TEMPORALLY_CLOSED` because its unary input always halts.

## Canonical prototype

- [Strict physical one-line composite total-machine controller](tm011_composite_total_machine_2kb.sh)
- [Strict physical one-line temporal certificate core](logical_chronon_temporal_closure_2kb.sh)
- Maximum size: 2,048 bytes.
- Input: an optional unary string such as `111`; default `111`.
- Output: JSON temporal certificate with ordered logical chronons and exact base-257 event codes.
- No floating-point arithmetic, SHA function, network, deployment, trading, or execution of other registered machines.

## Relationship to prior machines

TM-011 provides a common event-history layer for TM-001 through TM-010. It does not merge or replace their individual semantics. In particular, it does not derive TM-002's entropy model, TM-006's modal claims, or TM-009's photonic equations; it can only represent their finite state transitions when an explicit transition adapter is supplied.

## Scientific boundary

`LOGICAL_CHRONON` is a computational event type, not evidence that physical time is discrete or composed of particles. `TEMPORALLY_CLOSED` proves only the closure of the emitted finite trace. It does not prove time travel, immortality, a physical chronon, a photonic singularity, autonomous persistence, Turing completeness, or a solution to the halting problem.
