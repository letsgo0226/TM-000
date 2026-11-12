#!/usr/bin/env python3
"""Build limited, self-contained report consistency auditor. NOT the G28 explorer."""
from pathlib import Path

PYTHON = '''import json,sys
C=lambda v:v or sys.exit('BLOCKED')
x=json.load(sys.stdin)
C(x['version']=='G28' and x['status']=='OFFLINE_UNTESTED_HYPOTHESES')
t=x['audit_trace'];a=x['archive'];b=x['random_baseline_archive'];n=x['proposals_scored']
C(type(n)==int and 1<=n<=512 and n<=x['budget_requested'] and n<=x['candidate_universe'])
C(type(t)==list and len(t)==n and len({v['id'] for v in t})==n)
C([v['step'] for v in t]==list(range(1,n+1)))
C(len(a)==x['quality_diversity_occupied_cells'] and len(b)==x['random_baseline_occupied_cells'])
C(all(len({tuple(v['descriptor']) for v in k})==len(k) for k in (a,b)))
C(sum(v['synthetic_priority'] for v in a)==x['quality_diversity_sum_synthetic_priority'])
C(sum(v['synthetic_priority'] for v in b)==x['random_baseline_sum_synthetic_priority'])
C(all(v['status']=='UNTESTED_HYPOTHESIS' and v['observed_evidence'] is False and v['scientific_claim_proved'] is False for k in (a,b) for v in k))
C(x['actual_experiments_performed']==0 and x['evidence_independently_verified'] is False and x['predicted_real_world_outcomes'] is False)
C(x['platform_restrictions_bypassed'] is False and x['unbounded_computation_claimed'] is False and x['deployment_performed'] is False and x['live_orders_submitted']==0)
C(x['sha_used'] is False and x['human_review_required'] is True and x['surrogate_lookahead_inspections']>=n)
print(json.dumps(dict(version='G28_AUDIT',status='REPORT_CONSISTENT_NOT_AUTHENTICATED',records=n,cells=len(a),experiments=0,external_action=False),sort_keys=True))'''


def build():
    return ("python3 -c $'" + PYTHON.replace('\\', '\\\\').replace("'", "\\'")
            .replace('\n', '\\n') + "'\n").encode('utf-8')


if __name__ == '__main__':
    output = build()
    if output.count(b'\n') != 1 or len(output) > 2048:
        raise SystemExit(f'EXCEEDS_2KB: {len(output)}')
    Path(__file__).with_name('G28_Research_Report_Audit_2KB.sh').write_bytes(output)
    print('one_liner_bytes', len(output))
