import json
import tempfile
import unittest
from pathlib import Path

from mep.revisions import (
    correct,
    decide,
    drift_report,
    effective_preferences,
    graph_summary,
    is_approved,
    load_approvals,
    load_graph,
    propose,
    validate_record,
)

OWNER = "owner-test"
AGENT = "agent-test"


def base_record(**overrides):
    record = {
        "schema_version": "0.1",
        "preference_id": "pref-1",
        "revision_id": "rev-1",
        "parent_revision_ids": [],
        "owner_id": OWNER,
        "author_id": OWNER,
        "status": "active",
        "origin": "explicit",
        "statement": "Use concise explanations by default.",
        "scope": {"contexts": ["writing"]},
        "source": {"kind": "user", "reference": "source-1"},
    }
    record.update(overrides)
    return record


def write_record(root: Path, directory: str, record: dict) -> Path:
    target = root / ".mep" / directory
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{record['revision_id']}.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return path


class ValidationTests(unittest.TestCase):
    def test_valid_explicit(self):
        self.assertEqual(validate_record(base_record()), [])

    def test_inferred_requires_confidence(self):
        record = base_record(origin="inferred", author_id=AGENT, revision_id="rev-2")
        self.assertIn("inference requires confidence", validate_record(record))
        record["confidence"] = 0.7
        self.assertEqual(validate_record(record), [])

    def test_explicit_must_not_carry_confidence(self):
        record = base_record(confidence=0.5)
        self.assertIn("explicit revisions must not carry confidence", validate_record(record))

    def test_tombstone_must_not_carry_payload(self):
        record = base_record(status="deleted", parent_revision_ids=["rev-0"])
        del record["statement"], record["scope"], record["source"], record["origin"]
        self.assertEqual(validate_record(record), [])
        record["statement"] = "leak"
        self.assertIn("rejection or deletion carries preference data: statement", validate_record(record))

    def test_rejected_requires_parent(self):
        record = base_record(status="rejected")
        for key in ("origin", "statement", "scope", "source"):
            del record[key]
        self.assertIn("rejection or deletion requires at least one parent", validate_record(record))

    def test_self_parent_rejected(self):
        record = base_record(parent_revision_ids=["rev-1"])
        self.assertIn("a revision must not name itself as a parent", validate_record(record))


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_duplicate_revision_id_flagged(self):
        write_record(self.root, "revisions", base_record())
        write_record(self.root, "proposals", base_record(revision_id="rev-1", origin="inferred", author_id=AGENT, confidence=0.5))
        graph = load_graph(self.root)
        self.assertTrue(any("duplicate revision_id" in e for e in graph["errors"]))

    def test_unknown_parent_flagged(self):
        write_record(self.root, "revisions", base_record(parent_revision_ids=["rev-absent"]))
        graph = load_graph(self.root)
        self.assertTrue(any("unknown parent" in e for e in graph["errors"]))

    def test_owner_mismatch_flagged(self):
        write_record(self.root, "revisions", base_record())
        write_record(self.root, "revisions", base_record(revision_id="rev-2", parent_revision_ids=["rev-1"], owner_id="someone-else"))
        graph = load_graph(self.root)
        self.assertTrue(any("inconsistent owner_id" in e for e in graph["errors"]))

    def test_cycle_detected(self):
        write_record(self.root, "revisions", base_record(revision_id="rev-a", parent_revision_ids=["rev-b"]))
        write_record(self.root, "revisions", base_record(revision_id="rev-b", parent_revision_ids=["rev-a"]))
        graph = load_graph(self.root)
        self.assertTrue(any("cycle" in e for e in graph["errors"]))

    def test_cross_preference_parent_flagged(self):
        write_record(self.root, "revisions", base_record(revision_id="rev-1", preference_id="pref-a"))
        write_record(self.root, "revisions", base_record(revision_id="rev-2", preference_id="pref-b", parent_revision_ids=["rev-1"]))
        graph = load_graph(self.root)
        self.assertTrue(any("different preference" in e for e in graph["errors"]))


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _proposal(self, **overrides):
        args = dict(
            statement="Prefer terse bullet summaries.",
            origin="inferred",
            confidence=0.8,
            scope_contexts=["writing"],
            source_kind="observation",
            source_reference="ref-1",
            owner_id=OWNER,
            author_id=AGENT,
        )
        args.update(overrides)
        return propose(self.root, **args)

    def test_proposal_never_applies_alone(self):
        self._proposal()
        graph = load_graph(self.root)
        summary = graph_summary(graph)
        self.assertEqual(summary["proposals_pending"], 1)
        approvals = load_approvals(self.root)
        effective = effective_preferences(graph, approvals)
        self.assertEqual(effective["preferences"], {})

    def test_approve_applies_inferred_head(self):
        proposal = self._proposal()
        rev_id = proposal["proposal"]["revision_id"]
        decide(self.root, target_revision_id=rev_id, decision="approve", owner_id=OWNER, note="yes")
        graph = load_graph(self.root)
        self.assertEqual(graph["proposals"], [])
        approvals = load_approvals(self.root)
        self.assertTrue(is_approved(approvals, OWNER, proposal["proposal"]["preference_id"], rev_id))
        effective = effective_preferences(graph, approvals)
        pref = proposal["proposal"]["preference_id"]
        self.assertEqual(effective["preferences"][pref]["state"], "applied")
        self.assertEqual(effective["preferences"][pref]["origin"], "inferred-approved")

    def test_explicit_correction_supersedes_unapproved_inference(self):
        proposal = self._proposal()
        pref = proposal["proposal"]["preference_id"]
        correct(
            self.root,
            statement="Bullet summaries are fine for reports, not for decisions.",
            scope_contexts=["writing"],
            source_kind="user",
            source_reference="owner-session",
            owner_id=OWNER,
            preference_id=pref,
        )
        graph = load_graph(self.root)
        approvals = load_approvals(self.root)
        effective = effective_preferences(graph, approvals)
        entry = effective["preferences"][pref]
        self.assertEqual(entry["state"], "applied")
        self.assertEqual(entry["origin"], "explicit")
        self.assertIn("Bullet summaries are fine", entry["statement"])
        # The unapproved inference is superseded by the correction; its
        # proposal file moves to .mep/decided/ and no longer shows as pending.
        self.assertEqual(effective["pending_proposals"], [])
        self.assertEqual(list((self.root / ".mep" / "proposals").glob("*.json")), [])
        self.assertTrue(list((self.root / ".mep" / "decided").glob("*.json")))

    def test_reject_suppresses_preference(self):
        proposal = self._proposal()
        rev_id = proposal["proposal"]["revision_id"]
        decide(self.root, target_revision_id=rev_id, decision="reject", owner_id=OWNER)
        graph = load_graph(self.root)
        self.assertEqual(graph["proposals"], [])
        self.assertTrue((self.root / ".mep" / "decided" / f"{rev_id}.json").is_file())
        effective = effective_preferences(graph, load_approvals(self.root))
        self.assertEqual(effective["preferences"][proposal["proposal"]["preference_id"]]["state"], "suppressed")

    def test_conflicting_explicit_and_inference_both_heads(self):
        first = correct(
            self.root,
            statement="Keep examples under five lines.",
            scope_contexts=["writing"],
            source_kind="user",
            source_reference="owner-session",
            owner_id=OWNER,
        )
        pref = first["revision"]["preference_id"]
        self._proposal(preference_id=pref)
        # Owner correction naming both heads resolves the conflict.
        correct(
            self.root,
            statement="Examples under five lines, but decisions get the full derivation.",
            scope_contexts=["writing"],
            source_kind="user",
            source_reference="owner-session",
            owner_id=OWNER,
            preference_id=pref,
        )
        graph = load_graph(self.root)
        effective = effective_preferences(graph, load_approvals(self.root))
        entry = effective["preferences"][pref]
        self.assertEqual(entry["state"], "applied")

    def test_only_owner_can_decide(self):
        proposal = self._proposal()
        rev_id = proposal["proposal"]["revision_id"]
        with self.assertRaises(ValueError):
            decide(self.root, target_revision_id=rev_id, decision="approve", owner_id="someone-else")

    def test_drift_flags_pending_proposal(self):
        self._proposal()
        graph = load_graph(self.root)
        drift = drift_report(self.root, graph, [], max_pending_days=0)
        self.assertTrue(any(f["kind"] == "proposal_pending" for f in drift["findings"]))


if __name__ == "__main__":
    unittest.main()
