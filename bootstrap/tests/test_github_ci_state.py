"""An empty legacy statuses array cannot conceal a real Actions run."""
import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
probe = __import__('github_ci_state') if importlib.util.find_spec('github_ci_state') else None
SHA = '0ddeaac476dde1625448b5ec97a885a53549f480'


def snapshot():
    return {'repository': 'bajoicheg/g-cdc', 'head_sha': SHA,
            'statuses': {'sha': SHA, 'total_count': 0, 'statuses': []},
            'checks': {'total_count': 1, 'check_runs': [
                {'head_sha': SHA, 'name': 'Bootstrap + package + three consumers',
                 'status': 'in_progress', 'conclusion': None}]},
            'actions': {'total_count': 1, 'workflow_runs': [
                {'id': 36406335587, 'head_sha': SHA, 'path': '.github/workflows/release-validation.yml',
                 'repository': {'full_name': 'bajoicheg/g-cdc'},
                 'status': 'in_progress', 'conclusion': None,
                 'html_url': 'https://github.com/bajoicheg/g-cdc/actions/runs/36406335587'}]}}


class GithubCIStateTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(probe, 'GitHub CI inventory reconciler is missing')

    def test_empty_legacy_statuses_does_not_hide_running_actions(self):
        result = probe.assess(snapshot())
        self.assertEqual(result['state'], 'running')
        self.assertEqual(result['next_action'], 'observe_existing_run')
        self.assertFalse(result['execution_unavailable_proven'])
        self.assertFalse(result['release_ready'])

    def test_requests_cover_three_independent_github_surfaces(self):
        urls = probe.requests('bajoicheg/g-cdc', SHA)
        self.assertIn('/status', urls['statuses'])
        self.assertIn('/check-runs', urls['checks'])
        self.assertIn('head_sha=' + SHA, urls['actions'])

    def test_missing_or_partial_surfaces_are_unknown_not_no_ci(self):
        for name in ('checks', 'actions', 'statuses'):
            data = snapshot()
            data[name] = None
            result = probe.assess(data)
            self.assertFalse(result['execution_unavailable_proven'])
            self.assertFalse(result['inventory_complete'])
        data = snapshot()
        data['actions']['total_count'] = 2
        self.assertFalse(probe.assess(data)['inventory_complete'])

    def test_all_empty_means_no_observed_run_not_no_backend(self):
        data = snapshot()
        data['checks'] = {'total_count': 0, 'check_runs': []}
        data['actions'] = {'total_count': 0, 'workflow_runs': []}
        result = probe.assess(data)
        self.assertEqual(result['state'], 'no_observed_run')
        self.assertEqual(result['next_action'], 'inspect_workflow_triggers_and_authorized_execution_routes')
        self.assertFalse(result['execution_unavailable_proven'])

    def test_unrelated_commit_and_workflow_do_not_prove_candidate_execution(self):
        for field, value in (('head_sha', 'a' * 40), ('path', '.github/workflows/other.yml')):
            data = snapshot()
            data['actions']['workflow_runs'][0][field] = value
            data['checks'] = {'total_count': 0, 'check_runs': []}
            self.assertNotEqual(probe.assess(data)['state'], 'running')

    def test_success_is_observed_workflow_result_not_release_readiness(self):
        data = snapshot()
        for record in (data['actions']['workflow_runs'][0], data['checks']['check_runs'][0]):
            record.update(status='completed', conclusion='success')
        result = probe.assess(data)
        self.assertEqual(result['state'], 'workflow_succeeded')
        self.assertFalse(result['release_ready'])
        self.assertEqual(result['next_action'], 'verify_scope_and_required_release_evidence')

    def test_conflicting_and_failed_observations_never_report_success(self):
        data = snapshot()
        data['actions']['workflow_runs'][0].update(status='completed', conclusion='failure')
        result = probe.assess(data)
        self.assertNotEqual(result['state'], 'workflow_succeeded')
        self.assertFalse(result['release_ready'])

    def test_request_identity_is_validated(self):
        for repo, sha in (('bajoicheg/g-cdc?token=x', SHA), ('bajoicheg/g-cdc', 'main')):
            with self.assertRaises(ValueError):
                probe.requests(repo, sha)

    def test_malformed_run_identity_is_rejected_explicitly(self):
        for value in (None, [], {'full_name': None}):
            data = snapshot()
            data['actions']['workflow_runs'][0]['repository'] = value
            with self.assertRaisesRegex(ValueError, 'repository'):
                probe.assess(data)
