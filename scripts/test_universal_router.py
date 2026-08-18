#!/usr/bin/env python3
"""Behavioral tests for the universal router."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.task_router import route  # noqa: E402
from scripts.universal_router import CANONICAL_SKILLS, classify  # noqa: E402


def main() -> int:
    cases = {
        "\u505a\u4e00\u4e2aPPT\u5e76\u5bfc\u51fa": "artifact-studio",
        "\u626b\u63cf\u7cfb\u7edf\u662f\u5426\u6709\u6728\u9a6c": "system-safety",
        "\u8d4f\u6790\u8fd9\u9996\u8bd7": "humanities",
        "\u67e5\u627e\u8d44\u6599\u5e76\u6838\u5b9e\u8bef\u5bfc\u4fe1\u606f": "web-research",
        "\u505a\u4e00\u4e2a\u57fa\u56e0\u6570\u636e\u4eff\u771f": "simulation-biology",
        "\u5e2e\u6211\u64cd\u4f5c\u6d4f\u89c8\u5668": "computer-operation",
        "build a website and review the code": "software",
    }
    for text, expected in cases.items():
        result = classify(text)
        assert expected in result["domains"], (text, result)
        assert set(result["skills"]) <= CANONICAL_SKILLS, (text, result)

    audit = classify("security audit and add tests")
    assert "code-audit" in audit["skills"], audit
    assert "test-engineering" in audit["skills"], audit
    assert audit["priority"] == "P1", audit

    destructive = classify("delete temporary files")
    assert destructive["priority"] == "P0", destructive
    assert destructive["side_effect_level"] == "external-or-destructive-confirmation", destructive
    assert destructive["side_effect_evidence"], destructive

    negated = classify("Please do not delete files; only audit them read-only")
    assert negated["priority"] == "P2", negated
    assert negated["side_effect_level"] == "read-only", negated
    assert "code-audit" in negated["skills"], negated

    mixed = classify("search sources, inspect an image, and make a presentation")
    assert {"web-research", "artifact-studio", "orchestrate"} <= set(mixed["skills"] + mixed["domains"]), mixed
    assert "capability_choice" in mixed["primary_model_owns"], mixed
    assert "capability_probe" in mixed["parallel_candidates"], mixed

    compat = route("security audit and add tests")
    assert compat["signals"]["skills"] == audit["skills"], compat
    assert "capability_choice" in compat["execution"]["primary_model"], compat

    print("universal_router tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())