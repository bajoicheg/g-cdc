"""Independent release-binding Git reads reject local replacement overlays."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import test_release_bindings


class BootstrapGitObjectIntegrityTests(unittest.TestCase):
    def test_release_binding_reader_uses_genuine_commit_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = dict(os.environ, GIT_AUTHOR_NAME="Bootstrap fixture", GIT_AUTHOR_EMAIL="bootstrap@example.invalid",
                       GIT_COMMITTER_NAME="Bootstrap fixture", GIT_COMMITTER_EMAIL="bootstrap@example.invalid")
            def git(*args, input=None):
                return subprocess.check_output(["git", "-C", str(root), *args], input=input, text=True, env=env).strip()
            git("init", "-q")
            commits = []
            for value in ["genuine\n", "counterfeit\n"]:
                blob = git("hash-object", "-w", "--stdin", input=value)
                tree = git("mktree", input=f"100644 blob {blob}\tVERSION\n")
                commits.append(git("commit-tree", tree, input=value))
            git("replace", *commits)
            with mock.patch.object(test_release_bindings, "ROOT", root):
                self.assertEqual(test_release_bindings.git("show", commits[0] + ":VERSION"), "genuine")
