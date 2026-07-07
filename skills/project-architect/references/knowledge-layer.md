# Knowledge Layer — Obsidian Vault + Graphify

**Every new project ships with a two-part knowledge layer so memory and context are used efficiently from day one.** This is NOT optional and applies to ALL project categories.

| Layer | Location | What it holds | The question it answers |
|-------|----------|---------------|-------------------------|
| **Memory vault** (authored, Obsidian) | `~/SecondBrain/projects/<slug>/` (**central**, shared) | Human/agent-authored notes: decisions, domain glossary, ongoing context, gotchas | *Why* did we do this? What's the plan? What does term X mean? |
| **Code graph** (Graphify) | `graphify-out/` (**repo-local**) | Auto-extracted graph of code: functions, classes, schemas, god nodes, cross-module links — plus an auto-generated Obsidian vault of the codebase at `graphify-out/obsidian/` | *What* connects to what? Where does this flow go? |

The authored memory is **centralized**: every project's "why" lives under the single second-brain vault at `~/SecondBrain/`, so memory is never lost or fragmented across cwds and is referenced at every chat start (the global `~/.claude/CLAUDE.md` points the agent at it). The code graph stays **repo-local** because it is regenerated from the code and gitignored — centralizing it adds churn for no gain.

**The rule of thumb the project's agent follows:**
- Code / architecture / "where is X used" questions → **query the graph first** (`/graphify query "…"`) before grepping or reading many files. The query returns the relevant subgraph — far cheaper on context than reading files.
- "Why did we…", "what's the plan", "what does this term mean", "known gotcha" → **read the central vault** (`~/SecondBrain/projects/<slug>/`).

---

## Part 1 — Central Obsidian Memory Vault (`~/SecondBrain/projects/<slug>/`)

One shared Obsidian vault, `~/SecondBrain/`, holds every project. Open the app once at `~/SecondBrain/` and you see all projects. Each new project gets its own folder under `projects/`. It mirrors the user's global memory format: an index file plus one fact per note, frontmatter for recall, `[[wikilinks]]` between notes.

### Scaffold this structure (inside the central vault, not the repo)

```
~/SecondBrain/
  HOME.md                       # master index — add one pointer line per project here
  global/                       # cross-project conventions, preferences, feedback
  projects/
    <slug>/                     # ← create this for the new project
      MEMORY.md                 # project index — one line per note
      decisions/                # ADR-style notes: one decision per file
      domain/                   # glossary + domain model: one concept per file
      context/                  # ongoing work, goals, constraints, status
      reference/                # external links, dashboards, tickets, runbooks
```

After creating `projects/<slug>/`, append a pointer line under `## Proyectos` in `~/SecondBrain/HOME.md`.

### Note format (every file under the subfolders)

```markdown
---
name: <short-kebab-case-slug>
description: <one-line summary — used to decide relevance during recall>
metadata:
  type: decision | domain | context | reference
---

<The fact, in prose. For decisions, follow with **Why:** and **Consequences:** lines.>

Link related notes with [[their-name]] (the other note's `name:` slug).
```

### `MEMORY.md` index format

One line per note, grouped by type. No frontmatter, no note content — just pointers:

```markdown
# Project Memory — {PROJECT_NAME}

## Decisions
- [Why SQLite over Postgres](decisions/db-choice-sqlite.md) — single-writer, local-first

## Domain
- [What "parking lot" means](domain/parking-lot.md) — queue for uncertain items

## Context
- [Milestone 1 scope](context/milestone-1.md) — auth + ingestion, due {DATE}
```

### Seed content to generate at scaffold time (all under `~/SecondBrain/projects/<slug>/`)

1. `projects/<slug>/MEMORY.md` — the project index, pre-populated with one starter line per section.
2. `projects/<slug>/decisions/<initial-stack-choice>.md` — the first ADR capturing the stack/category chosen in the `/new-project` interview (language, framework, deployment target, **why**). This makes the vault non-empty and demonstrates the pattern.
3. `projects/<slug>/domain/` — one glossary note for the project's core noun if the interview surfaced domain terms.
4. A pointer line under `## Proyectos` in `~/SecondBrain/HOME.md`. (Vault conventions live once in `~/SecondBrain/HOME.md` — no per-project README needed.)

