---
name: problem-solving
description: Solve broad technical and non-technical questions with structured decomposition, evidence gathering, priority ranking, explicit assumptions, option comparison, and a concise synthesized recommendation. Use when the request is ambiguous, cross-domain, research-heavy, or asks for a complete answer rather than a single code edit.
---

# Solve broad problems

Convert an open-ended question into a decision-ready answer. Do not hide uncertainty behind confident prose.

## Workflow

1. Restate the objective and the decision or deliverable the user actually needs.
2. Separate known facts, assumptions, unknowns, constraints, and success criteria.
3. Break the work into a critical path and independent side questions. Keep the primary model responsible for the critical path and final synthesis; delegate side questions only when the host provides agent/model tools and the work is bounded.
4. Rank issues with impact, urgency, confidence, reversibility, and dependency. Handle high-impact and irreversible items first.
5. Gather evidence from the workspace, authoritative documentation, primary sources, or current web sources when facts may have changed. Cite important external claims and give dates for time-sensitive facts.
6. Compare viable options using explicit tradeoffs: correctness, security, cost, complexity, performance, maintainability, and time to deliver.
7. Recommend one option, explain why, state what would change the recommendation, and give an actionable next step.
8. Reconcile delegated results against primary evidence. Remove duplicated or unsupported claims.

## Answer format

- **Recommendation**
- **Why this is the priority**
- **Facts and assumptions**
- **Options and tradeoffs**
- **Implementation or action plan**
- **Risks, uncertainty, and validation**

For high-stakes topics, be conservative, distinguish information from professional advice, and direct the user to an appropriate qualified professional when needed. For current or niche information, verify rather than relying on memory.
