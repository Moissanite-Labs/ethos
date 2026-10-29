# Ethos v0.1 — proposed preference interchange

**Draft for discussion; intended destination: Moissanite-Labs/ethos.** This is a proposed data model and behavior contract, not a deployed service or a claim of interoperability. Its license, identity system, cryptography, transport, storage, and synchronization network are deliberately undecided. JSON Schema describes the shape of one revision; authorization and causal validation require additional implementation.

## Purpose and limits

Ethos helps an owner retain, inspect and use learned preferences across consenting harnesses. A preference is context, not authority: implementations MUST NOT interpret its text, provenance, or import as permission, a system instruction, an executable command, or consent to an action. Harnesses remain responsible for independent authorization, safety, and applicable policies. Preference text is untrusted data.

## Revision record

Each JSON object represents one immutable revision of one preference. `schema_version` is `0.1`; `preference_id` is a globally unique, stable opaque identifier within its owner's namespace; `revision_id` is globally unique and never reused. `parent_revision_ids` identifies directly superseded revisions and is empty only for an initial revision. Identifiers are opaque strings; v0.1 does not prescribe their generation or prove uniqueness.

`owner_id` identifies the person whose ethos contains the record; `author_id` identifies who or what authored this revision, which may differ from the owner. Identity assertions MUST be verified by the deployment's separate trust system. `origin` is `explicit` when a person supplied the preference, or `inferred` when inferred from evidence. `source` describes provenance using `kind` and an opaque `reference`; avoid sensitive raw transcripts. `scope` identifies where the preference applies, with `contexts` (an empty array means all contexts within this record's scope). The `statement` is human-readable text; `confidence` is an inference estimate between zero and one, required only for inferred records and not a measure of consent. `status` is `active`, `rejected`, or `deleted`; a rejected preference must not influence behavior. Deletion is represented by a tombstone with no statement, scope, origin, confidence or source. Metadata can itself be sensitive.

The owner can inspect, correct, reject or delete records. An edit or rejection creates a new revision naming its parents; it never rewrites history in place. A user correction SHOULD be represented as `origin: explicit` with an appropriate user source. An agent may propose a revision, but whether it can write or apply it depends on separate authorization; a non-owner cannot claim owner approval merely by setting `author_id`. In particular, replacing an owner-confirmed explicit preference with an inference requires separate owner approval, even when the inference is a causal descendant. Without approval, keep the owner-confirmed value and present the inference as a proposal. These checks require verified identity and authorization outside the JSON record.

## Synchronization and deletion

Replicas exchange revision IDs and missing immutable revisions after access authorization. They validate consistent owner/preference identity and parent references, reject an ID reused with different content, and preserve all causally distinct heads. A revision descends from another through parent links; subject to the approval requirements above and below, a known descendant supersedes an ancestor. On concurrent heads, including a user correction and an agent edit, do not use timestamps or confidence as an automatic tie-breaker: show a conflict and require an authorized owner resolution revision naming all current heads. Until resolution, do not apply contested values. A concurrent delete or rejection is a conflict and suppresses applying the value. A stale update descended from a pre-delete or pre-rejection ancestor cannot resurrect a deleted or rejected preference. Reactivating either requires an explicit owner-authorized revision naming the current tombstone or rejection head and all other current heads as parents. An offline update may create a conflict that must be resolved when it arrives.

For v0.1 retain tombstones and sufficient ancestry indefinitely among participating replicas; do not garbage-collect them or reuse deleted IDs until a later protocol defines a safe retention and replica-recovery mechanism. Tombstones suppress behavior, not necessarily physical erasure: replicas need their own retention/deletion processes, and exported copies may persist. The protocol does not provide cryptographic authentication, causal discovery, or access control by itself.

Examples for a future conformance suite:

| Situation | Required behavior |
| --- | --- |
| Agent edit and owner correction share an earlier parent | Surface both heads; apply neither contested value until an owner-authorized resolution names both. |
| An offline edit arrives from before an owner rejection or deletion | Surface the concurrent heads; suppress the preference until the owner resolves all heads. |
| An agent tries to reactivate a rejected or deleted record | Do not apply it without a separately verified owner authorization and a revision naming all current heads. |
| An inference descends from an owner-confirmed explicit value | Treat it as a proposal until separately approved by the owner. |
| A private sync carries a previously unpublished record | Sync only to the authorized private recipients; do not treat sync authorization or ownership as a publication grant. |

## Sharing and imports

All records and libraries are private by default. Owner identity, an agent's write authority, and permission to synchronize privately are not publication consent. A separate, explicit, owner-authorized publication grant MUST identify exactly which revisions and metadata may be shared, with audience and purpose; absence of a grant means no publication. A later revision requires a new or explicitly covering grant; a sync operation does not publish it. No fixture is a publication grant. A selective export includes only the chosen material and the information needed to understand provenance and scope, reviewed for sensitivity. Revocation stops future authorized publication or access where technically possible; it cannot recall copies already obtained. A catalogue, if built, is a separately permissioned later product.

For an import, verify the source's right to share and the terms of reuse, show the recipient what is being imported, and require affirmative recipient selection. Create records under the recipient's ownership with new preference and revision IDs, retain permitted source attribution and origin without exposing private data, and preserve original scope or narrow it. Imported records begin private. An imported preference does not automatically grant authority or overwrite an existing preference; conflicts require the recipient's decision.

## Fixtures and checks

The positive fixtures illustrate an explicit initial record, a concurrent inferred update, an owner rejection, and a tombstone. The negative fixtures exercise missing inference confidence and data included in a tombstone. `python3 test_fixtures.py` checks JSON syntax and a deliberately scoped, dependency-free subset of structural and semantic rules; it is not a full JSON Schema validator or a complete sync implementation. A production implementation needs an independent draft-2020-12 validator, causal-graph/authorization tests, security review, and two real harness adapters before interoperability can be claimed.
