#!/usr/bin/env python3
"""Render implementation-journal report.json files into report.html.

The report is the human layer of a finished milestone (references/report.md).
Each report.json becomes one self-contained report.html beside it: no network
requests, light and dark themes, readable on a phone.

The tasks directory also gets index.html, an overview of every milestone:
finished ones link to their report, and dossiers without a report show as a
single line (in progress, or finished without a report). The overview reads
only report.json, the task brief title, and the handoff status and date —
never the text of the handoff or log.

A report's optional "code" block is filled in from git: the renderer reads
the listed commits for file and line counts and links them to GitHub when
origin is a GitHub remote. Its optional "flow" block is drawn as an SVG.

Usage:
  render_report.py [PATH ...] [--open] [--repo DIR]

PATH may be a tasks directory (default: docs/tasks), a dossier directory, or
a report.json file. --open opens the overview (or the single report, when
there is no overview) in a browser. --repo names the git repository for the
code block when the report is not inside it. Run validate_journal.py first: this
script draws what it is given and skips sections that are empty or missing.
"""

import argparse
import html
import json
import re
import subprocess
import sys
import unicodedata
from urllib.parse import quote
import webbrowser
from pathlib import Path

REPORT_NAME = "report.json"
INDEX_NAME = "index.html"
DOSSIER_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9][a-z0-9-]*)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
OUTCOME_ICONS = {"done": "check", "partial": "half", "dropped": "x"}
KIND_ICONS = {
    "started": "flag", "decision": "fork", "found": "bulb",
    "changed-course": "turn", "paused": "pause", "finished": "check",
}

# Page text per report language (report.json "lang"; English when absent).
LABELS = {
    "en": {
        "html": "en", "sp": " ", "brand": "Journal", "theme": "Switch between light and dark",
        "outcome": {"done": "Done", "partial": "Partly done", "dropped": "Dropped"},
        "kind": {"started": "Started", "decision": "Decision", "found": "Found out",
                 "changed-course": "Changed course", "paused": "Paused", "finished": "Finished"},
        "step": {"done": "Done", "dropped": "Dropped", "current": "In progress",
                 "next": "Next", "later": "Later"},
        "finished_on": "Finished {date}", "closed_on": "Closed {date}",
        "result": "Result", "done_when": "Done when", "met": "{met} of {n} met", "not_met": "Not met: ",
        "plan": "The plan", "step_of": "Step {i} of {n}", "this": "This milestone",
        "changed": "What changed", "before": "Before", "now": "Now",
        "keep": "Keep in mind", "todo": "What to do:",
        "choices": "Choices made", "by_you": "You decided", "by_claude": "Claude decided",
        "why": "Why:", "instead_of": "Instead of: ",
        "story": "How it went", "show_ex": "Show example", "hide_ex": "Hide example",
        "show_why": "Show why it matters", "hide_why": "Hide why it matters",
        "matters": "Why it matters:",
        "dropped": "Dropped along the way", "instead": "Instead:", "dropped_on": "Dropped {date}",
        "touched": "Parts of the app touched", "docs": "Docs updated", "next": "What’s next",
        "details": "Details", "foot": "Written from this milestone’s journal on {date}.",
        "all": "All milestones", "title": "{name} report", "untitled": "Milestone",
        "ix_title": "{project} milestones", "ix_count_fin": "{n} finished",
        "ix_count_open": "{n} in progress", "ix_join": " and ", "ix_none": "No milestones yet",
        "ix_open": "In progress", "ix_fin": "Finished", "ix_no_report": "No report",
        "ix_started": "Started {date}", "ix_kicker_plan": "{milestone} in {plan}",
        "ix_goals": "{met} of {n} goals met", "ix_you_1": "1 choice by you",
        "ix_you_n": "{n} choices by you", "ix_risks": "{n} to keep in mind",
        "ix_empty": "When a milestone closes, its report shows up here.",
        "flow": "How it fits together", "flow_new": "New", "flow_changed": "Changed",
        "flow_same": "Already there", "code": "Where the code is", "code_sum": "{c} commits, {f} files",
        "code_lines": "+{a} −{d} lines", "code_files": "{n} files", "code_files_new": "{n} files, {k} new",
        "code_other": "Everything else", "code_commits": "Commits",
        "code_note": "Line counts leave out lock files and generated files.",
        "code_missing": "Not in the local repository",
    },
    "zh": {
        "html": "zh-CN", "sp": "", "brand": "开发日志", "theme": "切换深色或浅色",
        "outcome": {"done": "完成", "partial": "部分完成", "dropped": "已放弃"},
        "kind": {"started": "开始", "decision": "决定", "found": "发现",
                 "changed-course": "改变方向", "paused": "暂停", "finished": "完成"},
        "step": {"done": "已完成", "dropped": "已放弃", "current": "进行中",
                 "next": "下一步", "later": "之后"},
        "finished_on": "{date}完成", "closed_on": "{date}关闭",
        "result": "结果", "done_when": "完成标准", "met": "达成 {met}/{n}", "not_met": "未达成：",
        "plan": "计划", "step_of": "第 {i} 步，共 {n} 步", "this": "本里程碑",
        "changed": "有什么变化", "before": "之前", "now": "现在",
        "keep": "需要留意", "todo": "要做的事：",
        "choices": "做过的决定", "by_you": "你决定的", "by_claude": "Claude 决定的",
        "why": "原因：", "instead_of": "没选：",
        "story": "过程", "show_ex": "看例子", "hide_ex": "收起例子",
        "show_why": "看为什么重要", "hide_why": "收起",
        "matters": "为什么重要：",
        "dropped": "中途放弃的", "instead": "改为：", "dropped_on": "{date}放弃",
        "touched": "涉及的部分", "docs": "更新的文档", "next": "接下来",
        "details": "其他信息", "foot": "根据本里程碑的开发记录整理，{date}。",
        "all": "全部里程碑", "title": "{name}报告", "untitled": "里程碑",
        "ix_title": "{project}的里程碑", "ix_count_fin": "已完成 {n} 个",
        "ix_count_open": "进行中 {n} 个", "ix_join": "，", "ix_none": "还没有里程碑",
        "ix_open": "进行中", "ix_fin": "已完成", "ix_no_report": "没有报告",
        "ix_started": "{date}开始", "ix_kicker_plan": "{milestone}，属于{plan}",
        "ix_goals": "目标达成 {met}/{n}", "ix_you_1": "你做了 1 个决定",
        "ix_you_n": "你做了 {n} 个决定", "ix_risks": "{n} 件事需要留意",
        "ix_empty": "里程碑结束后，报告会出现在这里。",
        "flow": "现在怎么连起来", "flow_new": "新增", "flow_changed": "有改动", "flow_same": "原有",
        "code": "代码在哪", "code_sum": "{c} 次提交，{f} 个文件", "code_lines": "+{a} −{d} 行",
        "code_files": "{n} 个文件", "code_files_new": "{n} 个文件，{k} 个新增", "code_other": "其他",
        "code_commits": "提交", "code_note": "行数不含锁文件和自动生成的文件。",
        "code_missing": "本地仓库里找不到这个提交",
    },
}


def labels(lang):
    return LABELS.get(lang) or LABELS["en"]


ICON_PATHS = {
    "check": '<path d="M5 12l5 5L19 7"/>',
    "x": '<path d="M6 6l12 12M18 6L6 18"/>',
    "half": '<path d="M5 12h14"/>',
    "fork": '<circle cx="6" cy="5" r="2"/><circle cx="18" cy="5" r="2"/><circle cx="12" cy="19" r="2"/>'
            '<path d="M6 7v1a4 4 0 0 0 4 4h4a4 4 0 0 0 4-4V7M12 12v5"/>',
    "bulb": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-4 10.5c.6.6 1 1.4 1 2.5h6c0-1.1.4-1.9 1-2.5A6 6 0 0 0 12 3z"/>',
    "turn": '<path d="M9 14L4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-3"/>',
    "flag": '<path d="M5 21V4h11l-2 4 2 4H5"/>',
    "pause": '<path d="M9 5v14M15 5v14"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "back": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "right": '<path d="M9 6l6 6-6 6"/>',
    "chev": '<path d="M6 9l6 6 6-6"/>',
    "alert": '<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17h.01"/>',
    "book": '<path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M9 9h6M9 13h4"/>',
    "moon": '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4'
           'M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "dot": '<circle cx="12" cy="12" r="4" fill="currentColor"/>',
}

FORK_ART = (
    '<svg class="fork-art" width="56" height="64" viewBox="0 0 56 64" fill="none" '
    'stroke-linecap="round" aria-hidden="true">'
    '<circle class="fk-dot" cx="6" cy="32" r="5"/>'
    '<path class="fk-on" d="M11 32 C 28 32, 28 12, 48 12" stroke-width="3"/>'
    '<circle class="fk-dot" cx="50" cy="12" r="4"/>'
    '<path class="fk-off" d="M11 32 C 28 32, 28 52, 50 52" stroke-width="2" stroke-dasharray="2 5"/>'
    '</svg>'
)

