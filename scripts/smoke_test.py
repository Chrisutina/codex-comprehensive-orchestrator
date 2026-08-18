#!/usr/bin/env python3
"""Run the local helper smoke checks."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> None:
    print("$", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


if __name__ == "__main__":
    run([sys.executable, "scripts/task_router.py", "Audit authentication and add tests", "--json"])
    run([sys.executable, "scripts/test_command_detector.py", str(ROOT), "--json"])
    run([sys.executable, "scripts/workspace_inventory.py", str(ROOT), "--json"])
