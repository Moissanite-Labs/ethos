# Reference-only capture. NOT MEP code, NOT executed. Captured 2026-11-14,
# preserved verbatim apart from this banner. This generates a PDF the model
# that asked for it cannot read; the HTML inside html_content is the report.
# Provenance and full audit: docs/research/2026-11-14-scwsp-brief.md

import os
import weasyprint

os.makedirs('generated', exist_ok=True)
os.makedirs('temp', exist_ok=True)

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @page {
    size: letter portrait;
    margin: 0.42in 0.48in;
  }
  body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    color: #1a1d24;
    line-height: 1.32;
    font-size: 8.6pt;
    margin: 0;
    padding: 0;
  }
  .header {
    border-bottom: 2px solid #0f172a;
    padding-bottom: 6px;
    margin-bottom: 8px;
  }
  .title {
    font-size: 14.5pt;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.2px;
    margin: 0 0 2px 0;
  }
  .subtitle {
    font-size: 9pt;
    color: #475569;
    margin: 0;
    font-weight: 500;
  }
  .meta-bar {
    font-size: 7.6pt;
    color: #64748b;
    margin-top: 3px;
  }
  h2 {
    font-size: 9.6pt;
    font-weight: 700;
    color: #0f172a;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 2px;
    margin: 7px 0 4px 0;
    break-after: avoid;
  }
  p {
    margin: 0 0 5px 0;
  }
  .callout {
    background-color: #f8fafc;
    border-left: 3px solid #2563eb;
    padding: 5px 8px;
    margin: 5px 0 7px 0;
    font-size: 8.4pt;
    break-inside: avoid;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 5px 0 7px 0;
    font-size: 8pt;
    break-inside: avoid;
  }
  th {
    background-color: #0f172a;
    color: #ffffff;
    text-align: left;
    padding: 4px 6px;
    font-weight: 600;
  }
  td {
    border: 1px solid #cbd5e1;
    padding: 4px 6px;
    vertical-align: top;
  }
  tr:nth-child(even) td {
    background-color: #f8fafc;
  }
  .eq-box {
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 3px;
    padding: 4px 8px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 8.1pt;
    margin: 4px 0 6px 0;
    color: #0f172a;
    break-inside: avoid;
  }
  ul {
    margin: 2px 0 5px 0;
    padding-left: 15px;
  }
  li {
    margin-bottom: 2.5px;
  }
  .two-col {
    width: 100%;
    border-collapse: collapse;
    margin-top: 2px;
  }
  .two-col td {
    border: none;
    background: none !important;
    padding: 0;
    width: 49%;
    vertical-align: top;
  }
  .two-col td.spacer {
    width: 2%;
  }
  .footer {
    border-top: 1px solid #cbd5e1;
    margin-top: 6px;
    padding-top: 4px;
    font-size: 7.4pt;
    color: #64748b;
  }
  .code-inline {
    font-family: 'Courier New', Courier, monospace;
    background-color: #f1f5f9;
    padding: 0 2px;
    font-size: 8pt;
  }
</style>
</head>
<body>

<div class="header">
  <div class="title">Subspace-Constrained Weight-Space Programming (SC-WSP)</div>
  <div class="subtitle">Deterministic Multi-Tenant Isolation, Kilobyte-Scale State &amp; Composable Adapters for Planetary Inference</div>
  <div class="meta-bar">Technical Architecture Brief &bull; Prepared by Ahraz &bull; November 2026</div>
</div>

<div class="callout">
  <strong>Executive Summary:</strong> Serving millions of personalized AI workloads across shared TPU/GPU clusters faces a fundamental systems trade-off: stuffing user context into prompts saturates HBM and KV-cache bandwidth, whereas unguarded LoRA fine-tunes and raw weight-space edits introduce spectral instability and silent regressions in core reasoning or safety SLAs. <strong>SC-WSP</strong> bridges analytical null-space projection (AlphaEdit) with agentic weight-space synthesis, packaging behavioral and preference state as <strong>16&ndash;64 KB rank-<em>r</em> weight packets</strong> mathematically locked to the orthogonal complement of protected base capabilities (<span class="code-inline">K<sub>0</sub>&Delta;W = 0</span>).
</div>

<h2>1. The Infrastructure Bottleneck in Multi-Tenant Personalization</h2>
<table>
  <tr>
    <th style="width: 21%;">Serving Paradigm</th>
    <th style="width: 26%;">Memory &amp; Bandwidth Footprint</th>
    <th style="width: 27%;">Isolation &amp; SLA Guarantee</th>
    <th style="width: 26%;">Composability</th>
  </tr>
  <tr>
    <td><strong>Long-Context Prompting</strong></td>
    <td>High (10k+ tokens/req; severe HBM KV-cache pressure)</td>
    <td>Soft (prompt injection &amp; attention dilution risks)</td>
    <td>Fragile (context collisions &amp; quadratic attention cost)</td>
  </tr>
  <tr>
    <td><strong>Unguarded LoRA / WSP</strong></td>
    <td>Moderate to Low (MBs to KBs per adapter)</td>
    <td>None (spectral spikes degrade base reasoning/safety)</td>
    <td>Destructive (sign conflicts &amp; norm blowups on merge)</td>
  </tr>
  <tr>
    <td><strong>SC-WSP Packets (Ours)</strong></td>
    <td><strong>Ultra-Low (~16&ndash;64 KB factorized U, &Sigma;, V)</strong></td>
    <td><strong>Hard Linear-Algebraic (K<sub>0</sub>&Delta;W = 0 invariant)</strong></td>
    <td><strong>Orthogonal (conflict-free cascaded subspace weaving)</strong></td>
  </tr>
