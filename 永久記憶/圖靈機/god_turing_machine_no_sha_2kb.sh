#!/bin/bash
python3 -c $'s=\'s=%r;src=s%%s\\nimport json\\ndef G(b):\\n n=1\\n for v in b:n=n*257+v+1\\n return n\\ndef D(n):\\n a=[]\\n while n>1:\\n  n,r=divmod(n,257);assert r;a.append(r-1)\\n return bytes(a[::-1])\\nb=src.encode();g=G(b);assert D(g)==b\\nR={(0,"1"):(0,"X",1),(0,"_"):(1,"_",0)}\\nT={i:"1" for i in range(len(b))};q=h=steps=0\\nwhile q!=1:\\n a=T.get(h,"_");q,v,m=R[(q,a)];T[h]=v;h+=m;steps+=1\\ncert={"godel":str(g),"length":len(b),"trace_steps":steps,"final_tape":"".join(T[i] for i in range(len(b)))}\\ndef verify(code,c):\\n return D(int(c["godel"]))==code and len(code)==c["length"] and c["trace_steps"]==len(code)+1 and c["final_tape"]=="X"*len(code)\\nprint(json.dumps({"self_reproduced":src==s%%s,"godel_roundtrip":D(g)==b,"N":len(b),"steps":steps,"verified":verify(b,cert),"certificate":cert},separators=(",",":")))\';src=s%s
import json
def G(b):
 n=1
 for v in b:n=n*257+v+1
 return n
def D(n):
 a=[]
 while n>1:
  n,r=divmod(n,257);assert r;a.append(r-1)
 return bytes(a[::-1])
b=src.encode();g=G(b);assert D(g)==b
R={(0,"1"):(0,"X",1),(0,"_"):(1,"_",0)}
T={i:"1" for i in range(len(b))};q=h=steps=0
while q!=1:
 a=T.get(h,"_");q,v,m=R[(q,a)];T[h]=v;h+=m;steps+=1
cert={"godel":str(g),"length":len(b),"trace_steps":steps,"final_tape":"".join(T[i] for i in range(len(b)))}
def verify(code,c):
 return D(int(c["godel"]))==code and len(code)==c["length"] and c["trace_steps"]==len(code)+1 and c["final_tape"]=="X"*len(code)
print(json.dumps({"self_reproduced":src==s%s,"godel_roundtrip":D(g)==b,"N":len(b),"steps":steps,"verified":verify(b,cert),"certificate":cert},separators=(",",":")))'
