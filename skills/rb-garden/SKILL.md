---
name: rb-garden
description: "Run a Gardener subagent pass on a Wiki or Library sub-area to fix redundancies and inconsistencies while respecting its ask-first vs. converged GARDEN_POLICY.md."
disable-model-invocation: true
---

# Research Brain — Sub-Area Gardener (`rb-garden`)

Eliminate duplicate pages, stale cross-references, and contradictions inside a single Wiki or Library sub-area (`wiki/<area>` or `library/<area>`).

## Steps

1. **Inspect Sub-Area Policy**
   - Run `rb garden status` and read `<vault>/<area>/GARDEN_POLICY.md`.
   - Confirm whether `status` is `ask-first` or `converged`.
   - *Done when:* You know the exact target sub-area, its current policy status, and its documented approved rules.

2. **Dispatch Scoped Gardener Subagent**
   - Spawn a fresh-context Gardener subagent scoped **only** to `<vault>/<area>/` (plus `wiki/INDEX.md` and `library/catalog.json` read-only).
   - Have it run `rb lint`, identify redundant pages, contradictory claims, missing `status: verified` headers, broken `[[wikilinks]]`, or uncited statements, and prepare a concrete edit plan.
   - *Done when:* Subagent returns a concise audit listing each issue, exact file paths, and proposed changes.

3. **Respect Convergence Gate**
   - **If `status: ask-first`** (or if any edit falls outside `## Approved Rules` in `GARDEN_POLICY.md`):
     - Stage changes only on a dedicated git branch (`garden/<area>-YYYYMMDD`) OR present the exact proposed diff to the human.
     - Ask explicit permission before applying/merging to `main`. Record the human's decision in `GARDEN_POLICY.md` under `## Decision Log` and update `## Approved Rules` if a new general rule emerged.
     - If the human confirms the method has converged, run `rb garden converge <area> --approved`.
   - **If `status: converged`**:
     - Apply edits strictly covered by `## Approved Rules`, preserve every verbatim quote and `[@source-id, ...]` citation, and escalate any out-of-policy restructuring for approval.
   - *Done when:* `rb lint` exits 0 on the vault, human approval is obtained wherever required, and the verified result is committed cleanly.
