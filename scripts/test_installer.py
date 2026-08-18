#!/usr/bin/env python3
"""Focused tests for the portable installer."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from install import copy_plugin, ensure_model_catalog, update_marketplace  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "source"
        source.mkdir()
        (source / "model_catalog.example.json").write_text(json.dumps({
            "current_model": {"id": "host-current", "configured": True, "enabled": True},
            "models": [{"id": "helper", "configured": True, "enabled": True}],
        }), encoding="utf-8")
        assert ensure_model_catalog(source) is True
        catalog = json.loads((source / "model_catalog.json").read_text(encoding="utf-8"))
        assert catalog["current_model"]["enabled"] is True
        assert catalog["models"][0]["configured"] is False
        assert ensure_model_catalog(source) is False

        marketplace = root / ".agents" / "plugins" / "marketplace.json"
        update_marketplace(marketplace)
        update_marketplace(marketplace)
        data = json.loads(marketplace.read_text(encoding="utf-8"))
        entries = [item for item in data["plugins"] if item["name"] == "codex-comprehensive-orchestrator"]
        assert len(entries) == 1, entries
        assert entries[0]["source"]["path"] == "./plugins/codex-comprehensive-orchestrator"

        copy_source = root / "copy-source"
        copy_source.mkdir()
        (copy_source / "keep.txt").write_text("safe", encoding="utf-8")
        (copy_source / ".env.local").write_text("SECRET=must-not-copy", encoding="utf-8")
        (copy_source / "private.pyc").write_bytes(b"cache")
        (copy_source / "model_catalog.json").write_text("{}", encoding="utf-8")
        copied = root / "copy-destination"
        copy_plugin(copy_source, copied)
        assert (copied / "keep.txt").is_file()
        assert not (copied / ".env.local").exists()
        assert not (copied / "private.pyc").exists()
        assert not (copied / "model_catalog.json").exists()

    print("installer tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
