#!/usr/bin/env python3
"""Build the single-line G23 from G22's controller bits (digest-free)."""
from pathlib import Path
from G22_Blank_Tape_TM_core import rule_table_A, encode_A
h=format(int(encode_A(rule_table_A()),2),'0270x')
code="""import json,sys
C=lambda b:b or sys.exit('BLOCKED')
x=''.join(format(int(z,16),'04b') for z in '@HEX@')
a=['_','0','1','E0','E1','P0','P1','F0','F1'];f={}
for k in range(0,len(x),18):
 r=x[k:k+18];q=int(r[:4],2);v=int(r[4:8],2);w=int(r[8:12],2);d=int(r[12:14],2);n=int(r[14:],2);C(q<9 and v<9 and w<9 and d<3 and n<10 and (q,a[v]) not in f);f[q,a[v]]=a[w],'LRS'[d],n
for i,z in enumerate(x):f[10+i,'_']=z,'R',10+i+1 if i+1<len(x) else 0
p=[];n=2
while len(p)<6004:
 if all(n%d for d in p if d*d<=n):p.append(n)
 n+=1
t={};q=10;i=s=0;G=1
while q!=9 and s<4000000:
 old=t.get(i,0);C(-3000<=i<=3000);v,d,q=f[q,a[old]];new=a.index(v)
 if new!=old:
  z=p[2+ (2*i if i>=0 else -2*i-1)];G=G*z**(new-old) if new>old else G//z**(old-new)
  if new:t[i]=new
  else:t.pop(i,None)
 i+=(d=='R')-(d=='L');s+=1
C(q==9 and len(t)==2*len(x))
y=''.join(a[t[j]] for j in range(2*len(x)));C(y==x+x)
N=G;u={}
for k,z in enumerate(p[2:],start=2):
 v=0
 while N%z==0:N//=z;v+=1;C(v<9)
 if v:u[(k-2)//2 if k%2==0 else -(k-1)//2]=v
C(N==1 and u==t)
H=G*2**(q+1)*3**((2*i if i>=0 else -2*i-1)+1)
C(H%(2**(q+2))!=0 and H%(3**((2*i if i>=0 else -2*i-1)+2))!=0)
print(json.dumps(dict(version='G23',steps=s,rules=len(f),bits=len(y),integer_bits=G.bit_length(),full_configuration_integer_bits=H.bit_length(),state_head_prime_powers=True,exact_numeric_decode=True,prime_power_arithmetic=True,bitwise_verified=True,sha_used=False,orders=0),sort_keys=True))""".replace('@HEX@',h)
shell="python3 -c $'"+code.replace('\\','\\\\').replace("'","\\'").replace('\n','\\n')+"'\n"
Path(__file__).with_name('Universal_G_G23_Prime_Power_2KB.sh').write_text(shell,encoding='utf-8')
print('bytes',len(shell.encode('utf-8')))