### Rules for the vault

- One fact per file — high cohesion. Update the matching file rather than duplicating.
- `MEMORY.md` (the project's, and the master `HOME.md`) is the only file assumed loaded each session; keep it to one line per note.
- Convert relative dates to absolute (`due in 2 weeks` → `due 2026-06-29`).
- Don't store what the code or git history already records — store the *why* and the non-obvious.
- **Self-improvement loop lands here.** When the owner corrects the agent (operating-system rung 3), the lesson becomes a durable note (`context/` for "always do X here", `decisions/` if it changes an approach) with a pointer in `MEMORY.md` — NOT a throwaway `lessons.md`. Active task tracking stays in repo-local `tasks/todo.md`; durable lessons live in the vault so they survive across sessions and cwds.
- The project's `CLAUDE.md` must point the agent at `~/SecondBrain/projects/<slug>/MEMORY.md` and at graphify (see CLAUDE.md template).

---

## Part 2 — Graphify Code Knowledge Graph (`graphify-out/`)

Graphify (`graphifyy` on PyPI) turns the repo into a queryable knowledge graph using local tree-sitter extraction plus LLM semantic analysis. It is installed **globally once** and run **per project**.

> **Stack-agnostic:** graphify is a global CLI tool (like ripgrep or `gh`) — installing it needs Python+`uv` on the machine *once*, but it does NOT add Python as a dependency of the project. It graphs any language (TS, Go, Rust, etc.) via tree-sitter. A non-Python project carries no Python toolchain because of this layer; the CLI lives at user level, not in the repo.

### One-time global install (already done on this machine)

```bash
uv tool install graphifyy   # installs the `graphify` CLI
graphify install            # wires the /graphify skill into the AI assistant
```

If a future machine lacks it: run the two commands above (requires Python 3.10+ and `uv`).

### Per-project setup (do this at scaffold time, AFTER initial files exist)

1. Build the first graph from the project root, also emitting the Obsidian vault:
   ```
   /graphify . --obsidian
   ```
   This generates `graphify-out/` containing `graph.html` (interactive view), `GRAPH_REPORT.md` (god nodes + suggested queries), `graph.json` (the queryable graph), and `obsidian/` (a browsable Obsidian vault of the codebase — one note per node, cross-linked).
   - `--obsidian` is required to get the vault; without it graphify skips it (it writes one file per node). To point at an existing vault instead: `/graphify . --obsidian --obsidian-dir <path>`.
2. Add `graphify-out/` to `.gitignore` — the graph and its vault are regenerated locally, not committed (per project convention). This covers `graphify-out/obsidian/` too.
3. Keep it fresh with graphify's **native** refresh (no hand-rolled hooks):
   - After structural changes: `/graphify . --update` (incremental, re-extracts only changed files, no LLM call).
   - Optional live mode: `graphify watch .` rebuilds automatically on code changes.
   - Teams: `graphify install` can set up a git merge-driver so committed graphs union-merge cleanly (only relevant if you ever decide to commit the graph).

### Daily use (the agent's commands)

| Command | Use |
|---------|-----|
| `/graphify . --obsidian` | Build / rebuild the graph + Obsidian vault for the current folder |
| `/graphify . --update` | Incremental refresh after code changes (fast, no LLM) |
| `/graphify query "how does auth flow work"` | Ask the graph a natural-language question (BFS traversal) |
| `/graphify path "Entity1" "Entity2"` | Find the connection between two entities |
| `/graphify explain "SomeNode"` | Plain-language explanation of a node and its neighbors |
| `graphify affected "SomeNode"` | Reverse traversal — what is impacted if this changes |

### Rules for the graph

- Treat code/architecture questions as a **graphify query first**, grep/read second.
- `graphify-out/` is gitignored — never commit it; regenerate on a fresh clone with `/graphify . --obsidian`.
- Refresh after structural changes with `/graphify . --update` so the graph never lies about the codebase.