CSS = """
:root{
  --bg:#F5F6F8;--surface:#FFFFFF;--ink:#12151C;--ink2:#3A404C;--muted:#5B6271;
  --line:#E3E6EB;--line2:#D5D9E0;--soft:#F1F2F5;--hollow:#C9CED6;
  --blue:#2A55E5;--blue-ink:#1C3FB5;--blue-soft:#EEF1FD;--sky:#CFE0FF;
  --orange:#F08A3C;--orange-ink:#B04E0C;--orange-soft:#FDF1E7;--orange-line:#F3D2B6;
  --inv-bg:#12151C;--inv-ink:#FFFFFF;
  --head:"Space Grotesk",Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --body:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  color-scheme:light;
}
html.dark{
  --bg:#0E1116;--surface:#171B22;--ink:#ECEEF2;--ink2:#C9CED6;--muted:#9AA1AD;
  --line:#262C36;--line2:#363D4A;--soft:#20252E;--hollow:#4A5260;
  --blue:#3563F0;--blue-ink:#9DB5FF;--blue-soft:#1A2340;--sky:#24365F;
  --orange:#F59A52;--orange-ink:#FFB27A;--orange-soft:#2A1D12;--orange-line:#4A3220;
  --inv-bg:#ECEEF2;--inv-ink:#12151C;
  color-scheme:dark;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 var(--body);
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
h1,h2,h3{margin:0;font-family:var(--head);font-weight:600;letter-spacing:-.015em;text-wrap:balance}
p{margin:0;text-wrap:pretty}
ul,ol{margin:0;padding:0;list-style:none}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:24px}

.top{background:var(--surface);border-bottom:1px solid var(--line)}
.top-in{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:64px}
.brand{display:flex;align-items:center;gap:10px}
.logo{width:36px;height:36px;border-radius:10px;background:var(--inv-bg);color:var(--inv-ink);
  display:grid;place-items:center;flex:none}
.brand-t{display:flex;flex-direction:column;line-height:1.2}
.brand-t b{font-family:var(--head);font-size:16px}
.brand-t small{font-size:12px;color:var(--muted)}
.theme{width:44px;height:44px;border-radius:12px;border:1px solid var(--line2);background:var(--surface);
  color:var(--ink);display:grid;place-items:center;cursor:pointer;font:inherit}
.theme .sun{display:none}
html.dark .theme .sun{display:block}
html.dark .theme .moon{display:none}
.top-r{display:flex;align-items:center;gap:8px}
.nav{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:12px;
  font-size:15px;font-weight:600;color:var(--ink2);text-decoration:none}
.nav:hover{background:var(--soft);color:var(--ink)}
.nav:focus-visible{outline:2px solid var(--blue);outline-offset:2px}

main.wrap{padding-top:56px;padding-bottom:72px;display:flex;flex-direction:column;gap:64px}
.sec{display:flex;flex-direction:column;gap:20px;min-width:0}
.sec>h2,.sec-h h2{font-size:28px;line-height:1.2}
.sec-h{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:4px 16px}
.count{font-size:14px;font-weight:600;color:var(--muted)}

/* Hero: the headline, with the result beside it */
.hero{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:48px;align-items:center}
.hero.solo{grid-template-columns:minmax(0,1fr)}
.hero-t{display:flex;flex-direction:column;gap:16px}
.kicker{font-size:15px;font-weight:600;color:var(--muted)}
h1{font-size:clamp(34px,4.6vw,56px);line-height:1.04;letter-spacing:-.028em}
.goal{font-size:19px;line-height:1.5;color:var(--ink2);max-width:36em}
.result{padding:24px;display:flex;flex-direction:column;gap:20px}
.res-h{display:flex;align-items:center;gap:14px}
.res-i{flex:none;width:48px;height:48px;border-radius:50%;display:grid;place-items:center}
.o-done .res-i{background:var(--blue);color:#FFFFFF;box-shadow:0 0 0 6px var(--blue-soft)}
.o-partial .res-i{background:var(--orange);color:#12151C;box-shadow:0 0 0 6px var(--orange-soft)}
.o-dropped .res-i{border:2px dashed var(--hollow);color:var(--muted)}
.res-t{display:flex;flex-direction:column;gap:2px;line-height:1.2}
.res-t b{font-family:var(--head);font-size:24px;font-weight:600;letter-spacing:-.015em}
.res-t span{font-size:14px;color:var(--muted)}
.checks-b{display:flex;flex-direction:column;gap:12px;border-top:1px solid var(--line);padding-top:18px}
.checks-h{display:flex;justify-content:space-between;gap:12px;font-size:14px;font-weight:600;color:var(--muted)}
.checks-h h2{font:inherit;letter-spacing:0;color:var(--ink)}
.checks{display:flex;flex-direction:column;gap:10px}
.checks li{display:flex;align-items:flex-start;gap:10px;font-size:15px;line-height:1.4}
.tick{flex:none;width:22px;height:22px;border-radius:50%;display:grid;place-items:center}
.met .tick{background:var(--blue);color:#FFFFFF}
.unmet .tick{border:2px solid var(--orange)}
.unmet{color:var(--ink2)}

/* Plan track */
.plan{padding:28px 32px}
.plan .sec-h{margin-bottom:24px}
.plan .sec-h h2{font-size:20px}
.track-scroll{overflow-x:auto;padding-bottom:4px}
.track{padding:6px 0 0 6px;display:grid;grid-template-columns:repeat(var(--n),minmax(140px,1fr))}
.step{display:flex;flex-direction:column;gap:12px}
.node{display:flex;align-items:center}
.dot{flex:none;width:36px;height:36px;border-radius:50%;display:grid;place-items:center;
  font-size:14px;font-weight:600}
.bar{flex:1 1 auto;height:3px;margin:0 10px;border-radius:3px;background:var(--line2)}
.bar.on{background:var(--blue)}
.st-done .dot{background:var(--blue);color:#FFFFFF}
.st-dropped .dot{border:2px dashed var(--hollow);background:var(--surface);color:var(--muted)}
.st-current .dot{border:3px solid var(--blue);background:var(--surface);color:var(--blue)}
.st-next .dot,.st-later .dot{border:2px solid var(--hollow);background:var(--surface);color:var(--muted)}
.this .dot{box-shadow:0 0 0 6px var(--blue-soft)}
.step-t{display:flex;flex-direction:column;align-items:flex-start;gap:2px;padding-right:12px}
.step-n{font-weight:600;line-height:1.3}
.this .step-n{color:var(--blue-ink)}
.st-dropped .step-n{color:var(--muted);text-decoration:line-through;text-decoration-color:var(--hollow)}
.st-next .step-n,.st-later .step-n{color:var(--ink2)}
.step-s{font-size:14px;color:var(--muted)}
.this-tag{margin-top:6px;font-size:12px;font-weight:700;color:var(--blue-ink);background:var(--blue-soft);
  padding:2px 9px;border-radius:999px}

/* What changed: before and now, side by side */
.cmp{padding:4px 28px 8px}
.cmp-head,.cmp-row{display:grid;grid-template-columns:minmax(110px,190px) minmax(0,.8fr) 24px minmax(0,1fr);
  gap:16px;align-items:center}
.cmp-head{padding:16px 0 10px;font-size:13px;font-weight:600;color:var(--muted)}
.cmp-head .now-h{padding-left:16px;color:var(--blue-ink)}
.cmp-row{padding:12px 0;border-top:1px solid var(--line)}
.cmp-what{font-weight:600}
.cmp-before{color:var(--muted)}
.cmp-arrow{color:var(--hollow);display:grid;place-items:center}
.cmp-now{font-weight:600;color:var(--blue-ink);background:var(--blue-soft);padding:10px 16px;border-radius:12px}
.cmp-l{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}

/* Keep in mind */
.risks{background:var(--orange-soft);border:1px solid var(--orange-line);border-radius:24px;padding:4px 28px}
.risk{display:grid;grid-template-columns:40px minmax(0,1fr) auto;gap:6px 16px;padding:20px 0;align-items:start}
.risk+.risk{border-top:1px solid var(--orange-line)}
.risk-i{grid-row:1/span 2;width:40px;height:40px;border-radius:50%;background:var(--surface);
  color:var(--orange-ink);display:grid;place-items:center}
.risk-t{font-size:18px;font-weight:600;line-height:1.35;padding-top:7px}
.when{justify-self:end;margin-top:6px;font-size:13px;font-weight:600;color:var(--orange-ink);background:var(--surface);
  border:1px solid var(--orange-line);padding:3px 10px;border-radius:999px;white-space:nowrap}
.todo{grid-column:2/-1;font-size:15px;color:var(--ink2)}
.todo b{font-weight:600;color:var(--ink)}

/* Choices made */
.decs{display:grid;grid-template-columns:repeat(var(--cols),minmax(0,1fr));gap:20px}
.decs.one{grid-template-columns:minmax(0,560px)}
.dec{display:flex;flex-direction:column;gap:18px;padding:22px 24px 24px}
.dec.by-you{border-color:var(--orange-line)}
.dec-meta{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:13px;color:var(--muted)}
.who{font-size:12px;font-weight:700;padding:3px 10px;border-radius:999px;background:var(--soft);color:var(--ink2)}
.by-you .who{background:var(--orange-soft);color:var(--orange-ink)}
.fork{display:flex;gap:12px;align-items:stretch}
.fork-art{flex:none}
.fk-dot{fill:var(--blue)}
.fk-on{stroke:var(--blue)}
.fk-off{stroke:var(--hollow)}
.by-you .fk-dot{fill:var(--orange)}
.by-you .fk-on{stroke:var(--orange)}
.fork-t{display:flex;flex-direction:column;justify-content:space-between;gap:10px;min-width:0}
.fork-t h3{font-family:var(--body);font-size:18px;line-height:1.3;letter-spacing:-.01em}
.over{font-size:15px;color:var(--muted);text-decoration:line-through;text-decoration-color:var(--hollow)}
.why{font-size:15px;color:var(--ink2)}
.why b{font-weight:600;color:var(--ink)}
.dec .why{margin-top:auto;border-top:1px solid var(--line);padding-top:16px}

/* How it went, with what was dropped beside it */
.story-grid{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:56px;align-items:start}
.story-grid.solo{grid-template-columns:minmax(0,760px)}
.ev{display:grid;grid-template-columns:104px 36px minmax(0,1fr);column-gap:18px}
.ev-meta{display:flex;flex-direction:column;align-items:flex-end;gap:2px;padding-top:7px;text-align:right}
.ev-meta b,.ev-d b{font-size:14px;font-weight:600}
.ev-kind{font-size:13px;font-weight:600;color:var(--muted)}
.rail{display:flex;flex-direction:column;align-items:center}
.rail::after{content:"";flex:1 1 auto;width:2px;margin:6px 0;border-radius:2px;background:var(--line2)}
.ev:last-child .rail::after{background:transparent}
.ev-dot{flex:none;width:36px;height:36px;border-radius:50%;display:grid;place-items:center}
.ev-body{min-width:0;padding:5px 0 36px}
.ev:last-child .ev-body{padding-bottom:0}
.ev-d{display:none;align-items:baseline;gap:8px;margin-bottom:4px}
.ev-body h3{font-family:var(--body);font-size:19px;line-height:1.35;letter-spacing:-.01em}
.ev-sum{margin-top:4px;font-size:16px;color:var(--muted)}
.k-started .ev-dot{border:2px solid var(--hollow);background:var(--surface);color:var(--ink2)}
.k-decision .ev-dot{background:var(--blue);color:#FFFFFF}
.k-decision .ev-kind{color:var(--blue-ink)}
.k-found .ev-dot{background:var(--sky);color:var(--blue-ink)}
.k-found .ev-kind{color:var(--blue-ink)}
.k-changed-course .ev-dot{background:var(--inv-bg);color:var(--inv-ink)}
.k-changed-course .ev-kind{color:var(--ink)}
.k-paused .ev-dot{background:var(--orange);color:#12151C}
.k-paused .ev-kind{color:var(--orange-ink)}
.k-finished .ev-dot{background:var(--blue);color:#FFFFFF;box-shadow:0 0 0 6px var(--blue-soft)}
.k-finished .ev-kind{color:var(--blue-ink)}
details{margin-top:6px}
summary{display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:0 4px;margin-left:-4px;border-radius:10px;
  font-size:15px;font-weight:600;color:var(--blue-ink);cursor:pointer;list-style:none}
summary::-webkit-details-marker{display:none}
summary:hover .lbl{text-decoration:underline;text-underline-offset:3px}
summary:focus-visible,.theme:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
summary .chev{transition:transform .15s}
details[open] summary .chev{transform:rotate(180deg)}
details[open] .show,details:not([open]) .hide{display:none}
.ex{margin-top:4px;background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--blue);
  border-radius:4px 14px 14px 4px;padding:14px 18px;font-size:16px;line-height:1.55}
details .why{margin-top:12px}

.side{padding-top:7px}
.side h2{font-size:20px}
.drops{display:flex;flex-direction:column;gap:12px}
.drop{border:1.5px dashed var(--hollow);border-radius:20px;padding:18px 20px;display:flex;flex-direction:column;gap:8px}
.drop-h{display:flex;align-items:center;gap:10px}
.drop-x{flex:none;width:28px;height:28px;border-radius:50%;border:2px dashed var(--hollow);color:var(--muted);
  display:grid;place-items:center}
.drop h3{font-family:var(--body);font-size:17px;line-height:1.3;letter-spacing:-.01em}
.instead{font-size:15px}
.instead b{font-weight:600}
.drop .why{color:var(--muted)}
.drop-when{font-size:13px;color:var(--muted)}

/* Facts */
.facts{display:grid;grid-template-columns:repeat(var(--cols),minmax(0,1fr))}
.fact{padding:24px 28px;display:flex;flex-direction:column;gap:14px;min-width:0}
.fact+.fact{border-left:1px solid var(--line)}
.fact h2{font-family:var(--body);font-size:15px;font-weight:700;letter-spacing:0}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{display:inline-flex;align-items:center;gap:6px;font-size:14px;padding:6px 12px;border-radius:999px;background:var(--soft)}
.chip svg{color:var(--blue)}
.next{display:flex;flex-direction:column;gap:8px;font-size:15px}
.next li{display:flex;gap:10px}
.next svg{flex:none;margin-top:3px;color:var(--blue)}

.foot{font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:20px;margin-top:-24px}

html[lang^="zh"]{
  --head:"Space Grotesk",Inter,ui-sans-serif,system-ui,-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC",sans-serif;
  --body:Inter,ui-sans-serif,system-ui,-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC",sans-serif}
html[lang^="zh"] body{line-height:1.7}
html[lang^="zh"] h1,html[lang^="zh"] h2,html[lang^="zh"] h3,html[lang^="zh"] .res-t b{letter-spacing:0}
html[lang^="zh"] h1{line-height:1.2}

/* How it fits together */
.flow{padding:28px 28px 20px}
.flow-scroll{overflow-x:auto}
.flow-svg{display:block;margin:0 auto;max-width:100%;height:auto}
.flow-v{display:none}
.fl-node rect{stroke-width:1.5}
.fl-new rect{fill:var(--blue-soft);stroke:var(--blue)}
.fl-changed rect{fill:var(--surface);stroke:var(--blue)}
.fl-same rect{fill:none;stroke:var(--hollow);stroke-dasharray:5 4}
.fl-label{font:600 15px var(--body);fill:var(--ink)}
.fl-new .fl-label{fill:var(--blue-ink)}
.fl-same .fl-label{fill:var(--ink2)}
.fl-note{font:12.5px var(--body);fill:var(--muted)}
.fl-edge{fill:none;stroke:var(--muted);stroke-opacity:.45;stroke-width:2}
.fl-head{fill:var(--muted);fill-opacity:.6}
.fl-lbg{fill:var(--surface)}
.fl-elabel{font:600 12px var(--body);fill:var(--muted)}
.legend{display:flex;flex-wrap:wrap;justify-content:center;gap:8px 20px;margin-top:16px;font-size:13px;color:var(--muted)}
.lg{display:inline-flex;align-items:center;gap:8px}
.sw{width:18px;height:12px;border-radius:4px;border:1.5px solid var(--hollow)}
.lg-new .sw{background:var(--blue-soft);border-color:var(--blue)}
.lg-changed .sw{border-color:var(--blue)}
.lg-same .sw{border-style:dashed}

/* Where the code is */
.code{padding:4px 28px}
.areas .area{display:grid;grid-template-columns:minmax(0,1fr) 140px 116px 136px;gap:8px 20px;align-items:center;
  padding:16px 0;border-top:1px solid var(--line)}
.areas .area:first-child{border-top:0}
.area-t{min-width:0}
.area-w{font-weight:600}
.paths{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.path,.hash{font:12.5px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;padding:0 8px;border-radius:6px;
  text-decoration:none;overflow-wrap:anywhere}
.path{background:var(--soft);color:var(--ink2)}
a.path:hover{background:var(--blue-soft);color:var(--blue-ink)}
a.path:focus-visible,a.hash:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
.bar2{display:flex;height:8px;border-radius:4px;background:var(--soft);overflow:hidden}
.bar2 .a{background:var(--blue)}
.bar2 .d{background:var(--hollow)}
.lines{font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;text-align:right;white-space:nowrap}
.lines .add{color:var(--blue-ink)}
.lines .del{color:var(--muted)}
.files{font-size:14px;color:var(--muted);text-align:right;white-space:nowrap}
.commits{border-top:1px solid var(--line);padding:16px 0}
.commits h3{font-family:var(--body);font-size:14px;font-weight:600;color:var(--muted);letter-spacing:0;margin-bottom:10px}
.commits ul{display:flex;flex-direction:column;gap:8px}
.cm{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:12px;align-items:baseline;font-size:14px}
.hash{background:var(--blue-soft);color:var(--blue-ink)}
a.hash:hover{text-decoration:underline}
.cm-s{color:var(--ink2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cm-d{font-size:13px;color:var(--muted);white-space:nowrap}
.code-note{font-size:13px;color:var(--muted);padding-bottom:16px}

@media (max-width:960px){
  .hero{grid-template-columns:minmax(0,1fr);gap:28px}
  .result{max-width:520px}
  .story-grid{grid-template-columns:minmax(0,1fr);gap:48px}
  .side{padding-top:0}
  .decs{grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
}
@media (max-width:720px){
  main.wrap{padding-top:32px;gap:48px}
  .sec>h2,.sec-h h2{font-size:24px}
  .plan{padding:22px 20px}
  .plan .sec-h{margin-bottom:16px}
  .track{grid-template-columns:minmax(0,1fr);padding:0}
  .step{flex-direction:row;gap:14px}
  .node{flex-direction:column;align-self:stretch}
  .bar{width:3px;height:auto;min-height:14px;margin:6px 0}
  .step-t{padding:6px 0 18px}
  .step:last-child .step-t{padding-bottom:0}
  .cmp{padding:4px 20px}
  .cmp-head{display:none}
  .cmp-row{grid-template-columns:minmax(0,1fr);gap:6px;padding:16px 0}
  .cmp-row:first-child{border-top:0}
  .cmp-arrow{display:none}
  .cmp-before{display:flex;gap:8px}
  .cmp-now{display:flex;gap:8px;padding:8px 12px}
  .cmp-l{position:static;width:auto;height:auto;overflow:visible;clip:auto;
    flex:none;width:48px;font-size:13px;font-weight:600;line-height:1.7}
  .risks{padding:4px 20px}
  .risk{grid-template-columns:36px minmax(0,1fr)}
  .risk-i{grid-row:1/span 3;width:36px;height:36px}
  .risk-t{padding-top:5px}
  .when{grid-column:2;justify-self:start;margin-top:0}
  .todo{grid-column:2}
  .dec{padding:20px}
  .ev{grid-template-columns:36px minmax(0,1fr);column-gap:14px}
  .ev-meta{display:none}
  .ev-d{display:flex}
  .ev-body{padding-top:0}
  .facts{grid-template-columns:minmax(0,1fr)}
  .flow{padding:20px 12px 16px}
  .flow-h{display:none}
  .flow-v{display:block}
  .code{padding:4px 20px}
  .areas .area{grid-template-columns:minmax(0,1fr) auto}
  .area-t,.bar2{grid-column:1/-1}
  .lines{text-align:left}
  .cm{grid-template-columns:auto minmax(0,1fr)}
  .cm-d{display:none}
  .fact{padding:20px}
  .fact+.fact{border-left:0;border-top:1px solid var(--line)}
}
@media (prefers-reduced-motion:reduce){summary .chev{transition:none}}
@media print{
  .theme{display:none}
  body{background:#FFFFFF}
  .panel,.dec,.ev,.drop,.risk{break-inside:avoid}
}
"""

