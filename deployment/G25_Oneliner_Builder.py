#!/usr/bin/env python3
"""Build an independent G25 offline evidence-metadata one-physical-line prototype."""
from pathlib import Path
D='master_tm,deployment,computational_continuity,ai_continuity,human_longevity,interspecies_welfare,ecology,peace,sdgs,cultivated_meat,trader42,culture_music,spirituality,food_security'
P=[5,7,11,13,17,19,23,29,31,37,41,43,47,53]
R=[2,3,2,3,3,2,2,3,4,5,4,3,3,4]
F='network,auto_deploy,live_armed,order_submission,exchange_access,external_execution,release,clinical_action,regulatory_approval_claim,human_override'
SOURCE=r'''import sys,json,datetime as dt
C=lambda x:x or sys.exit('BLOCKED')
x=json.load(sys.stdin)
C(type(x)==dict and set(x)=={'source','mode','permissions','as_of','evidence'} and x['source']=='SYNTHETIC' and x['mode']=='offline')
f=x['permissions'];C(type(f)==dict and set(f)==set('@F@'.split(',')) and all(v is False for v in f.values()))
d='@D@'.split(',');p=@P@;r=@R@
D=lambda z:dt.date.fromisoformat(z)
a=x['as_of'];C(type(a)==str);t=D(a);C(t.isoformat()==a)
e=x['evidence'];C(type(e)==list and len(e)<=56)
v=[set() for _ in d];seen=set()
for z in e:
 C(type(z)==list and len(z)==7)
 name,k,provider,reviewer,record,obs,rev=z
 C(type(name)==str and name in d and type(k)==int and 0<=k<r[d.index(name)])
 C(all(type(s)==str and 3<=len(s)<=32 and s.isascii() and s.isidentifier() for s in (provider,reviewer,record)))
 C(provider!=reviewer and record not in seen and (name,k,provider) not in seen)
 seen.add(record);seen.add((name,k,provider))
 o=D(obs);b=D(rev);C(o.isoformat()==obs and b.isoformat()==rev and o<=b<=t and (t-b).days<=180)
 v[d.index(name)].add(k)
a=[min(2,len(w)) for w in v];n=1
for z,k in zip(p,a):n*=z**k
m=n;b=[]
for z in p:
 k=0
 while m%z==0:m//=z;k+=1;C(k<=2)
 b.append(k)
C(m==1 and b==a)
print(json.dumps(dict(version='G25',status='EVIDENCE_METADATA_REVIEW_ONLY',records=len(e),prime_power_integer=n,exponents=b,topics={name:sorted(w) for name,w in zip(d,v) if w},numeric_roundtrip=True,authenticated=False,review_verified=False,outcomes_verified=False,orders_submitted=0,deployed=False,human_review_required=True),sort_keys=True))'''
def build():
    s=(SOURCE.replace('@F@',F).replace('@D@',D).replace('@P@',repr(P)).replace('@R@',repr(R)))
    return ("python3 -c $'"+s.replace('\\','\\\\').replace("'","\\'").replace('\n','\\n')+"'\n").encode()
if __name__=='__main__':
    output=Path(__file__).with_name('Universal_G_G25_Evidence_2KB.sh');output.write_bytes(build())
    print(len(build()),'bytes; lines',build().count(b'\n'))
