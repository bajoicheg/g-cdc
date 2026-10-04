import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"bootstrap"))
from validate_release import matrix,source_lock
from src.cdc27.compatibility import validate_matrix
from src.cdc27.canonical_source import validate_source_lock
class CompatibilityFloorTests(unittest.TestCase):
    def matrix(self):
        d=json.loads((ROOT/"compatibility/matrix.json").read_text())
        d.update(minimum_supported_version="2.11.3",target_version="2.11.4",developed_under_version="2.11.3",supported_from_versions=["2.11.3"])
        return d
    def lock(self,target="2.11.4",driver="2.11.3"):
        d=json.loads((ROOT/"release/source.lock.json").read_text());d.update(target_version=target,development_driver_version=driver);return d
    def test_accepts_supported_matrix_boundary(self):
        for validate in (matrix,validate_matrix):
            with self.subTest(validator=validate.__module__):validate(self.matrix())
    def test_rejects_unsupported_runtime_in_matrix(self):
        d=self.matrix();d["supported_from_versions"].append("2.11.2")
        for validate in (matrix,validate_matrix):
            with self.subTest(validator=validate.__module__),self.assertRaisesRegex(ValueError,"2.11.3"):validate(d)
    def test_rejects_weakened_declared_floor(self):
        d=self.matrix();d["minimum_supported_version"]="2.10.0"
        for validate in (matrix,validate_matrix):
            with self.subTest(validator=validate.__module__),self.assertRaisesRegex(ValueError,"2.11.3"):validate(d)
    def test_accepts_supported_driver_boundary(self):
        for validate in (source_lock,validate_source_lock):
            with self.subTest(validator=validate.__module__):validate(self.lock())
    def test_rejects_unsupported_driver_even_for_supported_target(self):
        for validate in (source_lock,validate_source_lock):
            with self.subTest(validator=validate.__module__),self.assertRaisesRegex(ValueError,"2.11.3"):validate(self.lock("2.11.3","2.11.2"))
    def test_rejects_unsupported_target_and_driver(self):
        for validate in (source_lock,validate_source_lock):
            with self.subTest(validator=validate.__module__),self.assertRaisesRegex(ValueError,"2.11.3"):validate(self.lock("2.11.2","2.11.1"))
