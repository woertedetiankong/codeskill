# Report

The report is the human layer of a finished milestone: a short, visual summary a person reads after development instead of the handoff and log. It restates what the dossier already records in plain language; it is never a source of truth. When the report and the Markdown disagree, the Markdown wins and the report is fixed.

When to write it lives in SKILL.md. This file covers location, wording rules, and fields. A filled sample is in [report-example.json](report-example.json).

## Location

One report per milestone, inside its dossier:

```text
docs/tasks/<YYYY-MM-DD>-<slug>/report.json
```

`scripts/render_report.py` turns it into `report.html` beside it and refreshes `docs/tasks/index.html`, the overview of every milestone. `scripts/validate_journal.py` checks the fields, limits, and wording bans below.

## Wording Rules

These apply to every string in the file.

- Write for someone who did not watch the work. Use the names people see in the product ("Checkout page"), not code names.
- Never include file paths, code identifiers, commit hashes, PR numbers, branch names, commands, URLs, or Markdown syntax. Never include restart steps, red lines, or environment state. All of those stay in the handoff.
- Explain through a moment, not a rule: a person does something and sees a result. Invented example people ("Maya") are fine; real customer data is not.
- Say what is true for users now, not what Claude did. "Shoppers can pay without leaving the page", not "Implemented hosted payment fields".
- Use only facts the dossier records. Do not invent numbers.
- Dates are `YYYY-MM-DD`; the page formats them.
- Stay inside the word limits below. A limit that feels tight means the sentence is carrying detail that belongs in the log.

| Instead of | Write |
|---|---|
| Integrated provider SDK hosted fields (a3f9c21) | Payment company's secure box |
| Added `.well-known/apple-developer-merchantid-domain-association` | Apple Pay needs our site verified first |
| Persist tokens for guest checkout? | Can guests save their card for next time? |

## Fields

Every top-level field is required except `plan`. Write `[]` for an empty list rather than leaving the field out, so a missing field always means a mistake.

| Field | Shape | Limit | Comes from |
|---|---|---|---|
| `version` | `1` | | |
| `project` | text | 4 words | Repo or product name |
| `milestone` | text | 6 words | Task brief title |
| `finished` | date | | Handoff `updated` |
| `outcome` | `done`, `partial`, or `dropped` | | Handoff status and success criteria |
| `headline` | text | 12 words | Summary, rewritten as what users get |
| `goal` | text | 20 words | Task brief Goal |
| `doneWhen` | list of `{text, met}` | 1–5 items; text 8 words | Success criteria; `met` is true or false |
| `changes` | list of `{what, before, after}` | 0–5 items; what 5 words, before and after 6 words each | Summary and changed surfaces |
| `decisions` | list of `{date, picked, over, why, by}` | 0–6 items; picked and over 8 words, why 15 words | Key and closed decisions, log entries; `by` is `claude` or `you` |
| `story` | list of `{date, kind, title, summary, example, why}` | 1–10 items; title 10, summary 15, example 35, why 20 words | Log entries plus start and finish |
| `dropped` | list of `{what, date, instead, why}` | 0–5 items; what 6, instead 8, why 15 words | Abandoned approaches and cut scope; `instead` may be `null` |
| `risks` | list of `{risk, action, when}` | 0–3 items; risk 12, action 15, when 4 words | Known risks the reader can act on |
| `touched` | list of text | 0–6 items; 4 words each | Changed surfaces, as product areas |
| `docsUpdated` | list of text | 0–6 items; 4 words each | Docs and wiki section |
| `followUps` | list of text | 0–3 items; 12 words each | Follow-ups and next steps |
| `plan` | `{name, steps}` | optional; name 6 words | Plan status dashboard; omit when there is no parent plan |

`story.kind` is one of `started`, `decision`, `found` (a hidden constraint or discovery), `changed-course` (an approach abandoned or the plan deviated), `paused`, `finished`. Pick the five to ten moments a person would want to hear about, not every log entry.

`plan.steps` is a list of `{name, state, date, note, thisMilestone}`: `name` 4 words; `state` one of `done`, `current`, `next`, `later`, `dropped`; `date` optional; `note` optional, 8 words; `thisMilestone` true on exactly one step.

A risk without an action does not belong here. Either name what someone can do about it and when, or leave it in the handoff.

## Checks By Judgment

The validator can check shape, limits, and banned patterns. It cannot check these:

- Every fact traces to the task brief, handoff, or log.
- The headline says what changed for users, not what work happened.
- Each example shows one concrete moment, not the rule restated.
- `outcome` matches the success criteria: `done` only when every `doneWhen` item is met.
