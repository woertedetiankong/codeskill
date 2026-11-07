#!/usr/bin/env python3
"""Validate implementation-journal artifacts against the skill's discipline.

Checks the mechanical rules from SKILL.md and references/ so drift is caught
by a command instead of model diligence:

- handoff.md: frontmatter (status/updated), required sections, a runnable
  Restart Verify block with expected outputs, no "verify manually",
  read budget (WARN past HANDOFF_MAX_LINES).
- task-brief.md: Goal, Success Criteria, Parent plan, Created date.
- implementation-log.md: dated entry headings; consistency with the handoff
  (a missing log must be declared "Not required" in the handoff).
- NEXT-SESSION.md: handoff pointer that resolves, Errata / Now do /
  Red lines / First verify fields.
- report.json: the fields, choices, dates, list sizes, and word limits in
  references/report.md; no agent-facing text (hashes, paths, URLs, code
  names, Markdown); outcome agrees with doneWhen; one thisMilestone step.
  WARN when the handoff beside it is not Complete or report.html is
  missing or older than the JSON.
- Markdown files: relative-date phrases ("today", "last week", ...), broken
  relative links, leftover template placeholders. Code fences are skipped.

Usage:
  validate_journal.py [PATH ...] [--strict]

PATH may be a tasks directory (default: docs/tasks), a dossier directory,
or individual files; file roles are inferred from names. Exit 1 on ERROR
(or on WARN too with --strict), 0 otherwise. Repos with their own
conventions can pass explicit paths; unknown layouts degrade to warnings.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
RELATIVE_DATE_RE = re.compile(
    r"\b(today|yesterday|tomorrow|recently"
    r"|last week|next week|this week|last month|next month)\b",
    re.IGNORECASE,
)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)[^)]*\)")
PLACEHOLDERS = (
    "<YYYY-MM-DD>", "<command 1>", "<Verifiable criterion>",
    "<One concrete sentence", "<observable output>", "<milestone or slice>",
    "<Next action", "<one-sentence result", "<enforceable instruction",
    "<Decision and rationale", "<Risk>", "<Follow-up>", "<Assumption or",
    "<path or subsystem>", "<special environment state",
)
HANDOFF_REQUIRED = ("Summary", "Current State", "Next Steps", "Restart Verify")
# references/handoff-discipline.md read budget.
HANDOFF_MAX_LINES = 100
# Always written even when one line, because their absence is ambiguous.
HANDOFF_DECLARE = ("Git And Persistent State", "Implementation Log")
# A conditional section whose every line matches this is placeholder-only
# and should be omitted per references/handoff-discipline.md.
NONEISH_RE = re.compile(
    r"^(?:[\w /()-]+:)?\s*(?:none(?: known| yet)?|unknown(?:/not applicable)?"
    r"|not applicable|n/a)\s*\.?\s*$",
    re.IGNORECASE,
)

# references/report.md: the plain-language report of a closed milestone.
REPORT_NAME = "report.json"
REPORT_TEXT = {"project": 4, "milestone": 6, "headline": 12, "goal": 20}
OUTCOMES = ("done", "partial", "dropped")
STORY_KINDS = ("started", "decision", "found", "changed-course", "paused", "finished")
STEP_STATES = ("done", "current", "next", "later", "dropped")
# field: (min items, max items, {key: spec}). A spec is a word limit for
# required text, "?N" for text-or-null, "date", "bool", or a tuple of choices.
REPORT_LISTS = {
    "doneWhen": (1, 5, {"text": 8, "met": "bool"}),
    "changes": (0, 5, {"what": 5, "before": 6, "after": 6}),
    "decisions": (0, 6, {"date": "date", "picked": 8, "over": 8, "why": 15,
                         "by": ("claude", "you")}),
    "story": (1, 10, {"date": "date", "kind": STORY_KINDS, "title": 10,
                      "summary": 15, "example": 35, "why": 20}),
    "dropped": (0, 5, {"what": 6, "date": "date", "instead": "?8", "why": 15}),
    "risks": (0, 3, {"risk": 12, "action": 15, "when": 4}),
}
# field: (max items, words per item)
REPORT_TEXT_LISTS = {"touched": (6, 4), "docsUpdated": (6, 4), "followUps": (3, 12)}
REPORT_LANGS = ("en", "zh")
REPORT_KEYS = {"version", "finished", "outcome", "plan", "lang", "flow", "code",
               *REPORT_TEXT, *REPORT_LISTS, *REPORT_TEXT_LISTS}
# Optional "flow" diagram and "code" block (references/report.md).
FLOW_STATES = ("new", "changed", "same")
FLOW_LIMITS = {"nodes": (2, 6), "edges": (1, 8)}
CODE_LIMITS = {"commits": 20, "areas": 8, "paths": 6}
COMMIT_REF_RE = re.compile(r"[0-9a-f]{7,40}")
# Agent-facing detail that belongs in the handoff, never in the report.
REPORT_BANNED = (
    (re.compile(r"\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b"), "a commit hash"),
    (re.compile(r"(?:\bPR\s*)?#\d+\b"), "a PR or issue number"),
    (re.compile(r"https?://|\bwww\."), "a URL"),
    (re.compile(r"`|\*\*|\]\(|^#{1,6}\s"), "Markdown syntax"),
    (re.compile(r"(?:^|\s)\.{0,2}/\w|\b\w[\w.-]*/[\w.-]+/"
                r"|\b[\w-]+\.(?:py|jsx?|tsx?|md|json|html|css|scss|go|rs|java|kt|rb|php|sh|ya?ml|toml|sql|lock)\b"),
     "a file path"),
    (re.compile(r"\b[a-z][a-z0-9]*_[a-z0-9_]+\b|\b\w+\(\)"), "a code identifier"),
)


class Report:
    def __init__(self):
        self.errors = 0
        self.warnings = 0

    def error(self, path, line, msg):
        self.errors += 1
        print(f"{path}:{line}: ERROR {msg}")

    def warn(self, path, line, msg):
        self.warnings += 1
        print(f"{path}:{line}: WARN {msg}")


def read_lines(path):
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def fence_mask(lines):
    """True per line when inside a fenced code block (fence lines included)."""
    mask, inside = [], False
    for line in lines:
        if line.lstrip().startswith(("```", "~~~")):
            inside = not inside
            mask.append(True)
        else:
            mask.append(inside)
    return mask


def parse_frontmatter(lines):
    """Return (dict, last_line_index) for a leading --- block, or ({}, 0)."""
    if not lines or lines[0].strip() != "---":
        return {}, 0
    fields = {}
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return fields, i
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return {}, 0


def sections(lines):
    """Map '## Heading' -> (line_no, body_text)."""
    found, current, start = {}, None, 0
    for i, line in enumerate(lines):
        match = re.match(r"##\s+(.*)", line)
        if match:
            if current:
                found[current] = (start, "\n".join(lines[start: i]))
            current, start = match.group(1).strip(), i + 1
    if current:
        found[current] = (start, "\n".join(lines[start:]))
    return found


def check_common(path, lines, report):
    """Relative dates, broken relative links, leftover template placeholders."""
    mask = fence_mask(lines)
    for i, line in enumerate(lines, start=1):
        if mask[i - 1]:
            continue
        match = RELATIVE_DATE_RE.search(line)
        if match:
            report.warn(path, i, f'relative date "{match.group(0)}" — use an absolute YYYY-MM-DD date')
        for placeholder in PLACEHOLDERS:
            if placeholder in line:
                report.warn(path, i, f'template placeholder "{placeholder}" left unfilled')
        for target in LINK_RE.findall(line):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = (path.parent / target.split("#")[0]).resolve()
            if not resolved.exists():
                report.error(path, i, f"broken relative link: {target}")


def check_handoff(path, report):
    lines = read_lines(path)
    if len(lines) > HANDOFF_MAX_LINES:
        report.warn(path, len(lines),
                    f"handoff is {len(lines)} lines (budget {HANDOFF_MAX_LINES}) — move narrative into implementation-log.md")
    fm, _ = parse_frontmatter(lines)
    status = fm.get("status", "")
    if not re.match(r"(Complete|Provisional)\b", status):
        report.error(path, 1, 'frontmatter "status:" must be Complete or Provisional')
    if not DATE_RE.search(fm.get("updated", "")):
        report.error(path, 1, 'frontmatter "updated:" must carry a YYYY-MM-DD date')

    found = sections(lines)
    for name in HANDOFF_REQUIRED:
        if name not in found:
            report.error(path, 1, f'missing required section "## {name}"')
    for name in HANDOFF_DECLARE:
        if name not in found:
            report.warn(path, 1, f'missing "## {name}" — always declare it, one line is enough')
    if status.startswith("Complete") and "Validation" not in found:
        report.warn(path, 1, 'status Complete but no "## Validation" section — record the evidence')

    for name, (line_no, body) in found.items():
        if name in HANDOFF_REQUIRED or name in HANDOFF_DECLARE:
            continue
        content = [l.strip().lstrip("-*").strip() for l in body.splitlines()]
        content = [l for l in content if l and not l.startswith("```")]
        if not content or all(NONEISH_RE.match(l) for l in content):
            report.warn(path, line_no,
                        f'section "## {name}" is empty or placeholder-only — omit conditional sections instead')

    if "Restart Verify" in found:
        line_no, body = found["Restart Verify"]
        commands = [l for l in body.splitlines()
                    if l.strip() and not l.strip().startswith(("```", "#"))]
        if not commands:
            report.error(path, line_no, "Restart Verify has no runnable command")
        if "expected" not in body:
            report.error(path, line_no, "Restart Verify commands must state expected output")
        elif "mismatch" not in body:
            report.warn(path, line_no, "Restart Verify should say what a mismatch means")

    for i, line in enumerate(lines, start=1):
        if "verify manually" in line.lower():
            report.warn(path, i, 'says "verify manually" — name the exact command, screen, file, or artifact')

    log_section = found.get("Implementation Log")
    log_file = path.parent / "implementation-log.md"
    if not log_file.exists():
        if log_section and "not required" not in log_section[1].lower():
            report.warn(path, log_section[0],
                        'no implementation-log.md: section must say "Not required" with the reason')
    elif log_section and "implementation-log.md" not in log_section[1]:
        report.warn(path, log_section[0], "implementation-log.md exists but is not referenced here")


def check_brief(path, report):
    lines = read_lines(path)
    text = "\n".join(lines)
    for heading in ("## Goal", "## Success Criteria", "## Scope", "## Constraints"):
        if heading not in text:
            report.error(path, 1, f'missing section "{heading}"')
    if "Parent plan:" not in text:
        report.warn(path, 1, 'missing "Parent plan:" line (use "None found" when no plan exists)')
    if not any("Created:" in l and DATE_RE.search(l) for l in lines):
        report.warn(path, 1, 'missing "Created: YYYY-MM-DD" line')


def check_log(path, report):
    text = "\n".join(read_lines(path))
    if not re.search(r"^###\s+\d{4}-\d{2}-\d{2}", text, re.MULTILINE):
        report.error(path, 1, "no dated entry heading (### YYYY-MM-DD); an empty log should not exist")


def check_next_session(path, report):
    lines = read_lines(path)
    text = "\n".join(lines)
    pointer = re.search(r"Read\s+`([^`]+)`\s+first", text)
    if not pointer:
        report.error(path, 1, 'missing handoff pointer ("Read `<handoff path>` first")')
    else:
        target = Path(pointer.group(1))
        # Pointers may be written relative to the entry, the repo root, or
        # any directory between, so try every ancestor; cwd-independent.
        bases = [path.resolve().parent, *path.resolve().parents]
        if not (target.is_absolute() and target.exists()) \
                and not any((base / target).exists() for base in bases):
            report.error(path, 1, f"handoff pointer does not resolve: {pointer.group(1)}")
    for field in ("Errata:", "Now do:", "Red lines:", "First verify:"):
        if field not in text:
            report.warn(path, 1, f'missing "{field}" field')


# Chinese, Japanese, and Korean characters: two of them count as one word.
CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af]")


def word_count(text):
    """Space-separated words with a letter or digit, plus CJK characters two to a word."""
    cjk = len(CJK_RE.findall(text))
    rest = CJK_RE.sub(" ", text)
    return sum(1 for token in rest.split() if re.search(r"\w", token)) + (cjk + 1) // 2


def json_strings(value):
    """Every string inside a parsed JSON value."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from json_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from json_strings(item)


