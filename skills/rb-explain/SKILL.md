---
name: rb-explain
description: "Explain theoretical concepts, physical mechanisms, quantum chemistry or mathematical derivations, presentation Q&A prep, or methodological pivots ('old way vs. new way') using pure physical intuition first, then bridging to formal equations. Enforces: (1) a Markdown `## Reference Table` in every document defining EVERY mathematical symbol (inline and displayed) and EVERY new technical concept/method/acronym (e.g., WHAM, MBAR, FCD, GMH, TDA, umbrella sampling) before or at first use, (2) mandatory colored LaTeX per-symbol annotations on every displayed equation, (3) zero flippant parentheticals, orphan ratios, or bare 'unphysical' labels, and (4) strict provenance tags on every technical, qualitative, and quantitative claim."
---

# Research Brain — Intuition-First Explainer & Colored LaTeX Equations (`rb-explain`)

Turn dense mathematical, physical, or algorithmic ideas into crystal-clear explanations—assuming zero prior familiarity with the formalism first, earning every mechanism, method, and symbol transparently, and eliminating noise and unsourced claims.

For complete worked examples (voltage shapes $l=0,1,2$, the $9 \to 6 \to 5$ counting proof, permanent multipoles vs. non-local distributed polarizabilities, unit-scale rules, real-space-to-matrix bridge, 5-spot numeric chain, and "Push → Photograph → Listen" pair-response walkthroughs), read [`references/worked-examples.md`](references/worked-examples.md).

---

## Mandatory Document Standards (Apply to EVERY Markdown / Document Produced)

### 1. Markdown `## Reference Table` — Zero Undefined Symbols & Zero Unexplained New Ideas
Every unexplained symbol (`$f_B$`, `$\mu_B$`) or unexplained technical method/phrase (*"multi-walker distance umbrella sampling"*, `WHAM`, `MBAR`, `FCD`, `GMH`, `TDA`) is **noise** that slows assimilation.

- **Include a complete `## Reference Table` at the top of EVERY technical Markdown document** (easy to pin in an Obsidian side split-pane while scrolling) covering:
  1. **100% of mathematical symbols** used anywhere on the page—**both inline (`$f_B$`, `$\mu_B$`) AND displayed (`$$...$$`)**—with their exact matching equation colors.
  2. **100% of new technical concepts, algorithms, methods, and acronyms** introduced on the page (e.g., `WHAM`, `MBAR`, `FCD`, `GMH`, `TDA`, *"multi-walker distance umbrella sampling"*).
  ```markdown
  ## Reference Table (Symbols & Terms)
  | Symbol / Term | Color | Plain-English Physical / Operational Meaning | Units / Scope & Limitations |
  | :--- | :--- | :--- | :--- |
  | $\color{#1B3A5C}{T_p}$ | `#1B3A5C` | Frozen-density linear response rate for test pattern $p$ | $\text{Ha}/(\text{unit } p)$ |
  | **WHAM** (Weighted Histogram Analysis Method) | — | Reweights overlapping biased simulation windows into one unbiased free-energy curve | Requires binned histograms; sensitive to bin width |
  ```
- **Rule for every sentence introducing a new idea:** Whenever a sentence names any new concept, sampling protocol, method, or acronym (e.g., *"multi-walker distance umbrella sampling"*, *"WHAM / MBAR"*), you MUST explain what it physically/operationally means **before the sentence**, **inside the sentence itself**, OR **in the Markdown `## Reference Table`**—otherwise cut it instead of producing noise.

### 2. Colored LaTeX Per-Symbol Annotations on ALL Displayed Equations
Every displayed equation in **any** document produced (Markdown, Obsidian, Wiki, Notebook, or LaTeX/PDF) **must** carry colored LaTeX annotations unpacking **every individual symbol and operator**—never emit bare uncolored display equations and never bundle 3–4 symbols behind one summary phrase.

Consistent high-contrast semantic palette (matching the `## Reference Table` 1-to-1):
- **Navy** `#1B3A5C` — output / observable / target coupling
- **Teal** `#00798C` — state / density / resting system
- **Crimson** `#D1495B` — external perturbation / input / push / bridge contamination
- **Amber** `#C87D14` — operator / kernel / sum / transformation
- **Forest** `#2E8B57` — domain / mask / measure / scaling ratio
- **Plum** `#6A4C93` — coupling / index / cross-term / constraint

