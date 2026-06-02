---
name: implementation-journal
description: "Maintain two implementation memory documents during non-trivial coding work: an in-progress `implementation-log.md` that records decisions, ambiguity, failed paths, tradeoffs, and validation discoveries as they happen, and a polished `handoff.md` generated or updated at the end for the next human or AI. Use when the user asks for implementation notes, handoff docs, session handoff, decision logs, process logs, AI coding journals, or when a coding task is large, ambiguous, multi-step, likely to span sessions, or likely to involve important design choices."
---

# Implementation Journal

Use this skill to keep implementation memory visible while coding. The goal is to preserve the reasoning that final code and final summaries often hide.

## Documents

Create or update these files near the work unless the repo has an established docs location:

- `implementation-log.md`: working process log, updated during implementation.
- `handoff.md`: polished handoff document, updated near completion.

If the repo already has equivalent files, use the existing convention. If multiple tasks are active, use task-scoped names or folders, such as `docs/tasks/<slug>/implementation-log.md`.

## Workflow

1. At the start, create `implementation-log.md` with the task, date, assumptions, and initial plan.
2. During implementation, append only meaningful entries when decisions happen.
3. When the implementation changes direction, record the old path, why it failed or became less attractive, and the new path.
4. Before final response or commit, generate or refresh `handoff.md` from the log and the final code state.
5. Keep both files concise enough to be useful. Do not turn the log into a timestamped command transcript.

## What To Log

Write an entry when one of these happens:

- The spec is ambiguous and you choose a behavior.
- You discover an unknown constraint in the codebase.
- You reject or abandon an approach.
- You make a tradeoff between simplicity, compatibility, performance, UX, correctness, or scope.
- You intentionally deviate from the original request or implementation plan.
- A test, typecheck, lint, or manual check changes your understanding.
- You find a risk, follow-up, migration concern, or user-confirmation point.

Avoid logging:

- File-opening or search commands.
- Obvious edits that the diff already explains.
- Repeated status updates with no new decision.
- Narration that says only "implemented X" without why it matters.

## Log Entry Format

Use short dated sections. Add entries as bullets.

```markdown
# Implementation Log

## Task

Implement <brief task>.

## Assumptions

- <assumption or "None yet">

## Log

### 2026-05-19

- Spec does not say whether failed imports should roll back the whole batch. I am implementing per-item failure because the existing API already returns per-item status. Needs product confirmation if all-or-nothing behavior is expected.
- Tried adding validation in the route handler, but it duplicated service-layer checks. Kept validation in the service to avoid divergent behavior across API and CLI callers.
```

## Handoff Format

Make `handoff.md` a cleaned-up document for someone taking over. Prefer this structure:

```markdown
# Handoff

## Summary

<What changed and why.>

## Key Decisions

- <Decision and rationale.>

## Files Changed

- `<path>`: <role of the file/change>

## Validation

- <Command/check run and result>

## Known Risks

- <Risk or "None known">

## Follow-ups

- <Follow-up or "None">
```

## Updating Existing Documents

If the files already exist, append to `implementation-log.md` instead of rewriting history. For `handoff.md`, rewrite as needed so it reflects the final state clearly.

If old log entries are wrong because the plan changed, add a new entry explaining the change. Do not silently erase the old decision unless it contained sensitive information or noise that should never have been recorded.

## Final Response

When using this skill, mention the two document paths in the final response and call out whether `handoff.md` is complete or still provisional.
