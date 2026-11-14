# MCP deep-dive, processed (2026-11-14)

The owner exported a conversation from another assistant and asked for it to
be captured. The raw export is preserved verbatim in
[2026-11-14-mcp-session-raw.md](2026-11-14-mcp-session-raw.md). This file is
the processed version: what the session covered, what we verified, and what
it means for MEP. The full W-MCP design that came out of the same exchange is
preserved in [2026-11-14-w-mcp-sketch.md](2026-11-14-w-mcp-sketch.md).

## Provenance

The session was a Q&A across eleven turns covering MCP architecture,
versioning, context overhead, governance, fork strategy, compatibility
invariants, formal verification and the move to weight space. The assistant's
diagrams were embedded SVG/Timeline markup. Claims were checked against
primary sources on 2026-11-14 unless marked otherwise below.

## What the session got right, verified

- **MCP is now stateless.** The 2026-07-28 spec removed the handshake. Every
  request carries its protocol version and client info in `_meta`;
  `server/discover` is optional, and responses carry `ttlMs` and
  `cacheScope` so clients can reuse capability metadata. Verified against the
  published 2026-07-28 spec materials.
- **Governance runs through SEPs.** Major changes go through Specification
  Enhancement Proposals in the modelcontextprotocol repository: a Working
  Group discussion, a sponsor, a PR with a reference implementation, and
  conformance tests before a SEP is marked Final. Verified via
  modelcontextprotocol.io/seps and the repository process.
- **Tasks is the precedent for a slow feature done right.** SEP-1686
  proposed durable call-now-fetch-later execution in October 2025. It shipped
  experimental in the 2025-11-25 spec, was refactored into the Tasks
  extension (SEP-2663), and reached general availability in the 2026-07-28
  spec. Verified against the 2026-07-28 spec and the Tasks rollout posts.
- **Extensions are vendor-namespaced.** SEP-2133 defines
  `{vendor-prefix}/{name}` extension identifiers negotiated in capabilities
  and `_meta`. Standard hosts ignore unknown extensions. Extension-aware
  hosts opt in. Verified against SEP-2133 and the extensions overview.
- **Tools list is the context-window cost.** A connected server's tool names,
  descriptions and schemas are injected by the host at conversation start, so
  catalog size is the token lever, along with tool results and loaded
  resources. The host's mitigations are progressive discovery
  (`search_tools`-style), dynamic connect and disconnect, and programmatic
  tool calling. Verified against the client best-practices documentation.
- **Fork versus invariant.** Third-party hosts expect the wire contract:
  framing, `server/discover`, `_meta` negotiation, standard `tools/*`
  shapes. Everything inside the server, the host prompt-assembly side, and
  vendor extensions is an independent variable. Verified against the
  architecture and transport docs.
- **Lean 4 + a thin TCB is a real architecture for verified servers.** The
  session's advice to keep the OS/transport shim as the only trusted base and
  prove parse/round-trip, authorization gating and handler totality in a
  proof assistant matches how verifiable systems are structured and matches
  our own soko lineage. Not verified in code here yet. It is a direction,
  not a result.

## What the session got mostly right, with caveats

- **SEP numbering details** (e.g. "SEP-932" for governance, "SEP-2663" for
  Tasks extensions) are plausible and consistent with the sources checked,
  but do not quote them in normative text without re-checking each link.
- **SEP-2133 as an adoption path for MEP semantics** is sound as a strategy:
  ship an extension namespace, keep standard hosts working, let aware hosts
  opt in. It is not a shortcut around SEP review if we ever want the
  semantics in core.
- **Formally verified MEP core** targets the right properties: tombstones
  suppress, contested preferences apply nothing, proposals never apply,
  archived records neither apply nor shadow the base preference. Those are
  pure functions of the revision graph, so they are amenable to proof. The
  hard part is proving the Python reference against the model, which needs
  either extraction, a differential oracle, or rewriting the core in the
  proof assistant.

## Unverified or speculative

- The weight-space claims in the W-MCP sketch. The two core papers exist.
  The portable cross-family wire does not, and the gauge problem is
  explicitly unsolved. See the sketch document for the exact split.
- "GPT-6 Astra" as the editing model in the source material. We did not
  verify vendor claims; nothing here depends on them.
- Specific benchmark figures (7.9% to 48.1% MATH-500 and 8.35% to 37.80%).
  Treat as the source authors' results, not as MEP facts.

## What this means for MEP

1. **Ship as an extension before proposing core.** MEP can ship today as
   `io.moissanite/ethos` (or `gg.moissanite/ethos`, owner's call on the
   vendor prefix), negotiated via SEP-2133, with everything else unchanged.
   That is the lowest-risk way to make MEP a real ecosystem participant
   instead of a private contract.
2. **Keep the wire invariants untouched.** No new methods, no message
   reshaping. MEP adds vendor-namespaced capabilities and standard
   primitives only. That preserves Inspector, SDKs, hosts and every future
   client.
3. **Context economy is part of the design.** Our `depth: full|brief|paths`
   and `budget_chars` already follow the condensation discipline. If the
   ethos catalog ever grows large for agents, the same progressive-discovery
   pattern applies: a thin `search` tool in front of the full catalog.
4. **Deterministic caching is nearly free.** `ethos_list` responses can carry
   `ttlMs` and `cacheScope` once the server serves over Streamable HTTP, and
   the revision heads make the natural cache key.
5. **The verified-core track is real.** Tombstone-suppression and
   contested-applies-nothing are the kind of small, total, pure properties a
   Lean 4 model can prove. The Python implementation then gets differential
   testing against the model. That is soko practice, not new theory.
6. **The leverage is enforcement, not description.** Adding a
   `check_against_ethos` style deterministic gate turns ethos from "advice
   the model may ignore" into "constraints the host can enforce". The design
   question is what the gate covers: some ethos rules are mechanical
   (no secrets in artifacts), most are not (taste). The gate should be
   honest about which is which.

## Open questions for the owner

- Vendor prefix for the extension identity: `io.moissanite/ethos`,
  `gg.moissanite/ethos`, or `app.moissanite/ethos`?
- Do we want an SEP draft once the extension exists, or keep MEP as a
  community profile indefinitely?
- If the verified-core track starts, Lean 4 model plus differential testing,
  or a full rewrite of `mep/revisions.py` in Lean 4?
