import json
import tempfile
import unittest
from pathlib import Path

from mep.ethos import (
    build_context,
    learning_mode,
    load_ethos,
    query_ethos,
    read_document,
)


def make_tree(root: Path) -> None:
    (root / "principles").mkdir(parents=True)
    (root / "sops").mkdir(parents=True)
    (root / "principles" / "writing.md").write_text(
        "# Writing\n\nPlain language. Short sentences. Verify claims before they ship.\n", encoding="utf-8"
    )
    (root / "principles" / "security.md").write_text(
        "# Security\n\nNo secrets in shared artifacts. Private by default.\n", encoding="utf-8"
    )
    (root / "sops" / "github.md").write_text(
        "# GitHub SOP\n\nOpen a PR, keep it small, squash-merge with a clean message.\n", encoding="utf-8"
    )
    (root / "README.md").write_text("# my ethos\n\nThe record of how I work.\n", encoding="utf-8")


class DiscoverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_tree(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_discovers_layout_and_root_docs(self):
        ethos = load_ethos(self.root)
        paths = ethos.doc_paths
        self.assertIn("principles/writing.md", paths)
        self.assertIn("principles/security.md", paths)
        self.assertIn("sops/github.md", paths)
        self.assertIn("README.md", paths)

    def test_hashes_are_stable(self):
        a = load_ethos(self.root)
        b = load_ethos(self.root)
        self.assertEqual([d.sha256 for d in a.documents], [d.sha256 for d in b.documents])

    def test_missing_root_raises(self):
        with self.assertRaises(ValueError):
            load_ethos(self.root / "nope")


class QueryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_tree(self.root)
        self.ethos = load_ethos(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_ranking_prefers_relevant_doc(self):
        result = query_ethos(self.ethos, "verify claims")
        self.assertGreater(result["matched_documents"], 0)
        self.assertEqual(result["results"][0]["path"], "principles/writing.md")

    def test_deterministic(self):
        first = query_ethos(self.ethos, "secrets private")
        second = query_ethos(self.ethos, "secrets private")
        self.assertEqual([r["path"] for r in first["results"]], [r["path"] for r in second["results"]])
        self.assertEqual([r["score"] for r in first["results"]], [r["score"] for r in second["results"]])

    def test_scope_filter(self):
        result = query_ethos(self.ethos, "short", scope="principles")
        self.assertTrue(all(r["path"].startswith("principles/") for r in result["results"]))

    def test_no_terms(self):
        result = query_ethos(self.ethos, "a i")
        self.assertEqual(result["matched_documents"], 0)
        self.assertIn("note", result)


class ConfinementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_tree(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_escape_rejected(self):
        for bad in ("../secret.txt", "principles/../../etc/passwd", "/etc/passwd"):
            with self.assertRaises(ValueError):
                read_document(self.root, bad)


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_tree(self.root)
        self.ethos = load_ethos(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_budget_is_respected_and_omissions_listed(self):
        result = build_context(self.ethos, "writing plain language", budget_chars=350, depth="full")
        self.assertLessEqual(result["used_chars"], 350)
        self.assertTrue(result["omitted"] or any(i.get("truncated") for i in result["included"]))
        self.assertIn("## Sources", result["bundle"])

    def test_paths_depth_has_no_prose(self):
        result = build_context(self.ethos, "writing", budget_chars=4000, depth="paths")
        self.assertNotIn("## principles", result["bundle"])
        self.assertIn("sha256:", result["bundle"])

    def test_brief_depth_keeps_headings(self):
        result = build_context(self.ethos, "writing", budget_chars=6000, depth="brief")
        self.assertIn("# Writing", result["bundle"])


class LearningModeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_tree(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_default_on(self):
        self.assertEqual(learning_mode(self.root), "on")

    def test_file_switch_off(self):
        (self.root / ".mep").mkdir()
        (self.root / ".mep" / "learning").write_text("off\n", encoding="utf-8")
        self.assertEqual(learning_mode(self.root), "off")


if __name__ == "__main__":
    unittest.main()
