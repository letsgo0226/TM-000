#!/usr/bin/env python3
"""Offline source builder; not imported at G24 One-Liner runtime."""
from pathlib import Path
from G24_Cross_Domain_Godel_Core import DOMAINS, PRIMES, FORBIDDEN

SOURCE = r'''import sys,json
C=lambda v:v or sys.exit('BLOCKED')
x=json.load(sys.stdin)
C(type(x)==dict and set(x)=={'source','mode','permissions','events'} and x['source']=='SYNTHETIC' and x['mode']=='offline')
f=x['permissions'];C(type(f)==dict and set(f)==set('@FLAGS@'.split(',')) and all(v is False for v in f.values()))
d='@DOMAINS@'.split(',');p=@PRIMES@
a=[0]*len(d);n=1;es=x['events'];C(type(es)==list and len(es)<=56)
for e in es:
 C(type(e)==list and len(e)==2 and type(e[0])==str and e[0] in d and e[1] in ('ENTER_RESEARCH','RESET'))
 i=d.index(e[0]);v=int(e[1]=='ENTER_RESEARCH');C(a[i]!=v)
 if v:n*=p[i]
 else:C(n%p[i]==0);n//=p[i]
 a[i]=v
r=n;b=[]
for z in p:
 v=0
 while r%z==0:r//=z;v+=1;C(v<=1)
 b.append(v)
C(r==1 and b==a)
print(json.dumps(dict(version='G24',status='OFFLINE_CROSS_DOMAIN_RESEARCH_ONLY',prime_power_integer=n,prime_factors=[[z,v] for z,v in zip(p,b) if v],domain_phases={k:'RESEARCH_ONLY' if v else 'BLOCKED' for k,v in zip(d,b)},domains=len(d),events_replayed=len(es),full_numeric_roundtrip=True,digest_used=False,external_data_authenticated=False,independent_impact_verified=False,machine_universality_proved=False,all_dimensions_immortality_proved=False,world_peace_achieved=False,all_sdgs_achieved=False,cultivated_meat_safe_or_cruelty_free_proved=False,trader42_alpha_validated=False,orders_submitted=0,deployment_executed=False,human_review_required=True),sort_keys=True))'''


def build():
    py = SOURCE.replace('@FLAGS@', ','.join(FORBIDDEN))
    py = py.replace('@DOMAINS@', ','.join(DOMAINS)).replace('@PRIMES@', repr(list(PRIMES)))
    return ("python3 -c $'" + py.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n') + "'\n").encode()


if __name__ == '__main__':
    result = build()
    path = Path(__file__).with_name('Universal_G_G24_Cross_Domain_2KB.sh')
    path.write_bytes(result)
    print('bytes', len(result), 'physical lines', result.count(b'\n'))
