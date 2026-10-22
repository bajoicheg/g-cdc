#!/usr/bin/env python3
"""Dedicated one-document Git CAS ref, isolated from all product branches."""
from __future__ import annotations

from git_object_integrity import git_object_environment

import json
import os
import re
import secrets
import select
import subprocess
import time

from git_remote_identity import isolated_remote_args, remote_identity, repository_root
from parallel_task_planner import portable_path_key

STATE_FILE = "document.json"
REVISION = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
MAX_BYTES = 4 * 1024 * 1024


def canonical(document):
    if not isinstance(document, dict):
        raise ValueError("coordination document must be an object")
    encoded = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n"
    if len(encoded.encode("utf-8")) > MAX_BYTES:
        raise ValueError("coordination document exceeds 4 MiB")
    return encoded


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate coordination JSON key")
        value[key] = item
    return value


_BATCH_TIMEOUT = 20


class _ObjectPipe:
    """One local cat-file pipe; bounded framing and deadline, no authority."""

    def __init__(self, repo, option):
        self.buffer = bytearray()
        try:
            self.process = subprocess.Popen(
                ["git", "-C", str(repo), "cat-file", option],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                env=git_object_environment(GIT_TERMINAL_PROMPT="0"), bufsize=0)
        except (OSError, subprocess.SubprocessError):
            raise ValueError("Git document coordination unavailable") from None
        try:
            os.set_blocking(self.process.stdin.fileno(), False)
            os.set_blocking(self.process.stdout.fileno(), False)
        except BaseException:
            self.finish(False)
            raise

    def _ready(self, deadline, *, writing=False):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError("historical object batch timed out")
        fd = (self.process.stdin if writing else self.process.stdout).fileno()
        ready = select.select([] if writing else [fd], [fd] if writing else [], [], remaining)
        if not ready[1 if writing else 0]:
            raise ValueError("historical object batch timed out")
        return fd

    def send(self, specifications, deadline):
        # The empty request has the fixed ' missing' reply: a frame boundary,
        # never an additional object or caller-controlled Git expression.
        request = ("\n".join(specifications) + "\n\n").encode("ascii")
        offset = 0
        while offset < len(request):
            try:
                offset += os.write(self._ready(deadline, writing=True), request[offset:])
            except (OSError, subprocess.SubprocessError):
                raise ValueError("Git document coordination unavailable") from None

    def _fill(self, deadline):
        try:
            data = os.read(self._ready(deadline), 65536)
        except OSError:
            raise ValueError("Git document coordination unavailable") from None
        if not data:
            raise ValueError("incomplete historical object batch")
        self.buffer.extend(data)

    def line(self, deadline):
        while True:
            end = self.buffer.find(b"\n")
            if end >= 0:
                if end > 256:
                    raise ValueError("invalid historical object header")
                result = bytes(self.buffer[:end + 1]); del self.buffer[:end + 1]
                return result
            if len(self.buffer) > 256:
                raise ValueError("invalid historical object header")
            self._fill(deadline)

    def take(self, size, deadline):
        while len(self.buffer) < size:
            self._fill(deadline)
        result = bytes(self.buffer[:size]); del self.buffer[:size]
        return result

    def boundary(self, deadline):
        if self.line(deadline) != b" missing\n" or self.buffer:
            raise ValueError("unexpected historical object batch data")

    def finish(self, check):
        try:
            if check:
                self.process.stdin.close()
                deadline = time.monotonic() + _BATCH_TIMEOUT
                if self.buffer or os.read(self._ready(deadline), 1):
                    raise ValueError("unexpected historical object batch data")
                remaining = max(0.001, deadline - time.monotonic())
                if self.process.wait(timeout=remaining):
                    raise ValueError("Git document coordination command failed")
        except (OSError, subprocess.SubprocessError):
            raise ValueError("Git document coordination unavailable") from None
        finally:
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.process.kill(); self.process.wait(timeout=1)
            self.process.stdin.close(); self.process.stdout.close()


class _ObjectBatchSession:
    """Ephemeral POSIX transport for one generator; no cross-call state."""

    def __init__(self, repo):
        self.repo = repo; self.pipes = []; self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, kind, value, traceback):
        self.close(kind is None)

    def close(self, check):
        self.closed = True
        error = None
        for pipe in self.pipes:
            try:
                pipe.finish(check)
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                if error is None: error = exc
        self.pipes = []
        if error is not None:
            raise ValueError("Git historical object session did not close cleanly") from error

    def read(self, specifications, object_type, max_bytes):
        if (self.closed or not 1 <= len(specifications) <= 16
                or object_type not in {"tree", "blob"}
                or max_bytes != (128 if object_type == "tree" else MAX_BYTES)
                or any(type(spec) is not str or re.fullmatch(
                    r"(?:[0-9a-f]{40}|[0-9a-f]{64})(?:\^\{tree\})?", spec) is None
                       for spec in specifications)):
            raise ValueError("invalid historical object batch")
        if not self.pipes:
            try:
                self.pipes.append(_ObjectPipe(self.repo, "--batch-check"))
                self.pipes.append(_ObjectPipe(self.repo, "--batch"))
            except BaseException:
                self.close(False)
                raise
        check, body = self.pipes
        deadline = time.monotonic() + _BATCH_TIMEOUT
        check.send(specifications, deadline)
        headers = [check.line(deadline) for _ in specifications]
        check.boundary(deadline)
        checked = []
        for header in headers:
            parts = header.split()
            if (len(parts) != 3 or not REVISION.fullmatch(parts[0].decode("ascii"))
                    or parts[1] != object_type.encode("ascii") or not parts[2].isdigit()
                    or int(parts[2]) > max_bytes):
                raise ValueError("invalid historical object type or size")
            checked.append((header, int(parts[2])))
        deadline = time.monotonic() + _BATCH_TIMEOUT
        body.send(specifications, deadline)
        values = []
        for header, size in checked:
            if body.line(deadline) != header:
                raise ValueError("historical object batch changed")
            values.append(body.take(size, deadline))
            if body.take(1, deadline) != b"\n":
                raise ValueError("incomplete historical object body")
        body.boundary(deadline)
        return values


