# Ethos: the convergence (a proposal)

*opn-eve proposed ethos. 2026-11-14.*

**Status.** Proposal. Not implemented. This is the synthesis of the four
research sessions captured in `docs/research/` (MCP deep-dive, W-MCP sketch,
AlphaEdit and SC-WSP, taste-marketplace and its provenance follow-up) and the
work merged into `main` through PRs #7 to #12. It is meant to be read next to
`MEP.md`, not instead of it.

Here is the shape everything keeps pointing at, once you lay the four sessions
side by side. Call it **one source of truth, many compiled projections**.

## The recurring pattern

Every session this week, the winning design moved authority into inspectable,
deterministic, revocable space. The loser moved it somewhere opaque.

- MCP's own trajectory is this (stateless, self-describing, extensions).
- MEP v0.1 already is this (proposals need approval, tombstones suppress,
  preferences are context not authority).
- W-MCP failed this (capability the host can't inspect).
- AlphaEdit succeeds at exactly this, inside one model (K₀ projection equals
  provably zero effect where you were not allowed to act).
- The provenance sessions solve only this (watermarks and lineage DAGs exist
  so attribution is checkable, not asserted).

The convergence is not "merge MEP with weight-space." It is take the
principle that made each of those designs correct and apply it to the whole
stack.

## The architecture: two planes, one compiler

**Plane 1, the Legible Plane. Authoritative, auditable, text-first. This is
MEP.** Every artifact a machine reads on the owner's behalf lives here:
principles, preferences, histories, invariant documents, lineage DAGs,
catalogue listings. Hash-pinned end to end. Contested heads apply nothing.
The only plane where authority may exist. This is the built thing, and it is
~80% of the total value.

**Plane 2, the Compiled Plane. Optional, owner's explicit act, always a
cache, never a record.** Projections of Plane 1 into faster machinery on the
owner's authorized runtimes. The critical move is compile, don't edit:

- Plane 2 artifacts are produced by deterministic compilers from Plane 1
  inputs, not by an LLM editing weights. A fixed pipeline: ingest ethos
  documents, embed, contrast against neutral baseline, null-space project
  onto Plane 1 invariants' embeddings, spectral clamp, quantize, sign.
- Inspectable compilation means the buyer or loader verifies by re-running
  the compiler on the published inputs and comparing output hashes,
  demolishing the zero-knowledge versus deterministic distinction from the
  provenance session. Re-derivation is the proof. This only works because
  the compiler is public and boring by design.
- Revocable artifacts. Plane 2 packets are derived from Plane 1, invalidated
  when Plane 1 revises, deleted with the profile.
- Family-bound by construction. The gauge problem is dodged, not solved.
  Deltas carry the checkpoint-family identifier. Plane 1 stays
  model-agnostic forever.

The one rule that selects between any two implementations: is this effect
visible, attributable and revocable by the owner in bounded time? Plane 1
always answers yes. Plane 2 answers yes only through the compiler and the
gate. Anything failing the test is exiled.

## The layers, with what each exploration built

| Layer | Component | Origin | Status |
| --- | --- | --- | --- |
| 0 Wire | MCP + `gg.moissanite/ethos` extension (SEP-2133) | MCP deep-dive | designed, not shipped |
| 1 Records | v0.1 revisions, invariant documents, lineage DAG, royalty shares | AlphaEdit capture, provenance session | lineage DAG designed. Invariants proposed. Rest built |
| 2 Proofs | Lean 4 graph invariants (contested implies nothing, tombstone suppresses, proposal never applies) | verified-server session and MEP | planned (A3) |
| 3 Serving | mep server: tools, resources, prompts, panel, off switch | soko framework | built, tested |
| 4 Compilation | ethos to bundle (shipped), ethos to steering vector (first real Plane 2 milestone), ethos to delta (research) | taste marketplace capture, SC-WSP | bundle only |
| 5 Catalogue | selectively-importable profiles, attribution ledger, royalties | marketplace sessions | design needed. SPEC has always reserved it for a later product |
| 6 Sync | git-as-sync now, hosted HTTP+OAuth later, SEP core eventually | B6, MCP governance | agreed |

What the build history looks like across sessions: three of the four
explorations produce Plane 5 inputs (catalogue spec, provenance schemas,
compiler prototypes) and one hard constraint (no opaque authority). The
marketplace sessions were not a detour. They were the Plane 5 spec arriving
ahead of the Plane 1 catalogue it rides on.

## Hard vetoes (these are the non-negotiable convergence rules)

1. **No opaque deltas, ever.** Any weight-space artifact must be
   re-derivable from published Plane 1 inputs via the public compiler. If
   provenance requires mathematics only the publisher can run, it is not
   provenance. It is trust in a stranger.
2. **No auto-resolution of contested heads,** in any layer, by any merge
   policy, including royalty-weighted ones. Conflicts go to the owner. MEP
   learned this from the spec. The marketplace adopts it verbatim.
3. **No closed-weight injection.** Plane 2 exists only where the runtime can
   (a) execute with projection-enforced loading, (b) be turned off,
   (c) be audited. Today that means self-hosted open-weights, owner's
   machine.
4. **No SEP before strangers exercise the extension.** Tasks teaches the
   timeline; patience is the price of a stable core.
5. **Plane 1 is the only place a person lives.** Models, markets, agents,
   benchmarks, all are guests.

## Honest sequence from here

1. **Lineage DAG and attribution ledger** on the existing export format.
   Days. Unlocks the catalogue design without touching weights.
2. **Invariant documents and blast-radius parameters** in `ethos.json`. A
   week. The A2 enforcement axis in its final, minimal form.
3. **SEP-2133 extension** (`gg.moissanite/ethos`). Two days of spec text and
   negotiation tests. MEP becomes an ecosystem citizen.
4. **Verified core model in Lean 4**, differential-tested against
   `mep/revisions.py`. Weeks, compounding trust forever.
5. **Catalogue profile design note** (Plane 5). The marketplace that ships,
   text-space, gated at every import.
6. Then, and only then, a steering-vector compiler (Plane 2's first, tamest
   milestone) on a specific open-weights checkpoint family, on the owner's
   machine, off by default.

The convergence in one sentence: MEP is the court, the compiler is the clerk,
the model is trial. Everything the four sessions explored is one of those
three things wearing different clothes, and the architecture's only hard job
is making sure none of them ever trade places.