def check_flow(path, report, flow, check_value):
    nodes = flow.get("nodes") if isinstance(flow, dict) else None
    edges = flow.get("edges") if isinstance(flow, dict) else None
    if not isinstance(nodes, list) or not isinstance(edges, list):
        report.error(path, 1, "flow must be {nodes, edges}, or be left out")
        return
    low, high = FLOW_LIMITS["nodes"]
    if not low <= len(nodes) <= high:
        report.error(path, 1, f"flow has {len(nodes)} nodes (allowed {low}-{high}) — draw only the parts that changed and their neighbours")
    ids = set()
    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            report.error(path, 1, f"flow.nodes[{i}] must be an object")
            continue
        node_id = node.get("id")
        if not (isinstance(node_id, str) and node_id.strip()):
            report.error(path, 1, f"flow.nodes[{i}].id must be non-empty text")
        elif node_id in ids:
            report.error(path, 1, f'flow.nodes[{i}].id "{node_id}" is used twice')
        else:
            ids.add(node_id)
        check_value(f"flow.nodes[{i}].label", node.get("label"), 6)
        if "note" in node:
            check_value(f"flow.nodes[{i}].note", node["note"], 8)
        check_value(f"flow.nodes[{i}].state", node.get("state"), FLOW_STATES)
    low, high = FLOW_LIMITS["edges"]
    if not low <= len(edges) <= high:
        report.error(path, 1, f"flow has {len(edges)} edges (allowed {low}-{high})")
    for i, edge in enumerate(edges):
        if not isinstance(edge, dict):
            report.error(path, 1, f"flow.edges[{i}] must be an object")
            continue
        for end in ("from", "to"):
            if edge.get(end) not in ids:
                report.error(path, 1, f'flow.edges[{i}].{end} must name a node id')
        if edge.get("from") == edge.get("to"):
            report.error(path, 1, f"flow.edges[{i}] points at its own node")
        if "label" in edge:
            check_value(f"flow.edges[{i}].label", edge["label"], 4)


