# MEP, the Model Ethos Protocol, v0.1

Ethos is an evolution of context.

Context is what a model is given to work with. Ethos is what you are: what
you keep, what you corrected, what you refuse, what you return to. MEP makes
that a portable, checkable artifact that any harness can read and no harness
owns.

MCP serves context. MEP serves ethos. Same shape, different subject. An MEP
server is an MCP server with a contract about what it exposes and what it
never does.

This document is the contract. `v0.1/SPEC.md` defines the preference record
format. `mep/` is the reference implementation, Python 3.10+, standard
library only, served with `python3 -m mep`.

## Status

Draft v0.1. Implemented and tested in this repository. Not yet a stable
standard; expect changes between 0.1 and 1.0, all dated in `CHANGELOG.md`.

## Principles

1. **Authored, not generated.** The ethos is committed text. The server never
   writes prose on the owner's behalf. Ranking and truncation are
   deterministic, and truncation always says so.
2. **Context, not authority.** Ethos text is input. It grants no permission,
   overrides no policy, and cannot be used as consent. A harness remains
   responsible for authorization, safety and its own rules.
3. **Bounds the owner can see, check and undo.** Everything the server does
   is visible in `ethos_status`. The owner can turn learning off at any time
   and the off switch persists. Every change to the ethos is a revision.
   Undoing a change is a revision.
4. **Capture at the point of learning.** The reflect prompt and the proposal
   flow exist for this: five minutes and a file path beat an hour of
   reconstruction later.
5. **Verify before you trust.** Documents are hash-pinned end to end.
   `SHA256SUMS` covers the tree, exports carry `MANIFEST.sha256`, and a file
   that fails its hash is unverified, never assumed good.
6. **Honest limits, plainly reported.** Heuristics are labeled heuristics.
   Contested preferences apply nothing. A server that cannot verify something
   says so rather than guess.

## What an ethos is made of

### 1. Documents, the corpus model

A directory in the corpus layout: `principles/`, `sops/`, `teams/`,
`skills/`, `docs/`, plus root-level `README.md` and `CHANGELOG.md`. Every
entry is dated, attributed and owned. `CHANGELOG.md` is append-only in
practice: entries are added with a date and a reason, never rewritten.

### 2. Revisions, the v0.1 record model

Preferences are immutable revision records forming a causal graph, defined in
[`v0.1/SPEC.md`](v0.1/SPEC.md). The rules that matter most:

- A revision supersedes its parents. History is never rewritten.
- Rejected and deleted revisions carry no preference payload, only parents.
- Concurrent heads are a conflict. Nothing contested applies until the owner
  resolves them by naming all current heads.
- An inference is a proposal until the owner approves it. Approval is tracked
  outside the record, bound to the exact owner, preference and revision.
- A stale update descended from before a deletion cannot resurrect the
  deleted preference.

