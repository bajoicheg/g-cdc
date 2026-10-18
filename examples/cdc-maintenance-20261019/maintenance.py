"""Isolated candidates. No startup, provider, credentials, or native-store writes.

Adapters are trusted controller code, not proofs supplied as JSON. This module
never issues VerifiedTerminalProof or a lease-release capability.
"""
import errno
import math
import select
import socket
import time
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def birth(pid):
    return Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19]


def signal_owned(pid, expected_birth, sig, *, expected_uid):
    """Linux candidate: pin a PID before rechecking birth; never use signal_pid.

    Only usable where /proc and pidfd_open share the caller PID namespace.
    Caller must derive pid/birth from its own live descendant enumeration.
    Return denied/unknown to the live supervisor; neither means quiescence.
    """
    if sig not in (signal.SIGTERM, signal.SIGKILL):
        raise ValueError('termination signals only')
    if type(pid) is not int or pid <= 1 or not expected_birth:
        raise ValueError('bound process identity required')
    fd = None
    try:
        if int(os.readlink('/proc/self')) != os.getpid():
            return {'status': 'unknown', 'reason': 'proc PID namespace mismatch'}
        if not hasattr(os, 'pidfd_open') or not hasattr(signal, 'pidfd_send_signal'):
            return {'status': 'unknown', 'reason': 'pidfd unsupported'}
        fd = os.pidfd_open(pid, 0)
        if birth(pid) != str(expected_birth):
            return {'status': 'unknown', 'reason': 'birth mismatch'}
        # All four UID columns must agree; no broad CAP_KILL or elevated worker.
        fields = next(x for x in Path(f'/proc/{pid}/status').read_text().splitlines()
                      if x.startswith('Uid:')).split()[1:]
        if expected_uid != os.geteuid() or any(int(x) != expected_uid for x in fields):
            return {'status': 'denied', 'reason': 'isolated UID boundary'}
        signal.pidfd_send_signal(fd, sig)
        return {'status': 'sent', 'quiescent': False}
    except ProcessLookupError:
        return {'status': 'absent', 'quiescent': False}
    except PermissionError as exc:
        return {'status': 'denied', 'errno': exc.errno, 'quiescent': False}
    except (OSError, ValueError, StopIteration) as exc:
        return {'status': 'unknown', 'reason': type(exc).__name__, 'quiescent': False}
    finally:
        if fd is not None:
            os.close(fd)


def recovery_assessment(facts):
    """Diagnostic only: absence of known births cannot prove no descendants."""
    return {'schema': 'maintenance-recovery-assessment/v1',
            'original_request_ref': facts['request_ref'],
            'facts_digest': digest(facts), 'disposition': 'UNKNOWN',
            'task_success': False, 'replay_allowed': False, 'release_allowed': False,
            'missing_boundary': 'authentic original supervisor waitpid_ECHILD; '
                                'native authenticated postlaunch recovery capability',
            'known_births_absent': facts.get('known_births_absent') is True}


