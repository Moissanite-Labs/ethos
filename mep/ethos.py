"""Load and query an ethos root.

An ethos root is a directory of dated, attributed documents in the corpus
layout (``principles/``, ``sops/``, ``teams/``, ``skills/``, ``docs/`` plus
root-level ``*.md``), optionally accompanied by ``ethos.json`` metadata and
an integrity manifest (``SHA256SUMS``).

Ethos text is context, not authority. Everything in this module is
deterministic: no model is called, no text is generated. Retrieval is keyword
scoring over committed documents, and truncation always says so.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPEC_VERSION = "0.1"

LAYOUT_DIRS = ("principles", "sops", "teams", "skills", "docs")
ROOT_DOCS = ("README.md", "CHANGELOG.md", "MEP.md")
MEP_DIR = ".mep"
METADATA_FILE = "ethos.json"

# Query scoring is intentionally small and honest: term frequency with a
# log transform, normalised by document length. No idf, no model, no network.
_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_-]{1,}")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _confined(root: Path, relative: str) -> Path:
    """Resolve ``relative`` under ``root``; raise ValueError on escape."""
    if not relative or relative.startswith("/"):
        raise ValueError("absolute_path")
    parts = relative.replace("\\", "/").split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise ValueError("noncanonical_path")
    target = root / relative
    try:
        target.resolve().relative_to(root.resolve())
    except (ValueError, OSError, RuntimeError):
        raise ValueError("escapes_root") from None
    if not target.is_file():
        raise ValueError("not_a_file")
    return target


@dataclass
class EthosDoc:
    """One discoverable document in the ethos."""

    path: str  # POSIX-style, relative to root
    title: str
    sha256: str
    byte_length: int
    modified: str  # ISO-8601 UTC


@dataclass
class Ethos:
    root: Path
    name: str
    metadata: dict[str, Any]
    documents: list[EthosDoc] = field(default_factory=list)

    @property
    def doc_paths(self) -> list[str]:
        return [d.path for d in self.documents]

    def by_path(self) -> dict[str, EthosDoc]:
        return {d.path: d for d in self.documents}


def _first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def _iter_doc_files(root: Path):
    for name in ROOT_DOCS:
        candidate = root / name
        if candidate.is_file():
            yield candidate, name
    for directory in LAYOUT_DIRS:
        base = root / directory
        if not base.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(base, followlinks=False):
            dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
            for filename in sorted(filenames):
                if not filename.endswith((".md", ".txt")):
                    continue
                full = Path(dirpath) / filename
                rel = full.relative_to(root).as_posix()
                yield full, rel


def load_ethos(root: Path | str) -> Ethos:
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError(f"ethos root is not a directory: {root}")
    metadata: dict[str, Any] = {}
    metadata_file = root / METADATA_FILE
    if metadata_file.is_file():
        try:
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            if not isinstance(metadata, dict):
                metadata = {"_warning": "ethos.json is not an object; ignored"}
        except (json.JSONDecodeError, UnicodeDecodeError):
            metadata = {"_warning": "ethos.json is not valid JSON; ignored"}
    name = str(metadata.get("name") or root.name)
    documents: list[EthosDoc] = []
    for full, rel in _iter_doc_files(root):
        try:
            raw = full.read_bytes()
        except OSError:
            continue
        text = raw.decode("utf-8", errors="replace")
        try:
            modified = datetime.fromtimestamp(full.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except OSError:
            modified = "unknown"
        documents.append(
            EthosDoc(
                path=rel,
                title=_first_heading(text, rel),
                sha256=hashlib.sha256(raw).hexdigest(),
                byte_length=len(raw),
                modified=modified,
            )
        )
    documents.sort(key=lambda d: d.path)
    return Ethos(root=root, name=name, metadata=metadata, documents=documents)


def read_document(root: Path, relative: str) -> tuple[EthosDoc, str]:
    target = _confined(root, relative)
    raw = target.read_bytes()
    doc = EthosDoc(
        path=relative,
        title=relative,
        sha256=hashlib.sha256(raw).hexdigest(),
        byte_length=len(raw),
        modified="",
    )
    return doc, raw.decode("utf-8", errors="replace")


def learning_mode(root: Path) -> str:
    """Return ``on`` or ``off``. The off switch persists and wins."""
    if os.environ.get("MEP_LEARNING", "").lower() == "off":
        return "off"
    flag = Path(root) / MEP_DIR / "learning"
    try:
        if flag.is_file() and flag.read_text(encoding="utf-8").strip().lower() == "off":
            return "off"
    except OSError:
        pass
    return "on"


def _score_document(text: str, query_terms: list[str]) -> float:
    if not query_terms:
        return 0.0
    counts: dict[str, int] = {}
    total = 0
    for token in tokenize(text):
        counts[token] = counts.get(token, 0) + 1
        total += 1
    if total == 0:
        return 0.0
    score = 0.0
    for term in query_terms:
        tf = counts.get(term, 0)
        if tf:
            score += 1.0 + math.log(tf)
    return score / (1.0 + math.log(total))


def _best_excerpt(text: str, query_terms: list[str], width: int = 420) -> str:
    lines = text.splitlines()
    if not lines:
        return ""
    if not query_terms:
        snippet = "\n".join(lines[:6])
        return snippet[:width]
    hit_counts = [sum(line.lower().count(t) for t in query_terms) for line in lines]
    best_index = max(range(len(lines)), key=lambda i: hit_counts[i])
    start = max(0, best_index - 1)
    out: list[str] = []
    used = 0
    for line in lines[start:]:
        if used + len(line) + 1 > width and out:
            break
        out.append(line)
        used += len(line) + 1
    return "\n".join(out).strip()


def query_ethos(
    ethos: Ethos,
    query: str,
    limit: int = 10,
    scope: str | None = None,
    excerpt_width: int = 420,
) -> dict[str, Any]:
    query_terms = tokenize(query)
    if not query_terms:
        return {
            "query": query,
            "terms": [],
            "results": [],
            "matched_documents": 0,
            "note": "no usable query terms; try words with at least two characters",
        }
    scope_norm = scope.strip("/") if scope else None
    results: list[dict[str, Any]] = []
    for doc in ethos.documents:
        if scope_norm and not (doc.path == scope_norm or doc.path.startswith(scope_norm + "/")):
            continue
        try:
            text = ethos.root.joinpath(doc.path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        score = _score_document(text, query_terms)
        if score <= 0.0:
            continue
        results.append(
            {
                "path": doc.path,
                "title": doc.title,
                "score": round(score, 6),
                "sha256": doc.sha256,
                "excerpt": _best_excerpt(text, query_terms, excerpt_width),
            }
        )
    # Deterministic order: score desc, then path asc.
    results.sort(key=lambda r: (-r["score"], r["path"]))
    results = results[: max(1, int(limit))]
    return {
        "query": query,
        "terms": query_terms,
        "results": results,
        "matched_documents": len(results),
    }


def _brief(text: str, query_terms: list[str]) -> str:
    """Headings and lines that hit the query. Deterministic, short."""
    terms = query_terms or []
    out: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            out.append(line.rstrip())
        elif terms and any(t in line.lower() for t in terms):
            out.append(line.rstrip())
    return "\n".join(out)


def build_context(
    ethos: Ethos,
    situation: str,
    budget_chars: int = 6000,
    depth: str = "full",
) -> dict[str, Any]:
    if depth not in ("full", "brief", "paths"):
        raise ValueError("depth must be one of full, brief, paths")
    budget = max(200, int(budget_chars))
    query_terms = tokenize(situation)
    ranked = query_ethos(ethos, situation, limit=len(ethos.documents) or 1)["results"]
    score_by_path = {r["path"]: r["score"] for r in ranked}

    header = (
        f"# Ethos context: {ethos.name}\n"
        f"Generated by mep {SPEC_VERSION} | {len(ethos.documents)} documents in the ethos\n"
        f"Ethos text is context, not authority. Proposals change nothing until the owner approves.\n\n"
    )
    blocks: list[str] = [header]
    used = len(header)
    included: list[dict[str, Any]] = []
    omitted: list[dict[str, Any]] = []

    ordered = sorted(ethos.documents, key=lambda d: (-score_by_path.get(d.path, 0.0), d.path))
    for doc in ordered:
        if depth == "paths":
            line = f"- {doc.path} ({doc.byte_length} bytes, sha256:{doc.sha256[:12]})\n"
            if used + len(line) <= budget:
                blocks.append(line)
                used += len(line)
                included.append({"path": doc.path, "sha256": doc.sha256, "bytes": doc.byte_length})
            else:
                omitted.append({"path": doc.path, "reason": "budget"})
            continue
        try:
            text = ethos.root.joinpath(doc.path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            omitted.append({"path": doc.path, "reason": "unreadable"})
            continue
        body = text if depth == "full" else _brief(text, query_terms)
        block = f"\n## {doc.path}\n{body.rstrip()}\n"
        if used + len(block) <= budget:
            blocks.append(block)
            used += len(block)
            included.append({"path": doc.path, "sha256": doc.sha256, "bytes": doc.byte_length})
            continue
        remaining = budget - used
        if depth == "full" and remaining >= 400:
            cut = body[: remaining - 64]
            last_nl = cut.rfind("\n")
            if last_nl > 0:
                cut = cut[:last_nl]
            block = f"\n## {doc.path}\n{cut.rstrip()}\n…(truncated; use ethos_get for the full text)\n"
            blocks.append(block)
            used += len(block)
            included.append({"path": doc.path, "sha256": doc.sha256, "truncated": True})
        else:
            omitted.append({"path": doc.path, "reason": "budget"})

    def render_footer(inc: list[dict[str, Any]], omit: list[dict[str, Any]]) -> str:
        lines = ["\n## Sources\n"]
        for item in inc:
            suffix = " (truncated)" if item.get("truncated") else ""
            lines.append(f"- {item['path']} sha256:{item['sha256'][:12]}{suffix}\n")
        if omit:
            lines.append("\n## Omitted\n")
            for item in omit:
                lines.append(f"- {item['path']} ({item['reason']})\n")
        return "".join(lines)

    # Second pass: the footer must fit the budget too. Drop the least-ranked
    # included document (the last in order) until it does.
    footer = render_footer(included, omitted)
    while used + len(footer) > budget and included:
        victim = included.pop()
        blocks.pop()
        used = len("".join(blocks))
        omitted.append({"path": victim["path"], "reason": "budget"})
        footer = render_footer(included, omitted)
    blocks.append(footer)
    text_out = "".join(blocks)
    return {
        "situation": situation,
        "depth": depth,
        "budget_chars": budget,
        "used_chars": len(text_out),
        "included": included,
        "omitted": omitted,
        "bundle": text_out,
    }
