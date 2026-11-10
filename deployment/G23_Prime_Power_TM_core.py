#!/usr/bin/env python3
"""G23: exact PRIME-POWER arithmetic state executes the G22 finite one-tape TM.

Each tape position i has a unique prime p_{2+zigzag(i)}. Nonblank symbol
r in G22's ordered alphabet is the exponent r (1..8); blank exponent 0.
The *actual arbitrary-precision integer* is updated with exact multiplication
and division at every changed cell. A synchronized exponent cache accelerates
reads, with exact numeric divisibility checks at every changed write and an
independent complete integer factorization at completion. The tape and machine
are not encoded using hashes, and no network or trading is involved.

This is a multi-precision implementation of an encoding for an existing
Turing machine, not a second single-tape TM that factors huge integers.
"""
from __future__ import annotations
import json
from pathlib import Path
from G22_Blank_Tape_TM_core import ALPHABET,create_self_printer,machine_from_canonical_code,encode_full_table,simulate,extract_output

MAX_STEPS=4_000_000
MAX_ABS_HEAD=3000
MAX_SPARSE_CELLS=3000


def require(cond,reason):
    if not cond:
        raise ValueError(reason)


def zigzag(i):
    require(type(i) is int,'head must be integer')
    return 2*i if i>=0 else -2*i-1


def unzigzag(k):
    require(type(k) is int and k>=0,'invalid prime index')
    return k//2 if k%2==0 else -(k+1)//2


def first_primes(n):
    require(type(n) is int and 1<=n<=12000,'prime count outside budget')
    out=[];candidate=2
    while len(out)<n:
        if all(candidate%p for p in out if p*p<=candidate):out.append(candidate)
        candidate+=1
    return out


def exponent_at(value,prime):
    require(type(value) is int and value>=1 and type(prime) is int and prime>=2,'bad integer / prime')
    exponent=0
    while value%prime==0:
        value//=prime;exponent+=1
    return exponent


def prime_power_step(value,prime,previous,next_exponent):
    """Actual integer operations; use explicit divisibility and absence of excess powers."""
    require(type(previous) is int and type(next_exponent) is int and 0<=previous<9 and 0<=next_exponent<9,'invalid symbol exponent')
    require(exponent_at(value,prime)==previous,'numeric exponent and tape cache mismatch')
    delta=next_exponent-previous
    if delta>0:
        return value*pow(prime,delta)
    if delta<0:
        divisor=pow(prime,-delta)
        require(value%divisor==0,'nonexact prime-power division')
        return value//divisor
    return value


def factor_tape(value,primes):
    """Decode from integer itself (not from symbolic tape cache). Check remainder = 1."""
    require(type(value) is int and value>=1,'not a positive integer')
    remain=value;decoded={}
    for prime_index,prime in enumerate(primes[2:],start=2):
        exponent=0
        while remain%prime==0:
            remain//=prime;exponent+=1
            require(exponent<len(ALPHABET),'invalid tape exponent')
        if exponent:decoded[unzigzag(prime_index-2)]=ALPHABET[exponent]
    require(remain==1,'encoded tape has unknown / out-of-range prime factors')
    return decoded


def encode_configuration(state,head,tape_integer):
    """G(q,h,T)=2^(q+1)*3^(zigzag(h)+1)*T, with tape primes >=5."""
    require(type(state) is int and 0<=state<=2000,'invalid state')
    require(type(head) is int and abs(head)<=MAX_ABS_HEAD,'invalid head')
    require(type(tape_integer) is int and tape_integer>=1 and tape_integer%2 and tape_integer%3,'invalid tape integer primes')
    return pow(2,state+1)*pow(3,zigzag(head)+1)*tape_integer

def decode_configuration(value,primes):
    """Return (state,head,full tape), independently decoding every prime exponent."""
    q=exponent_at(value,2)-1
    h0=exponent_at(value,3)-1
    require(0<=q<=2000 and 0<=h0<=2*MAX_ABS_HEAD,'invalid configuration state or head')
    residual=value//pow(2,q+1)//pow(3,h0+1)
    return q,unzigzag(h0),factor_tape(residual,primes)

