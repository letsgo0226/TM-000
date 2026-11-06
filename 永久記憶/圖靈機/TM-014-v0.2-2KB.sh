#!/bin/sh
exec python3 -c 'import sys,json
try:
 a=json.load(open(sys.argv[1])) if len(sys.argv)>1 else {"rules":[["q","1","q","1",1]],"input":"111","start":"q","halt":["H"]};N=int(sys.argv[2]) if len(sys.argv)>2 else 20
 assert 0<=N<=1000000 and isinstance(a,dict)
 b=a.get("blank","_");s=a["start"];h=a["halt"];r=a["rules"];w=a.get("input","")
 assert all(isinstance(z,str) and len(z)==1 for z in [b,*w]) and isinstance(s,str) and isinstance(h,list) and all(isinstance(z,str) for z in h) and isinstance(r,list)
 d={}
 for q,c,t,v,m in r:
  assert isinstance(q,str) and isinstance(t,str) and isinstance(c,str) and isinstance(v,str) and len(c)==len(v)==1 and type(m)==int and m in (-1,0,1) and (q,c) not in d
  d[q,c]=(t,v,m)
 p=0;t={i:c for i,c in enumerate(w) if c!=b};seen={};hist=[];cycle=None;status="UNKNOWN";k=0
 while k<N+1:
  if s in h:status="HALTED";break
  key=(s,p,tuple(sorted(t.items())))
  if key in seen:status="PROVEN_NONHALTING";cycle=[seen[key],k];break
  if k==N:break
  seen[key]=k;z=d.get((s,t.get(p,b)))
  if z is None:status="HALTED";break
  hist.append([s,p,sorted(t.items())]);s,v,m=z
  if v==b:t.pop(p,None)
  else:t[p]=v
  p+=m;k+=1
 out={"system":"TM-014/v0.2","status":status,"steps":k,"state":s,"head":p,"tape":sorted(t.items()),"bound":N}
 if len(sys.argv)>3 and sys.argv[3]=="--cert":out.update(machine=a,trace=hist,cycle=cycle)
 print(json.dumps(out,separators=(",",":")))
except (Exception) as e:
 print(json.dumps({"system":"TM-014/v0.2","status":"INVALID","reason":str(e)},separators=(",",":")))' "$@"
