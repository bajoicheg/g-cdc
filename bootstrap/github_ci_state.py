#!/usr/bin/env python3
"""Inspect three GitHub CI surfaces; advisory snapshot, never release authority.

--requests emits read-only API URLs for the authorized connector. --snapshot
reads their decoded responses under statuses/checks/actions, plus repository
and head_sha. Use null for a failed or unavailable read, never an empty list.
"""
import argparse
import json
from pathlib import Path
import re

WORKFLOW = '.github/workflows/release-validation.yml'
CHECK = 'Bootstrap + package + three consumers'
ACTIVE = {'queued', 'in_progress', 'requested', 'waiting', 'pending'}


def requests(repository, sha):
    if not isinstance(repository, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('repository must be owner/name')
    if not isinstance(sha, str) or not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('head_sha must be a full lowercase commit SHA')
    base = f'https://api.github.com/repos/{repository}'
    return {'statuses': f'{base}/commits/{sha}/status',
            'checks': f'{base}/commits/{sha}/check-runs?per_page=100',
            'actions': f'{base}/actions/runs?head_sha={sha}&per_page=100'}


def _collection(data, key):
    if data is None:
        return [], False
    if not isinstance(data, dict) or not isinstance(data.get(key), list):
        raise ValueError(f'invalid {key} response; use null for a failed read')
    total = data.get('total_count')
    if type(total) is not int or total < len(data[key]):
        raise ValueError(f'invalid total_count for {key}')
    if not all(isinstance(item, dict) for item in data[key]):
        raise ValueError(f'invalid {key} item')
    return data[key], total == len(data[key])


def assess(snapshot):
    if not isinstance(snapshot, dict):
        raise ValueError('snapshot must be an object')
    repo, sha = snapshot.get('repository'), snapshot.get('head_sha')
    urls = requests(repo, sha)
    statuses, sc = _collection(snapshot.get('statuses'), 'statuses')
    checks, cc = _collection(snapshot.get('checks'), 'check_runs')
    runs, ac = _collection(snapshot.get('actions'), 'workflow_runs')
    if snapshot.get('statuses') is not None and snapshot['statuses'].get('sha') != sha:
        raise ValueError('legacy status response is for another commit')
    for run in runs:
        repository = run.get('repository')
        if not isinstance(repository, dict) or not isinstance(repository.get('full_name'), str):
            raise ValueError('invalid workflow run repository identity')
    exact_runs = [r for r in runs if r.get('head_sha') == sha
                  and str(r.get('path', '')).split('@', 1)[0] == WORKFLOW
                  and r.get('repository', {}).get('full_name', '').lower() == repo.lower()]
    exact_checks = [c for c in checks if c.get('head_sha') == sha and c.get('name') == CHECK]
    complete = sc and cc and ac
    run_active = any(r.get('status') in ACTIVE for r in exact_runs)
    check_active = any(c.get('status') in ACTIVE for c in exact_checks)
    if run_active or (check_active and not exact_runs):
        state, action = 'running', 'observe_existing_run'
    elif check_active and exact_runs:
        state, action = 'inconsistent', 'refresh_run_and_check_attempts'
    elif not complete:
        state, action = 'unknown', 'complete_ci_inventory'
    elif exact_runs and all(r.get('status') == 'completed' and r.get('conclusion') == 'success' for r in exact_runs) \
            and all(c.get('status') == 'completed' and c.get('conclusion') == 'success' for c in exact_checks) \
            and all(s.get('state') == 'success' for s in statuses):
        state, action = 'workflow_succeeded', 'verify_scope_and_required_release_evidence'
    elif exact_runs or exact_checks or statuses:
        state, action = 'needs_inspection', 'inspect_jobs_logs_and_run_attempts'
    else:
        state, action = 'no_observed_run', 'inspect_workflow_triggers_and_authorized_execution_routes'
    return {'repository': repo, 'head_sha': sha, 'state': state, 'next_action': action,
            'inventory_complete': complete, 'workflow_run_ids': [r.get('id') for r in exact_runs],
            'requests': urls, 'snapshot_only': True,
            'execution_unavailable_proven': False, 'release_ready': False,
            'authorizes_external_start': False, 'authorizes_product_write': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--requests', nargs=2, metavar=('OWNER/REPO', 'HEAD_SHA'))
    group.add_argument('--snapshot', type=Path)
    args = parser.parse_args(argv)
    try:
        result = requests(*args.requests) if args.requests else assess(json.loads(args.snapshot.read_text()))
    except (ValueError, OSError) as exc:
        parser.exit(2, f'CI_PROBE_RED: {exc}\n')
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
