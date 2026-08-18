#!/usr/bin/env python3
"""Read-only repository inventory for Codex orchestration."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", "vendor", "dist", "build", "coverage", ".venv", "venv", "__pycache__", "target"}
MANIFESTS = {"package.json", "pyproject.toml", "setup.py", "requirements.txt", "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts", "composer.json", "Gemfile", "Package.swift", "plugin.json"}
TEST_MARKERS = ("test", "tests", "spec", "specs", "__tests__")
RISK_PATTERNS = {
    "todo": re.compile(r"(?<![A-Za-z])TODO(?![A-Za-z])|(?<![A-Za-z])FIXME(?![A-Za-z])|(?<![A-Za-z])HACK(?![A-Za-z])", re.I),
    "debug_print": re.compile(r"\b(console\.log|pdb\.set_trace|debugger|logging\.debug|breakpoint\s*\()\b"),
    "dynamic_eval": re.compile(r"\b(eval|exec|Function)\s*\("),
    "broad_catch": re.compile(r"except\s+Exception|catch\s*\([^)]*Exception|catch\s*\{", re.I),
    "secret_hint": re.compile(r"(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}", re.I),
}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts[:-1]):
            continue
        yield path


def is_probably_text(path: Path) -> bool:
    return path.suffix.lower() in {
        ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go", ".rs", ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".php", ".rb", ".swift", ".vue", ".svelte", ".html", ".css", ".scss", ".sql", ".sh", ".ps1", ".yml", ".yaml", ".json", ".toml", ".xml", ".md", ""
    }


def _is_detector_definition(path: Path, line: str, kind: str) -> bool:
    # The scanner's own regex declarations are not findings in its scanned tree.
    if path.name == "workspace_inventory.py" and "re.compile" in line:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--max-files", type=int, default=10000)
    args = parser.parse_args()
    if args.max_files < 0:
        parser.error("--max-files must be non-negative")

    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        parser.error(f"not a directory: {root}")

    files = []
    extensions = Counter()
    manifests = []
    tests = []
    risk_hits = []
    truncated = False
    for path in iter_files(root):
        if len(files) >= args.max_files:
            truncated = True
            break
        rel = path.relative_to(root).as_posix()
        files.append(rel)
        extensions[path.suffix.lower() or "[no extension]"] += 1
        if path.name in MANIFESTS:
            manifests.append(rel)
        lowered = rel.lower()
        if any(marker in {part.lower() for part in path.parts} for marker in TEST_MARKERS) or re.search(r"(^|[._-])(test|spec)([._-]|$)", path.stem, re.I):
            tests.append(rel)
        if is_probably_text(path):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for name, pattern in RISK_PATTERNS.items():
                lines = [
                    line_no
                    for line_no, line in enumerate(text.splitlines(), 1)
                    if not _is_detector_definition(path, line, name) and pattern.search(line)
                ]
                if lines:
                    risk_hits.append({"kind": name, "file": rel, "lines": lines[:20], "count": len(lines)})

    result = {
        "root": str(root),
        "file_count": len(files),
        "truncated": truncated,
        "extensions": dict(extensions.most_common()),
        "manifests": sorted(manifests),
        "codex_plugin_manifest": ".codex-plugin/plugin.json" if ".codex-plugin/plugin.json" in manifests else None,
        "test_files": sorted(tests),
        "test_file_count": len(tests),
        "risk_hits": risk_hits,
        "top_level": sorted(p.name for p in root.iterdir()),
    }
    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Root: {result['root']}")
        print(f"Files: {result['file_count']} | Test files: {result['test_file_count']}")
        print("Manifests:", ", ".join(result["manifests"]) or "none")
        print("Extensions:", ", ".join(f"{k}={v}" for k, v in result["extensions"].items()))
        if risk_hits:
            print("Risk signals:")
            for hit in risk_hits:
                print(f"  {hit['kind']}: {hit['file']}:{','.join(map(str, hit['lines']))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
