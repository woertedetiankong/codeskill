# Goal Brief Template

Use this template for the final Markdown document. Keep sections that help `/goal`; omit sections that are truly irrelevant.

## File Naming

Default filename:

```text
goal-brief-{short-slug}.md
```

Examples:

- `goal-brief-checkout-redesign.md`
- `goal-brief-build-time-optimization.md`
- `goal-brief-auth-migration.md`

## Markdown Template

````md
# Goal Brief: {Project or Outcome Name}

> Prepared for Codex `/goal` mode.  
> Created: {YYYY-MM-DD}  
> Source conversation: {same thread / new thread / pasted context}  
> Owner: {user/team, if known}

## Goal Objective

{One specific sentence describing what Codex must accomplish. This should be concrete enough to stand alone as the first sentence of a `/goal` command.}

## /goal Command

```text
/goal {specific one-sentence objective}. Use this Goal Brief as the authoritative task contract. Continue working until the Completion Criteria are satisfied, preserve the Constraints and Forbidden Shortcuts, report progress as requested, and do not mark the goal complete until the Final Review and Handoff requirements are done.
```

## Desired Outcome

{Describe the concrete end state in 1-3 paragraphs. Prefer user-visible outcomes and measurable results over implementation wishes.}

## Captured Requirements and Decisions

- User-stated requirements: {exact requirements gathered during interview}
- Examples/references: {screenshots, URLs, issues, docs, designs, logs, or examples}
- Decisions made during interview: {choices selected and why}
- Rejected options: {approaches the user declined or ruled out}
- Wording/preferences to preserve: {names, product language, tone, UX preferences, compatibility promises}

## Completion Criteria

- {Criterion 1: measurable/verifiable}
- {Criterion 2: measurable/verifiable}
- {Criterion 3: measurable/verifiable}

## Verification Plan

- Commands/tests to run: `{known command}` or first discover the repo's standard verification command from package config, README, CI config, or existing docs; then run the relevant subset and report limitations.
- Manual checks or screenshots: {what to inspect}
- Metrics/baselines: {baseline and target, if applicable}
- Dataset/device/network assumptions: {seed data, browser/device profile, network profile, or "not applicable"}
- Percentiles/regression budget: {p95/p99, acceptable variance, rollback threshold, or "not applicable"}
- Closest realistic environment: {local, preview, staging, production-like test environment, physical device, or "not available"; note production gaps as residual risk}
- Required evidence: {logs, screenshots, benchmark output, PR link, report, etc.}

## Starting Context

- Repository/workspace: {path, URL, or unknown}
- Branch/current state: {branch or unknown}
- Relevant files/modules: {files, modules, designs, issues, docs}
- Known suspicion or prior findings: {what the user believes may matter}

## Scope

In scope:

- {Included area}
- {Included area}

Out of scope:

- {Excluded area}
- {Excluded area}

## Constraints

- Technical constraints: {framework, language, API, compatibility, performance}
- Design/product constraints: {design system, UX expectations, copy tone}
- Process constraints: {TDD, commit cadence, PR policy, review requirements}
- Budget/time/token constraints: {limits if any}

## Allowed Tools and Environment

- Local commands: {allowed commands or categories}
- Browser/apps/connectors: {Chrome, Browser, GitHub, etc.}
- External services/deployments: {preview, staging, prod, Colab, etc.}
- Data/devices/accounts: {what can be used}

## Safety and Permissions

- Do not touch: {production, secrets, billing, user data, permissions, etc.}
- Ask before: {deploying, pushing, deleting, sending messages, using paid APIs, etc.}
- Sensitive data rules: {redaction, local-only, no uploads, etc.}

## Forbidden Shortcuts

- {Shortcut that would make metrics pass but violate intent}
- {Shortcut that would fake the result}
- {Shortcut that would reduce coverage, quality, or maintainability}

## Progress Reporting

- Update cadence: {after each milestone / every N minutes / before risky actions}
- Progress artifact: {Markdown file, HTML dashboard, PR comments, commits, status-check side thread, scheduled check-in, etc.}
- Commit/PR expectations: {commit points, draft PR, branch naming}

## Rollback, Cutover, and Rehearsal

