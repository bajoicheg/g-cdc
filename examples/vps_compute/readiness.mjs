import { pathToFileURL } from 'node:url';

const STATES = Object.freeze(['queued', 'reserved', 'running', 'unknown', 'terminal_pending',
  'succeeded', 'failed', 'cancelled', 'timed_out', 'retired_unknown']);
const PROJECTS = new Set(['infrastructure', 'g-cdc', 'g-switcher', 'g-pc-health-check', 'g-ad-control']);
const ACTIVE = new Set(['reserved', 'running', 'unknown', 'terminal_pending']);
const UNRESOLVED = new Set(['unknown', 'retired_unknown']);
const FAILED = new Set(['failed', 'timed_out']);
const MAX_BYTES = 1024 * 1024;

function object(value, label) {
  if (value === null || typeof value !== 'object' || Array.isArray(value) ||
      ![Object.prototype, null].includes(Object.getPrototypeOf(value))) {
    throw new TypeError(`${label} must be an object`);
  }
  for (const key of Reflect.ownKeys(value)) {
    const descriptor = Object.getOwnPropertyDescriptor(value, key);
    if (typeof key !== 'string' || !descriptor.enumerable || !Object.hasOwn(descriptor, 'value')) {
      throw new TypeError(`${label} must have string data fields`);
    }
  }
}

function fields(value, expected, label) {
  object(value, label);
  const keys = Object.keys(value);
  if (Reflect.ownKeys(value).length !== expected.length || keys.length !== expected.length ||
      !expected.every(key => Object.hasOwn(value, key))) {
    throw new TypeError(`${label} has missing or unexpected fields`);
  }
}

/** Summarize observations only; this grants no execution or product acceptance. */
export function summarizeStatus(status) {
  fields(status, ['revision', 'dispatch_enabled', 'tasks'], 'status');
  if (typeof status.revision !== 'string' || !/^[a-fA-F0-9]{40}$/.test(status.revision)) {
    throw new TypeError('revision must be 40 hexadecimal characters');
  }
  if (typeof status.dispatch_enabled !== 'boolean') throw new TypeError('dispatch_enabled must be boolean');
  object(status.tasks, 'tasks');
  const report = {
    revision: status.revision,
    dispatch_enabled: status.dispatch_enabled,
    total_tasks: 0,
    counts: Object.fromEntries(STATES.map(state => [state, 0])),
    active_task_ids: [], queued_task_ids: [], unresolved_task_ids: [], failed_task_ids: [],
    ready_to_accept: false,
  };
  for (const id of Object.keys(status.tasks).sort()) {
    if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(id) || ['constructor', 'prototype'].includes(id)) {
      throw new TypeError('task ID must be a safe 1–128 character ASCII identifier');
    }
    const task = status.tasks[id];
    fields(task, ['state', 'project_id', 'handle_id', 'result'], 'task');
    if (typeof task.state !== 'string' || !STATES.includes(task.state)) throw new TypeError('unregistered task state');
    if (typeof task.project_id !== 'string' || !PROJECTS.has(task.project_id)) throw new TypeError('unregistered project_id');
    if (task.handle_id !== null && (typeof task.handle_id !== 'string' ||
        !/^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$/.test(task.handle_id))) {
      throw new TypeError('handle_id must be null or a UUID');
    }
    if (task.result !== null) object(task.result, 'result');
    report.total_tasks++;
    report.counts[task.state]++;
    if (ACTIVE.has(task.state)) report.active_task_ids.push(id);
    if (task.state === 'queued') report.queued_task_ids.push(id);
    if (UNRESOLVED.has(task.state)) report.unresolved_task_ids.push(id);
    if (FAILED.has(task.state)) report.failed_task_ids.push(id);
  }
  report.ready_to_accept = report.dispatch_enabled &&
    [report.active_task_ids, report.queued_task_ids, report.unresolved_task_ids, report.failed_task_ids]
      .every(ids => ids.length === 0);
  return report;
}

// JSON.parse validates grammar first. This token walk then rejects duplicate keys,
// including escaped aliases, which JSON.parse would silently overwrite.
function rejectDuplicateKeys(document) {
  const tokens = document.match(/"(?:\\[\s\S]|[^"\\])*"|[{}\[\],:]|[^{}\[\],:\s]+/g);
  const stack = [];
  for (const token of tokens) {
    const parent = stack.at(-1);
    if (token === '{') {
      stack.push({ keys: new Set(), expectingKey: true });
    } else if (token === '[') {
      stack.push({ keys: null });
    } else if (token === '}' || token === ']') {
      stack.pop();
    } else if (token === ',') {
      if (parent?.keys) parent.expectingKey = true;
    } else if (token === ':') {
      parent.expectingKey = false;
    } else if (parent?.keys && parent.expectingKey) {
      const key = JSON.parse(token);
      if (parent.keys.has(key)) throw new TypeError('duplicate JSON field');
      parent.keys.add(key);
      parent.expectingKey = false;
    }
  }
}

async function main() {
  try {
    const chunks = [];
    let size = 0;
    for await (const chunk of process.stdin) {
      size += chunk.length;
      if (size > MAX_BYTES) throw new TypeError('stdin exceeds 1 MiB');
      chunks.push(chunk);
    }
    const document = new TextDecoder('utf-8', { fatal: true }).decode(Buffer.concat(chunks));
    const status = JSON.parse(document);
    rejectDuplicateKeys(document);
    process.stdout.write(JSON.stringify(summarizeStatus(status)) + '\n');
  } catch (error) {
    process.stderr.write(`readiness: ${error.message}\n`);
    process.exitCode = 1;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) await main();
