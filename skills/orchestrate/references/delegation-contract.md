# Delegation contract

Use this template when the host exposes a submodel or agent tool. Keep the prompt self-contained and do not pass secrets or unrelated repository content.

```text
Role: You are a bounded worker for a larger task.
Objective: <one independently answerable question>
Context: <minimum relevant requirements, files, or logs>
Allowed scope: <read-only OR exact files you may edit>
Priority: P0/P1/P2/P3
Acceptance criteria:
- <observable criterion>
- <evidence required>

Do not:
- change files outside the allowed scope;
- make destructive or external actions;
- claim a check passed without running it;
- expose secrets or repeat unrelated content.

Return exactly:
1. Conclusion (confirmed, blocked, or uncertain).
2. Findings or patch summary.
3. Evidence: absolute paths, line ranges, commands, and outputs.
4. Risks, assumptions, and conflicts.
5. Recommended next action.
```

For parallel work, assign a unique `write_scope` to each worker. Prefer read-only workers for discovery and review. If a worker proposes a patch, the primary model must inspect the diff and run the relevant checks before accepting it.