INDEX_CSS = """
.ix-hero{display:flex;flex-direction:column;gap:12px}
.ix-sum{font-size:19px;color:var(--ink2)}
.rows{display:flex;flex-direction:column;gap:12px}
.row{display:grid;grid-template-columns:132px minmax(0,1fr) auto;gap:6px 24px;align-items:center;
  padding:22px 24px;color:inherit;text-decoration:none}
a.row:hover{border-color:var(--hollow)}
a.row:hover .row-go{color:var(--blue-ink);transform:translateX(2px)}
a.row:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
.row-date{font-size:14px;font-weight:600;color:var(--muted)}
.row-main{display:flex;flex-direction:column;gap:4px;min-width:0}
.row-k{font-size:14px;font-weight:600;color:var(--muted)}
.row-h{font-size:21px;line-height:1.3}
.row-meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.tag{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:600;padding:3px 10px;
  border-radius:999px;background:var(--soft);color:var(--ink2)}
.tag svg{color:var(--blue)}
.tag.warn{background:var(--orange-soft);color:var(--orange-ink)}
.tag.warn svg,.tag.you svg{color:currentColor}
.tag.you{background:var(--orange-soft);color:var(--orange-ink)}
.row-end{display:flex;align-items:center;gap:14px}
.row-go{color:var(--muted);display:grid;place-items:center;transition:transform .15s}
.pill{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:600;padding:3px 11px;
  border-radius:999px;white-space:nowrap}
.pill-done{background:var(--blue-soft);color:var(--blue-ink)}
.pill-partial{background:var(--orange-soft);color:var(--orange-ink)}
.pill-dropped,.pill-none{background:var(--soft);color:var(--ink2)}
.pill-open{border:1.5px solid var(--blue);color:var(--blue-ink)}
.pill-open::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--blue)}
.row.slim{padding:16px 24px;border-style:dashed;border-color:var(--line2);background:transparent}
.row.slim .row-h{font-size:18px}
.empty{padding:28px;color:var(--ink2)}
@media (max-width:720px){
  .row{grid-template-columns:minmax(0,1fr) auto;align-items:start;padding:18px 20px}
  .row-date{grid-column:1;grid-row:1}
  .row-main{grid-column:1/-1;grid-row:2}
  .row-end{grid-column:2;grid-row:1}
  .row-go{display:none}
  .row.slim{padding:14px 20px}
}
@media (prefers-reduced-motion:reduce){.row-go{transition:none}}
"""

