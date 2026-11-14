# Cryptographic and geometric provenance in weight space, processed (2026-11-14)

Captured 2026-11-14 from the final session in the AlphaEdit to WSP to
marketplace series. The session proposes how creators of marketplace taste
packets prove authorship, prove safety, and collect proportional royalties.
The owner flagged this as the last round before a step back and an
evaluation. Claims were checked against primary sources on capture. The
verbatim source is preserved beside this file.

## What holds up

- **Weight-space watermarking / model fingerprinting is a real field**
  (model IP protection, black-box and white-box verification). Embedding a
  keyed, near-orthogonal carrier subspace into singular vectors is a
  plausible and honest construction, since random unit vectors in high
  dimensions are near-orthogonal by concentration of measure. Detection by
  cosine correlation with a hypothesis test is standard. What is unverified
  is survival rate of a specific watermark through SLERP, sign-election
  trimming and cascaded null projection. That is an expectation to test,
  not a guarantee.
- **Spectral energy attribution** (project the woven matrix onto each
  contributor's right-singular basis, take Frobenius energy, normalize) is
  mathematically well-defined and is a simple, usable royalty formula.
- **Merkle-DAG lineage** (signed parent hashes plus the exact operators
  applied at each weave step) is standard honest bookkeeping and the
  strongest part of the proposal.
- **Grassmannian chordal distance** between singular subspaces as a
  lineage/overlap detector is a legitimate tool. Evasion rates under small
  noise and the false-positive floor are unknown and would need calibration.

## What is mislabeled or overstated

- **The "zero-knowledge proof of null-space compliance" is not zero-knowledge,
  and does not need to be.** Both quantities (`‖K₀ΔW‖_F ≤ τ`,
  `‖ΔW‖₂ ≤ γ‖W₀‖₂`) are publicly computable linear-algebraic checks on the
  packet itself. Anyone with the packet can verify in milliseconds. No secret
  witness exists. The session's own alternative, a deterministic verifier
  hash against the canonical K₀, is the correct design. ZK machinery only
  buys something when the packet must remain hidden from the verifier,
  which is the opposite of an import you are about to load. ZKML/zkLLM do
  verifiable computation, which is a real field, but no shipped system
  certifies "this delta is null-space-clean for your K₀" end to end.
- **"Exact, tamper-evident" attribution is not exact when contributors
  overlap.** Energy does not decompose cleanly across non-orthogonal
  contributors. Cross-terms double count. The number only becomes honest
  under sequential null-space projection, which is exactly what the marketplace
  weaves enforce, so in the designed pipeline the approximation is defensible.
  Outside that pipeline, `w_i` is a heuristic share, not an invariant.
- **The enforcement gap from before is still present.** A null-space
  certificate only binds anything if the host projects at load time. vLLM
  multi-LoRA loads user adapters today with no projection. The certificate
  is either redundant (project at load and it cannot be violated) or
  decorative (trust the packet and it proves nothing about what the host
  will actually do). The real fix is load-time projection inside the
  inference runtime, which nobody ships today.
- **Model names and product framing** remain the source session's flavor
  and are not adopted.

## The importable idea for the text-space marketplace

The lineage concept transplants cleanly into MEP, where it costs nothing
and does real work:

- **Signed lineage DAG on export bundles.** Every `ethos_export` already
  pins SHA-256 of every artifact. Add a signed DAG recording parents
  (imported profiles) and operators applied at import (selective section
  import, conflict resolutions, attribution of each record). This is a few
  hundred lines on top of the existing bundle, and it gives the catalogue
  profile its micropayment/royalty ledger, its anti-laundering check (match
  against the registry by hash and by document-overlap score), and its
  provenance story for attribution.
- **Deterministic compliance check replaces the ZK claim entirely.** For the
  text marketplace, "this profile is null-space clean" is not needed at all.
  "this profile obeys invariants" is a deterministic check the importing
  host runs against its own invariant-flagged documents. No cryptography
  required.
- **Royalty arithmetic survives translation.** Frobenius energy attribution
  becomes "share of approved revisions originating from each imported
  profile," which is exact, simple, and auditable, because text-space
  attribution has orthogonal, unambiguous units.

## Status

Marketplace weight-space provenance: research, same tripwire as the other
weight-track notes (verifier-gated, projecting runtimes must exist first).
Text-space lineage DAG and royalty ledger: real, buildable, and cheap.
Next step is the evaluation the owner asked for. The weight market is not
blocking it.
