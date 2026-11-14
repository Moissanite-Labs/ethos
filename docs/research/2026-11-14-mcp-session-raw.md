> Provenance. Captured 2026-11-14 from a conversation the owner exported from
> another assistant (apparently Gemini). Preserved verbatim, including the
> embedded diagram markup (`<svg>`, `<Timeline>`, `<Sequence>`) and footnote
> URLs. Nothing here is MEP canon or verified fact: treat every claim as a
> lead to check against the primary sources in
> [docs/research/2026-11-14-mcp-session-notes.md](2026-11-14-mcp-session-notes.md).
> The owner asked for this capture verbatim. Unedited otherwise.
>
> Note on tooling: this file preserves third-party output as-is. It is not
> authored by this project and does not pass this repository's prose
> check, by construction. The processed notes live in
> [2026-11-14-mcp-session-notes.md](2026-11-14-mcp-session-notes.md).

---

# Model Context Protocol (MCP) — Complete Verbatim Conversation Transcript

---

## Turn 1

### User
diagram to explain mcp architecture please

### Assistant
The **Model Context Protocol (MCP)** uses a **client–host–server** architecture built on **JSON-RPC 2.0** to standardize how AI applications connect to external data sources and tools ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)).

### 1. Host–Client–Server Topology

An **MCP Host** (such as an AI IDE, desktop assistant, or agent runtime) coordinates the LLM and enforces security boundaries, spinning up one isolated **MCP Client** per **MCP Server** connection ([MCP Specification](https://modelcontextprotocol.io/specification/draft/architecture)).

```svg
<svg viewBox="0 0 680 416" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --lumi-ink: light-dark(#000000, #e0e0e0);
      --lumi-muted: light-dark(#5f6368, #9aa0a6);
      --lumi-dim: light-dark(#f2f0f0, #242528);
      --lumi-container: light-dark(#e8e6e6, #2d2f33);
      --lumi-outline: light-dark(#727676, #9a9b9c);
      --lumi-accent-bg: light-dark(#dcf1ff, #192967);
      --lumi-primary: light-dark(#3186ff, #9dd2ff);
      --lumi-sans: 'Google Sans Flex', var(--font-family, 'Google Sans', sans-serif);
      --lumi-mono: 'Google Sans Code', ui-monospace, monospace;
    }
    text { font-weight: 400; stroke: none; }
    .t-l1 { font-family: var(--lumi-sans); font-size: 15px; fill: var(--lumi-ink); }
    .t-l2 { font-family: var(--lumi-mono); font-size: 13px; font-style: italic; fill: var(--lumi-ink); }
    .t-l4 { font-family: var(--lumi-sans); font-size: 13px; fill: var(--lumi-muted); }
    .node-step { fill: var(--lumi-dim); stroke: none; }
    .node-focal { fill: var(--lumi-accent-bg); stroke: var(--lumi-primary); stroke-width: 1.25; }
    .node-store { fill: var(--lumi-container); stroke: var(--lumi-outline); stroke-width: 1; }
    .edge-seg { fill: none; stroke: var(--lumi-ink); stroke-width: 1.3; stroke-linecap: round; stroke-dasharray: 0 4; }
    .edge-arrow { fill: none; stroke: var(--lumi-ink); stroke-width: 1.3; stroke-linecap: round; stroke-dasharray: 0 4; marker-end: url(#lumi-caret-1); }
  </style>
  <defs>
    <marker id="lumi-caret-1" viewBox="0 0 10 10" refX="7.5" refY="5" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" orient="auto">
      <path d="M 3 1.2 L 7.5 5 L 3 8.8" fill="none" stroke="var(--lumi-ink)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <rect class="node-focal" x="230" y="20" width="220" height="72" rx="36"/>
  <text class="t-l1" x="340" y="47" text-anchor="middle" dominant-baseline="central">MCP Host</text>
  <text class="t-l4" x="340" y="68" text-anchor="middle" dominant-baseline="central">AI app, LLM &amp; security</text>

  <path class="edge-arrow" d="M 340 100 L 340 108 Q 340 124 324 124 L 198 124 Q 182 124 182 140 L 182 160"/>
  <path class="edge-arrow" d="M 340 100 L 340 108 Q 340 124 356 124 L 482 124 Q 498 124 498 140 L 498 160"/>

  <rect class="node-step" x="88" y="168" width="188" height="72" rx="36"/>
  <text class="t-l1" x="182" y="195" text-anchor="middle" dominant-baseline="central">MCP Client 1</text>
  <text class="t-l4" x="182" y="216" text-anchor="middle" dominant-baseline="central">1:1 isolated session</text>

  <rect class="node-step" x="404" y="168" width="188" height="72" rx="36"/>
  <text class="t-l1" x="498" y="195" text-anchor="middle" dominant-baseline="central">MCP Client 2</text>
  <text class="t-l4" x="498" y="216" text-anchor="middle" dominant-baseline="central">1:1 isolated session</text>

  <line class="edge-seg" x1="182" y1="248" x2="182" y2="264"/>
  <rect data-role="edge-pill" x="154" y="272" width="56" height="20" rx="10" fill="var(--lumi-dim)"/>
  <text class="t-l2" x="182" y="282" text-anchor="middle" dominant-baseline="central">stdio</text>
  <line class="edge-arrow" x1="182" y1="300" x2="182" y2="316"/>

  <line class="edge-seg" x1="498" y1="248" x2="498" y2="264"/>
  <rect data-role="edge-pill" x="432" y="272" width="132" height="20" rx="10" fill="var(--lumi-dim)"/>
  <text class="t-l2" x="498" y="282" text-anchor="middle" dominant-baseline="central">Streamable HTTP</text>
  <line class="edge-arrow" x1="498" y1="300" x2="498" y2="316"/>

  <rect class="node-store" x="88" y="324" width="188" height="72" rx="36"/>
  <text class="t-l1" x="182" y="351" text-anchor="middle" dominant-baseline="central">Local MCP Server</text>
  <text class="t-l4" x="182" y="372" text-anchor="middle" dominant-baseline="central">Files, Git, local CLI</text>

  <rect class="node-store" x="404" y="324" width="188" height="72" rx="36"/>
  <text class="t-l1" x="498" y="351" text-anchor="middle" dominant-baseline="central">Remote MCP Server</text>
  <text class="t-l4" x="498" y="372" text-anchor="middle" dominant-baseline="central">APIs, DBs, SaaS</text>
</svg>
```

- **Isolation by design:** Servers cannot read the full conversation history or inspect other servers; the host mediates all cross-server context and user consent ([MCP Specification](https://modelcontextprotocol.io/specification/draft/architecture)).
- **Transport layer:** Local servers typically run as subprocesses over **stdio**, while remote servers communicate over **Streamable HTTP** with optional Server-Sent Events and OAuth/bearer-token auth ([Transport Layer](https://modelcontextprotocol.io/docs/2025-03-26/learn/architecture)).

### 2. Data Layer & Core Primitives

Above the transport, clients and servers exchange **JSON-RPC 2.0** messages to negotiate capabilities and expose three main server primitives ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)):

```svg
<svg viewBox="0 0 680 264" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --lumi-ink: light-dark(#000000, #e0e0e0);
      --lumi-muted: light-dark(#5f6368, #9aa0a6);
      --lumi-dim: light-dark(#f2f0f0, #242528);
      --lumi-container: light-dark(#e8e6e6, #2d2f33);
      --lumi-outline: light-dark(#727676, #9a9b9c);
      --lumi-accent-bg: light-dark(#dcf1ff, #192967);
      --lumi-primary: light-dark(#3186ff, #9dd2ff);
      --lumi-sans: 'Google Sans Flex', var(--font-family, 'Google Sans', sans-serif);
      --lumi-mono: 'Google Sans Code', ui-monospace, monospace;
    }
    text { font-weight: 400; stroke: none; }
    .t-l1 { font-family: var(--lumi-sans); font-size: 15px; fill: var(--lumi-ink); }
    .t-l2 { font-family: var(--lumi-mono); font-size: 13px; font-style: italic; fill: var(--lumi-ink); }
    .t-l4 { font-family: var(--lumi-sans); font-size: 13px; fill: var(--lumi-muted); }
    .node-step { fill: var(--lumi-dim); stroke: none; }
    .node-focal { fill: var(--lumi-accent-bg); stroke: var(--lumi-primary); stroke-width: 1.25; }
    .node-store { fill: var(--lumi-container); stroke: var(--lumi-outline); stroke-width: 1; }
    .edge-seg { fill: none; stroke: var(--lumi-ink); stroke-width: 1.3; stroke-linecap: round; stroke-dasharray: 0 4; }
    .edge-arrow { fill: none; stroke: var(--lumi-ink); stroke-width: 1.3; stroke-linecap: round; stroke-dasharray: 0 4; marker-end: url(#lumi-caret-2); }
  </style>
  <defs>
    <marker id="lumi-caret-2" viewBox="0 0 10 10" refX="7.5" refY="5" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" orient="auto">
      <path d="M 3 1.2 L 7.5 5 L 3 8.8" fill="none" stroke="var(--lumi-ink)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <rect class="node-step" x="80" y="20" width="176" height="72" rx="36"/>
  <text class="t-l1" x="168" y="47" text-anchor="middle" dominant-baseline="central">MCP Client</text>
  <text class="t-l4" x="168" y="68" text-anchor="middle" dominant-baseline="central">Declares capabilities</text>

  <line class="edge-seg" x1="264" y1="56" x2="282" y2="56"/>
  <rect data-role="edge-pill" x="290" y="46" width="100" height="20" rx="10" fill="var(--lumi-dim)"/>
  <text class="t-l2" x="340" y="56" text-anchor="middle" dominant-baseline="central">JSON-RPC 2.0</text>
  <line class="edge-arrow" x1="398" y1="56" x2="416" y2="56"/>

  <rect class="node-focal" x="424" y="20" width="176" height="72" rx="36"/>
  <text class="t-l1" x="512" y="47" text-anchor="middle" dominant-baseline="central">MCP Server</text>
  <text class="t-l4" x="512" y="68" text-anchor="middle" dominant-baseline="central">Advertises primitives</text>

  <path class="edge-arrow" d="M 512 100 L 512 112 Q 512 128 496 128 L 146 128 Q 130 128 130 144 L 130 160"/>
  <path class="edge-arrow" d="M 512 100 L 512 112 Q 512 128 496 128 L 356 128 Q 340 128 340 144 L 340 160"/>
  <path class="edge-arrow" d="M 512 100 L 512 112 Q 512 128 528 128 L 534 128 Q 550 128 550 144 L 550 160"/>

  <rect class="node-store" x="40" y="168" width="180" height="76" rx="38"/>
  <text class="t-l1" x="130" y="196" text-anchor="middle" dominant-baseline="central">Tools</text>
  <text class="t-l4" x="130" y="217" text-anchor="middle" dominant-baseline="central">Executable actions</text>

  <rect class="node-store" x="250" y="168" width="180" height="76" rx="38"/>
  <text class="t-l1" x="340" y="196" text-anchor="middle" dominant-baseline="central">Resources</text>
  <text class="t-l4" x="340" y="217" text-anchor="middle" dominant-baseline="central">Read-only context</text>

  <rect class="node-store" x="460" y="168" width="180" height="76" rx="38"/>
  <text class="t-l1" x="550" y="196" text-anchor="middle" dominant-baseline="central">Prompts</text>
  <text class="t-l4" x="550" y="217" text-anchor="middle" dominant-baseline="central">Reusable templates</text>
</svg>
```

- **Tools** let the model invoke external functions (e.g., querying a DB or running a build), **Resources** expose structured data (files, schemas, logs) to the host, and **Prompts** provide user-invoked workflow templates ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)).

---

## Turn 2

### User
Show a sequence diagram of the MCP protocol version and capability discovery handshake between a client and server.

### Assistant
In the latest MCP specification (`2026-07-28`), the protocol is **stateless**: every request carries the client's protocol version and capabilities in `_meta`, while `server/discover` lets a client inspect what a server supports up front ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)).

```svg
<svg viewBox="0 0 680 436" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --lumi-ink: light-dark(#000000, #e0e0e0);
      --lumi-muted: light-dark(#5f6368, #9aa0a6);
      --lumi-dim: light-dark(#f2f0f0, #242528);
      --lumi-container: light-dark(#e8e6e6, #2d2f33);
      --lumi-outline: light-dark(#727676, #9a9b9c);
      --lumi-accent-bg: light-dark(#dcf1ff, #192967);
      --lumi-primary: light-dark(#3186ff, #9dd2ff);
      --lumi-sans: 'Google Sans Flex', var(--font-family, 'Google Sans', sans-serif);
      --lumi-mono: 'Google Sans Code', ui-monospace, monospace;
    }
    text { font-weight: 400; stroke: none; }
    .t-l1 { font-family: var(--lumi-sans); font-size: 15px; fill: var(--lumi-ink); }
    .t-l2 { font-family: var(--lumi-mono); font-size: 13px; font-style: italic; fill: var(--lumi-ink); }
    .t-l4 { font-family: var(--lumi-sans); font-size: 13px; fill: var(--lumi-muted); }
    .node-step { fill: var(--lumi-dim); stroke: none; }
    .node-focal { fill: var(--lumi-accent-bg); stroke: var(--lumi-primary); stroke-width: 1.25; }
    .lifeline { fill: none; stroke: var(--lumi-outline); stroke-width: 1; stroke-dasharray: 2 4; }
    .edge-arrow { fill: none; stroke: var(--lumi-ink); stroke-width: 1.3; stroke-linecap: round; stroke-dasharray: 0 4; marker-end: url(#lumi-caret-1); }
  </style>
  <defs>
    <marker id="lumi-caret-1" viewBox="0 0 10 10" refX="7.5" refY="5" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" orient="auto">
      <path d="M 3 1.2 L 7.5 5 L 3 8.8" fill="none" stroke="var(--lumi-ink)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <rect class="node-step" x="56" y="20" width="168" height="56" rx="28"/>
  <text class="t-l1" x="140" y="48" text-anchor="middle" dominant-baseline="central">MCP Client</text>

  <rect class="node-focal" x="456" y="20" width="168" height="56" rx="28"/>
  <text class="t-l1" x="540" y="48" text-anchor="middle" dominant-baseline="central">MCP Server</text>

  <line class="lifeline" x1="140" y1="84" x2="140" y2="420"/>
  <line class="lifeline" x1="540" y1="84" x2="540" y2="420"/>

  <text class="t-l2" x="340" y="110" text-anchor="middle" dominant-baseline="central">1. server/discover</text>
  <line class="edge-arrow" x1="148" y1="124" x2="532" y2="124"/>
  <text class="t-l4" x="340" y="139" text-anchor="middle" dominant-baseline="central">_meta: protocolVersion, clientCapabilities, clientInfo</text>

  <text class="t-l2" x="340" y="182" text-anchor="middle" dominant-baseline="central">If mismatch: UnsupportedProtocolVersionError</text>
  <line class="edge-arrow" x1="532" y1="196" x2="148" y2="196"/>
  <text class="t-l4" x="340" y="211" text-anchor="middle" dominant-baseline="central">Returns supportedVersions; client retries</text>

  <text class="t-l2" x="340" y="254" text-anchor="middle" dominant-baseline="central">2. Discovery Result (complete)</text>
  <line class="edge-arrow" x1="532" y1="268" x2="148" y2="268"/>
  <text class="t-l4" x="340" y="283" text-anchor="middle" dominant-baseline="central">capabilities (tools, resources), serverInfo, ttlMs</text>

  <text class="t-l2" x="340" y="326" text-anchor="middle" dominant-baseline="central">3. tools/list (or subscriptions/listen)</text>
  <line class="edge-arrow" x1="148" y1="340" x2="532" y2="340"/>
  <text class="t-l4" x="340" y="355" text-anchor="middle" dominant-baseline="central">Repeats _meta version &amp; capabilities per request</text>

  <text class="t-l2" x="340" y="392" text-anchor="middle" dominant-baseline="central">4. Primitive Schemas &amp; ttlMs</text>
  <line class="edge-arrow" x1="532" y1="406" x2="148" y2="406"/>
</svg>
```

- **Protocol version negotiation:** The client declares `io.modelcontextprotocol/protocolVersion` in `_meta`; if the server doesn't support it, it returns `UnsupportedProtocolVersionError` with `supportedVersions` so the client can retry ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)).
- **Cacheable discovery:** `server/discover` is optional because every request already carries `_meta`, and its response includes `ttlMs` and `cacheScope` so clients can reuse capability metadata across requests ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)). *(Older `2025-06-18` implementations instead used a stateful `initialize` / `notifications/initialized` startup handshake — [2025-06-18 Spec](https://modelcontextprotocol.io/specification/2025-06-18/architecture).)*

---

## Turn 3

### User
does mcp size affect context window? why or why not?

### Assistant
**Yes—the size of an MCP server's *exposed interface* directly affects the context window, while its internal code and unqueried data do not.**

### What consumes context window
- **Upfront tool definitions (`tools/list`):** In a standard setup, the MCP host injects every connected server's tool names, descriptions, and JSON `inputSchema`s into the model's prompt at the start of a conversation; across dozens of servers or hundreds of tools, those schemas alone can eat most of the context window before the model reads your prompt ([MCP Client Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices)).
- **Tool results and loaded resources:** Every `tools/call` response (`content` array), embedded resource, or invoked prompt template is appended to the conversation history and counts against the context limit ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)).

