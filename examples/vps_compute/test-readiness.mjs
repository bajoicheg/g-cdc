import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, openSync, closeSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { summarizeStatus } from './readiness.mjs';

const states = ['queued', 'reserved', 'running', 'unknown', 'terminal_pending', 'succeeded', 'failed', 'cancelled', 'timed_out', 'retired_unknown'];
const status = (tasks = {}, dispatch_enabled = true) => ({ revision: 'a'.repeat(40), dispatch_enabled, tasks });
const task = (state) => ({ state, project_id: 'g-cdc', handle_id: null, result: null });

test('healthy and disabled reports include every zero count', () => {
  const report = summarizeStatus(status());
  assert.deepEqual(report, { revision: 'a'.repeat(40), dispatch_enabled: true, total_tasks: 0,
    counts: Object.fromEntries(states.map(s => [s, 0])), active_task_ids: [], queued_task_ids: [],
    unresolved_task_ids: [], failed_task_ids: [], ready_to_accept: true });
  assert.equal(summarizeStatus(status({}, false)).ready_to_accept, false);
  assert.equal(summarizeStatus(status({ a: task('succeeded'), b: task('cancelled') })).ready_to_accept, true);
});

for (const state of states.filter(s => !['succeeded', 'cancelled'].includes(s))) {
  test(`${state} blocks readiness and stays in its actual category`, () => {
    const report = summarizeStatus(status({ example: task(state) }));
    assert.equal(report.ready_to_accept, false);
    assert.equal(report.counts[state], 1);
    assert.deepEqual(report.active_task_ids, ['reserved', 'running', 'unknown', 'terminal_pending'].includes(state) ? ['example'] : []);
    assert.deepEqual(report.queued_task_ids, state === 'queued' ? ['example'] : []);
    assert.deepEqual(report.unresolved_task_ids, ['unknown', 'retired_unknown'].includes(state) ? ['example'] : []);
    assert.deepEqual(report.failed_task_ids, ['failed', 'timed_out'].includes(state) ? ['example'] : []);
    assert.equal(report.counts.succeeded, 0);
  });
}

test('stable ordering, observation-only results, all projects and immutable input', () => {
  const projects = ['infrastructure', 'g-cdc', 'g-switcher', 'g-pc-health-check', 'g-ad-control'];
  const entries = projects.map((project_id, i) => [`task-${4-i}`, { ...task('unknown'), project_id,
    handle_id: '12345678-1234-1234-1234-123456789abc', result: { accepted: true, state: 'succeeded' } }]);
  const input = status(Object.fromEntries(entries));
  const before = structuredClone(input);
  Object.values(input.tasks).forEach(t => { Object.freeze(t.result); Object.freeze(t); });
  Object.freeze(input.tasks); Object.freeze(input);
  const report = summarizeStatus(input);
  assert.deepEqual(report.active_task_ids, ['task-0', 'task-1', 'task-2', 'task-3', 'task-4']);
  assert.deepEqual(report.unresolved_task_ids, report.active_task_ids);
  assert.deepEqual(report, summarizeStatus(status(Object.fromEntries(entries.reverse()))));
  assert.deepEqual(input, before);
  assert.equal(report.ready_to_accept, false);
});

test('every ID list sorts independently across multiple tasks', () => {
  const input = status(Object.fromEntries([
    ['z-queued', task('queued')], ['z-failed', task('failed')], ['z-retired', task('retired_unknown')],
    ['z-running', task('running')], ['a-queued', task('queued')], ['a-timeout', task('timed_out')],
    ['a-unknown', task('unknown')],
  ]));
  const report = summarizeStatus(input);
  assert.equal(report.total_tasks, 7);
  assert.deepEqual(report.active_task_ids, ['a-unknown', 'z-running']);
  assert.deepEqual(report.queued_task_ids, ['a-queued', 'z-queued']);
  assert.deepEqual(report.unresolved_task_ids, ['a-unknown', 'z-retired']);
  assert.deepEqual(report.failed_task_ids, ['a-timeout', 'z-failed']);
});

