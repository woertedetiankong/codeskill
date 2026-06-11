# Templates

Use these templates only when the repo has no established equivalent.

## Task Brief

```markdown
# Task Brief: <Milestone Name>

> Created: <YYYY-MM-DD>
> Parent plan: <link or "None found">
> Status: In progress

## Goal

<One concrete sentence describing this slice of work.>

## Success Criteria

- <Verifiable criterion>
- <Verifiable criterion>

## Scope

In scope:
- <Area>

Out of scope:
- <Area>

## Constraints

- <Technical, product, compatibility, or process constraint>

## Expected Knowledge Updates

- <Plan/docs/wiki pages likely to change, or "Unknown until implementation">
- Task index: <`docs/tasks/INDEX.md` update expected, or "Not required">
```

## Implementation Log

Use this template only after a log trigger occurs. Do not create an empty implementation log just because a task dossier exists.

```markdown
# Implementation Log

> Created: <YYYY-MM-DD>

## Task

<Brief task statement.>

## Assumptions

- <Assumption or "None yet">

## Initial Approach

- <Starting approach or "To be discovered from the repo">

## Log

### <YYYY-MM-DD>

- <Decision, constraint, failed path, tradeoff, validation discovery, risk, or follow-up.>
```

## Handoff

````markdown
---
title: Handoff <YYYY-MM-DD> - <milestone or slice>
status: Complete | Provisional
updated: <YYYY-MM-DD>
supersedes: <previous handoff path, or omit if none>
---

# Handoff

## Summary

<What changed and why.>

## Current State

<One sentence describing where this milestone stands.>

## Git And Persistent State

- Branch: <branch and relevant commit hashes, or "Unknown/not applicable">
- Persistent state: <PRs, migrations, generated artifacts, external state, or "None known">

## Environment State

<Special local/runtime state that changes the safe next action, or "None known".>

## Key Decisions

- <Decision and rationale.>

## Closed Decisions / Do Not Reopen

- <Rejected option and one-line reason, or "None">

## Changed Surfaces

- `<path or subsystem>`: <role of the change>

## Cross-Module References

- Depends on: [<module or task>](<relative path to handoff or docs>) - <contract or reason, or "None">
- Referenced by: [<module or task>](<relative path to handoff or docs>) - <contract or reason, or "Unknown/not applicable">

## Validation

- `<command/check>`: <result>

## Restart Verify

```bash
<command 1>  # expected: <observable output>; mismatch means: <diagnosis>
<command 2>  # expected: <observable output>; mismatch means: <diagnosis>
```

## Next Steps

1. <Next action by ROI and reason, or "None">

## Red Lines And Gotchas

- Red line: <enforceable instruction, or "None">
- Gotcha: <environment/data/process hazard, or "None known">

## Docs And Wiki

- Rewritten: <docs/wiki pages or "None">
- Merged: <docs/wiki pages or "None">
- Deleted: <docs/wiki pages or "None">
- Created: <docs/wiki pages or "None">
- Not required: <reason, if no docs/wiki update was needed>

## Implementation Log

- <`implementation-log.md` path and summary, or "Not required - no meaningful decision trail occurred">

## Known Risks

- <Risk or "None known">

## Follow-ups

- <Follow-up or "None">

## Restart Opener

```text
Project <path> (<name>). Read <handoff path> and <new-session entry path> first.
Previous session: <one-sentence result with evidence>.
Current state: <one-sentence board>.
Environment: <special environment state or "None known">.
Now do: 1. <next step> 2. <next step>.
Red lines: <enforceable instruction>.
First verify: <command> (expected <output>; mismatch means <diagnosis>).
```
````

## New-Session Entry

```markdown
## New Session Entry

- Read first: `<handoff path>`.
- Errata: <known stale section in handoff, or "None known">.
- Current board: <3-6 bullets with current state and next action>.
- Environment: <special environment state or "None known">.
- Red lines: <enforceable constraints, or "None">.
- First verify: `<command>`; expected <output>; mismatch means <diagnosis>.
```

## Task Index

Use this only when the project has multi-module work, several plan-linked dossiers, or at least three task dossiers.

```markdown
# Task Index

| Module / Slice | Status | Task Dossier | Latest Handoff | Depends On | Referenced By | Notes |
|---|---|---|---|---|---|---|
| <module or slice> | <In progress/Done/Blocked> | [task](<task folder>/task-brief.md) | [handoff](<task folder>/handoff.md) | [<module>](<relative path>) or None | [<module>](<relative path>) or Unknown | <short note> |
```

## Wiki Index Entry

```markdown
- [<Page Title>](<page>.md) - <One-line summary of durable knowledge on this page.>
```

## Wiki Log Entry

```markdown
## [<YYYY-MM-DD>] <type> | <Title>

- Source: <task dossier, plan, source doc, or conversation>
- Updated: <wiki/docs pages touched>
- Notes: <important synthesis, contradiction, or cleanup>
```

## Long-Term Plan Status Row

```markdown
| <Milestone> | <Status> | <YYYY-MM-DD> | <Evidence link> | <short note> |
```

Use `In progress` with a task dossier link at start, `Done` with a handoff link at completion, and `Abandoned` or `Replaced` with a log/decision link when the milestone changes direction.
