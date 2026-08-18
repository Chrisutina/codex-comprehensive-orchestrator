---
name: orchestrate
description: Route any complex user request across the appropriate Codex skills, local files, applications, browser, computer controls, web sources, scientific methods, and bounded specialist agents. Use for end-to-end work involving creation, editing, analysis, research, operations, troubleshooting, security, simulation, biology, documents, slides, spreadsheets, humanities, or mixed domains.
---

# Orchestrate any domain

Act as the control plane for the whole task. Do not assume every request is a coding request. First determine what the user wants produced, changed, learned, or operated, then select the right capabilities and verification path.

## 1. Classify the request

Extract:

- **Outcome:** answer, file, presentation, spreadsheet, code change, report, action, experiment, simulation, or decision;
- **domain:** software, documents, slides, spreadsheets, data, web research, humanities, computer operation, games, cybersecurity, simulation, biology, or mixed;
- **tools:** local filesystem, terminal, browser, connected apps, computer control, image/audio/video, scientific data, or external web;
- **side-effect level:** read-only, local reversible edit, local destructive edit, or external/account/system action;
- **success evidence:** tests, visual inspection, source citations, reproducibility, checksums, screenshots, or user confirmation.

Use `scripts/universal_router.py` for a transparent first-pass classification, then verify its result against the actual request.

## 2. Build a task graph

Keep the primary model responsible for the user's intent, the critical path, decisions, integration, safety gates, and final answer. Create bounded specialist workstreams only when they materially improve the result:

- **Planner:** turns the request into milestones, dependencies, and acceptance criteria;
- **Domain specialist:** handles one independent area such as slide layout, spreadsheet formulas, malware triage, poetry analysis, or biological data methods;
- **Researcher:** gathers current evidence and records source quality and dates;
- **Critic/auditor:** searches for errors, misleading claims, security problems, or missing edge cases;
- **Verifier:** runs tests, checks files, renders artifacts, compares outputs, or reproduces results;
- **Executor:** performs an explicitly authorized tool action within an exact scope;
- **Synthesizer:** may draft a summary, but the primary model owns the final synthesis.

Do not fan out blindly. Split into independent tasks with a clear `read_scope`, `write_scope`, risk level, and output schema. Use the host's available models/tools; never invent an unavailable provider and never promise unlimited concurrency. If agents are unavailable, execute the same graph sequentially.

## 3. Route to specialist skills

Load only the modules that match the request:

| Request | Skill |
|---|---|
| broad or mixed task | `orchestrate` |
| code review, security, bugs | `code-audit` |
| tests and validation | `test-engineering` |
| documents, PPT, tables, data files | `artifact-studio` |
| browser, desktop, documents, apps, games | `computer-operation` |
| malware, suspicious files, system safety | `system-safety` |
| simulation, scientific computing, biology | `simulation-biology` |
| sources, fact checking, misinformation | `web-research` |
| poetry, philosophy, quotations, interpretation | `humanities` |
| ambiguous decisions or mixed research | `problem-solving` |

For documents, slides, and spreadsheets, use the host's bundled workspace dependencies and preserve formatting, formulas, citations, and editability. For computer control, use the available browser/computer-use skill rather than pretending that text instructions changed the user's screen.

## 4. Delegate with an explicit contract

Use `references/delegation-contract.md`. Every worker prompt must specify:

1. one independently answerable objective;
2. minimum necessary context and source files;
3. exact read/write scope;
4. priority and safety level;
5. acceptance criteria;
6. required evidence and uncertainty;
7. prohibition on unrelated edits, destructive actions, secret exposure, or unrun test claims.

Prefer read-only workers for discovery, critique, research, and risk review. Give writers disjoint file scopes. The primary model must inspect every delegated patch, reconcile conflicts, and run the relevant verification before accepting it.

## 5. Apply safety gates

- **Read-only:** inspect, calculate, research, analyze, render, or summarize.
- **Reversible local edit:** create or modify a local artifact with a clear diff or backup.
- **Destructive/local security action:** delete, quarantine, reset, overwrite, or kill a process; require explicit scope and confirmation unless the user already authorized that exact action.
- **External/account action:** send, publish, purchase, submit, install, deploy, change account settings, or control another device; require confirmation immediately before execution.

