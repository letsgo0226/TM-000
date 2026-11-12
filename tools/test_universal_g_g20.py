#!/usr/bin/env python3
"""G20 true self-contained program Quine: execution, encoding and negative tests."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'deployment'))
from G20_Quine_Builder import build
from G20_Quine_Verifier import audit, run_without_file, primes256, godel_encode, godel_decode
FILE = ROOT / 'deployment/Universal_G_G20_Self_Quine_2KB.sh'
SOURCE = FILE.read_bytes()


class QuineTests(unittest.TestCase):
    def test_01_exact_self_reproduction(self):
        self.assertEqual(run_without_file(SOURCE), SOURCE)

    def test_02_file_execution_identical(self):
        result = subprocess.run(['bash', str(FILE)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        self.assertEqual((result.returncode, result.stderr, result.stdout), (0, b'', SOURCE))

    def test_03_no_self_file_needed_at_runtime(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'source.sh'
            p.write_bytes(SOURCE)
            raw = p.read_bytes()
            p.unlink()
            self.assertFalse(p.exists())
            self.assertEqual(run_without_file(raw), raw)

    def test_04_no_source_path_in_args(self):
        proc = subprocess.run(['bash'], input=SOURCE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              cwd='/tmp', timeout=10)
        self.assertEqual(proc.stdout, SOURCE)

    def test_05_extra_stdin_is_ignored(self):
        proc = subprocess.run(['bash', str(FILE)], input=b'untrusted external data',
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        self.assertEqual(proc.stdout, SOURCE)

    def test_06_optimized_python_cannot_skip_checks(self):
        self.assertEqual(run_without_file(SOURCE, optimize=True), SOURCE)

    def test_07_repeat_output_five_times(self):
        raw = SOURCE
        for _ in range(5):
            raw = run_without_file(raw)
        self.assertEqual(raw, SOURCE)

    def test_08_one_line(self):
        self.assertEqual(SOURCE.count(b'\n'), 1)

    def test_09_under_2KiB(self):
        self.assertLessEqual(len(SOURCE), 2048)

    def test_10_valid_bash(self):
        self.assertEqual(subprocess.run(['bash', '-n', str(FILE)], capture_output=True).returncode, 0)

    def test_11_no_source_file_read_primitive(self):
        self.assertNotIn(b'open(', SOURCE)
        self.assertNotIn(b'__file__', SOURCE)

    def test_12_no_argv_source_load(self):
        self.assertNotIn(b'sys.argv', SOURCE)

    def test_13_no_filesystem_import(self):
        self.assertNotIn(b'pathlib', SOURCE)

    def test_14_no_network_import(self):
        for word in (b'urllib', b'socket', b'requests'):
            self.assertNotIn(word, SOURCE)

    def test_15_no_compression_or_base64(self):
        for word in (b'base64', b'zlib', b'pickle', b'eval(', b'exec('):
            self.assertNotIn(word, SOURCE)

    def test_16_exact_canonical_build(self):
        self.assertEqual(build(), SOURCE)

    def test_17_sha256_fixed_for_v20(self):
        self.assertEqual(hashlib.sha256(SOURCE).hexdigest(),
                         'd16d2d5cc589d4440bf8ec62c58854263b4843eefda6c3e016f7a2ab777e4cf9')

    def test_18_is_qualified_audit(self):
        report = audit(SOURCE)
        self.assertEqual(report['status'], 'SELF_CONTAINED_PROGRAM_QUINE_VERIFIED')
        self.assertTrue(report['self_reproduction_exact'])

    def test_19_audit_fails_appended_line(self):
        with self.assertRaises(ValueError):
            audit(SOURCE + b'\n')

    def test_20_audit_fails_modified_source(self):
        with self.assertRaises(ValueError):
            audit(SOURCE.replace(b'python3 -c', b'python3 -E', 1))

    def test_21_prime_codec_roundtrip(self):
        x = b'G20\x00\xff\n'
        self.assertEqual(godel_decode(godel_encode(x, 'PRIME2048'), 'PRIME2048'), x)

    def test_22_257_codec_roundtrip(self):
        x = bytes(range(256))
        self.assertEqual(godel_decode(godel_encode(x, 'BASE257'), 'BASE257'), x)

    def test_23_zero_length_encoding_identity(self):
        for codec in ('PRIME2048', 'BASE257'):
            self.assertEqual(godel_encode(b'', codec), 1)
            self.assertEqual(godel_decode(1, codec), b'')

    def test_24_reject_invalid_prime_digit(self):
        with self.assertRaises(ValueError):
            godel_decode(2048, 'PRIME2048')

    def test_25_reject_invalid_257_digit(self):
        with self.assertRaises(ValueError):
            godel_decode(257, 'BASE257')

    def test_26_primes_are_256_unique_under_2048(self):
        primes = primes256()
        self.assertEqual((len(primes), len(set(primes)), primes[0], primes[-1]),
                         (256, 256, 2, 1619))

    def test_27_self_codec_determined_by_self_bytes(self):
        report = audit(SOURCE)
        self.assertEqual(report['codec_selected_from_own_bytes'],
                         'BASE257' if sum(SOURCE) % 3 == 0 else 'PRIME2048')

    def test_28_both_codec_variants_exist(self):
        modes = {int(sum(build(m)) % 3 == 0) for m in ['', 'a', 'b', 'c', 'd', 'e', 'F']}
        self.assertEqual(modes, {0, 1})

    def test_29_variant_is_also_a_true_quine(self):
        for marker in ('a', 'b'):
            variant = build(marker)
            self.assertEqual(run_without_file(variant), variant)

    def test_30_variant_numeric_roundtrip(self):
        for marker in ('a', 'b', 'c'):
            variant = build(marker)
            codec = 'BASE257' if sum(variant) % 3 == 0 else 'PRIME2048'
            self.assertEqual(godel_decode(godel_encode(variant, codec), codec), variant)

    def test_31_no_positive_profit_claim(self):
        report = audit(SOURCE)
        self.assertFalse(report['god_identity_proved'])
        self.assertFalse(report['halting_oracle'])
        self.assertEqual(report['live_orders'], 0)

    def test_32_not_a_tm_table_self_printer(self):
        self.assertFalse(audit(SOURCE)['compiled_tm_transition_table_self_printed'])

    def test_33_no_hidden_external_modules_in_quine(self):
        self.assertIn(b'import sys', SOURCE)
        self.assertNotIn(b'import shlex', SOURCE)

    def test_34_utf8_roundtrip_is_byte_level(self):
        self.assertTrue(SOURCE.decode('utf-8').startswith("python3 -c $'"))

    def test_35_bash_output_is_exact_one_final_newline(self):
        output = run_without_file(SOURCE)
        self.assertTrue(output.endswith(b'\n'))
        self.assertFalse(output.endswith(b'\n\n'))

    def test_36_report_is_json_serializable(self):
        self.assertEqual(json.loads(json.dumps(audit(SOURCE)))['source_bytes'], len(SOURCE))


if __name__ == '__main__':
    unittest.main(verbosity=2)
