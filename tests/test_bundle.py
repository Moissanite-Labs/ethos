import json
import tempfile
import unittest
from pathlib import Path

from mep.bundle import export_bundle
from mep.integrity import verify_manifest
from mep.revisions import correct, propose


def make_tree(root: Path) -> None:
    (root / "principles").mkdir(parents=True)
    (root / "principles" / "a.md").write_text("# A\n\nAlpha rule.\n", encoding="utf-8")
    (root / "README.md").write_text("# test ethos\n", encoding="utf-8")


def manifest_ok(dest: Path) -> bool:
    lines = (dest / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines()
    import hashlib

    for line in lines:
        digest, rel = line.split("  ", 1)
        if hashlib.sha256((dest / rel).read_bytes()).hexdigest() != digest:
            return False
    return True


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "ethos"
        self.root.mkdir()
        make_tree(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_export_bundle_verifies(self):
        correct(
            self.root,
            statement="Ship small, verify everything.",
            scope_contexts=["shipping"],
            source_kind="user",
            source_reference="owner-session",
            owner_id="owner-test",
        )
        dest = Path(self.tmp.name) / "export"
        result = export_bundle(self.root, dest)
        self.assertEqual(result["revisions"], 1)
        self.assertTrue((dest / "documents" / "principles" / "a.md").is_file())
        self.assertTrue((dest / "revisions").is_dir())
        self.assertTrue(manifest_ok(dest))

    def test_export_refuses_broken_graph(self):
        bad = self.root / ".mep" / "revisions"
        bad.mkdir(parents=True)
        (bad / "rev-bad.json").write_text("{not json", encoding="utf-8")
        with self.assertRaises(ValueError):
            export_bundle(self.root, Path(self.tmp.name) / "out")

    def test_export_refuses_nonempty_dest(self):
        dest = Path(self.tmp.name) / "occupied"
        dest.mkdir()
        (dest / "keep.txt").write_text("x", encoding="utf-8")
        with self.assertRaises(ValueError):
            export_bundle(self.root, dest)

    def test_pending_proposals_included(self):
        propose(
            self.root,
            statement="Something observed.",
            origin="inferred",
            confidence=0.6,
            scope_contexts=[],
            source_kind="observation",
            source_reference="ref",
            owner_id="owner-test",
            author_id="agent-test",
        )
        dest = Path(self.tmp.name) / "export2"
        result = export_bundle(self.root, dest)
        self.assertEqual(result["proposals"], 1)
        self.assertTrue(list((dest / "proposals").glob("*.json")))


if __name__ == "__main__":
    unittest.main()