THEME_BOOT = """<script>
(function () {
  var saved = null;
  try { saved = localStorage.getItem("ij-theme"); } catch (e) {}
  var dark = saved ? saved === "dark"
    : !!(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
  if (dark) document.documentElement.classList.add("dark");
})();
</script>"""

TOGGLE_JS = ("var d=document.documentElement.classList.toggle('dark');"
             "try{localStorage.setItem('ij-theme',d?'dark':'light')}catch(e){}")

PRINT_JS = """<script>
window.addEventListener("beforeprint", function () {
  document.querySelectorAll("details").forEach(function (d) { d.open = true; });
});
</script>"""

PAGE = """<!doctype html>
<html lang="%%LANG%%">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%%TITLE%%</title>
%%BOOT%%
<style>%%CSS%%</style>
</head>
<body>
<header class="top">
  <div class="wrap top-in">
    <div class="brand">
      <span class="logo">%%LOGO%%</span>
      <span class="brand-t"><b>%%BRAND%%</b><small>%%PROJECT%%</small></span>
    </div>
    <div class="top-r">%%NAV%%<button class="theme" type="button" aria-label="%%THEME%%" onclick="%%TOGGLE%%">%%MOON%%%%SUN%%</button></div>
  </div>
</header>
<main class="wrap">
%%BODY%%
</main>
%%PRINT%%
</body>
</html>
"""


def esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def icon(name, size=18, width=2, cls=""):
    cls_attr = f' class="{cls}"' if cls else ""
    return (f'<svg{cls_attr} width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{ICON_PATHS[name]}</svg>')


def fmt_date(value, t, year=False):
    try:
        y, m, d = (int(part) for part in str(value).split("-"))
        month = MONTHS[m - 1]
    except (ValueError, IndexError):
        return esc(value)
    if t["html"].startswith("zh"):
        return f"{y}年{m}月{d}日" if year else f"{m}月{d}日"
    return f"{month} {d}, {y}" if year else f"{month} {d}"


def dicts(value):
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def texts(value):
    return [item for item in value if isinstance(item, str) and item.strip()] if isinstance(value, list) else []


def grid_cols(n):
    """Columns for a row of cards: never leave a lone card beside empty slots."""
    return {1: 1, 2: 2, 4: 2}.get(n, 3)


def result_panel(data, t):
    outcome = data.get("outcome")
    rows = dicts(data.get("doneWhen"))
    if outcome not in t["outcome"] and not rows:
        return ""
    parts = []
    if outcome in t["outcome"]:
        sub = ""
        if data.get("finished"):
            key = "closed_on" if outcome == "dropped" else "finished_on"
            sub = f'<span>{t[key].format(date=fmt_date(data["finished"], t, year=True))}</span>'
        parts.append(
            f'<div class="res-h"><span class="res-i">{icon(OUTCOME_ICONS[outcome], 24, 3)}</span>'
            f'<span class="res-t"><b>{t["outcome"][outcome]}</b>{sub}</span></div>')
    if rows:
        items = []
        met_count = 0
        for row in rows:
            met = row.get("met") is True
            met_count += met
            tick = icon("check", 12, 3.5) if met else ""
            hidden = "" if met else f'<span class="vh">{t["not_met"]}</span>'
            cls = "met" if met else "unmet"
            items.append(f'<li class="{cls}"><span class="tick">{tick}</span>'
                         f'<span>{hidden}{esc(row.get("text", ""))}</span></li>')
        parts.append(
            f'<div class="checks-b"><div class="checks-h"><h2 id="done-h">{t["done_when"]}</h2>'
            f'<span>{t["met"].format(met=met_count, n=len(rows))}</span></div>'
            '<ul class="checks" aria-labelledby="done-h">' + "".join(items) + "</ul></div>")
    cls = f"panel result o-{outcome}" if outcome in t["outcome"] else "panel result"
    return f'<aside class="{cls}" aria-label="{t["result"]}">' + "".join(parts) + "</aside>"


