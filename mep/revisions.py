"""Preference revision graph: records, validation, heads, decisions.

Implements the local-store semantics of the Ethos v0.1 preference interchange
(``v0.1/SPEC.md``). The v0.1 schema describes one immutable revision; this
module adds the graph rules the spec requires: globally unique revision ids,
one owner per preference, parents that exist, no cycles, contested heads that
apply nothing, and owner approval tracked outside the record.

Authority model
---------------

- A **proposal** (in ``.mep/proposals/``) never applies on its own. Only
  records in ``.mep/revisions/`` can apply, and even then a causal head is
  not enough: an inferred head applies only if the owner approved it;
  otherwise the nearest applicable owner-confirmed explicit ancestor applies.
- **ethos_correct** is the owner's direct path: it writes an explicit
  revision straight into the canonical store.
- **ethos_decide** is how a proposal becomes canonical (approve) or ceases to
  apply (reject, delete). Rejection and deletion are new revisions that name
  all current heads as parents; history is never rewritten.

State layout under the root (all inside ``.mep/``)
--------------------------------------------------

- ``revisions/*.json``  canonical revision records (apply)
- ``proposals/*.json``  pending proposals (never apply)
- ``decided/*.json``    proposals the owner disposed of (audit archive)
- ``approvals.json``    owner approvals bound to (owner_id, preference_id, revision_id)
- ``learning``          the off switch; contains ``off`` to disable writes
"""

from __future__ import annotations

import json
import secrets
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPEC_VERSION = "0.1"

MEP_DIR = ".mep"
REVISIONS_DIR = "revisions"
PROPOSALS_DIR = "proposals"
DECIDED_DIR = "decided"
APPROVALS_FILE = "approvals.json"

ALLOWED_KEYS = {
    "schema_version",
    "preference_id",
    "revision_id",
    "parent_revision_ids",
    "owner_id",
    "author_id",
    "status",
    "origin",
    "statement",
    "confidence",
    "scope",
    "source",
}
REQUIRED_KEYS = {
    "schema_version",
    "preference_id",
    "revision_id",
    "parent_revision_ids",
    "owner_id",
    "author_id",
    "status",
}
STATUSES = {"active", "rejected", "deleted"}
ORIGINS = {"explicit", "inferred"}
PAYLOAD_KEYS = {"origin", "statement", "confidence", "scope", "source"}


def new_id(prefix: str) -> str:
    return f"{prefix}-{secrets.token_hex(6)}"


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_record(record: Any) -> list[str]:
    """Structural checks on one revision record. Empty list means valid."""
    if not isinstance(record, dict):
        return ["record must be an object"]
    errors: list[str] = []
    if REQUIRED_KEYS - record.keys():
        errors.append("missing required fields: " + ", ".join(sorted(REQUIRED_KEYS - record.keys())))
    if record.keys() - ALLOWED_KEYS:
        errors.append("unknown fields: " + ", ".join(sorted(record.keys() - ALLOWED_KEYS)))
    if record.get("schema_version") != SPEC_VERSION:
        errors.append("schema_version must be '0.1'")
    status = record.get("status")
    if not isinstance(status, str) or status not in STATUSES:
        errors.append("status must be one of active, rejected, deleted")
        status = None
    for key in ("preference_id", "revision_id", "owner_id", "author_id"):
        value = record.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"{key} must be a non-empty string")
    parents = record.get("parent_revision_ids")
    if not isinstance(parents, list) or any(not isinstance(p, str) or not p for p in parents):
        errors.append("parent_revision_ids must be a list of non-empty strings")
        parents = []
    else:
        if len(set(parents)) != len(parents):
            errors.append("parent_revision_ids must be unique")
        if status in ("rejected", "deleted") and not parents:
            errors.append("rejection or deletion requires at least one parent")
        if record.get("revision_id") in parents:
            errors.append("a revision must not name itself as a parent")
    if status in ("rejected", "deleted"):
        leaked = PAYLOAD_KEYS & record.keys()
        if leaked:
            errors.append("rejection or deletion carries preference data: " + ", ".join(sorted(leaked)))
        return errors
    for key in ("origin", "statement", "scope", "source"):
        if key not in record:
            errors.append(f"active revision missing {key}")
    origin = record.get("origin")
    if origin not in ORIGINS:
        errors.append("origin must be explicit or inferred")
    if not isinstance(record.get("statement"), str) or not record["statement"]:
        errors.append("statement must be a non-empty string")
    if origin == "inferred":
        confidence = record.get("confidence")
        if confidence is None:
            errors.append("inference requires confidence")
        elif isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append("confidence must be a number between 0 and 1")
    elif "confidence" in record:
        errors.append("explicit revisions must not carry confidence")
    scope = record.get("scope")
    if not isinstance(scope, dict) or set(scope) != {"contexts"}:
        errors.append("scope must be an object with exactly one key: contexts")
    else:
        contexts = scope.get("contexts")
        if (
            not isinstance(contexts, list)
            or any(not isinstance(c, str) or not c for c in contexts)
            or len(set(contexts)) != len(contexts)
        ):
            errors.append("scope.contexts must be a list of unique non-empty strings")
    source = record.get("source")
    if not isinstance(source, dict) or set(source) != {"kind", "reference"}:
        errors.append("source must be an object with exactly the keys kind and reference")
    else:
        for key in ("kind", "reference"):
            if not isinstance(source.get(key), str) or not source[key]:
                errors.append(f"source.{key} must be a non-empty string")
    return errors


