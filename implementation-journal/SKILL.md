---
name: implementation-journal
description: "Run a milestone implementation journal for substantial coding work: connect a long-term plan to a task dossier, maintain implementation memory, produce a restart-ready handoff, keep a new-session entry current, and reconcile durable knowledge into project docs/wiki when appropriate. Use when the user asks for implementation notes, handoff docs, restart/session handoffs, task dossiers, AI coding journals, long-term plan execution, milestone implementation, cross-session work, architecture decision logging, project wiki updates, knowledge reconciliation, phase-complete cleanup, or when a coding task is milestone-sized, plan-linked, cross-session, architecture-affecting, or likely to involve important design choices."
---

# Implementation Journal

Use this skill to make long-running AI-assisted development compound instead of evaporating into chat history. The job is not to keep a command transcript. The job is to connect a plan, the current milestone, the implementation reasoning, the restart handoff, and the durable project knowledge base.

## Core Rule

For ordinary small fixes, do not create ceremony unless the user asks for it. For milestone-sized work, create or update a task dossier, log meaningful implementation decisions only when there is a real decision trail to preserve, keep restart continuity current, and finish by reconciling what became true back into the plan and docs/wiki.

Existing project conventions win. If the repo already has task folders, decision records, wiki pages, or handoff docs, use those names and locations instead of the defaults below.

## Default Documents

- Long-term plan: an existing roadmap, issue, goal brief, plan document, or user-provided plan. Do not invent a broad roadmap when the user only asked for one slice.
- Task dossier: `docs/tasks/<YYYY-MM-DD>-<slug>/`.
- Task index: `docs/tasks/INDEX.md` when the work spans multiple modules, the plan has several task dossiers, or at least three task dossiers exist.
- `task-brief.md`: the contract for this slice of work.
- `implementation-log.md`: conditional append-only decision log for ambiguity, constraints, failed paths, tradeoffs, validation surprises, risks, and cross-session reasoning. Do not create it solely to fill a template.
- `handoff.md`: rewritten near completion so the next human or AI can continue without reading the whole log; include restart verify commands, closed decisions, red lines, environment state, and gotchas.
- New-session entry: the repo's existing session entry file if present, otherwise `tasks/todo.md` top section. Keep it as a pointer plus errata layer for the latest handoff, not a second handoff.
- Project wiki: `docs/wiki/index.md`, `docs/wiki/log.md`, and topic pages when the repo already has a wiki, the user asks for durable wiki knowledge, or the milestone creates cross-cutting facts worth compiling.

## Goal Brief Input

`goal-brief-builder` is an optional upstream skill, not a dependency.

- If a `goal-brief-*.md`, `/goal` brief, issue brief, or similar execution brief exists, treat it as the parent plan or source of intent.
- Do not duplicate the whole goal brief into `task-brief.md`. Extract only the current implementation slice, success criteria, constraints, forbidden shortcuts, validation expectations, and expected docs/wiki updates.
- If no goal brief exists, build the task dossier directly from the user's request and set `Parent plan: None found`.
- Do not run a full goal-brief interview from this skill unless the request is too ambiguous or risky to implement safely.

Read [references/document-model.md](references/document-model.md) when choosing artifact paths or deciding what belongs in plan, task dossier, handoff, or wiki.
Read [references/handoff-discipline.md](references/handoff-discipline.md) before creating or refreshing a cross-session handoff, restart opener, or new-session entry.
Read [references/templates.md](references/templates.md) before creating new documents.
Read [references/knowledge-sync.md](references/knowledge-sync.md) before end-of-stage cleanup or wiki/docs reconciliation.

## Workflow

1. Ground in the plan and repo.
   - Locate the long-term plan or the most specific source of intent.
   - Discover existing conventions before creating files: search for task folders, handoffs, session entries, todo files, decision records, wiki indexes, roadmap/plan docs, README, AGENTS/CLAUDE, and docs directories.
   - Identify the current implementation slice, success criteria, scope, constraints, and known affected docs/wiki topics.
   - For multi-module work, identify known upstream/downstream modules and existing task dossiers that may reference the changed contract.
   - If the requested milestone is too large to finish safely in one implementation pass, carve out the smallest coherent sub-slice that preserves the milestone intent, record the default slice in `task-brief.md`, and ask for confirmation only when the slice boundary changes user-visible scope or risk.
   - If no long-term plan exists, do not invent one. Create the task dossier for the requested slice and set `Parent plan: None found`.

2. Create or update the task dossier.
   - Use `docs/tasks/<YYYY-MM-DD>-<slug>/` unless the repo has a better convention.
   - Link the dossier from the long-term plan when the plan exists.
   - Create `implementation-log.md` only when a log trigger appears: ambiguous behavior chosen, hidden constraint discovered, failed path rejected, tradeoff made, validation changed understanding, risk/follow-up found, or cross-session reasoning would be hard to reconstruct.
   - For long, multi-session, architecture-affecting, or high-risk milestones, assume a log trigger is likely; create the log early once there is a real assumption, decision, or constraint to record.
   - Keep `task-brief.md` current when scope or acceptance criteria materially change.
   - Create or refresh `docs/tasks/INDEX.md` only when it helps discovery: multi-module work, several plan-linked dossiers, or at least three task dossiers. Keep it lightweight.
   - Create a provisional `handoff.md` before any planned pause or final response, even if implementation is not complete.
   - Create or refresh the new-session entry so a future session can find the latest handoff immediately.

