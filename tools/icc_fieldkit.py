#!/usr/bin/env python3
"""ICC v0.5: offline opt-in key pinning and restore challenge/response.

A successful challenge shows a trusted *key holder* could verify a source-signed
archive in a particular session. It does not prove real-world identity, remote
location, long-term retention or immortality. No networking or auto-enrollment.
"""
import argparse
import json
import re
import secrets
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization

import icc_node as node
import icc_peer as peer
import icc_archive as archive

CHALLENGE = 'ICC-OFFLINE-RESTORE-CHALLENGE-v1'
RESPONSE = 'ICC-OFFLINE-RESTORE-RESPONSE-v1'
STATEMENT = 'Locally validated and reconstructed a source-signed checkpoint; storage location not attested.'


def key_fingerprint(pem):
    key = peer.get_public(pem)
    public_der = key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    hasher = hashes.Hash(hashes.BLAKE2s(32))
    hasher.update(public_der)
    return hasher.finalize().hex()


def trust_with_pin(enroll, pub, approved_fingerprint, registry, output):
    expected = approved_fingerprint.lower()
    if not re.fullmatch(r'[a-f0-9]{64}', expected):
        raise ValueError('invalid BLAKE2s-256 fingerprint')
    key_text = Path(pub).read_text(encoding='ascii')
    if key_fingerprint(key_text) != expected:
        raise ValueError('independently confirmed fingerprint mismatch')
    peer.trust(enroll, pub, registry, output)
    return {'status':'PINNED_LOCAL_TRUST', 'fingerprint_blake2s':expected,
            'real_world_identity_verified_by_code':False}


def validate_challenge(c):
    if not isinstance(c, dict) or set(c) != {'protocol','nonce','origin','checkpoint','step'}:
        raise ValueError('incorrect challenge schema')
    if c['protocol'] != CHALLENGE or not isinstance(c['nonce'], str) or not re.fullmatch(r'[a-f0-9]{64}', c['nonce']):
        raise ValueError('invalid challenge nonce/version')
    peer.good_label(c['origin'])
    state = node.decode_checkpoint(c['checkpoint'])
    if type(c['step']) is not int or state['step'] != c['step']:
        raise ValueError('challenge step mismatch')
    return c


def new_challenge(witness, registry):
    proof = peer.verify_signed(witness, registry)
    c = {'protocol':CHALLENGE, 'nonce':secrets.token_hex(32), 'origin':proof['node'],
         'checkpoint':proof['checkpoint'], 'step':proof['step']}
    return validate_challenge(c)


def make_response(challenge, archive_path, registry, private_path, custodian):
    c = validate_challenge(challenge)
    peer.good_label(custodian)
    if custodian == c['origin']:
        raise ValueError('origin and custodian must have separate approved keys')
    if custodian not in registry['peers']:
        raise ValueError('custodian is not in locally approved registry')
    private = peer.get_private(private_path)
    public_pem = peer.public_pem(private)
    if public_pem != registry['peers'][custodian]:
        raise ValueError('custodian private key does not match approved public key')
    bundle = archive.canonical_file(archive_path)
    checkpoint = archive.validate_bundle(bundle, registry)
    if bundle['signed_witness']['node'] != c['origin'] or checkpoint != c['checkpoint']:
        raise ValueError('archive did not match the requested source checkpoint')
    # Every checkpoint has already been replayed from genesis by validate_bundle.
    restored = node.canonical(checkpoint) + b'\n'
    if json.loads(restored) != checkpoint:
        raise ValueError('cannot reconstruct checkpoint')
    payload = {'protocol':RESPONSE, 'nonce':c['nonce'], 'custodian':custodian,
               'origin':c['origin'], 'checkpoint':checkpoint, 'statement':STATEMENT,
               'stored_geographically_independent':False, 'real_world_identity_proven':False}
    return {**payload, 'signature':peer.sign(private,payload)}


