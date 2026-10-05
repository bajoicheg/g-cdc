import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import consumer_package_checks as checks

class CleanConsumerTests(unittest.TestCase):
    def fixture(self,body):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        root=Path(tmp.name);pkg=root/'src'/'package';(pkg/'tests').mkdir(parents=True)
        (root/'canonical-only').write_text('undeclared fixture')
        (pkg/'tests'/'test_probe.py').write_text('import unittest\nfrom pathlib import Path\nclass T(unittest.TestCase):\n def test_probe(self):\n  '+body+'\n')
        return pkg
    def test_package_runs_without_canonical_siblings(self):
        pkg=self.fixture('self.assertFalse((Path(__file__).resolve().parents[3]/"canonical-only").exists())')
        with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(checks.run(pkg),0)
    def test_clean_layout_failure_is_propagated(self):
        pkg=self.fixture('(Path(__file__).resolve().parents[3]/"canonical-only").read_text()')
        with contextlib.redirect_stdout(io.StringIO()):self.assertNotEqual(checks.run(pkg),0)

if __name__=='__main__':unittest.main()
