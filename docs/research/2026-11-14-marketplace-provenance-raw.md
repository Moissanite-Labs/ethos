> Provenance. Captured 2026-11-14, preserved as shared, extracted to text from
> the owner's session with another assistant. Third-party output, unedited.
> It does not pass this repository's prose check, by construction. See
> [2026-11-14-marketplace-provenance.md](2026-11-14-marketplace-provenance.md)
> for the verification.

---

For a marketplace where users slice, weave, and remix pieces of each other's taste profiles, Cryptographic and Geometric Provenance in Weight Space solves a core economic and epistemic problem: how to prove who contributed what when matrices are added, orthogonalized, and SLERP-blended.

Because taste packets live as low-rank null-space perturbations (ΔW = U Σ Vᵀ ∈ Null(K₀)), provenance can be embedded directly into the geometry of the singular vectors and paired with zero-knowledge / cryptographic commitments.

1. Subspace Watermarking (Geometric Attribution)

When a creator publishes a taste packet ΔW_A = Σ_{k=1..r} σ_k u_k v_kᵀ, each rank-1 mode (u_k, v_k) occupies a specific 1D line in a high-dimensional space. In high-dimensional geometry, random unit vectors are nearly orthogonal. You can embed an invisible, mathematically verifiable signature directly into the weight update:
• Keyed Pseudo-Random Subspace Anchors: Using the creator's cryptographic public key pk_A and a seed, generate a secret orthonormal set of high-frequency "carrier" directions C_A ∈ R^{d×m} inside Null(K₀).
• Perturbation Embedding: Mix a tiny, imperceptible amplitude ε (e.g., ε ≈ 1e-3 σ_k) of the creator's carrier vector c_{A,k} into their published singular vector: ũ_k = (u_k + ε c_{A,k}) / ‖u_k + ε c_{A,k}‖₂.
• Why It Survives Remixing: Even if a downstream buyer takes only 20% of Creator A's profile, applies SLERP blending with Creator B, and projects it through P_self, the inner product ⟨ΔW_composite v_k, c_{A,k}⟩ remains statistically significant (detectable via a simple hypothesis test / cosine correlation threshold) as long as any non-trivial energy from Creator A's subspace remains active.

2. Spectral Royalties (Proportional Attribution Algebra)

At merge time, attribution is proportional to how much of a creator's taste survived the weave. For each creator i, project the final woven matrix onto creator i's original orthonormal right-singular basis V_i:
  E_i = ‖ΔW_comp V_i‖_F²
Then normalize: w_i = E_i / Σ_j E_j. This yields an exact, tamper-evident metric for micropayments, creator reputation, or lineage graphs, automatically discounting creators whose traits were stripped out via concept erasure or zeroed out during sign-consensus trimming.

3. Cryptographic Lineage & ZK-Proofs of Well-Formedness

Two trust failures: poisoning (a malicious packet secretly breaks safety or core logic) and laundering (re-packaging someone else's taste packet as your own).
• Proof of Null-Space Compliance (Zero-Knowledge / Verifiable Check):
Before a .taste packet is listed, the publisher attaches a lightweight cryptographic proof (or deterministic verifier hash against the standard K₀ basis) proving ‖K₀ ΔW‖_F ≤ τ and ‖ΔW‖₂ ≤ γ ‖W₀‖₂. Buyers can verify in milliseconds, without running a single forward pass.
• Merkle-DAG Lineage Trees:
Every woven .taste file carries a signed Merkle Directed Acyclic Graph (DAG) header recording the parent packet hashes, the exact linear operators applied (e.g., SLERP(t=0.35), ProjectNull(V_self), SliceMode([0, 2])), and the resulting spectral attribution weights w_i.
• Anti-Laundering Detection:
If a bad actor tries to strip metadata and re-upload someone else's packet with minor noise, the marketplace indexer runs a Grassmannian chordal distance check between the new submission's singular subspaces (U_new, V_new) and existing registry entries. High subspace overlap flags derivative lineage automatically.

End-to-End .taste Packet Structure

| Layer | Contents | Verification Mechanism |
| Payload | Quantized low-rank factors (U, Σ, V) + carrier watermark ε C_A | Reconstructs ΔW ∈ Null(K₀) |
| Semantic Index | Human-readable labels per singular mode k (e.g., mode_0: "austere geometry") | Enables selective trait toggling |
| Safety Certificate | Commitment hash against canonical K₀ & spectral norm bound γ | Guarantees zero core model degradation |
| Lineage Header | Signed Merkle-DAG of parent hashes + Frobenius energy shares w_i | Enforces verifiable attribution & royalties |

The session ended with canned follow-ups: implementation code, security edge cases, or the deep dives on watermarking math, ZK mechanics and royalty attribution; the owner indicated this was the last round before stepping back to evaluate.
