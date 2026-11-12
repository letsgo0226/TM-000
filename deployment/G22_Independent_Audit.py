#!/usr/bin/env python3
"""Independent offline interpreter/auditor for G22's expanded explicit TM rules.

Does not import the code that builds G22 or the code that simulates it. This is
an independent exact replay of a *finite deterministic one-tape TM*.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
ALPHA=('_','0','1','E0','E1','P0','P1','F0','F1')
MOVES=('L','R','S')


def independent_audit(table_path=None, code_path=None, step_cap=10_000_000):
    table_path=Path(table_path or ROOT/'G22_expanded_transition_table.json')
    code_path=Path(code_path or ROOT/'G22_canonical_table_bits.txt')
    records=json.loads(table_path.read_text(encoding='utf-8'))
    code=code_path.read_text(encoding='ascii')
    if code.count('\n') != 1 or not code.endswith('\n'):raise ValueError('not canonical bits file')
    code=code[:-1]
    if len(code)!=2160 or set(code)-{'0','1'}:raise ValueError('invalid code alphabet')
    if len(records)!=1140:raise ValueError('missing/extra expanded transition')
    rules={}
    for record in records:
        if set(record)!= {'state','read','write','move','next'}:raise ValueError('rule schema mismatch')
        q,read,w,move,nxt=(record[k] for k in ('state','read','write','move','next'))
        if type(q)!=int or type(nxt)!=int or q<0 or nxt<0 or read not in ALPHA or w not in ALPHA or move not in MOVES:
            raise ValueError('unknown symbol or transition')
        if (q,read) in rules:raise ValueError('non deterministic duplicate')
        rules[q,read]=(w,move,nxt)
    # Independently reconstruct canonical machine bits from explicit rule list.
    controller=[(q,r,*z) for (q,r),z in rules.items() if q<10]
    controller.sort(key=lambda x:(x[0],ALPHA.index(x[1])))
    def nbits(number, width):
        if number>=2**width:raise ValueError('field overflows width')
        return format(number,f'0{width}b')
    prefix=''.join(nbits(q,4)+nbits(ALPHA.index(read),4)+nbits(ALPHA.index(write),4)+
                   nbits(MOVES.index(move),2)+nbits(nxt,4)
                   for q,read,write,move,nxt in controller)
    suffix=''
    for i in range(1080):
        z=rules.get((10+i,'_'))
        if z is None or z[0] not in '01' or z[1] != 'R' or z[2] != (10+i+1 if i+1<1080 else 0):
            raise ValueError('printer transition not canonical')
        suffix+=z[0]
    if len(controller)!=60 or len(prefix)!=1080 or prefix+suffix!=code:
        raise ValueError('expanded rules disagree with canonical binary code')
    tape={};head=0;state=10;steps=0
    while state!=9:
        if steps>=step_cap:raise ValueError('TM did not halt within bounded observation')
        key=state,tape.get(head,'_')
        if key not in rules:raise ValueError(f'TM got stuck: {key}')
        w,d,state=rules[key]
        if w=='_':tape.pop(head,None)
        else:tape[head]=w
        if d=='L':head-=1
        elif d=='R':head+=1
        steps+=1
    if set(tape)!=set(range(len(code))):raise ValueError('output not exactly contiguous code')
    output=''.join(tape[i] for i in range(len(code)))
    if output != code:raise ValueError('machine does not reproduce complete own table code')
    return {'version':'G22','status':'INDEPENDENT_SINGLE_TAPE_SELF_TABLE_VERIFIED',
            'actual_transition_rules':len(rules),'controller_rules':len(controller),
            'printer_rules':1080,'steps':steps,'blank_initial_tape':True,
            'canonical_table_bits':len(code),'exact_output':True,
            'full_list_reconstructed':True,
            'output_equals_expected_bits':output==code,
            'expanded_rules_equal_encoded_rules':True,
            'externally_loaded_runtime_tape':False,'oracle_claim':False,
            'readable_expanded_rule_list_in_final_tape':False}


if __name__=='__main__':
    print(json.dumps(independent_audit(),sort_keys=True))
