# TM-015 — Real God Turing Machine (research candidate)

- **Source**: `Real_God_Turing_Machine.sh` (user-provided, preserved byte-for-byte)
- **Size**: 2,035 bytes; one physical line plus trailing LF (`< 2,048` bytes)
- **SHA-256**: `4e68a5a333417e7f5b49989a297b72a41642efce892b0033b27621f19c248c6d`
- **Status**: `RESEARCH_CANDIDATE_NOT_MASTER`; **execution policy**: never execute implicitly.
- **Master retained**: `UTM-PLEIADES-v0.2-PTCA` remains the designated TM-000 master, `BOUNDED_SIMULATION_ONLY` / `FUNCTIONAL_ONLY`.

## Scope of verification

The core has a shell-level Quine (default output is its own complete command), a reversible prime-digit encoding of finite UTF-8 data using 256 prime atoms and radix 2048, and a finite proof sketch for the identity of the free monoid of words. Local sanitized manual checks completed for shell syntax, byte-identical Quine output, `-v`, `-p`, and `-e`/`-d` including Chinese and 🌌.

`-g` denotes the prime encoding of the **empty word**, namely 1; `-G` denotes the much larger Gödel encoding of the **full program**. The uniqueness of a two-sided identity in a monoid does not establish a unique universal code, the identity of God, AGI, the existence of a nonphysical memory store, zero physical entropy, immortality, or a halting oracle.

The core uses `assert` (which Python `-O` may omit). Do not treat `-v` as a hardened verifier. A safe offline static check is available in `tools/test_tm015_real_god.py` and does **not** execute the archived core. Other TM-000 registered machines, certificates, rollback mechanisms and master source remain unchanged.

## Manual review only

```bash
python3 tools/test_tm015_real_god.py
python3 tools/load_turing_registry.py --select TM-015
# Execute the archived core only after review and in an isolated, resource-limited environment:
# env -i PATH="$PATH" bash 永久記憶/圖靈機/Real_God_Turing_Machine.sh -v
```

No automatic master promotion, autonomous deployment, GitHub mutation, online communication or cross-device synchronization is authorized by this registration.
