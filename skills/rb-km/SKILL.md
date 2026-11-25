---
name: rb-km
description: "Operate the Research Brain Knowledge Management system: Librarian cataloging of external sources in library/, Wiki maintenance of verified ground-truth pages in wiki/, Project Notebook synthesis in projects/<slug>/notebook/, and chronological Worklog logging in projects/<slug>/worklogs/. Trigger when ingesting papers/sources, looking up verified ground truth, recording session progress, or promoting verified findings to the wiki."
---

# Research Brain — Knowledge Management (`rb-km`)

Every piece of knowledge has **one canonical home** inside the git-backed Global Vault (`rb doctor` prints the resolved vault path):

| Store | Path in Vault | Mutability | Trust Level | Role |
| :--- | :--- | :--- | :--- | :--- |
| **Library** | `library/<area>/` + `catalog.json` | Immutable originals | Primary source | External papers, specs, PDFs, datasets, and `.highlights.md` |
| **Wiki** | `wiki/<area>/` + `INDEX.md` | Curated & versioned | **Verified ground truth** | Reusable cross-project facts backed by exact `[@source-id, p.X, L.Y]` citations |
| **Project Notebook** | `projects/<slug>/notebook/` | Mutable living synthesis | Working / in-progress | Current hypotheses, active Lamport proofs, open questions for one project |
| **Worklog** | `projects/<slug>/worklogs/YYYY-MM-DD.md` | Append-only | Chronological raw log | Experiments run, dead ends, commands, decisions, raw verbatim extracts |

Read [`references/librarian-classification.md`](references/librarian-classification.md) when organizing new Library subject areas or resolving ambiguous cataloging.

## Context-Budgeted Retrieval (Focus on Subtask Only)
- Start from `wiki/INDEX.md` or `projects/<slug>/notebook/README.md`—never read the full vault or old worklogs speculatively.
- When searching across many Library sources or Wiki pages, dispatch a **Librarian subagent** (fresh context) to retrieve only the exact relevant passages and source IDs.

## Branch 1 — Librarian (Ingest External Source)
1. Save or obtain the source file locally (PDF, Markdown, text, or captured web/paper text).
2. Run `rb ingest <file> --id <authorYEARslug> --area <area> --title "..." --url "..."` to copy it into `library/<area>/`, record its SHA-256 in `library/catalog.json`, and ensure `library/<area>/GARDEN_POLICY.md` exists.
3. If the source was fetched for an active project, log the ingestion via `rb log <project> --kind quote --text "..." --cite "[@<id>, p.X]"`.
- *Done when:* `library/catalog.json` contains the source ID and `git status` shows the source + catalog staged/committed cleanly.

## Branch 2 — Wiki Orchestrator (Write / Promote Ground Truth)
1. Promote content to `wiki/<area>/<concept>.md` **only after verification** (verified quote from Library, passed `rb-proof`, or verified empirical result). Keep unverified ideas in `projects/<slug>/notebook/`.
2. Every Wiki page includes frontmatter `status: verified`, concise Zettelkasten-style atomic scope (one concept/result per page), verbatim quotes (`rb-cite`) citing `library/` or a logged worklog, and links in `wiki/INDEX.md`.
3. Run `rb lint` and commit the verified update to the vault repo.
- *Done when:* `rb lint` exits 0 with zero errors and the vault git commit is recorded.

## Branch 3 — Project Notebook & Worklog
1. **During a session**: Record concrete experiments, decisions, dead ends, and verbatim source extracts via `rb log <project> --kind <exp|decision|quote|dead-end> --text "..."`.
2. **At session milestones**: Distill durable takeaways into `projects/<slug>/notebook/README.md` (and `HYPOTHESES.md`) so the next fresh-context agent inherits current state without re-reading raw worklogs.
3. Commit vault updates atomically and run `rb lint`.
- *Done when:* Worklog captures raw events, Notebook reflects current concise state, and `rb lint` exits 0.
