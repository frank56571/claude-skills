"""Task board logic for orchestrated mode — pure stdlib, no dependencies.

State lives in <main-checkout>/coordination/ (board.json + handoffs/ +
DASHBOARD.md), resolved via `git rev-parse --git-common-dir` so every
worktree's server process converges on the same board. Concurrency is an
advisory fcntl lock + atomic replace — safe on local disk, not on NFS.

All operations validate inputs at the boundary and reject invalid state
transitions; error messages name the offending task/pattern because rejection
IS the anti-overlap mechanism.
"""

from __future__ import annotations

import fcntl
import fnmatch
import json
import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

STATES = ("open", "claimed", "in_progress", "handoff_submitted", "done", "cancelled")
TRANSITIONS = {
    ("open", "claimed"),
    ("claimed", "in_progress"),
    ("in_progress", "in_progress"),  # progress refresh / heartbeat
    ("claimed", "handoff_submitted"),
    ("in_progress", "handoff_submitted"),
    ("handoff_submitted", "done"),
    ("handoff_submitted", "in_progress"),  # rejection sends it back
}
ACTIVE_STATES = ("open", "claimed", "in_progress", "handoff_submitted")
SEVERITIES = ("warning", "blocker")
HANDOFF_STATUSES = ("completed", "partial", "blocked")
STALE_MINUTES = int(os.environ.get("BOARD_STALE_MINUTES", "30"))
LOG_CAP = 100