def hero(data, t):
    goal = f'<p class="goal">{esc(data["goal"])}</p>' if data.get("goal") else ""
    kicker = f'<p class="kicker">{esc(data["milestone"])}</p>' if data.get("milestone") else ""
    panel = result_panel(data, t)
    cls = "hero" if panel else "hero solo"
    return (f'<section class="{cls}"><div class="hero-t">{kicker}'
            f'<h1>{esc(data.get("headline", ""))}</h1>{goal}</div>{panel}</section>')


def section_plan(plan, t):
    steps = dicts(plan.get("steps")) if isinstance(plan, dict) else []
    if not steps:
        return ""
    items = []
    position = ""
    for i, step in enumerate(steps):
        state = step.get("state") if step.get("state") in t["step"] else "later"
        marks = {"done": icon("check", 18, 3), "dropped": icon("x", 16, 2.5), "current": icon("dot", 18)}
        mark = marks.get(state, str(i + 1))
        sub = t["step"][state]
        if step.get("date") and state in ("done", "dropped"):
            sub += " " + fmt_date(step["date"], t)
        note = f'<span class="step-s">{esc(step["note"])}</span>' if step.get("note") else ""
        this = step.get("thisMilestone") is True
        if this:
            position = f'<span class="count">{t["step_of"].format(i=i + 1, n=len(steps))}</span>'
        tag = f'<span class="this-tag">{t["this"]}</span>' if this else ""
        bar = ""
        if i < len(steps) - 1:
            on = state in ("done", "dropped") and steps[i + 1].get("state") in ("done", "dropped", "current")
            bar_cls = "bar on" if on else "bar"
            bar = f'<span class="{bar_cls}" aria-hidden="true"></span>'
        li_cls = f"step st-{state}" + (" this" if this else "")
        current = ' aria-current="step"' if this else ""
        items.append(
            f'<li class="{li_cls}"{current}><div class="node"><span class="dot">{mark}</span>{bar}</div>'
            f'<div class="step-t"><span class="step-n">{esc(step.get("name", ""))}</span>'
            f'<span class="step-s">{sub}</span>{note}{tag}</div></li>')
    name = esc(plan.get("name") or t["plan"])
    return (f'<section class="panel plan" aria-labelledby="plan-h">'
            f'<div class="sec-h"><h2 id="plan-h">{name}</h2>{position}</div>'
            f'<div class="track-scroll"><ol class="track" style="--n:{len(steps)}">'
            + "".join(items) + "</ol></div></section>")


def section_changes(changes, t):
    rows = dicts(changes)
    if not rows:
        return ""
    items = []
    for row in rows:
        items.append(
            f'<li class="cmp-row"><span class="cmp-what">{esc(row.get("what", ""))}</span>'
            f'<span class="cmp-before"><span class="cmp-l">{t["before"]}</span><span>{esc(row.get("before", ""))}</span></span>'
            f'<span class="cmp-arrow">{icon("arrow", 18, 2)}</span>'
            f'<span class="cmp-now"><span class="cmp-l">{t["now"]}</span><span>{esc(row.get("after", ""))}</span></span></li>')
    head = (f'<div class="cmp-head" aria-hidden="true"><span></span><span>{t["before"]}</span><span></span>'
            f'<span class="now-h">{t["now"]}</span></div>')
    return (f'<section class="sec" aria-labelledby="chg-h"><h2 id="chg-h">{t["changed"]}</h2>'
            f'<div class="panel cmp">{head}<ul>' + "".join(items) + "</ul></div></section>")


def section_risks(risks, t):
    rows = dicts(risks)
    if not rows:
        return ""
    items = []
    for row in rows:
        when = f'<span class="when">{esc(row["when"])}</span>' if row.get("when") else ""
        items.append(
            f'<li class="risk"><span class="risk-i">{icon("alert", 18)}</span>'
            f'<p class="risk-t">{esc(row.get("risk", ""))}</p>{when}'
            f'<p class="todo"><b>{t["todo"]}</b>{t["sp"]}{esc(row.get("action", ""))}</p></li>')
    return (f'<section class="sec" aria-labelledby="risk-h"><h2 id="risk-h">{t["keep"]}</h2>'
            '<ul class="risks">' + "".join(items) + "</ul></section>")


def section_decisions(decisions, t):
    rows = dicts(decisions)
    if not rows:
        return ""
    cards = []
    for row in rows:
        by_you = row.get("by") == "you"
        cls = "panel dec by-you" if by_you else "panel dec"
        who = t["by_you"] if by_you else t["by_claude"]
        when = f'<span>{fmt_date(row["date"], t)}</span>' if row.get("date") else ""
        cards.append(
            f'<article class="{cls}"><div class="dec-meta"><span class="who">{who}</span>{when}</div>'
            f'<div class="fork">{FORK_ART}<div class="fork-t">'
            f'<h3>{esc(row.get("picked", ""))}</h3>'
            f'<s class="over"><span class="vh">{t["instead_of"]}</span>{esc(row.get("over", ""))}</s></div></div>'
            f'<p class="why"><b>{t["why"]}</b>{t["sp"]}{esc(row.get("why", ""))}</p></article>')
    n = len(cards)
    cls = "decs one" if n == 1 else "decs"
    return (f'<section class="sec" aria-labelledby="dec-h"><h2 id="dec-h">{t["choices"]}</h2>'
            f'<div class="{cls}" style="--cols:{grid_cols(n)}">' + "".join(cards) + "</div></section>")


def section_story(story, t):
    rows = dicts(story)
    if not rows:
        return ""
    items = []
    for row in rows:
        kind = row.get("kind") if row.get("kind") in t["kind"] else "started"
        when = fmt_date(row["date"], t) if row.get("date") else ""
        meta = f'<b>{when}</b><span class="ev-kind">{t["kind"][kind]}</span>'
        details = ""
        if row.get("example") or row.get("why"):
            example = f'<p class="ex">{esc(row["example"])}</p>' if row.get("example") else ""
            why = f'<p class="why"><b>{t["matters"]}</b>{t["sp"]}{esc(row["why"])}</p>' if row.get("why") else ""
            show, hide = (t["show_ex"], t["hide_ex"]) if row.get("example") else (t["show_why"], t["hide_why"])
            details = (f'<details><summary><span class="lbl"><span class="show">{show}</span>'
                       f'<span class="hide">{hide}</span></span>{icon("chev", 16, 2.5, "chev")}</summary>'
                       f'{example}{why}</details>')
        summary = f'<p class="ev-sum">{esc(row["summary"])}</p>' if row.get("summary") else ""
        items.append(
            f'<li class="ev k-{kind}"><div class="ev-meta">{meta}</div>'
            f'<div class="rail"><span class="ev-dot">{icon(KIND_ICONS[kind], 18)}</span></div>'
            f'<div class="ev-body"><div class="ev-d">{meta}</div>'
            f'<h3>{esc(row.get("title", ""))}</h3>{summary}{details}</div></li>')
    return (f'<section class="sec" aria-labelledby="story-h"><h2 id="story-h">{t["story"]}</h2>'
            '<ol class="timeline">' + "".join(items) + "</ol></section>")


def section_dropped(dropped, t):
    rows = dicts(dropped)
    if not rows:
        return ""
    cards = []
    for row in rows:
        instead = f'<p class="instead"><b>{t["instead"]}</b>{t["sp"]}{esc(row["instead"])}</p>' if row.get("instead") else ""
        when = ""
        if row.get("date"):
            when = f'<p class="drop-when">{t["dropped_on"].format(date=fmt_date(row["date"], t))}</p>'
        cards.append(
            f'<li class="drop"><div class="drop-h"><span class="drop-x">{icon("x", 14, 2.5)}</span>'
            f'<h3>{esc(row.get("what", ""))}</h3></div>{instead}'
            f'<p class="why">{esc(row.get("why", ""))}</p>{when}</li>')
    return (f'<section class="sec side" aria-labelledby="drop-h"><h2 id="drop-h">{t["dropped"]}</h2>'
            '<ul class="drops">' + "".join(cards) + "</ul></section>")


