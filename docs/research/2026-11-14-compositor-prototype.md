# The taste compositor code, with a corrected verification (2026-11-14)

Captured 2026-11-14 from the owner's session with another assistant. The
owner shared Gemini's "Subspace Taste Compositor & Attribution Engine," a
Python reference implementation for the weight-space marketplace track
(package a taste packet, embed a keyed subspace watermark, weave marked
packets, compute Frobenius energy royalties). It targets **Plane 2**, which
the convergence proposal parks. It is preserved here as a reference
prototype, not as MEP code.

## Files

- `prototypes/2026-11-14-taste-compositor.py`: the implementation, verbatim
  apart from a provenance banner. Not imported by `mep/`. Not in the shipped
  package.
- `prototypes/2026-11-14-taste-compositor-fixcheck.py`: a corrected
  verification harness written during capture. Run it from the repo root.
  it locates the prototype by path.

## What was verified on capture

The prototype runs on numpy 2.5.4 (Python 3.14) without modification. Its own
final check prints `K0 Invariance Leakage (should be ~0): 6.93e+00`, which
looks like a failure of the whole method. It is not. The bundled check
computes `||K0 @ composite.delta_w||`, which is not the invariant the
construction builds. The construction projects the **input** side of the
perturbation into the orthogonal complement of the preserved keys, so the
guarantee is `||composite.delta_w @ K0.T||_F ≈ 0`, not `K0 @ dW ≈ 0`.

Measured with the corrected harness:

- woven edit leakage: `3.68e-15` (exact for practical purposes)
- per-creator mint leakage: `2.7e-13` and `2.8e-13`
- bundled (wrong) check, for the record: `6.93e+00`
- royalty shares printed by the demo run: alice 0.7323, bob 0.2677

The null-space machinery is sound exactly as constructed, with one sign
orientation the original author should fix (the final print uses the wrong
product).

## Defects and honesty notes

- **Wrong invariant in the shipped check.** The last line of the verification
  run measures the invariant the construction does not build, and reads as a
  failure. Anyone extending this code should fix that line first.
- **Watermark basis overclaim.** `_derive_carrier_basis` promises carriers
  "strictly inside Null(K₀)" but is called with `np.eye(...)` in
  `mint_taste_packet`. The carrier lives in output space, where K₀ does not
  act. The claim is a docstring, not a fact. Watermark survival through the
  QR re-orthonormalization and through downstream SVD/weave rounds at
  ε=1e-3 is asserted nowhere in the code and would need
  `verify_watermark` to measure; the session defers that piece.
- **Royalty double-counting.** "Exact Frobenius energy attribution" holds
  cleanly only when contributors are mutually orthogonal, which is what the
  cascaded projection was designed to ensure. Under the designed weave the
  attribution is defensible. In general it is a heuristic share that sums
  to 1 by construction of `energies`, not a conservation law. Call it an
  attribution score, not a proof.
- **packet_hash is not portable.** It hashes raw array bytes, so it commits
  to this machine's dtype/layout, not to a cross-platform packet format.
  A `.taste` format would fix dtype, shape and ordering explicitly.
- **No validation or error handling**: mixed packet shapes, empty market
  list, or a watermark carrier of zero norm after projection are all
  unhandled.
- **K₀ semantics.** This instantiation treats a (32,128) random matrix as
  "preserved knowledge keys" and its row space as the subspace to guard.
  AlphaEdit's real construction is over cached keys/covariances of the
  preserved facts. The demo is a toy with the right algebraic skeleton, not
  a reproduction of AlphaEdit's determinism.

## Where this sits

This is Plane 2 tooling, parked behind the tripwires recorded in the
convergence proposal: self-hosted open-weights runtime, load-time
projection by the host, owner-authorized import. None of those exist in a
shipped product today. The two pieces worth salvaging for the buildable
track are the **attribution formula** (royalty shares from importance
weights, directly translatable to "share of approved revisions imported
from each source") and the **lineage list shape** (root hash + shares per
import event), both of which fit the MEP catalogue profile design as
records, no matrices required.

## Verbatim source session

The implementation above is preserved verbatim (banner aside) and was run
as-is on capture. Gemini's closing text, preserved verbatim:

"Key Mechanics in This Implementation

• Cascade Orthogonality (@ P_null @ P_self): When weaving a new creator's
packet onto an existing profile, P_self guarantees the imported style writes
strictly into unallocated dimensions of your personal aesthetic.

• Exact Frobenius Energy Attribution: Because src.V is orthonormal,
projecting the final clamped matrix onto each creator's right-singular
subspace measures the exact surviving variance contributed by that creator,
accounting for any traits clipped, pruned or orthogonalized away.

If you want to keep building out the protocol, the session offered: trait-level
mode slicing with semantic tagging for toggling individual singular modes as
directly addressable royalty-bearing units, and verify_watermark(composite,
creator_public_key) for measuring carrier correlation after downstream
remixing. Neither exists yet."