class BoardError(Exception):
    """Raised on any rejected operation; the message explains exactly why."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- state dir

def state_dir() -> str:
    """Resolve the shared coordination dir (env override, else git common dir)."""
    override = os.environ.get("BOARD_STATE_DIR")
    if override:
        return os.path.abspath(override)
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise BoardError(
            "Cannot locate the board: not inside a git repo and BOARD_STATE_DIR "
            "is not set. Run from the project checkout or a worktree."
        ) from exc
    return os.path.join(os.path.dirname(os.path.abspath(out)), "coordination")


def _board_path(sdir: str) -> str:
    return os.path.join(sdir, "board.json")


@contextmanager
def locked(sdir: str):
    os.makedirs(sdir, exist_ok=True)
    with open(os.path.join(sdir, ".board.lock"), "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


# ------------------------------------------------------------------ load/save

def empty_board(project: str = "", goal: str = "") -> dict:
    return {
        "version": 1,
        "project": project,
        "goal": goal,
        "counters": {"task": 0, "flag": 0},
        "updated_at": _now(),
        "tasks": [],
        "flags": [],
        "log": [],
    }


def load_board(sdir: str) -> dict:
    path = _board_path(sdir)
    if not os.path.exists(path):
        return empty_board()
    try:
        with open(path) as fh:
            board = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        raise BoardError(
            f"board.json is corrupt ({exc}). Restore from {path}.bak before continuing."
        ) from exc
    _validate_board(board, path)
    return board


def _validate_board(board: dict, path: str) -> None:
    problems = []
    if board.get("version") != 1:
        problems.append(f"unsupported version {board.get('version')!r}")
    for key in ("counters", "tasks", "flags", "log"):
        if key not in board:
            problems.append(f"missing key {key!r}")
    for task in board.get("tasks", []):
        if task.get("status") not in STATES:
            problems.append(f"task {task.get('id')!r} has invalid status {task.get('status')!r}")
    if problems:
        raise BoardError(
            f"board.json failed validation: {'; '.join(problems)}. "
            f"Restore from {path}.bak before continuing."
        )


def save_board(sdir: str, board: dict) -> None:
    path = _board_path(sdir)
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak")
    fd, tmp = tempfile.mkstemp(dir=sdir, prefix=".board-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(board, fh, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    with open(os.path.join(sdir, "DASHBOARD.md"), "w") as fh:
        fh.write(render_dashboard(board))


# ----------------------------------------------------------- glob overlap

def _is_wild(seg: str) -> bool:
    return any(ch in seg for ch in "*?[")


def _segs_compatible(a: str, b: str) -> bool:
    wild_a, wild_b = _is_wild(a), _is_wild(b)
    if not wild_a and not wild_b:
        return a == b
    if wild_a and not wild_b:
        return fnmatch.fnmatchcase(b, a)
    if wild_b and not wild_a:
        return fnmatch.fnmatchcase(a, b)
    return True  # both wild — conservative


def _patterns_overlap(a: list, b: list) -> bool:
    if not a or not b:
        # One pattern exhausted while the other continues: directory
        # containment (src/auth owns src/auth/login.py) → overlap.
        return True
    if a[0] == "**" or b[0] == "**":
        return True  # prefix matched so far; ** swallows any remainder
    if _segs_compatible(a[0], b[0]):
        return _patterns_overlap(a[1:], b[1:])
    return False


def scopes_may_overlap(scope_a: list, scope_b: list):
    """Return the (pattern_a, pattern_b) pair that may collide, or None.

    Conservative matcher: exact segments + directory containment + wildcard
    segments (character classes count as full wildcards, no brace expansion).
    Over-rejects exotic patterns by design — a false positive costs one cheap
    re-scope; a false negative costs a merge conflict.
    """
    for pa in scope_a:
        for pb in scope_b:
            if _patterns_overlap(pa.strip("/").split("/"), pb.strip("/").split("/")):
                return (pa, pb)
    return None


def files_within_scope(files: list, scope: list) -> list:
    """Return the files that fall OUTSIDE every scope pattern."""
    return [
        f for f in files
        if not any(
            _patterns_overlap(f.strip("/").split("/"), p.strip("/").split("/"))
            for p in scope
        )
    ]


# ------------------------------------------------------------- validation

def validate_task_input(title: str, spec: str, acceptance_criteria: list,
                        file_scope: list) -> None:
    if not title or not title.strip():
        raise BoardError("title must be non-empty")
    if not spec or not spec.strip():
        raise BoardError("spec must be non-empty")
    if not acceptance_criteria:
        raise BoardError("at least one acceptance criterion is required")
    if not file_scope:
        raise BoardError("file_scope must declare at least one glob")
    for pattern in file_scope:
        if os.path.isabs(pattern) or ".." in pattern.split("/"):
            raise BoardError(
                f"file_scope pattern {pattern!r} must be a relative path inside the repo"
            )


def find_task(board: dict, task_id: str) -> dict:
    for task in board["tasks"]:
        if task["id"] == task_id:
            return task
    raise BoardError(f"no such task: {task_id}")


def _check_transition(task: dict, new_status: str) -> None:
    if new_status == "cancelled":
        if task["status"] == "done":
            raise BoardError(f"{task['id']} is done and cannot be cancelled")
        return
    if (task["status"], new_status) not in TRANSITIONS:
        raise BoardError(
            f"invalid transition for {task['id']}: {task['status']} → {new_status}"
        )


def _require_assignee(task: dict, worker_id: str) -> None:
    if task.get("assignee") != worker_id:
        raise BoardError(
            f"{task['id']} is assigned to {task.get('assignee')!r}, not {worker_id!r}"
        )


def check_handoff(status: str, left_undone: list, commands_run: list) -> None:
    if status not in HANDOFF_STATUSES:
        raise BoardError(f"handoff status must be one of {HANDOFF_STATUSES}")
    for entry in commands_run:
        if not isinstance(entry, dict) or "cmd" not in entry \
                or not isinstance(entry.get("exit_code"), int):
            raise BoardError(
                "every commands_run entry needs {cmd, exit_code:int} — "
                "claims without exit codes are not evidence"
            )
    if status == "completed":
        if left_undone:
            raise BoardError("status 'completed' requires an empty left_undone list")
        bad = [e["cmd"] for e in commands_run if e["exit_code"] != 0]
        if bad:
            raise BoardError(
                f"status 'completed' with nonzero exit codes: {bad} — submit as 'partial'"
            )


def find_stale(board: dict, now: datetime = None) -> list:
    now = now or datetime.now(timezone.utc)
    threshold = now - timedelta(minutes=STALE_MINUTES)
    stale = []
    for task in board["tasks"]:
        if task["status"] not in ("claimed", "in_progress"):
            continue
        updated = datetime.strptime(task["updated_at"], "%Y-%m-%dT%H:%M:%SZ") \
            .replace(tzinfo=timezone.utc)
        if updated < threshold:
            stale.append(task["id"])
    return stale


def worker_active_task(board: dict, worker_id: str):
    for task in board["tasks"]:
        if task.get("assignee") == worker_id and \
                task["status"] in ("claimed", "in_progress", "handoff_submitted"):
            return task
    return None


# ------------------------------------------------------------- mutations
# Immutability style: builders return NEW dicts; callers replace, never mutate.

def append_log(board: dict, line: str) -> dict:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    log = (board["log"] + [f"{stamp} {line}"])[-LOG_CAP:]
    return {**board, "log": log, "updated_at": _now()}


def _replace_task(board: dict, updated: dict) -> dict:
    tasks = [updated if t["id"] == updated["id"] else t for t in board["tasks"]]
    return {**board, "tasks": tasks}


def _slug(title: str) -> str:
    keep = "".join(ch if ch.isalnum() else "-" for ch in title.lower())
    return "-".join(filter(None, keep.split("-")))[:40]


def add_task(board: dict, title: str, spec: str, acceptance_criteria: list,
             file_scope: list, depends_on: list) -> tuple:
    validate_task_input(title, spec, acceptance_criteria, file_scope)
    known = {t["id"] for t in board["tasks"]}
    missing = [d for d in depends_on if d not in known]
    if missing:
        raise BoardError(f"depends_on references unknown tasks: {missing}")
    for other in board["tasks"]:
        if other["status"] in ("done", "cancelled"):
            continue
        hit = scopes_may_overlap(file_scope, other["file_scope"])
        if hit:
            raise BoardError(
                f"file_scope overlap with {other['id']} ({other['title']!r}): "
                f"{hit[0]!r} may intersect {hit[1]!r}. Re-scope one of them "
                f"or use depends_on."
            )
    number = board["counters"]["task"] + 1
    task = {
        "id": f"T-{number:03d}",
        "title": title, "spec": spec,
        "acceptance_criteria": acceptance_criteria,
        "file_scope": file_scope, "depends_on": depends_on,
        "status": "open", "assignee": None, "branch": None,
        "created_at": _now(), "updated_at": _now(),
        "progress_note": None, "handoff": None, "resolution": None,
    }
    board = {**board, "counters": {**board["counters"], "task": number},
             "tasks": board["tasks"] + [task]}
    return append_log(board, f"{task['id']} created: {title}"), task


def claim(board: dict, task_id: str, worker_id: str) -> tuple:
    task = find_task(board, task_id)
    _check_transition(task, "claimed")
    active = worker_active_task(board, worker_id)
    if active:
        raise BoardError(
            f"{worker_id} already has an active task ({active['id']}); "
            f"submit its handoff first"
        )
    unmet = [d for d in task["depends_on"]
             if find_task(board, d)["status"] != "done"]
    if unmet:
        raise BoardError(f"{task_id} has unmet dependencies: {unmet}")
    branch = f"feat/{task_id}-{_slug(task['title'])}"
    updated = {**task, "status": "claimed", "assignee": worker_id,
               "branch": branch, "updated_at": _now()}
    board = _replace_task(board, updated)
    return append_log(board, f"{task_id} claimed by {worker_id}"), updated


def progress(board: dict, task_id: str, worker_id: str, note: str) -> tuple:
    task = find_task(board, task_id)
    _require_assignee(task, worker_id)
    _check_transition(task, "in_progress")
    updated = {**task, "status": "in_progress", "progress_note": note,
               "updated_at": _now()}
    board = _replace_task(board, updated)
    return append_log(board, f"{task_id} progress ({worker_id}): {note}"), updated


def handoff(board: dict, task_id: str, worker_id: str, status: str,
            payload: dict) -> tuple:
    task = find_task(board, task_id)
    _require_assignee(task, worker_id)
    _check_transition(task, "handoff_submitted")
    check_handoff(status, payload.get("left_undone", []),
                  payload.get("commands_run", []))
    outside = files_within_scope(payload.get("files_touched", []),
                                 task["file_scope"])
    if outside:
        raise BoardError(
            f"files_touched outside {task_id}'s file_scope: {outside}. "
            f"Raise a flag and wait for a scope decision — never edit them."
        )
    updated = {**task, "status": "handoff_submitted",
               "handoff": f"coordination/handoffs/{task_id}.md",
               "updated_at": _now()}
    board = _replace_task(board, updated)
    board = append_log(board, f"{task_id} handoff submitted by {worker_id} ({status})")
    if payload.get("issues") or payload.get("deviations"):
        board, _ = add_flag(board, task_id, "warning",
                            "handoff has non-empty issues/deviations — review before close",
                            "board")
    return board, updated


def add_flag(board: dict, task_id: str, severity: str, message: str,
             source: str) -> tuple:
    if severity not in SEVERITIES:
        raise BoardError(f"severity must be one of {SEVERITIES}")
    find_task(board, task_id)  # must exist
    number = board["counters"]["flag"] + 1
    flag = {"id": f"F-{number:03d}", "task_id": task_id, "severity": severity,
            "source": source, "message": message, "raised_at": _now(),
            "open": True}
    board = {**board, "counters": {**board["counters"], "flag": number},
             "flags": board["flags"] + [flag]}
    return append_log(board, f"{flag['id']} [{severity}] on {task_id}: {message}"), flag


def close(board: dict, task_id: str, resolution: str, note: str) -> tuple:
    task = find_task(board, task_id)
    if resolution == "done":
        _check_transition(task, "done")
        blockers = [f["id"] for f in board["flags"]
                    if f["task_id"] == task_id and f["open"]
                    and f["severity"] == "blocker"]
        if blockers:
            raise BoardError(f"cannot close {task_id} as done: open blocker flags {blockers}")
        flags = [{**f, "open": False} if f["task_id"] == task_id else f
                 for f in board["flags"]]
        updated = {**task, "status": "done", "resolution": note, "updated_at": _now()}
        board = {**_replace_task(board, updated), "flags": flags}
    elif resolution == "rejected":
        _check_transition(task, "in_progress")
        updated = {**task, "status": "in_progress", "updated_at": _now()}
        board = _replace_task(board, updated)
        board, _ = add_flag(board, task_id, "warning", f"handoff rejected: {note}",
                            "orchestrator")
        task = updated
    elif resolution == "cancelled":
        _check_transition(task, "cancelled")
        updated = {**task, "status": "cancelled", "resolution": note,
                   "updated_at": _now()}
        board = _replace_task(board, updated)
    else:
        raise BoardError("resolution must be done | rejected | cancelled")
    return append_log(board, f"{task_id} closed as {resolution}: {note}"), \
        find_task(board, task_id)


def flag_stale(board: dict) -> dict:
    """Auto-flag stale tasks once each (idempotent per staleness episode)."""
    for task_id in find_stale(board):
        already = any(f["task_id"] == task_id and f["open"] and f["source"] == "stale"
                      for f in board["flags"])
        if not already:
            board, _ = add_flag(board, task_id, "warning",
                                f"no heartbeat for over {STALE_MINUTES} min", "stale")
    return board


# ------------------------------------------------------------- rendering

def render_dashboard(board: dict) -> str:
    stale = set(find_stale(board))
    lines = [
        f"# Board — {board.get('project') or 'project'}",
        f"Goal: {board.get('goal') or '(not set)'} · Updated: {board['updated_at']}",
        "",
        "| ID | Task | Status | Assignee | Deps | Handoff |",
        "|----|------|--------|----------|------|---------|",
    ]
    for t in board["tasks"]:
        status = t["status"] + (" ⚠️stale" if t["id"] in stale else "")
        lines.append(
            f"| {t['id']} | {t['title']} | {status} | {t['assignee'] or '—'} "
            f"| {', '.join(t['depends_on']) or '—'} | {t['handoff'] or '—'} |"
        )
    open_flags = [f for f in board["flags"] if f["open"]]
    lines.append("")
    lines.append(f"## Open flags ({len(open_flags)})")
    for f in open_flags:
        lines.append(f"- {f['id']} [{f['severity']}] {f['task_id']} ({f['source']}): {f['message']}")
    lines.append("")
    lines.append("## Log (last 15)")
    lines.extend(f"- {line}" for line in board["log"][-15:])
    return "\n".join(lines) + "\n"


def render_handoff_md(task: dict, worker_id: str, status: str, payload: dict) -> str:
    def block(items):
        return "\n".join(f"- {i}" for i in items) if items else "- (none)"
    commands = "\n".join(
        f"- `{e['cmd']}` → {e['exit_code']}" for e in payload.get("commands_run", [])
    ) or "- (none)"
    return f"""# Handoff — {task['id']} {task['title']}
Worker finished: {_now()} · Worker: {worker_id} · Branch: {payload.get('branch') or task['branch']} · Status: {status}

## Completed
{block(payload.get('completed', []))}

## Left undone
{block(payload.get('left_undone', []))}

## Commands run (with exit codes)
{commands}

## Issues discovered
{block(payload.get('issues', []))}

## Deviations from spec
{block(payload.get('deviations', []))}

## Files touched
{block(payload.get('files_touched', []))}

## Acceptance criteria
{block(task['acceptance_criteria'])}
"""


def write_handoff_file(sdir: str, task: dict, worker_id: str, status: str,
                       payload: dict) -> str:
    hdir = os.path.join(sdir, "handoffs")
    os.makedirs(hdir, exist_ok=True)
    path = os.path.join(hdir, f"{task['id']}.md")
    with open(path, "w") as fh:
        fh.write(render_handoff_md(task, worker_id, status, payload))
    return path
