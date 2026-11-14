# Changelog

Dated record of every change to this repository and its reason. Newest first.

## 2026-11-14: Ethos convergence proposal (opn-eve)

Added `docs/proposal/2026-11-14-ethos-convergence.md`, a synthesis of the
MCP deep-dive, W-MCP, AlphaEdit and marketplace sessions into one
architecture: two planes (legible Plane 1, compiled Plane 2) and one
compiler. It proposes a lineage DAG on exports, invariant documents, the
SEP-2133 extension, a Lean 4 verified core, and a text-space catalogue
profile. Proposal, not implemented. Reason: the sessions individually
converge on this shape. It should be on the record as one proposal rather
than four captures.

## 2026-11-14: Capture the marketplace provenance session as research

Added `docs/research/2026-11-14-marketplace-provenance.md` with the verbatim
source beside it. The session proposes cryptographic and geometric
provenance for weight-space taste packets. Watermarking and spectral
attribution are real techniques. The zero-knowledge claim is mislabeled
(deterministic check suffices) and enforceability still requires host-side
projection at load time, which nobody ships. The importable idea is a
signed lineage DAG plus a royalty ledger on ethos export bundles. No protocol
changes.

## 2026-11-14: Capture the taste-marketplace session as research

Added `docs/research/2026-11-14-taste-marketplace.md` with the verbatim
source beside it. The session maps a subjective taste profile to a
low-rank null-space-projected weight packet, then extends it to a
multi-profile marketplace algebra. Every cited method exists (Bradley-Terry,
contrastive steering, TIES-merging, SLERP). The synthesis does not, and the
weight-space variant trades MEP's one non-negotiable (a gate the host can
inspect) for a capability it cannot audit. The buildable marketplace is a
MEP catalogue profile in text space. No protocol changes.

## 2026-11-14: Capture AlphaEdit and the SC-WSP proposal as research

Added `docs/research/2026-11-14-alphaedit-and-scwsp.md` with the verbatim
source beside it. AlphaEdit is real and checks out (ICLR 2025 Oral,
Outstanding Paper, arXiv:2410.02355). SC-WSP is a design hypothesis, not a
published method. Reason: these ideas sharpen the enforcement axis (A2) as a
proposal for invariant-flagged documents, and they give better vocabulary to
the verified-core track (A3). No protocol changes.

## 2026-11-14: Capture the MCP deep-dive session as research

Added `docs/research/`: the processed notes from a conversation the owner
captured from another assistant, the verbatim export, and the W-MCP sketch it
produced. No protocol changes. Reason: the session's conclusions about MCP
governance (SEPs, extensions, Tasks) and verified servers are inputs to the
MEP roadmap, and capture at the point of learning is cheaper than
reconstruction. Claims were spot-checked against primary sources on capture.
The notes record what held and what did not.

## 2026-11-13: MEP v0.1, the Model Ethos Protocol and reference server

Added MEP.md, the forkable `template/`, and `mep/`, a stdlib-only Python MCP
server implementing the serving surface (resources, tools, prompts, the
panel and the off switch). Preference records remain governed by `v0.1/`.
Reason: ethos is useful as a protocol, not only as a library. Serving it over
MCP makes any harness able to read an owner's ethos with no bespoke
integration, and the bounded-change philosophy needs a concrete surface to
live on. Built from the soko framework (AHRAZZLE/soko) for integrity and
confinement, and the weft-eido philosophy for condensation, bounded
adaptation and the off switch.

## 2026-11-13: Apache-2.0

Added LICENSE, NOTICE, CONTRIBUTING.md and SECURITY.md. Reason: the protocol
and server are meant to be built on by anyone. They need a license a
stranger can rely on.

## 2026-10-29: Ethos v0.1 merged (spec, schema, fixtures)

Initial proposal merged as v0.1 with conformance fixtures and schema tests.
Reason: preferences need an immutable, checkable record before any serving
layer can be trusted.
