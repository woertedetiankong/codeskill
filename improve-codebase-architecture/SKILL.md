---
name: improve-codebase-architecture
description: Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the decisions in docs/adr/. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, reduce legacy compatibility or defensive-code bloat, make a codebase more testable and AI-navigable, use Codex sub-agents for architecture exploration, or produce an optional visual HTML architecture report.
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. Prefer replacing obsolete compatibility paths with tighter interfaces over preserving every old call shape. The aim is testability and AI-navigability.

## Glossary

Use these terms exactly in every suggestion. Consistent language is the point — don't drift into "component," "service," "API," or "boundary." Full definitions in [LANGUAGE.md](LANGUAGE.md).

- **Module** — anything with an interface and an implementation (function, class, package, slice).
- **Interface** — everything a caller must know to use the module: types, invariants, error modes, ordering, config. Not just the type signature.
- **Implementation** — the code inside.
- **Depth** — leverage at the interface: a lot of behaviour behind a small interface. **Deep** = high leverage. **Shallow** = interface nearly as complex as the implementation.
- **Seam** — where an interface lives; a place behaviour can be altered without editing in place. (Use this, not "boundary.")
- **Adapter** — a concrete thing satisfying an interface at a seam.
- **Compatibility layer** — a temporary Module that keeps an old interface working while forwarding to a new one. Treat it as debt unless an ADR, public contract, or migration window requires it.
- **Leverage** — what callers get from depth.
- **Locality** — what maintainers get from depth: change, bugs, knowledge concentrated in one place.

Key principles (see [LANGUAGE.md](LANGUAGE.md) for the full list):

- **Deletion test**: imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.**
- **One adapter = hypothetical seam. Two adapters = real seam.**
- **Replacement over compatibility layering**: unless an ADR, public contract, supported migration window, or currently-used external caller requires backward compatibility, prefer deleting obsolete paths and narrowing the interface over adding fallbacks, compatibility adapters, or defensive branches.
- **Defensive code must buy observed risk**: add guards only for inputs that can actually cross the Module's interface. Normalize invalid states at the seam; don't scatter defensive checks through the implementation.

This skill is _informed_ by the project's domain model. The domain language gives names to good seams; ADRs record decisions the skill should not re-litigate.

## Process

### 1. Explore

Read the project's domain glossary and any ADRs in the area you're touching first.

When Codex multi-agent tools are available and the user has asked for sub-agents, delegation, or parallel exploration, spawn one or more Codex explorer sub-agents with `multi_agent_v1.spawn_agent` and `agent_type="explorer"`. Give each explorer a specific, non-overlapping codebase question, then integrate their findings with your own local reading. Good explorer prompts include:

- "Find shallow modules around <domain concept>; report files, call sites, and why the interface feels as complex as the implementation."
- "Find compatibility layers, deprecated call shapes, fallbacks, or defensive branches around <area>; report what evidence would make them safe to remove."
- "Find test seams around <area>; report where tests cross stable interfaces versus implementation details."

If sub-agent tools are unavailable or not explicitly authorized for this run, explore locally with `rg`, file reads, and the same questions below. Don't follow rigid heuristics — explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?
- Where are legacy compatibility paths, fallbacks, deprecated call shapes, or defensive branches keeping an old interface alive?
- Where do repeated guards suggest the interface has unclear invariants that should be tightened at the seam?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

### 2. Present candidates

Before presenting anything, apply a quality gate. A candidate is worth surfacing only when it has **real friction**:

- Recent or likely work would touch the area and currently requires bouncing between modules.
- A bug, test gap, adapter mismatch, or roadmap item would become easier after deepening.
- The change has meaningful **Locality** or **Leverage**, not merely cleaner naming or prettier layering.
- The candidate is not just "the next abstraction" after a recent successful deepening. Re-suggest a just-deepened Module only when new friction remains at its interface.

Use the current product direction to rank candidates. If docs name an upcoming priority, prefer candidates that unblock it. Put theoretical or low-value ideas in a short **Backlog** note instead of presenting them as active recommendations.

Present a numbered list of deepening opportunities only for candidates that pass the gate. For each candidate:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage, and also in how tests would improve
- **Removal plan** — what old paths, wrappers, fallback branches, tests, or compatibility adapters can be deleted; what evidence proves they are safe to remove; and what must temporarily remain because of an explicit contract or migration window

**Use CONTEXT.md vocabulary for the domain, and [LANGUAGE.md](LANGUAGE.md) vocabulary for the architecture.** If `CONTEXT.md` defines "Order," talk about "the Order intake module" — not "the FooBarHandler," and not "the Order service."

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly (e.g. _"contradicts ADR-0007 — but worth reopening because…"_). Don't list every theoretical refactor an ADR forbids.

**Stop rules**:

- Do not aim for five candidates by default. One strong candidate is better than five marginal ones.
- If no candidate passes the quality gate, say so clearly and list at most 1-3 backlog observations.
- If a previous round just deepened several Modules, frame new findings as "second-round candidates" and explicitly say they are optional unless they unblock current work.
- Recommend at most 1-2 candidates to explore now. Mark the rest as "backlog" or "defer" when they lack urgency.
- Never imply the user should keep refactoring until the skill finds no more suggestions. This skill is a radar, not an acceptance test.

Default output is the numbered candidate list above.

**Optional HTML report mode**: use this only when the user explicitly asks for an HTML report, visual report, before/after diagrams, or asks to make the architecture review visual. In that mode:

- Read [HTML-REPORT.md](HTML-REPORT.md) before writing the report.
- Apply the same quality gate, ranking, stop rules, ADR conflict handling, and removal-plan discipline as the default output. The visual mode changes presentation, not standards.
- Write a self-contained HTML file to the OS temp directory so nothing lands in the repo. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `<tmpdir>/architecture-review-<timestamp>.html` so each run gets a fresh file.
- Open it for the user when the environment supports it — `xdg-open <path>` on Linux, `open <path>` on macOS, `start <path>` on Windows — and tell them the absolute path.
- If no candidate passes the quality gate, do not invent visual candidates. Say so clearly; create a short empty-finding report only if the user explicitly requested an HTML artifact.

Do NOT propose interfaces yet. Ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, drop into a grilling conversation. Walk the design tree with them — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Before designing a new interface, decide what gets removed. Ask which old call shapes, compatibility layers, fallback branches, and defensive checks are still required by real callers. If the answer is "probably nobody," search the codebase instead of preserving them by default.

Side effects happen inline as decisions crystallize:

- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add the term to `CONTEXT.md` — same discipline as `/grill-with-docs` (see [CONTEXT-FORMAT.md](../grill-with-docs/CONTEXT-FORMAT.md)). Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update `CONTEXT.md` right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR, framed as: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing — skip ephemeral reasons ("not worth it right now") and self-evident ones. See [ADR-FORMAT.md](../grill-with-docs/ADR-FORMAT.md).
- **Want to explore alternative interfaces for the deepened module?** See [INTERFACE-DESIGN.md](INTERFACE-DESIGN.md).
