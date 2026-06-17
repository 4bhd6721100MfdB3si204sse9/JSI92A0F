import tempfile
import unittest
from pathlib import Path

from sentinel.output import allocate_run_dir, unique_run_dir


class OutputTest(unittest.TestCase):
    def test_unique_run_dir_adds_suffix_when_timestamp_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "20260614T000000Z").mkdir()
            (root / "20260614T000000Z-01").mkdir()

            run_dir = unique_run_dir(root, "20260614T000000Z")

            self.assertEqual(run_dir.name, "20260614T000000Z-02")

    def test_allocate_run_dir_creates_unique_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            first = allocate_run_dir(root, "20260614T000000Z")
            second = allocate_run_dir(root, "20260614T000000Z")

            self.assertTrue(first.exists())
            self.assertTrue(second.exists())
            self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