class NativeInterruptRPC:
    """Dedicated native bridge, AF_UNIX stream, one JSON line each direction.

    Controller supplies a pinned private bridge path (never user input). No
    credentials, generic method dispatch, reconnect, retry, or worker threads.
    Native bridge MUST validate admission/provider/account/permission/quality
    guards and exact autonomous identity, enforce deadline_monotonic_ns in the
    same host clock domain before effect, and never queue/replay expired requests.
    An acknowledgement is transport evidence only, never physical closure.
    """
    MAX_FRAME = 4096
    MAX_TIMEOUT = 5.0

    def __init__(self, endpoint, *, timeout_seconds):
        if not isinstance(endpoint, str) or not endpoint.startswith('/'):
            raise ValueError('private absolute native bridge path required')
        if (type(timeout_seconds) not in (int, float) or
                not math.isfinite(timeout_seconds) or
                not 0 < timeout_seconds <= self.MAX_TIMEOUT):
            raise ValueError('finite timeout in (0, 5] seconds required')
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def interrupt(self, thread, turn):
        deadline = time.monotonic() + self.timeout_seconds
        request = {'method': 'turn/interrupt', 'params': {'threadId': thread, 'turnId': turn},
                   'deadline_monotonic_ns': int(deadline * 1_000_000_000)}
        frame = json.dumps(request, separators=(',', ':')).encode() + b'\n'
        uncertain = {'status': 'uncertain', 'replay_allowed': False}
        if len(frame) > self.MAX_FRAME:
            return dict(uncertain, reason='request too large')

        def wait(sock, writing):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError()
            ready = select.select([] if writing else [sock], [sock] if writing else [], [], remaining)
            if not (ready[0] or ready[1]) or time.monotonic() >= deadline:
                raise TimeoutError()

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.setblocking(False)
                code = sock.connect_ex(self.endpoint)
                if code not in (0, errno.EINPROGRESS, errno.EALREADY, errno.EWOULDBLOCK):
                    raise OSError(code, 'native bridge connect failed')
                if code:
                    wait(sock, True)
                    error = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                    if error:
                        raise OSError(error, 'native bridge connect failed')
                offset = 0
                while offset < len(frame):
                    wait(sock, True)
                    try:
                        sent = sock.send(frame[offset:])
                    except BlockingIOError:
                        continue
                    if not sent:
                        raise ConnectionError('closed during send')
                    offset += sent
                response = bytearray()
                while b'\n' not in response:
                    wait(sock, False)
                    try:
                        chunk = sock.recv(self.MAX_FRAME + 1 - len(response))
                    except BlockingIOError:
                        continue
                    if not chunk:
                        raise ConnectionError('closed before acknowledgement')
                    response.extend(chunk)
                    if len(response) > self.MAX_FRAME:
                        raise ValueError('oversized acknowledgement')
                ack = json.loads(response)
                if time.monotonic() >= deadline:
                    raise TimeoutError()
                if ack != {'status': 'acknowledged', 'threadId': thread, 'turnId': turn}:
                    raise ValueError('unbound acknowledgement')
                return {'status': 'acknowledged', 'quiescent': False, 'replay_allowed': False}
        except TimeoutError:
            return dict(uncertain, reason='timeout')
        except (OSError, ValueError, RecursionError) as exc:
            return dict(uncertain, reason='transport failure', error_type=type(exc).__name__)


