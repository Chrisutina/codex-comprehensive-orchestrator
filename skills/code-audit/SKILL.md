---
name: code-audit
description: Audit source code, configuration, APIs, and diffs for correctness, security, reliability, performance, and maintainability, then prioritize findings and propose or implement regression tests. Use for code review, security review, pre-release checks, bug triage, or requests to find problems in a web app or program.
---

# Audit code rigorously

Audit behavior and risk, not style preferences. Start from the user's contract, threat model, and changed surface. Expand to callers, data boundaries, configuration, and tests only when needed to validate a finding.

## Workflow

1. Read repository guidance and identify language/framework, entry points, trust boundaries, persistence, network calls, authentication, authorization, and deployment assumptions.
2. Inspect the diff first when one exists. Then trace each changed function through its callers and error paths.
3. Run the lightest available static checks and focused tests. Do not install tools or change lockfiles unless requested or clearly necessary.
4. Check these categories as applicable:
   - correctness and edge cases;
   - authentication, authorization, injection, path traversal, SSRF, XSS, CSRF, unsafe deserialization, secret leakage, and insecure defaults;
   - input validation, output encoding, data-flow and privacy boundaries;
   - concurrency, retries, idempotency, timeouts, resource exhaustion, and failure recovery;
   - type safety, null/empty handling, transaction boundaries, caching, and compatibility;
   - performance hotspots, N+1 behavior, unbounded loops, large payloads, and expensive work on request paths;
   - observability, operability, migration safety, and maintainability.
5. For every plausible issue, verify the execution path and distinguish confirmed issues from review questions or hypotheses.
6. Add a focused regression test for each confirmed fix when a test harness exists. If no harness exists, provide a concrete reproducible case and a test plan.

## Finding format

Order by priority, then confidence. Use this format:

```text
[P0|P1|P2|P3] [confirmed|hypothesis] Short title
Location: C:\absolute\path\file.ext:line[-line]
Impact: What can happen and who/what is affected.
Evidence: The exact control/data flow, failing test, or reproducible input.
Fix: Smallest safe remediation, including compatibility considerations.
Regression test: Test name or precise case that prevents recurrence.
Confidence: high|medium|low
```

Priority guidance:

- **P0:** exploitable security issue, data loss/corruption, outage, or a clearly broken critical contract;
- **P1:** high-impact bug, privilege boundary failure, likely production failure, or missing critical validation;
- **P2:** meaningful correctness, reliability, performance, or maintainability risk;
- **P3:** low-risk improvement or polish.

Do not inflate severity for theoretical concerns. Do not downgrade a concrete exploit because a test is missing. Explain assumptions when impact depends on deployment or configuration.

## Fix mode

When the user asks for fixes, address P0/P1 first, preserve public behavior unless the contract requires change, and keep edits narrowly scoped. After each fix:

- inspect the complete diff;
- add or update the regression test;
- run the focused test and relevant lint/type/build checks;
- re-audit adjacent paths for the same root cause.

End with a table of findings, changed files, checks run, unresolved questions, and residual risk. Never label an issue fixed without evidence.
