# Changelog

Dated record of every change to this repository and its reason. Newest first.

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
