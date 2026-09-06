# Claude Code Hooks for implementation-journal

Optional harness enforcement for the skill's two weakest prompt-only guarantees: session-start continuity and immediate validation feedback. Nothing here is loaded automatically — installing means pasting the snippet below into a settings file yourself.

## What each hook does

- `session-start.sh` (SessionStart): when the project has `docs/tasks/NEXT-SESSION.md`, its content is injected into context at session start — resume becomes zero-effort, no pasting. When the session start was caused by compaction (`source: "compact"`), it also injects a reminder to refresh `handoff.md` and the restart entry, covering the *unplanned* context loss the skill's "refresh before any planned pause" rule cannot catch. Exits silently in projects without a journal, so a global install is safe.
- `post-edit-validate.sh` (PostToolUse on Edit/Write): after any edit to a file under `docs/tasks/`, runs `scripts/validate_journal.py` on that file and feeds ERROR lines straight back to Claude via exit code 2. The edit is not blocked; warnings are deliberately excluded so drafting isn't nagged — they stay in the quality-gate run.

A separate PreCompact hook was considered and rejected: PreCompact hook output is not added to Claude's context, so it cannot instruct the session to refresh anything. The SessionStart `compact` source is the working equivalent, firing immediately after compaction.

## Install

Add to `~/.claude/settings.json` (all projects) or `<project>/.claude/settings.json` (one project). If a `hooks` key already exists, merge these entries into it:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"/mnt/d/llm/skill op/implementation-journal/hooks/session-start.sh\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"/mnt/d/llm/skill op/implementation-journal/hooks/post-edit-validate.sh\""
          }
        ]
      }
    ]
  }
}
```

Notes:

- The paths contain a space, hence the inner quotes. If you later symlink the skill into `~/.claude/skills/implementation-journal`, point the commands there instead.
- The SessionStart entry has no `matcher`, so it fires on every source (`startup`, `resume`, `clear`, `compact`); the script branches on the source itself.
- Both scripts need `python3` on PATH (the validator already does).
- Hook changes are picked up when a session starts; restart or run `/hooks` to verify registration.
- Uninstall by removing the entries again — the scripts keep no state.

## Review checklist before installing

- Read both scripts; they only read stdin JSON, read journal files, and run the bundled validator. Neither writes files or touches the network.
- If your repos keep dossiers somewhere other than `docs/tasks/`, adjust the path in both scripts first.