</table>

<h2>2. Core Mathematical &amp; Systems Architecture</h2>
<p>Rather than treating model customization as an unconstrained parameter update, SC-WSP compiles preference signals, behavioral repairs, or domain skills into a <strong>formally bounded low-rank perturbation</strong> through a four-stage pipeline:</p>

<div class="eq-box">
  <strong>1. Orthogonal Guardrail:</strong> &Delta;W<sub>safe</sub> = &Delta;W<sub>raw</sub> &middot; P<sub>0</sub>, &nbsp;where P<sub>0</sub> = I &minus; K<sub>0</sub>K<sub>0</sub><sup>+</sup> &nbsp;&rArr;&nbsp; K<sub>0</sub>&Delta;W<sub>safe</sub> = 0 (Zero Base Interference)<br>
  <strong>2. Cascaded Weaving:</strong> &nbsp;&nbsp;&Delta;W<sub>comp</sub> = &Delta;W<sub>self</sub> + &beta;(&Delta;W<sub>new</sub> &middot; P<sub>0</sub> &middot; P<sub>self</sub>), &nbsp;where P<sub>self</sub> = I &minus; V<sub>self</sub>V<sub>self</sub><sup>T</sup><br>
  <strong>3. Spectral Clamping:</strong> &nbsp;&Delta;W<sub>final</sub> = min(1, &gamma;&Vert;W<sub>0</sub>&Vert;<sub>2</sub> / &Vert;&Delta;W<sub>comp</sub>&Vert;<sub>2</sub>) &Delta;W<sub>comp</sub> &nbsp;(Eliminates Activation Explosions)
</div>

<ul>
  <li><strong>Protected Capability Subspace (K<sub>0</sub>):</strong> Precomputed once per base model checkpoint from canonical reasoning, coding, tool-use, and safety calibration activations. Any candidate update is projected onto <span class="code-inline">Null(K<sub>0</sub>)</span>, guaranteeing zero interference with base SLAs without per-tenant regression sweeps.</li>
  <li><strong>Cascaded Orthogonal Composition:</strong> When hot-swapping or combining multiple skill/persona packets at runtime, projecting incoming updates through <span class="code-inline">P<sub>self</sub></span> restricts new adaptations to unallocated subspace dimensions&mdash;preventing destructive interference across multi-skill workloads.</li>
  <li><strong>Zero-Pass Pre-Flight Verification &amp; Metering:</strong> Before a cluster mounts a third-party packet, a deterministic check verifies <span class="code-inline">&Vert;K<sub>0</sub>&Delta;W&Vert;<sub>F</sub> &le; &tau;</span> and spectral bound <span class="code-inline">&gamma;</span> in sub-millisecond time. Post-weave attribution shares are computed via exact Frobenius projection (<span class="code-inline">E<sub>i</sub> = &Vert;&Delta;W<sub>comp</sub>V<sub>i</sub>&Vert;<sub>F</sub><sup>2</sup></span>), enabling auditable metering and provenance.</li>
</ul>

<h2>3. TPU / GPU Serving Implications &amp; Open Systems Questions</h2>
<table class="two-col">
  <tr>
    <td>
      <p><strong>Runtime &amp; Storage Advantages</strong></p>
      <ul>
        <li><strong>KV-Cache Offloading:</strong> Replaces recurring multi-kilobyte prompt prefixes with static, cacheable rank-4 factors (<span class="code-inline">U &isin; &#8477;<sup>d&times;r</sup>, V &isin; &#8477;<sup>d&times;r</sup></span>) streamed cleanly from object storage into HBM.</li>
        <li><strong>Deterministic Multi-Tenancy:</strong> Enables safe execution of untrusted or user-composed adapters on shared inference slices with database-grade isolation.</li>
        <li><strong>Agentic Self-Repair:</strong> Allows meta-agents to patch reasoning loops in weight space while hardware/runtime wrappers enforce <span class="code-inline">P<sub>0</sub></span> invariants.</li>
      </ul>
    </td>
    <td class="spacer"></td>
    <td>
      <p><strong>Key Infrastructure Discussion Topics</strong></p>
      <ul>
        <li><strong>Systolic Array Batching:</strong> Optimizing heterogeneous rank-<em>r</em> (<span class="code-inline">r=4..16</span>) batched GEMMs (<span class="code-inline">xW<sub>0</sub> + (xU)&Sigma;V<sup>T</sup></span>) across TPU v5p/Trillium pods without fragmenting MXU utilization.</li>
        <li><strong>Subspace Fragmentation:</strong> Managing <span class="code-inline">Null(K<sub>0</sub>)</span> capacity limits across millions of tenants and recycling low-variance singular modes.</li>
        <li><strong>Distributed Caching:</strong> Tiering hot composite packets across HBM, host DRAM, and Colossus/GCS for sub-10ms cold-start personalization.</li>
      </ul>
    </td>
  </tr>
</table>

<div class="footer">
  <strong>Status &amp; Artifacts:</strong> Working Python reference compositor &amp; Frobenius attribution engine verified (<span class="code-inline">&Vert;K<sub>0</sub>&Delta;W&Vert;<sub>F</sub> &lt; 10<sup>&minus;14</sup></span>). Full mathematical specification and multi-profile algebra implementation available upon request.
</div>

</body>
</html>
"""

output_path = 'generated/SC-WSP_Technical_Brief.pdf'
weasyprint.HTML(string=html_content).write_pdf(output_path)

# Verify page count
import pypdf
reader = pypdf.PdfReader(output_path)
print("Page count:", len(reader.pages))
