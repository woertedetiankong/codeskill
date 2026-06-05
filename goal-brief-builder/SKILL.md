---
name: goal-brief-builder
description: Interview a user in Plan mode and produce a Markdown brief that can be handed to Codex /goal mode as durable development instructions. Use when the user explicitly wants a /goal brief, asks to prepare work for goal mode, wants a Plan-mode interview, mentions request_user_input or askuserquestiontool, or wants a durable task brief for another Codex thread.
---

# Goal Brief Builder

## Purpose

Turn a fuzzy request into a self-contained `/goal` brief. The final document should let the user continue in the same thread or upload it to a new thread and run `/goal` without losing intent, constraints, success criteria, or review expectations.

## Interview Workflow

1. Restate the current understanding in 2-4 sentences.
2. Identify missing information across: outcome, scope, success criteria, environment, constraints, measurement, safety, progress reporting, and final handoff.
3. If running in Plan mode and `request_user_input` is available, use it for focused interview rounds. Ask 1-3 questions per round. Each question must have a header of 12 characters or fewer, a stable `snake_case` id, and 2-3 mutually exclusive options. Each option needs a short label and a one-sentence description of the tradeoff. Put the recommended option first and suffix its label with `(Recommended)`. Do not include an `Other` option; the client adds it automatically. Avoid multi-part questions.
4. If not in Plan mode or the question tool is unavailable, interview in normal chat with concise questions.
5. If the real answer may be multi-select, split it into follow-up questions or preserve the nuance in `Captured Requirements and Decisions`; do not force a false single choice.
6. Stop interviewing when the goal can be written with concrete completion criteria and no high-risk ambiguity. Always ask before finalizing if the outcome, verification, destructive permissions, production/external access, rollback/cutover plan, or scope boundaries are unclear. Do not chase perfection; preserve low-risk uncertainties in an `Open Questions` section with conservative defaults.
7. If requirements are mutually contradictory or make verification impossible, do not finalize an execution brief. Explain the contradiction and either keep interviewing or produce a planning-only/runbook brief with explicit non-execution boundaries.
8. In Plan mode, return the complete Markdown brief in the final response unless the user explicitly gave a path or asked you to create a file. Outside Plan mode, write or propose a Markdown file named `goal-brief-<slug>.md` unless the user gave a path.

## Question Strategy

Prioritize questions in this order:

1. Outcome: What user-visible or measurable result must exist when `/goal` finishes?
2. Verification: What commands, tests, screenshots, metrics, demos, or checks prove success?
3. Scope: What files, modules, platforms, workflows, or users are included or excluded?
4. Starting Context: What repo, branch, design, issue, article, plan, logs, or known suspicion should Codex start from?
5. Constraints: What tools, libraries, style rules, compatibility promises, deadlines, or budget limits matter?
6. Forbidden Shortcuts: What would look complete but count as failure?
7. Environment and Access: What is the most realistic environment Codex can safely use, what production gaps should be reported as risk, and what services, browsers, accounts, deployments, datasets, devices, or secrets are required or forbidden?
8. Visual Goals: If screenshots/mockups are involved, are they context or acceptance criteria, and what design-system, responsive, accessibility, interaction-state, and anti-cropping constraints apply?
9. Progress Measurement: What metrics, baseline, logs, screenshots, evals, or checkpoints prove the work is improving?
10. Progress Reporting: How often should Codex report, commit, update artifacts, create draft PRs, or leave status-check artifacts for long-running goals?
11. Rollback/Cutover: For migrations, deployments, data changes, or risky auth/payment work, what rollback, cutover, rehearsal, and operator handoff boundaries apply?
12. Finalization: What cleanup, review, documentation, or handoff must happen before marking the goal complete?

## Output Rules

Read [references/goal-brief-template.md](references/goal-brief-template.md) before drafting the final brief.

The final brief must include:

- A task-specific `Goal Objective` sentence.
- A clear `/goal` command section the user can copy or attach.
- Captured user requirements, decisions, examples, rejected paths, and wording preferences that matter when moving to a new thread.
- Verifiable completion criteria.
- Allowed tools and environments.
- Explicit non-goals and forbidden shortcuts.
- Progress reporting instructions for long-running work.
- Rollback/cutover instructions when the goal touches migrations, deployments, data, auth, billing, or other risky systems.
- Final review and cleanup requirements.
- Open questions, if any, with conservative default assumptions.

Keep the brief practical and operational. Avoid motivational language, broad aspirations, and vague acceptance criteria such as "make it better" unless paired with measurable checks.

## Quality Gate

Before finishing, check whether the brief answers:

- What exactly should Codex accomplish?
- How will Codex know it is done?
- Where should Codex start?
- What should Codex avoid?
- What evidence should Codex leave behind?
- What cleanup or review is required before completion?

If any answer is missing and materially changes implementation risk, ask another interview question instead of finalizing.
