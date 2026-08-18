---
name: test-engineering
description: Derive, write, and run risk-based tests from code behavior, requirements, and recent changes across web and software projects. Use when the user asks for tests, coverage, regression protection, test strategy, failing-test diagnosis, or validation after implementation.
---

# Engineer tests from behavior

Treat tests as executable contract and risk control. Infer behavior from requirements, public interfaces, existing conventions, and failure modes rather than chasing a coverage number.

## Workflow

1. Identify the test runner, package manager, language, fixtures, mocks, environment variables, and existing test naming conventions.
2. Map the behavior under test: inputs, outputs, state changes, side effects, errors, permissions, timing, retries, and dependencies.
3. Rank cases by risk:
   - normal success path;
   - boundary and empty values;
   - invalid, malformed, duplicated, and adversarial inputs;
   - authorization and tenant isolation;
   - dependency failure, timeout, retry, partial failure, and idempotency;
   - persistence/transaction rollback and concurrency where relevant;
   - browser/device/network behavior for web applications;
   - compatibility and migration behavior for public APIs.
4. Prefer the smallest stable test layer: unit for pure logic, integration for boundaries and persistence, end-to-end only for user-critical flows. Avoid testing implementation details that block safe refactoring.
5. Write tests that fail for the old bug and pass for the intended behavior. Keep fixtures deterministic and cleanup explicit.
6. Run focused tests first, then the relevant suite, then lint/type/build checks. Use the repository's documented commands; discover them from manifests if undocumented.
7. Report untested risk, environment dependencies, flaky behavior, and any test that was not run.

## Test-plan format

Before a large test change, produce a compact matrix:

| Case | Risk | Layer | Expected behavior | Status |
|---|---|---|---|---|
| ... | P0/P1/P2 | unit/integration/e2e | observable assertion | planned/written/passed/blocked |

For each test added, name the contract it protects. Include at least one negative or boundary case for every important input boundary. For security-sensitive logic, assert both rejection and non-leakage of sensitive details.

## Completion criteria

Consider the task complete only when:

- the intended behavior is asserted;
- the regression or new tests are deterministic;
- focused tests pass, or the exact blocker is recorded;
- broader checks are run when practical;
- the final answer distinguishes written, executed, passed, failed, and blocked tests.

If the project has no test harness, do not silently invent a framework. Offer the smallest justified setup and a runnable manual verification plan.
