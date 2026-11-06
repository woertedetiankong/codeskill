# codeskill

Personal Codex skills.

## Skills

- `tdd` - Test-driven development with a red-green-refactor loop.
- `improve-codebase-architecture` - Architecture review workflow for finding deepening opportunities in a codebase.
- `transparent-workshop-illustrations` - D-style Chinese technical article body illustrations.
- `implementation-journal` - Plan-linked task dossiers, implementation memory, handoffs, project wiki reconciliation, and a visual report when a milestone closes.
- `goal-brief-builder` - Plan-mode interview workflow for drafting `/goal`-ready development briefs.
- `html` - Self-contained HTML artifacts in the effective HTML style.
- `html-diagram` - Full-screen HTML/SVG architecture diagrams in the effective HTML style.
- `html-plan` - Pragmatic, visually organized self-contained HTML plan pages.

## Install

### implementation-journal in Claude Code

Install it as a plugin. This also registers its hooks and adds `/implementation-journal:report`, which renders the milestone reports and opens the overview page in your browser:

```text
/plugin marketplace add woertedetiankong/codeskill
/plugin install implementation-journal@codeskill
```

### Codex

Copy a skill directory into your Codex skills directory:

```sh
cp -R tdd ~/.codex/skills/
cp -R improve-codebase-architecture ~/.codex/skills/
cp -R transparent-workshop-illustrations ~/.codex/skills/
cp -R implementation-journal ~/.codex/skills/
cp -R goal-brief-builder ~/.codex/skills/
cp -R html ~/.codex/skills/
cp -R html-diagram ~/.codex/skills/
cp -R html-plan ~/.codex/skills/
```

To see implementation-journal's reports from Codex, ask for them (the skill runs the renderer with `--open`), or run this from the repo root:

```sh
python3 ~/.codex/skills/implementation-journal/scripts/render_report.py --open
```