def story_row(data, t):
    story = section_story(data.get("story"), t)
    dropped = section_dropped(data.get("dropped"), t)
    if not story:
        return dropped
    if not dropped:
        return f'<div class="story-grid solo">{story}</div>'
    return f'<div class="story-grid">{story}{dropped}</div>'


def section_facts(data, t):
    blocks = []
    code = data.get("code") if isinstance(data.get("code"), dict) else {}
    touched = [] if dicts(code.get("areas")) else texts(data.get("touched"))
    if touched:
        chips = "".join(f'<li class="chip">{esc(item)}</li>' for item in touched)
        blocks.append(f'<div class="fact"><h2>{t["touched"]}</h2><ul class="chips">{chips}</ul></div>')
    docs = texts(data.get("docsUpdated"))
    if docs:
        chips = "".join(f'<li class="chip">{icon("check", 14, 3)}{esc(item)}</li>' for item in docs)
        blocks.append(f'<div class="fact"><h2>{t["docs"]}</h2><ul class="chips">{chips}</ul></div>')
    follow = texts(data.get("followUps"))
    if follow:
        items = "".join(f"<li>{icon('arrow', 16, 2.5)}<span>{esc(item)}</span></li>" for item in follow)
        blocks.append(f'<div class="fact"><h2>{t["next"]}</h2><ul class="next">{items}</ul></div>')
    if not blocks:
        return ""
    return (f'<section class="panel facts" aria-label="{t["details"]}" style="--cols:{len(blocks)}">'
            + "".join(blocks) + "</section>")


# Flow diagram -----------------------------------------------------------------

FLOW_STATES = ("new", "changed", "same")
FLOW_LABEL_PX, FLOW_NOTE_PX, FLOW_EDGE_PX = 15, 12.5, 12
FLOW_PAD_X, FLOW_ROW_GAP = 16, 18


def text_px(text, size, bold=False):
    """Rough rendered width; SVG text does not wrap, so boxes are sized from this."""
    width = 0.0
    for ch in str(text):
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            width += size
        elif ch == " ":
            width += size * 0.3
        elif ch.isupper() or ch.isdigit():
            width += size * 0.64
        else:
            width += size * 0.54
    return width * (1.06 if bold else 1.0)


def flow_parts(flow):
    nodes = [n for n in dicts(flow.get("nodes")) if isinstance(n.get("id"), str) and n.get("label")]
    ids = {n["id"] for n in nodes}
    edges = [e for e in dicts(flow.get("edges")) if e.get("from") in ids and e.get("to") in ids
             and e.get("from") != e.get("to")]
    return nodes, edges


def flow_layers(nodes, edges):
    """Longest-path layers; bounded so a cycle cannot loop forever."""
    layer = {n["id"]: 0 for n in nodes}
    for _ in range(len(nodes)):
        moved = False
        for e in edges:
            want = layer[e["from"]] + 1
            if layer[e["to"]] < want < len(nodes):
                layer[e["to"]] = want
                moved = True
        if not moved:
            break
    columns = []
    for n in nodes:
        while len(columns) <= layer[n["id"]]:
            columns.append([])
        columns[layer[n["id"]]].append(n)
    return [c for c in columns if c]


def flow_svg(flow, t, vertical):
    nodes, edges = flow_parts(flow)
    columns = flow_layers(nodes, edges)
    has_note = any(n.get("note") for n in nodes)
    h = 62 if has_note else 44
    size = {}
    for n in nodes:
        w = max(text_px(n["label"], FLOW_LABEL_PX, bold=True), text_px(n.get("note", ""), FLOW_NOTE_PX))
        size[n["id"]] = max(112, round(w + 2 * FLOW_PAD_X))
    label_w = max([text_px(e.get("label", ""), FLOW_EDGE_PX) for e in edges] + [0])
    pos = {}
    if not vertical:
        gap = max(56, round(label_w + 56))
        col_w = [max(size[n["id"]] for n in col) for col in columns]
        col_h = [len(col) * h + (len(col) - 1) * FLOW_ROW_GAP for col in columns]
        height = max(col_h)
        x = 0
        for ci, col in enumerate(columns):
            y = (height - col_h[ci]) / 2
            for n in col:
                pos[n["id"]] = (x + (col_w[ci] - size[n["id"]]) / 2, y)
                y += h + FLOW_ROW_GAP
            x += col_w[ci] + gap
        width = x - gap
    else:
        gap = 60
        row_w = [sum(size[n["id"]] for n in row) + (len(row) - 1) * 14 for row in columns]
        width = max(row_w + [0])
        y = 0
        for ri, row in enumerate(columns):
            x = (width - row_w[ri]) / 2
            for n in row:
                pos[n["id"]] = (x, y)
                x += size[n["id"]] + 14
            y += h + gap
        height = y - gap

    pad = 8
    marker = "fl-arrow-v" if vertical else "fl-arrow-h"
    parts = [f'<svg class="flow-svg {"flow-v" if vertical else "flow-h"}" viewBox="{-pad} {-pad} '
             f'{width + 2 * pad:.0f} {height + 2 * pad:.0f}" width="{width + 2 * pad:.0f}" '
             f'role="img" aria-labelledby="flow-h">'
             f'<defs><marker id="{marker}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" '
             f'markerHeight="5" orient="auto-start-reverse"><path class="fl-head" d="M0 0L10 5L0 10z"/></marker></defs>']
    for e in edges:
        (x1, y1), (x2, y2) = pos[e["from"]], pos[e["to"]]
        w1, w2 = size[e["from"]], size[e["to"]]
        if not vertical:
            sx, sy, ex, ey = x1 + w1, y1 + h / 2, x2 - 2, y2 + h / 2
            mid = (sx + ex) / 2
            d = f"M{sx:.1f} {sy:.1f} C{mid:.1f} {sy:.1f} {mid:.1f} {ey:.1f} {ex:.1f} {ey:.1f}"
        else:
            sx, sy, ex, ey = x1 + w1 / 2, y1 + h, x2 + w2 / 2, y2 - 2
            mid = (sy + ey) / 2
            d = f"M{sx:.1f} {sy:.1f} C{sx:.1f} {mid:.1f} {ex:.1f} {mid:.1f} {ex:.1f} {ey:.1f}"
        parts.append(f'<path class="fl-edge" d="{d}" marker-end="url(#{marker})"/>')
        if e.get("label"):
            lw = text_px(e["label"], FLOW_EDGE_PX) + 12
            cx, cy = (sx + ex) / 2, (sy + ey) / 2
            if vertical and abs(ex - sx) > 2:
                # Beside the straight end of a bent edge, on its outer side.
                side = -1 if ex < sx else 1
                cx, cy = ex + side * (lw / 2 + 10), ey - 16
            elif vertical:
                cx += lw / 2 + 8
            elif abs(ey - sy) > 2:
                # Above (or below) the flat end of a bent edge, clear of the bend.
                cx = ex - lw / 2 - 14
                cy = ey - 14 if ey < sy else ey + 14
            parts.append(f'<rect class="fl-lbg" x="{cx - lw / 2:.1f}" y="{cy - 10:.1f}" width="{lw:.1f}" height="20" rx="10"/>'
                         f'<text class="fl-elabel" x="{cx:.1f}" y="{cy + 4:.1f}" text-anchor="middle">{esc(e["label"])}</text>')
    for n in nodes:
        x, y = pos[n["id"]]
        state = n.get("state") if n.get("state") in FLOW_STATES else "same"
        w = size[n["id"]]
        label_y = y + (24 if n.get("note") else h / 2 + 5)
        parts.append(f'<g class="fl-node fl-{state}"><rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="12"/>'
                     f'<text class="fl-label" x="{x + w / 2:.1f}" y="{label_y:.1f}" text-anchor="middle">{esc(n["label"])}</text>')
        if n.get("note"):
            parts.append(f'<text class="fl-note" x="{x + w / 2:.1f}" y="{y + 45:.1f}" text-anchor="middle">{esc(n["note"])}</text>')
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


def section_flow(flow, t):
    if not isinstance(flow, dict):
        return ""
    nodes, _ = flow_parts(flow)
    if len(nodes) < 2:
        return ""
    used = {n.get("state") if n.get("state") in FLOW_STATES else "same" for n in nodes}
    legend = "".join(f'<li class="lg lg-{s}"><span class="sw"></span>{t["flow_" + s]}</li>'
                     for s in FLOW_STATES if s in used)
    desc = "；".join(f'{n["label"]}（{t["flow_" + (n.get("state") if n.get("state") in FLOW_STATES else "same")]}）'
                    for n in nodes) if t["html"].startswith("zh") else "; ".join(
        f'{n["label"]} ({t["flow_" + (n.get("state") if n.get("state") in FLOW_STATES else "same")].lower()})'
        for n in nodes)
    return (f'<section class="sec" aria-labelledby="flow-h"><h2 id="flow-h">{t["flow"]}</h2>'
            f'<div class="panel flow"><div class="flow-scroll">{flow_svg(flow, t, False)}{flow_svg(flow, t, True)}</div>'
            f'<p class="vh">{esc(desc)}</p><ul class="legend">{legend}</ul></div></section>')