def verify_response(challenge, response, witness, registry):
    c = validate_challenge(challenge)
    source = peer.verify_signed(witness, registry)
    if c['origin'] != source['node'] or c['checkpoint'] != source['checkpoint'] or c['step'] != source['step']:
        raise ValueError('challenge is not bound to the provided source witness')
    expected = {'protocol','nonce','custodian','origin','checkpoint','statement',
                'stored_geographically_independent','real_world_identity_proven','signature'}
    if not isinstance(response,dict) or set(response) != expected:
        raise ValueError('response schema mismatch')
    custodian = peer.good_label(response['custodian'])
    if custodian == c['origin'] or custodian not in registry['peers']:
        raise ValueError('unapproved or non-distinct custodian')
    if response['protocol'] != RESPONSE or response['statement'] != STATEMENT:
        raise ValueError('invalid response statement')
    if response['nonce'] != c['nonce'] or response['origin'] != c['origin'] or response['checkpoint'] != c['checkpoint']:
        raise ValueError('response does not match issued challenge')
    if response['stored_geographically_independent'] is not False or response['real_world_identity_proven'] is not False:
        raise ValueError('unsupported physical custody or identity claims')
    payload = {k:v for k,v in response.items() if k != 'signature'}
    peer.check(registry['peers'][custodian],payload,response['signature'])
    return {'status':'SIGNED_RESTORE_RESPONSE_VALID', 'origin':c['origin'],
            'custodian':custodian,'step':c['step'],'private_key_holder_verified':True,
            'real_world_identity_verified':False,'physical_offsite_storage_verified':False,
            'long_term_retention_proven':False,'medical_effect_proven':False}


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    sub=cli.add_subparsers(dest='cmd',required=True)
    k=sub.add_parser('fingerprint');k.add_argument('--public',required=True)
    t=sub.add_parser('trust-pin')
    t.add_argument('--enrollment',required=True);t.add_argument('--public',required=True)
    t.add_argument('--approved-fingerprint',required=True)
    t.add_argument('--registry',required=True);t.add_argument('--output',required=True)
    c=sub.add_parser('challenge');c.add_argument('--witness',required=True)
    c.add_argument('--registry',required=True);c.add_argument('--output',required=True)
    a=sub.add_parser('respond')
    a.add_argument('--challenge',required=True);a.add_argument('--archive',required=True)
    a.add_argument('--registry',required=True);a.add_argument('--private',required=True)
    a.add_argument('--custodian',required=True);a.add_argument('--output',required=True)
    v=sub.add_parser('verify');v.add_argument('--challenge',required=True)
    v.add_argument('--response',required=True);v.add_argument('--witness',required=True)
    v.add_argument('--registry',required=True)
    x=cli.parse_args()
    if x.cmd=='fingerprint':
        result={'algorithm':'BLAKE2s-256','fingerprint':key_fingerprint(Path(x.public).read_text(encoding='ascii')),
                'independent_confirmation_required':True}
    elif x.cmd=='trust-pin':
        result=trust_with_pin(x.enrollment,x.public,x.approved_fingerprint,x.registry,x.output)
    elif x.cmd=='challenge':
        peer.write(x.output,new_challenge(peer.load(x.witness),peer.get_registry(x.registry)))
        result={'status':'FRESH_CHALLENGE_ISSUED','replay_tracking':'OPERATOR_REQUIRED'}
    elif x.cmd=='respond':
        peer.write(x.output,make_response(peer.load(x.challenge),x.archive,peer.get_registry(x.registry),x.private,x.custodian))
        result={'status':'SIGNED_RESPONSE_CREATED','geographic_location_not_proven':True}
    else:
        result=verify_response(peer.load(x.challenge),peer.load(x.response),peer.load(x.witness),peer.get_registry(x.registry))
    print(json.dumps(result,separators=(',',':')))


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,TypeError,KeyError,UnicodeError,InvalidSignature) as ex:
        print(json.dumps({'status':'DENY','reason':str(ex)}),file=sys.stderr)
        sys.exit(1)
