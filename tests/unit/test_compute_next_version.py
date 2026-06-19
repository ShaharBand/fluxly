import importlib.util
import sys
import unittest
from pathlib import Path


def _load_compute_next_version():
    script_path = Path(__file__).resolve().parents[2] / ".github" / "scripts" / "compute_next_version.py"
    spec = importlib.util.spec_from_file_location("compute_next_version", script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["compute_next_version"] = module
    spec.loader.exec_module(module)
    return module


cnv = _load_compute_next_version()


class ComputeNextVersionTest(unittest.TestCase):
    def test_patch_bump_from_release_version(self) -> None:
        self.assertEqual(cnv.compute_next_version("1.0.3", "patch"), "1.0.4")

    def test_minor_bump_from_release_version(self) -> None:
        self.assertEqual(cnv.compute_next_version("1.0.3", "minor"), "1.1.0")

    def test_major_bump_from_release_version(self) -> None:
        self.assertEqual(cnv.compute_next_version("1.0.3", "major"), "2.0.0")

    def test_accepts_v_prefix(self) -> None:
        self.assertEqual(cnv.compute_next_version("v1.0.3", "patch"), "1.0.4")

    def test_rejects_hatch_dev_version(self) -> None:
        with self.assertRaises(ValueError):
            cnv.parse_release_version("1.1.dev0")

    def test_first_release_without_tags(self) -> None:
        self.assertEqual(cnv.compute_next_version("0.0.0", "patch"), "0.0.1")


if __name__ == "__main__":
    unittest.main()
