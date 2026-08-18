#!/usr/bin/env python3
"""Suggest safe test commands from common project manifests without running them."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def suggest_commands(root: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Return manifest evidence and safe, non-executed test suggestions."""
    suggestions: list[dict[str, str]] = []
    evidence: list[str] = []

    package = root / "package.json"
    if package.exists():
        try:
            data: Any = json.loads(package.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("package.json root must be an object")
            scripts = data.get("scripts", {})
            if not isinstance(scripts, dict):
                raise ValueError("package.json scripts must be an object")
            for name in ("test", "test:unit", "test:integration", "lint", "typecheck", "build"):
                if name in scripts:
                    suggestions.append({"command": f"npm run {name}", "reason": f"package.json script: {name}"})
            evidence.append("package.json")
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError):
            evidence.append("package.json (unreadable)")
    if (root / "pytest.ini").exists() or (root / "pyproject.toml").exists() or (root / "setup.cfg").exists():
        suggestions.extend([
            {"command": "python -m pytest", "reason": "Python test discovery"},
            {"command": "python -m compileall .", "reason": "Python syntax smoke check"},
        ])
        evidence.append("Python project config")
    if (root / "go.mod").exists():
        suggestions.extend([
            {"command": "go test ./...", "reason": "Go test suite"},
            {"command": "go vet ./...", "reason": "Go static analysis"},
        ])
        evidence.append("go.mod")
    if (root / "Cargo.toml").exists():
        suggestions.extend([
            {"command": "cargo test", "reason": "Rust test suite"},
            {"command": "cargo check", "reason": "Rust compile/type check"},
        ])
        evidence.append("Cargo.toml")
    if (root / "pom.xml").exists():
        suggestions.append({"command": "mvn test", "reason": "Maven test lifecycle"})
        evidence.append("pom.xml")
    return evidence, suggestions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    evidence, suggestions = suggest_commands(root)
    result = {"root": str(root), "evidence": evidence, "suggestions": suggestions}
    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Evidence:", ", ".join(evidence) or "none")
        for item in suggestions:
            print(f"- {item['command']} ({item['reason']})")
        if not suggestions:
            print("No safe test command inferred; inspect repository guidance and existing CI configuration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
