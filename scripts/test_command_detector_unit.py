#!/usr/bin/env python3
"""Focused regression checks for test_command_detector."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from test_command_detector import suggest_commands


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "package.json").write_text(json.dumps({"scripts": {"test": "pytest", "build": "vite"}}), encoding="utf-8")
        evidence, suggestions = suggest_commands(root)
        assert evidence == ["package.json"], (evidence, suggestions)
        assert {item["command"] for item in suggestions} == {"npm run test", "npm run build"}, suggestions

        (root / "package.json").write_text("[]", encoding="utf-8")
        evidence, suggestions = suggest_commands(root)
        assert evidence == ["package.json (unreadable)"], (evidence, suggestions)
        assert suggestions == [], suggestions

        (root / "package.json").write_text(json.dumps({"scripts": []}), encoding="utf-8")
        evidence, suggestions = suggest_commands(root)
        assert evidence == ["package.json (unreadable)"], (evidence, suggestions)
        assert suggestions == [], suggestions

    print("test_command_detector tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
