#!/usr/bin/env python3
"""G22: explicit deterministic single-tape self-printer under full binary table code.

The TM starts on a blank tape, does not read program files or obtain its own
transition table from an oracle, and emits its own *complete, reversibly
specified binary transition-table encoding* to its final tape. The specialized
canonical encoding (not literal expanded JSON table) is documented below.

This builder/checker is EXTERNAL to the machine; execution is entirely
interpretation of an explicit fixed finite transition table.
"""
import json
from pathlib import Path

ALPHABET = ('_', '0', '1', 'E0', 'E1', 'P0', 'P1', 'F0', 'F1')
DIRECTIONS = ('L', 'R', 'S')
A_NAMES = ('begin', 'mark_end', 'seek_left', 'seek_next', 'append_0',
           'append_1', 'return_left', 'cleanup_left', 'cleanup_right', 'HALT')
BLANK = '_'
PRINTER_START = 10
RECORD_BITS = 18


def rule_table_A():
    """The finite duplication controller A; only one-tape symbol transitions."""
    rows = []
    def add(q, read, write, move, next_q):
        if not (0 <= q <= 8 and 0 <= next_q <= 9):
            raise ValueError('invalid controller state')
        rows.append((q, read, write, move, next_q))
    add(0, '_', '_', 'L', 1)
    add(1, '0', 'E0', 'L', 2)
    add(1, '1', 'E1', 'L', 2)
    nonblank = ALPHABET[1:]
    for symbol in nonblank:
        add(2, symbol, symbol, 'L', 2)
    add(2, '_', '_', 'R', 3)
    for symbol in ('P0','P1'):
        add(3, symbol, symbol, 'R', 3)
    for symbol, mark, state in (('0','P0',4), ('1','P1',5), ('E0','F0',4), ('E1','F1',5)):
        add(3, symbol, mark, 'R', state)
    for symbol in ('F0','F1'):
        add(3, symbol, symbol, 'L', 7)
    for which, write in ((4, '0'), (5,'1')):
        for symbol in nonblank:
            add(which, symbol, symbol, 'R', which)
        add(which, '_', write, 'L', 6)
    for symbol in nonblank:
        add(6, symbol, symbol, 'L', 6)
        add(7, symbol, symbol, 'L', 7)
    add(6, '_', '_', 'R', 3)
    add(7, '_', '_', 'R', 8)
    for symbol, replacement in (('P0','0'),('P1','1')):
        add(8, symbol, replacement, 'R', 8)
    for symbol, replacement in (('F0','0'),('F1','1')):
        add(8, symbol, replacement, 'S', 9)
    return sorted(rows, key=lambda row: (row[0], ALPHABET.index(row[1])))


def encode_A(A):
    """Explicit 18-bit fixed-width records: q(4),read(4),write(4),dir(2),next(4)."""
    values = []
    for q, read, write, direction, next_q in A:
        fields = ((q,4), (ALPHABET.index(read),4),
                  (ALPHABET.index(write),4), (DIRECTIONS.index(direction),2),
                  (next_q,4))
        values.append(''.join(f'{value:0{n}b}' for value,n in fields))
    return ''.join(values)


def decode_A(bits):
    if not isinstance(bits, str) or len(bits) % RECORD_BITS or not bits or any(c not in '01' for c in bits):
        raise ValueError('noncanonical controller binary representation')
    result = []
    for i in range(0,len(bits),RECORD_BITS):
        rec=bits[i:i+RECORD_BITS]
        q=int(rec[0:4],2); read=int(rec[4:8],2); write=int(rec[8:12],2)
        direction=int(rec[12:14],2); nxt=int(rec[14:18],2)
        if not(q<=8 and read<len(ALPHABET) and write<len(ALPHABET) and direction<=2 and nxt<=9):
            raise ValueError('unknown A machine state/symbol')
        result.append((q,ALPHABET[read],ALPHABET[write],DIRECTIONS[direction],nxt))
    if len({(q,read) for q,read,*_ in result}) != len(result):
        raise ValueError('duplicate transition')
    if encode_A(sorted(result, key=lambda x:(x[0],ALPHABET.index(x[1])))) != bits:
        raise ValueError('noncanonical rule order')
    return result