# Where the code is --------------------------------------------------------------

GENERATED_RE = re.compile(r"(^|/)(pnpm-lock\.yaml|package-lock\.json|yarn\.lock|bun\.lockb?|Cargo\.lock"
                          r"|poetry\.lock|uv\.lock|Gemfile\.lock|composer\.lock|go\.sum)$"
                          r"|\.gen\.|_snapshot\.json$|\.min\.(js|css)$")


def git(repo, *args):
    try:
        out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                             timeout=20, encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


def repo_root(start):
    out = git(start, "rev-parse", "--show-toplevel")
    return Path(out.strip()) if out and out.strip() else None


def github_base(repo):
    url = (git(repo, "remote", "get-url", "origin") or "").strip()
    match = re.match(r"(?:https://github\.com/|git@github\.com:)([^/]+/[^/]+?)(?:\.git)?/?$", url)
    return f"https://github.com/{match.group(1)}" if match else None


def is_journal_file(path):
    parts = path.split("/")
    if any(DOSSIER_RE.match(p) for p in parts[:-1]):
        return True
    return len(parts) >= 2 and parts[-2] == "tasks" and parts[-1] in ("NEXT-SESSION.md", "INDEX.md", INDEX_NAME)


def code_stats(repo, commits):
    """Per-commit info and per-file totals across the listed commits."""
    info, files = [], {}
    for ref in commits:
        meta = git(repo, "show", "-s", "--format=%H%x00%h%x00%ad%x00%s", "--date=short", ref)
        if not meta or meta.count("\x00") < 3:
            info.append({"ref": ref, "missing": True})
            continue
        full, short, date, subject = meta.strip("\n").split("\x00", 3)
        info.append({"ref": ref, "full": full, "short": short, "date": date, "subject": subject})
        for line in (git(repo, "show", "--no-renames", "--name-status", "--format=", full) or "").splitlines():
            bits = line.split("\t")
            if len(bits) < 2 or is_journal_file(bits[-1]):
                continue
            entry = files.setdefault(bits[-1], {"add": 0, "del": 0, "new": False})
            if bits[0].startswith("A"):
                entry["new"] = True
        for line in (git(repo, "show", "--no-renames", "--numstat", "--format=", full) or "").splitlines():
            bits = line.split("\t", 2)
            if len(bits) < 3 or bits[0] == "-" or bits[2] not in files or GENERATED_RE.search(bits[2]):
                continue
            files[bits[2]]["add"] += int(bits[0])
            files[bits[2]]["del"] += int(bits[1])
    return info, files


def area_of(path, areas):
    best, best_len = None, -1
    for i, area in enumerate(areas):
        for p in texts(area.get("paths")):
            p = p.strip("/")
            if (path == p or path.startswith(p + "/")) and len(p) > best_len:
                best, best_len = i, len(p)
    return best


def section_code(code, t, repo):
    if not isinstance(code, dict):
        return ""
    areas = dicts(code.get("areas"))
    commits = texts(code.get("commits"))
    if not areas and not commits:
        return ""
    info, files = code_stats(repo, commits) if repo and commits else ([], {})
    found = [c for c in info if not c.get("missing")]
    base = github_base(repo) if repo else None
    last = found[-1]["full"] if found else None

    totals = [{"files": 0, "new": 0, "add": 0, "del": 0} for _ in areas]
    other = {"files": 0, "new": 0, "add": 0, "del": 0}
    for path, f in files.items():
        i = area_of(path, areas)
        bucket = totals[i] if i is not None else other
        bucket["files"] += 1
        bucket["new"] += f["new"]
        bucket["add"] += f["add"]
        bucket["del"] += f["del"]
    rows = [(a.get("what", ""), texts(a.get("paths")), totals[i]) for i, a in enumerate(areas)]
    if other["files"]:
        rows.append((t["code_other"], [], other))
    peak = max([r[2]["add"] + r[2]["del"] for r in rows] + [1])

    def path_chip(p):
        label = esc(p)
        if base and last:
            kind = (git(repo, "cat-file", "-t", f"{last}:{p.strip('/')}") or "").strip()
            if kind in ("tree", "blob"):
                href = f"{base}/{kind}/{last}/{quote(p.strip('/'), safe='/')}"
                return f'<a class="path" href="{esc(href)}">{label}</a>'
        return f'<span class="path">{label}</span>'

    items = []
    for what, paths, s in rows:
        chips = "".join(path_chip(p) for p in paths)
        chips = f'<div class="paths">{chips}</div>' if chips else ""
        stats = ""
        if files:
            a_w = 100 * s["add"] / peak
            d_w = 100 * s["del"] / peak
            count = (t["code_files_new"].format(n=s["files"], k=s["new"]) if s["new"]
                     else t["code_files"].format(n=s["files"]))
            stats = (f'<span class="bar2" aria-hidden="true"><span class="a" style="width:{a_w:.1f}%"></span>'
                     f'<span class="d" style="width:{d_w:.1f}%"></span></span>'
                     f'<span class="lines"><span class="add">+{s["add"]:,}</span> <span class="del">−{s["del"]:,}</span></span>'
                     f'<span class="files">{count}</span>')
        items.append(f'<li class="area"><div class="area-t"><span class="area-w">{esc(what)}</span>{chips}</div>{stats}</li>')

    commit_rows = []
    for c in info:
        if c.get("missing"):
            commit_rows.append(f'<li class="cm"><span class="hash">{esc(c["ref"])}</span>'
                               f'<span class="cm-s">{t["code_missing"]}</span><span></span></li>')
            continue
        hash_html = esc(c["short"])
        if base:
            hash_html = f'<a class="hash" href="{esc(base)}/commit/{c["full"]}">{hash_html}</a>'
        else:
            hash_html = f'<span class="hash">{hash_html}</span>'
        commit_rows.append(f'<li class="cm">{hash_html}<span class="cm-s">{esc(c["subject"])}</span>'
                           f'<span class="cm-d">{fmt_date(c["date"], t)}</span></li>')
    commits_html = ""
    if commit_rows:
        commits_html = (f'<div class="commits"><h3>{t["code_commits"]}</h3><ul>' + "".join(commit_rows) + "</ul></div>")

    summary = ""
    if files:
        add = sum(f["add"] for f in files.values())
        rem = sum(f["del"] for f in files.values())
        summary = (f'<span class="count">{t["code_sum"].format(c=len(found), f=len(files))}，'
                   if t["html"].startswith("zh") else f'<span class="count">{t["code_sum"].format(c=len(found), f=len(files))}, ')
        summary += f'{t["code_lines"].format(a=f"{add:,}", d=f"{rem:,}")}</span>'
    note = f'<p class="code-note">{t["code_note"]}</p>' if files else ""
    return (f'<section class="sec" aria-labelledby="code-h"><div class="sec-h"><h2 id="code-h">{t["code"]}</h2>{summary}</div>'
            f'<div class="panel code"><ul class="areas">' + "".join(items) + f'</ul>{commits_html}{note}</div></section>')


def page(title, project, body, t, css=CSS, nav=""):
    replacements = {
        "%%LANG%%": t["html"],
        "%%TITLE%%": esc(title),
        "%%BOOT%%": THEME_BOOT,
        "%%CSS%%": css,
        "%%LOGO%%": icon("book", 20),
        "%%BRAND%%": t["brand"],
        "%%PROJECT%%": esc(project),
        "%%NAV%%": nav,
        "%%THEME%%": t["theme"],
        "%%TOGGLE%%": TOGGLE_JS,
        "%%MOON%%": icon("moon", 18, 2, "moon"),
        "%%SUN%%": icon("sun", 18, 2, "sun"),
        "%%PRINT%%": PRINT_JS,
        "%%BODY%%": "\n".join(part for part in body if part),
    }
    out = PAGE
    for token, value in replacements.items():
        out = out.replace(token, value)
    return out


def render(data, index_href=None, repo=None):
    t = labels(data.get("lang"))
    body = [
        hero(data, t),
        section_plan(data.get("plan"), t),
        section_changes(data.get("changes"), t),
        section_flow(data.get("flow"), t),
        section_risks(data.get("risks"), t),
        section_decisions(data.get("decisions"), t),
        story_row(data, t),
        section_code(data.get("code"), t, repo),
        section_facts(data, t),
    ]
    if data.get("finished"):
        body.append(f'<p class="foot">{t["foot"].format(date=fmt_date(data["finished"], t, year=True))}</p>')
    nav = ""
    if index_href:
        nav = f'<a class="nav" href="{esc(index_href)}">{icon("back", 16, 2.5)}{t["all"]}</a>'
    title = t["title"].format(name=data.get("milestone") or t["untitled"])
    return page(title, data.get("project", ""), body, t, nav=nav)


# Overview page -------------------------------------------------------------

def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return {}


