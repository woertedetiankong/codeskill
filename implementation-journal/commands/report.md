---
description: Render this repo's milestone reports and open the overview page in a browser
allowed-tools: Bash(python3:*)
---

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/render_report.py" --open 2>&1`

The lines above are the output of rendering the milestone reports in docs/tasks and opening the overview page. Reply in one or two sentences: which page opened, or, if it failed, what it means. "docs/tasks not found" means this repo has no journal yet; "No browser available" means the user should open the printed path themselves. Do not run any other command.
