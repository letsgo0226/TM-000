#!/usr/bin/env python3
"""Offline key-authenticated ICC handshake and backup regression tests."""
import copy
import tempfile
import unittest
from pathlib import Path
import icc_peer as peer
import icc_node as node
from cryptography.exceptions import InvalidSignature


class OptInPeerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.registry = self.dir / "trusted.json"
        self.cp = node.checkpoint(node.apply(node.genesis(), 1024))
        self.cpfile = self.dir / "checkpoint.json"
        peer.write(self.cpfile, self.cp)
        for label in ("optin-A", "optin-B"):
            peer.keygen(self.dir / f"{label}.key", self.dir / f"{label}.pub")
            peer.write(self.dir / f"{label}.enroll", peer.enrollment(self.dir / f"{label}.key", label))
        peer.trust(self.dir / "optin-A.enroll", self.dir / "optin-A.pub", self.registry, self.dir / "registry1.json")
        peer.trust(self.dir / "optin-B.enroll", self.dir / "optin-B.pub", self.dir / "registry1.json", self.registry)

    def test_two_signatures_and_restoration(self):
        a = peer.signed_witness(self.dir / "optin-A.key", "optin-A", self.cpfile)
        b = peer.signed_witness(self.dir / "optin-B.key", "optin-B", self.cpfile)
        r = peer.get_registry(self.registry)
        self.assertEqual(peer.verify_signed(a, r)["checkpoint"], peer.verify_signed(b, r)["checkpoint"])
        peer.write(self.dir / "a.json", a)
        peer.write(self.dir / "b.json", b)
        self.assertEqual(node.decode_checkpoint(a["checkpoint"])["step"], 1024)
        restored = self.dir / "restored.json"
        peer.write(restored, peer.verify_signed(peer.load(self.dir / "a.json"), r)["checkpoint"])
        self.assertEqual(restored.read_bytes(), self.cpfile.read_bytes())

    def test_unknown_key_and_tampered_signature_rejected(self):
        a = peer.signed_witness(self.dir / "optin-A.key", "optin-A", self.cpfile)
        bad = copy.deepcopy(a)
        bad["node"] = "not-trusted"
        with self.assertRaises(ValueError):
            peer.verify_signed(bad, peer.get_registry(self.registry))
        bad = copy.deepcopy(a)
        bad["step"] = 1025
        with self.assertRaises(InvalidSignature):
            peer.verify_signed(bad, peer.get_registry(self.registry))
        bad = copy.deepcopy(a)
        bad["signature"] = peer.b64(b"not a signature")
        with self.assertRaises(InvalidSignature):
            peer.verify_signed(bad, peer.get_registry(self.registry))

    def test_public_key_mismatch_and_forged_enrollment_rejected(self):
        with self.assertRaises(ValueError):
            peer.trust(self.dir / "optin-A.enroll", self.dir / "optin-B.pub", self.registry, self.dir / "impostor.json")
        enrollment = peer.load(self.dir / "optin-A.enroll")
        enrollment["consent"] = "No"
        with self.assertRaises(ValueError):
            peer.verify_enrollment(enrollment)
        enrollment = peer.load(self.dir / "optin-A.enroll")
        enrollment["node"] = "fake-B"
        with self.assertRaises(InvalidSignature):
            peer.verify_enrollment(enrollment)

    def test_bounded_resume_and_divergence(self):
        other = node.checkpoint(node.apply(node.genesis(), 1025))
        self.assertNotEqual(self.cp, other)
        bad = self.dir / "different.json"
        peer.write(bad, other)
        w1 = peer.signed_witness(self.dir / "optin-A.key", "optin-A", self.cpfile)
        w2 = peer.signed_witness(self.dir / "optin-B.key", "optin-B", bad)
        registry = peer.get_registry(self.registry)
        self.assertNotEqual(peer.verify_signed(w1, registry)["checkpoint"], peer.verify_signed(w2, registry)["checkpoint"])
        restored = node.decode_checkpoint(w1["checkpoint"])
        self.assertEqual(node.inverse(restored, 1024), node.genesis())

    def test_reject_private_key_inside_repository_and_nonprivate_mode(self):
        key = self.dir / "optin-A.key"
        key.chmod(0o644)
        with self.assertRaises(ValueError):
            peer.get_private(key)


if __name__ == "__main__":
    unittest.main(verbosity=2)