def plain_title(text):
    """A one-line Markdown title as plain text."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("`", "").replace("**", "").replace("__", "")
    return text.strip(" #*_")


def dossier_name(dossier):
    for line in read_text(dossier / "task-brief.md").splitlines():
        match = re.match(r"#\s+(?:Task Brief:\s*)?(.+)", line)
        if match and plain_title(match.group(1)):
            return plain_title(match.group(1))
    slug = DOSSIER_RE.match(dossier.name).group(2)
    return slug.replace("-", " ").capitalize()


def load_report(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def dossiers_in(tasks_dir):
    try:
        children = list(tasks_dir.iterdir())
    except OSError:
        return []
    return sorted(p for p in children if p.is_dir() and DOSSIER_RE.match(p.name))


def project_name(tasks_dir, reports):
    for data in reports:
        if isinstance(data.get("project"), str) and data["project"].strip():
            return data["project"]
    here = tasks_dir.resolve()
    for folder in (here, *here.parents):
        if (folder / ".git").exists():
            return folder.name
    return here.parent.name


def index_lang(reports):
    """The language most reports use; English on a tie or with no reports."""
    counts = {}
    for data in reports:
        lang = data.get("lang") if data.get("lang") in LABELS else "en"
        counts[lang] = counts.get(lang, 0) + 1
    best = max(counts.values(), default=0)
    return "en" if counts.get("en", 0) == best else max(counts, key=counts.get, default="en")


def index_row_finished(dossier, data, t):
    outcome = data.get("outcome")
    pill = ""
    if outcome in t["outcome"]:
        pill = f'<span class="pill pill-{outcome}">{t["outcome"][outcome]}</span>'
    when = data.get("finished") or DOSSIER_RE.match(dossier.name).group(1)
    kicker = esc(data.get("milestone") or dossier_name(dossier))
    plan = data.get("plan") if isinstance(data.get("plan"), dict) else {}
    if plan.get("name"):
        kicker = t["ix_kicker_plan"].format(milestone=kicker, plan=esc(plan["name"]))
    tags = []
    goals = dicts(data.get("doneWhen"))
    if goals:
        met = sum(1 for g in goals if g.get("met") is True)
        tags.append(f'<span class="tag">{icon("check", 13, 3)}{t["ix_goals"].format(met=met, n=len(goals))}</span>')
    yours = sum(1 for d in dicts(data.get("decisions")) if d.get("by") == "you")
    if yours:
        text = t["ix_you_1"] if yours == 1 else t["ix_you_n"].format(n=yours)
        tags.append(f'<span class="tag you">{icon("fork", 13, 2.5)}{text}</span>')
    risks = len(dicts(data.get("risks")))
    if risks:
        tags.append(f'<span class="tag warn">{icon("alert", 13, 2.5)}{t["ix_risks"].format(n=risks)}</span>')
    meta = f'<div class="row-meta">{"".join(tags)}</div>' if tags else ""
    href = f"{dossier.name}/report.html"
    return (when, f'<li><a class="panel row" href="{esc(href)}"><span class="row-date">{fmt_date(when, t, year=True)}</span>'
                  f'<span class="row-main"><span class="row-k">{kicker}</span>'
                  f'<span class="row-h">{esc(data.get("headline", ""))}</span>{meta}</span>'
                  f'<span class="row-end">{pill}<span class="row-go">{icon("right", 20, 2.5)}</span></span></a></li>')


def index_row_plain(dossier, label, cls, date_text, sort_date):
    return (sort_date, f'<li><div class="panel row slim"><span class="row-date">{date_text}</span>'
                       f'<span class="row-main"><span class="row-h">{esc(dossier_name(dossier))}</span></span>'
                       f'<span class="row-end"><span class="pill {cls}">{label}</span></span></div></li>')


def render_index(tasks_dir):
    entries, reports = [], []
    for dossier in dossiers_in(tasks_dir):
        data = load_report(dossier / REPORT_NAME)
        entries.append((dossier, data))
        if data is not None:
            reports.append(data)
    t = labels(index_lang(reports))

    finished, open_rows = [], []
    for dossier, data in entries:
        started = DOSSIER_RE.match(dossier.name).group(1)
        if data is not None:
            finished.append(index_row_finished(dossier, data, t))
            continue
        handoff = frontmatter(read_text(dossier / "handoff.md"))
        if handoff.get("status", "").startswith("Complete"):
            updated = handoff.get("updated", "")
            when = updated if DATE_RE.match(updated) else started
            finished.append(index_row_plain(dossier, t["ix_no_report"], "pill-none",
                                            fmt_date(when, t, year=True), when))
        else:
            open_rows.append(index_row_plain(dossier, t["ix_open"], "pill-open",
                                             t["ix_started"].format(date=fmt_date(started, t)), started))
    finished.sort(key=lambda row: row[0], reverse=True)
    open_rows.sort(key=lambda row: row[0], reverse=True)
    reports.sort(key=lambda d: str(d.get("finished", "")), reverse=True)
    project = project_name(tasks_dir, reports)

    counts = []
    if finished:
        counts.append(t["ix_count_fin"].format(n=len(finished)))
    if open_rows:
        counts.append(t["ix_count_open"].format(n=len(open_rows)))
    summary = t["ix_join"].join(counts) if counts else t["ix_none"]
    body = [f'<section class="ix-hero"><h1>{esc(project)}</h1><p class="ix-sum">{summary}</p></section>']
    if open_rows:
        body.append(f'<section class="sec" aria-labelledby="open-h"><h2 id="open-h">{t["ix_open"]}</h2>'
                    '<ul class="rows">' + "".join(row for _, row in open_rows) + "</ul></section>")
    if finished:
        body.append(f'<section class="sec" aria-labelledby="fin-h"><h2 id="fin-h">{t["ix_fin"]}</h2>'
                    '<ul class="rows">' + "".join(row for _, row in finished) + "</ul></section>")
    if not finished and not open_rows:
        body.append(f'<p class="panel empty">{t["ix_empty"]}</p>')
    return page(t["ix_title"].format(project=project), project, body, t, css=CSS + INDEX_CSS)


# Command line --------------------------------------------------------------

def collect(paths):
    """Expand args into (paths, report.json files); default tasks dir when none given."""
    if not paths:
        default = Path("docs/tasks")
        if not default.is_dir():
            print("No paths given and docs/tasks not found; pass the tasks dir, "
                  "dossier dirs, or report.json files explicitly.", file=sys.stderr)
            sys.exit(2)
        paths = [default]
    paths = [Path(raw) for raw in paths]
    files = []
    for p in paths:
        if p.is_dir():
            files.extend(sorted(p.rglob(REPORT_NAME)))
        elif p.is_file():
            files.append(p)
        else:
            print(f"Path not found: {p}", file=sys.stderr)
            sys.exit(2)
    return paths, files


def tasks_dirs(paths, files):
    """Folders that hold dated dossiers: the overview goes in each of them."""
    found = {}

    def add(folder):
        found.setdefault(folder.resolve(), folder)

    for p in paths:
        if p.is_dir():
            if DOSSIER_RE.match(p.resolve().name):
                add(p.parent if p.name else p.resolve().parent)
            elif dossiers_in(p):
                add(p)
    for f in files:
        if DOSSIER_RE.match(f.resolve().parent.name):
            add(f.parent.parent)
    return list(found.values())


def open_page(path):
    try:
        opened = webbrowser.open(path.resolve().as_uri())
    except webbrowser.Error:
        opened = False
    if opened:
        print(f"opened {path}")
    else:
        print(f"No browser available here; open {path} yourself.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", help="tasks dir, dossier dirs, or report.json files")
    parser.add_argument("--repo", help="git repository for the code section (default: the report's own)")
    parser.add_argument("--open", action="store_true",
                        help="open the overview page (or the report) in a browser")
    args = parser.parse_args()

    paths, files = collect(args.paths)
    folders = tasks_dirs(paths, files)
    if not files and not folders:
        print("No report.json or dated dossier found.", file=sys.stderr)
        sys.exit(2)
    failed = 0
    written = []
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"{path}: cannot read report: {exc}", file=sys.stderr)
            failed += 1
            continue
        if not isinstance(data, dict):
            print(f"{path}: report must be a JSON object", file=sys.stderr)
            failed += 1
            continue
        in_dossier = DOSSIER_RE.match(path.resolve().parent.name)
        out = path.with_name("report.html")
        repo = Path(args.repo) if args.repo else repo_root(path.resolve().parent)
        out.write_text(render(data, f"../{INDEX_NAME}" if in_dossier else None, repo), encoding="utf-8")
        written.append(out)
        print(f"wrote {out}")
    indexes = []
    for folder in folders:
        out = folder / INDEX_NAME
        out.write_text(render_index(folder), encoding="utf-8")
        indexes.append(out)
        print(f"wrote {out}")
    if args.open:
        target = indexes[0] if indexes else (written[-1] if written else None)
        if target:
            open_page(target)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
