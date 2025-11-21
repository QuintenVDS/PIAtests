import os
import time
import sys
import types
from pathlib import Path
import pytest

def test_old_logs_are_deleted_after_threshold(monkeypatch, tmp_path):

    monkeypatch.setenv("BASE_LOGS", str(tmp_path))
    # create files and set their mtimes to simulate "12 months old
    twelve_months_seconds = 60 * 60 * 24 * 30 * 12
    active = tmp_path / "ownphotos.log"
    old1 = tmp_path / "ownphotos.log.1"
    old2 = tmp_path / "ownphotos.log.2"
    recent = tmp_path / "ownphotos.log.recent"

    active.write_text("current log")
    old1.write_text("old log 1")
    old2.write_text("old log 2")
    recent.write_text("recent log")

    now = time.time()
    old_time = now - (twelve_months_seconds + 10)
    os.utime(old1, (old_time, old_time))
    os.utime(old2, (old_time, old_time))

    # give external cleanup up to max_wait_seconds to remove old files
    # simulated 12-month-old mtimes above; don't actually wait 12 months
    max_wait_seconds = 30
    deadline = time.time() + max_wait_seconds

    # make sure os.utime set the mtimes we expected
    mtime_old1 = os.path.getmtime(old1)
    mtime_old2 = os.path.getmtime(old2)
    assert (now - mtime_old1) >= twelve_months_seconds, "old1 mtime not old"
    assert (now - mtime_old2) >= twelve_months_seconds, "old2 mtime not old"

    while time.time() < deadline:
        remaining = set(p.name for p in tmp_path.iterdir())
        if "ownphotos.log.1" not in remaining and "ownphotos.log.2" not in remaining:
            break
        time.sleep(0.5)

    remaining = sorted(p.name for p in tmp_path.iterdir())
    assert all(x not in remaining for x in ("ownphotos.log.1", "ownphotos.log.2")), (
        f"Old logs were not deleted within wait time. Remaining: {remaining}")