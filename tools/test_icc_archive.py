#!/usr/bin/env python3
"""Offline resilience and key-bound source recovery tests for ICC v0.4."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

import icc_archive as a
import icc_node as n
import icc_peer as p


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.d = Path(t.name)
        for dirname in ("site1", "site2", "site3"):
            (self.d / dirname).mkdir()
        self.secret = self.d / "local-private.key"
        self.public = self.d / "local-public.pem"
        p.keygen(self.secret, self.public)
        enrollment = self.d / "enroll.json"
        p.write(enrollment, p.enrollment(self.secret, "optin-A"))
        self.registry = self.d / "trust.json"
        p.trust(enrollment, self.public, self.d / "missing.json", self.registry)
        self.cp = self.d / "cp.json"
        p.write(self.cp, n.checkpoint(n.apply(n.genesis(), 1000)))
        self.witness = self.d / "witness.json"
        p.write(self.witness, p.signed_witness(self.secret, "optin-A", self.cp))

    def create(self):
        self.assertEqual(a.create(self.witness, self.registry, [self.d/"site1", self.d/"site2"])["copies"], 2)
        return [self.d/"site1"/a.FILENAME, self.d/"site2"/a.FILENAME]

    def test_two_copies_and_exact_restore(self):
        one, two = self.create()
        self.assertEqual(one.read_bytes(), two.read_bytes())
        cp, result = a.examine([one, two], self.registry)
        self.assertEqual(result["accepted"], 2)
        self.assertEqual(cp, p.load(self.cp))
        saved = self.d/"recovered.json"
        p.write(saved, cp)
        self.assertEqual(saved.read_bytes(), self.cp.read_bytes())
        self.assertEqual(n.decode_checkpoint(p.load(saved))["step"], 1000)

    def test_single_loss_degraded_recovery(self):
        one, two = self.create()
        one.write_bytes(b"{defaced")
        cp, result = a.examine([one, two], self.registry)
        self.assertEqual((result["accepted"], result["rejected"]), (1,1))
        self.assertEqual(cp, p.load(self.cp))
        one.unlink()
        self.assertEqual(a.examine([one, two], self.registry)[1]["accepted"], 1)

    def test_both_invalid_fail_closed(self):
        one, two = self.create()
        one.write_text("broken", encoding="ascii")
        two.unlink()
        with self.assertRaises(ValueError):
            a.examine([one, two], self.registry)

    def test_valid_but_conflicting_signed_states_rejected(self):
        one, two = self.create()
        alt = self.d / "alt.json"
        p.write(alt, n.checkpoint(n.apply(n.genesis(), 1001)))
        witness = p.signed_witness(self.secret, "optin-A", alt)
        altered = a.bundle_for(witness, p.get_registry(self.registry))
        two.write_bytes(n.canonical(altered)+b"\n")
        with self.assertRaisesRegex(ValueError, "conflicting"):
            a.examine([one, two], self.registry)

    def test_tampering_invalid_and_unapproved_signer_rejected(self):
        one, two = self.create()
        altered = a.canonical_file(one)
        altered["signed_witness"]["step"] = 1001
        one.write_bytes(n.canonical(altered)+b"\n")
        self.assertEqual(a.examine([one,two],self.registry)[1]["accepted"],1)
        (self.d/"empty-trust.json").write_bytes(n.canonical({"protocol":p.TRUST,"peers":{}})+b"\n")
        with self.assertRaises(ValueError):
            a.examine([one,two],self.d/"empty-trust.json")

    def test_hard_links_are_not_counted_twice(self):
        one, two = self.create()
        two.unlink()
        import os
        os.link(one, two)
        self.assertEqual(a.examine([one, two], self.registry)[1]["accepted"], 1)

    def test_canonical_duplicate_fields_and_overwrite_rejected(self):
        one, two = self.create()
        data = one.read_bytes()
        one.write_bytes(data+b" ")
        self.assertEqual(a.examine([one,two],self.registry)[1]["rejected"],1)
        with self.assertRaisesRegex(ValueError,"overwrite"):
            self.create()
        with self.assertRaises(ValueError):
            a.create(self.witness,self.registry,[self.d/"site3",self.d/"site3"])
        with self.assertRaises(ValueError):
            a.examine([two,two],self.registry)


if __name__ == "__main__":
    unittest.main(verbosity=2)