- **Markdown / Obsidian / KaTeX (`\color` + `\underbrace`/`\overbrace`, alternating above/below):**
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
- **LaTeX / PDF (`\usepackage{annotate-equations}`):** Use `\eqnmarkbox[color]{id}{term}` + `\annotate[yshift=...]{above/below,left/right}{id}{short plain label}` with `\vspace*{2.2em}` before and `\vspace*{2.0em}` after (compile $\ge 2\times$ with `pdflatex`).

### 3. Strict Provenance on ALL Technical, Qualitative & Quantitative Claims (`rb-cite`)
Explanatory documents are **never** exempt from `rb-cite`. Every factual technical, qualitative (*"barely changes"*, *"prevents collapse"*), or quantitative (*"$|H_{\text{eff}}| = 8.96 \times 10^{-7}\text{ eV}$"*, *"$< 10\%$ effect"*, *"ratio $0.193$"*) claim must carry an inline provenance tag in the same paragraph:
- Primary literature → verbatim quote + `[@source-id, p.X, L.Y]`
- Local computation / script / output → `[calc: path/to/script.py]` or `[worklog: YYYY-MM-DD]`
- Synthetic teaching illustration → `[example]` (clearly labeled synthetic)
- Unverified working assertion → `[UNVERIFIED]`

### 4. Anti-Flippancy & Earned Explanations (Zero Breezy Shorthand)
- **Zero unexplained acronyms or methods in prose OR tables:** Spell out every acronym (e.g., `FCD`, `GMH`, `TDA`, `WHAM`, `MBAR`) on first mention and inside comparison tables, state what it physically computes, and state explicitly **which failure mode it fixes AND what it still does NOT fix** (e.g., whether `FCD` fixes bridge-mediated mixing or shares the same limitation).
- **Zero breezy parentheticals:** Never compress a complex physical instability or algorithmic safeguard into a flippant parenthetical (e.g., *"stopping fake low-energy collapse"*). State the physical cause and consequence cleanly in plain prose.
- **Zero unexplained ratios or dual numbers:** Whenever quoting a ratio or paired variants (e.g., `0.193` vs. `20.34 / 77.77 = 0.262`), explicitly state (1) what the numerator is physically, (2) what the denominator is physically, (3) why the two variants differ (e.g., projected vs. full norm), and (4) what threshold makes that magnitude physically decisive.
- **Separate real physics from mathematical artifacts:** Never dismiss a plausible physical mechanism with a bare label (*"unphysical"*, *"fake"*). Whenever a reader could reasonably ask *"Wait—couldn't that third residue/intermediate genuinely participate?"*, explicitly split **(a) what IS physically real** (e.g., genuine bridge mixing / superexchange mediation) from **(b) what specifically breaks the formula** (e.g., projecting a 3-state dipole through a 2-state formula introduces a mathematical distortion/sign flip that does not equal the true physical coupling).

---

## Phase 1: Trapdoor Audit (Before Writing)