def machine_from_canonical_code(code):
    """Reversibly decode *every* TM transition from the full canonical binary code.

    Canonical code = X||Y, |X|=|Y|, X explicit 18-bit A rule records,
    Y write symbols for chain states B_0..B_|Y|-1. Each B transition on blank
    writes Y[i], moves right, and enters B_(i+1), or A entry at the last.
    The whole code determines all A and B transitions, start state, and halt.
    """
    if not isinstance(code,str) or len(code)%2 or any(c not in '01' for c in code):
        raise ValueError('invalid paired code')
    mid = len(code)//2
    a = decode_A(code[:mid]); y=code[mid:]
    transitions = {(q, read): (write, move, nxt) for q,read,write,move,nxt in a}
    for i, char in enumerate(y):
        transitions[(PRINTER_START+i,'_')] = (char,'R',PRINTER_START+i+1 if i+1<len(y) else 0)
    return transitions


def encode_full_table(transitions):
    a=[(q,read,write,move,nextq) for (q,read),(write,move,nextq) in transitions.items() if q<PRINTER_START]
    a=sorted(a,key=lambda x:(x[0],ALPHABET.index(x[1])))
    X=encode_A(a)
    y=[]
    for i in range(len(X)):
        actual=transitions.get((PRINTER_START+i,'_'))
        expected_next=PRINTER_START+i+1 if i+1<len(X) else 0
        if actual is None or actual[0] not in ('0','1') or actual[1:]!=('R',expected_next):
            raise ValueError('noncanonical printer transition')
        y.append(actual[0])
    if len(transitions)!=len(a)+len(y):
        raise ValueError('extra transition')
    return X+''.join(y)


def create_self_printer():
    X=encode_A(rule_table_A())
    M=machine_from_canonical_code(X+X)
    if encode_full_table(M)!=X+X:
        raise ValueError('serialization is not inverse')
    return M, X+X


def simulate(transitions, max_steps=10_000_000):
    """Low-level TM ONLY: from entirely blank tape, state=B0, head=0."""
    tape={};head=0;state=PRINTER_START;steps=0
    while state!=9:
        if steps>=max_steps: return dict(status='STEP_LIMIT',steps=steps,head=head,tape=tape, state=state)
        read=tape.get(head,BLANK)
        rule=transitions.get((state,read))
        if rule is None: return dict(status='STUCK',steps=steps,head=head,tape=tape,state=state)
        write,direction,nxt=rule
        if write==BLANK: tape.pop(head,None)
        else: tape[head]=write
        head += (direction=='R')-(direction=='L')
        state=nxt;steps+=1
    return dict(status='HALTED', steps=steps, head=head, tape=tape, state=state)


def extract_output(result, expected_len):
    if result['status']!='HALTED':raise ValueError('machine did not halt')
    tape=result['tape']
    if set(tape)!=set(range(expected_len)):
        raise ValueError('missing/extra output tape cells')
    value=''.join(tape[i] for i in range(expected_len))
    if any(c not in '01' for c in value):raise ValueError('leftover work marker')
    return value


def audit(max_steps=10_000_000):
    M,code=create_self_printer()
    final=simulate(M,max_steps)
    output=extract_output(final,len(code))
    if output != code: raise ValueError('bit-for-bit output mismatch')
    decoded = machine_from_canonical_code(output)
    if decoded != M: raise ValueError('complete transition table mismatch')
    if encode_full_table(decoded) != output: raise ValueError('reversible table mismatch')
    expanded=[{'state':q,'read':read,'write':write,'move':direction,'next':next_q}
      for (q,read),(write,direction,next_q) in sorted(M.items(), key=lambda kv:(kv[0][0],ALPHABET.index(kv[0][1])))]
    return {'version':'G22','status':'BLANK_TAPE_SELF_TABLE_CODE_VERIFIED',
            'initial_tape':'BLANK','tape_count':1,'deterministic':True,
            'A_rule_count':len(rule_table_A()),'printer_rule_count':len(code)//2,
            'total_rules':len(M),'canonical_code_bits':len(code),
            'steps':final['steps'],'head':final['head'],
            'output_equals_expected_bits': output == code,
            'decoded_table_equals_original': decoded == M,
            'serialization_roundtrip': encode_full_table(decoded) == output,
            'complete_table_roundtrip':True,'output_equals_own_full_table_code':True,
            'expanded_transition_table':expanded,'canonical_code':code,
            'full_rule_list_printed_as_json':False,
            'source_file_read_by_tm':False,'external_tape_input':False,
            'halt_oracle':False,'divinity_proved':False,'production_deployed':False}


if __name__=='__main__':
    report=audit()
    root=Path(__file__).resolve().parent
    (root/'G22_canonical_table_bits.txt').write_text(report['canonical_code']+'\n')
    (root/'G22_expanded_transition_table.json').write_text(json.dumps(report['expanded_transition_table'],ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('canonical_code','expanded_transition_table')},sort_keys=True))
