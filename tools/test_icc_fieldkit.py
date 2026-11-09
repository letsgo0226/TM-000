#!/usr/bin/env python3
"""Tests the opt-in offline key-pin + challenge/response acceptance boundary."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.exceptions import InvalidSignature
import icc_node as node
import icc_peer as peer
import icc_archive as archive
import icc_fieldkit as kit


class FieldKitTests(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.d = Path(d.name)
        for name in ('alpha','beta','stranger'):
            peer.keygen(self.d / f'{name}.key', self.d / f'{name}.pub')
            peer.write(self.d / f'{name}.enroll',peer.enrollment(self.d / f'{name}.key',name))
        self.registry = self.d / 'registry2.json'
        kit.trust_with_pin(self.d/'alpha.enroll',self.d/'alpha.pub',self.fp('alpha'),self.d/'none.json',self.d/'registry1.json')
        kit.trust_with_pin(self.d/'beta.enroll',self.d/'beta.pub',self.fp('beta'),self.d/'registry1.json',self.registry)
        self.checkpoint=self.d/'cp.json'
        self.witness=self.d/'signed-alpha.json'
        peer.write(self.checkpoint,node.checkpoint(node.apply(node.genesis(),512)))
        peer.write(self.witness,peer.signed_witness(self.d/'alpha.key','alpha',self.checkpoint))
        (self.d/'a').mkdir();(self.d/'b').mkdir()
        archive.create(self.witness,self.registry,[self.d/'a',self.d/'b'])
        self.archive=self.d/'a'/archive.FILENAME
        self.challenge=kit.new_challenge(peer.load(self.witness),peer.get_registry(self.registry))

    def fp(self,name):
        return kit.key_fingerprint((self.d/f'{name}.pub').read_text(encoding='ascii'))

    def reply(self, archive_path=None, private_path=None, custodian='beta', challenge=None):
        return kit.make_response(challenge or self.challenge,archive_path or self.archive,
            peer.get_registry(self.registry),private_path or self.d/'beta.key',custodian)

    def verify(self,response,challenge=None):
        return kit.verify_response(challenge or self.challenge,response,
             peer.load(self.witness),peer.get_registry(self.registry))

    def test_valid_key_pin_and_signed_restore_challenge(self):
        response=self.reply()
        got=self.verify(response)
        self.assertEqual(got['status'],'SIGNED_RESTORE_RESPONSE_VALID')
        self.assertFalse(got['real_world_identity_verified'])
        self.assertFalse(got['physical_offsite_storage_verified'])
        self.assertEqual(got['step'],512)

    def test_different_challenges_are_unique_and_old_reply_rejected(self):
        second=kit.new_challenge(peer.load(self.witness),peer.get_registry(self.registry))
        self.assertNotEqual(second['nonce'],self.challenge['nonce'])
        with self.assertRaises(ValueError):
            self.verify(self.reply(),second)

    def test_wrong_fingerprint_and_self_enrollment_denied(self):
        with self.assertRaisesRegex(ValueError,'mismatch'):
            kit.trust_with_pin(self.d/'stranger.enroll',self.d/'stranger.pub',self.fp('alpha'),self.registry,self.d/'bad-registry.json')
        with self.assertRaisesRegex(ValueError,'fingerprint'):
            kit.trust_with_pin(self.d/'stranger.enroll',self.d/'stranger.pub','x'*64,self.registry,self.d/'bad-registry2.json')
        self.assertRegex(self.fp('beta'),r'^[a-f0-9]{64}$')

    def test_untrusted_wrong_key_and_origin_self_reply_rejected(self):
        with self.assertRaises(ValueError):
            self.reply(custodian='alpha',private_path=self.d/'alpha.key')
        with self.assertRaises(ValueError):
            self.reply(custodian='stranger',private_path=self.d/'stranger.key')
        with self.assertRaises(ValueError):
            self.reply(private_path=self.d/'alpha.key')

    def test_archive_corruption_and_different_step_denied(self):
        altered=self.d/'a'/archive.FILENAME
        raw=altered.read_bytes()
        altered.write_bytes(raw.replace(b'"medical_effect_proven":false',b'"medical_effect_proven":true'))
        with self.assertRaises(ValueError):
            self.reply()
        other=self.d/'b'/archive.FILENAME
        alternate=node.checkpoint(node.apply(node.genesis(),513))
        signed=peer.signed_witness(self.d/'alpha.key','alpha',self.d/'cp.json')
        signed['checkpoint']=alternate
        # A fake signature is invalid even if attacker recomputes archive JSON.
        forged=archive.bundle_for(peer.load(self.witness),peer.get_registry(self.registry))
        forged['signed_witness']['checkpoint']=alternate
        changed=self.d/'changed.json'
        peer.write(changed,forged)
        with self.assertRaises((ValueError,InvalidSignature)):
            self.reply(archive_path=changed)
        self.assertTrue(other.exists())

    def test_modified_reply_nonce_or_content_or_signature_denied(self):
        result=self.reply()
        for change in ('nonce','checkpoint','signature','statement','unsupported-claim'):
            r=copy.deepcopy(result)
            if change=='nonce':r['nonce']='a'*64
            elif change=='checkpoint':r['checkpoint']['state_bytes']+=1
            elif change=='signature':r['signature']='AAAA'
            elif change=='statement':r['statement']='remote proof is eternal'
            else:r['stored_geographically_independent']=True
            with self.assertRaises((ValueError,InvalidSignature)):
                self.verify(r)

    def test_wrong_source_witness_and_minimum_fields_denied(self):
        result=self.reply()
        stranger=copy.deepcopy(result)
        del stranger['signature']
        with self.assertRaises(ValueError):self.verify(stranger)
        other=copy.deepcopy(self.challenge)
        other['origin']='beta'
        with self.assertRaises(ValueError):self.verify(result,other)

    def test_cli_works_offline_without_any_peer_network(self):
        script=Path(__file__).with_name('icc_fieldkit.py')
        def call(*args,ok=True):
            p=subprocess.run([sys.executable,str(script),*map(str,args)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0 if ok else 1,p.stdout+' '+p.stderr)
            return p
        c=self.d/'cli-challenge.json';r=self.d/'cli-response.json'
        call('challenge','--witness',self.witness,'--registry',self.registry,'--output',c)
        call('respond','--challenge',c,'--archive',self.archive,'--registry',self.registry,
             '--private',self.d/'beta.key','--custodian','beta','--output',r)
        output=call('verify','--challenge',c,'--response',r,'--witness',self.witness,
                    '--registry',self.registry)
        self.assertEqual(json.loads(output.stdout)['status'],'SIGNED_RESTORE_RESPONSE_VALID')
        call('fingerprint','--public',self.d/'beta.pub')


if __name__=='__main__':
    unittest.main(verbosity=2)