class GitDocumentStore:
    """Non-force remote CAS; every proposal has an unpredictable commit nonce.

    This ref must be dedicated to document.json. Reads reject any other root
    content, so this store cannot silently erase another coordination format.
    """

    def __init__(self, repo, remote, coordination_ref, coordination_store_id, *, protected_refs=()):
        self.repo = repository_root(repo)
        self.remote = remote
        self.ref = coordination_ref
        self.store_id = coordination_store_id
        if not isinstance(self.ref, str) or not self.ref.startswith("refs/heads/cdc/"):
            raise ValueError("document coordination ref must be a dedicated refs/heads/cdc/ ref")
        if not isinstance(self.store_id, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", self.store_id):
            raise ValueError("coordination endpoint identity must be explicit")
        self._git("check-ref-format", self.ref)
        protected = {portable_path_key(ref) for ref in protected_refs}
        if portable_path_key(self.ref) in protected:
            raise ValueError("coordination ref must be portable-isolated from product refs")
        self._assert_remote_identity()

    def _assert_remote_identity(self):
        if remote_identity(self.repo, self.remote) != self.store_id:
            raise ValueError("document coordination remote identity drift")

    def _git(self, *args, input_text=None):
        env = git_object_environment(GIT_TERMINAL_PROMPT="0", GIT_AUTHOR_NAME="CDC coordination",
                   GIT_AUTHOR_EMAIL="cdc@example.invalid", GIT_COMMITTER_NAME="CDC coordination",
                   GIT_COMMITTER_EMAIL="cdc@example.invalid")
        try:
            result = subprocess.run(["git", "-C", str(self.repo), *args], input=input_text, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=20)
        except (OSError, subprocess.SubprocessError):
            raise ValueError("Git document coordination unavailable") from None
        if result.returncode:
            raise ValueError("Git document coordination command failed")
        return result.stdout.rstrip("\n")

    def _remote_revision(self):
        self._assert_remote_identity()
        rows = self._git("ls-remote", "--refs", self.remote, self.ref).splitlines()
        if not rows:
            return None
        if len(rows) != 1:
            raise ValueError("ambiguous document coordination ref")
        parts = rows[0].split("\t")
        if len(parts) != 2 or parts[1] != self.ref or not REVISION.fullmatch(parts[0]):
            raise ValueError("invalid document coordination revision")
        return parts[0]

    def read(self):
        revision = self._remote_revision()
        if revision is None:
            return None, None
        config, remote = isolated_remote_args(self.repo, self.remote, self.store_id)
        self._git(*config, "fetch", "--no-tags", "--no-write-fetch-head", "--refmap=", remote, self.ref)
        if self._git("cat-file", "-t", revision) != "commit":
            raise ValueError("document coordination ref must point to a commit")
        if self._git("ls-tree", "--name-only", revision).splitlines() != [STATE_FILE]:
            raise ValueError("dedicated coordination tree must contain only document.json")
        document = self._read_document_object(revision)
        if revision != self._remote_revision():
            raise ValueError("coordination ref moved during read")
        return revision, document

    def read_revision(self, revision):
        """Read an immutable document from this coordination ref's authoritative history."""
        if not isinstance(revision, str) or not REVISION.fullmatch(revision):
            raise ValueError("invalid historical document revision")
        current, _ = self.read()
        if current is None:
            raise ValueError("document coordination history is absent")
        if self._git("cat-file", "-t", revision) != "commit":
            raise ValueError("historical document revision must be a commit")
        try:
            base = self._git("merge-base", revision, current)
        except ValueError:
            raise ValueError("historical revision is not in authoritative document ancestry") from None
        if base != revision:
            raise ValueError("historical revision is not in authoritative document ancestry")
        return self._read_document_object(revision)

    def _read_document_object(self, revision):
        """Decode a genuine immutable object from an already authenticated snapshot."""
        document, = self._read_document_objects([revision])
        return document

    def _batch_objects(self, specifications, object_type, max_bytes):
        """Read a small immutable batch, checking sizes before materializing bodies.

        Specifications are constructed here from full object IDs, never caller
        expressions. Both subprocesses disable replacement refs and grafts.
        """
        request = ("\n".join(specifications) + "\n").encode("ascii")
        env = git_object_environment(GIT_TERMINAL_PROMPT="0")

        def run(option):
            try:
                result = subprocess.run(
                    ["git", "-C", str(self.repo), "cat-file", option], input=request,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=20)
            except (OSError, subprocess.SubprocessError):
                raise ValueError("Git document coordination unavailable") from None
            if result.returncode:
                raise ValueError("Git document coordination command failed")
            return result.stdout

        headers = run("--batch-check").splitlines()
        if len(headers) != len(specifications):
            raise ValueError("incomplete historical object batch")
        checked = []
        for header in headers:
            parts = header.split()
            if (len(parts) != 3 or not REVISION.fullmatch(parts[0].decode("ascii"))
                    or parts[1] != object_type.encode("ascii") or not parts[2].isdigit()
                    or int(parts[2]) > max_bytes):
                raise ValueError("invalid historical object type or size")
            checked.append((header, int(parts[2])))
        raw = run("--batch")
        offset = 0
        values = []
        for header, size in checked:
            prefix = header + b"\n"
            if raw[offset:offset + len(prefix)] != prefix:
                raise ValueError("historical object batch changed")
            offset += len(prefix)
            value = raw[offset:offset + size]
            offset += size
            if len(value) != size or raw[offset:offset + 1] != b"\n":
                raise ValueError("incomplete historical object body")
            offset += 1
            values.append(value)
        if offset != len(raw):
            raise ValueError("unexpected historical object batch data")
        return values

    def _read_document_objects(self, revisions):
        """Decode every authenticated revision, with bounded batched Git I/O.

        This is transport only: callers still authenticate the complete native
        graph, endpoint and fresh head. No process/persistent authority is added.
        At most 16 trees or 16 bounded document blobs are materialized at once.
        """
        from itertools import islice
        from contextlib import nullcontext
        revisions = iter(revisions)
        session = _ObjectBatchSession(self.repo) if os.name == "posix" else None
        with session if session is not None else nullcontext():
            batch = session.read if session is not None else self._batch_objects
            while True:
                chunk = list(islice(revisions, 16))
                if not chunk:
                    return
                if any(not isinstance(revision, str) or not REVISION.fullmatch(revision)
                       for revision in chunk):
                    raise ValueError("invalid historical document revision")
                trees = batch([revision + "^{tree}" for revision in chunk], "tree", 128)
                blobs = []
                for revision, tree in zip(chunk, trees):
                    # Exactly one root entry named document.json; reject trees,
                    # gitlinks and any additional entry before reading JSON.
                    header, separator, oid = tree.partition(b"\0")
                    if (not separator or not re.fullmatch(rb"[0-7]+ document\.json", header)
                            or len(oid) != len(revision) // 2):
                        raise ValueError("historical coordination tree must contain only document.json")
                    blobs.append(oid.hex())
                for payload in batch(blobs, "blob", MAX_BYTES):
                    # Match _git's text/universal-newline and trailing-LF handling.
                    payload = payload.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"
                    # Exact canonical equality already excludes duplicate keys.
                    # Decode valid history in C; preserve the original strict
                    # decoder and its error ordering for every rejected payload.
                    try:
                        document = json.loads(payload)
                        exact = canonical(document) == payload
                    except (ValueError, TypeError, RecursionError):
                        exact = False
                    if not exact:
                        document = None
                        document = json.loads(payload, object_pairs_hook=unique_object)
                        if canonical(document) != payload:
                            raise ValueError("historical coordination document must have canonical JSON encoding")
                    yield document

    def compare_and_swap(self, expected_revision, document, *, recovery_capability=None):
        payload = canonical(document)
        current, previous = self.read()
        if expected_revision != current:
            raise ValueError("stale expected document revision")
        from unknown_recovery import validate_intake_transition
        validate_intake_transition(previous, document, store=self, expected_revision=expected_revision, recovery_capability=recovery_capability)
        blob = self._git("hash-object", "-w", "--stdin", input_text=payload)
        tree = self._git("mktree", input_text=f"100644 blob {blob}\t{STATE_FILE}\n")
        parent = ["-p", expected_revision] if expected_revision else []
        commit = self._git("commit-tree", tree, *parent,
                           input_text="Update CDC coordination\n\nCAS proposal: " + secrets.token_hex(32) + "\n")
        # Only the SDK-issued one-use consumption can retain its own proposal.
        # This non-secret local commit identity is not a launch permission.
        from unknown_recovery import _StartConsumption
        if type(recovery_capability) is _StartConsumption:
            recovery_capability._bind_proposal(self, expected_revision, commit)
        # Revalidate immediately before the side effect; never force-update the ref.
        self._assert_remote_identity()
        config, remote = isolated_remote_args(self.repo, self.remote, self.store_id)
        self._git(*config, "-c", "push.followTags=false", "push", "--porcelain", remote, f"{commit}:{self.ref}")
        if self._remote_revision() != commit:
            raise ValueError("document CAS did not become authoritative")
        return commit
