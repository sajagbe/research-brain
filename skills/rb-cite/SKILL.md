---
name: rb-cite
description: "Enforce verbatim quoting with exact page/line/source citations before acting on external ideas, run deterministic out-of-model quote verification (`rb verify-quotes`), and apply non-destructive source highlights (`rb highlight --confirmed`) once the human confirms understanding. Trigger whenever citing papers, docs, codebases, or highlighting understood references."
---

# Research Brain — Verbatim Citation & Source Highlighting (`rb-cite`)

Zero paraphrased claims masquerading as quotes, and zero unverified citations entering the Wiki, Notebook, or implementation plans.

## Branch 1 — Quote Verbatim Before Acting
1. **Check Library provenance**: Look up the source in `<vault>/library/catalog.json`.
   - If the source is **new**, ingest it first with `rb ingest <file> --id <source-id> --area <area> --title "..." --url "..."` so the full document enters `library/`, then log it to the project worklog (`rb log`).
   - If the source is **already cataloged**, extract only the specific target page/lines needed for the current subtask.
2. **Format every quote block** so deterministic hooks can verify it:
   ```markdown
   > "Exact verbatim substring from the source document." [@source-id, p.12]
   ```
   - For PDFs: include `p.<page>` (1-indexed), optionally `, L.<start>-<end>`.
   - For Markdown / text / code files: include `L.<start>` or `L.<start>-<end>` (1-indexed).
3. **Run deterministic verification outside the model's control**:
   - Execute `rb verify-quotes <file>` (and rely on the installed `git` pre-commit hook on every commit).
   - If verification fails, inspect the actual source page/lines and correct the quote—never fabricate or smooth wording inside quotation marks.
- *Done when:* Every relied-upon external claim carries a verbatim quote with `[@source-id, p.X/L.Y]` and `rb verify-quotes` exits 0.

## Branch 2 — Highlight After Human Understanding
1. **Wait for explicit human confirmation**: Never run `rb highlight` merely because an agent read a passage. Trigger highlighting only when the human confirms they understood a cited reference (e.g., *"got it, highlight that"*, *"mark that reference understood"*).
2. **Apply non-destructive highlights**:
   ```bash
   rb highlight <source-id> --page <N> --quote "<exact verbatim quote>" --note "<1-sentence takeaway>" --confirmed
   ```
   - For PDFs, `rb highlight` preserves the original immutable PDF and writes a real yellow highlight annotation onto `<source-id>.annotated.pdf` plus an entry in `<source-id>.highlights.md`.
   - For text/Markdown sources, it appends the Obsidian-highlighted quote (`==...==`) to `<source-id>.highlights.md`.
3. Commit the sidecar / annotated PDF in the vault repo.
- *Done when:* `rb highlight --confirmed` exits 0 and prints the updated sidecar / annotated PDF path.
