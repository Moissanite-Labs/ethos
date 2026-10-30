"""Fixture contract checks; not a general JSON Schema validator."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parent


def load(name):
    return json.loads((ROOT / "fixtures" / name).read_text())


def problems(record):
    if not isinstance(record, dict):
        return ["record must be an object"]
    errors = []
    required = {"schema_version", "preference_id", "revision_id", "parent_revision_ids", "owner_id", "author_id", "status"}
    allowed = required | {"origin", "statement", "confidence", "scope", "source"}
    if required - record.keys() or record.keys() - allowed:
        errors.append("missing or unknown fields")
    status = record.get("status")
    if record.get("schema_version") != "0.1" or not isinstance(status, str) or status not in {"active", "rejected", "deleted"}:
        errors.append("version or status")
    for key in ("preference_id", "revision_id", "owner_id", "author_id"):
        if not isinstance(record.get(key), str) or not record[key]:
            errors.append(key)
    parents = record.get("parent_revision_ids")
    if not isinstance(parents, list) or any(not isinstance(x, str) or not x for x in parents) or len(set(parents)) != len(parents):
        errors.append("parents")
    else:
        if status in ("rejected", "deleted") and not parents:
            errors.append("rejection or deletion requires a parent")
        if record.get("revision_id") in parents:
            errors.append("self parent")
    fields = {"origin", "statement", "scope", "source"}
    if status in ("deleted", "rejected"):
        if (fields | {"confidence"}) & record.keys():
            errors.append("rejection or tombstone contains preference data")
    else:
        origin = record.get("origin")
        if fields - record.keys() or not isinstance(origin, str) or origin not in {"explicit", "inferred"} or not isinstance(record.get("statement"), str) or not record.get("statement"):
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
        for name, expected in (("invalid-inference.json", "inference confidence"), ("invalid-tombstone.json", "rejection or tombstone contains preference data")):
            with self.subTest(name=name):
                self.assertIn(expected, problems(load(name)))

    def test_invalid_parents(self):
        for name in ("rejected.json", "tombstone.json"):
            with self.subTest(name=name):
                self.assertIn("rejection or deletion requires a parent", problems(dict(load(name), parent_revision_ids=[])))
        r = load("explicit.json")
        self.assertIn("self parent", problems(dict(r, parent_revision_ids=[r["revision_id"]])))

    def test_confidence_and_payload_rules(self):
        self.assertIn("explicit confidence", problems(dict(load("explicit.json"), confidence=0.5)))
        example = dict(load("explicit.json"), confidence=0.5)
        for name in ("rejected.json", "tombstone.json"):
            for field in ("origin", "statement", "confidence", "scope", "source"):
                with self.subTest(name=name, forbidden_field=field):
                    self.assertIn("rejection or tombstone contains preference data", problems(dict(load(name), **{field: example[field]})))

    def test_malformed_inputs_return_errors(self):
        for r in ([], dict(load("explicit.json"), status=[]), dict(load("explicit.json"), origin={}), dict(load("explicit.json"), parent_revision_ids=[{}]), dict(load("explicit.json"), scope={"contexts":[{}]})):
            with self.subTest(record=r):
                self.assertTrue(problems(r))

    def test_fixture_revision_ids_are_unique(self):
        records = [json.loads(p.read_text()) for p in (ROOT / "fixtures").glob("*.json")]
        ids = [r["revision_id"] for r in records]
        self.assertEqual(len(ids), len(set(ids)))

    def test_full_json_schema_when_available(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional jsonschema package is not installed")
        schema = json.loads((ROOT / "schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        for name in ("explicit.json", "inferred.json", "tombstone.json", "rejected.json"):
            with self.subTest(name=name):
                self.assertEqual(list(validator.iter_errors(load(name))), [])
        for name in ("invalid-inference.json", "invalid-tombstone.json"):
            with self.subTest(name=name):
                self.assertTrue(list(validator.iter_errors(load(name))))
        for name in ("rejected.json", "tombstone.json"):
            with self.subTest(name=name, case="empty parents"):
                self.assertTrue(list(validator.iter_errors(dict(load(name), parent_revision_ids=[]))))
        with self.subTest(case="explicit confidence"):
            self.assertTrue(list(validator.iter_errors(dict(load("explicit.json"), confidence=0.5))))
        example = dict(load("explicit.json"), confidence=0.5)
        for name in ("rejected.json", "tombstone.json"):
            for field in ("origin", "statement", "confidence", "scope", "source"):
                with self.subTest(name=name, forbidden_field=field):
                    self.assertTrue(list(validator.iter_errors(dict(load(name), **{field: example[field]}))))

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

    def test_inferred_descendant_does_not_encode_owner_approval(self):
        original, proposal = load("explicit.json"), load("inferred.json")
        self.assertEqual(proposal["parent_revision_ids"], [original["revision_id"]])
        self.assertNotEqual(proposal["author_id"], proposal["owner_id"])
        self.assertNotIn("approval", proposal)
        self.assertNotIn("proposal", proposal)

    def test_schema_and_fixture_enums_match(self):
        schema = json.loads((ROOT / "schema.json").read_text())
        self.assertEqual(schema["properties"]["schema_version"]["const"], "0.1")
        self.assertEqual(set(schema["properties"]["status"]["enum"]), {"active", "rejected", "deleted"})
        self.assertEqual(set(schema["properties"]["origin"]["enum"]), {"explicit", "inferred"})
        self.assertEqual(set(schema["required"]), {"schema_version", "preference_id", "revision_id", "parent_revision_ids", "owner_id", "author_id", "status"})


if __name__ == "__main__":
    unittest.main()