3. Log only useful implementation memory, and skip the file when nothing qualifies.
   - Append a log entry when you choose behavior for an ambiguous spec, discover a codebase constraint, abandon an approach, make a tradeoff, intentionally deviate from the plan, learn from validation, or identify a risk/follow-up.
   - Do not log file-opening commands, obvious edits, repeated progress notes, or narration that merely says "implemented X".
   - Do not create an empty or ceremonial implementation log. If no log trigger occurred, say so in the handoff instead of inventing entries.
   - After each verified work unit, write back the meaningful progress, evidence, and changed next steps. Do not wait until the end of the chat if the state has materially changed.
   - When a confirmed discovery affects multiple modules, shared contracts, architecture rules, integration behavior, or future implementation slices, update the relevant wiki/docs immediately if another active or upcoming module may depend on it. Use a clearly named durable-knowledge follow-up only when the fact needs user confirmation, would expand scope, or cannot be safely edited now.
   - Use absolute dates such as `2026-06-10`; never use relative dates such as "today" or "recently".

4. Refresh the handoff before final response, commit, or phase completion.
   - Rewrite `handoff.md` so it reflects the final code state and current next steps.
   - Include what changed, key decisions, affected files/surfaces, validation evidence, risks, follow-ups, cross-module references, docs/wiki updates, restart verify commands, special environment state, gotchas, enforceable red lines, and closed decisions that should not be reopened.
   - Include a restart opener: a short pasteable first message for the next session that names the project, the latest handoff, the entry file, the current state, special environment state, immediate next steps, red lines, and the first verify command.
   - Mark it provisional if implementation or validation is intentionally incomplete.

5. Reconcile durable knowledge.
   - Update the long-term plan status for the slice with absolute dates and links to the task dossier or handoff.
   - Update `docs/tasks/INDEX.md` when it exists or when the conditions for creating it are met.
   - Update README, AGENTS/CLAUDE guidance, docs, and project wiki pages when they now describe stale behavior.
   - Merge duplicate content, rewrite outdated sections, and delete superseded final-state claims. Preserve important history in the implementation log or a decision record when such history exists, not in current-facing docs.
   - Do not add "Update: the new behavior is..." underneath stale instructions. Replace or remove the stale instruction.
   - Use a small cleanup loop: inventory likely stale docs, classify each change as rewrite/merge/delete/keep, edit, then rerun targeted search for the old commands, names, routes, or claims.
   - Append a concise entry to `docs/wiki/log.md` when a wiki exists or when the milestone creates enough durable cross-linked knowledge to justify starting one. Otherwise reconcile existing docs and state that no wiki was created.
   - Refresh the new-session entry after the handoff changes. If part of the latest handoff is already stale, write the correction in the entry instead of silently rewriting history.

## Knowledge Boundaries

- `implementation-log.md` is conditional and append-only except for removing accidental secrets or obvious noise. It explains why the work went a certain way; it is not a command transcript or required artifact when no meaningful decision trail exists.
- `handoff.md`, `task-brief.md`, wiki topic pages, README, and docs are living documents. Rewrite them until they describe the current truth clearly.
- The new-session entry is a lightweight pointer and errata layer. It should not grow into a duplicate status document.
- The project wiki is compiled knowledge, not raw chat history. File durable concepts, architecture facts, decisions, integration rules, and open questions there.
- The long-term plan tracks status and intent. It should link to evidence, not duplicate every implementation detail.
- Handoff is current operational state, not a knowledge base. Move reusable lessons and durable concepts to docs/wiki or decision records.

## Quality Gate

Before finishing a milestone, check:

- The task dossier exists or there is a deliberate reason it was unnecessary.
- `implementation-log.md` exists only if log triggers occurred; when it exists, it contains the important decisions and validation discoveries. If it does not exist, the handoff states that no implementation log was required.
- `handoff.md` is complete or clearly marked provisional.
- The handoff contains runnable restart verify commands with expected outputs and what mismatches mean.
- Cross-module dependencies or dependents are recorded with stable paths when the work touches module boundaries.
- Closed decisions and enforceable red lines are visible in the handoff when they matter.
- `docs/tasks/INDEX.md` exists and is current when the project has enough task dossiers or module relationships to need it.
- The new-session entry points to the latest handoff and records any known errata.
- The long-term plan status is updated when a parent plan exists.
- Current-facing docs/wiki no longer contain stale claims about the changed behavior.
- Docs/wiki changes are identified as rewritten, merged, deleted, created, or not required.
- New public APIs, commands, environment variables, architecture decisions, or workflows are documented for the right audience.
- There are no relative-date claims introduced by the journal or docs update.

When updating this skill itself or validating a complex workflow, use isolated subagents or thread forks if the environment supports them. Give each agent a realistic scenario and the skill artifact, not your expected answer. If no subagent facility is available, skip this step and note that limitation.

## Final Response

Mention the task dossier path, the handoff path, whether the handoff is complete or provisional, whether `implementation-log.md` was created or not required, the new-session entry path when one was created or updated, and which docs/wiki pages were reconciled. If no dossier was created, briefly state why.