def _store_dir(root: Path, name: str) -> Path:
    return Path(root) / MEP_DIR / name


def _read_records_dir(directory: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    if not directory.is_dir():
        return records, errors
    for path in sorted(directory.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
            errors.append(f"{path.name}: unreadable record ({exc})")
            continue
        problem = validate_record(record)
        if problem:
            errors.append(f"{path.name}: " + "; ".join(problem))
            continue
        record = dict(record)
        record["_file"] = path.name
        records.append(record)
    return records, errors


def load_graph(root: Path | str) -> dict[str, Any]:
    """Load revisions, proposals and the decided archive; fail closed.

    The decided archive holds proposals the owner dispositioned (approved to
    canon, rejected, or superseded by a correction). Those records stay in the
    graph so supersession edges remain valid, but they never apply on their
    own and never appear as pending.
    """
    root = Path(root)
    revisions, rev_errors = _read_records_dir(_store_dir(root, REVISIONS_DIR))
    proposals, prop_errors = _read_records_dir(_store_dir(root, PROPOSALS_DIR))
    decided, dec_errors = _read_records_dir(_store_dir(root, DECIDED_DIR))
    for record in decided:
        record["_archived"] = True
    errors = (
        [f"revisions: {e}" for e in rev_errors]
        + [f"proposals: {e}" for e in prop_errors]
        + [f"decided: {e}" for e in dec_errors]
    )
    graph_records = revisions + proposals + decided
    by_id: dict[str, dict[str, Any]] = {}
    for record in graph_records:
        rid = record["revision_id"]
        if rid in by_id:
            errors.append(f"duplicate revision_id {rid!r} in {by_id[rid]['_file']} and {record['_file']}")
        else:
            by_id[rid] = record
    owners: dict[str, str] = {}
    for record in graph_records:
        owner = owners.setdefault(record["preference_id"], record["owner_id"])
        if owner != record["owner_id"]:
            errors.append(
                f"preference {record['preference_id']!r} has inconsistent owner_id "
                f"({owner!r} vs {record['owner_id']!r})"
            )
    pref_by_id = {record["revision_id"]: record["preference_id"] for record in graph_records}
    for record in graph_records:
        for parent in record["parent_revision_ids"]:
            if parent not in pref_by_id:
                errors.append(f"{record['revision_id']!r}: unknown parent {parent!r}")
            elif pref_by_id[parent] != record["preference_id"]:
                errors.append(f"{record['revision_id']!r}: parent {parent!r} belongs to a different preference")
    # Cycle check over the full graph (Kahn's algorithm).
    indegree = {rid: 0 for rid in by_id}
    children: dict[str, list[str]] = {rid: [] for rid in by_id}
    for record in graph_records:
        for parent in record["parent_revision_ids"]:
            if parent in indegree:
                indegree[record["revision_id"]] += 1
                children[parent].append(record["revision_id"])
    queue = sorted(rid for rid, deg in indegree.items() if deg == 0)
    visited = 0
    while queue:
        current = queue.pop()
        visited += 1
        for child in children[current]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
        queue.sort()
    if visited != len(by_id):
        cyclic = sorted(rid for rid, deg in indegree.items() if deg > 0)
        errors.append("revision graph has a cycle involving: " + ", ".join(cyclic))
    return {
        "revisions": revisions,
        "proposals": proposals,
        "decided": decided,
        "errors": errors,
    }


def _all_records(graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Every record in the graph, all three stores."""
    return graph["revisions"] + graph["decided"] + graph["proposals"]


def _structure_records(graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Applied canon plus archived dispositions, used for graph structure.

    Pending proposals are deliberately excluded: they are not structure, they
    are overlay. Archiving moves a proposal into the structure where its
    supersession edges keep the graph valid.
    """
    return graph["revisions"] + graph["decided"]


def heads(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Causal heads per preference: records nobody supersedes.

    Archived (decided) records are not candidates. An archived record still
    supersedes its parents, but only once something else claims the
    archived record's position. A record the owner plainly declined claims
    nothing, so its supersession edge is void and the base preference resumes
    effect. A record superseded by a later correction or tombstone keeps its
    edge, so the whole chain resolves to a single head.
    """
    visible = [r for r in records if not r.get("_archived")]
    archived = [r for r in records if r.get("_archived")]
    superseded = {p for r in visible for p in r["parent_revision_ids"]}
    # Expand through archived records, each at most once, until no new parent
    # appears. An archived record superseded by something claims its parents.
    expanded: set[str] = set()
    queue = sorted(superseded)
    while queue:
        current = queue.pop(0)
        if current in expanded:
            continue
        expanded.add(current)
        for record in archived:
            if record["revision_id"] == current:
                for parent in record["parent_revision_ids"]:
                    if parent not in superseded:
                        superseded.add(parent)
                        queue.append(parent)
    per_pref: dict[str, list[dict[str, Any]]] = {}
    for record in visible:
        if record["revision_id"] not in superseded:
            per_pref.setdefault(record["preference_id"], []).append(record)
    for pref in per_pref:
        per_pref[pref].sort(key=lambda r: r["revision_id"])
    return per_pref


def load_approvals(root: Path | str) -> list[dict[str, Any]]:
    approvals_file = Path(root) / MEP_DIR / APPROVALS_FILE
    if not approvals_file.is_file():
        return []
    try:
        data = json.loads(approvals_file.read_text(encoding="utf-8"))
        entries = data.get("approvals", []) if isinstance(data, dict) else []
        return [e for e in entries if isinstance(e, dict)]
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return []


def _save_approvals(root: Path, approvals: list[dict[str, Any]]) -> None:
    approvals_file = Path(root) / MEP_DIR / APPROVALS_FILE
    approvals_file.parent.mkdir(parents=True, exist_ok=True)
    approvals_file.write_text(
        json.dumps({"schema": "mep-approvals-1", "approvals": approvals}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def is_approved(
    approvals: list[dict[str, Any]], owner_id: str, preference_id: str, revision_id: str
) -> bool:
    return any(
        a.get("owner_id") == owner_id
        and a.get("preference_id") == preference_id
        and a.get("revision_id") == revision_id
        for a in approvals
    )


def _ancestry(records: list[dict[str, Any]], start: dict[str, Any]):
    """Yield the start revision and its ancestors, nearest first."""
    by_id = {r["revision_id"]: r for r in records}
    queue = [start]
    seen: set[str] = set()
    while queue:
        current = queue.pop(0)
        if current["revision_id"] in seen:
            continue
        seen.add(current["revision_id"])
        yield current
        for parent in current["parent_revision_ids"]:
            ancestor = by_id.get(parent)
            if ancestor is not None:
                queue.append(ancestor)


def effective_preferences(graph: dict[str, Any], approvals: list[dict[str, Any]]) -> dict[str, Any]:
    """Resolve what applies, what is contested, what is pending."""
    structure = _structure_records(graph)
    proposals = graph["proposals"]
    rev_heads = heads(structure)
    out: dict[str, Any] = {}
    for pref, pref_heads in sorted(rev_heads.items()):
        if any(h["status"] in ("rejected", "deleted") for h in pref_heads):
            out[pref] = {"state": "suppressed", "reason": "rejection or deletion head", "heads": [h["revision_id"] for h in pref_heads]}
            continue
        active_heads = [h for h in pref_heads if h["status"] == "active" and not h.get("_archived")]
        if len(active_heads) > 1:
            out[pref] = {
                "state": "contested",
                "reason": "multiple active heads; the owner must resolve with ethos_correct or ethos_decide",
                "heads": [h["revision_id"] for h in active_heads],
            }
            continue
        if not active_heads:
            out[pref] = {"state": "suppressed", "reason": "no active head", "heads": [h["revision_id"] for h in pref_heads]}
            continue
        head = active_heads[0]
        if head["origin"] == "explicit":
            out[pref] = {"state": "applied", "revision_id": head["revision_id"], "origin": "explicit", "statement": head["statement"], "scope": head["scope"], "source": head["source"]}
            continue
        if is_approved(approvals, head["owner_id"], pref, head["revision_id"]):
            out[pref] = {
                "state": "applied",
                "revision_id": head["revision_id"],
                "origin": "inferred-approved",
                "statement": head["statement"],
                "scope": head["scope"],
                "source": head["source"],
                "confidence": head.get("confidence"),
            }
            continue
        # Unapproved inference: fall back to the nearest confirmed explicit or
        # approved ancestor, if any.
        for ancestor in _ancestry(structure, head):
            if ancestor["revision_id"] == head["revision_id"]:
                continue
            if ancestor["status"] != "active" or ancestor.get("_archived"):
                continue
            confirmed = ancestor["origin"] == "explicit" or is_approved(
                approvals, ancestor["owner_id"], pref, ancestor["revision_id"]
            )
            if confirmed:
                out[pref] = {
                    "state": "applied",
                    "revision_id": ancestor["revision_id"],
                    "origin": "explicit" if ancestor["origin"] == "explicit" else "inferred-approved",
                    "statement": ancestor["statement"],
                    "scope": ancestor["scope"],
                    "source": ancestor["source"],
                    "pending_proposal": head["revision_id"],
                }
                break
        else:
            out[pref] = {
                "state": "pending",
                "reason": "head is an unapproved inference and no confirmed ancestor exists",
                "heads": [head["revision_id"]],
            }
    result = {
        "preferences": out,
        "pending_proposals": [
            {
                "preference_id": p["preference_id"],
                "revision_id": p["revision_id"],
                "author_id": p["author_id"],
                "origin": p["origin"],
                "statement": p["statement"],
                "confidence": p.get("confidence"),
                "scope": p["scope"],
                "source": p["source"],
            }
            for p in proposals
        ],
        "errors": graph["errors"],
    }
    return result


def graph_summary(graph: dict[str, Any]) -> dict[str, Any]:
    """Counts and contested preferences, for status reporting."""
    all_records = _all_records(graph)
    structure = _structure_records(graph)
    rev_heads = heads(structure)
    contested = {
        pref: sorted(h["revision_id"] for h in hs)
        for pref, hs in rev_heads.items()
        if sum(1 for h in hs if h["status"] == "active" and not h.get("_archived")) > 1
    }
    suppressed = {
        pref: sorted(h["revision_id"] for h in hs)
        for pref, hs in rev_heads.items()
        if any(h["status"] in ("rejected", "deleted") for h in hs)
    }
    preferences = {r["preference_id"] for r in all_records}
    return {
        "revisions": len(graph["revisions"]),
        "decided": len(graph["decided"]),
        "proposals_pending": len(graph["proposals"]),
        "preferences": len(preferences),
        "contested": contested,
        "suppressed": suppressed,
        "errors": graph["errors"],
    }


def _current_head_ids(graph: dict[str, Any], preference_id: str) -> list[str]:
    combined = [r for r in _all_records(graph) if r["preference_id"] == preference_id]
    per_pref = heads(combined)
    return [h["revision_id"] for h in per_pref.get(preference_id, [])]


def drift_report(root: Path | str, graph: dict[str, Any], approvals: list[dict[str, Any]], max_pending_days: int = 14, stale_days: int = 180) -> dict[str, Any]:
    """Deterministic staleness heuristics, labelled as heuristics.

    No model is involved. These are prompts to the owner, not findings.
    """
    root = Path(root)
    now = datetime.now(tz=timezone.utc).timestamp()
    findings: list[dict[str, str]] = []
    for proposal in graph["proposals"]:
        path = _store_dir(root, PROPOSALS_DIR) / f"{proposal['revision_id']}.json"
        try:
            age_days = (now - path.stat().st_mtime) / 86400
        except OSError:
            continue
        if age_days > max_pending_days:
            findings.append(
                {
                    "kind": "proposal_pending",
                    "detail": f"{proposal['revision_id']} waited {int(age_days)} days for a decision",
                    "preference_id": proposal["preference_id"],
                }
            )
    summary = graph_summary(graph)
    for pref, members in summary["contested"].items():
        findings.append({"kind": "contested", "detail": f"{pref} has multiple active heads: {', '.join(members)}", "preference_id": pref})
    for pref, members in summary["suppressed"].items():
        findings.append({"kind": "suppressed", "detail": f"{pref} is suppressed by a rejection or deletion head: {', '.join(members)}", "preference_id": pref})
    revisions = graph["revisions"]
    if revisions:
        newest = 0.0
        for record in revisions:
            path = _store_dir(root, REVISIONS_DIR) / f"{record['revision_id']}.json"
            try:
                newest = max(newest, path.stat().st_mtime)
            except OSError:
                continue
        if newest and (now - newest) / 86400 > stale_days:
            findings.append(
                {
                    "kind": "stale",
                    "detail": f"no revision recorded in {int((now - newest) / 86400)} days; re-read or prune the ethos",
                    "preference_id": "",
                }
            )
    return {
        "heuristic": True,
        "findings": findings,
        "finding_count": len(findings),
        "note": "heuristics only; the owner decides what they mean",
    }


def _archive_superseded(root: Path, graph: dict[str, Any], parent_ids: list[str]) -> list[str]:
    """Move pending proposals named as parents into the decided archive.

    The new record names them as parents, so they are dispositioned; leaving
    them in proposals/ would make the pending list lie.
    """
    proposal_files = {p["revision_id"] for p in graph["proposals"]}
    archived: list[str] = []
    archive_dir = _store_dir(root, DECIDED_DIR)
    for pid in parent_ids:
        if pid in proposal_files:
            source = _store_dir(root, PROPOSALS_DIR) / f"{pid}.json"
            if source.is_file():
                archive_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(archive_dir / f"{pid}.json"))
                archived.append(pid)
    return archived


def _write_record(directory: Path, record: dict[str, Any]) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{record['revision_id']}.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def propose(
    root: Path | str,
    *,
    statement: str,
    origin: str,
    scope_contexts: list[str],
    source_kind: str,
    source_reference: str,
    owner_id: str,
    author_id: str,
    confidence: float | None = None,
    preference_id: str | None = None,
) -> dict[str, Any]:
    root = Path(root)
    if origin not in ORIGINS:
        raise ValueError("origin must be explicit or inferred")
    if not statement.strip():
        raise ValueError("statement must be non-empty")
    if not source_kind.strip() or not source_reference.strip():
        raise ValueError("source kind and reference are required")
    graph = load_graph(root)
    preference_id = preference_id or new_id("pref")
    known_prefs = {r["preference_id"] for r in _all_records(graph)}
    if preference_id not in known_prefs:
        parents: list[str] = []
    else:
        owners = {
            r["owner_id"]
            for r in _all_records(graph)
            if r["preference_id"] == preference_id
        }
        if owners != {owner_id}:
            raise ValueError(f"preference_id {preference_id!r} exists under a different owner")
        parents = _current_head_ids(graph, preference_id)
    revision_id = new_id("rev")
    record: dict[str, Any] = {
        "schema_version": SPEC_VERSION,
        "preference_id": preference_id,
        "revision_id": revision_id,
        "parent_revision_ids": parents,
        "owner_id": owner_id,
        "author_id": author_id,
        "status": "active",
        "origin": origin,
        "statement": statement.strip(),
        "scope": {"contexts": list(dict.fromkeys(scope_contexts))},
        "source": {"kind": source_kind.strip(), "reference": source_reference.strip()},
    }
    if origin == "inferred":
        if confidence is None:
            raise ValueError("inferred proposals require confidence")
        record["confidence"] = confidence
    elif confidence is not None:
        raise ValueError("explicit proposals must not carry confidence")
    problems = validate_record(record)
    if problems:
        raise ValueError("invalid record: " + "; ".join(problems))
    path = _write_record(_store_dir(root, PROPOSALS_DIR), record)
    return {"proposal": record, "path": str(path.relative_to(root)), "parent_revision_ids": parents}


def correct(
    root: Path | str,
    *,
    statement: str,
    scope_contexts: list[str],
    source_kind: str,
    source_reference: str,
    owner_id: str,
    preference_id: str | None = None,
) -> dict[str, Any]:
    """The owner's direct path: write an explicit revision into the canon."""
    root = Path(root)
    graph = load_graph(root)
    preference_id = preference_id or new_id("pref")
    parents = _current_head_ids(graph, preference_id) if preference_id_exists(graph, preference_id) else []
    record: dict[str, Any] = {
        "schema_version": SPEC_VERSION,
        "preference_id": preference_id,
        "revision_id": new_id("rev"),
        "parent_revision_ids": parents,
        "owner_id": owner_id,
        "author_id": owner_id,
        "status": "active",
        "origin": "explicit",
        "statement": statement.strip(),
        "scope": {"contexts": list(dict.fromkeys(scope_contexts))},
        "source": {"kind": source_kind.strip() or "user", "reference": source_reference.strip() or "owner-session"},
    }
    problems = validate_record(record)
    if problems:
        raise ValueError("invalid record: " + "; ".join(problems))
    archived = _archive_superseded(root, graph, parents)
    path = _write_record(_store_dir(root, REVISIONS_DIR), record)
    return {
        "revision": record,
        "path": str(path.relative_to(root)),
        "parent_revision_ids": parents,
        "archived_proposals": archived,
    }


def preference_id_exists(graph: dict[str, Any], preference_id: str) -> bool:
    return any(
        r["preference_id"] == preference_id for r in _all_records(graph)
    )


def decide(
    root: Path | str,
    *,
    target_revision_id: str,
    decision: str,
    owner_id: str,
    note: str = "",
) -> dict[str, Any]:
    """Owner decision on a proposal (or applied revision).

    decision must be one of:
      approve  - the proposal becomes canonical; approval is recorded
      decline  - the proposal is archived, nothing changes; the underlying
                 preference keeps whatever effect it had
      reject   - a rejected revision is written naming all current heads;
                 the preference is suppressed until you reactivate it with
                 ethos_correct naming these heads as parents
      delete   - a tombstone is written naming all current heads; same
                 suppression semantics, distinct state
    """
    root = Path(root)
    if decision not in ("approve", "decline", "reject", "delete"):
        raise ValueError("decision must be approve, decline, reject or delete")
    graph = load_graph(root)
    proposals = {p["revision_id"]: p for p in graph["proposals"]}
    applied = {r["revision_id"]: r for r in graph["revisions"]}
    if target_revision_id in proposals:
        target = proposals[target_revision_id]
        target_is_proposal = True
    elif target_revision_id in applied:
        target = applied[target_revision_id]
        target_is_proposal = False
    else:
        raise ValueError(f"unknown revision_id {target_revision_id!r}")
    if target["owner_id"] != owner_id:
        raise ValueError("only the owner can decide on their own records")
    if decision == "approve":
        if not target_is_proposal:
            raise ValueError("approve applies to proposals; applied records need no approval")
        approvals = load_approvals(root)
        approvals.append(
            {
                "owner_id": owner_id,
                "preference_id": target["preference_id"],
                "revision_id": target["revision_id"],
                "approved_at": _utc_now(),
                "note": note.strip(),
            }
        )
        _save_approvals(root, approvals)
        source_path = _store_dir(root, PROPOSALS_DIR) / f"{target_revision_id}.json"
        dest = _store_dir(root, REVISIONS_DIR) / f"{target_revision_id}.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(dest))
        return {
            "decision": "approve",
            "revision_id": target_revision_id,
            "preference_id": target["preference_id"],
            "path": str(dest.relative_to(root)),
        }
    if decision == "decline":
        if not target_is_proposal:
            raise ValueError("decline applies to proposals; for canonical records use reject or delete")
        source_path = _store_dir(root, PROPOSALS_DIR) / f"{target_revision_id}.json"
        archive = _store_dir(root, DECIDED_DIR) / f"{target_revision_id}.json"
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(archive))
        return {
            "decision": "decline",
            "revision_id": target_revision_id,
            "preference_id": target["preference_id"],
            "archived_to": str(archive.relative_to(root)),
            "effect": "none; the underlying preference keeps whatever effect it had",
        }
    # reject or delete: write a new revision that names all current heads.
    status = "rejected" if decision == "reject" else "deleted"
    heads_now = _current_head_ids(graph, target["preference_id"])
    if target_revision_id not in heads_now:
        heads_now.append(target_revision_id)
    record: dict[str, Any] = {
        "schema_version": SPEC_VERSION,
        "preference_id": target["preference_id"],
        "revision_id": new_id("rev"),
        "parent_revision_ids": heads_now,
        "owner_id": owner_id,
        "author_id": owner_id,
        "status": status,
    }
    problems = validate_record(record)
    if problems:
        raise ValueError("invalid record: " + "; ".join(problems))
    archived = _archive_superseded(root, graph, heads_now)
    path = _write_record(_store_dir(root, REVISIONS_DIR), record)
    # The target itself is already archived above when it was a proposal and
    # is named in heads_now; nothing further to move.
    return {
        "decision": decision,
        "revision_id": record["revision_id"],
        "preference_id": target["preference_id"],
        "parent_revision_ids": heads_now,
        "path": str(path.relative_to(root)),
        "archived_proposals": archived,
    }
