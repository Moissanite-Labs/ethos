> Provenance. Captured 2026-11-14, preserved as shared, extracted to text from
> the owner's session with another assistant. Third-party output, unedited.
> It does not pass this repository's prose check, by construction. See
> [2026-11-14-taste-marketplace.md](2026-11-14-taste-marketplace.md) for the
> verification and the mapping to MEP.

---

To turn a subjective taste profile (preferences over flavor, style, aesthetics, or tone) into parameters that can be transmitted and injected via Subspace-Constrained Weight-Space Programming (SC-WSP), you have to transform sparse human feedback into a low-rank orthogonal weight perturbation (Δ_safe). This pipeline converts preference data into executable neural geometry through five core mathematical transformations:

1. Preference Quantification (Bradley-Terry / Pairwise Logits)

Raw taste is qualitative ("I prefer crisp, minimalist prose over ornate metaphors" or "I like smoky, acidic flavors over sweet ones"). First, map choices onto a continuous latent utility space.
• Transformation: Given pairwise preference comparisons y_i ≻ y_j, model the latent reward r_θ(x) using the Bradley-Terry-Luce (BTL) probabilistic model:
  P(y_i ≻ y_j) = σ(r_θ(y_i) − r_θ(y_j))
• Output: A scalar reward signal or ranked preference dataset D_taste = {(x, y+, y−)}.

2. Contrastive Activation Extraction (Mean-Difference / PCA)

Neural networks represent aesthetic and stylistic concepts as linear directions in activation space (the Linear Representation Hypothesis). Instead of sending raw text examples, extract the geometric direction of the taste profile inside the target model's hidden layers.
• Transformation: Pass positive (y+) and negative (y−) taste exemplars through the model and harvest hidden states h_l ∈ R^d at layer l. Compute the contrastive steering vector v_taste (or take the top k principal components via SVD of the activation differences):
  v_taste = (1/N) Σ_{i=1..N} (h_l(y_i+) − h_l(y_i−))
• Output: A dense semantic direction vector v_taste ∈ R^d capturing the essence of the preference.

3. Weight-Space Lifting (Outer-Product / Rank-r Synthesis)

To make the taste profile permanently part of the network's weights—and transmissible as compact model parameters rather than a prompt—lift the activation vector into a matrix perturbation ΔW ∈ R^{d_out × d_in}.
• Transformation: Use a rank-1 outer product (similar to ROME/AlphaEdit key-value updates) or a low-rank adapter decomposition (LoRA-style AB^T) driven by a single step of Direct Preference Optimization (DPO) gradient:
  ΔW_raw = α v_taste k_trigger^T  or  ΔW_raw = UΣV^T  (truncated to rank r ≪ d)
  where k_trigger is the input key representation of contexts where the taste applies.
• Output: A compact, low-rank tensor ΔW_raw (represented by just two thin matrices U and V for ultra-lightweight transmission).

4. Null-Space Projection (The AlphaEdit Guardrail)

A raw taste perturbation will almost certainly bleed into general reasoning, factual recall, or syntax. Before the taste parameters are applied or transmitted, project them onto the null space of core cognitive capabilities (K₀).
• Transformation: Multiply the candidate taste matrix by the orthogonal projector P = I − K₀ K₀⁺:
  ΔW_safe = ΔW_raw · P
• Output: An invariant taste tensor where K₀ ΔW_safe = 0. The model's factual knowledge and logical reasoning remain mathematically untouched while its stylistic/aesthetic output shifts.

5. Spectral Normalization & Quantization (Transmission Packet)

To ensure the taste profile can be safely composed with other users' profiles or future edits, normalize its singular values and compress it for communication.
• Transformation: Scale ΔW_safe so its spectral norm stays within a safe ratio γ of the base layer W₀, then quantize the factorized matrices (U', V') to 8-bit or 4-bit integers:
  ΔW_final = min(1, γ‖W₀‖₂ / ‖ΔW_safe‖₂) · ΔW_safe
• Output: A lightweight, portable statistical payload (often just a few kilobytes) that another node or model can load directly into its weights to immediately adopt the taste profile.

Summary Flow

Stage | Mathematical Object | Size | Purpose
1. Raw Taste | Pairwise Preferences (y+ ≻ y−) | Discrete text/choices | Captures human aesthetic signal
2. Latent Direction | Contrastive Vector v_taste | R^d (e.g., 4,096 floats) | Isolates taste in representation space
3. Weight Lift | Low-Rank Factors (U, V) | R^{d×r} (e.g., r=4) | Converts activation shift into weight update
4. Subspace Lock | Projected Matrix ΔW_safe | Null(K₀) | Guarantees zero damage to core capabilities
5. Packetization | Spectral-Clamped (U', V') | ~16–64 KB | Enables safe, pure-parameter transmission

Then the owner asked about packaging profiles into a marketplace where people weave the parts of others' they like into their own. The assistant responded with Subspace-Constrained Multi-Profile Algebra:

1. Orthogonal Disentanglement (Extracting "Parts" of Someone's Taste)

Singular Mode Decomposition: Factorize the incoming packet via SVD: ΔW_A = Σ σ_k u_k v_k^T. Each rank-1 component represents an independent, orthogonal principal axis of User A's taste. Users preview and toggle individual modes k rather than importing the entire profile.
Concept Erasure (Subspace Rejection): If a user wants everything except a component in V_reject, project it out: ΔW_{A\reject} = ΔW_A (I − V_reject V_reject^T).

2. Conflict-Free Weaving (TIES-Merging + Null-Space Alignment)

Step A: Sign-Consensus Trimming (TIES-Style): Trim low-magnitude noise, elect the dominant sign coordinate-wise weighted by your priority weight α: γ = sgn((1−α)ΔW_self + α ΔW_market). Average only the parameters that align with the elected sign.
Step B: Sequential Null-Space Locking: Treat your current taste profile ΔW_self as preserved knowledge. Build Personal Invariance Projector P_self = I − V_self V_self^T. Project the marketplace profile through both projectors: ΔW_woven = ΔW_self + β (ΔW_market P₀ P_self). Result: the imported taste writes only into the orthogonal complement of your existing aesthetic.

3. Smooth Taste Interpolation (Geodesic / SLERP Blending)

u_blend(t) = [sin((1−t)Ω)/sin Ω] u_self + [sin(tΩ)/sin Ω] u_market, where Ω = arccos(u_selfᵀ u_market). Preserves the sharpness of the profile across every slider position t ∈ [0, 1].

Summary of Marketplace Operations

Marketplace Action | Mathematical Operation | Effect
Sample a Trait | Rank-1 SVD Slice (σ_k u_k v_k^T) | Imports a single isolated aesthetic axis
Filter Out a Vibe | Subspace Rejection (ΔW (I − V_bad V_bad^T)) | Strips unwanted stylistic tendencies
Expand Taste Safely | Cascaded Null Projection (ΔW_new P₀ P_self) | Adds novel sensibility orthogonal to identity & core logic
Dial Intensity | SLERP | Smoothly blends without norm collapse
Resolve Clashes | Weighted Sign-Election + Spectral Clamp | Prevents destructive interference
