---
name: rb-explain
description: "Explain theoretical concepts, physical mechanisms, quantum chemistry or mathematical derivations, presentation Q&A prep, or methodological pivots ('old way vs. new way') using pure physical intuition first, then bridging to formal equations. Enforces mandatory colored LaTeX equation annotations unpacking every individual symbol in any document produced (Markdown/Obsidian/KaTeX/HTML or LaTeX/PDF)."
---

# Research Brain — Intuition-First Explainer & Colored LaTeX Equations (`rb-explain`)

Turn dense mathematical, physical, or algorithmic ideas into crystal-clear explanations—assuming zero prior familiarity with the formalism first, then earning every symbol underneath with mandatory colored LaTeX annotations.

For complete worked examples (voltage shapes $l=0,1,2$, the $9 \to 6 \to 5$ counting proof, permanent multipoles vs. non-local distributed polarizabilities, unit-scale rules, real-space-to-matrix bridge, 5-spot numeric chain, and "Push → Photograph → Listen" pair-response walkthroughs), read [`references/worked-examples.md`](references/worked-examples.md).

---

## Mandatory Rule — Colored LaTeX Annotations on ALL Equations in ANY Document Produced

Every displayed equation in **any** document produced (Markdown, Obsidian notes, Wiki pages, Project Notebooks, HTML/KaTeX reports, or LaTeX/PDF papers and guides) **must** carry colored LaTeX annotations unpacking **every individual symbol and operator**—never emit bare uncolored display equations and never bundle 3–4 symbols behind one summary phrase.

Use a consistent, high-contrast semantic palette:
- **Navy** `#1B3A5C` (output / observable / total quantity)
- **Teal** `#00798C` (state / density / resting system)
- **Crimson** `#D1495B` (external perturbation / input / push)
- **Amber** `#C87D14` (operator / kernel / transformation / sum)
- **Forest** `#2E8B57` (mask / domain / measure / scaling factor)
- **Plum** `#6A4C93` (coupling / cross-term / index / constraint)

### Format A — Markdown, Obsidian, HTML & KaTeX Documents
Use explicit `\color{#hex}{...}` combined with `\underbrace{...}_{\text{...}}` and `\overbrace{...}^{\text{...}}` (alternating above/below to prevent collisions; add a 1-to-1 per-symbol table underneath if an equation has >5 symbols):

```latex
$$
\color{#1B3A5C}{\underbrace{T_p}_{\text{frozen linear rate}}}
=
-\;
\color{#C87D14}{\overbrace{\int}^{\text{sum over all 3D cubes}}}
\color{#00798C}{\underbrace{\rho_0(\mathbf{r})}_{\text{resting electron density}}}
\,
\color{#D1495B}{\overbrace{h_p(\mathbf{r})}^{\text{masked test voltage pattern}}}
\,
\color{#2E8B57}{\underbrace{d\mathbf{r}}_{\text{tiny cube volume}}}
$$
```

### Format B — LaTeX & PDF Documents
Use `\usepackage{annotate-equations}` (`\eqnmarkbox[color]{id}{term}` + `\annotate[yshift=...]{above/below,left/right}{id}{short plain label}`), reserving `\vspace*{2.2em}` before and `\vspace*{2.0em}` after and alternating above/below + left/right to avoid overlaps (compile $\ge 2$ times with `pdflatex`; fall back to `\color` + `\underbrace`/`\overbrace` only if `annotate-equations` cannot be loaded):

```latex
\vspace*{2.2em}
\begin{equation*}
  \eqnmarkbox[navy]{Tp}{T_p}
  = -\;
  \eqnmarkbox[amber]{int}{\int}
  \eqnmarkbox[teal]{rho}{\rho_0(\mathbf{r})}\,
  \eqnmarkbox[rosered]{hp}{h_p(\mathbf{r})}\,
  \eqnmarkbox[leaf]{dr}{d\mathbf{r}}
\end{equation*}
\annotate[yshift=1.2em]{above,left}{Tp}{frozen linear rate}
\annotate[yshift=1.2em]{above,right}{hp}{masked test voltage}
\annotate[yshift=-1.2em]{below,left}{rho}{resting electron density}
\annotate[yshift=-1.2em]{below,right}{dr}{tiny cube volume}
\vspace*{2.0em}
```

*Completion check:* Run `rb lint` on vault Markdown files to confirm zero uncolored display equations slip through, and inspect rendered PDFs/HTML visually for label collisions.

---

## Phase 1: Trapdoor Audit (Before Writing)

