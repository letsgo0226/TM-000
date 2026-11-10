#!/usr/bin/env python3
"""Independent G24S finite-domain arithmetical audit (no import from G24S core).

Recomputes all 12 prime exponents, their actual integer product and a full
numeric division, then compares separately run one-line engine output.
Neither auditor nor engine makes network, trading, or deployment requests.
"""
import json
from pathlib import Path
import subprocess
import sys

DOMAINS = ('universal_tm','automated_deployment','ai_continuity','human_longevity',
           'interspecies_welfare','ecological_continuity','global_peace','sdgs',
           'cultivated_meat','psychosocial','philosophical','trader42')
ROOT=Path(__file__).resolve().parent


def check(source=None, binary=None):
    source=Path(source or ROOT/'G24S_example_request.json')
    binary=Path(binary or ROOT/'Universal_G_G24S_Cross_Domain_2KB.sh')
    data=source.read_bytes()
    if len(data)>16384 or not data:raise ValueError('invalid offline fixture length')
    request=json.loads(data)
    if (set(request) != {'source','mode','human_review','domains','network',
                         'deployment','trading','credentials','external_action'} or
        request['source']!='SYNTHETIC' or request['mode']!='offline' or
        request['human_review'] is not True or
        any(request[v] is not False for v in ('network','deployment','trading','credentials','external_action'))):
        raise ValueError('external authority or schema not allowed')
    if set(request['domains'])!=set(DOMAINS):raise ValueError('domain mismatch')
    prime_values=[]
    n=2
    while len(prime_values)<14:
        if not any(n%p==0 for p in prime_values if p*p<=n):prime_values.append(n)
        n+=1
    integer=1;expected=[];states=[];writes=0
    for i,name in enumerate(DOMAINS):
        pair=request['domains'][name]
        if type(pair)!=list or len(pair)!=2 or type(pair[0])!=int or not 0<=pair[0]<=100 or type(pair[1])!=bool:
            raise ValueError('invalid domain evidence')
        count,veto=pair
        state=3 if veto else 2 if count>=3 else 1
        integer*=prime_values[i+2]
        writes+=1
        if state>1:
            integer*=prime_values[i+2]**(state-1)
            writes+=1
        states.append(state)
        expected.append({'domain':name,'synthetic_checks':count,'veto':veto,
                         'state':('EVIDENCE_GAP','SYNTHETIC_REVIEW_ONLY','VETOED')[state-1]})
    remainder=integer
    observed=[]
    for prime in prime_values[2:]:
        e=0
        while remainder%prime==0:
            remainder//=prime;e+=1
            if e>3:raise ValueError('non-canonical exponent')
        observed.append(e)
    if observed!=states or remainder!=1:raise ValueError('numeric register mismatch')
    whole=2**3*3**13*integer
    p=subprocess.run(['bash',str(binary)],input=data,capture_output=True,timeout=8,check=False)
    if p.returncode:raise ValueError('one-line engine rejected valid fixture')
    report=json.loads(p.stdout)
    if (report.get('version')!='G24S' or report.get('status')!='CROSS_DOMAIN_SYNTHETIC_REVIEW_ONLY'
        or report.get('master')!='UTM-PLEIADES-v0.2-PTCA'
        or report.get('exact_numeric_roundtrip') is not True
        or report.get('configuration_roundtrip') is not True
        or report.get('sha_used') is not False
        or report['domains']!=expected or report['prime_power_integer_bits']!=integer.bit_length()
        or report['configuration_integer_bits']!=whole.bit_length()
        or report['prime_power_transition_count']!=writes
        or report['registered']!=12 or report['domain_count']!=12
        or report['synthetic_reviewed']!=states.count(2)
        or report['evidence_gaps']!=states.count(1)
        or report['vetoed']!=states.count(3)
        or report['approved_external_actions']!=0
        or report['network_calls']!=0
        or report['deployment_allowed'] or report['trading_allowed']
        or report['real_world_outcomes_proved'] or report['all_dimensions_immortality_proved']):
        raise ValueError('G24S one-line cross-domain semantic mismatch')
    return {'version':'G24S','status':'INDEPENDENT_PRIME_POWER_DOMAINS_VERIFIED',
            'domains_checked':12, 'prime_power_writes':writes,
            'integer_bits':integer.bit_length(),'configuration_bits':whole.bit_length(),
            'full_integer_factorization':True, 'identical_12_domain_report':True,
            'external_calls':0, 'real_outcomes_proved':False}

if __name__=='__main__':
    try:
        print(json.dumps(check(),sort_keys=True))
    except (OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired) as error:
        print('BLOCKED: '+str(error),file=sys.stderr)
        raise SystemExit(1)
