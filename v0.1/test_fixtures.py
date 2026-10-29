"""Fixture contract checks; not a general JSON Schema validator."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parent


def load(name):
    return json.loads((ROOT / "fixtures" / name).read_text())


def problems(record):
    errors = []
    required = {"schema_version", "preference_id", "revision_id", "parent_revision_ids", "owner_id", "author_id", "status"}
    allowed = required | {"origin", "statement", "confidence", "scope", "source"}
    if required - record.keys() or record.keys() - allowed:
        errors.append("missing or unknown fields")
    if record.get("schema_version") != "0.1" or record.get("status") not in {"active", "rejected", "deleted"}:
        errors.append("version or status")
    for key in ("preference_id", "revision_id", "owner_id", "author_id"):
        if not isinstance(record.get(key), str) or not record[key]:
            errors.append(key)
    parents = record.get("parent_revision_ids")
    if not isinstance(parents, list) or any(not isinstance(x, str) or not x for x in parents) or len(set(parents)) != len(parents):
        errors.append("parents")
    fields = {"origin", "statement", "scope", "source"}
    if record.get("status") == "deleted":
        if (fields | {"confidence"}) & record.keys():
            errors.append("tombstone contains preference data")
    else:
        if fields - record.keys() or record.get("origin") not in {"explicit", "inferred"} or not isinstance(record.get("statement"), str) or not record.get("statement"):
            errors.append("preference fields")
        if record.get("origin") == "inferred":
            c = record.get("confidence")
            if isinstance(c, bool) or not isinstance(c, (int, float)) or not 0 <= c <= 1:
                errors.append("inference confidence")
        elif "confidence" in record:
            errors.append("explicit confidence")
        scope, source = record.get("scope"), record.get("source")
        if not isinstance(scope, dict) or set(scope) != {"contexts"} or not isinstance(scope["contexts"], list) or any(not isinstance(x, str) or not x for x in scope["contexts"]) or len(set(scope["contexts"])) != len(scope["contexts"]):
            errors.append("scope")
        if not isinstance(source, dict) or set(source) != {"kind", "reference"} or any(not isinstance(x, str) or not x for x in source.values()):
            errors.append("source")
    return errors


class Fixtures(unittest.TestCase):
    def test_valid(self):
        for name in ("explicit.json", "inferred.json", "tombstone.json", "rejected.json"):
            with self.subTest(name=name):
                self.assertEqual(problems(load(name)), [])

    def test_invalid(self):
        for name in ("invalid-inference.json", "invalid-tombstone.json"):
            with self.subTest(name=name):
                self.assertTrue(problems(load(name)))

    def test_concurrent_delete_and_edit_share_parent(self):
        original, edit, tombstone = (load(n) for n in ("explicit.json", "inferred.json", "tombstone.json"))
        self.assertEqual(edit["parent_revision_ids"], [original["revision_id"]])
        self.assertEqual(tombstone["parent_revision_ids"], [original["revision_id"]])
        self.assertEqual(len({original["preference_id"], edit["preference_id"], tombstone["preference_id"]}), 1)
        self.assertEqual(len({original["revision_id"], edit["revision_id"], tombstone["revision_id"]}), 3)

    def test_rejection_is_distinct_owner_authored_revision(self):
        original, rejection = load("explicit.json"), load("rejected.json")
        self.assertEqual(rejection["parent_revision_ids"], [original["revision_id"]])
        self.assertEqual(rejection["owner_id"], rejection["author_id"])
        self.assertEqual(rejection["status"], "rejected")

    def test_schema_and_fixture_enums_match(self):
        schema = json.loads((ROOT / "schema.json").read_text())
        self.assertEqual(schema["properties"]["schema_version"]["const"], "0.1")
        self.assertEqual(set(schema["properties"]["status"]["enum"]), {"active", "rejected", "deleted"})
        self.assertEqual(set(schema["properties"]["origin"]["enum"]), {"explicit", "inferred"})
        self.assertEqual(set(schema["required"]), {"schema_version", "preference_id", "revision_id", "parent_revision_ids", "owner_id", "author_id", "status"})


if __name__ == "__main__":
    unittest.main()
