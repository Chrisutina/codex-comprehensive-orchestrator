#!/usr/bin/env python3
"""Capability-aware model selection without making network calls.

This script produces a routing recommendation for the host orchestrator. It
never calls a provider, reads secret values, or treats an unconfigured model as
available. The host model remains responsible for approval, delegation, and
final synthesis.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable


DEFAULT_CURRENT_MODEL = {
    "id": "host-current",
    "provider": "host",
    "capabilities": ["text", "reasoning", "code", "planning"],
    "configured": True,
    "enabled": True,
    "quality_tier": 3,
    "cost_tier": 2,
    "context_window": 128000,
}

CAPABILITY_PATTERNS: dict[str, tuple[str, ...]] = {
    "vision": (
        r"\b(?:image|picture|photo|screenshot|diagram|visual|ocr|scan\s+image|see\s+this|look\s+at|识别|看图)\b",
        r"\u56fe\u50cf|\u56fe\u7247|\u7167\u7247|\u622a\u56fe|\u56fe\u8868|\u8bc6\u56fe|\u89c6\u89c9|OCR|\u626b\u63cf\u56fe\u7247|\u770b\u56fe|\u8bc6\u522b\u56fe\u7247",
    ),
    "image_generation": (
        r"\b(?:generate|create|draw|paint|design)\s+(?:an?\s+)?(?:image|picture|illustration|artwork|logo|icon|poster|封面|配图)\b",
        r"\u751f\u6210\u56fe\u7247|\u753b\u56fe|\u521b\u4f5c\u63d2\u56fe|\u751f\u6210\u56fe\u50cf|\u8bbe\u8ba1\u56fe\u7247|\u505a\u56fe",
    ),
    "audio": (
        r"\b(?:audio|speech|voice|transcription|transcribe|podcast|recording|sound|音频|语音|转录|听写|录音)\b",
        r"\u97f3\u9891|\u8bed\u97f3|\u8f6c\u5f55|\u542c\u5199|\u5f55\u97f3|\u58f0\u97f3|\u64ad\u97f3",
    ),
    "video": (
        r"\b(?:video|film|movie|clip|animation|footage|视频|影片|影像|动画|录像)\b",
        r"\u89c6\u9891|\u5f71\u50cf|\u89c6\u9891\u5206\u6790|\u52a8\u753b|\u5f55\u50cf|\u7247\u6bb5",
    ),
    "computer_control": (
        r"\b(?:click|browser|desktop|computer|screen|game|play|open\s+the\s+app|automate|操作电脑|浏览器|桌面|点击|打游戏|操作窗口|自动化)\b",
        r"\u64cd\u4f5c\u7535\u8111|\u6d4f\u89c8\u5668|\u684c\u9762|\u70b9\u51fb|\u6253\u6e38\u620f|\u64cd\u4f5c\u7a97\u53e3|\u81ea\u52a8\u5316",
    ),
    "web_access": (
        r"\b(?:search|research|online|latest|news|fact[- ]?check|browse|sources?|查资料|网上查|最新|新闻|核实|文献|网页资料)\b",
        r"\u641c\u7d22|\u67e5\u8d44\u6599|\u7f51\u4e0a|\u6700\u65b0|\u65b0\u95fb|\u6838\u5b9e|\u6587\u732e|\u7f51\u9875\u8d44\u6599",
    ),
    "artifact_generation": (
        r"\b(?:pptx?|powerpoint|slide|presentation|document|docx|spreadsheet|excel|xlsx|pdf|table|word|报告|演示文稿|幻灯片|文档|表格|电子表格|导出文件)\b",
        r"PPT|\u5e7b\u706f\u7247|\u6f14\u793a\u6587\u7a3f|\u6587\u6863|\u8868\u683c|\u7535\u5b50\u8868\u683c|\u62a5\u544a|\u5bfc\u51fa\u6587\u4ef6",
    ),
    "scientific_computing": (
        r"\b(?:simulation|numerical|scientific|physics|engineering|statistics|modeling|calculation|仿真|数值计算|科学计算|物理|工程|统计建模|模拟)\b",
        r"\u4eff\u771f|\u6570\u503c\u8ba1\u7b97|\u79d1\u5b66\u8ba1\u7b97|\u7269\u7406|\u5de5\u7a0b|\u7edf\u8ba1\u5efa\u6a21|\u6a21\u62df",
    ),
    "biology": (
        r"\b(?:biology|genome|genomics|protein|bioinformatics|gene|cell|dna|rna|sequence|生物|基因|基因组|蛋白|生物信息|细胞|序列)\b",
        r"\u751f\u7269|\u57fa\u56e0|\u57fa\u56e0\u7ec4|\u86cb\u767d|\u751f\u7269\u4fe1\u606f|\u7ec6\u80de|\u5e8f\u5217",
    ),
    "long_context": (
        r"\b(?:whole\s+repository|entire\s+codebase|long\s+document|large\s+dataset|full\s+archive|全仓库|整个代码库|长文档|大型数据集|全量资料)\b",
        r"\u5168\u4ed3\u5e93|\u6574\u4e2a\u4ee3\u7801\u5e93|\u957f\u6587\u6863|\u5927\u578b\u6570\u636e\u96c6|\u5168\u91cf\u8d44\u6599",
    ),
    "deep_reasoning": (
        r"\b(?:complex proof|difficult architecture|hard problem|formal reasoning|complex simulation|复杂证明|复杂架构|高难度|深度推理|复杂仿真)\b",
        r"\u590d\u6742\u8bc1\u660e|\u590d\u6742\u67b6\u6784|\u9ad8\u96be\u5ea6|\u6df1\u5ea6\u63a8\u7406|\u590d\u6742\u4eff\u771f",
    ),
    "system_security": (
        r"\b(?:virus|trojan|malware|ransomware|defender|system\s+scan|startup\s+entries|木马|病毒|恶意软件|勒索软件|扫描系统|启动项|安全排查)\b",
        r"\u6728\u9a6c|\u75c5\u6bd2|\u6076\u610f\u8f6f\u4ef6|\u52d2\u7d22\u8f6f\u4ef6|\u626b\u63cf\u7cfb\u7edf|\u542f\u52a8\u9879|\u5b89\u5168\u6392\u67e5",
    ),
    "speech_recognition": (
        r"\b(?:speech[- ]to[- ]text|stt|transcribe|voice\s+recognition|语音转文字|语音识别|听写)\b",
        r"\u8bed\u97f3\u8f6c\u6587\u5b57|\u8bed\u97f3\u8bc6\u522b|\u542c\u5199",
    ),
    "ocr": (
        r"\b(?:ocr|text\s+extraction|document\s+parsing|图片文字提取|文档解析)\b",
        r"OCR|\u56fe\u7247\u6587\u5b57\u63d0\u53d6|\u6587\u6863\u89e3\u6790",
    ),
}

COMPILED_PATTERNS = {
    capability: tuple(re.compile(pattern, re.I) for pattern in patterns)
    for capability, patterns in CAPABILITY_PATTERNS.items()
}

HIGH_RISK_MARKERS = re.compile(
    r"\b(?:security|medical|legal|financial|credential|production|payment|virus|malware)\b|"
    r"\u5b89\u5168|\u533b\u7597|\u6cd5\u5f8b|\u8d22\u52a1|\u51ed\u636e|\u751f\u4ea7|\u652f\u4ed8|\u75c5\u6bd2|\u6728\u9a6c",
    re.I,
)


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def required_capabilities(task: str) -> list[str]:
    """Infer capabilities conservatively; the host model must confirm intent."""
    if not isinstance(task, str):
        raise TypeError("task must be a string")
    return [
        capability
        for capability, patterns in COMPILED_PATTERNS.items()
        if any(pattern.search(task) for pattern in patterns)
    ]


def _as_capabilities(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {str(item).strip() for item in value if str(item).strip()}


def _normalize_model(raw: Any, *, current: bool = False) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("each model must be an object")
    model_id = raw.get("id")
    if not isinstance(model_id, str) or not model_id.strip():
        raise ValueError("each model needs a non-empty string id")
    return {
        "id": model_id.strip(),
        "provider": str(raw.get("provider", "unknown")),
        "capabilities": sorted(_as_capabilities(raw.get("capabilities", []))),
        "configured": bool(raw.get("configured", current)),
        "enabled": bool(raw.get("enabled", True)),
        "quality_tier": int(raw.get("quality_tier", 0) or 0),
        "cost_tier": int(raw.get("cost_tier", 2) or 2),
        "context_window": int(raw.get("context_window", 0) or 0),
        "api_key_env": (
            raw.get("api_key_env")
            if isinstance(raw.get("api_key_env"), str)
            and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", raw["api_key_env"])
            else None
        ),
    }


def normalize_catalog(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("catalog must be a JSON object")
    current_raw = raw.get("current_model", DEFAULT_CURRENT_MODEL)
    current = _normalize_model(current_raw, current=True)
    models_raw = raw.get("models", [])
    if not isinstance(models_raw, list):
        raise ValueError("catalog.models must be a list")
    models = [_normalize_model(item) for item in models_raw]
    if not any(model["id"] == current["id"] for model in models):
        models.insert(0, current)
    return {"current_model": current, "models": models}


def load_catalog(path: str | Path) -> dict[str, Any]:
    catalog_path = Path(path).expanduser()
    try:
        raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read catalog: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid catalog JSON: {exc.msg}") from exc
    return normalize_catalog(raw)


def _public_model(model: dict[str, Any]) -> dict[str, Any]:
    """Return metadata safe for logs and prompts; never return secret values."""
    result = {
        "id": model["id"],
        "provider": model["provider"],
        "capabilities": model["capabilities"],
        "configured": model["configured"],
        "enabled": model["enabled"],
        "quality_tier": model["quality_tier"],
        "cost_tier": model["cost_tier"],
        "context_window": model["context_window"],
    }
    if model.get("api_key_env"):
        result["api_key_env"] = model["api_key_env"]
    return result


def _available(model: dict[str, Any]) -> bool:
    return bool(model["configured"] and model["enabled"])


def _estimate_effort(task: str, required: list[str]) -> str:
    score = len(required) * 2
    if len(task) > 600:
        score += 2
    if len(required) >= 4:
        score += 2
    if any(capability in required for capability in ("long_context", "deep_reasoning")):
        score += 2
    if score >= 8:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


def _quality_risk(task: str, required: list[str], current: dict[str, Any], effort: str) -> str:
    missing = set(required) - set(current["capabilities"])
    if missing or HIGH_RISK_MARKERS.search(task) or effort == "high":
        return "high"
    if len(required) >= 2 or current["quality_tier"] < 2:
        return "medium"
    return "low"


def _candidate_score(model: dict[str, Any], required: set[str], current: dict[str, Any]) -> tuple[int, int, int, int]:
    capabilities = set(model["capabilities"])
    coverage = len(required & capabilities)
    quality_gain = model["quality_tier"] - current["quality_tier"]
    context = model["context_window"]
    cost_penalty = -model["cost_tier"]
    return (coverage, quality_gain, context, cost_penalty)


def select_model(task: str, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(task, str):
        raise TypeError("task must be a string")
    catalog = normalize_catalog(catalog or {"current_model": DEFAULT_CURRENT_MODEL, "models": []})
    current = catalog["current_model"]
    models = catalog["models"]
    required = required_capabilities(task)
    required_set = set(required)
    missing = sorted(required_set - set(current["capabilities"]))
    effort = _estimate_effort(task, required)
    quality_risk = _quality_risk(task, required, current, effort)
    available = [model for model in models if model["id"] != current["id"] and _available(model)]
    complete_candidates = [model for model in available if required_set <= set(model["capabilities"])]
    complete_candidates.sort(key=lambda model: _candidate_score(model, required_set, current), reverse=True)

    # Greedy set cover lets a mixed task use several bounded helpers, for example
    # one vision model plus one artifact-capable model.
    selected_helpers: list[dict[str, Any]] = []
    uncovered = set(missing)
    remaining = list(available)
    while uncovered:
        choices = [model for model in remaining if uncovered & set(model["capabilities"])]
        if not choices:
            break
        choices.sort(
            key=lambda model: (
                len(uncovered & set(model["capabilities"])),
                model["quality_tier"],
                model["context_window"],
                -model["cost_tier"],
            ),
            reverse=True,
        )
        chosen = choices[0]
        selected_helpers.append(chosen)
        uncovered -= set(chosen["capabilities"])
        remaining.remove(chosen)

    selected = complete_candidates[0] if complete_candidates else (selected_helpers[0] if selected_helpers and not uncovered else None)
    decision = "use_current"
    if missing:
        decision = "delegate_missing_capability" if selected_helpers and not uncovered else "request_user_configuration"
    elif quality_risk == "high":
        better = [
            model for model in available
            if required_set <= set(model["capabilities"])
            and (model["quality_tier"] > current["quality_tier"] or model["context_window"] > current["context_window"])
        ]
        better.sort(key=lambda model: _candidate_score(model, required_set, current), reverse=True)
        if better:
            selected = better[0]
            selected_helpers = [selected]
            decision = "switch_for_quality"

    if decision == "use_current":
        selected = None
        selected_helpers = []

    needs_configuration = decision == "request_user_configuration"
    if decision == "request_user_configuration":
        capability_probe = {
            "questions": [
                "Which configured model or provider supplies the missing capabilities?",
                "Is the required endpoint/API key available through environment variables?",
                "What data may be transferred to that helper model?",
            ],
            "catalog_fields": ["id", "provider", "capabilities", "configured", "api_key_env"],
        }
    else:
        capability_probe = {"questions": [], "catalog_fields": []}

    # Build auto-trigger hints for each helper
    trigger_hints: dict[str, list[str]] = {}
    for helper in selected_helpers:
        helper_caps = set(helper["capabilities"])
        triggered_by = sorted(required_set & helper_caps)
        trigger_hints[helper["id"]] = triggered_by

    return {
        "decision": decision,
        "required_capabilities": required,
        "current_model": _public_model(current),
        "capability_gaps": missing,
        "estimated_effort": effort,
        "quality_risk": quality_risk,
        "selected_helper": _public_model(selected) if selected else None,
        "selected_helpers": [_public_model(model) for model in selected_helpers],
        "unmet_after_selection": sorted(uncovered),
        "fallback_candidates": [_public_model(model) for model in complete_candidates[:5]],
        "needs_user_configuration": needs_configuration,
        "auto_trigger_hints": trigger_hints,
        "switch_request": {
            "missing_capabilities": missing,
            "context_to_transfer": ["task_goal", "relevant_inputs", "acceptance_criteria"],
            "do_not_transfer": ["secrets", "credentials", "unrelated_files", "private_data_without_consent"],
        },
        "capability_probe": capability_probe,
        "primary_model_owns": [
            "intent_and_scope",
            "final_model_choice",
            "sensitive_data_filtering",
            "critical_path",
            "result_review",
            "final_synthesis",
        ],
        "execution_note": (
            "This is a recommendation protocol. It does not call external APIs. "
            "Only configured and enabled models may be selected."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", nargs="*", help="task text; stdin is used when omitted")
    parser.add_argument("--catalog", type=Path, help="path to a user-maintained model catalog JSON")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    task = " ".join(args.task).strip()
    if not task:
        import sys
        task = sys.stdin.read().strip()
    try:
        catalog = load_catalog(args.catalog) if args.catalog else None
        result = select_model(task, catalog)
    except (TypeError, ValueError) as exc:
        if args.as_json:
            print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        else:
            print(f"error: {exc}")
        return 2
    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Decision: {result['decision']}")
        print(f"Required: {', '.join(result['required_capabilities']) or 'none'}")
        print(f"Gaps: {', '.join(result['capability_gaps']) or 'none'}")
        if result["selected_helpers"]:
            print("Selected helpers: " + ", ".join(model["id"] for model in result["selected_helpers"]))
            for helper_id, caps in result.get("auto_trigger_hints", {}).items():
                print(f"  {helper_id} triggered by: {', '.join(caps)}")
        if result["needs_user_configuration"]:
            print("User configuration is required before delegation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())