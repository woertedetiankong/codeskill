# Task Brief: Implementation Journal Refactor

> Created: 2026-06-10
> Parent plan: User-provided plan in the current Codex thread
> Status: Done

## Goal

Upgrade `implementation-journal` from a logging-only skill into a milestone-level workflow for long-term plan execution, task dossiers, handoffs, and project wiki knowledge reconciliation.

## Success Criteria

- `codeskill/implementation-journal/SKILL.md` describes the new 5-stage workflow and no longer frames the skill as only a log plus handoff.
- Reference files define the document model, knowledge sync cleanup rules, and reusable templates.
- `agents/openai.yaml` and `codeskill/README.md` describe the upgraded behavior.
- The installed copy under `/Users/superstorm/.codex/skills/implementation-journal` matches the source copy.
- Validation includes `quick_validate.py`, stale wording search, source/install diff, agent-team forward tests, and a manual dry-run.

## Scope

In scope:
- `codeskill/implementation-journal`
- `/Users/superstorm/.codex/skills/implementation-journal`
- `codeskill/README.md`
- This task dossier

Out of scope:
- Redesigning other skills
- Creating a full project wiki for `embedded-ai-client`

## Constraints

- Keep `SKILL.md` concise and move reusable detail into `references/`.
- Preserve the skill name `implementation-journal`.
- Use milestone-triggered behavior by default, not ceremony for every small fix.
- Use editor-style cleanup principles: merge, rewrite, and delete stale current-facing claims while keeping important rationale in logs.

## Expected Knowledge Updates

- Update the source skill and installed skill copy.
- Record this refactor as a real use of the task dossier workflow.
