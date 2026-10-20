# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp"]
# ///
"""MCP stdio server exposing the orchestrated-mode task board.

Run via the project's .mcp.json: `uv run --script coordination/board_server.py`.
Every terminal (main checkout and worktrees) spawns its own process; all of
them share one board because board_logic resolves the git common dir.
All logic and validation live in board_logic.py — this file is wiring only.
"""

import board_logic as bl
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("board")


def _mutate(fn):
    """Lock → load → apply → save. fn(board) returns (board, result)."""
    sdir = bl.state_dir()
    with bl.locked(sdir):
        board, result = fn(bl.load_board(sdir))
        bl.save_board(sdir, board)
    return result


@mcp.tool()
def create_task(title: str, spec: str, acceptance_criteria: list[str],
                file_scope: list[str], depends_on: list[str] = []) -> dict:
    """Create a task (orchestrator only). Rejects file_scope globs that may
    overlap any non-done task's scope — re-scope or use depends_on instead."""
    task = _mutate(lambda b: bl.add_task(b, title, spec, acceptance_criteria,
                                         file_scope, list(depends_on)))
    return {"task_id": task["id"], "status": task["status"]}


@mcp.tool()
def get_board() -> dict:
    """Full board summary. Also runs stale detection (auto-flags tasks with no
    heartbeat) and regenerates coordination/DASHBOARD.md."""
    sdir = bl.state_dir()
    with bl.locked(sdir):
        board = bl.flag_stale(bl.load_board(sdir))
        bl.save_board(sdir, board)
    return {
        "project": board["project"], "goal": board["goal"],
        "tasks": [{k: t[k] for k in ("id", "title", "status", "assignee",
                                     "depends_on", "file_scope")}
                  for t in board["tasks"]],
        "open_flags": [f for f in board["flags"] if f["open"]],
        "stale_task_ids": bl.find_stale(board),
    }


@mcp.tool()
def get_task_status(task_id: str) -> dict:
    """Full record for one task, including its open flags and handoff path."""
    board = bl.load_board(bl.state_dir())
    task = bl.find_task(board, task_id)
    return {**task, "open_flags": [f for f in board["flags"]
                                   if f["task_id"] == task_id and f["open"]]}


@mcp.tool()
def claim_task(task_id: str, worker_id: str) -> dict:
    """Claim an open task (workers). Rejects if deps are unmet, the worker
    already has an active task, or the task is not open. Returns the branch
    name to create: `git checkout -b <branch> main`."""
    task = _mutate(lambda b: bl.claim(b, task_id, worker_id))
    return {"task_id": task["id"], "branch": task["branch"],
            "file_scope": task["file_scope"], "spec": task["spec"],
            "acceptance_criteria": task["acceptance_criteria"]}


@mcp.tool()
def update_progress(task_id: str, worker_id: str, note: str) -> dict:
    """Heartbeat + progress note (assignee only). Call at least every ~20 min
    of work — silence past the stale threshold auto-flags the task."""
    task = _mutate(lambda b: bl.progress(b, task_id, worker_id, note))
    return {"task_id": task["id"], "status": task["status"]}


@mcp.tool()
def submit_handoff(task_id: str, worker_id: str, status: str,
                   completed: list[str], left_undone: list[str],
                   commands_run: list[dict], issues: list[str],
                   deviations: list[str], files_touched: list[str],
                   branch: str) -> dict:
    """Submit the structured handoff (assignee only). status: completed |
    partial | blocked. Every commands_run entry needs {cmd, exit_code:int}.
    Rejects: missing exit codes, 'completed' with leftovers or nonzero exits,
    files_touched outside the task's file_scope."""
    payload = {"completed": completed, "left_undone": left_undone,
               "commands_run": commands_run, "issues": issues,
               "deviations": deviations, "files_touched": files_touched,
               "branch": branch}
    sdir = bl.state_dir()
    with bl.locked(sdir):
        board = bl.load_board(sdir)
        board, task = bl.handoff(board, task_id, worker_id, status, payload)
        path = bl.write_handoff_file(sdir, task, worker_id, status, payload)
        bl.save_board(sdir, board)
    return {"task_id": task_id, "handoff_path": path, "status": task["status"]}


@mcp.tool()
def raise_flag(task_id: str, severity: str, message: str, source: str) -> dict:
    """Raise a red flag on a task. severity: warning | blocker. Open blocker
    flags prevent close_task(done)."""
    flag = _mutate(lambda b: bl.add_flag(b, task_id, severity, message, source))
    return {"flag_id": flag["id"]}


@mcp.tool()
def list_flags(open_only: bool = True) -> list[dict]:
    """List flags, open ones by default."""
    board = bl.load_board(bl.state_dir())
    return [f for f in board["flags"] if f["open"] or not open_only]


@mcp.tool()
def close_task(task_id: str, resolution: str, note: str) -> dict:
    """Close a task (orchestrator only). resolution: done (requires submitted
    handoff + no open blocker flags; closes its warnings) | rejected (back to
    in_progress with a flag explaining why) | cancelled."""
    task = _mutate(lambda b: bl.close(b, task_id, resolution, note))
    return {"task_id": task["id"], "status": task["status"]}


@mcp.tool()
def set_goal(project: str, goal: str) -> dict:
    """Set the project name and mission goal shown on the dashboard
    (orchestrator, once at kickoff)."""
    def apply(board):
        board = {**board, "project": project, "goal": goal}
        return bl.append_log(board, f"goal set: {goal}"), goal
    _mutate(apply)
    return {"ok": True}


if __name__ == "__main__":
    mcp.run()
