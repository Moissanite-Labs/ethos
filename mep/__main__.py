"""MCP stdio entry point and JSON CLI for serving an ethos."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .server import dispatch_tool_call, serve_stdio


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mep",
        description="Serve an ethos over MCP (stdio), or query it from the command line.",
    )
    parser.add_argument("--root", default=None, help="Ethos root (default: MEP_ROOT or the current directory)")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("serve", help="Run MCP JSON-RPC over stdio (default)")
    for cmd, help_text in [
        ("capabilities", "Report server capabilities and ethos root status"),
        ("status", "Show the ethos panel (loaded, pending, integrity)"),
        ("heads", "Show causal heads, conflicts and pending proposals"),
        ("history", "Show revision records"),
    ]:
        sub.add_parser(cmd, help=help_text)
    p = sub.add_parser("integrity", help="Verify (default) or rewrite the SHA256SUMS manifest")
    p.add_argument("--write", action="store_true")
    sub.add_parser("list", help="List documents in the ethos").add_argument("--scope", default=None)
    p = sub.add_parser("get", help="Read one document")
    p.add_argument("path")
    p = sub.add_parser("query", help="Deterministic keyword query")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--scope", default=None)
    p = sub.add_parser("context", help="Compose a budgeted context bundle")
    p.add_argument("situation")
    p.add_argument("--budget", type=int, default=6000)
    p.add_argument("--depth", choices=["full", "brief", "paths"], default="full")
    args = parser.parse_args(argv)

    root = Path(args.root or os.environ.get("MEP_ROOT") or ".").resolve()
    if args.cmd in (None, "serve"):
        return serve_stdio(root)
    try:
        if args.cmd == "capabilities":
            tool, payload = "ethos_capabilities", {}
        elif args.cmd == "status":
            tool, payload = "ethos_status", {}
        elif args.cmd == "heads":
            tool, payload = "ethos_heads", {}
        elif args.cmd == "history":
            tool, payload = "ethos_history", {}
        elif args.cmd == "list":
            tool, payload = "ethos_list", ({"scope": args.scope} if args.scope else {})
        elif args.cmd == "get":
            tool, payload = "ethos_get", {"path": args.path}
        elif args.cmd == "query":
            tool, payload = "ethos_query", {"query": args.query, "limit": args.limit, **({"scope": args.scope} if args.scope else {})}
        elif args.cmd == "context":
            tool, payload = "ethos_context", {"situation": args.situation, "budget_chars": args.budget, "depth": args.depth}
        elif args.cmd == "integrity":
            tool, payload = "ethos_integrity", {"write": args.write}
        else:
            parser.error(f"unknown command {args.cmd}")
        out = dispatch_tool_call(tool, payload, root)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "command": args.cmd}), file=sys.stderr)
        return 2
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
