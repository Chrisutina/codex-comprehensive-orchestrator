#!/usr/bin/env python3
"""Install and register the plugin with a portable, user-local setup.

The installer never creates credentials or enables external providers. It copies the
plugin to ~/plugins, creates a safe disabled model catalog, updates the personal
marketplace without overwriting unrelated entries, and asks the Codex CLI to register
and install the plugin when that CLI is available.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

PLUGIN_NAME = "codex-comprehensive-orchestrator"
MARKETPLACE_NAME = "personal"


def _copy_ignore_patterns() -> tuple[str, ...]:
    # Never copy repository metadata, generated caches, local credentials, or private
    # model configuration into another user's installation.
    return (
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "model_catalog.json",
        ".env",
        ".env.*",
        "*.pyc",
        "*.pyo",
        "*.pyd",
    )


def _default_marketplace() -> dict[str, Any]:
    return {
        "name": MARKETPLACE_NAME,
        "interface": {"displayName": "Personal"},
        "plugins": [],
    }


def _load_json_object(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        Path(temp_name).replace(path)
    finally:
        temporary = Path(temp_name)
        if temporary.exists():
            temporary.unlink()


def _marketplace_entry() -> dict[str, Any]:
    return {
        "name": PLUGIN_NAME,
        "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Productivity",
    }


def update_marketplace(path: Path) -> None:
    marketplace = _load_json_object(path, _default_marketplace())
    marketplace.setdefault("name", MARKETPLACE_NAME)
    marketplace.setdefault("interface", {"displayName": "Personal"})
    plugins = marketplace.get("plugins", [])
    if not isinstance(plugins, list):
        raise ValueError(f"marketplace.plugins must be a list: {path}")
    entry = _marketplace_entry()
    marketplace["plugins"] = [item for item in plugins if not isinstance(item, dict) or item.get("name") != PLUGIN_NAME]
    marketplace["plugins"].append(entry)
    _write_json_atomic(path, marketplace)


def copy_plugin(source: Path, destination: Path) -> None:
    source = source.resolve()
    destination = destination.resolve()
    if source == destination:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(*_copy_ignore_patterns()),
    )


def ensure_model_catalog(destination: Path) -> bool:
    catalog = destination / "model_catalog.json"
    if catalog.exists():
        return False
    example = destination / "model_catalog.example.json"
    if not example.exists():
        return False
    value = _load_json_object(example, {})
    # Keep every provider disabled until the user supplies authorized configuration.
    current = value.get("current_model")
    if isinstance(current, dict):
        current["configured"] = True
        current["enabled"] = True
    models = value.get("models")
    if isinstance(models, list):
        for model in models:
            if isinstance(model, dict):
                model["configured"] = False
                model["enabled"] = False
    _write_json_atomic(catalog, value)
    return True


def register_with_codex(home: Path, *, skip: bool) -> list[dict[str, Any]]:
    if skip:
        return [{"command": "codex", "status": "skipped", "reason": "--no-register"}]
    codex = shutil.which("codex")
    if not codex:
        return [{"command": "codex", "status": "unavailable", "reason": "Codex CLI was not found on PATH"}]
    results: list[dict[str, Any]] = []
    commands = [
        [codex, "plugin", "marketplace", "add", str(home)],
        [codex, "plugin", "add", f"{PLUGIN_NAME}@{MARKETPLACE_NAME}", "--json"],
    ]
    for command in commands:
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        results.append(
            {
                "command": " ".join(command),
                "status": "ok" if completed.returncode == 0 else "failed",
                "returncode": completed.returncode,
                "stdout": completed.stdout[-2000:],
                "stderr": completed.stderr[-2000:],
            }
        )
        if completed.returncode != 0:
            break
    return results


def install(source: Path, *, home: Path | None = None, no_register: bool = False) -> dict[str, Any]:
    source = source.resolve()
    home = (home or Path.home()).resolve()
    if not (source / ".codex-plugin" / "plugin.json").is_file():
        raise ValueError(f"not a plugin root: {source}")
    destination = home / "plugins" / PLUGIN_NAME
    marketplace = home / ".agents" / "plugins" / "marketplace.json"
    copy_plugin(source, destination)
    catalog_created = ensure_model_catalog(destination)
    update_marketplace(marketplace)
    codex = register_with_codex(home, skip=no_register)
    return {
        "plugin": PLUGIN_NAME,
        "source": str(source),
        "destination": str(destination),
        "marketplace": str(marketplace),
        "model_catalog_created": catalog_created,
        "codex": codex,
        "next_step": "Start a new Codex thread after installation so the updated plugin is loaded.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--home", type=Path, help="override the user home directory for testing")
    parser.add_argument("--no-register", action="store_true", help="only copy files and update marketplace")
    args = parser.parse_args()
    try:
        result = install(args.source, home=args.home, no_register=args.no_register)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
