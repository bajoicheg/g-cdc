"""Portable hosted tests; all effects are fakes. Never run against live PIDs."""
import errno
import signal
import sqlite3
import socket
import time
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import maintenance as m


class SpendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / 'ledger.sqlite')
        self.book = m.Ledger(self.path)
        self.book.configure('task', {'calls': 1}, {'calls': 3})

    def tearDown(self):
        self.book.close()
        self.tmp.cleanup()

    def test_crash_charge_survives_reopen_and_aggregate_other_thread(self):
        native = Mock(); native.authorize.side_effect = RuntimeError('denied')
        effect = Mock()
        with self.assertRaises(RuntimeError):
            self.book.execute('task', 'desktop', 'turn1', 'intent', {'calls': 1}, native, effect)
        effect.assert_not_called()
        self.book.close(); self.book = m.Ledger(self.path)
        self.book.reserve('task', 'another-thread', 'turn2', 'intent', {'calls': 1})
        with self.assertRaises(ValueError):
            self.book.reserve('task', 'desktop', 'turn3', 'intent', {'calls': 1})

    def test_replay_and_policy_change_rejected(self):
        self.book.reserve('task', 'desktop', 'turn1', 'intent', {'calls': 1})
        with self.assertRaises(sqlite3.IntegrityError):
            self.book.reserve('task', 'desktop', 'turn1', 'intent', {'calls': 1})
        with self.assertRaises(ValueError):
            self.book.configure('task', {'calls': 0}, {'calls': 99})

    def test_native_before_effect(self):
        order = []
        native = Mock(); native.authorize.side_effect = lambda **kw: order.append('native') or object()
        def effect(grant):
            self.assertIsNotNone(grant); order.append('effect'); return 7
        self.assertEqual(self.book.execute('task', 'd', 't', 'i', {'calls': 1}, native, effect), 7)
        self.assertEqual(order, ['native', 'effect'])

    def test_exact_interrupt_once_and_owner_safety(self):
        self.book.reserve('task', 'desktop', 'turn1', 'intent', {'calls': 1})
        rpc = m.NativeInterruptRPC('/private/native.sock', timeout_seconds=0.1)
        with patch.object(m.NativeInterruptRPC, 'interrupt', return_value={'status': 'acknowledged'}) as call:
            for supported, owner in [(False, False), (True, True)]:
                self.book.interrupt('desktop', 'turn1', supported=supported, owner_dialogue=owner, rpc=rpc)
            call.assert_not_called()
            self.book.interrupt('desktop', 'turn1', supported=True, owner_dialogue=False, rpc=rpc)
            call.assert_called_once_with(rpc, 'desktop', 'turn1')
            with self.assertRaises(sqlite3.IntegrityError):
                self.book.interrupt('desktop', 'turn1', supported=True, owner_dialogue=False, rpc=rpc)

    def test_arbitrary_adapter_rejected_before_dispatch(self):
        self.book.reserve('task', 'desktop', 'turn1', 'intent', {'calls': 1})
        rpc = Mock()
        with self.assertRaises(TypeError):
            self.book.interrupt('desktop', 'turn1', supported=True, owner_dialogue=False, rpc=rpc)
        rpc.call.assert_not_called()

    def exercise_transport(self, response=None, close_peer=False):
        self.book.reserve('task', 'desktop', 'turn1', 'intent', {'calls': 1})
        client, peer = socket.socketpair()
        # Use a real nonblocking kernel stream; only connection establishment is
        # replaced. No worker thread or provider/native service is started.
        class Connected:
            def __enter__(self): return self
            def __exit__(self, *args): client.close()
            def connect_ex(self, endpoint): return 0
            def __getattr__(self, key): return getattr(client, key)
        try:
            if response is not None: peer.sendall(response)
            if close_peer: peer.shutdown(socket.SHUT_WR)
            rpc = m.NativeInterruptRPC('/private/native.sock', timeout_seconds=0.03)
            with patch.object(m.socket, 'socket', return_value=Connected()) as factory:
                started = time.monotonic()
                result = self.book.interrupt('desktop', 'turn1', supported=True, owner_dialogue=False, rpc=rpc)
                elapsed = time.monotonic() - started
                self.assertLess(elapsed, 0.5)
                peer.settimeout(0.5)
                request = peer.recv(4096)
                self.assertIn(b'"deadline_monotonic_ns":', request)
                self.assertIn(b'"threadId":"desktop","turnId":"turn1"', request)
                self.book.close(); self.book = m.Ledger(self.path)
                with self.assertRaises(sqlite3.IntegrityError):
                    self.book.interrupt('desktop', 'turn1', supported=True, owner_dialogue=False, rpc=rpc)
                factory.assert_called_once()
                self.assertEqual(self.book.db.execute('SELECT status FROM turns').fetchall(), [('UNKNOWN',)])
                with self.assertRaises(ValueError):
                    self.book.reserve('task', 'other', 'turn2', 'intent', {'calls': 2})
                return result
        finally:
            client.close(); peer.close()

    def test_unresponsive_transport_deadline_and_no_replay(self):
        result = self.exercise_transport()
        self.assertEqual(result, {'status': 'uncertain', 'reason': 'timeout', 'replay_allowed': False})

    def test_uncertain_transport_no_replay(self):
        result = self.exercise_transport(close_peer=True)
        self.assertEqual(result['status'], 'uncertain')
        self.assertEqual(result['reason'], 'transport failure')
        self.assertFalse(result['replay_allowed'])

    def test_wrong_turn_acknowledgement_is_uncertain(self):
        result = self.exercise_transport(b'{"status":"acknowledged","threadId":"desktop","turnId":"other"}\n')
        self.assertEqual(result['status'], 'uncertain')

    def test_bound_acknowledgement_is_not_closure(self):
        result = self.exercise_transport(b'{"status":"acknowledged","threadId":"desktop","turnId":"turn1"}\n')
        self.assertEqual(result['status'], 'acknowledged')
        self.assertFalse(result['quiescent'])

    def test_nonfinite_or_unbounded_timeout_rejected(self):
        for timeout in (0, -1, float('inf'), float('nan'), True, 6):
            with self.assertRaises(ValueError):
                m.NativeInterruptRPC('/private/native.sock', timeout_seconds=timeout)

    def test_bad_counters_fail_closed(self):
        for charge in ({'calls': -1}, {'calls': True}, {'other': 1}):
            with self.assertRaises(ValueError):
                self.book.reserve('task', 'd', 't', 'i', charge)


