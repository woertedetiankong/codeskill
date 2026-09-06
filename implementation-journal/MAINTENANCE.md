# Maintaining This Skill

Guidance for editing the skill itself. Nothing in this file is loaded at runtime; do not reference it from SKILL.md.

- When changing SKILL.md or the references, validate with isolated subagents or thread forks if the environment supports them. Give each agent a realistic scenario and the skill artifact, not your expected answer. If no subagent facility is available, skip this step and note the limitation.
- Each rule lives in exactly one place: creation conditions and triggers in SKILL.md; formats, field definitions, and deep guidance in `references/`. Before adding text, search the other files for restatements of the same rule and consolidate instead of duplicating.
- `agents/openai.yaml` is metadata for a non-Claude harness; Claude Code ignores it. Keep it only while the skill is used with that harness.
- `hooks/` holds optional Claude Code hook scripts and their install snippet (hooks/README.md). Nothing loads them automatically — the user installs them into settings.json by hand. Keep their journal-file paths and validator invocation in sync with SKILL.md defaults and the script.
- `scripts/validate_journal.py` mechanically mirrors rules that live in SKILL.md and `references/` (handoff frontmatter and sections, restart-verify shape, relative-date bans, log entry format, session-entry fields, template placeholders). When editing those rules, update the script's checks in the same change, and rerun it against one known-good and one deliberately broken fixture dossier before shipping.
