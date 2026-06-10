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
```

## Implementation Log

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

```markdown
# Handoff

## Summary

<What changed and why.>

## Key Decisions

- <Decision and rationale.>

## Changed Surfaces

- `<path or subsystem>`: <role of the change>

## Validation

- `<command/check>`: <result>

## Docs And Wiki

- Rewritten: <docs/wiki pages or "None">
- Merged: <docs/wiki pages or "None">
- Deleted: <docs/wiki pages or "None">
- Created: <docs/wiki pages or "None">
- Not required: <reason, if no docs/wiki update was needed>

## Known Risks

- <Risk or "None known">

## Follow-ups

- <Follow-up or "None">
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