def git_commit_exists(repo, ref):
    try:
        out = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.returncode == 0


def check_code(path, report, code, check_value):
    commits = code.get("commits") if isinstance(code, dict) else None
    areas = code.get("areas") if isinstance(code, dict) else None
    if not isinstance(commits, list) or not isinstance(areas, list):
        report.error(path, 1, "code must be {commits, areas}, or be left out")
        return
    if not commits and not areas:
        report.error(path, 1, "code has no commits and no areas — leave it out instead")
    if len(commits) > CODE_LIMITS["commits"]:
        report.error(path, 1, f'code.commits has {len(commits)} items (allowed 0-{CODE_LIMITS["commits"]})')
    try:
        inside = subprocess.run(["git", "-C", str(path.parent), "rev-parse", "--is-inside-work-tree"],
                                capture_output=True, text=True, timeout=10).returncode == 0
    except (OSError, subprocess.SubprocessError):
        inside = False
    for i, ref in enumerate(commits):
        if not (isinstance(ref, str) and COMMIT_REF_RE.fullmatch(ref)):
            report.error(path, 1, f"code.commits[{i}] must be a commit hash (7-40 hex characters)")
        elif inside and git_commit_exists(path.parent, ref) is False:
            report.warn(path, 1, f"code.commits[{i}] {ref} is not in this repository — the page will show it without numbers")
    if len(areas) > CODE_LIMITS["areas"]:
        report.error(path, 1, f'code.areas has {len(areas)} items (allowed 0-{CODE_LIMITS["areas"]})')
    for i, area in enumerate(areas):
        if not isinstance(area, dict):
            report.error(path, 1, f"code.areas[{i}] must be an object")
            continue
        check_value(f"code.areas[{i}].what", area.get("what"), 8)
        paths = area.get("paths")
        if not isinstance(paths, list) or not 1 <= len(paths) <= CODE_LIMITS["paths"]:
            report.error(path, 1, f'code.areas[{i}].paths must list 1-{CODE_LIMITS["paths"]} repo paths')
            continue
        for j, item in enumerate(paths):
            if not (isinstance(item, str) and item.strip()) or item.startswith("/") or ".." in item.split("/") \
                    or re.match(r"https?://", item):
                report.error(path, 1, f"code.areas[{i}].paths[{j}] must be a path relative to the repo root")


