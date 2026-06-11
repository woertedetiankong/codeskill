# Document Model

Use this reference when deciding where implementation knowledge should live.

## Layers

| Layer | Audience | Purpose | Edit style |
|---|---|---|---|
| Long-term plan | User, product owner, future agents | Intent, milestones, status, links to evidence | Living status document |
| Task index | Future implementers and agents | Discover task dossiers, latest handoffs, and module relationships | Lightweight registry |
| Task dossier | Current and next implementer | Work contract and milestone memory | Task-scoped |
| Implementation log | Future implementer debugging decisions | Decisions, constraints, failed paths, validation discoveries | Conditional append-only |
| Handoff | Next human or AI | Current state, what changed, how to continue, how to verify restart reality | Rewrite to current truth |
| New-session entry | Next AI session | Pointer to the latest handoff, known errata, red lines, first verify command | Lightweight current pointer |
| Project wiki | Team and future agents | Compiled durable knowledge and cross-links | Rewrite and refactor |
| README/docs | New users/operators/integrators | How to run, use, integrate, and operate | Rewrite to current truth |
| AGENTS/CLAUDE | Agents working in the repo | Project conventions and non-obvious guardrails | Concise current guidance |

## Default Paths

Use existing repo conventions first. If none exist:

```text
docs/tasks/<YYYY-MM-DD>-<slug>/task-brief.md
docs/tasks/<YYYY-MM-DD>-<slug>/implementation-log.md
docs/tasks/<YYYY-MM-DD>-<slug>/handoff.md
docs/tasks/INDEX.md
tasks/todo.md
docs/wiki/index.md
docs/wiki/log.md
docs/wiki/<topic>.md
```

Use lowercase hyphenated slugs. Prefer the milestone outcome over an implementation detail, such as `auth-device-flow` rather than `add-routes`.

## Long-Term Plan

The plan should answer: what is being built, why it matters, what milestones exist, and what status each milestone has. Keep it brief and link out to task dossiers or handoffs for evidence.

Accepted parent-plan sources include roadmaps, planning docs, GitHub issues, user-provided plans, `/goal` briefs, and `goal-brief-*.md` files produced by `goal-brief-builder`.

When using a goal brief, treat it as the source of intent and constraints. Do not copy the entire brief into the task dossier. Derive the active slice, success criteria, scope boundaries, forbidden shortcuts, validation expectations, and final handoff requirements.

When no goal brief or parent plan exists, do not create a fake roadmap. Create the task dossier directly from the user's request and set `Parent plan: None found`.

When a slice starts, mark it `In progress` with an absolute date and link to the task dossier. When it completes, mark it `Done` with an absolute date and link to the handoff. When it is abandoned or replaced, mark that explicitly and link to the log entry explaining why.

Do not duplicate implementation details from the task dossier into the plan.

If a milestone is too large, create a sub-slice that has a coherent deliverable and does not silently change user-visible scope. Record the chosen sub-slice in the task brief and link it under the parent milestone.

## Task Dossier

Create or update `docs/tasks/INDEX.md` when it improves discovery: multi-module work, several plan-linked dossiers, or at least three task dossiers. Keep it as a registry, not a second plan. Each row should point to the task dossier and latest handoff, name the module/surface, record status, and list upstream/downstream task references using stable relative links.

`task-brief.md` is the contract. It should include the selected slice, success criteria, scope, constraints, source plan link, and expected docs/wiki touchpoints.

`implementation-log.md` is a conditional decision log. Create it only when there is implementation memory worth preserving: ambiguous behavior chosen, hidden constraints, rejected paths, tradeoffs, validation surprises, risks, or cross-session reasoning. Do not create it as an empty ritual file or command transcript. Append dated entries when meaningful decisions happen. Do not rewrite history after a plan changes; add a new entry explaining the change.

If no log trigger occurs, record `Implementation log: Not required - no meaningful decision trail occurred` in the handoff.

`handoff.md` is the takeover document. Rewrite it near completion so it is short, accurate, and useful without reading the whole log. Include restart verify commands, expected outputs, mismatch meanings, cross-module references, closed decisions, red lines, and gotchas when they affect continuity.

Use stable relative links when one module references another module's dossier, handoff, docs, or wiki topic. Prefer a predictable shape:

```markdown
- Depends on: [auth device flow](../2026-06-10-auth-device-flow/handoff.md) - token contract
- Referenced by: [billing import](../2026-06-12-billing-import/handoff.md) - user identity mapping
```

The new-session entry is the first landing point for a new chat. Use the repo's established session/todo file, or `tasks/todo.md` by default. It should point to the latest handoff, note any known errata, and provide the first verify command. Keep state details in the handoff so the entry does not become a competing authority.

## Project Wiki

The wiki is compiled project knowledge, inspired by the LLM Wiki pattern: it sits between raw sources and future answers. It should accumulate durable synthesis instead of making each future agent rediscover facts from scratch.

`index.md` is content-oriented. List pages with one-line summaries and useful categories.

`log.md` is chronological. Append entries for meaningful ingests, milestone completions, lint/cleanup passes, and major wiki restructures. Use a parseable heading style:

```markdown
## [2026-06-10] milestone | Implementation journal refactor
```

Topic pages should be edited in place as understanding improves. Remove stale claims rather than piling new corrections underneath them.

Create a wiki only when the milestone produces reusable concepts, architecture knowledge, integration contracts, or decisions that future work should discover. For a small isolated fix, update existing docs and skip new wiki scaffolding.
