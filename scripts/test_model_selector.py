#!/usr/bin/env python3
"""Tests for capability-aware model routing."""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.model_selector import load_catalog, select_model  # noqa: E402


CURRENT = {
    "id": "host-current",
    "provider": "host",
    "capabilities": ["text", "reasoning", "code", "planning"],
    "configured": True,
    "enabled": True,
    "quality_tier": 3,
    "cost_tier": 2,
    "context_window": 128000,
}


def catalog(*models, current=None):
    return {"current_model": current or CURRENT, "models": list(models)}


def main() -> int:
    ordinary = select_model("write a sorting algorithm and add tests")
    assert ordinary["decision"] == "use_current", ordinary

    missing_vision = select_model("\u8bc6\u522b\u8fd9\u5f20\u56fe\u7247")
    assert missing_vision["decision"] == "request_user_configuration", missing_vision
    assert "vision" in missing_vision["capability_gaps"], missing_vision

    vision_helper = {
        "id": "vision-helper",
        "provider": "user-configured",
        "capabilities": ["text", "vision", "ocr"],
        "configured": True,
        "enabled": True,
        "quality_tier": 3,
        "cost_tier": 2,
    }
    delegated = select_model("\u8bc6\u522b\u8fd9\u5f20\u56fe\u7247", catalog(vision_helper))
    assert delegated["decision"] == "delegate_missing_capability", delegated
    assert delegated["selected_helper"]["id"] == "vision-helper", delegated

    current_with_vision = dict(CURRENT, capabilities=CURRENT["capabilities"] + ["vision"])
    use_current = select_model("\u8bc6\u522b\u8fd9\u5f20\u56fe\u7247", catalog(current=current_with_vision))
    assert use_current["decision"] == "use_current", use_current

    long_task = select_model("\u5ba1\u8ba1\u5168\u4ed3\u5e93\u5e76\u8fd0\u884c\u5b8c\u6574\u6d4b\u8bd5")
    assert "long_context" in long_task["capability_gaps"], long_task
    assert long_task["decision"] == "request_user_configuration", long_task

    disabled = dict(vision_helper, id="disabled-vision", configured=True, enabled=False)
    not_selected = select_model("\u8bc6\u522b\u8fd9\u5f20\u56fe\u7247", catalog(disabled))
    assert not_selected["decision"] == "request_user_configuration", not_selected
    assert not_selected["selected_helper"] is None, not_selected

    artifact_helper = {
        "id": "artifact-helper",
        "provider": "user-configured",
        "capabilities": ["artifact_generation", "text"],
        "configured": True,
        "enabled": True,
        "quality_tier": 3,
        "cost_tier": 2,
    }
    mixed = select_model(
        "\u8bc6\u522b\u8fd9\u5f20\u56fe\u7247\u5e76\u5236\u4f5cPPT",
        catalog(vision_helper, artifact_helper),
    )
    assert mixed["decision"] == "delegate_missing_capability", mixed
    assert {model["id"] for model in mixed["selected_helpers"]} == {"vision-helper", "artifact-helper"}, mixed
    assert mixed["unmet_after_selection"] == [], mixed

    secret_value = "SHOULD_" + "NOT_APPEAR"
    secret_catalog = catalog(dict(vision_helper, api_key=secret_value, api_key_env="VISION_KEY"))
    output = json.dumps(select_model("\u8bc6\u522b\u56fe\u7247", secret_catalog), ensure_ascii=False)
    assert "SHOULD_NOT_APPEAR" not in output, output
    assert "VISION_KEY" in output, output

    try:
        load_catalog(Path(__file__).with_name("missing-catalog.json"))
    except ValueError:
        pass
    else:
        raise AssertionError("missing catalog should fail clearly")

    print("model_selector tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())