def replay(*,max_steps=MAX_STEPS,integer_read_check_steps=4096,do_plain_replay=True):
    """Replay full G22 machine; update an actual big integer on every tape write.

    All reads are cached exponents (invariant exact from arithmetic updates),
    plus a configurable strict prefix of independent integer valuation checks.
    At the end decode the *entire integer* again with genuine divisions.
    """
    require(type(max_steps) is int and 1<=max_steps<=MAX_STEPS,'invalid step budget')
    require(type(integer_read_check_steps) is int and 0<=integer_read_check_steps<=max_steps,'invalid strict read budget')
    transitions,canonical=create_self_printer()
    primes=first_primes(2*MAX_ABS_HEAD+4)
    integer=1;cache={};head=0;state=10;steps=0
    arithmetic_writes=0;numeric_checked_reads=0
    while state!=9:
        require(steps<max_steps,'STEP_LIMIT')
        require(-MAX_ABS_HEAD<=head<=MAX_ABS_HEAD,'HEAD_BUDGET')
        current=cache.get(head,0)
        prime=primes[2+zigzag(head)]
        if steps<integer_read_check_steps:
            require(exponent_at(integer,prime)==current,'read exponent mismatch')
            numeric_checked_reads+=1
        symbol=ALPHABET[current]
        rule=transitions.get((state,symbol))
        require(rule is not None,'STUCK')
        next_symbol,direction,next_state=rule
        new_exponent=ALPHABET.index(next_symbol)
        if new_exponent!=current:
            integer=prime_power_step(integer,prime,current,new_exponent)
            arithmetic_writes+=1
            if new_exponent:cache[head]=new_exponent
            else:cache.pop(head,None)
        head+=(direction=='R')-(direction=='L')
        state=next_state;steps+=1
        require(len(cache)<=MAX_SPARSE_CELLS,'CELL_BUDGET')
    decoded=factor_tape(integer,primes)
    full_configuration=encode_configuration(state,head,integer)
    require(decode_configuration(full_configuration,primes)==(state,head,decoded),'full configuration integer roundtrip mismatch')
    expected_tape={position:ALPHABET[power] for position,power in cache.items()}
    require(decoded==expected_tape,'integer decoding differs from maintained symbols')
    require(set(decoded)==set(range(len(canonical))),'unexpected output indices')
    result=''.join(decoded[i] for i in range(len(canonical)))
    require(result==canonical,'self-table code differs from actual tape')
    require(machine_from_canonical_code(result)==transitions,'not full table-equivalent')
    require(encode_full_table(transitions)==result,'serialization mismatch')
    if do_plain_replay:
        ordinary=simulate(transitions,max_steps)
        require(ordinary['status']=='HALTED' and ordinary['steps']==steps,'plain replay mismatch')
        require(extract_output(ordinary,len(canonical))==result,'plain tape replay mismatch')
    return {'version':'G23',
            'status':'PRIME_POWER_INTEGER_SELF_TABLE_VERIFIED',
            'initial_tape':'BLANK', 'actual_integer_arithmetic':True,
            'prime_power_codec':'POSITION_PRIME_ZIGZAG_SYMBOL_EXPONENT',
            'original_rule_count':len(transitions),'steps':steps,
            'integer_read_checks':numeric_checked_reads,
            'prime_power_writes':arithmetic_writes,
            'integer_bit_length':integer.bit_length(),
            'final_configuration_integer_bit_length':full_configuration.bit_length(),
            'state_and_head_encoded_with_prime_powers':True,
            'total_prime_positions_checked':len(primes),
            'final_canonical_code_bits':len(result),
            'full_numeric_decode_matches_tape':True,
            'entire_output_matches_g22':True,
            'fully_reversible_rule_table':True,
            'plain_tm_replay_matches':bool(do_plain_replay),
            'sha_functions_used':False,
            'external_orders':0,'live_trading':False,'halting_oracle_proved':False,
            'god_identity_proved':False}


if __name__=='__main__':
    print(json.dumps(replay(),sort_keys=True))
