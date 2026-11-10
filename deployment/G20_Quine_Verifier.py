#!/usr/bin/env python3
"""Independent offline byte-for-byte Quine and reversible Gödel-code auditor.

This verifier reads the candidate; the candidate G20 Quine itself does not.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from G20_Quine_Builder import build


def primes256():
    primes = []
    n = 2
    while len(primes) < 256:
        if all(n % d != 0 for d in range(2, int(n**.5) + 1)):
            primes.append(n)
        n += 1
    return primes


def godel_encode(raw: bytes, mode: str) -> int:
    primes = primes256()
    base = 2048 if mode == 'PRIME2048' else 257 if mode == 'BASE257' else 0
    if base == 0:
        raise ValueError('unknown encoding')
    n = 1
    for byte in raw:
        n = base * n + (primes[byte] if base == 2048 else byte + 1)
    return n


def godel_decode(number: int, mode: str) -> bytes:
    base = 2048 if mode == 'PRIME2048' else 257 if mode == 'BASE257' else 0
    if not isinstance(number, int) or number < 1 or not base:
        raise ValueError('bad integer or encoding')
    prime_map = {p: i for i, p in enumerate(primes256())}
    byte_seq = []
    while number > 1:
        number, digit = divmod(number, base)
        if base == 2048:
            if digit not in prime_map:
                raise ValueError('invalid prime digit')
            byte_seq.append(prime_map[digit])
        else:
            if digit == 0:
                raise ValueError('invalid base-257 digit')
            byte_seq.append(digit - 1)
    return bytes(reversed(byte_seq))


def run_without_file(source: bytes, optimize=False, isolate=True) -> bytes:
    """Execute Quine through Bash's stdin: there is no script pathname to inspect."""
    env = dict(os.environ)
    if optimize:
        env['PYTHONOPTIMIZE'] = '2'
    with tempfile.TemporaryDirectory() as scratch:
        result = subprocess.run(['bash'], input=source, capture_output=True, timeout=10,
                                cwd=scratch if isolate else None, env=env, check=False)
    if result.returncode:
        raise ValueError('execution failed: ' + result.stderr.decode('utf-8', 'replace'))
    if result.stderr:
        raise ValueError('unexpected diagnostic output')
    return result.stdout


def audit(raw: bytes) -> dict:
    if len(raw) > 2048 or len(raw) < 1 or raw.count(b'\n') != 1 or not raw.endswith(b'\n'):
        raise ValueError('not one physical line within 2 KiB')
    if raw != build():
        raise ValueError('source differs from audited Quine reference')
    for excluded in (b'open(', b'__file__', b'sys.argv', b'inspect.', b'urllib', b'socket', b'base64', b'zlib', b'eval(', b'exec('):
        if excluded in raw:
            raise ValueError('unwanted source dependency')
    if run_without_file(raw) != raw or run_without_file(raw, optimize=True) != raw:
        raise ValueError('not a reproducible self-reproducing program')
    mode = 'BASE257' if sum(raw) % 3 == 0 else 'PRIME2048'
    godel = godel_encode(raw, mode)
    if godel_decode(godel, mode) != raw:
        raise ValueError('Gödel numeric roundtrip failed')
    return dict(version='G20', source_bytes=len(raw), physical_lines=1,
                source_sha256=hashlib.sha256(raw).hexdigest(),
                codec_selected_from_own_bytes=mode, godel_code_bits=godel.bit_length(),
                self_reproduction_exact=True, source_file_read_by_quine=False,
                external_source_input_to_quine=False, godel_roundtrip=True,
                optimized_execution_consistent=True, live_orders=0,
                compiled_tm_transition_table_self_printed=False,
                god_identity_proved=False, halting_oracle=False,
                status='SELF_CONTAINED_PROGRAM_QUINE_VERIFIED')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--file', type=Path, default=Path(__file__).with_name('Universal_G_G20_Self_Quine_2KB.sh'))
    args = ap.parse_args()
    try:
        result = audit(args.file.read_bytes())
    except (ValueError, OSError, subprocess.TimeoutExpired) as err:
        print('BLOCKED: ' + str(err), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