def check_report(path, report):
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        report.error(path, exc.lineno, f"not valid JSON: {exc.msg}")
        return
    if not isinstance(data, dict):
        report.error(path, 1, "report must be a JSON object")
        return

    def line_of(value):
        if isinstance(value, str):
            # Prefer a match in value position, so a value that is also a key
            # (e.g. "milestone") points at the right line.
            dumped = (json.dumps(value, ensure_ascii=False), json.dumps(value))
            for needle in (*(": " + d for d in dumped), *dumped):
                index = text.find(needle)
                if index >= 0:
                    return text.count("\n", 0, index) + 1
        return 1

    def check_value(name, value, spec):
        if isinstance(spec, str) and spec.startswith("?"):
            if value is None:
                return
            spec = int(spec[1:])
        line = line_of(value)
        if spec == "date":
            if not (isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)):
                report.error(path, line, f"{name} must be a YYYY-MM-DD date")
        elif spec == "bool":
            if not isinstance(value, bool):
                report.error(path, line, f"{name} must be true or false")
        elif isinstance(spec, tuple):
            if value not in spec:
                report.error(path, line, f"{name} must be one of: {', '.join(spec)}")
        elif not (isinstance(value, str) and value.strip()):
            report.error(path, line, f"{name} must be non-empty text")
        elif word_count(value) > spec:
            report.error(path, line, f"{name} is {word_count(value)} words (limit {spec}) "
                                     "— keep the detail in the log")

    if data.get("version") != 1:
        report.error(path, 1, "version must be 1")
    if "lang" in data:
        check_value("lang", data["lang"], REPORT_LANGS)
    headline = data.get("headline") if isinstance(data.get("headline"), str) else ""
    if CJK_RE.search(headline) and data.get("lang") != "zh":
        report.warn(path, 1, 'headline is Chinese but "lang" is not "zh" — the page labels will be English')
    elif data.get("lang") == "zh" and headline and not CJK_RE.search(headline):
        report.warn(path, 1, '"lang" is "zh" but the headline is not Chinese')
    for key in sorted(set(data) - REPORT_KEYS):
        report.warn(path, 1, f'unknown field "{key}" — references/report.md lists the fields')
    singles = [*REPORT_TEXT.items(), ("finished", "date"), ("outcome", OUTCOMES)]
    for key, spec in singles:
        if key not in data:
            report.error(path, 1, f'missing field "{key}"')
        else:
            check_value(key, data[key], spec)

    for key, (low, high, fields) in REPORT_LISTS.items():
        items = data.get(key)
        if not isinstance(items, list):
            report.error(path, 1, f'"{key}" must be a list (write [] when empty)')
            continue
        if not low <= len(items) <= high:
            report.error(path, 1, f'"{key}" has {len(items)} items (allowed {low}-{high})')
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                report.error(path, 1, f"{key}[{i}] must be an object")
                continue
            for field, spec in fields.items():
                if field not in item:
                    report.error(path, 1, f'{key}[{i}] is missing "{field}"')
                else:
                    check_value(f"{key}[{i}].{field}", item[field], spec)

    for key, (high, limit) in REPORT_TEXT_LISTS.items():
        items = data.get(key)
        if not isinstance(items, list):
            report.error(path, 1, f'"{key}" must be a list (write [] when empty)')
            continue
        if len(items) > high:
            report.error(path, 1, f'"{key}" has {len(items)} items (allowed 0-{high})')
        for i, item in enumerate(items):
            check_value(f"{key}[{i}]", item, limit)

    if "plan" in data:
        plan = data["plan"]
        steps = plan.get("steps") if isinstance(plan, dict) else None
        if not isinstance(steps, list) or not steps:
            report.error(path, 1, "plan must be {name, steps} with at least one step, or be left out")
        else:
            check_value("plan.name", plan.get("name"), 6)
            marked = 0
            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    report.error(path, 1, f"plan.steps[{i}] must be an object")
                    continue
                check_value(f"plan.steps[{i}].name", step.get("name"), 4)
                check_value(f"plan.steps[{i}].state", step.get("state"), STEP_STATES)
                if "date" in step:
                    check_value(f"plan.steps[{i}].date", step["date"], "date")
                if "note" in step:
                    check_value(f"plan.steps[{i}].note", step["note"], 8)
                if step.get("thisMilestone") is True:
                    marked += 1
            if marked != 1:
                report.error(path, 1, f"plan.steps must mark exactly one thisMilestone (found {marked})")

    if "flow" in data:
        check_flow(path, report, data["flow"], check_value)
    if "code" in data:
        check_code(path, report, data["code"], check_value)

    # The code block is the one place for paths and commits; everything else is prose.
    prose = {key: value for key, value in data.items() if key != "code"}
    for value in json_strings(prose):
        for pattern, what in REPORT_BANNED:
            if pattern.search(value):
                report.error(path, line_of(value),
                             f'looks like {what}: "{value}" — agent-facing detail stays in the handoff')
                break

    done_when = data.get("doneWhen")
    if isinstance(done_when, list):
        met = [item.get("met") is True for item in done_when if isinstance(item, dict)]
        if data.get("outcome") == "done" and not all(met):
            report.error(path, 1, 'outcome is "done" but a doneWhen item is not met')
        if data.get("outcome") == "partial" and met and all(met):
            report.warn(path, 1, 'outcome is "partial" but every doneWhen item is met')

    handoff = path.with_name("handoff.md")
    if not handoff.exists():
        report.warn(path, 1, "no handoff.md beside the report — a report summarizes a closed milestone")
    else:
        status = parse_frontmatter(read_lines(handoff))[0].get("status", "")
        if not status.startswith("Complete"):
            report.warn(path, 1, "handoff.md is not Complete — write the report when the milestone closes")
    page = path.with_name("report.html")
    if not page.exists():
        report.warn(path, 1, "report.html not rendered — run scripts/render_report.py")
    elif page.stat().st_mtime < path.stat().st_mtime:
        report.warn(path, 1, "report.html is older than report.json — rerun scripts/render_report.py")


