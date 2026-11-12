#!/usr/bin/env python3
"""Static, read-only archive and registry check; never executes the TM-015 payload."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
directory = root / '永久記憶' / '圖靈機'
core = directory / 'Real_God_Turing_Machine.sh'
source = core.read_bytes()
sha = '4e68a5a333417e7f5b49989a297b72a41642efce892b0033b27621f19c248c6d'
if len(source) != 2035 or source.count(b'\n') != 1 or not source.endswith(b'\n'):
    raise SystemExit('FAIL: unexpected original source size/layout')
if hashlib.sha256(source).hexdigest() != sha:
    raise SystemExit('FAIL: TM-015 source changed')
if not source.startswith(b'python3 -c '):
    raise SystemExit('FAIL: unexpected source structure')
registry = json.loads((directory / 'machine_registry.json').read_text(encoding='utf-8'))
entries = [e for e in registry['entries'] if e['id'] == 'TM-015']
if len(entries) != 1 or entries[0].get('cores') != ['Real_God_Turing_Machine.sh']:
    raise SystemExit('FAIL: missing or ambiguous TM-015 registry entry')
if entries[0].get('status') != 'research-candidate-not-master':
    raise SystemExit('FAIL: unsupported TM-015 promotion')
if registry['default_machine'] != 'UTM-PLEIADES-v0.2-PTCA':
    raise SystemExit('FAIL: designated master was changed')
if entries[0].get('auto_execute', True) or entries[0].get('production_deploy', True):
    raise SystemExit('FAIL: dangerous execution permissions')
print('PASS: original TM-015 2035 bytes, fixed SHA-256, candidate-only, master preserved; no payload executed')