### What does *not* consume context window
- **Server codebase and backing stores:** An MCP server's own implementation size, dependencies, databases, and unread `resources` stay isolated in the server process and never enter the LLM's context unless explicitly requested by the client ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)).

### How hosts keep context overhead small
- **Progressive tool discovery:** Once tool definitions exceed a small threshold (for example, 1%–5% of the context window), the host withholds full schemas and gives the model a lightweight `search_tools` meta-tool to load only the schemas it needs ([MCP Client Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices)).
- **Dynamic server connections:** Hosts can keep a lightweight server index, connect to a server only when needed, and disconnect it afterward to free context ([MCP Client Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices)).
- **Programmatic tool calling:** Instead of passing large intermediate tool outputs back through the model step by step, the model can invoke multiple tools from a single script so only the final result enters context ([MCP Client Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices)).

---

## Turn 4

### User
who decides mcp specs and updates

### Assistant
Anthropic originally created MCP in November 2024 ([Anthropic](https://www.anthropic.com/news/model-context-protocol)), and the specification is now governed as an open-source project under **SEP-932** ([Governance and Stewardship](https://modelcontextprotocol.io/community/governance), [SEP-932](https://modelcontextprotocol.io/seps/932-model-context-protocol-governance)).

### Who makes the decisions
- **Lead Maintainers:** Serve as final decision-makers responsible for long-term project health ([Governance and Stewardship](https://modelcontextprotocol.io/community/governance)).
- **Core Maintainers:** Steer the MCP specification and overall roadmap, meet bi-weekly, appoint component maintainers, and can veto maintainer decisions by majority vote ([Governance and Stewardship](https://modelcontextprotocol.io/community/governance), [SEP-932](https://modelcontextprotocol.io/seps/932-model-context-protocol-governance)).
- **Maintainers & Working Groups:** Own specific SDKs, documentation, and domain Working Groups, where community proposals are refined and sponsored ([Governance and Stewardship](https://modelcontextprotocol.io/community/governance), [Contributing to MCP](https://modelcontextprotocol.io/community/contributing)).

### How spec updates are approved
Major protocol changes go through **Specification Enhancement Proposals (SEPs)** in the [`modelcontextprotocol`](https://github.com/modelcontextprotocol/modelcontextprotocol) GitHub repository ([SEPs Index](https://modelcontextprotocol.io/seps)):
1. A contributor discusses the idea in a Working Group or Interest Group and secures a **Working Group** or **Core Maintainer** sponsor ([Contributing to MCP](https://modelcontextprotocol.io/community/contributing)).
2. The SEP pull request (with a prototype) is reviewed by **Core Maintainers** ([Contributing to MCP](https://modelcontextprotocol.io/community/contributing)).
3. Once accepted, the reference implementation, schema/spec updates, and conformance tests must be completed before the SEP is marked `Final` and merged ([SEP Guidelines](https://mcp-staging.mintlify.app/community/sep-guidelines)).

---

## Turn 5

### User
show me what this looks like in pracice

### Assistant
A concrete way to see MCP governance in action is **SEP-1686 (Tasks)**—the feature that added durable "call-now, fetch-later" execution for long-running workflows ([SEP-1686](https://modelcontextprotocol.io/seps/1686-tasks)).

&lt;Timeline&gt;
&lt;TimelineEvent title=&quot;1. Proposal &amp; Core Maintainer acceptance (SEP-1686)&quot; time=&quot;Oct 20, 2025&quot;&gt;
Authors opened [issue #1686](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1686) to let servers wrap systems like AWS Step Functions and CI/CD pipelines with a `taskId` and polling (`tasks/get`). Once the prototype and spec text ([PR #1732](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1686)) passed review, Core Maintainers marked it `Final` ([SEP-1686](https://modelcontextprotocol.io/seps/1686-tasks)).
&lt;/TimelineEvent&gt;
&lt;TimelineEvent title=&quot;2. Experimental release in the 2025-11-25 spec&quot; time=&quot;Nov 25, 2025&quot;&gt;
After a 14-day release-candidate validation window ([MCP Blog](https://blog.modelcontextprotocol.io/tags/protocol/)), Tasks shipped as an experimental core feature in the [2025-11-25 specification](https://modelcontextprotocol.io/specification/2025-11-25/changelog).
&lt;/TimelineEvent&gt;
&lt;TimelineEvent title=&quot;3. Production feedback shapes the 2026 roadmap&quot; time=&quot;Mar 9, 2026&quot;&gt;
Real-world deployments surfaced gaps around transient failure retries and result-retention expiry, so maintainers placed Tasks lifecycle iteration onto the [2026 MCP Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/).
&lt;/TimelineEvent&gt;
&lt;TimelineEvent title=&quot;4. Release Candidate &amp; opt-in Beta SDKs&quot; time=&quot;May – Jun 2026&quot;&gt;
Working Groups refactored Tasks into an official extension (`io.modelcontextprotocol/tasks` via SEP-2663) to fit the new stateless core, then shipped a [Release Candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) and opt-in [Beta SDKs](https://blog.modelcontextprotocol.io/posts/sdk-betas-2026-07-28/) for TypeScript, Python, Go, and C# so developers could test before lock-in.
&lt;/TimelineEvent&gt;
&lt;TimelineEvent title=&quot;5. General availability in 2026-07-28&quot; time=&quot;Jul 28, 2026&quot;&gt;
The [2026-07-28 specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/) went live alongside updated Tier 1 SDKs passing 100% conformance tests, backed by a formal 12-month deprecation window for older behaviors ([2026-07-28 Spec](https://blog.modelcontextprotocol.io/posts/2026-07-28/), [Ruby SDK Tier 1](https://blog.modelcontextprotocol.io/posts/ruby-sdk-tier-1/)).
&lt;/TimelineEvent&gt;
&lt;/Timeline&gt;

In day-to-day practice, this means nothing lands in the core spec on a single PR: ideas incubate in Working Groups or `experimental-ext-` repos ([Roadmap](https://modelcontextprotocol.io/development/roadmap)), require a prototype and conformance tests before a SEP is marked `Final`, and get road-tested via a Release Candidate and beta SDKs before becoming GA.

---

## Turn 6

### User
lets delve into making custom MCPs

### Assistant
Building a custom MCP server comes down to defining a small, well-typed capability surface with an official SDK, serving it over **stdio** or **Streamable HTTP**, and verifying it with the **MCP Inspector** ([Build an MCP Server](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server)).

&lt;Sequence&gt;
&lt;Step title=&quot;Design the tools, resources, and prompts&quot; subtitle=&quot;Keep schemas lean to save context tokens&quot;&gt;
Decide what the model should **execute** (`Tools`), what read-only data the host should **attach** (`Resources`), and what reusable templates users can **trigger** (`Prompts`) ([Build an MCP Server](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server)). Write crisp tool names and parameter descriptions, since those schemas are what the LLM sees ([Build MCP Server Guide](https://mcp.so/blog/build-mcp-server)).
&lt;/Step&gt;
&lt;Step title=&quot;Set up an official Tier 1 SDK&quot;&gt;
Choose the **TypeScript v2 SDK** (`@modelcontextprotocol/server`, `zod`, `tsx` on Node 20+) or the **Python SDK v2** (`mcp &gt;= 2.0.0` via `uv`) ([TypeScript SDK v2](https://ts.sdk.modelcontextprotocol.io/v2/get-started/first-server.html), [Build an MCP Client](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-client)). Official SDKs handle JSON-RPC 2.0 framing, `server/discover`, and `_meta` version negotiation automatically ([MCP SDKs](https://modelcontextprotocol.io/docs/2026-07-28/sdk)).
&lt;/Step&gt;
&lt;Step title=&quot;Register typed tools inside a server factory&quot;&gt;
Define a factory function that instantiates your server and registers tools with validated schemas (`registerTool(name, config, handler)` with Zod in TypeScript, or `MCPServer` with Python type hints and docstrings) ([TypeScript SDK v2](https://ts.sdk.modelcontextprotocol.io/v2/get-started/first-server.html), [Build an MCP Server](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server)). Using a factory lets the same server logic run across both local and stateless HTTP transports ([Build MCP Server Guide](https://mcp.so/blog/build-mcp-server)).
&lt;/Step&gt;
&lt;Step title=&quot;Attach a transport&quot; subtitle=&quot;Never log to stdout on stdio servers&quot;&gt;
Use `serveStdio` for local child-process integrations, or `createMcpHandler` for stateless remote **Streamable HTTP** endpoints behind a standard load balancer ([TypeScript SDK v2](https://ts.sdk.modelcontextprotocol.io/v2/get-started/first-server.html), [Build MCP Server Guide](https://mcp.so/blog/build-mcp-server)). Always write logs to `stderr` when using `stdio`, because `stdout` carries the JSON-RPC stream ([TypeScript SDK v2](https://ts.sdk.modelcontextprotocol.io/v2/get-started/first-server.html)).
&lt;/Step&gt;
&lt;Step title=&quot;Test with MCP Inspector and wire into a host&quot;&gt;
Run `npx @modelcontextprotocol/inspector &lt;command&gt;` (or use `--cli` for scripted CI checks) to test `tools/list` and `tools/call` before connecting a host like Claude Desktop, Cursor, or VS Code ([MCP Inspector](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector), [Inspector CLI](https://modelcontextprotocol.io/docs/draft/tools/inspector/cli)).
&lt;/Step&gt;
&lt;/Sequence&gt;

One detail that trips up most first builds: return tool failures as structured tool error results (`isError: true`) rather than crashing the process, so the LLM can read the message and recover ([Build an MCP Client](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-client)).

---

## Turn 7

### User
what if i didnt want to adhere to the protocol? fork the MCP repo into my own version? would it still work with models? what considerations?

### Assistant
**Yes, it will still work with LLMs—provided you control the MCP Host/Client—because models never speak MCP directly.**

The model only sees tool names, descriptions, JSON Schemas, and tool results that the **host application** translates into the LLM provider's native function-calling format ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)). The [`modelcontextprotocol`](https://github.com/modelcontextprotocol/modelcontextprotocol) repository is MIT-licensed ([LICENSE](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/LICENSE)), so you're legally free to fork the spec or SDKs.

### What breaks vs. what keeps working
- **Your own host + server stack (works):** If you fork both the client and server—say, swapping JSON-RPC 2.0 for gRPC, binary framing, or custom execution receipts—any LLM will still reason over your tools normally as long as your host feeds it clean schemas and results.
- **Third-party hosts (breaks):** Off-the-shelf hosts like Claude Desktop, Cursor, and VS Code expect standard `server/discover` (or legacy `initialize`), `_meta` version negotiation, and standard `tools/*` payloads ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)). Changing wire shapes or rejecting standard versions breaks plug-and-play support.

### Key considerations before forking
- **Loss of ecosystem tooling:** You give up zero-config compatibility with the [MCP Inspector](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector), community servers, and conformance suites unless you maintain a translation shim.
- **Security and spec-drift burden:** You become solely responsible for porting upstream fixes around OAuth/CIMD authorization, issuer validation, and transport hardening ([2026-07-28 Spec](https://blog.modelcontextprotocol.io/posts/2026-07-28/)).
- **Alternatives to a hard fork:**
  - **Use an MCP Extension (SEP-2133):** MCP lets you attach custom, opt-in capabilities under a `{vendor-prefix}/{extension-name}` namespace in `capabilities` and `_meta`, keeping standard hosts working while your own host reads the custom fields ([SEP-2133](https://modelcontextprotocol.io/seps/2133-extensions)).
  - **Keep a thin adapter:** Run your own internal protocol between your services, and expose a small MCP-compliant facade only where third-party hosts need to connect.

---

## Turn 8

### User
what do i need to keep the same to maintain compatibility, vs what can i use as an independent variable to alter in attempts to arrive at optimization?

### Assistant
To stay compatible with third-party MCP hosts (Claude Desktop, Cursor, VS Code) and tools like the [MCP Inspector](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector), you only need to lock down the **wire contract**. Everything inside the server, on the host's prompt-assembly side, and inside vendor extensions is an independent variable you can tune.

| Layer | Keep Fixed (Compatibility Invariant) | Vary Freely (Optimization Lever) |
| :--- | :--- | :--- |
| **Envelope & Lifecycle** | JSON-RPC 2.0 framing, standard methods (`server/discover`, `tools/*`, `resources/*`), and `_meta` version/capability fields ([Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)) | Internal routing, request batching, and horizontal scaling behind a round-robin load balancer via `Mcp-Method` / `Mcp-Name` headers ([2026-07-28 Spec](https://blog.modelcontextprotocol.io/posts/2026-07-28/)) |
| **Transport & Auth** | Clean `stdio` (logs strictly on `stderr`) or Streamable HTTP with standard OAuth / RFC 9207 `iss` validation ([TypeScript SDK v2](https://ts.sdk.modelcontextprotocol.io/v2/get-started/first-server.html), [2026-07-28 RC](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)) | Process runtime, async I/O engine, connection pooling, and HTTP compression/keep-alive tuning |
| **Tool Surface & Schemas** | Valid JSON Schema 2020-12 `inputSchema` / `outputSchema`, `content` arrays, and `isError: true` for recoverable errors ([2026-07-28 RC](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/), [Build an MCP Client](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-client)) | Tool granularity (coarse workflow tools vs. fine-grained CRUD), description token density, and deterministic tool ordering for prompt-cache hits ([2026-07-28 Spec](https://blog.modelcontextprotocol.io/posts/2026-07-28/)) |
| **Catalog & Context Loading** | Valid `tools/list` / `resources/read` response shapes ([Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)) | `ttlMs` and `cacheScope` freshness hints on the server; **progressive discovery** (`search_tools`), dynamic server connect/disconnect, and **programmatic tool calling** on the host ([Client Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices)) |
| **Custom Capabilities** | Standard core capability keys (`tools`, `resources`, `prompts`, `elicitation`) ([Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)) | Vendor-namespaced **SEP-2133 Extensions** (`{vendor-prefix}/{name}`) and custom `_meta` keys—standard hosts ignore them while your own host can act on them ([SEP-2133](https://modelcontextprotocol.io/seps/2133-extensions)) |

The highest-leverage variables to sweep first are **tool granularity + description length** (token cost and tool-selection accuracy), **`ttlMs` + deterministic ordering** (latency and prompt-cache hit rate), and **progressive discovery** on the host once your tool catalog grows past a few percent of the context window ([Client Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices)).

---

## Turn 9

### User
i want to make an MCP that's formally verified end-to-end

### Assistant
To build an end-to-end formally verified MCP server without breaking compatibility with standard hosts, keep the **OS/transport I/O shim** as a thin, isolated Trusted Computing Base (TCB) and push **parsing, `_meta` version/capability gating, schema validation, tool logic, and serialization** into a verified core (for example, in **Lean 4** compiled to native code or paired with a **C11** differential verifier).

*(Note on scope: you can formally verify the server's protocol state machine, policy gates, and deterministic handlers end-to-end, while the OS socket/pipe layer, TLS stack, and remote LLM remain outside the proof boundary.)*

```svg
<svg viewBox="0 0 680 256" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --lumi-ink: light-dark(#000000, #e0e0e0);
      --lumi-muted: light-dark(#5f6368, #9aa0a6);
      --lumi-dim: light-dark(#f2f0f0, #242528);
      --lumi-container: light-dark(#e8e6e6, #2d2f33);
      --lumi-outline: light-dark(#727676, #9a9b9c);
      --lumi-accent-bg: light-dark(#dcf1ff, #192967);
      --lumi-primary: light-dark(#3186ff, #9dd2ff);
      --lumi-sans: 'Google Sans Flex', var(--font-family, 'Google Sans', sans-serif);
      --lumi-mono: 'Google Sans Code', ui-monospace, monospace;
    }
    text { font-weight: 400; stroke: none; }
    .t-l1 { font-family: var(--lumi-sans); font-size: 15px; fill: var(--lumi-ink); }
    .t-l2 { font-family: var(--lumi-mono); font-size: 13px; font-style: italic; fill: var(--lumi-ink); }
    .t-l4 { font-family: var(--lumi-sans); font-size: 13px; fill: var(--lumi-muted); }
    .node-step { fill: var(--lumi-dim); stroke: none; }
    .node-focal { fill: var(--lumi-accent-bg); stroke: var(--lumi-primary); stroke-width: 1.25; }
    .node-store { fill: var(--lumi-container); stroke: var(--lumi-outline); stroke-width: 1; }
    .edge-arrow { fill: none; stroke: var(--lumi-ink); stroke-width: 1.3; stroke-linecap: round; stroke-dasharray: 0 4; marker-end: url(#lumi-caret-fv); }
  </style>
  <defs>
    <marker id="lumi-caret-fv" viewBox="0 0 10 10" refX="7.5" refY="5" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" orient="auto">
      <path d="M 3 1.2 L 7.5 5 L 3 8.8" fill="none" stroke="var(--lumi-ink)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <rect class="node-store" x="64" y="20" width="216" height="72" rx="36"/>
  <text class="t-l1" x="172" y="47" text-anchor="middle" dominant-baseline="central">Thin I/O Shim (TCB)</text>
  <text class="t-l4" x="172" y="68" text-anchor="middle" dominant-baseline="central">stdio / HTTP bytes in &amp; out</text>

  <line class="edge-arrow" x1="288" y1="56" x2="392" y2="56"/>

  <rect class="node-focal" x="400" y="20" width="216" height="72" rx="36"/>
  <text class="t-l1" x="508" y="47" text-anchor="middle" dominant-baseline="central">Protocol &amp; Policy Gate</text>
  <text class="t-l4" x="508" y="68" text-anchor="middle" dominant-baseline="central">Lean 4: _meta, schema, auth</text>

  <line class="edge-arrow" x1="508" y1="100" x2="508" y2="156"/>

  <rect class="node-focal" x="400" y="164" width="216" height="72" rx="36"/>
  <text class="t-l1" x="508" y="191" text-anchor="middle" dominant-baseline="central">Verified Tool Kernel</text>
  <text class="t-l4" x="508" y="212" text-anchor="middle" dominant-baseline="central">Total handlers + invariants</text>

  <line class="edge-arrow" x1="392" y1="200" x2="288" y2="200"/>

  <rect class="node-step" x="64" y="164" width="216" height="72" rx="36"/>
  <text class="t-l1" x="172" y="191" text-anchor="middle" dominant-baseline="central">Verified Response</text>
  <text class="t-l4" x="172" y="212" text-anchor="middle" dominant-baseline="central">JSON-RPC + SEP-2133 receipt</text>

  <line class="edge-arrow" x1="172" y1="156" x2="172" y2="100"/>
</svg>
```

### What to verify at each layer
- **Wire parser & serializer:** Prove round-trip and totality (`parse (serialize res) = ok res`) for JSON-RPC 2.0 envelopes, `server/discover`, and `_meta` version/capability headers ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)).
- **Protocol & authorization gate:** Prove that unsupported `protocolVersion` values always emit `UnsupportedProtocolVersionError` ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)), and that no `tools/call` reaches a handler unless its arguments satisfy the tool's `inputSchema` predicate and policy checks.
- **Tool kernel & CI axioms:** Prove domain invariants on pure/total handlers (returning `isError: true` on domain failures) with zero `sorry` and `#print axioms` verification in CI; if you need C11 for raw speed, run a differential verifier comparing the C11 runtime against the Lean 4 reference semantics.
- **Verifiable receipts via SEP-2133:** Attach execution/attestation receipts inside a vendor-namespaced **SEP-2133** extension in `_meta` so standard MCP hosts ignore them while your own host can verify them ([SEP-2133](https://modelcontextprotocol.io/seps/2133-extensions)).

---

## Turn 10

### User
could i create an mcp that's just a bunch of taste-dictating parameters on the backend?

### Assistant
**Yes—an MCP server can act purely as a centralized "taste & policy engine" on the backend**, and it maps cleanly onto MCP's three core primitives ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)):

- **As `Resources` (read-only context):** Expose your taste parameters as addressable URIs (e.g., `taste://architecture/invariants` or `taste://ui/tokens`) so any connected host can attach them on demand ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)).
- **As `Prompts` (reusable templates):** Bundle parameter sets into user-triggered workflow templates that inject your exact rules into a session ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)).
- **As `Tools` (on-demand lookup & enforcement):** Expose a `get_taste_rules(domain)` tool so the model only fetches the slice it needs for the current task—plus an optional `check_against_taste(candidate)` tool that scores or rejects outputs deterministically ([Client Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices)).

### Two design tips so it works well in practice
- **Pair steering with a deterministic check:** Textual taste parameters alone are soft guidance—LLMs can still drift. Adding a validator tool that returns structured violations (or `isError: true`) turns taste into an enforceable feedback loop ([Build an MCP Client](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-client)).
- **Scope parameters by domain:** Keep each resource or tool response focused on one domain (code style, API shape, visual tokens) rather than dumping a massive global config into context all at once ([Client Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices)).

---

## Turn 11

### User
not those kinds of parameters. what if we used the concept of an MCP to communicate with a model directly similar to weight-space programming?

### Assistant
**Not with standard MCP on closed-weight APIs—because standard MCP operates strictly in token and context space, never inside a model's weights or residual stream** ([MCP Architecture Overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)).

However, if you **self-host open-weights models** and control the inference engine, you *can* repurpose the MCP pattern—typed capability discovery, schema validation, and policy-gated RPC—as a **weight- and activation-space control plane** wired directly into the forward pass:

```svg
<svg viewBox="0 0 680 180" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --lumi-ink: light-dark(#000000, #e0e0e0);
      --lumi-muted: light-dark(#5f6368, #9aa0a6);
      --lumi-dim: light-dark(#f2f0f0, #242528);
      --lumi-container: light-dark(#e8e6e6, #2d2f33);
      --lumi-outline: light-dark(#727676, #9a9b9c);
      --lumi-accent-bg: light-dark(#dcf1ff, #192967);
      --lumi-primary: light-dark(#3186ff, #9dd2ff);
      --lumi-sans: 'Google Sans Flex', var(--font-family, 'Google Sans', sans-serif);
      --lumi-mono: 'Google Sans Code', ui-monospace, monospace;
    }
    text { font-weight: 400; stroke: none; }
    .t-l1 { font-family: var(--lumi-sans); font-size: 15px; fill: var(--lumi-ink); }
    .t-l4 { font-family: var(--lumi-sans); font-size: 13px; fill: var(--lumi-muted); }
    .node-step { fill: var(--lumi-dim); stroke: none; }
    .node-focal { fill: var(--lumi-accent-bg); stroke: var(--lumi-primary); stroke-width: 1.25; }
    .node-store { fill: var(--lumi-container); stroke: var(--lumi-outline); stroke-width: 1; }
    .edge-arrow { fill: none; stroke: var(--lumi-ink); stroke-width: 1.3; stroke-linecap: round; stroke-dasharray: 0 4; marker-end: url(#lumi-caret-ws); }
  </style>
  <defs>
    <marker id="lumi-caret-ws" viewBox="0 0 10 10" refX="7.5" refY="5" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" orient="auto">
      <path d="M 3 1.2 L 7.5 5 L 3 8.8" fill="none" stroke="var(--lumi-ink)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <rect class="node-step" x="24" y="54" width="176" height="72" rx="36"/>
  <text class="t-l1" x="112" y="81" text-anchor="middle" dominant-baseline="central">MCP Control Plane</text>
  <text class="t-l4" x="112" y="102" text-anchor="middle" dominant-baseline="central">Typed RPC &amp; bounds</text>

  <line class="edge-arrow" x1="208" y1="90" x2="244" y2="90"/>

  <rect class="node-focal" x="252" y="54" width="176" height="72" rx="36"/>
  <text class="t-l1" x="340" y="81" text-anchor="middle" dominant-baseline="central">Inference Runtime</text>
  <text class="t-l4" x="340" y="102" text-anchor="middle" dominant-baseline="central">vLLM / custom forward</text>

  <line class="edge-arrow" x1="436" y1="90" x2="472" y2="90"/>

  <rect class="node-store" x="480" y="54" width="176" height="72" rx="36"/>
  <text class="t-l1" x="568" y="81" text-anchor="middle" dominant-baseline="central">Weight / Latent Space</text>
  <text class="t-l4" x="568" y="102" text-anchor="middle" dominant-baseline="central">LoRA, RepE, sampler</text>
</svg>
```

### What you can actually modulate this way
- **Dynamic Multi-LoRA routing:** Expose `load_lora` / `select_adapter` as schema-validated operations that swap low-rank adapter matrices (`B(Ax)`) per request against a shared frozen base model, as supported in [vLLM Multi-LoRA serving](https://docs.vllm.ai/en/latest/features/lora/) ([vLLM Multi-LoRA Architecture](https://ashishsrivastav.com/blog/vllm-multi-lora-adapters-serving)).
- **Activation steering (Representation Engineering):** Expose layer-targeted steering vectors or Sparse Autoencoder (SAE) feature clamps (`steer_layer(layer, vector_id, coeff)`) that add or project concept directions directly onto hidden states during the forward pass without spending context tokens ([Representation Engineering Survey](https://arxiv.org/html/2502.17601v1), [SPARE SAE Steering](https://aclanthology.org/2025.naacl-long.264.pdf)).
- **Sampler & logit-level constraints:** Toggle grammar masks or logit biases per request at the decoding boundary.

### Key constraints & where formal verification fits
- **Nonlinear interference:** Stacking multiple steering vectors or LoRA adapters simultaneously can interfere unpredictably and degrade coherence or safety ([Representation Engineering Survey](https://arxiv.org/html/2502.17601v1)).
- **High-privilege attack surface:** Runtime LoRA loading is explicitly flagged as unsafe outside isolated, trusted environments ([vLLM LoRA Docs](https://docs.vllm.ai/en/latest/features/lora/)), and steering vectors themselves form an adversarial attack surface ([Steering Vectors Attack Surface](https://arxiv.org/html/2606.05958v1)).
- **What you can formally verify:** You can verify the **control-plane invariants** in Lean 4—proving that only signed adapter hashes load, layer indices are in bounds, and steering coefficients stay within calibrated norms—even though the neural forward pass itself remains empirical.

---

## Turn 12

### User
can i get this entire conversation with all texts, links, inline diagrams, code, and everything else - package together and exported please? can be to google drive or in any format, whatever works best

### Assistant
I've packaged the full conversation—including all five vector diagrams, the SEP-1686 timeline, the compatibility table, and clickable source links—into an 8-page PDF (`mcp-architecture-and-verification-guide.pdf`).