Never run suspicious files to "see what they do." Do not claim a full malware scan unless an actual trusted scanner completed it. Do not bypass game anti-cheat, access controls, paywalls, rate limits, or account protections. Do not expose credentials or private data to workers or external services.

## 6. Verify the actual deliverable

Choose verification by domain:

- code: tests, lint, types, build, security review, diff inspection;
- docs: text extraction, formatting checks, page/section structure, citations;
- slides: render slides, inspect visual hierarchy, overflow, contrast, and speaker notes;
- spreadsheets: inspect formulas, recalculation, number formats, totals, and representative cells;
- research: claim-to-source matrix, dates, primary-source preference, conflicting evidence;
- humanities: quote fidelity, translation/context, interpretation versus fact;
- computer operation: screenshot/state confirmation and action log;
- cybersecurity: scanner output, hashes, indicators, scope, and limitations;
- simulation/biology: units, parameters, model assumptions, reproducibility, controls, and provenance.

If verification is blocked, state exactly why. Never convert "created" into "validated" without evidence.

## 7. Return one complete answer

Use:

1. **Result or artifact**
2. **What was done and which specialists/tools were used**
3. **Priority findings, risks, and unresolved uncertainty**
4. **Evidence and verification**
5. **Files, screenshots, citations, or checksums**
6. **Next action or confirmation needed**

For mixed tasks, keep each domain's evidence separate before giving the cross-domain conclusion.

## 8. Make an intelligent model choice

Before expensive or multimodal work, invoke the `model-routing` skill and/or run `scripts/model_selector.py`:

1. Inspect the current model's actual modalities, context window, tool access, permissions, and quality constraints.
2. Infer required capabilities from the request: vision, audio, video, computer control, web access, artifact generation, scientific computing, biology, long context, deep reasoning, or system security.
3. Choose `use_current`, `delegate_missing_capability`, `switch_for_quality`, `request_user_configuration`, or `blocked`.
4. Prefer an explicitly configured specialist model that covers the smallest bounded gap. Never assume that a named provider such as Qwen is installed or that its API is reachable.
5. Keep the primary model responsible for intent, critical path, model choice, sensitive-data filtering, safety gates, conflict resolution, integration, final verification, and the final answer.
6. Transfer only the task goal, relevant input, and acceptance criteria. Exclude secrets, credentials, unrelated files, and private data without consent.
7. Log the helper model ID, capability, input scope, provenance, uncertainty, and verification status. If no helper is configured, tell the user exactly what capability or configuration is missing and request it rather than fabricating a call.
8. **Auto-trigger on domain detection**: When the task text contains domain-specific keywords (e.g., "识别图片", "语音转文字", "视频分析"), the router automatically infers the required capability and selects helpers without explicit user prompting. The `auto_trigger_hints` field shows which capabilities triggered each helper.

### Auto-trigger examples

| User says | Inferred capability | Auto-selected helper |
|-----------|---------------------|----------------------|
| "识别这张图片里的文字" | vision + ocr | vision-capable model |
| "把这段录音转成文字" | audio + speech_recognition | audio-capable model |
| "分析这个视频的内容" | video | video-capable model |
| "生成一个PPT报告" | artifact_generation | artifact-capable model |
| "查一下最新新闻并核实" | web_access | web-capable model |

### Capability probing

Run `scripts/capability_prober.py` to auto-detect available models and their capabilities from configured providers:

```text
python scripts/capability_prober.py --catalog model_catalog.json --dry-run
python scripts/capability_prober.py --catalog model_catalog.json --json
```

The prober queries provider endpoints (e.g., OpenAI `/v1/models`, Ollama `/api/tags`) and infers capabilities from model IDs using pattern matching. It updates the catalog with newly detected capabilities without overwriting user-declared ones.

This routing is a recommendation and coordination protocol, not a security boundary. Tool permissions, external network access, destructive-action confirmations, and provider policies still apply.