class SignalTests(unittest.TestCase):
    def invoke(self, error=None, observed_birth='birth', uid='42'):
        with patch.object(m.os, 'readlink', return_value='999'), \
             patch.object(m.os, 'getpid', return_value=999), \
             patch.object(m.os, 'geteuid', return_value=42), \
             patch.object(m.os, 'pidfd_open', return_value=8, create=True) as opened, \
             patch.object(m.signal, 'pidfd_send_signal', side_effect=error, create=True) as sent, \
             patch.object(m, 'birth', return_value=observed_birth), \
             patch.object(m.Path, 'read_text', return_value='Uid:\t'+ '\t'.join([uid]*4)), \
             patch.object(m.os, 'close') as closed:
            result = m.signal_owned(1234, 'birth', signal.SIGTERM, expected_uid=42)
            closed.assert_called_once_with(8)
            return result, sent.call_count

    def test_permission_error_is_not_terminal(self):
        result, count = self.invoke(PermissionError(errno.EPERM, 'denied'))
        self.assertEqual(result['status'], 'denied'); self.assertFalse(result['quiescent'])
        self.assertEqual(count, 1)

    def test_pid_reuse_and_uid_crossing_never_signal(self):
        for kwargs in ({'observed_birth': 'reused'}, {'uid': '43'}):
            result, count = self.invoke(**kwargs)
            self.assertIn(result['status'], ('unknown', 'denied')); self.assertEqual(count, 0)

    def test_sent_and_absent_are_not_closure(self):
        for error in (None, ProcessLookupError()):
            result, _ = self.invoke(error)
            self.assertFalse(result['quiescent'])


class RecoveryTests(unittest.TestCase):
    def test_known_birth_absence_never_authorizes_replay_or_release(self):
        result = m.recovery_assessment({'request_ref': 'original', 'known_births_absent': True})
        for key in ('task_success', 'replay_allowed', 'release_allowed'):
            self.assertFalse(result[key])
        self.assertEqual(result['disposition'], 'UNKNOWN')

    def test_maintenance_failure_does_not_close(self):
        native = Mock()
        binding = dict(task='new', source='frozen', claim='one', uid=42, cgroup='isolated', intent_digest='digest')
        def fail(cap): raise PermissionError()
        result = m.maintenance_step(binding, native, fail)
        self.assertEqual(result['status'], 'UNKNOWN')
        native.verify_and_record.assert_not_called()

    def test_usage_dimensions(self):
        self.assertEqual(m.usage(12, 8, 3, 4), dict(total=12, input=8, cached_input=3, uncached_input=5, output=4))
        for values in ((12, 8, 9, 4), (16, 8, 3, 4)):
            with self.assertRaises(ValueError): m.usage(*values)


if __name__ == '__main__':
    unittest.main()
