"""Strict, portable source-manifest checks; no claim of binary reproducibility.

After reviewing a source change, run ``python3 -m mep.integrity --write --root <ethos>``
and review the manifest diff with the source diff. This is a consistency check
against a repository-owned manifest, not independent approval or authenticity.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def confined_path(root: Path, relative: str) -> tuple[Path | None, str | None]:
    parts = relative.replace("\\", "/").split("/")
    if not relative or relative.startswith("/") or ".." in parts:
        return None, "absolute_empty_or_parent_path"
    if "\\" in relative or any(p in ("", ".") for p in parts):
        return None, "noncanonical_path"
    target = root / relative
    try:
        target.resolve().relative_to(root.resolve())
    except (ValueError, OSError, RuntimeError):
        return None, "escapes_root"
    return target, None


SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}


def manifest_entries(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        parts = rel.split("/")
        if any(p in SKIP_DIRS for p in parts):
            continue
        if rel == "SHA256SUMS":
            continue
        yield rel, path


def write_manifest(root: Path) -> int:
    root = root.resolve()
    lines = []
    for rel, path in manifest_entries(root):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {rel}\n")
    (root / "SHA256SUMS").write_text("".join(lines), encoding="utf-8")
    return len(lines)


def verify_manifest(root: Path, manifest: Path | None = None) -> dict:
    root = root.resolve()
    manifest = manifest or root / "SHA256SUMS"
    result = {
        "manifest_present": manifest.is_file(),
        "manifest_sha256": None,
        "files_verified": 0,
        "mismatched_files": [],
        "missing_files": [],
        "unconfined_paths": [],
        "malformed_lines": [],
        "unlisted_files": [],
        "ok": False,
    }
    if not manifest.is_file():
        return result
    raw = manifest.read_bytes()
    result["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
    listed: set[str] = set()
    for line in raw.decode("utf-8", errors="replace").splitlines():
        line = line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            result["malformed_lines"].append(line)
            continue
        digest, rel = parts
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            result["malformed_lines"].append(line)
            continue
        target, error = confined_path(root, rel)
        if error:
            result["unconfined_paths"].append({"path": rel, "error": error})
            continue
        listed.add(rel)
        if not target.is_file():
            result["missing_files"].append(rel)
            continue
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            result["mismatched_files"].append(rel)
        else:
            result["files_verified"] += 1
    for rel, _ in manifest_entries(root):
        if rel not in listed:
            result["unlisted_files"].append(rel)
    result["ok"] = not any(
        result[key]
        for key in ("mismatched_files", "missing_files", "unconfined_paths", "malformed_lines")
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mep.integrity", description="Verify or write the SHA256SUMS manifest.")
    parser.add_argument("--root", default=".", help="Ethos root (default: current directory)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Rewrite SHA256SUMS from the tree")
    mode.add_argument("--verify", action="store_true", help="Verify the tree against SHA256SUMS")
    args = parser.parse_args(argv)
    root = Path(args.root)
    if args.write:
        count = write_manifest(root)
        print(f"wrote {count} entries to {root / 'SHA256SUMS'}")
        return 0
    report = verify_manifest(root)
    import json

    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
