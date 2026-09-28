"""Independent checks against actual release records, not only templates."""
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "src/continuous-development-cycle"


def read(path):
    return json.loads((ROOT / path).read_text())


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


class ReleaseBindingsTests(unittest.TestCase):
    def test_candidate_agrees_with_version_and_development_base(self):
        version = (ROOT / "VERSION").read_text().strip()
        candidate = read("release/candidate.json")
        lock = read("release/source.lock.json")
        matrix = read("compatibility/matrix.json")
        self.assertIn(candidate["status"], {"candidate", "released"})
        for actual in (candidate["version"], lock["target_version"], matrix["target_version"],
                       read(PACKAGE + "/manifest.json")["version"],
                       (ROOT / PACKAGE / "VERSION").read_text().strip()):
            self.assertEqual(actual, version)
        self.assertEqual(candidate["developed_under_version"], lock["development_driver_version"])
        self.assertEqual(matrix["developed_under_version"], lock["development_driver_version"])
        self.assertIn(lock["development_driver_version"], matrix["supported_from_versions"])
        self.assertEqual(set(candidate["evidence"]),
                         {"bootstrap", "package", "compatibility", "fault_injection", "consumers"})

    def test_prior_driver_is_the_recorded_git_package(self):
        lock = read("release/source.lock.json")
        source = lock["base_validation_commit"]
        self.assertRegex(source, r"^[0-9a-f]{40}$")
        self.assertEqual(git("show", source + ":" + PACKAGE + "/VERSION"),
                         lock["development_driver_version"])
        self.assertEqual(git("rev-parse", source + ":" + PACKAGE), lock["base_package_tree"])

    def test_candidate_and_snapshots_bind_actual_package(self):
        candidate = read("release/candidate.json")
        self.assertRegex(candidate["source_commit"], r"^[0-9a-f]{40}$")
        actual = git("rev-parse", "HEAD:" + PACKAGE)
        self.assertEqual(candidate["package_tree"], actual)
        self.assertEqual(git("rev-parse", candidate["source_commit"] + ":" + PACKAGE), actual)
        for consumer in ("g-supervisor", "g-ad-control", "g-pc-health-check"):
            with self.subTest(consumer=consumer):
                snapshot = read("consumer/evidence/" + consumer + "/source.json")
                self.assertEqual(snapshot["candidate_version"], candidate["version"])
                self.assertEqual(snapshot["candidate_package_tree"], actual)
                self.assertRegex(snapshot["source_commit"], r"^[0-9a-f]{40}$")

    def test_release_evidence_paths_exist(self):
        for refs in read("release/candidate.json")["evidence"].values():
            for ref in refs:
                if ref.startswith(("release/", "docs/", "bootstrap/", "src/", "fault-injection/")):
                    self.assertTrue((ROOT / ref.split("#", 1)[0]).is_file(), ref)

    def test_no_tests_hidden_below_non_packages(self):
        tests = ROOT / PACKAGE / "tests"
        for path in tests.rglob("test_*.py"):
            parent = path.parent
            while parent != tests:
                self.assertTrue((parent / "__init__.py").is_file(),
                                "unittest discovery skips " + str(path.relative_to(ROOT)))
                parent = parent.parent
