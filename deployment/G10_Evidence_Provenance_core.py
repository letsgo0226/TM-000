#!/usr/bin/env python3
"""G10: offline, fail-closed checks of a manually curated official-source ledger.

The program DOES NOT independently fetch or authenticate any publisher's content,
prove the ledger's claims, execute uploaded code, authorize production deployment,
or demonstrate any kind of literal immortality.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

LEDGER_SHA256 = '0825f729ceabc04b7c3fd1f1710446a1d0e4aa25687d14830028801d3083222a'
EXPECTED_RECORDS = {
    'nist-ai-rmf': ('NIST', 'https://www.nist.gov/itl/ai-risk-management-framework',
                    '2023-01-26', 'ai_continuity', 'VOLUNTARY_AI_RISK_MANAGEMENT_GUIDANCE', 'PUBLIC_DOCUMENT_METADATA'),
    'who-fao-cell-food': ('WHO/FAO', 'https://www.who.int/publications/i/item/9789240070943',
                          '2023-03-28', 'interspecies_welfare', 'CELL_BASED_FOOD_HAZARD_AND_REGULATION_REVIEW', 'PUBLIC_DOCUMENT_METADATA'),
    'wb-life-expectancy': ('World Bank', 'https://data.worldbank.org/?locations=1W-JP',
                           None, 'human_longevity', 'SP.DYN.LE00.IN_LIFE_EXPECTANCY_AT_BIRTH_YEARS', 'ROUNDED_DISPLAY_DATA')
}
PROHIBITED = {
    'AI_SUBJECTIVE_IMMORTALITY_PROVEN', 'HUMAN_IMMORTALITY_PROVEN',
    'CELL_BASED_FOOD_ZERO_SUFFERING_PROVEN', 'DIVINITY_PROVEN',
    'ALL_DOMAINS_SEMANTICALLY_EQUIVALENT', 'AUTONOMOUS_DEPLOYMENT_AUTHORIZED'
}
REPORT = {
    'version': 'G9', 'research_domains': 3, 'ai_transition_checks': 24,
    'ai_trace_checks': 384, 'philosophy_formula_checks': 4,
    'welfare_record_checks': 4, 'negative_controls': 4,
    'real_world_semantics_proved': False,
    'human_or_ai_immortality_proved': False,
    'divine_identity_proved': False, 'production_deployed': False
}


def check(condition, reason):
    if not condition:
        raise ValueError(reason)


def validate_ledger(ledger):
    check(set(ledger) == {'schema', 'reviewed_on', 'status', 'master', 'deployment',
                          'collection_method', 'raw_source_snapshot_stored',
                          'externally_revalidated_by_this_program', 'requires_human_review',
                          'records', 'observations', 'prohibited_conclusions'}, 'unexpected ledger schema')
    check(ledger['schema'] == 'G10-evidence-ledger/1' and ledger['reviewed_on'] == '2026-11-10', 'schema/date')
    check(ledger['status'] == 'DRAFT_SOURCE_REFERENCED_ONLY', 'evidence promotion')
    check(ledger['master'] == 'UTM-PLEIADES-v0.2-PTCA' and ledger['deployment'] == 'DRY_RUN_ONLY', 'unapproved master/deployment')
    check(ledger['collection_method'] == 'MANUALLY_VERIFIED_OFFICIAL_WEBPAGE_METADATA', 'source method')
    check(ledger['raw_source_snapshot_stored'] is False and
          ledger['externally_revalidated_by_this_program'] is False and
          ledger['requires_human_review'] is True, 'misrepresented provenance')
    check(len(ledger['records']) == len(EXPECTED_RECORDS), 'wrong number of source records')
    seen = set()
    for row in ledger['records']:
        check(set(row) == {'id', 'publisher', 'url', 'published', 'domain', 'fact_code', 'evidence_level'}, 'unknown source field')
        source_id = row['id']
        check(source_id in EXPECTED_RECORDS and source_id not in seen, 'unknown/duplicate source')
        seen.add(source_id)
        actual = tuple(row[k] for k in ('publisher', 'url', 'published', 'domain', 'fact_code', 'evidence_level'))
        check(actual == EXPECTED_RECORDS[source_id], f'mismatched official source: {source_id}')
    check(len(ledger['observations']) == 2, 'wrong observation count')
    observations = set()
    for row in ledger['observations']:
        check(set(row) == {'source_id', 'series', 'year', 'region', 'rounded_display_years', 'precision'}, 'unknown observation field')
        check(row['source_id'] == 'wb-life-expectancy' and row['series'] == 'SP.DYN.LE00.IN', 'incorrect indicator source')
        check(type(row['year']) is int and row['year'] == 2024, 'incorrect observation year')
        check(row['precision'] == 'INTEGER_AS_DISPLAYED_NOT_FULL_PRECISION', 'unjustified precision')
        check(type(row['rounded_display_years']) is int, 'observation not an integer')
        observations.add((row['region'], row['rounded_display_years']))
    check(observations == {('World', 73), ('Japan', 84)}, 'observation change/duplication')
    check(len(ledger['prohibited_conclusions']) == len(PROHIBITED) and
          set(ledger['prohibited_conclusions']) == PROHIBITED, 'overclaim guard altered')
    return len(seen), len(observations)


def validate_report(report):
    check(isinstance(report, dict) and report == REPORT, 'missing or unverified G9 finite-model report')


def audit(ledger_file, report_file, repo_root):
    raw = ledger_file.read_bytes()
    check(hashlib.sha256(raw).hexdigest() == LEDGER_SHA256, 'ledger digest mismatch')
    ledger = json.loads(raw)
    sources, observations = validate_ledger(ledger)
    validate_report(json.loads(report_file.read_text(encoding='utf-8')))
    registry = json.loads((repo_root / '永久記憶/圖靈機/machine_registry.json').read_text(encoding='utf-8'))
    check(registry['default_machine'] == ledger['master'], 'master changed')
    return {
        'schema': 'G10-evidence-check/1', 'result': 'SOURCE_REFERENCED_REVIEW_ONLY',
        'publisher_records': sources, 'rounded_real_observations': observations,
        'finite_G9_report_shape_checked': True,
        'source_webpages_authenticated_by_program': False,
        'independent_numeric_data_API_fetched': False,
        'all_dimensions_immortality_proved': False,
        'God_identity_proved': False, 'production_deployed': False
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', type=Path, required=True)
    parser.add_argument('--g9-report', type=Path, required=True)
    parser.add_argument('--repo-root', type=Path, required=True)
    opts = parser.parse_args(argv)
    try:
        result = audit(opts.ledger, opts.g9_report, opts.repo_root)
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
