"""Read-only project initialization and conservative migration previews."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import yaml
from contracts import StrictLoader, semver
from codex_cloud_profile import validate_profile
from policy_migration import plan as policy_plan
from validate_adapter import validate_adapter
from validate_checkpoint_24 import validate_checkpoint_24

ROOT = Path(__file__).resolve().parents[1]
PRESETS = {'portable': ('MEDIUM', 'any'), 'windows': ('MEDIUM', 'windows'),
           'android': ('MEDIUM', 'android'), 'critical': ('FULL', 'any')}
LEVELS = {'FAST': 0, 'MEDIUM': 1, 'FULL': 2}
AUTHORITY = {name: False for name in ('authorizes_product_write',
             'authorizes_external_start', 'authorizes_lease_mutation',
             'authorizes_release', 'authorizes_adoption')}


def _fields(value, fields, label):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ValueError(label + ' fields mismatch')


def _text(value, label, *, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise ValueError(label + ' must be text')
    return value


def _sha(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{40}', value):
        raise ValueError('source_head must be exact Git SHA')
    return value


def _preset(value):
    if not isinstance(value, str) or value not in PRESETS:
        raise ValueError('unknown project preset')
    return PRESETS[value]


def _yaml(text):
    _text(text, 'YAML')
    if len(text) > 262144:
        raise ValueError('configuration exceeds 256 KiB')
    try:
        value = yaml.load(text, Loader=StrictLoader)
    except (yaml.YAMLError, RecursionError) as exc:
        raise ValueError('invalid strict YAML') from exc
    if not isinstance(value, dict):
        raise ValueError('configuration must be mapping')
    return value


def _checkpoint(text):
    _text(text, 'checkpoint')
    match = re.match(r'\A---\n(.*?)\n---(?P<body>\n.*|\Z)', text, re.S)
    if match is None:
        raise ValueError('checkpoint requires YAML frontmatter')
    return _yaml(match.group(1)), match.group('body')


def _render_checkpoint(value, body):
    return '---\n' + yaml.safe_dump(value, sort_keys=False, allow_unicode=True) + '---' + body


def _unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('duplicate JSON field: ' + key)
        value[key] = item
    return value


def _cloud(text, repository, branch, digest):
    if text is None:
        value = json.loads((ROOT / 'templates/codex-cloud-profile.json').read_text())
        value.update(repository=repository, source_ref='refs/heads/' + branch,
                     policy_digest='sha256:' + digest)
        validate_profile(value)
        return json.dumps(value, indent=2) + '\n', {'status': 'UNCONFIGURED', 'reused': False}
    _text(text, 'cloud_profile_json')
    value = json.loads(text, object_pairs_hook=_unique)
    validate_profile(value)
    if value['repository'] != repository or value['source_ref'] != 'refs/heads/' + branch:
        raise ValueError('Cloud profile project/source identity mismatch')
    status = ('REUSE_PENDING_FRESH_PROBE' if value['policy_digest'] == 'sha256:' + digest
              else 'REQUALIFY')
    return text, {'status': status, 'reused': True}


def _file(path, content, before=None):
    h = lambda text: hashlib.sha256(text.encode('utf-8')).hexdigest()
    return dict(path=path, content=content, before_sha256=None if before is None else h(before),
                after_sha256=h(content))


def _result(action, preset, source_head, digest, files, cloud, reason,
            *, operation=None, compatibility=None):
    return dict(schema='cdc-project-plan/v1', action=action, preset=preset,
                source_head=source_head, policy_digest=digest, files=files,
                changed_paths=[f['path'] for f in files if f['before_sha256'] != f['after_sha256']],
                cloud_reuse=cloud, reason=reason, existing_operation=operation,
                original_compatibility=compatibility, **AUTHORITY)


def initialize(request):
    _fields(request, {'schema', 'repository', 'branch', 'source_head', 'preset',
                      'validation', 'cloud_profile_json'}, 'init request')
    if request['schema'] != 'cdc-init-request/v1':
        raise ValueError('unsupported init schema')
    repository, branch = request['repository'], request['branch']
    if not isinstance(repository, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository) or '..' in repository:
        raise ValueError('repository must be canonical owner/name')
    if not isinstance(branch, str) or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_./-]*', branch) or any(part in {'', '.', '..'} or part.endswith(('.', '.lock')) or part.startswith('.') for part in branch.split('/')) or '..' in branch:
        raise ValueError('branch must be safe refs/heads suffix')
    source = _sha(request['source_head'])
    quality, platform = _preset(request['preset'])
    validation = request['validation']
    _fields(validation, {'quick', 'full', 'release'}, 'validation')
    for name in validation:
        _text(validation[name], name, empty=name == 'quick')
    adapter = _yaml((ROOT / 'templates/development-cycle.yaml').read_text())
    adapter['repository'].update(name=repository.split('/')[1], remote=repository)
    adapter['quality']['default_level'] = quality
    adapter['validation'].update(validation, final_platform=platform)
    adapter['checkpoint']['path'] = 'docs/work-status/current.md'
    binding = validate_adapter(adapter)
    cp, body = _checkpoint((ROOT / 'templates/work-status-v4.md').read_text())
    cp.update(repository=repository, branch=branch, candidate_sha=source,
              policy_revision=binding['policy_revision'], policy_digest=binding['policy_digest'])
    validate_checkpoint_24(cp, adapter)
    cloud_text, cloud = _cloud(request['cloud_profile_json'], repository, branch, binding['policy_digest'])
    scaffold = dict(schema='cloud-entry-inputs-template/v1', configuration_status='UNCONFIGURED',
                    input_schema='cloud-entry-inputs/v1',
                    required_snapshots=['context', 'probe', 'registry', 'routing_policy', 'routing_context'])
    files = [_file('docs/development-cycle.yaml', yaml.safe_dump(adapter, sort_keys=False, allow_unicode=True)),
             _file('docs/work-status/current.md', _render_checkpoint(cp, body)),
             _file('docs/cdc-cloud-profile.json', cloud_text),
             _file('docs/cdc-cloud-entry-inputs.template.json', json.dumps(scaffold, indent=2) + '\n')]
    return _result('INIT', request['preset'], source, binding['policy_digest'], files,
                   cloud, 'review_generated_files_then_use_existing_managed_writer')

