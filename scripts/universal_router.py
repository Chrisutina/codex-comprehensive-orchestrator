#!/usr/bin/env python3
"""Context-aware first-pass router for broad Codex tasks.

The router separates human-facing domains from canonical Skill IDs. It is a
hint, not an authorization layer: the host model must inspect intent, tools,
model capabilities, and confirmation requirements before acting.
"""
from __future__ import annotations

import argparse
import json
import re
from typing import Iterable


def _compile(pattern: str, flags: int = 0) -> re.Pattern[str]:
    return re.compile(pattern, flags | re.I)


DOMAIN_RULES: dict[str, re.Pattern[str]] = {
    "software": _compile(
        r"(?:\b(?:code|program|website|web\s+app|bug|api|repository|software|playwright)\b|"
        r"\u4ee3\u7801|\u7a0b\u5e8f|\u7f51\u9875|\u7f51\u7ad9|\u8f6f\u4ef6|\u63a5\u53e3|\u4ed3\u5e93|\u5e94\u7528\u7a0b\u5e8f)"
    ),
    "artifact-studio": _compile(
        r"(?:\b(?:word|docx|document|report|pptx?|powerpoint|slide|presentation|excel|xlsx|"
        r"spreadsheet|csv|table|pdf|artifact)\b|\u6587\u6863|\u62a5\u544a|\u5e7b\u706f\u7247|\u6f14\u793a\u6587\u7a3f|\u8868\u683c|\u7535\u5b50\u8868\u683c|\u6587\u4ef6\u5de5\u4ef6|PPT)"
    ),
    "computer-operation": _compile(
        r"(?:\b(?:open|click|browser|desktop|computer|screen|game|play|app)\b|"
        r"\u64cd\u4f5c\u7535\u8111|\u64cd\u4f5c\u6d4f\u89c8\u5668|\u6d4f\u89c8\u5668|\u684c\u9762\u8f6f\u4ef6|\u70b9\u51fb|\u6253\u6e38\u620f|\u6e38\u620f|\u622a\u56fe)"
    ),
    "system-safety": _compile(
        r"(?:\b(?:virus|trojan|malware|ransomware|suspicious\s+file|defender|scan\s+system)\b|"
        r"\u6728\u9a6c|\u75c5\u6bd2|\u6076\u610f\u8f6f\u4ef6|\u52d2\u7d22\u8f6f\u4ef6|\u53ef\u7591\u6587\u4ef6|\u626b\u63cf\u7cfb\u7edf|\u542f\u52a8\u9879|\u6301\u4e45\u5316)"
    ),
    "simulation-biology": _compile(
        r"(?:\b(?:simulation|physics|engineering|genome|genomics|bioinformatics|biology|protein|"
        r"scientific\s+computing|statistics)\b|\u751f\u7269|\u57fa\u56e0|\u86cb\u767d|\u4eff\u771f|\u6a21\u62df|\u79d1\u5b66\u8ba1\u7b97|\u751f\u7269\u4fe1\u606f|\u7edf\u8ba1\u5206\u6790)"
    ),
    "web-research": _compile(
        r"(?:\b(?:search|research|online|latest|news|fact[- ]?check|misinformation|claim|source\s+quality)\b|"
        r"\u67e5\u8d44\u6599|\u7f51\u4e0a\u67e5|\u6700\u65b0|\u65b0\u95fb|\u4e8b\u5b9e\u6838\u67e5|\u8bef\u5bfc|\u6765\u6e90\u6838\u9a8c|\u6587\u732e\u68c0\u7d22|\u8d44\u6599\u6838\u5b9e)"
    ),
    "humanities": _compile(
        r"(?:\b(?:poem|poetry|literature|philosophy|quote|aphorism|rhetoric|translation)\b|"
        r"\u8bd7|\u8bd7\u6587|\u6587\u5b66|\u54f2\u5b66|\u8bed\u5f55|\u540d\u8a00|\u8d4f\u6790|\u7ffb\u8bd1|\u4fee\u8f9e)"
    ),
    "problem-solving": _compile(
        r"(?:\b(?:why|how|compare|decision|strategy|trade[- ]?off|recommend)\b|"
        r"\u5206\u6790|\u4e3a\u4ec0\u4e48|\u5982\u4f55|\u65b9\u6848|\u51b3\u7b56|\u6bd4\u8f83|\u6743\u8861|\u5efa\u8bae|\u89e3\u51b3\u95ee\u9898)"
    ),
}

SKILL_RULES: dict[str, re.Pattern[str]] = {
    "code-audit": _compile(
        r"(?:\b(?:audit|review|vulnerability|security\s+review|code\s+review)\b|\u4ee3\u7801\u5ba1\u8ba1|\u4ee3\u7801\u5ba1\u67e5|\u6f0f\u6d1e\u5ba1\u8ba1|\u5b89\u5168\u5ba1\u8ba1)"
    ),
    "test-engineering": _compile(
        r"(?:\b(?:tests?|testing|regression|pytest|unit\s+tests?|integration\s+tests?|test\s+plan)\b|\u6d4b\u8bd5|\u56de\u5f52\u6d4b\u8bd5|\u6d4b\u8bd5\u8ba1\u5212|\u9a8c\u6536\u6d4b\u8bd5)"
    ),
}

