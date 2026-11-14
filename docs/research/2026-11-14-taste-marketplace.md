# Taste into weight space, processed (2026-11-14)

Captured 2026-11-14 from a session the owner shared that extended the
SC-WSP line into two steps: compiling a subjective taste profile into a
portable, null-space-projected low-rank weight packet, then a marketplace
algebra for weaving several people's packets together
(subspace-constrained multi-profile composition). The owner noted this is
"something we are already exploring: packaging different profiles into a
marketplace where people can weave the parts of others' they like into
their own, personal expansion and taste refinement". The verbatim source is
preserved beside this file.

Claims checked against primary sources on capture, unless marked unverified.

## The five-step pipeline, fact-by-fact

1. **Bradley-Terry over pairwise comparisons.** Standard, textbook, and how
   RLHF reward models are trained. sigma(r(y+) - r(y-)) is the usual model.
   No dispute.
2. **Contrastive steering vectors from activation differences.** The "linear
   representation hypothesis" is an active, legitimate research thread.
   Averaging hidden-state differences across paired exemplars is a known
   method (representation engineering). Verified as real technique family.
3. **Outer-product / low-rank lift.** Rank-1 or LoRA-style lifting of a
   steering direction into a weight delta is standard practice
   (ROME-style rank-1 edits, LoRA decompositions). Sound.
4. **Null-space projection (AlphaEdit guardrail).** Verified machinery from
   the AlphaEdit capture. Keeping the delta orthogonal to preserved-knowledge
   keys is exactly what AlphaEdit does.
5. **Spectral normalization and quantization.** Normalizing largest singular
   value against the base layer and quantizing factors is standard, sane
   engineering.

The pipeline is coherent. Every step exists somewhere in the literature. It
has never been run end-to-end to produce a portable, semantic-tagged "taste
file" as a product, and nothing about the math guarantees that what it
extracts is "taste" rather than a style-correlated artifact of the exemplar
set. Treat the pipeline as a design, not a result.

## The marketplace algebra

Independent verification status:

- **SVD singular-mode slicing** of a merged profile: mathematically correct
  decomposition. The claim that modes carry separable semantic traits is
  plausible from SAE/representation work but is not guaranteed. Rank modes of
  an output-side delta are not guaranteed legible "aesthetic axes".
- **Concept erasure via subspace rejection**: standard projection, valid.
- **TIES-merging sign election (trim, elect dominant sign, average on
  agreement)**: real method, Yadav et al. 2023, used in mergekit. The
  attribution to it in the session is accurate.
- **Cascaded null projection (P₀ then P_self)**: consistent application of
  AlphaEdit's constraint to a new preserved subspace (your current taste).
  Sound as math, novel as product.
- **SLERP on singular vectors to dial taste intensity**: SLERP is a real
  interpolation used in model merging. "Modifies without norm collapse" is
  heralded by intuition more than measurement. Plausible, unverified.
- **Grassmannian/Stiefel framing**: correct terminology (subspaces on the
  Grassmannian, orthonormal frames on the Stiefel manifold), used loosely in
  the source. It changes nothing operationally.

Net: the algebra is legitimate composition theory applied to a product idea
that does not exist yet. Nothing here constitutes a working marketplace, but
nothing here is nonsense either.

## The mapping to MEP, and the line it must not cross

The marketplace the owner is exploring decomposes into two very different
things that the session text blurs:

### 1. A text-space profile marketplace (buildable now, fits MEP)

Every operation in the marketplace algebra has a document-space analog that
already works or is one design note away:

| Weight-space operation | Text-space MEP analog | Status |
| --- | --- | --- |
| Rank-1 slice import (one aesthetic axis) | Import the sections of another ethos that carry the trait, attribution intact | Possible today with ethos_get/export granularity |
| Subspace rejection (strip one vibe) | Select a subset of sections at import. The excluded parts are never copied | Possible |
| Cascaded null projection (keep your identity) | Imported preferences enter as proposals against your existing heads. You approve per conflict | Built and tested |
| TIES sign election | Contested heads surface to you. You resolve explicitly or reject | Deliberate design: MEP never auto-elects a winner |
| SLERP intensity dial | Inference confidence 0..1 plus explicit/approved gating | Built |
| Spectral clamp (blast-radius) | Invariant-flagged documents proposal (see the AlphaEdit capture) | Proposal |
| Provenance watermarking per mode | Source records, kind/reference, attribution in imports | Built at record level. A catalogue would need a registry (see below) |

The one genuinely missing piece in text space is **discovery**: a catalogue
of publishable ethos profiles ( "people's profiles you can browse, fork,
import"). The v0.1 spec explicitly defers a catalogue
("If a catalogue, if built, is a separately permissioned later product").
Designing that catalogue, with selective section import, attribution
ledgers and conflict preview against your current heads, is a real product
direction for ethos, buildable entirely today, no weights involved.

### 2. A weight-space packet marketplace (not safe, not now)

The critical difference is authority. In token space, an imported ethos
remains **context the host can read, quote, diff and reject**. The owner and
every gate can inspect it. Approvals bind exact revisions. Tombstones
suppress. Nothing applies that you did not approve. In weight space, the
packet becomes **capability the host cannot inspect**: it is an opaque binary
in the forward pass. The same null-space constraint that protects your
reasoning also enforces nothing you can see: it edits what the model *does*,
not what the model can *tell the host*. A marketplace packet, weighted toward
refusal-direction ablation or subtle manipulation, ships inside an object no
MEP tool is ever allowed to parse.

This is the one non-negotiable conclusion of this capture: **an ethos in
weights is an ethos without a gate.** Null-space projection protects the
model's other capabilities from the packet. It does nothing to protect you
from the packet. Marketplace mechanics for weights only become safe when
the host itself verifies incoming deltas (the verifier-gate discussion in
the W-MCP notes), and that gate does not exist in any shipped runtime.

If weight-space profiles ever ship, the minimum honest bar is: open weights,
locally rebuilt base, owner-verified packet provenance, and a delta the host
can reverse and inspect. None of the environments where that is true today
also have users asking for taste LoRAs at scale, so this stays parked.

## Direction

- The marketplace that matters is the **catalogue profile on top of MEP**:
  publishable, importable, selectively mergeable ethos profiles with
  attribution, on the existing record model. Natural home in a future MEP
  extension and possibly an SEP after adoption data exists.
- The **taste-strength dimension** (0..1 inference adoption dial) maps to
  existing confidence semantics. The slice/reject UX maps to partial import.
- The **weight-space track** stays research with the W-MCP and AlphaEdit
  notes. Reopens when self-hosted open-weights runtimes make verified deltas
  possible, which today means never for hosted APIs.