Scan the topic for 12 failure modes before drafting:
1. **Black-Box "Math Nouns":** Flag words like *potential, derivative, integrate, curvature, harmonic, CPHF, TDA, FCD, GMH, WHAM, MBAR, umbrella sampling, projection, equivariance, gauge, multipole*. Earn every term physically before naming it.
2. **Procedural Ambiguity ("What Do We Actually *Do*?"):** State explicitly what is applied, held fixed, or varied.
3. **The "AND vs. OR" Trap:** Separate the one-at-a-time Testing Phase from the all-together (AND) Prediction Phase.
4. **Magic Numbers & Unexplained Coefficients:** Trace every count (`9 -> 6 -> 5`) and factor (`2z^2 - x^2 - y^2`, `1/2`, `c^2`) to counting + symmetry + a conservation law.
5. **Unanchored Spatial Shapes:** Trace sign patterns edge-to-edge (`-1 -> 0 -> +1` vs. `+1 -> 0 -> +1`) and anchor to familiar shapes ($s, p, d$).
6. **Bundled Equation Labels:** Unpack every individual symbol and operator in colored LaTeX annotations.
7. **Silent Real-Space $\leftrightarrow$ Matrix Jumps:** Show the 3D real-space integral before bridging 1-to-1 into orbital/matrix notation.
8. **Ungrounded Numbers & Mask-vs.-Slicing Traps:** Anchor numeric chains to one coordinate ruler (`Input -> Procedure -> Output`), and separate nuclear masks ($w_A$) from density weighting or slicing.
9. **Undefined Inline Symbols & Unexplained New Ideas:** Audit every inline symbol (`$f_B$`, `$\mu_B$`, `$^3\text{FMN}^*$`) AND every specialized concept/method/acronym (`WHAM`, `MBAR`, *"multi-walker distance umbrella sampling"*) — each must be explained before/inside the sentence or listed in the Markdown `## Reference Table`.
10. **Unexplained Acronyms & Unscoped Method Tables:** Ensure every method in a comparison table defines both what it physically computes and which exact failure mode it fixes vs. leaves unfixed.
11. **Flippant Parentheticals & Orphan Ratios:** Expand every compressed technical parenthetical and unpack numerator, denominator, variant differences, and physical significance of every ratio.
12. **Bare "Unphysical" Labels & Uncited Claims:** Replace every hand-waved *"unphysical"* with the real-physics vs. formula-artifact split, and attach provenance (`[@id, p.X]`, `[calc: ...]`, `[worklog: ...]`, `[example]`, or `[UNVERIFIED]`) to every technical, qualitative, and quantitative claim.

---

## Phase 2: Layer 1 — Pure Physical Story (Zero Jargon)

1. **Physical Origin & Mask vs. Pattern:** State where the influence comes from, what stays fixed, and what changes.
2. **Edge-to-Edge Spatial Behavior:** Trace Level, Slope (`-1 -> 0 -> +1`), and Curvature (`+1 -> 0 -> +1` vs. `-1` waist), anchored to $s, p, d$ shapes.
3. **Two Tangible Physical Stages:** Separate Frozen Baseline ($\mathbf{T}$) from Induced Relaxation ($\boldsymbol{\Pi}$) via **"Push $\to$ Photograph $\to$ Listen"**, then explain Prediction (AND + $c^2$ double scaling).
4. **Unit Scale $= 1$ Rules:** Use the **"Price of 1 Apple" Rule** (linear) and **"Spring Stiffness" Rule** (quadratic).
5. **One Continuous Numeric Chain:** Feed the literal numerical output of Step $k$ as input to Step $k+1$ on one fixed coordinate ruler (tagged `[example]` if synthetic, or `[calc: ...]` if real).

---

## Phase 3: Layer 2 — Counting, Conservation Constraints & Dual-Scale Units

1. **Three-Step Dimension Derivation:** Raw combinatorial grid $\to$ algebraic symmetry $\to$ physical conservation rule (explaining every count and coefficient).
2. **Dual-Scale Units Table:** Map physical meaning, everyday units, natural/domain units, and what "1 unit" means physically.

---

## Phase 4: Layer 3 — Two-Stage Formal Bridge (Real Space $\to$ Matrices)

1. **Real-Space Colored Equation First:** Show the 3D real-space expression with mandatory per-symbol colored LaTeX annotations matching the Markdown `## Reference Table`.
2. **Explicit 1-to-1 Matrix/Basis Bridge:** Map every real-space piece to its matrix/basis counterpart ($\rho_0 \leftrightarrow \mathbf{D}_0$, $h_p \leftrightarrow \mathbf{h}_p$, $\int d\mathbf{r} \leftrightarrow \operatorname{Tr}$), then display the colored annotated matrix equation.

---

## Phase 5: Framing a Methodological Pivot ("Old Way vs. New Way")

1. **Honor the Old Method First:** Explain why it worked for its original regime.
2. **Concrete Physical Breakdowns (Real Physics vs. Formula Artifact):** Show exact physical scenarios where the old formula fails, separating real physical effects from mathematical artifacts.
3. **Plain Contrast & Honest Scope of the New Method:** State clearly what moved/replaced what, AND state explicitly which failure modes the new method fixes vs. which limitations remain.
4. **30-Second Spoken Takeaway:** End with one memorable, jargon-free paragraph ready to deliver verbally.

---

## Completion Verification (Before Delivering Any Document)
Run `rb lint <file.md>` to deterministically verify verbatim quotes, colored display equations, `## Reference Table` presence, defined acronyms, and quantitative claim provenance.
