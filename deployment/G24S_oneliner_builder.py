#!/usr/bin/env python3
"""Regenerate G24S single physical-line plaintext Bash + Python entrypoint."""
from pathlib import Path

PYTHON = '''import json,sys
C=lambda v:v or sys.exit('BLOCKED')
s=sys.stdin.buffer.read(16385);C(0<len(s)<=16384);x=json.loads(s)
a='universal_tm automated_deployment ai_continuity human_longevity interspecies_welfare ecological_continuity global_peace sdgs cultivated_meat psychosocial philosophical trader42'.split()
f='network deployment trading credentials external_action'.split()
C(type(x)==dict and set(x)==set(['source','mode','human_review','domains']+f) and x['source']=='SYNTHETIC' and x['mode']=='offline' and x['human_review'] is True and all(x[k] is False for k in f))
d=x['domains'];C(type(d)==dict and set(d)==set(a))
p=[];n=2
while len(p)<14:
 if all(n%v for v in p if v*v<=n):p.append(n)
 n+=1
G=1;b=[];e=[];w=0
for i,k in enumerate(a):
 z=d[k];C(type(z)==list and len(z)==2 and type(z[0])==int and 0<=z[0]<=100 and type(z[1])==bool)
 c,v=z;h=3 if v else 2 if c>=3 else 1
 G*=p[i+2];w+=1
 if h>1:G*=p[i+2]**(h-1);w+=1
 b.append(h)
 e.append(dict(domain=k,state=('EVIDENCE_GAP','SYNTHETIC_REVIEW_ONLY','VETOED')[h-1],synthetic_checks=c,veto=v))
N=G;r=[]
for z in p[2:]:
 v=0
 while N%z==0:N//=z;v+=1;C(v<=3)
 r.append(v)
C(N==1 and r==b)
H=2**3*3**13*G;C(H//(2**3*3**13)==G and H%(2**4)!=0 and H%(3**14)!=0)
print(json.dumps(dict(version='G24S',status='CROSS_DOMAIN_SYNTHETIC_REVIEW_ONLY',parent='G23_PRIME_POWER_TM',master='UTM-PLEIADES-v0.2-PTCA',domains=e,domain_count=12,registered=12,synthetic_reviewed=b.count(2),evidence_gaps=b.count(1),vetoed=b.count(3),prime_power_integer_bits=G.bit_length(),configuration_integer_bits=H.bit_length(),prime_power_transition_count=w,exact_numeric_roundtrip=True,configuration_roundtrip=True,approved_external_actions=0,network_calls=0,deployment_allowed=False,trading_allowed=False,real_world_outcomes_proved=False,all_dimensions_immortality_proved=False,source_authenticity_proved=False,sha_used=False),ensure_ascii=False,sort_keys=True,separators=(',',':')))'''


def build():
    return ("python3 -c $'"+PYTHON.replace('\\','\\\\').replace("'","\\'").replace('\n','\\n')+"'\n").encode('utf-8')

if __name__ == '__main__':
    path=Path(__file__).with_name('Universal_G_G24S_Cross_Domain_2KB.sh')
    path.write_bytes(build())
    print('bytes=',path.stat().st_size,'physical_lines=',path.read_bytes().count(b'\n'))
