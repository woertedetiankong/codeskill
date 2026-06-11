# Handoff Discipline

Use this reference when creating or refreshing a cross-session handoff. The goal is restart continuity: a new human or AI session should know what is true, what to verify first, what to do next, and what not to touch.

## Three-Layer Model

1. `handoff.md`: the authority for the current milestone state.
2. New-session entry: a short top section in `tasks/todo.md` or the repo's established session entry file. It points to the latest handoff and records errata if a handoff section became stale.
3. Restart opener: a pasteable first message for the next AI session. It compresses the file pointers, immediate next steps, verify command, and red lines.

Keep these layers distinct. The entry is a pointer and errata layer, not a second handoff. The opener is a launch instruction, not a status document.

## Minimum Handoff Fields

Every restart-ready handoff should include:

- Current state: one sentence saying where the milestone stands.
- Git and persistent state: branch, key commit hashes, PR state, unpushed work, generated artifacts, migrations, or external state that matters.
- Environment state: special local/runtime state that changes the safe next action, such as the current checkout driving production hooks, a required service already running, or a temporary data snapshot in use.
- Session results with evidence: what changed and the proof, such as commits, test results, manual checks, review findings, or produced artifacts.
- Cross-module references: stable links to upstream dependencies and downstream dependents when the work touches module boundaries or shared contracts.
- Next backlog by ROI: the next actions in priority order, with short reasons.
- Closed decisions: rejected options and one-line reasons. Label them so future agents do not reopen them accidentally.
- Restart verify: commands or checks that can be run first, with expected output and what a mismatch means.
- Environment constraints and gotchas: non-obvious services, env vars, data safety rules, local state, or operational hazards.
- Red lines: enforceable instructions such as "do not push without user approval" or "do not run destructive migration commands automatically."
- Docs/wiki sync: what durable knowledge was updated, skipped, or still needs reconciliation.

## Restart Verify

Make verification concrete enough to run immediately:

```bash
<command 1>  # expected: <observable output>; mismatch means: <diagnosis>
<command 2>  # expected: <observable output>; mismatch means: <diagnosis>
```

Prefer checks that anchor reality: `git log --oneline -2`, branch/status checks, targeted tests, schema/version checks, row counts, generated file hashes, service health endpoints, or CLI dry runs.

Do not write "verify manually" when a command would be more precise. If validation is manual, state the exact screen, file, API response, or artifact to inspect.

## New-Session Entry

Place this at the top of the repo's existing todo/session file, or use `tasks/todo.md` if no convention exists:

```markdown
## New Session Entry

- Read first: `<handoff path>`.
- Errata: <known stale section in handoff, or "None known">.
- Current board: <3-6 bullets summarizing state and next action>.
- Environment: <special environment state or "None known">.
- Red lines: <enforceable constraints>.
- First verify: `<command>`; expected <output>; mismatch means <diagnosis>.
```

When a new handoff supersedes the old one, update this entry. Keep older entries only if the repo already preserves historical entries; otherwise link history from the handoff chain.

## Restart Opener

Add a short pasteable opener to the handoff when the work may continue in a new chat:

```text
Project <path> (<name>). Read <handoff path> and <new-session entry path> first.
Previous session: <one-sentence result with evidence>.
Current state: <one-sentence board>.
Environment: <special environment state or "None known">.
Now do: 1. <next step> 2. <next step>.
Red lines: <enforceable instruction>; <enforceable instruction>.
First verify: <command> (expected <output>; mismatch means <diagnosis>).
```

Write red lines as commands the agent can obey. "Be careful" is not enforceable; "do not push until the user explicitly says push" is enforceable.

## Write-Back Discipline

Write back after each verified work unit, such as a passing test run, a committed change, a settled decision, an unblocked dependency, or a newly discovered risk. Record progress plus evidence plus changed next steps.

Do not mark work done without evidence. If tests were not run, say so. If a PR is not merged, do not write that it is merged.

## History And Knowledge Boundaries

Do not silently rewrite append-only implementation logs. For handoffs, prefer rewriting to current truth near completion; if preserving historical handoff snapshots is a project convention, create a new handoff and link it with `supersedes`.

Handoff stores operational state needed for the next session. Durable lessons, reusable architecture knowledge, integration contracts, and conventions belong in README/docs/wiki/decision records.
