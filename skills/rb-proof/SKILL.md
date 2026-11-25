---
name: rb-proof
description: "Decompose a research hypothesis, design, or algorithm into Lamport numbered hierarchical claims, run recursive zero-context adversarial proof/review subagents until counterexamples vanish, and select an external formalization check (Python/SymPy/Z3/tests or Lean/TLA+) before building. Trigger before implementing any non-trivial hypothesis, mathematical derivation, architecture claim, or experimental plan."
---

# Research Brain — Proof & Adversarial Verification (`rb-proof`)

Prove the claim before writing implementation code. Focus strictly on the current subtask using only the scoped sources loaded via `rb-km`.

Read [`references/lamport-template.md`](references/lamport-template.md) for the exact Lamport numbering and review-report schema.

## Steps

1. **Scope & Ground the Claim**
   - State the top-level hypothesis (`Theorem / Claim 1`) in one falsifiable sentence inside `projects/<slug>/notebook/proofs/<claim-slug>.md`.
   - Attach exact verbatim quotes (`rb-cite`) for every external theorem, equation, or empirical premise the claim relies on.
   - *Done when:* Top-level claim, explicit assumptions, and `rb verify-quotes` on the proof file all exit 0.

2. **Lamport Hierarchical Decomposition**
   - Break `1.` into numbered, independently verifiable sub-claims (`1.1.`, `1.2.`, …; recurse to `1.1.1.` where a step still spans multiple logical leaps).
   - Keep each leaf claim small enough that a zero-context reviewer can verify it solely from its stated premises and cited sources.
   - *Done when:* Every inference step names the exact earlier numbered claims or `[@source-id, p.X]` citations it depends on, up to `max_depth` (default `3`, check `rb doctor`).

3. **Recursive Zero-Context Adversarial Review**
   - Spawn **2 independent fresh-context subagents** (`reviewers_per_round` from config, default `2`) in parallel. Give each subagent *only* the proof file and the specific referenced source excerpts—never prior chat history or your reasoning draft.
   - Instruct each adversarial reviewer to hunt strictly for **substantive failures**: concrete counterexamples, hidden assumptions, invalid quantifiers/edge cases, mismatched definitions, or unverified leaps (ignore prose style).
   - If `pstack`'s `interrogate` skill is installed, apply its proven-finding bar (every objection must exhibit a concrete counterexample or broken dependency).
   - For every surviving objection: either fix the flaw or split the contested step into finer Lamport substeps (`1.2.1.`, `1.2.2.`) and dispatch fresh zero-context reviewers on the revised branch.
   - Repeat up to `max_rounds` (default `3`).
   - *Done when:* Both independent zero-context reviewers report **zero substantive objections**, OR round 3 ends and the unresolved counterexamples are escalated clearly to the human.

4. **External Formalization Gate**
   - Choose the lightest external tool that actually captures the claim's invariants (outside LLM text generation):
     - **Default tier**: Executable Python (`uv`) script — SymPy symbolic equivalence, numerical / Monte Carlo boundary tests, property-based tests (`hypothesis`), Z3 constraint check, or custom lint/hook rule.
     - **Heavy formal tier (opt-in)**: Lean 4 (theorem proving) or TLA+ (concurrency/state machines — compose with `pstack`'s `create-formal-verification-skill` / `statechart`).
   - Run the external check and verify it **fails** when an assumption is violated (proving the check tests the real invariant).
   - *Done when:* The external check passes on the valid claim, fails on a negated control case, and the proof + verification script are committed to git and logged via `rb log <project> --kind decision`.
