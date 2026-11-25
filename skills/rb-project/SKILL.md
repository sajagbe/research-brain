---
name: rb-project
description: "Bootstrap a new sandboxed research project: git repo/worktree, Project Notebook, Worklog, vault pointer, and pre-commit verification hooks."
disable-model-invocation: true
---

# Research Brain — Project Bootstrap (`rb-project`)

Set up every new research or engineering project with version control, a persistent Project Notebook, an append-only Worklog, and deterministic pre-commit quote/lint hooks before doing substantive work.

## Steps

1. **Verify Global Vault & Tools**
   - Run `rb doctor`. If the Global Vault is not initialized yet, run `rb init-vault`.
   - *Done when:* `rb doctor` passes all checks.

2. **Initialize Project Spaces**
   - Run:
     ```bash
     rb init-project "<project-name>" --repo "<project-repo-path>"
     ```
   - This creates `<vault>/projects/<slug>/notebook/` (`README.md`, `HYPOTHESES.md`, `proofs/`), `<vault>/projects/<slug>/worklogs/`, writes `.research-brain.toml` in the code repo, ensures `git init`, and installs the portable `pre-commit` hook.
   - *Done when:* `rb init-project` exits 0 and prints the created notebook, worklog, marker, and hook paths.

3. **Seed Initial Context & First Commit**
   - Populate `projects/<slug>/notebook/README.md` with the research goal, success criteria, and initial references.
   - Log project kickoff via `rb log "<project-name>" --kind decision --text "Initialized project workspace and research notebook."`.
   - Record the initial git commit in both the vault and the project repo.
   - *Done when:* Both repos have clean `git status` and `rb lint` exits 0.
