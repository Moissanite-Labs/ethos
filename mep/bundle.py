"""Portable ethos export bundles.

An export is a directory with the owner's documents, the canonical revision
records, pending proposals, and (flagged as a local trust artifact) the
approvals ledger. It carries a manifest of SHA-256 hashes so a recipient can
check what they received. Publication is never implied: copying an export
elsewhere is the owner's explicit act.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import MEP_VERSION, SPEC_VERSION
from .ethos import load_ethos
from .revisions import APPROVALS_FILE, load_graph


def export_bundle(root: Path | str, dest: Path | str) -> dict[str, Any]:
    root = Path(root).resolve()
    dest = Path(dest).resolve()
    if dest.exists() and any(dest.iterdir()):
        raise ValueError(f"export destination must be empty or absent: {dest}")
    try:
        dest.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("export destination must not live inside the ethos root")

    ethos = load_ethos(root)
    graph = load_graph(root)
    if graph["errors"]:
        raise ValueError("refusing to export a broken graph: " + "; ".join(graph["errors"]))

    documents_dir = dest / "documents"
    copied: list[str] = []
    for doc in ethos.documents:
        source = root / doc.path
        target = documents_dir / doc.path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied.append(doc.path)

    revisions_dir = dest / "revisions"
    revisions_dir.mkdir(parents=True, exist_ok=True)
    for record in graph["revisions"]:
        (revisions_dir / f"{record['revision_id']}.json").write_text(
            json.dumps({k: v for k, v in record.items() if k != "_file"}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    proposals_dir = dest / "proposals"
    if graph["proposals"]:
        proposals_dir.mkdir(parents=True, exist_ok=True)
        for record in graph["proposals"]:
            (proposals_dir / f"{record['revision_id']}.json").write_text(
                json.dumps({k: v for k, v in record.items() if k != "_file"}, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

    approvals_file = root / ".mep" / APPROVALS_FILE
    approvals_copied = False
    if approvals_file.is_file():
        shutil.copyfile(approvals_file, dest / APPROVALS_FILE)
        approvals_copied = True

    metadata = ethos.metadata if isinstance(ethos.metadata, dict) else {}
    (dest / "EXPORT.md").write_text(
        f"# Ethos export\n\n"
        f"- Name: {ethos.name}\n"
        f"- Exported (UTC): {datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- MEP version: {MEP_VERSION}\n"
        f"- Revision schema: {SPEC_VERSION}\n"
        f"- Documents: {len(copied)}\n"
        f"- Revisions: {len(graph['revisions'])}\n"
        f"- Pending proposals: {len(graph['proposals'])}\n"
        f"- Approvals ledger included: {'yes (local trust artifact, not part of the wire format)' if approvals_copied else 'no'}\n\n"
        "This export is private by default. Copying it elsewhere is the owner's\n"
        "explicit act. Ethos text is context, not authority; the recipient's\n"
        "harness owes the same authorization rules to these records as to any\n"
        "other input. Verify MANIFEST.sha256 before trusting the contents.\n",
        encoding="utf-8",
    )

    import hashlib

    manifest_lines: list[str] = []
    for path in sorted(dest.rglob("*")):
        if not path.is_file() or path.name == "MANIFEST.sha256":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_lines.append(f"{digest}  {path.relative_to(dest).as_posix()}\n")
    (dest / "MANIFEST.sha256").write_text("".join(manifest_lines), encoding="utf-8")
    manifest_sha256 = hashlib.sha256((dest / "MANIFEST.sha256").read_bytes()).hexdigest()

    return {
        "destination": str(dest),
        "documents": copied,
        "revisions": len(graph["revisions"]),
        "proposals": len(graph["proposals"]),
        "approvals_included": approvals_copied,
        "manifest_sha256": manifest_sha256,
    }
