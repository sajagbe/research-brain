# Research Brain

Portable, harness-agnostic research organization, knowledge management, Lamport structured proof workflow, and deterministic citation verification for any coding agent (Claude Code, Codex, Cursor, OpenCode, Antigravity, or headless remote SSH Linux boxes).

## Architecture

- **`AGENTS.md`**: Ultra-lean (~30 lines) core invariants, 50% context ceiling, personal conventions, and skill pointers synced across harnesses.
- **6 Focused Skills (`skills/`)**:
  - `rb-proof` *(model-invoked)* — Lamport hierarchical proof decomposition (`1.`, `1.1.`, `1.1.1.`), bounded recursive zero-context adversarial review (depth 3, 2 reviewers, max 3 rounds), and external formalization gate.
  - `rb-km` *(model-invoked)* — Librarian (`library/`), Wiki ground truth (`wiki/`), Project Notebook (`projects/<slug>/notebook/`), and append-only Worklogs (`projects/<slug>/worklogs/`).
  - `rb-cite` *(model-invoked)* — Verbatim quote-before-acting protocol (`[@source-id, p.X, L.Y]`), deterministic `rb verify-quotes`, and non-destructive human-confirmed highlights (`rb highlight --confirmed`).
  - `rb-explain` *(model-invoked)* — Intuition-first theory/math explanations, real-space-to-matrix bridges, and mandatory colored LaTeX equation annotations in all documents (`\color` + `\underbrace`/`\overbrace` or `annotate-equations` `\eqnmarkbox`/`\annotate`).
  - `rb-garden` *(user-invoked)* — Scoped sub-area Gardener pass honoring `GARDEN_POLICY.md` (`ask-first` until explicitly promoted to `converged`).
  - `rb-project` *(user-invoked)* — Bootstrap a sandboxed project repo, notebook, worklog, vault pointer, and git pre-commit hooks.
- **Deterministic CLI (`rb`) + Git Hooks**: Runs completely outside model control. Verifies verbatim quotes against immutable Library originals (PDF via PyMuPDF and text/Markdown/code via line ranges), checks Wiki verification headers and Gardener policies, and blocks invalid commits via `git` pre-commit hooks.
- **Companion `pstack` Composition**: `./install.sh` automatically fetches and links `cursor/plugins`'s `pstack` skills alongside Research Brain on every local or remote machine.

## Install (Local Mac or Remote Linux Device)

```bash
git clone <your-research-brain-repo-url> ~/research-brain
cd ~/research-brain
./install.sh --with-harness-hooks
```

To point to a synced remote vault repository on another machine:

```bash
git clone <your-vault-repo-url> ~/research-brain-vault
./install.sh --vault ~/research-brain-vault
# or per-shell: export RESEARCH_BRAIN_VAULT=~/research-brain-vault
```

## Quick CLI Reference

```bash
rb doctor                                                     # Check tools, vault, hooks, config
rb init-project "My Study" --repo ~/code/my-study             # Create Notebook, Worklog, repo hook
rb ingest paper.pdf --id lamport2012 --area proofs            # Catalog immutable source in library/
rb verify-quotes --staged                                     # Deterministically verify verbatim quotes
rb highlight lamport2012 --page 2 --quote "..." --confirmed   # Non-destructive PDF + MD highlight
rb log my-study --kind exp --text "Baseline converged."       # Append chronological worklog entry
rb lint                                                       # Full vault integrity check (quotes, colors, ref table, acronyms, provenance)
rb garden status                                              # Show ask-first / converged sub-areas
rb garden converge wiki/general --approved                    # Promote sub-area after human approval
```
