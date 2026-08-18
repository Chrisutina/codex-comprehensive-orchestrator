#!/usr/bin/env python3
"""Capability probing and auto-detection for configured providers.

This script probes configured providers to discover available models and their
capabilities, updating the local catalog with detected capabilities. It never
stores API keys and only uses them for the duration of the probe request.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# Pattern-based capability inference from model IDs
CAPABILITY_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "vision": [
        re.compile(r"vision|vl|image|multimodal|4o|claude-3|gemini", re.I),
        re.compile(r"llava|bakllava|moondream", re.I),
    ],
    "audio": [
        re.compile(r"audio|whisper|speech|voice|turbo", re.I),
    ],
    "video": [
        re.compile(r"video|sora|veo|runway|pika", re.I),
    ],
    "image_generation": [
        re.compile(r"dall-e|stable-diffusion|midjourney|flux|imagegen", re.I),
    ],
    "speech_recognition": [
        re.compile(r"whisper|speech-to-text|stt|transcri", re.I),
    ],
    "ocr": [
        re.compile(r"ocr|text-extract|document", re.I),
    ],
    "long_context": [
        re.compile(r"long|128k|200k|1m|claude-3|gemini-1\.5", re.I),
    ],
    "code": [
        re.compile(r"code|codex|starcoder|deepseek-coder", re.I),
    ],
    "reasoning": [
        re.compile(r"reason|think|o1|o3|r1", re.I),
    ],
    "web_access": [
        re.compile(r"web|search|browse|online", re.I),
    ],
}


def infer_capabilities(model_id: str) -> list[str]:
    """Infer capabilities from model ID using pattern matching."""
    caps: list[str] = ["text"]  # All models get text by default
    for cap, patterns in CAPABILITY_PATTERNS.items():
        if any(p.search(model_id) for p in patterns):
            caps.append(cap)
    return caps


def probe_openai_compatible(
    base_url: str, api_key: str, timeout: int = 30
) -> list[dict[str, Any]]:
    """Probe an OpenAI-compatible /v1/models endpoint."""
    url = f"{base_url.rstrip('/')}/v1/models"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = data.get("data", [])
            return [
                {
                    "id": m.get("id", "unknown"),
                    "capabilities": infer_capabilities(m.get("id", "")),
                }
                for m in models
            ]
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as exc:
        print(f"  probe failed for {url}: {exc}")
        return []


def probe_ollama(base_url: str, timeout: int = 30) -> list[dict[str, Any]]:
    """Probe a local Ollama /api/tags endpoint."""
    url = f"{base_url.rstrip('/')}/api/tags"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = data.get("models", [])
            return [
                {
                    "id": m.get("name", "unknown"),
                    "capabilities": infer_capabilities(m.get("name", "")),
                }
                for m in models
            ]
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as exc:
        print(f"  probe failed for {url}: {exc}")
        return []


def probe_provider(
    provider: str, base_url: str | None, api_key_env: str | None, timeout: int = 30
) -> list[dict[str, Any]]:
    """Probe a provider and return discovered models with capabilities."""
    api_key = os.environ.get(api_key_env) if api_key_env else None
    if api_key_env and not api_key:
        print(f"  skipping {provider}: {api_key_env} not set")
        return []

    if provider == "openai":
        return probe_openai_compatible(
            base_url or "https://api.openai.com", api_key or "", timeout
        )
    if provider == "anthropic":
        # Anthropic doesn't have a public list endpoint; return empty
        # and rely on catalog declaration
        print(f"  {provider}: no public model list endpoint, using catalog declaration")
        return []
    if provider == "qwen":
        return probe_openai_compatible(
            base_url or "https://dashscope.aliyuncs.com/compatible-mode",
            api_key or "",
            timeout,
        )
    if provider == "ollama":
        return probe_ollama(base_url or "http://localhost:11434", timeout)
    if provider == "local":
        print(f"  {provider}: local models require manual capability declaration")
        return []

    print(f"  {provider}: unknown provider type, skipping probe")
    return []


def merge_capabilities(
    declared: list[str], detected: list[str]
) -> tuple[list[str], list[str]]:
    """Merge declared and detected capabilities; return (merged, newly_detected)."""
    declared_set = set(declared)
    detected_set = set(detected)
    merged = sorted(declared_set | detected_set)
    newly_detected = sorted(detected_set - declared_set)
    return merged, newly_detected


def probe_and_update_catalog(
    catalog_path: Path, timeout: int = 30, dry_run: bool = False
) -> dict[str, Any]:
    """Probe all configured providers and update the catalog."""
    raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    models = raw.get("models", [])
    probing_config = raw.get("capability_probing", {})

    if not probing_config.get("enabled", False):
        return {"status": "probing_disabled", "models_updated": 0}

    results: list[dict[str, Any]] = []
    updated_count = 0

    for model in models:
        if not model.get("enabled", True):
            continue
        if not model.get("configured", False):
            continue

        provider = model.get("provider", "unknown")
        model_id = model.get("id", "unknown")
        base_url = model.get("base_url")
        api_key_env = model.get("api_key_env")

        print(f"Probing {provider}/{model_id}...")
        detected = probe_provider(provider, base_url, api_key_env, timeout)

        if not detected:
            continue

        # Find the specific model in detected results
        detected_caps: list[str] = []
        for d in detected:
            if d["id"] == model_id:
                detected_caps = d["capabilities"]
                break

        if not detected_caps:
            # Model not found in provider list; use provider-level detection
            # or keep declared capabilities
            print(f"  model {model_id} not found in provider list")
            continue

        declared = model.get("capabilities", [])
        merged, newly_detected = merge_capabilities(declared, detected_caps)

        if newly_detected:
            print(f"  newly detected capabilities: {newly_detected}")
            updated_count += 1

        if not dry_run:
            model["capabilities"] = merged
            model["auto_detected_capabilities"] = newly_detected

        results.append(
            {
                "model_id": model_id,
                "provider": provider,
                "declared": declared,
                "detected": detected_caps,
                "newly_detected": newly_detected,
                "merged": merged,
            }
        )

    if not dry_run and updated_count > 0:
        catalog_path.write_text(
            json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    return {
        "status": "probed",
        "models_updated": updated_count,
        "results": results,
        "dry_run": dry_run,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path("model_catalog.json"),
        help="path to model catalog JSON",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="probe timeout in seconds",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would be updated without writing",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    if not args.catalog.exists():
        print(f"error: catalog not found at {args.catalog}")
        return 2

    result = probe_and_update_catalog(args.catalog, args.timeout, args.dry_run)

    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\nProbing complete: {result['models_updated']} models updated")
        if result["dry_run"]:
            print("(dry run — no changes written)")
        for r in result["results"]:
            if r["newly_detected"]:
                print(f"  {r['model_id']}: +{r['newly_detected']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
