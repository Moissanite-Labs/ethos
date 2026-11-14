import tempfile
import unittest
from pathlib import Path

from mep.integrity import verify_manifest, write_manifest


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "principles").mkdir()
        (self.root / "principles" / "a.md").write_text("# A\n", encoding="utf-8")
        (self.root / "README.md").write_text("# test\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_roundtrip_ok(self):
        write_manifest(self.root)
        report = verify_manifest(self.root)
        self.assertTrue(report["ok"])
        self.assertEqual(report["files_verified"], 2)

    def test_tamper_detected(self):
        write_manifest(self.root)
        (self.root / "principles" / "a.md").write_text("# changed\n", encoding="utf-8")
        report = verify_manifest(self.root)
        self.assertFalse(report["ok"])
        self.assertIn("principles/a.md", report["mismatched_files"])

    def test_missing_detected(self):
        write_manifest(self.root)
        (self.root / "README.md").unlink()
        report = verify_manifest(self.root)
        self.assertFalse(report["ok"])
        self.assertIn("README.md", report["missing_files"])

    def test_malformed_line_detected(self):
        (self.root / "SHA256SUMS").write_text("not-a-hash  README.md\n", encoding="utf-8")
        report = verify_manifest(self.root)
        self.assertFalse(report["ok"])
        self.assertTrue(report["malformed_lines"])

    def test_unconfined_path_detected(self):
        (self.root / "SHA256SUMS").write_text("0" * 64 + "  ../escape.md\n", encoding="utf-8")
        report = verify_manifest(self.root)
        self.assertFalse(report["ok"])
        self.assertEqual(report["unconfined_paths"][0]["path"], "../escape.md")

    def test_missing_manifest_reports_absent(self):
        report = verify_manifest(self.root)
        self.assertFalse(report["manifest_present"])
        self.assertFalse(report["ok"])


if __name__ == "__main__":
    unittest.main()
