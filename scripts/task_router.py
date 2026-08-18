#!/usr/bin/env python3
"""Backward-compatible risk router backed by the unified universal router."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.universal_router import classify  # noqa: E402


def route(text: str) -> dict:
    result = classify(text)
    return {
        "priority": result["priority"],
        "rationale": (
            "High-impact or sensitive language detected."
            if result["priority"] == "P0"
            else "Sensitive or regulated-domain language detected."
            if result["priority"] == "P1"
            else "No active critical signal detected; confirm scope before fan-out."
        ),
        "signals": {
            "critical": result["risk_signals"]["p0"],
            "important": result["risk_signals"]["p1"],
            "domains": result["domains"],
            "skills": result["skills"],
            "side_effect_level": result["side_effect_level"],
        },
        "execution": {
            "primary_model": [
                "requirements",
                "critical_path",
                "capability_choice",
                "integration",
                "final_verification",
            ],
            "delegatable": [
                "inventory",
                "independent_audit",
                "test_enumeration",
                "documentation_or_options",
                "capability_probe",
            ],
            "guardrail": "Keep delegated writes disjoint and review all outputs before integration.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="*", help="task text; stdin is used when omitted")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    text = " ".join(args.text).strip()
    if not text:
        text = sys.stdin.read().strip()
    result = route(text)
    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Priority: {result['priority']}\n{result['rationale']}")
        print("Primary:", ", ".join(result["execution"]["primary_model"]))
        print("Delegatable:", ", ".join(result["execution"]["delegatable"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
