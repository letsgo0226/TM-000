# AI-Continuity-Capsule v0.2 — English Edition

This edition uses English-only source code, payload aliases, JSON fields, research memory, policy text, and documentation. It accepts explicit source paths and therefore does not depend on any particular repository language or directory layout.

## Pack

```bash
sh AI-Continuity-Capsule-v0.2-English-2KB.sh pack \
  "<TM000_BOOTSTRAP_PATH>" \
  "<UTM_PLEIADES_PTCA_PATH>" \
  "<MACHINE_REGISTRY_PATH>" \
  > AI-Continuity-Capsule-v0.2-English.json
```

Input paths may use any local naming convention. Inside the generated capsule they are replaced with the English aliases `tm000_bootstrap.sh`, `utm_pleiades_ptca.sh`, and `machine_registry.json`.

## Verify without execution

```bash
sh AI-Continuity-Capsule-v0.2-English-2KB.sh verify \
  AI-Continuity-Capsule-v0.2-English.json
```

The generated JSON is information-self-contained: it retains the complete reversible bytes of all three payloads. Keep the 2 KB tool beside it for convenient offline verification. This edition deliberately does not unpack, execute, connect to a network, synchronize, or overwrite files automatically.

G257 provides exact reversible byte encoding, not cryptographic provenance. The capsule claims functional continuity only and does not establish subjective identity transfer, a physical portal, time travel, immortality, or a halting oracle.