class Ledger:
    """Private, controller-owned SQLite file on durable local disk.

    One transaction charges task aggregates and one-use exact turn identity.
    Crashes/failed callbacks remain charged UNKNOWN. Existing baseline is immutable.
    This is an additional gate, never a replacement for native/account admission.
    """
    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=5)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS tasks(task TEXT PRIMARY KEY, baseline TEXT NOT NULL, limits TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS turns(thread TEXT, turn TEXT, task TEXT NOT NULL,
          intent TEXT NOT NULL, charge TEXT NOT NULL, status TEXT NOT NULL,
          PRIMARY KEY(thread,turn));
        CREATE TABLE IF NOT EXISTS stops(thread TEXT, turn TEXT, PRIMARY KEY(thread,turn));
        ''')

    def close(self):
        self.db.close()

    def configure(self, task, baseline, limits):
        self._numbers(baseline); self._numbers(limits)
        if set(baseline) != set(limits):
            raise ValueError('baseline/limit dimensions differ')
        row = (task, json.dumps(baseline, sort_keys=True), json.dumps(limits, sort_keys=True))
        self.db.execute('INSERT OR IGNORE INTO tasks VALUES (?,?,?)', row)
        if self.db.execute('SELECT * FROM tasks WHERE task=?', (task,)).fetchone() != row:
            raise ValueError('immutable original policy')

    @staticmethod
    def _numbers(values):
        if not values or any(type(v) is not int or v < 0 for v in values.values()):
            raise ValueError('nonnegative integer counters required')

    def reserve(self, task, thread, turn, intent, charge):
        self._numbers(charge)
        if not all(isinstance(x, str) and x for x in (task, thread, turn, intent)):
            raise ValueError('exact identity required')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row = self.db.execute('SELECT baseline,limits FROM tasks WHERE task=?', (task,)).fetchone()
            if row is None:
                raise ValueError('unregistered task')
            used, limits = map(json.loads, row)
            if set(charge) != set(limits):
                raise ValueError('all budget dimensions required')
            for (raw,) in self.db.execute('SELECT charge FROM turns WHERE task=?', (task,)):
                for k, v in json.loads(raw).items():
                    used[k] += v
            if any(used[k] + charge[k] > limits[k] for k in limits):
                raise ValueError('aggregate budget exhausted')
            self.db.execute('INSERT INTO turns VALUES (?,?,?,?,?,?)',
                            (thread, turn, task, intent, json.dumps(charge), 'UNKNOWN'))
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def execute(self, task, thread, turn, intent, charge, native, effect):
        """native.authorize must genuinely check all original gates and reserve.

        effect must consume the returned native one-use capability. Native API
        integration is deliberately mandatory; a JSON allow flag is insufficient.
        No retry on exception; recovery observes the original turn only.
        """
        self.reserve(task, thread, turn, intent, charge)
        grant = native.authorize(task=task, thread=thread, turn=turn, intent=intent)
        result = effect(grant)
        self.db.execute('UPDATE turns SET status=? WHERE thread=? AND turn=?',
                        ('RETURNED', thread, turn))
        return result

    def interrupt(self, thread, turn, *, supported, owner_dialogue, rpc):
        """One exact-turn attempt, no polling, no thread-wide cancellation.

        supported is a controller capability established against the frozen RPC
        schema, not guessed from method naming. Owner dialogue is never stopped.
        """
        if owner_dialogue or not supported:
            return {'status': 'blocked', 'reason': 'owner dialogue or unsupported exact-turn RPC'}
        if self.db.execute('SELECT 1 FROM turns WHERE thread=? AND turn=?', (thread, turn)).fetchone() is None:
            raise ValueError('unreserved turn')
        if type(rpc) is not NativeInterruptRPC:
            raise TypeError('concrete bounded native bridge adapter required')
        self.db.execute('INSERT INTO stops VALUES (?,?)', (thread, turn))
        return NativeInterruptRPC.interrupt(rpc, thread, turn)


def usage(total, input_tokens, cached_input, output):
    """Reasoning is already included in output; never add it again."""
    values = [total, input_tokens, cached_input, output]
    if any(type(v) is not int or v < 0 for v in values) or cached_input > input_tokens or total != input_tokens + output:
        raise ValueError('inconsistent token observation')
    return dict(total=total, input=input_tokens, cached_input=cached_input,
                uncached_input=input_tokens-cached_input, output=output)


def maintenance_step(binding, native, operation):
    """One controller-owned step, never an autonomous recovery/observer loop.

    Native adapter validates exact registered claim/source/UID/cgroup/lease and
    all original budgets before returning a live one-use capability. Operation
    must execute inside that capability's isolated cold-path scope. On any error
    the original claim stays spent; only native verification may close it.
    """
    required = {'task', 'source', 'claim', 'uid', 'cgroup', 'intent_digest'}
    if set(binding) != required or not all(binding[k] for k in required):
        raise ValueError('complete frozen maintenance binding required')
    capability = native.admit(dict(binding))
    try:
        result = operation(capability)
    except Exception as exc:
        return {'status': 'UNKNOWN', 'replay_allowed': False,
                'error_type': type(exc).__name__, 'binding_digest': digest(binding)}
    # No JSON result can serve as a native proof. Adapter must verify physical
    # aggregate closure and original ownership independently, including readback.
    return native.verify_and_record(capability, result)
