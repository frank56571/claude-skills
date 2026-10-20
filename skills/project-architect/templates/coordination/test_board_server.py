# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Smoke test for the task board — plain asserts, no framework, no network.

Run: uv run --script coordination/test_board_server.py  (or python3 directly).
Exercises every lifecycle guarantee against a temp state dir; exits 0 on pass.
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_logic as bl  # noqa: E402


def rejects(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except bl.BoardError as exc:
        return str(exc)
    raise AssertionError(f"{fn.__name__}{args} should have been rejected")


def reload_ok(sdir):
    with open(os.path.join(sdir, "board.json")) as fh:
        return json.load(fh)  # raises if not valid JSON


def main():
    tmp = tempfile.TemporaryDirectory()
    os.environ["BOARD_STATE_DIR"] = tmp.name
    sdir = bl.state_dir()
    assert sdir == os.path.abspath(tmp.name), "env override must win"

    board = bl.empty_board("demo", "smoke goal")

    # create + persist
    board, t1 = bl.add_task(board, "Auth API", "Implement login endpoints.",
                            ["pytest tests/test_auth.py exits 0"],
                            ["src/auth/**", "tests/test_auth.py"], [])
    assert t1["id"] == "T-001" and t1["status"] == "open"
    bl.save_board(sdir, board)
    assert reload_ok(sdir)["tasks"][0]["id"] == "T-001"

    # anti-overlap: dir containment + wildcard segment; disjoint accepted
    msg = rejects(bl.add_task, board, "Login page", "x", ["c"],
                  ["src/auth/login.py"], [])
    assert "T-001" in msg, "rejection must name the colliding task"
    rejects(bl.add_task, board, "Models", "x", ["c"], ["src/*/models.py"], [])
    board, t2 = bl.add_task(board, "Billing", "Webhooks.", ["c"],
                            ["src/billing/**"], ["T-001"])
    assert t2["id"] == "T-002"

    # input validation
    rejects(bl.add_task, board, "Bad", "x", [], ["src/x/**"], [])
    rejects(bl.add_task, board, "Bad", "x", ["c"], ["/etc/passwd"], [])
    rejects(bl.add_task, board, "Bad", "x", ["c"], ["src/../secrets"], [])
    rejects(bl.add_task, board, "Bad", "x", ["c"], ["src/other/**"], ["T-999"])

    # claim: ok / double-claim / second active task / unmet deps
    board, t1 = bl.claim(board, "T-001", "worker-2")
    assert t1["status"] == "claimed" and t1["branch"].startswith("feat/T-001-")
    rejects(bl.claim, board, "T-001", "worker-3")           # not open anymore
    rejects(bl.claim, board, "T-002", "worker-2")           # one active task
    rejects(bl.claim, board, "T-002", "worker-3")           # dep T-001 not done

    # progress: assignee-only heartbeat
    rejects(bl.progress, board, "T-001", "worker-3", "hi")
    board, t1 = bl.progress(board, "T-001", "worker-2", "endpoints done")
    assert t1["status"] == "in_progress"

    # handoff: missing exit code / out-of-scope files / completed-with-leftovers
    good_cmds = [{"cmd": "pytest -q", "exit_code": 0}]
    rejects(bl.handoff, board, "T-001", "worker-2", "completed",
            {"commands_run": [{"cmd": "pytest -q"}], "files_touched": []})
    rejects(bl.handoff, board, "T-001", "worker-2", "completed",
            {"commands_run": good_cmds, "files_touched": ["src/billing/x.py"]})
    rejects(bl.handoff, board, "T-001", "worker-2", "completed",
            {"commands_run": good_cmds, "left_undone": ["docs"],
             "files_touched": []})
    rejects(bl.handoff, board, "T-001", "worker-2", "completed",
            {"commands_run": [{"cmd": "pytest -q", "exit_code": 1}],
             "files_touched": []})
    payload = {"completed": ["login + refresh"], "left_undone": [],
               "commands_run": good_cmds, "issues": [],
               "deviations": ["bcrypt→argon2"],
               "files_touched": ["src/auth/api.py", "tests/test_auth.py"],
               "branch": t1["branch"]}
    board, t1 = bl.handoff(board, "T-001", "worker-2", "completed", payload)
    assert t1["status"] == "handoff_submitted"
    path = bl.write_handoff_file(sdir, t1, "worker-2", "completed", payload)
    text = open(path).read()
    assert "→ 0" in text and "bcrypt→argon2" in text
    # non-empty deviations auto-flagged a warning
    assert any(f["open"] and f["task_id"] == "T-001" for f in board["flags"])

    # close: blocker blocks done; rejection reopens; done closes warnings
    board, _ = bl.add_flag(board, "T-001", "blocker", "secret in diff", "sentinel")
    msg = rejects(bl.close, board, "T-001", "done", "ship it")
    assert "blocker" in msg
    board, t1 = bl.close(board, "T-001", "rejected", "remove the secret")
    assert t1["status"] == "in_progress"
    # blocker resolved by hand for the test, resubmit, close as done
    board = {**board, "flags": [{**f, "open": False} for f in board["flags"]]}
    board, t1 = bl.handoff(board, "T-001", "worker-2", "completed", payload)
    board, t1 = bl.close(board, "T-001", "done", "clean")
    assert t1["status"] == "done"
    rejects(bl.close, board, "T-001", "done", "again")      # invalid transition
    rejects(bl.close, board, "T-001", "cancelled", "nope")  # done is final

    # deps unlocked; worker freed after handoff+close
    board, t2 = bl.claim(board, "T-002", "worker-2")
    assert t2["status"] == "claimed"

    # dashboard regenerated with final states
    bl.save_board(sdir, board)
    dash = open(os.path.join(sdir, "DASHBOARD.md")).read()
    assert "T-001" in dash and "done" in dash and "T-002" in dash

    # stale detection
    old = (datetime.now(timezone.utc) - timedelta(hours=2)) \
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    board = bl._replace_task(board, {**bl.find_task(board, "T-002"),
                                     "updated_at": old})
    assert bl.find_stale(board) == ["T-002"]
    board = bl.flag_stale(board)
    stale_flags = [f for f in board["flags"] if f["source"] == "stale" and f["open"]]
    assert len(stale_flags) == 1
    assert len([f for f in bl.flag_stale(board)["flags"]
                if f["source"] == "stale"]) == 1  # idempotent

    # board stays valid JSON + passes schema validation after everything
    bl.save_board(sdir, board)
    assert bl.load_board(sdir)["counters"]["task"] == 2

    tmp.cleanup()
    print("board smoke test: OK")


if __name__ == "__main__":
    main()
