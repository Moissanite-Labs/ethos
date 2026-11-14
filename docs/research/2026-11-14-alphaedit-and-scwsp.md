# AlphaEdit and the SC-WSP proposal, processed (2026-11-14)

Captured 2026-11-14 from a session the owner shared that compared
AlphaEdit with Weight-Space Programming (WSP) and sketched a hybrid called
Subspace-Constrained Weight-Space Programming (SC-WSP). Claims were
spot-checked against primary sources on the day of capture. What follows is
the verified core, the unverified parts, and what the ideas mean for MEP.
The verbatim export is preserved alongside the earlier MCP session notes.

## What AlphaEdit actually is

- Paper: Fang, Jiang, Wang, Ma, Shi, Wang, Chua and colleagues,
  "AlphaEdit: Null-Space Constrained Knowledge Editing for Language Models",
  arXiv:2410.02355. ICLR 2025 Oral, awarded ICLR 2025 Outstanding Paper.
  Verified against arXiv, OpenReview and the official repository
  (jianghoucheng/alphaedit).
- Mechanism: edits that would perturb preserved knowledge are projected into
  the null space of the preserved-knowledge key matrices before being applied:
  Δ_safe = Δ_raw (I − K₀ K₀⁺). Outputs about preserved knowledge are provably
  unchanged.
- Effect: boosts locate-then-edit methods by about 36.7% on average, mostly
  on knowledge-editing benchmarks (counterfact and similar), with a single
  line of projection code. Tested on LLaMA3, GPT2-XL and GPT-J.
- Scope: declarative key-value knowledge in MLP layers. It does not fix
  broken reasoning procedures, RL policies, or circuit-level algorithmic
  faults. Sequential edits are its strength.

## What the session claimed beyond the paper

- "Average of around 36% with minimal extra code" is accurate, on editing
  benchmarks, not on general capability.
- "ICLR 2025 Outstanding Paper" is accurate.
- The Null-space formulation and the projection equation are faithful.
- The comparison table against WSP is a fair, common framing: AlphaEdit is
  constrained closed-form editing. WSP is agentic read-diagnose-write with a
  code execution sandbox and no invariance guarantee.
- SC-WSP (apply WSP freely, project through the AlphaEdit guardrail, bound
  the spectral norm, feed the projection residual back to the editing agent)
  is a coherent proposal, not a published method. It has no benchmark, no
  implementation in the source material, and the thresholds it quotes
  (e.g. `norm(K0 @ delta) < 1e-5`) are the author's numbers, not verified
  constants. Treat as a design hypothesis.
- Model names in the session ("GPT-6 Astra", "Claude Opus 5.5") and the
  "50 forward passes" worked example are flavor from the source session,
  not MEP facts.

## The K₀ framing, moved into text space

AlphaEdit's constraint is worth naming precisely because it generalizes:

  The change may be arbitrary. It may not have any component inside the
  subspace that must not change. K₀ is whatever the owner of the artifact
  refuses to disturb. The projector strips anything else.

MEP already implements this in document space, without the metaphor:

- The tombstone and approvals ledger are K₀. An unapproved inference has
  zero component in that subspace and applies nothing.
- `ethos_correct` writes into the subspace explicitly and visibly.
- The candidate half of `check_against_ethos` is the projector: deterministic,
  in-process, total.

The gap: MEP does not yet name which *documents* are protected. An ethos can
carry rules nobody can enforce mechanically, and some rules should never be
advisory:

- **Invariant-flagged documents.** A document (or section) marked `invariant`
  carries obligations MEP enforces mechanically: no inferred preference may
  contradict it, `check_against_ethos` must flag violations as errors, and
  nothing in `.mep/proposals/` may be approved when it negates an invariant.
  Security principles, the tombstone set, the approvals ledger, and anything
  the owner marks explicitly. This is the text-space transposition of
  canonical capability K₀: the projector is the deterministic checker, not a
  null-space matrix.
- **Spectral bound analog.** Not a norm on weights, but a blast-radius bound
  on changes: a proposal touching N documents or scopes larger than a
  configured size is routed to the owner rather than the approval fast path.
- **Residual feedback analog.** If a projection would neuter an inferred
  preference (because it lives entirely inside the invariant subspace), the
  proposer receives that as structured feedback instead of a silent drop.

All three are proposals, not shipped behavior. They fit the existing
architecture: `check_against_ethos` gating on invariants is Track A work;
bounded blast radius and residual feedback are policy parameters in
`ethos.json`.

## Where this sits in the MEP map

- It does not touch Track A items 1, 3, 4 or any Track B work. Those are the
  production path.
- It sharpens Track A item 2 (enforcement) from "adds a check tool" to "adds
  invariant-flagged documents and an honest gate". That is the concrete,
  MEP-native form of the idea in this session worth stealing.
- It validates Track A item 3 (verified core) in better language: the graph
  invariants are the protected K₀ every revision must respect, and the
  verified-core track proves exactly that with no hand-waving.
- The weight-space track (SC-WSP, W-MCP) remains research, not roadmap. It
  reopens when self-hosted open-weights inference with editing access exists
  in our stack, which it does not today. Closed-weight APIs cannot do any of
  this.

## Standing honesty notes

- The session implies AlphaEdit is drop-in for any edit. In practice the
  calibration covariance (K₀) construction and layer selection matter, and
  misuse editing constraints can silently do nothing to the bug you are
  trying to fix.
- SC-WSP's "formally bounded" claim inherits AlphaEdit's linear-algebraic
  guarantee, which is with respect to cached key representations, not
  perfect behavioral preservation. It is a bound, not a proof of goodness.
- Nothing here establishes that any ethos can be usefully compiled into
  weights. The cross-family gauge problem documented in the W-MCP notes
  still rules out a portable wire.