- Applies to: {migrations, deployments, data changes, auth/payment/security changes, or "not applicable"}
- Rehearsal plan: {staging rehearsal, dry run, backup/restore test, local-only simulation, or "not applicable"}
- Cutover boundary: {who performs production/staging cutover and what Codex may or may not do}
- Rollback plan: {how to revert safely, what data/config must be backed up, and who approves rollback}
- Monitoring/acceptance window: {SLO, logs, dashboards, error budget, operator confirmation, or "not applicable"}

## Final Review and Handoff

Before marking the goal complete, Codex must:

- Run the Verification Plan and include results.
- Review the diff for accidental changes, dead code, temporary files, and failed attempts.
- Update relevant docs or explain why none are needed.
- Summarize what changed, what was verified, and residual risks.

## Open Questions and Default Assumptions

- Question: {open question}
  Default assumption: {safe conservative assumption until clarified}
````

## Interview Question Examples

Use these as raw material. Prefer fewer, sharper questions.

### Outcome

- What should be true when this goal is complete?
- Is the goal a new feature, a fix, an optimization, a migration, a redesign, research, or cleanup?
- Who is the end user or reviewer for the result?

### Verification

- What objective signal should Codex optimize for?
- Are there existing tests, benchmarks, screenshots, logs, or dashboards to use?
- What result would convince you that this is actually done?
- For performance goals, what baseline, target, percentile, dataset size, browser/device, and network assumptions matter?
- If no verification command is known, should Codex discover one from the repo or should this remain an open question?
- What is the most realistic safe environment Codex can use, and what production gaps should be reported as residual risk?

### Scope

- Which parts of the codebase are definitely in scope?
- Which areas should Codex avoid even if they seem related?
- Should Codex preserve current behavior, or is behavior allowed to change?
- If the answer is naturally multi-select, which choices are primary and which should be preserved as secondary context?

### Environment

- Does Codex need Chrome, the in-app Browser, GitHub, a local dev server, staging, production logs, a physical device, or external tools?
- Is it allowed to install dependencies or use paid APIs?
- Are there accounts or services Codex may inspect but not modify?

### Visual Goals

- Are screenshots or mockups context, acceptance criteria, or both?
- What design system, responsive breakpoints, accessibility requirements, and interaction states must be preserved?
- What shortcuts are forbidden, such as cropping a reference image, hiding text overflow, or matching only one viewport?

### Rollback and Cutover

- For migrations, deployments, data changes, auth, billing, or security work, who performs cutover and rollback?
- What rehearsal, dry run, backup, monitoring, and operator confirmation are required?
- If production access is forbidden, should this be a planning-only/runbook brief rather than an execution goal?

### Forbidden Shortcuts

- What would be a fake success for this goal?
- Are there metrics Codex might game by weakening tests, hiding errors, cropping images, disabling checks, or reducing scope?

### Progress and Handoff

- Should Codex commit at milestones or only at the end?
- Should it maintain a progress document?
- What should the final handoff include for you to trust it?
- Should the brief be returned inline, written to a file, or both?
- For multi-day goals, should Codex maintain a persistent artifact, draft PR, side-thread status path, or scheduled check-in?

## Good `/goal` Prompt Pattern

```text
/goal {specific one-sentence objective}. Use the attached Goal Brief as the task contract. First confirm the baseline and verification plan, then execute in scoped milestones. Keep a progress log, avoid the forbidden shortcuts, and ask before any action listed under Safety and Permissions. Do not mark the goal complete until every Completion Criterion is verified and the Final Review and Handoff section is done.
```

## Anti-Patterns to Avoid

- "Make it better" without metrics, examples, or acceptance checks.
- "Pixel perfect" without design-system, responsive, accessibility, and anti-cropping constraints.
- Performance goals without a baseline, target, and repeatable measurement command.
- Performance goals that do not define dataset/device/network assumptions or guard against benchmark-only wins.
- Long migrations without progress checkpoints and rollback/compatibility expectations.
- Contradictory execution goals that forbid the access, schema changes, tests, rehearsal, or verification needed to prove success.
- Goals that require real accounts, deployments, paid APIs, or production changes without permission boundaries.
