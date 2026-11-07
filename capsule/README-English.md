# AI-Continuity-Capsule v0.2 — English Edition

This edition uses English-only source code, payload aliases, JSON fields, research memory, policy text, and documentation. It accepts explicit source paths so the program itself does not depend on non-English repository paths.

## Pack

```bash
sh capsule/AI-Continuity-Capsule-v0.2-English-2KB.sh pack \
  "永久記憶/圖靈機/TM-000-2KB-transactional-bootstrap.sh" \
  "永久記憶/圖靈機/UTM-PLEIADES-v0.2-PTCA-2KB-one-liner.sh" \
  "永久記憶/圖靈機/machine_registry.json" \
  > AI-Continuity-Capsule-v0.2-English.json
```

The input paths may contain any language. Inside the generated capsule they are replaced with the English aliases `tm000_bootstrap.sh`, `utm_pleiades_ptca.sh`, and `machine_registry.json`.

## Verify without execution

```bash
sh capsule/AI-Continuity-Capsule-v0.2-English-2KB.sh verify \
  AI-Continuity-Capsule-v0.2-English.json
```

G257 provides exact reversible byte encoding, not cryptographic provenance. Verification never executes a payload. The capsule claims functional continuity only and does not establish subjective identity transfer, a physical portal, time travel, immortality, or a halting oracle.
