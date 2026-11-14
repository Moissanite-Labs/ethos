# The W-MCP sketch (captured 2026-11-14)

Preserved verbatim from a session the owner shared on 2026-11-14. It reworks
MCP onto a weight-space wire. It is captured as a research direction, not as
a design for MEP. Read the provenance notes at the bottom before believing
any of it.

## The sketch

Replacing the text-token wire of the Model Context Protocol (MCP) with a
**Weight-Space Model Protocol (W-MCP)** shifts model communication from
**context-window serialization** to **direct parameter and subspace
transactions**. Instead of flattening external state into thousands of
tokens, the model's layers, residual subspaces, and low-rank adapters become
typed, capability-negotiated endpoints.

### Mapping MCP primitives into weight space

| MCP Primitive | Standard Token Wire | Weight-Space Wire (`W-MCP`) | Wire Invariant Required |
| --- | --- | --- | --- |
| `_meta` handshake | Protocol version and JSON capability flags | Architecture hash, layer geometry (`L, d_model, d_ff`), quantization, and SAE dictionary or SVD basis IDs | Exact checkpoint digest + basis alignment check |
| `resources/*` | Static/dynamic text URIs appended to KV cache | Read-only SVD slices or mountable rank-r Parametric RAG LoRA deltas via vLLM adapters | Mutual subspace orthogonality across mounted resources |
| `prompts/*` | Reusable text templates steering attention indirectly | Residual-stream steering vectors or SAE feature clamps: `steer(layer=l, dir=v, alpha)` | Bounded activation norm shift relative to residual RMS |
| `tools/*` | Autoregressive JSON call, text result | Latent probe interrupt on residual threshold, surgical rank-k weight patch ΔW (Takehi et al.) or forward-probe oracle (Hu et al.) | Spectral norm cap (‖ΔW‖₂ ≤ ε) + reversible transaction log |

### Two distinct architectures

- **Target-as-server (surgical model debugging).** A frontier reasoning model
  acts as the MCP client while a target network exposes weights and forward
  probes as an MCP server. In Sparks of Weight-Space Programming, an editing
  model subtracted a loop-inducing direction across 64 output columns in two
  layers (0.016% of Qwen3.5-0.8B), lifting MATH-500 accuracy from 7.9% to
  48.1%. Wrapping that workflow in MCP replaces raw tensor scripting with
  structured queries (`weights/svd`, `circuits/composition`,
  `probes/forward_kl`) and atomic rollback transactions.
- **Context-as-delta (zero-token parametric mounting).** External servers
  compile domain knowledge or behavioral policies directly into ephemeral
  low-rank weight deltas via LoRA hypernetworks rather than dumping tokens
  into the prompt. Three MCP servers means dynamically composing three
  low-rank deltas (W' = W₀ + Σ BᵢAᵢ) in GPU memory with zero context-window
  bloat.

### Three hard bottlenecks

- **The gauge and basis problem.** Token protocols work universally because
  UTF-8 means the same thing to every model, whereas raw weight matrices have
  arbitrary neuron permutation, scaling, and rotation symmetries. Recent
  audits (Can an LLM Actually Reason About Weights?, arXiv:2611.08070) show
  raw weight reading leans heavily on boundary-layer statistics and dataset
  priors rather than deep interior weight-flow tracing. A portable W-MCP
  cannot ship raw coordinates across model families. `_meta` negotiation must
  either bind to a canonical checkpoint hash or transmit patches in a shared
  semantic basis (aligned SAE features or input-output behavioral Jacobian
  targets).
- **Superposition collisions at scale.** In Hu et al. (arXiv:2611.09382), a
  1,023-parameter BF16 edit jumped Qwen3.5-0.8B from 8.35% to 37.80% on
  MATH-500, whereas Qwen3.5-9B barely budged (97.70% → 97.35%) and
  cross-task transfer occasionally regressed unrelated skills. If multiple
  W-MCP servers write deltas concurrently, the host router must project
  incoming ΔWᵢ into orthogonal nullspaces of existing capabilities (similar
  to ROME/MEMIT nullspace constraints) so servers do not overwrite each
  other.
- **Proof-carrying weight patches at the TCB boundary.** In token-space MCP a
  human or policy engine can read a JSON tool call before approving it. In
  weight space, an untrusted ΔW is an opaque binary patch capable of
  silently ablating refusal directions (SAE Refusal Steering,
  arXiv:2411.11296). Deployability requires a verifier gate between
  synthesis and GPU commit: cheap linear-algebraic certificates (spectral
  norm bounds, zero inner-product against protected safety subspaces) plus
  formal behavioral checks like permutation-invariant PCTL model checking
  (arXiv:2611.11604).

## Provenance and standing

Spot-checked 2026-11-14 by the ethos maintainers:

- "Sparks of Weight-Space Programming" is real and current (Takehi, Teoh,
  Zhang, Khattab, Nov 2026). The Qwen3.5-0.8B 7.9% → 48.1% MATH-500 figure is
  theirs. Treat replication as unverified until the benchmark harness ships.
- Hu et al., "Exploring Weight-Space Programming" (arXiv:2611.09382) is
  real. Its headline is uneven, localized gains and inconsistent reliability,
  not wholesale transfer.
- arXiv:2611.08070 (the skeptical audit) is real and is the load-bearing
  counterweight: boundary-layer statistics and dataset priors, not deep
  weight-flow reasoning.
- Citations to arXiv:2411.11296 and arXiv:2611.11604 were not
  independently checked and are plausible placeholders.
- "GPT-6 Astra" is the name used in the source material. No claim is made
  here about its availability or identity.
- Nothing here is MEP direction. MEP v0.1 deliberately ships no weight-space
  wire. This sketch is preserved for the day the gauge problem is solved.