Scan the topic for eight failure modes that break intuition:
1. **Black-Box "Math Nouns":** Flag words like *potential, derivative, integrate, curvature, harmonic, CPHF, matrix, transpose, projection, equivariance, gauge, orthogonality, multipole, Laplace's equation,* or *quadratic response*. Earn every term physically (push, pull, shift, stretch, pinch, count) before naming it.
2. **Procedural Ambiguity ("What Do We Actually *Do*?"):** State explicitly what is applied in physical space, what is held fixed, and what changes.
3. **The "AND vs. OR" Trap:** Separate the **one-at-a-time Testing Phase** (tasting each basis pattern separately) from the **all-together (AND) Prediction Phase** (keeping and summing all channels).
4. **Magic Numbers & Unexplained Coefficients:** Trace every count (`9 -> 6 -> 5`) and coefficient (`2z^2 - x^2 - y^2`, `1/2`, `c^2`) to counting + symmetry + a physical conservation law.
5. **Unanchored Spatial Shapes:** Trace sign patterns edge-to-edge (`-1 -> 0 -> +1` ramp vs. `+1 -> 0 -> +1` curvature) and anchor to familiar shapes ($s, p, d$ orbitals).
6. **Bundled Equation Labels:** Unpack every individual symbol and operator in colored annotations—never wrap 3–4 symbols under one summary phrase.
7. **Silent Real-Space $\leftrightarrow$ Matrix Jumps:** Show the 3D real-space integral before bridging 1-to-1 into basis-set matrices ($\rho_0 \to \mathbf{D}_0$, $h_p \to \mathbf{h}_p$, $\int d\mathbf{r} \to \operatorname{Tr}$).
8. **Ungrounded Numbers & Mask-vs.-Slicing Traps:** Anchor numeric examples to one fixed coordinate ruler (`Input -> Procedure -> Output`), and keep nuclear masks ($w_A$) distinct from slicing an atom or weighing electron density.

---

## Phase 2: Layer 1 — Pure Physical Story (Zero Jargon)

1. **Physical Origin & Mask vs. Pattern:** State where the external influence comes from, what stays fixed (the atom's full room via mask $w_A$), and what changes (each basis pattern projected across that same full room one at a time).
2. **Edge-to-Edge Spatial Behavior:** Trace Level (uniform shift), Slope (`-1 -> 0 -> +1` sideways pull), and Curvature (`+1 -> 0 -> +1` ends vs. `-1` waist elongation/pinch), anchored to $s, p, d$ shapes.
3. **Two Tangible Physical Stages:**
   - **Step 1 — Frozen-Density Baseline / Permanent Distributed Multipoles ($\mathbf{T}$):** Freeze the equilibrium cloud; chop into tiny pieces and sum the push on each piece.
   - **Step 2 — Induced Relaxation / Non-Local Distributed Polarizabilities ($\boldsymbol{\Pi}$) via "Push $\to$ Photograph $\to$ Listen":** Beat 1 pushes with handle $p$ alone to capture moved-charge photograph ($\delta\mathbf{D}^{(p)}$); Beat 2 holds that photograph still while laying stencil $q$ over it (unifying self-squish, on-atom coupling, and cross-bond charge flow).
   - **Step 3 — Prediction (AND + $c^2$ Scaling):** Double the push $\rightarrow$ twice the induced charge shift *and* twice the pull on it ($2 \times 2 = 4$).
4. **Why Unit Scale $= 1$ Suffices:** Use the **"Price of 1 Apple" Rule** (linear baseline) and **"Spring Stiffness" Rule** (quadratic induction).
5. **One Running Numeric Chain:** Feed the literal numerical output of Step $k$ as input to Step $k+1$ on one fixed coordinate ruler.

---

## Phase 3: Layer 2 — Counting, Conservation Constraints & Dual-Scale Units

1. **Three-Step Dimension Derivation:** Raw combinatorial grid (`3x3 = 9`) $\to$ algebraic symmetry (`xy = yx` gives `6`) $\to$ physical conservation rule (Sealed Water Balloon / Laplace $\nabla^2 V = 0$ gives `5`, and explains coefficients like `+2 - 1 - 1 = 0`).
2. **Dual-Scale Units Table:** Map physical meaning, everyday units ($\text{V}, \text{V/\AA}, \text{V/\AA}^2$), domain/natural units ($\text{Ha}/e$, etc.), and what "1 unit" means physically.

---

## Phase 4: Layer 3 — Two-Stage Formal Bridge (Real Space $\to$ Matrices)

1. **Real-Space Colored Equation First:** Display the 3D real-space expression with mandatory per-symbol colored LaTeX annotations (Format A or B above).
2. **Explicit 1-to-1 Matrix/Basis Bridge:** Map every real-space object directly to its basis-set/matrix symbol ($\rho_0 \leftrightarrow \mathbf{D}_0$, $h_p \leftrightarrow \mathbf{h}_p$, $\int d\mathbf{r} \leftrightarrow \operatorname{Tr}$), then display the matrix equation with mandatory per-symbol colored LaTeX annotations.

---

## Phase 5: Framing a Methodological Pivot ("Old Way vs. New Way")

1. **Honor the Old Method First:** State why it seemed natural for a static snapshot.
2. **Concrete Physical Breakdowns:** Show exact physical failure scenarios (not abstract critique).
3. **Plain Contrast of the New Mechanism:** State clearly what moved and what replaced what.
4. **30-Second Spoken Takeaway:** End with one memorable, jargon-free paragraph ready to deliver verbally.