MEP adds the local store on top: `.mep/revisions/` (canonical),
`.mep/proposals/` (pending, never applied), `.mep/decided/` (archive of
disposed proposals), `.mep/approvals.json` (the owner's approvals), and
`.mep/learning` (the off switch).

In MEP v0.1, parent revisions always belong to the same preference.
Cross-preference ancestry is reserved.

### 3. Serving, the soko framework

The reference server ports the soko-verified-mcp framework to this job:

- Python standard library only. No dependencies to audit.
- MCP over stdio, both newline-delimited JSON-RPC and Content-Length framed
  messages. Tools return structured content as well as text.
- Path confinement on every file read: no absolute paths, no `..`, nothing
  outside the ethos root.
- Deterministic retrieval: log term-frequency scoring, length-normalised, no
  model, no network, same query, same ranking.
- An integrity manifest (`SHA256SUMS`) checked by `ethos_integrity`.

## The serving surface

### Resources

| URI | Meaning |
| --- | --- |
| `ethos://about` | Server, MEP and schema versions, protocol documents. |
| `ethos://status` | The panel, as JSON. |
| `ethos://revisions` | Effective preference states as JSON. |
| `ethos://document/<path>` | One document, verbatim. |

### Tools

| Tool | What it does |
| --- | --- |
| `ethos_capabilities` | Versions, root, counts, integrity, learning switch. |
| `ethos_list` | Discoverable documents with size, hash and modified time. |
| `ethos_get` | One document, verbatim, hash-pinned. |
| `ethos_query` | Deterministic keyword search, ranked and excerpt-anchored. |
| `ethos_context` | A budgeted bundle for a situation, with sources and omissions listed. |
| `ethos_status` | The panel: loaded, pending, integrity, drift. |
| `ethos_heads` | Causal heads, contested and suppressed preferences. |
| `ethos_history` | The revision graph, optionally for one preference. |
| `ethos_propose` | Write a proposal. Never applies on its own. |
| `ethos_decide` | Owner decision: approve, decline, reject or delete. |
| `ethos_correct` | Owner path: write an explicit revision into the canon. |
| `ethos_export` | Portable bundle with a manifest. Refuses a broken graph. |
| `ethos_integrity` | Verify the tree against `SHA256SUMS`, or rewrite it after review. |

`ethos_propose`, `ethos_decide` and `ethos_correct` are refused with a clear
message while learning is off.

### Prompts

- `reflect`: the three capture questions: what did you learn, decide or
  verify, where does it live now, and who can build on it next.
- `review`: review an artifact against the ethos documents it actually holds.

## The panel and the off switch

`ethos_status` is the panel the reader can check. It names the ethos, says
what is loaded, what is pending, what conflicts, what failed integrity, what
the drift heuristics flag, and whether learning is on or off. It never
changes anything.

The off switch is `.mep/learning` containing the word `off`, or the
environment variable `MEP_LEARNING=off`. While off, every write tool is a
no-op that says so. The owner turns it back on by removing the switch. The
switch is a file, so it persists across restarts and harnesses.

## Condensation, not regeneration

MEP inherits the condensing-prose discipline from Eido: when the reader has
less room, serve less text, never different text.

`ethos_context` takes `depth`:

- `full`, whole documents until the character budget runs out.
- `brief`, headings and lines hitting the query terms only.
- `paths`, provenance only: what exists, with hashes, no prose.

Truncation lands on a line boundary and is marked with
`…(truncated; use ethos_get for the full text)`. The bundle ends with a
`Sources` section pinning every included file by SHA-256 and an `Omitted`
section listing what did not fit. Nothing is summarized by a model, ever.

## Adaptation, bounded

An ethos that never changes is a snapshot. An ethos that changes silently is
surveillance. MEP allows adaptation only inside bounds the owner can see:

- **Corrections.** Every `ethos_correct` is a revision naming all current
  heads. The next `ethos_context` reflects it, and the history shows why.
- **Proposals.** An agent that keeps seeing the owner work a certain way can
  propose; the owner decides in one call.
- **Drift.** `ethos_drift` (surfaced in `ethos_status`) flags pending
  proposals older than two weeks, contested preferences, stale revisions and
  preferences nobody has looked at. These are prompts, not instructions.
- **Budgets.** Callers serve less when there is less room, per the
  condensation contract above.

What adaptation never includes: rewriting a document in place, applying an
unapproved proposal, weakening a rule because it was inconvenient once, or
any change the owner cannot find in `ethos_history`.

## Authority

| Actor | May | May not |
| --- | --- | --- |
| Harness | Read, query, serve, export on request | Approve a proposal. Write history |
| Agent | Propose revisions and flag drift | Apply its own proposals. Approve anything |
| Owner | Correct, approve, decline, reject, delete, export, publish | Retroactively rewrite a revision (record a new one) |

The owner's actions travel through `ethos_correct` and `ethos_decide`. `ethos_decide`
has four outcomes with distinct semantics: `approve` makes a proposal canonical,
`decline` archives it with no effect, `reject` writes a rejected revision naming
all current heads so the preference is suppressed until a later correction
reactivates it, and `delete` writes a tombstone with the same effect. Both tools
write records. Neither edits records. The harness should confirm with the human
before calling either, the same as any irreversible tool.

## Export and sharing

`ethos_export` writes a portable bundle: `documents/`, `revisions/`,
`proposals/`, `approvals.json` (flagged as a local trust artifact, not part
of the wire format), `EXPORT.md` and `MANIFEST.sha256`. The export refuses to
run on a broken graph.

An export is private by default. Copying it anywhere is the owner's explicit
act. Publication requires a separate, explicit grant that names the revisions,
the audience and the purpose. Absence of a grant means no publication. The
sync rules in [`v0.1/SPEC.md`](v0.1/SPEC.md) cover what replicas must and
must not do. MEP v0.1 implements records and the local store only. There is
no network synchronization in this version.

## Conformance

An implementation conforms to MEP v0.1 when it:

- serves the tools and resources above, or an explicit superset, and reports
  itself via `ethos_capabilities`;
- rejects records that fail structural validation, and refuses to serve a
  graph with a cycle, a duplicate revision id, an unknown parent, or
  inconsistent owners;
- never applies a proposal without the owner's decision bound to the exact
  revision;
- applies nothing from a contested preference, and suppresses rejected or
  deleted preferences;
- honors the learning off switch on every write path;
- verifies `SHA256SUMS` on demand, and says plainly when no manifest exists.

The fixture contract checks (`v0.1/test_fixtures.py`) and the test suite
(`tests/`) define the current expectation in code.

## Failure behaviour

Missing files, broken JSON and hash mismatches produce explicit errors. There
is no silent fallback that quietly serves the wrong document, degrades a rank
to random order, or treats an unverified file as verified. A harness calling
this server can trust that silence means "no data", never "no problem".

## Credit

Apache-2.0; see LICENSE.

- Framework and integrity design: [ahrazzle/soko](https://github.com/ahrazzle/soko)
- Bounded-change and reading-response philosophy: [Moissanite-Labs/weft-eido](https://github.com/Moissanite-Labs/weft-eido)
- Content model and governance: the Aska Digital corpus
- Preference records: Ethos v0.1 (`v0.1/SPEC.md`)