def classify(path):
    name = path.name.lower()
    if name == REPORT_NAME:
        return check_report
    if "handoff" in name:
        return check_handoff
    if "brief" in name:
        return check_brief
    if "implementation-log" in name or name == "log.md":
        return check_log
    if "next-session" in name:
        return check_next_session
    return None


def collect(paths):
    """Expand args into journal files; default tasks dir when none given."""
    if not paths:
        default = Path("docs/tasks")
        if not default.is_dir():
            print("No paths given and docs/tasks not found; pass the tasks dir, "
                  "dossier dirs, or files explicitly.", file=sys.stderr)
            sys.exit(2)
        paths = [default]
    files = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(sorted(p.rglob("*.md")))
            files.extend(sorted(p.rglob(REPORT_NAME)))
        elif p.is_file():
            files.append(p)
        else:
            print(f"Path not found: {p}", file=sys.stderr)
            sys.exit(2)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", help="tasks dir, dossier dirs, or files")
    parser.add_argument("--strict", action="store_true", help="warnings also fail")
    args = parser.parse_args()

    report = Report()
    files = collect(args.paths)
    checked = 0
    for path in files:
        checker = classify(path)
        if path.suffix.lower() == ".md":
            check_common(path, read_lines(path), report)
        if checker:
            checker(path, report)
            checked += 1

    print(f"\n{len(files)} file(s) scanned, {checked} journal file(s) checked: "
          f"{report.errors} error(s), {report.warnings} warning(s)")
    if report.errors or (args.strict and report.warnings):
        sys.exit(1)


if __name__ == "__main__":
    main()
