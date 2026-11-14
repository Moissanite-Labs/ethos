# The SC-WSP Technical Architecture Brief, audited (2026-11-14)

Captured 2026-11-14. The owner received a one-page PDF ("Subspace-Constrained
Weight-Space Programming: Deterministic Multi-Tenant Isolation,
Kilobyte-Scale State & Composable Adapters for Planetary Inference," dated
November 2026, "Prepared by Ahraz") with the Python/weasyprint source that
generates it. Two hard facts before the audit:

- This model cannot read PDF files, so the rendered artifact was not read.
  Every finding below is based on the HTML source inside the generator,
  which contains the complete report.
- The generator was not executed during capture: `weasyprint` and `pypdf`
  are not installed in this environment and no packages were added. It runs
  as ordinary Python modulo the two imports. Nothing else can be claimed
  about it until it is executed on a machine with the dependencies.

Generator preserved verbatim in
`prototypes/2026-11-14-scwsp-brief-generator.py`.

## What the document is

A one-page infrastructure pitch: personalized AI workloads on shared
TPU/GPU clusters, one brief, no citations, no benchmarks, eight-and-a-half
point type, "Prepared by Ahraz." Every technical claim chains back to the
WESP/AlphaEdit/taste-marketplace sessions already recorded in this
directory. It is a deck in PDF clothing, not an engineering specification.

## What is wrong, with measurements

1. **The footer "verified under 10^-14" claim is false for the metric it
   prints.** The footer says: "Working Python reference compositor and
   Frobenius attribution engine verified." Measured on
   the reference compositor itself (numpy 2.5.4): `‖K0 @ dW‖ = 6.93e+00`.
   The invariant the construction actually builds holds at `‖dW @ K0.T‖ ≈
   3.7e-15`. The brief inherited the wiring bug recorded in the prototype
   capture and then amplified it into a product claim. If this PDF circulates
   under the owner's name, that is the line that will be quoted.
2. **The headline invariant is mislabeled throughout.** "K₀ΔW = 0" appears in
   the callout, the invariants table, the equation box and the footer. In the
   construction captured from the same session, ΔW annihilates the preserved
   key directions (ΔW · K₀-keys⊥ ⇒ ΔW·K₀ᵀ = 0). The correct product never
   prints in the brief. The wrong one is printed four times. Fix the symbol
   orientation everywhere before this document leaves the machine.
3. **"Guarantees zero interference with base SLAs without per-tenant
   regression sweeps" overstates what null-space projection buys.**
   Projection protects only the span of K₀. Anything outside that span
   receives nothing. The document never says how K₀ is harvested, how large
   it is, or how coverage of "core reasoning, coding, tool-use, safety" is
   established. Rank-32 random keys of a 128-dim toy model are not "core
   reasoning, coding, tool use and safety" of a production checkpoint. A real
   K₀ would need stated methodology and evaluation on the target base.
4. **"Database-grade isolation" for untrusted adapters on shared slices has
   no implementation anywhere.** Nothing in vLLM or any serving stack today
   enforces a projection step on loaded user adapters. The guarantee is a
   property the brief asserts exists, on hardware that does not expose it.
5. **The packet-size claim is unsupported.** "16–64 KB factorized U,Σ,V per
   packet" works out for a single layer at modest d and rank 4 (2·4096·4·2·2
   bytes ≈ 65 KB per direction-pair per layer). It does not survive contact
   with full-network adapters at rank 4–16 across 30+ layers. The honest
   figure is on the order of a few MB, which is still small and still worth
   saying correctly.
6. **Attribution is called "exact" three times.** Under sequential
   null-space weaving with orthogonal contributors it is defensible. In
   general it is a normalized score that sums to one by construction, not a
   conservation law, and not an independent audit. "Exact" needs the
   orthogonality condition beside it every time it prints.
7. **Positioning without numbers.** "Planetary inference," "Colossus/GCS,"
   "TPU v5p/Trillium," "KV-cache offloading," "sub-10ms cold-start": all
   presented as engineering without a single measured memory, throughput or
   cold-start figure from any model, any GPU/TPU, any workload. An
   infrastructure audience will ask for those before the second paragraph.
8. **No provenance.** Not a citation in the brief. No license line. No
   artifact hashes. The byline reads "Prepared by Ahraz" on
   model-authored output with invented verification. Ownership optics are the
   owner's call to make, not inherit from a generator script.
9. **Good faith notes.** The layout works, the typography is usable, the
   structure is disciplined (bottleneck table, math, implications, footer
   status line), and the row-space projection premise is the real, correct
   AlphaEdit lineage. The bones are fine. The flesh is unaudited claims.

## What would make this document honest

- Replace "K₀ΔW = 0" with the correct orientation everywhere, and state the
  K₀ construction (source data, rank, coverage, evaluation) once, plainly.
- Change "verified" into: "reference prototype reproduces the
  preserved-key-invariance up to float noise on a 128-dim toy model. Real
  measurements pending on the target checkpoint." Then measure, once, on the
  target checkpoint, and print that number.
- Delete "database-grade isolation," "zero sweeps," "planetary," "exact,"
  "sub-10ms," "16–64 KB" or replace each with a measured fact.
- Add one benchmark table: before/after quality on two workloads, adapter
  size in MB, load time, and one sequential-weave regression curve.
- Reattribute honestly: "Draft by opn-eve (OpenCode), reviewed by A," or
  whatever the owner actually wants on the byline.

Until those land, this document is a narrative, not a specification, and
should not leave the machine under a named author.

## Disposition

The brief answers to the marketplace work already captured rather than to
the ethos protocol. It is preserved as a research artifact, not adopted,
not cited by MEP, not republished. The PDF itself is not committed here.
it remains in the owner's Downloads for the owner to decide whether to
keep, correct or discard.
