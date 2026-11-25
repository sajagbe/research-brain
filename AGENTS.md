## Research Brain

Central operating discipline for research and engineering tasks across any coding agent. Vault path resolves via `RESEARCH_BRAIN_VAULT` or `~/.config/research-brain/config.toml` (`rb doctor` inspects status).

### Core Invariants
1. **Sandboxed VCS discipline**: Work inside a `git` repository; use a dedicated branch or worktree for parallel explorations. Record an atomic commit after every verified step so every state is inspectable and revertible.
2. **50% context ceiling**: Keep active context under 50%. Offload broad search, literature reads, adversarial review, and vault gardening to fresh-context subagents; return concise summaries and exact file paths to the main thread.
3. **Prove before building**: Before implementing any non-trivial hypothesis, design, or method, invoke **`rb-proof`** to decompose claims into Lamport numbered assertions, run zero-context adversarial review, and choose an external formalization check.
4. **Quote verbatim before acting**: Before relying on or implementing any claim from an external source, invoke **`rb-cite`**, quote verbatim with `[@source-id, p.X, L.Y]`, and pass `rb verify-quotes`.
5. **Single-task KM focus**: Load only the Library, Wiki, and Project Notebook slices needed for the current subtask via **`rb-km`**. Write verified, cited ground truths to `wiki/`; write working notes to `projects/<name>/notebook/` and chronological events to `projects/<name>/worklogs/`.
6. **Compose with `pstack`**: Use `pstack` skills (`interrogate`, `correct`, `show-me-your-work`, `create-formal-verification-skill`, `principle-prove-it-works`) when installed; turn every repeated human correction into a lint rule, hook, or skill update.

### Skill Pointers
- **`rb-proof`**: Lamport hierarchical proofs, recursive zero-context adversarial review, and external formalization checks before building.
- **`rb-km`**: Librarian cataloging (`library/`), Wiki ground-truth maintenance (`wiki/`), Project Notebook synthesis, and Worklog logging.
- **`rb-cite`**: Verbatim source quoting, `rb verify-quotes` hook checks, and human-confirmed source highlighting (`rb highlight --confirmed`).
- **User-invoked setup & maintenance**: `/rb-project` (bootstrap project + hooks), `/rb-garden` (sub-area redundancy/consistency pass).

### Personal Conventions
- **Spelling**: US English.
- **Python**: Manage environments and tools with `uv`.
- **Commits**: Atomic conventional commits on verified states; ask before amending published history or force-pushing.
- **Provenance**: Tag any claim without an inspected primary source `[UNVERIFIED]`; highlight source documents only after explicit human confirmation (`rb highlight --confirmed`).
