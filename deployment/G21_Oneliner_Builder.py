#!/usr/bin/env python3
"""Generate a self-contained shell harness containing G21 fixed controller table bits.

The _machine_ starts blank. The Shell program only instantiates and checks
its finite transition table; it is not the self-printing transition table.
"""
from pathlib import Path
from G21_Blank_Tape_TM_core import rule_table_A, encode_A
X=encode_A(rule_table_A())
assert len(X)==1080
h=f'{int(X,2):0270x}'
source='''import json,hashlib,sys
C=lambda b:b or sys.exit('BLOCKED')
x=''.join(format(int(z,16),'04b') for z in '~HEX~')
a=['_','0','1','E0','E1','P0','P1','F0','F1'];f={}
for k in range(0,len(x),18):
 r=x[k:k+18];q=int(r[:4],2);v=int(r[4:8],2);w=int(r[8:12],2);d=int(r[12:14],2);n=int(r[14:],2);C(q<9 and v<9 and w<9 and d<3 and n<10 and (q,a[v]) not in f);f[q,a[v]]=a[w],'LRS'[d],n
for i,z in enumerate(x):f[10+i,'_']=z,'R',10+i+1 if i+1<len(x) else 0
t={};q=10;i=s=0
while q!=9 and s<10000000:
 k=(q,t.get(i,'_'));C(k in f);v,d,q=f[k]
 if v=='_':t.pop(i,None)
 else:t[i]=v
 i+=(d=='R')-(d=='L');s+=1
C(q==9 and len(t)==2*len(x))
y=''.join(t[j] for j in range(2*len(x)));C(y==x+x)
print(json.dumps(dict(version='G21',status='BLANK_TAPE_SELF_TABLE_CODE_VERIFIED',rules=len(f),bits=len(y),steps=s,sha256=hashlib.sha256(y.encode()).hexdigest(),blank_tape=True,no_external_input=True,decoded_complete_table=True,printed_expanded_json=False),sort_keys=True))'''.replace('~HEX~',h)
file="python3 -c $'"+source.replace('\\','\\\\').replace("'","\\'").replace('\n','\\n')+"'\n"
Path(__file__).with_name('Universal_G_G21_Blank_Tape_TM_2KB.sh').write_text(file)
print('bits',len(X),'hex',len(h),'one_liner_bytes',len(file.encode()), 'one line',file.count('\n')==1)