test('reject missing, extra, unsafe and wrongly typed fields', () => {
  const bad = [null, [], {}, { ...status(), revision: 'a'.repeat(39) }, { ...status(), revision: 40 },
    { ...status(), dispatch_enabled: 1 }, { ...status(), tasks: [] }, { ...status(), extra: true }];
  for (const key of ['revision', 'dispatch_enabled', 'tasks']) { const x = status(); delete x[key]; bad.push(x); }
  for (const id of ['', '../escape', 'two words', '__proto__', 'constructor', 'prototype', 'x'.repeat(129)]) {
    bad.push(status(Object.fromEntries([[id, task('queued')]])));
  }
  for (const field of ['state', 'project_id', 'handle_id', 'result']) {
    const t = task('queued'); delete t[field]; bad.push(status({ a: t }));
  }
  for (const [field, values] of Object.entries({ state: ['bogus', 'RUNNING', null, 1], project_id: ['other', null, 2],
    handle_id: ['', 'bad', 3, {}], result: [[], 'success', true, 1] })) {
    for (const value of values) bad.push(status({ a: { ...task('queued'), [field]: value } }));
  }
  bad.push(status({ a: null }), status({ a: [] }), status({ a: { ...task('queued'), status: 'succeeded' } }));
  bad.push({ ...status(), [Symbol('extra')]: true });
  const accessor = status(); Object.defineProperty(accessor, 'revision', { get() { throw new Error('must not invoke getter'); } });
  bad.push(accessor);
  const hidden = status(); Object.defineProperty(hidden.tasks, 'hidden', { value: task('running') });
  bad.push(hidden);
  for (const input of bad) assert.throws(() => summarizeStatus(input), TypeError);
});

function cli(input) {
  assert.ok(process.env.TMPDIR, 'assigned TMPDIR is required');
  const dir = mkdtempSync(join(process.env.TMPDIR, 'readiness-test-'));
  const descriptors = [];
  try {
    writeFileSync(join(dir, 'stdin'), input);
    descriptors.push(openSync(join(dir, 'stdin'), 'r'), openSync(join(dir, 'stdout'), 'w'), openSync(join(dir, 'stderr'), 'w'));
    const child = spawnSync(process.execPath, [new URL('./readiness.mjs', import.meta.url).pathname], { stdio: descriptors });
    assert.ifError(child.error);
    return { code: child.status, stdout: readFileSync(join(dir, 'stdout'), 'utf8'), stderr: readFileSync(join(dir, 'stderr'), 'utf8') };
  } finally { descriptors.forEach(closeSync); rmSync(dir, { recursive: true, force: true }); }
}

test('CLI emits only deterministic report JSON', () => {
  const input = status({ pending: task('retired_unknown') });
  const output = cli(JSON.stringify(input));
  assert.equal(output.code, 0); assert.equal(output.stderr, '');
  assert.equal(output.stdout, JSON.stringify(summarizeStatus(input)) + '\n');
});

test('CLI rejects malformed, ambiguous and oversized documents without a report', () => {
  for (const input of ['', '{', '{}', JSON.stringify(status()) + '{}',
    '{"revision":"' + 'a'.repeat(40) + '","revision":"' + 'b'.repeat(40) + '","dispatch_enabled":true,"tasks":{}}',
    '{"revision":"' + 'a'.repeat(40) + '","dispatch_enabled":true,"tasks":{"a":{},"\\u0061":{}}}',
    JSON.stringify(status({ a: task('unknown') })).replace('"state":"unknown"', '"state":"unknown","state":"succeeded"'),
    JSON.stringify(status({ a: { ...task('succeeded'), result: { nested: 1 } } })).replace('"nested":1', '"nested":1,"nested":2'),
    ' '.repeat(1024 * 1024 + 1), '"' + 'é'.repeat(600000) + '"']) {
    const output = cli(input);
    assert.notEqual(output.code, 0); assert.equal(output.stdout, ''); assert.match(output.stderr, /readiness:/);
  }
});

test('CLI validates UTF-8 and accepts nested observation objects without interpreting them', () => {
  const invalid = cli(Buffer.from([0xff]));
  assert.notEqual(invalid.code, 0); assert.equal(invalid.stdout, ''); assert.match(invalid.stderr, /readiness:/);
  const input = status({ a: { ...task('retired_unknown'), result: { entries: [{ accepted: true }, { accepted: false }],
    text: 'braces {}, colon : and quote "', nested: { state: 'succeeded' } } } });
  const output = cli(JSON.stringify(input));
  assert.equal(output.code, 0); assert.equal(output.stderr, '');
  assert.deepEqual(JSON.parse(output.stdout), summarizeStatus(input));
});

test('CLI accepts the exact byte limit', () => {
  const input = JSON.stringify(status());
  assert.equal(cli(input + ' '.repeat(1024 * 1024 - Buffer.byteLength(input))).code, 0);
});
