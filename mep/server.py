"""Standards-compliant MCP stdio JSON-RPC 2.0 server for the Model Ethos Protocol.

Derived from the soko-verified-mcp framework (ahrazzle/soko): stdlib-only
Python, dual newline-delimited / Content-Length framed stdio, structured
content on every tool call, and honest capability reporting. The ethos is
served as-is from an owner-controlled root directory.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple

from . import MEP_VERSION, SERVER_INFO, SERVER_INSTRUCTIONS, SPEC_VERSION, SUPPORTED_PROTOCOLS
from .ethos import build_context, load_ethos, query_ethos, read_document
from .bundle import export_bundle
from .integrity import verify_manifest, write_manifest
from .revisions import (
    correct,
    decide,
    drift_report,
    effective_preferences,
    graph_summary,
    load_approvals,
    load_graph,
    propose,
)

DEFAULT_INSTRUCTIONS = SERVER_INSTRUCTIONS


def _root() -> Path:
    return Path(os.environ.get("MEP_ROOT", ".")).resolve()


TOOLS: List[Dict[str, Any]] = [
    {
        "name": "ethos_capabilities",
        "title": "Report Server Capabilities & Ethos Root Status",
        "description": "Report MEP/spec versions, the ethos root in use, document counts, revision graph health, integrity manifest status and the learning switch. Never conflates a missing file with a healthy one.",
        "inputSchema": {"type": "object", "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "ethos_list",
        "title": "List Documents in the Ethos",
        "description": "List every discoverable document (principles/, sops/, teams/, skills/, docs/ and root-level *.md) with path, title, size, SHA-256 and modified time. Optionally limit to a sub-directory prefix.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scope": {"type": "string", "description": "Optional POSIX path prefix, e.g. 'sops' or 'teams/exo.md'."},
            },
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "ethos_get",
        "title": "Read One Document",
        "description": "Read a single document by POSIX path relative to the ethos root. Paths that escape the root are rejected. Returns text, SHA-256 and byte length.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "POSIX path relative to the ethos root, e.g. 'principles/ethos.md'."}},
            "required": ["path"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "ethos_query",
        "title": "Query the Ethos (Deterministic Keyword Search)",
        "description": "Score every document against the query terms (log-frequency, length-normalised) and return ranked paths with excerpts. No model is involved; the same query always returns the same ranking.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 10, "minimum": 1, "maximum": 100},
                "scope": {"type": "string", "description": "Optional POSIX path prefix to search within."},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "ethos_context",
        "title": "Compose a Budgeted Ethos Bundle for a Situation",
        "description": "Build a deterministic context bundle for a described situation: ranked documents included until the character budget runs out, a Sources section with SHA-256 pins, and an Omitted section listing what did not fit. depth=full includes whole documents; depth=brief keeps only headings and query-hitting lines; depth=paths lists provenance only.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "situation": {"type": "string", "description": "What the agent is about to do, in the owner's words or the harness's."},
                "budget_chars": {"type": "integer", "default": 6000, "minimum": 200, "maximum": 200000},
                "depth": {"type": "string", "enum": ["full", "brief", "paths"], "default": "full"},
            },
            "required": ["situation"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "ethos_status",
        "title": "Show the Ethos Panel (What Is Loaded, What Is Pending)",
        "description": "The panel: name and metadata, document and revision counts, contested or suppressed preferences, pending proposals, integrity manifest result, learning switch state, and drift heuristics. Says what it is doing and why; never applies anything.",
        "inputSchema": {"type": "object", "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "ethos_heads",
        "title": "Show Causal Heads, Conflicts and Pending Proposals",
        "description": "List the causal head of every preference, which preferences are contested (multiple active heads) or suppressed (rejection/deletion head), and which proposals await the owner's decision.",
        "inputSchema": {"type": "object", "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "ethos_history",
        "title": "Show the Revision History of the Ethos",
        "description": "Return the canonical revision records (optionally filtered to one preference_id) in topological order, without the records' payload data redacted beyond what the on-disk store holds. History is append-only; rejected and deleted revisions name their parents.",
        "inputSchema": {
            "type": "object",
            "properties": {"preference_id": {"type": "string"}},
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "ethos_propose",
        "title": "Propose a Preference Revision (Never Applies Alone)",
        "description": "Write a proposal into .mep/proposals/. A proposal never takes effect: the owner must approve it with ethos_decide or write an explicit revision with ethos_correct. Requires origin (explicit or inferred); inferred proposals require confidence between 0 and 1.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "statement": {"type": "string", "description": "One preference, in one sentence."},
                "origin": {"type": "string", "enum": ["explicit", "inferred"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1, "description": "Required when origin=inferred; forbidden otherwise."},
                "scope_contexts": {"type": "array", "items": {"type": "string", "minLength": 1}, "default": []},
                "source_kind": {"type": "string", "description": "e.g. user, observation, import."},
                "source_reference": {"type": "string", "description": "Opaque reference; avoid raw transcripts."},
                "owner_id": {"type": "string", "description": "Owner the proposal belongs to."},
                "author_id": {"type": "string", "description": "Who or what authored this revision."},
                "preference_id": {"type": "string", "description": "Existing preference this updates; omit to start a new one."},
            },
            "required": ["statement", "origin", "source_kind", "source_reference", "owner_id", "author_id"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "idempotentHint": False, "openWorldHint": False},
    },
    {
        "name": "ethos_decide",
        "title": "Owner Decision on a Proposal (Approve, Reject, Delete)",
        "description": "approve: the proposal becomes canonical and an approval is recorded. reject: a rejected revision is written naming all current heads. delete: a tombstone is written naming all current heads. History is never rewritten. The harness should confirm with the human before calling this.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_revision_id": {"type": "string"},
                "decision": {"type": "string", "enum": ["approve", "reject", "delete"]},
                "owner_id": {"type": "string"},
                "note": {"type": "string", "default": ""},
            },
            "required": ["target_revision_id", "decision", "owner_id"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "idempotentHint": False, "openWorldHint": False},
    },
    {
        "name": "ethos_correct",
        "title": "Owner Correction: Explicit Revision into the Canon",
        "description": "The owner's direct path. Write an explicit revision naming all current heads of the preference (or start a new preference). Use this when the human tells the harness what they actually want; it supersedes without erasing history.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "statement": {"type": "string"},
                "scope_contexts": {"type": "array", "items": {"type": "string", "minLength": 1}, "default": []},
                "source_kind": {"type": "string", "default": "user"},
                "source_reference": {"type": "string", "default": "owner-session"},
                "owner_id": {"type": "string"},
                "preference_id": {"type": "string", "description": "Existing preference to supersede; omit to start a new one."},
            },
            "required": ["statement", "owner_id"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "idempotentHint": False, "openWorldHint": False},
    },
    {
        "name": "ethos_export",
        "title": "Export a Portable Ethos Bundle",
        "description": "Write a portable bundle: documents/, revisions/, pending proposals/, approvals.json (flagged as a local trust artifact), EXPORT.md and MANIFEST.sha256. Refuses to run on a broken graph. Copying the bundle elsewhere is the owner's explicit act; export implies nothing about publication.",
        "inputSchema": {
            "type": "object",
            "properties": {"dest": {"type": "string", "description": "Empty-or-absent directory to write the bundle to."}},
            "required": ["dest"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "idempotentHint": False, "openWorldHint": False},
    },
    {
        "name": "ethos_integrity",
        "title": "Verify or Rewrite the SHA256SUMS Manifest",
        "description": "Verify the ethos tree against SHA256SUMS (default), or rewrite the manifest (write=true) after a reviewed change. A consistency check against a repository-owned manifest, not independent approval.",
        "inputSchema": {
            "type": "object",
            "properties": {"write": {"type": "boolean", "default": False}},
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "idempotentHint": True, "openWorldHint": False},
    },
]

RESOURCES: List[Dict[str, Any]] = [
    {
        "uri": "ethos://about",
        "name": "About this MEP server",
        "description": "Server, MEP and revision schema versions, and the home repository.",
        "mimeType": "application/json",
    },
    {
        "uri": "ethos://status",
        "name": "Ethos status panel",
        "description": "Loaded metadata, counts, integrity result, learning switch and drift heuristics.",
        "mimeType": "application/json",
    },
    {
        "uri": "ethos://revisions",
        "name": "Effective preferences",
        "description": "What applies, what is contested, what is pending owner decision.",
        "mimeType": "application/json",
    },
]

PROMPTS: List[Dict[str, Any]] = [
    {
        "name": "reflect",
        "description": "End-of-session capture: what did you learn, decide or verify; where does it live now; who can build on it next.",
        "arguments": [
            {"name": "situation", "description": "What was being worked on", "required": True},
        ],
    },
    {
        "name": "review",
        "description": "Review an artifact against the ethos: which principles speak to it, what is missing, what should be captured.",
        "arguments": [
            {"name": "artifact", "description": "The artifact under review (text or a path in the ethos)", "required": True},
        ],
    },
]


def _learning_block(root: Path) -> Optional[Dict[str, Any]]:
    state = os.environ.get("MEP_LEARNING", "").lower() == "off"
    flag = root / ".mep" / "learning"
    try:
        if flag.is_file() and flag.read_text(encoding="utf-8").strip().lower() == "off":
            state = True
    except OSError:
        pass
    if state:
        return {
            "learning": "off",
            "written": False,
            "message": "learning is off for this ethos; nothing was written. Turn it on with the owner (remove .mep/learning or set MEP_LEARNING != off).",
        }
    return None


def _status(root: Path) -> Dict[str, Any]:
    ethos = load_ethos(root)
    graph = load_graph(root)
    approvals = load_approvals(root)
    summary = graph_summary(graph)
    effective = effective_preferences(graph, approvals)
    drift = drift_report(root, graph, approvals)
    integrity = verify_manifest(root) if (root / "SHA256SUMS").is_file() else None
    return {
        "name": ethos.name,
        "metadata": ethos.metadata,
        "mep_version": MEP_VERSION,
        "spec_version": SPEC_VERSION,
        "root": str(root),
        "documents": len(ethos.documents),
        "document_paths": ethos.doc_paths,
        "revisions": summary,
        "effective": effective,
        "integrity": integrity,
        "learning": "off" if _learning_block(root) else "on",
        "drift": drift,
    }


def dispatch_tool_call(name: str, args: Dict[str, Any], root: Optional[Path] = None) -> Dict[str, Any]:
    root = (root or _root()).resolve()
    if name == "ethos_capabilities":
        status = _status(root)
        return {
            "server": SERVER_INFO,
            "mep_version": MEP_VERSION,
            "spec_version": SPEC_VERSION,
            "root": str(root),
            "ethos_name": status["name"],
            "documents": status["documents"],
            "revisions": status["revisions"],
            "integrity_ok": (status["integrity"] or {}).get("ok") if status["integrity"] else "no manifest",
            "learning": status["learning"],
            "unbacked": [],
            "note": "All features are stdlib-only; no external backends are optional for this server.",
        }
    if name == "ethos_list":
        ethos = load_ethos(root)
        scope = (args.get("scope") or "").strip("/")
        docs = [
            {
                "path": d.path,
                "title": d.title,
                "bytes": d.byte_length,
                "sha256": d.sha256,
                "modified": d.modified,
            }
            for d in ethos.documents
            if not scope or d.path == scope or d.path.startswith(scope + "/")
        ]
        return {"documents": docs, "count": len(docs), "total": len(ethos.documents)}
    if name == "ethos_get":
        _, text = read_document(root, str(args["path"]))
        import hashlib

        return {"path": args["path"], "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "byte_length": len(text.encode("utf-8")), "text": text}
    if name == "ethos_query":
        ethos = load_ethos(root)
        return query_ethos(
            ethos,
            str(args["query"]),
            limit=int(args.get("limit", 10)),
            scope=args.get("scope"),
        )
    if name == "ethos_context":
        ethos = load_ethos(root)
        return build_context(
            ethos,
            str(args["situation"]),
            budget_chars=int(args.get("budget_chars", 6000)),
            depth=str(args.get("depth", "full")),
        )
    if name == "ethos_status":
        return _status(root)
    if name == "ethos_heads":
        graph = load_graph(root)
        approvals = load_approvals(root)
        from .revisions import heads as _heads

        per_pref = {
            pref: [h["revision_id"] for h in hs] for pref, hs in _heads(graph["revisions"]).items()
        }
        return {
            **graph_summary(graph),
            "heads": per_pref,
            "pending_proposals": [p["revision_id"] for p in graph["proposals"]],
            "approvals": len(approvals),
        }
    if name == "ethos_history":
        graph = load_graph(root)
        records = graph["revisions"] + graph["proposals"]
        preference_id = args.get("preference_id")
        if preference_id:
            records = [r for r in records if r["preference_id"] == preference_id]
        records = [{k: v for k, v in r.items() if k != "_file"} for r in records]
        return {"records": records, "count": len(records)}
    if name in ("ethos_propose", "ethos_decide", "ethos_correct"):
        blocked = _learning_block(root)
        if blocked is not None:
            return blocked
        if name == "ethos_propose":
            return propose(
                root,
                statement=str(args["statement"]),
                origin=str(args["origin"]),
                confidence=args.get("confidence"),
                scope_contexts=[str(c) for c in (args.get("scope_contexts") or [])],
                source_kind=str(args["source_kind"]),
                source_reference=str(args["source_reference"]),
                owner_id=str(args["owner_id"]),
                author_id=str(args["author_id"]),
                preference_id=args.get("preference_id"),
            )
        if name == "ethos_decide":
            return decide(
                root,
                target_revision_id=str(args["target_revision_id"]),
                decision=str(args["decision"]),
                owner_id=str(args["owner_id"]),
                note=str(args.get("note", "")),
            )
        return correct(
            root,
            statement=str(args["statement"]),
            scope_contexts=[str(c) for c in (args.get("scope_contexts") or [])],
            source_kind=str(args.get("source_kind", "user")),
            source_reference=str(args.get("source_reference", "owner-session")),
            owner_id=str(args["owner_id"]),
            preference_id=args.get("preference_id"),
        )
    if name == "ethos_export":
        return export_bundle(root, Path(str(args["dest"])).expanduser())
    if name == "ethos_integrity":
        if bool(args.get("write", False)):
            count = write_manifest(root)
            return {"written": True, "entries": count, "path": str(root / "SHA256SUMS")}
        return verify_manifest(root)
    raise KeyError(f"Unknown tool: {name}")


def _read_resource_content(uri: str, root: Path) -> Dict[str, Any]:
    if uri == "ethos://about":
        text = json.dumps(
            {
                "server": SERVER_INFO,
                "mep_version": MEP_VERSION,
                "spec_version": SPEC_VERSION,
                "repository": "https://github.com/Moissanite-Labs/ethos",
                "protocol": "MEP.md",
                "revision_schema": "v0.1/SPEC.md",
            },
            indent=2,
        )
        return {"uri": uri, "mimeType": "application/json", "text": text}
    if uri == "ethos://status":
        return {"uri": uri, "mimeType": "application/json", "text": json.dumps(_status(root), indent=2)}
    if uri == "ethos://revisions":
        graph = load_graph(root)
        approvals = load_approvals(root)
        effective = effective_preferences(graph, approvals)
        return {"uri": uri, "mimeType": "application/json", "text": json.dumps(effective, indent=2)}
    if uri.startswith("ethos://document/"):
        path = uri[len("ethos://document/") :]
        _, text = read_document(root, path)
        return {"uri": uri, "mimeType": "text/markdown", "text": text}
    raise KeyError(f"Unknown resource: {uri}")


def _get_prompt_messages(name: str, pargs: Dict[str, Any], root: Path) -> Dict[str, Any]:
    if name == "reflect":
        situation = str(pargs.get("situation", "the work just done"))
        text = (
            f"Before closing out: {situation}\n\n"
            "Ask and answer, in writing:\n"
            "1. What did I learn, decide or verify?\n"
            "2. Where does it live now? If the answer is 'nowhere', the work is not done.\n"
            "3. Who can build on it next?\n\n"
            "Capture the answer as a committed file, a corpus/ethos entry, or a proposal via ethos_propose. "
            "A proposal changes nothing until the owner decides."
        )
        return {"description": "End-of-session capture", "messages": [{"role": "user", "content": {"type": "text", "text": text}}]}
    if name == "review":
        artifact = str(pargs.get("artifact", ""))
        ethos = load_ethos(root)
        doc_list = "\n".join(f"- {d.path}: {d.title}" for d in ethos.documents)
        text = (
            f"Review this artifact against the ethos:\n\n{artifact}\n\n"
            f"The ethos holds these documents:\n{doc_list}\n\n"
            "For each, say whether it speaks to the artifact and how. Flag anything missing. "
            "Do not invent rules; if something is unclear, propose it with ethos_propose and let the owner decide."
        )
        return {"description": "Review against the ethos", "messages": [{"role": "user", "content": {"type": "text", "text": text}}]}
    raise KeyError(f"Unknown prompt: {name}")


def handle_jsonrpc_message(msg: Dict[str, Any], root: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    root = (root or _root()).resolve()
    method = msg.get("method")
    msg_id = msg.get("id")
    params = msg.get("params") or {}

    if msg_id is None:
        return None

    if method == "initialize":
        req_ver = params.get("protocolVersion", "2025-03-26")
        neg_ver = req_ver if req_ver in SUPPORTED_PROTOCOLS else "2025-03-26"
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": neg_ver,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "prompts": {"listChanged": False},
                },
                "serverInfo": SERVER_INFO,
                "instructions": DEFAULT_INSTRUCTIONS,
            },
        }

    if method == "server/discover":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersions": SUPPORTED_PROTOCOLS,
                "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                "serverInfo": SERVER_INFO,
                "instructions": DEFAULT_INSTRUCTIONS,
            },
        }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments") or {}
        if not tool_name or not any(t["name"] == tool_name for t in TOOLS):
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32602, "message": f"Unknown tool: {tool_name!r}"},
            }
        try:
            payload = dispatch_tool_call(tool_name, tool_args, root)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(payload, indent=2)}],
                    "structuredContent": payload,
                    "isError": False,
                },
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps({"error": str(exc), "tool": tool_name})}],
                    "isError": True,
                },
            }

    if method == "resources/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"resources": RESOURCES}}

    if method == "resources/read":
        uri = params.get("uri", "")
        try:
            content = _read_resource_content(uri, root)
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"contents": [content]}}
        except (KeyError, ValueError) as exc:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32602, "message": str(exc)}}

    if method == "prompts/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"prompts": PROMPTS}}

    if method == "prompts/get":
        pname = params.get("name", "")
        pargs = params.get("arguments") or {}
        try:
            res = _get_prompt_messages(pname, pargs, root)
            return {"jsonrpc": "2.0", "id": msg_id, "result": res}
        except KeyError as exc:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32602, "message": str(exc)}}

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Method not found: {method!r}"},
    }


def _read_next_message(stream: BinaryIO) -> Optional[Tuple[Any, bool]]:
    """Read either a newline-delimited JSON-RPC message (MCP stdio standard) or a Content-Length framed message."""
    while True:
        line = stream.readline()
        if not line:
            return None
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower().startswith(b"content-length:"):
            length = int(stripped.split(b":", 1)[1].strip())
            while True:
                hdr = stream.readline()
                if not hdr or hdr in (b"\r\n", b"\n"):
                    break
            body = stream.read(length)
            return json.loads(body.decode("utf-8")), True
        return json.loads(stripped.decode("utf-8")), False


def _write_message(stream: BinaryIO, payload: Any, use_content_length: bool = False) -> None:
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if use_content_length:
        header = f"Content-Length: {len(encoded)}\r\n\r\n".encode("ascii")
        stream.write(header + encoded)
    else:
        stream.write(encoded + b"\n")
    stream.flush()


def serve_stdio(root: Optional[Path] = None) -> int:
    root = (root or _root()).resolve()
    stdin_bin = sys.stdin.buffer
    stdout_bin = sys.stdout.buffer

    while True:
        try:
            item = _read_next_message(stdin_bin)
        except Exception as exc:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc}"}}
            _write_message(stdout_bin, err, False)
            continue
        if item is None:
            break
        msg, use_cl = item
        if isinstance(msg, list):
            replies = [r for sub in msg if (r := handle_jsonrpc_message(sub, root)) is not None]
            if replies:
                _write_message(stdout_bin, replies, use_cl)
        elif isinstance(msg, dict):
            reply = handle_jsonrpc_message(msg, root)
            if reply is not None:
                _write_message(stdout_bin, reply, use_cl)
    return 0
