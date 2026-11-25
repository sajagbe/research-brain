# Lamport Structured Proof Template

Save each active proof in `<vault>/projects/<slug>/notebook/proofs/<claim-slug>.md`.

```markdown
---
project: <slug>
claim_id: <claim-slug>
status: draft | adversarially-verified | formalized | contested
round: 0
---

# Claim 1: <One falsifiable statement>

## Premises & Grounded Sources
- **P1**: <explicit assumption>
- **P2**:
  > "<exact verbatim quote>" [@source-id, p.X, L.Y]

## Proof Structure (Lamport Numbering)
- **1.1.** <Sub-claim 1>
  - *By:* P1, P2
  - **1.1.1.** <Finer atomic step if challenged>
  - **1.1.2.** <Finer atomic step if challenged>
- **1.2.** <Sub-claim 2>
  - *By:* 1.1
- **1.3.** Q.E.D. — Claim 1 follows from 1.1 and 1.2.

## Adversarial Review Log
| Round | Reviewer | Target Step | Concrete Objection / Counterexample | Resolution |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Reviewer A (0-ctx) | 1.1 | Missing positivity bound on $x$ | Added P3 ($x > 0$) and split 1.1.1–1.1.2 |

## External Formalization Check
- **Tool:** `uv run pytest ...` / `sympy` / `z3` / `lean4`
- **Negated Control Result:** Fails as expected when P3 is relaxed.
- **Verified Commit:** `<git-sha>`
```

## Prompt Template for Zero-Context Adversarial Reviewer

Give each reviewer ONLY the proof markdown and referenced excerpts:

> You are a hostile, zero-context proof verifier. You have zero access to the author's intent. Inspect each numbered Lamport claim (`1.1`, `1.1.1`, …) strictly against its listed premises and quoted excerpts. Report ONLY concrete counterexamples, hidden unstated assumptions, boundary failures, or non-sequiturs. Do not comment on wording or style. If every step holds rigorously from its stated premises, reply `ZERO_OBJECTIONS`.
