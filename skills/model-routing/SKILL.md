---
name: model-routing
description: Assess task capabilities against the current model, tools, and explicitly configured helper models; choose current execution, bounded delegation, a quality switch, or a safe request for user configuration without exposing secrets.
---

# Model routing and intelligent choice

Use this skill whenever a request may exceed the current model's modalities, context, tools, quality, or reasonable effort budget. The goal is not to call a random model: it is to make a transparent, capability-aware decision and keep the primary model in control.

## Decision procedure

1. Parse the requested outcome, inputs, domains, risk, freshness needs, and required evidence.
2. Inspect the host's actual capabilities and tools. Treat an ability as available only when the host exposes it or the user has configured a helper model/tool for it.
3. Infer required capabilities such as `vision`, `audio`, `video`, `computer_control`, `web_access`, `artifact_generation`, `scientific_computing`, `biology`, `long_context`, `deep_reasoning`, or `system_security`.
4. Classify the current path as:
   - `use_current`: the current model and tools are sufficient;
   - `delegate_missing_capability`: a configured helper covers a bounded missing capability;
   - `switch_for_quality`: a configured helper is materially better for a high-effort or high-risk task;
   - `request_user_configuration`: a required capability has no configured provider;
   - `blocked`: no safe path exists or authorization is missing.
5. Select the smallest helper that covers the gap. For mixed tasks, delegate only the modality-specific or independently verifiable part; keep intent, critical path, sensitive-data filtering, safety gates, integration, and final synthesis with the primary model.
6. Before transfer, minimize context. Send the goal, relevant input, acceptance criteria, and necessary excerpts only. Never send secrets, credentials, unrelated files, or private data without consent.
7. Record the helper model ID/provider, capability covered, input scope, time, result status, uncertainty, and whether the primary model independently verified it.

## Catalog and API rules

- Use `scripts/model_selector.py` for a deterministic recommendation. It reads a user-maintained catalog and does not make network calls.
- A model is selectable only when it is explicitly `configured: true` and `enabled: true`. Do not assume a provider, endpoint, API key, or vision model exists.
- Store API keys only in environment variables or the host secret manager. Catalogs may name an `api_key_env` variable but must never contain the key value.
- Do not put keys in prompts, logs, artifacts, test fixtures, or delegated context.
- If the user provides temporary API access, use the narrowest scope, avoid persistent configuration, delete temporary files/configuration after the task, and report cleanup. Do not silently retain credentials.
- External calls require the host's network/tool permission and any required user authorization. If the provider is unavailable, state the gap instead of fabricating a result.

## Mixed-task pattern

For a request such as "inspect this image, research the claims, and make a presentation":

1. The primary model defines the acceptance criteria and sensitive-data policy.
2. A configured vision helper extracts image facts; a web-capable helper gathers dated sources; an artifact-capable path creates the presentation.
3. Each worker returns structured findings with provenance and uncertainty.
4. The primary model reconciles conflicts, checks high-impact claims, generates or edits the artifact, and performs final verification.

## Output contract

Every routing decision should expose:

- required capabilities and current capability gaps;
- estimated effort and quality risk;
- selected helper and rejected/available alternatives;
- user configuration needed, if any;
- context allowed to transfer and data that must not transfer;
- verification and fallback plan.

The script is a recommendation aid, not an authorization or security boundary. The host must still confirm side effects and enforce tool permissions.