P0_RULES = _compile(
    r"(?:\b(?:production|outage|data\s+loss|breach|payment|deploy|delete|quarantine|kill|purchase)\b|"
    r"\u751f\u4ea7\u73af\u5883|\u5bb5\u673a|\u6570\u636e\u4e22\u5931|\u6cc4\u9732|\u652f\u4ed8|\u90e8\u7f72|\u5220\u9664|\u9694\u79bb|\u7ec8\u6b62\u8fdb\u7a0b|\u8d2d\u4e70)"
)
P1_RULES = _compile(
    r"(?:\b(?:security|auth|permission|medical|legal|financial|credential|account\s+settings)\b|"
    r"\u5b89\u5168|\u8ba4\u8bc1|\u6743\u9650|\u533b\u7597|\u6cd5\u5f8b|\u8d22\u52a1|\u51ed\u636e|\u8d26\u53f7\u8bbe\u7f6e|\u9690\u79c1)"
)

SIDE_EFFECT_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "external-or-destructive-confirmation",
        _compile(
            r"(?:\b(?:delete|remove|erase|wipe|quarantine|kill|terminate|install|publish|send|"
            r"purchase|deploy|submit|upload|format|reset|change\s+settings|click\s+submit)\b|"
            r"\u5220\u9664|\u79fb\u9664|\u64e6\u9664|\u6e05\u7a7a|\u9694\u79bb|\u7ec8\u6b62|\u5b89\u88c5|\u53d1\u5e03|\u53d1\u9001|\u8d2d\u4e70|\u90e8\u7f72|\u63d0\u4ea4|\u4e0a\u4f20|\u683c\u5f0f\u5316|\u91cd\u7f6e|\u4fee\u6539\u8bbe\u7f6e|\u70b9\u51fb\u63d0\u4ea4)"
        ),
    ),
    (
        "local-reversible-edit",
        _compile(
            r"(?:\b(?:write|edit|modify|generate|create\s+(?:a\s+)?(?:file|document|presentation|spreadsheet)|save)\b|"
            r"\u5199\u5165|\u7f16\u8f91|\u4fee\u6539|\u751f\u6210|\u5236\u4f5c|\u521b\u5efa\u6587\u4ef6|\u521b\u5efa\u6587\u6863|\u5236\u4f5cPPT|\u5236\u4f5c\u8868\u683c|\u4fdd\u5b58)"
        ),
    ),
)

NEGATION_RULE = _compile(
    r"(?:\b(?:do\s+not|don't|does\s+not|never|without|no\s+need\s+to|avoid)\b|"
    r"\u7981\u6b62|\u4e0d\u8981|\u522b|\u52ff|\u65e0\u9700|\u4e0d\u9700\u8981|\u4ec5\u5206\u6790|\u53ea\u8bfb)\s*$"
)

CANONICAL_SKILLS = {
    "orchestrate",
    "artifact-studio",
    "computer-operation",
    "system-safety",
    "simulation-biology",
    "web-research",
    "humanities",
    "code-audit",
    "test-engineering",
    "problem-solving",
}


def _active_matches(text: str, pattern: re.Pattern[str]) -> list[str]:
    """Return matches not immediately negated by the user's wording."""
    active: list[str] = []
    for match in pattern.finditer(text):
        prefix = text[: match.start()].rstrip()
        context = prefix[-32:]
        if NEGATION_RULE.search(context):
            continue
        active.append(match.group(0))
    return active


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def classify(text: str) -> dict:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    text = text.strip()
    domains = [name for name, pattern in DOMAIN_RULES.items() if pattern.search(text)]
    skills = [name for name, pattern in SKILL_RULES.items() if pattern.search(text)]

    if not domains:
        domains = ["problem-solving"]
    if "problem-solving" in domains and len(domains) > 1:
        domains.remove("problem-solving")
    if "orchestrate" not in skills:
        skills.insert(0, "orchestrate")

    if "artifact-studio" in domains:
        skills.append("artifact-studio")
    for domain in domains:
        if domain in CANONICAL_SKILLS and domain not in {"software", "problem-solving"}:
            skills.append(domain)
    if "software" in domains and not any(skill in skills for skill in ("code-audit", "test-engineering")):
        skills.append("problem-solving")
    if "problem-solving" in domains:
        skills.append("problem-solving")
    skills = [skill for skill in _unique(skills) if skill in CANONICAL_SKILLS]

    active_p0 = _active_matches(text, P0_RULES)
    active_p1 = _active_matches(text, P1_RULES)
    priority = "P2"
    if active_p0:
        priority = "P0"
    elif active_p1:
        priority = "P1"

    side_effect = "read-only"
    side_effect_evidence: list[str] = []
    for level, pattern in SIDE_EFFECT_RULES:
        active = _active_matches(text, pattern)
        if active:
            side_effect = level
            side_effect_evidence = _unique(active)
            break

    return {
        "domains": _unique(["orchestrate", *domains]),
        "skills": skills,
        "priority": priority,
        "risk_signals": {"p0": _unique(active_p0), "p1": _unique(active_p1)},
        "side_effect_level": side_effect,
        "side_effect_evidence": side_effect_evidence,
        "primary_model_owns": [
            "intent",
            "critical_path",
            "capability_choice",
            "safety_gates",
            "integration",
            "final_verification",
            "final_answer",
        ],
        "parallel_candidates": [
            "inventory",
            "independent_review",
            "research",
            "test_design",
            "visual_or_structural_check",
            "capability_probe",
        ],
        "note": (
            "Heuristics are a starting point. The host model must inspect intent, "
            "negation, available tools/models, and confirmation requirements before acting."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="*", help="task text; stdin is used when omitted")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    text = " ".join(args.text).strip()
    if not text:
        import sys
        text = sys.stdin.read().strip()
    result = classify(text)
    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Domains: {', '.join(result['domains'])}")
        print(f"Skills: {', '.join(result['skills'])}")
        print(f"Priority: {result['priority']}")
        print(f"Side effects: {result['side_effect_level']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())