# Ethos

Ethos proposes a common format for carrying a person's preferences between agent tools. Owners can inspect, correct, reject and delete preferences. A learned preference provides context. It does not grant permission to act.

The repository contains a **draft v0.1 specification**, a JSON Schema and example records. It does not yet provide harness adapters, synchronization, identity verification or authorization. Passing schema validation does not establish consent or make a preference effective.

- [Specification and implementation requirements](v0.1/SPEC.md)
- [Revision schema](v0.1/schema.json)
- [Example records](v0.1/fixtures/)
- [Fixture checks](v0.1/test_fixtures.py)

Run the checks from the repository root:

```sh
python3 v0.1/test_fixtures.py -v
```

The JSON Schema check requires the optional `jsonschema` package and reports a skip when it is absent. The remaining fixture checks cover a limited set of record rules. They do not test a complete synchronization or authorization implementation.

An implementation needs authenticated ownership and grants, causal graph validation, conflict and deletion handling, and two real harness adapters before claiming interoperability. Private synchronization and publication require separate consent. The specification records those requirements without selecting a network or identity system.
