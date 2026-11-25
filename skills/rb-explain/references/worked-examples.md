# Worked Examples: Intuition-First Theory Explanations

Use these eight gold-standard reference patterns when preparing explanations, derivations, or presentation Q&A answers under the `intuition-first-explainer` skill.

---

## Worked Example A: Voltage, Level ($l=0$), Slope ($l=1$), and Curvature ($l=2$)

### 1. Where Does Voltage Come From, and What Does Applying It Mean?
- In real life, a molecule is surrounded by neighboring atoms—water molecules, amino acids in a protein, or metal ions like $\text{Mg}^{2+}$.
- Every neighbor carries positive or negative electric charge, reaching across space to pull or push on our molecule's electrons:
  - A **positive** neighbor creates a region of **positive voltage** (an electron wants to go there).
  - A **negative** neighbor creates a region of **negative voltage** (an electron gets pushed away from there).
- **So "voltage" at any spot is simply:** *how strongly the outside environment attracts ($+$) or repels ($-$) an electron at that exact spot.*
- **Do we put a $1e$ point charge at the center of Atom A?** **No!** A point charge at the center would blow up to infinity right at the nucleus ($1/r \to \infty$ as $r \to 0$). Instead, the external charges sit *outside* Atom A, so inside Atom A's 3D space the voltage is **smooth**. We project all smooth 3D test voltage patterns across Atom A's full neighborhood one at a time, using Atom A's nuclear-only Becke fade-out mask $w_A(\mathbf{r})$ strictly to turn the test voltage smoothly to $0$ on neighboring atoms (never weighing electron density and never slicing Atom A into smaller sub-volumes).

### 2. Edge-to-Edge Physical Traces Across Atom A
Imagine Atom A's electron cloud as a fuzzy ball centered on its nucleus:

- **Level ($l=0$) — Everywhere feels the same voltage:**
  $$\text{Left edge: } +1\text{ V} \quad\longrightarrow\quad \text{Center: } +1\text{ V} \quad\longrightarrow\quad \text{Right edge: } +1\text{ V}$$
  Because left and right feel the exact same pull, the cloud doesn't slide sideways; instead, the whole atom becomes a more attractive place for electrons (matching $s$-like density gain/loss along bonds).

- **Slope ($l=1$) — One side is $-$, the opposite side is $+$:**
  $$\text{Left edge: } -1\text{ V} \quad\longrightarrow\quad \text{Center: } 0\text{ V} \quad\longrightarrow\quad \text{Right edge: } +1\text{ V}$$
  Plotting $-1 \to 0 \to +1$ is a straight tilted ramp. Electrons on the left ($-1\text{ V}$) are repelled right; electrons on the right ($+1\text{ V}$) are pulled further right. So the whole cloud **shifts sideways** (tested along $x$, $y$, and $z$—matching $p_x, p_y, p_z$ orbital shapes).

- **Curvature ($l=2$) — Both ends pull outward while the waist pinches inward:**
  Trace left-to-right alongside front-to-back across Atom A:
  $$\text{Left edge: } +1\text{ V} \quad\longrightarrow\quad \text{Center: } 0\text{ V} \quad\longrightarrow\quad \text{Right edge: } +1\text{ V}$$
  $$\text{Front edge: } -1\text{ V} \quad\longrightarrow\quad \text{Center: } 0\text{ V} \quad\longrightarrow\quad \text{Back edge: } -1\text{ V}$$
  - $+1 \to 0 \to +1$ is a U-shaped curve ($+x^2$), while $-1 \to 0 \to -1$ is an upside-down U-curve ($-y^2$).
  - Because *both* left and right pull equally outward, the cloud's center does not slide sideways; instead, **the cloud stretches fatter along left-right and pinches skinnier along front-back** (matching $d$-orbital / quadrupole lobes).
  - **Crucial insight:** Even a *single* nearby ion creates curvature across Atom A, because $1/\text{distance}$ is a curved graph—steeper on the near edge of Atom A's cloud than on the far edge. Breaking that curve into pieces gives average Level ($l=0$) + average straight Slope ($l=1$) + the bend/Curvature ($l=2$).

---

## Worked Example B: Counting Proof — Why $9 \to 6 \to 5$ Curvature Patterns and Why the "$2$" in $2z^2 - x^2 - y^2$

### 1. From 9 Pairs to 6 Quadratic Building Blocks
To write every possible quadratic (degree-2) voltage curve around Atom A at $(0,0,0)$, pick two coordinates from $(x,y,z)$ and multiply them in a $3 \times 3$ grid:
$$
\begin{pmatrix}
x^2 & xy & xz \\
yx & y^2 & yz \\
zx & zy & z^2
\end{pmatrix}
$$
- **9 total slots** $\to$ because $xy = yx$, $xz = zx$, and $yz = zy$, the lower-left duplicates the upper-right, leaving **6 unique blocks**:
  - 3 axial terms: $x^2, y^2, z^2$
  - 3 diagonal cross terms: $xy, xz, yz$

### 2. Why Electrostatics Kills 1 of the 6: The "Sealed Water Balloon" Rule
Suppose someone tries to build an all-around bowl $V(x,y,z) = x^2 + y^2 + z^2$ curving upward in every direction at once:
- Electric field arrows flow from high voltage to low voltage. If voltage curved upward along $\pm x$, $\pm y$, and $\pm z$ simultaneously, field lines would converge **inward toward $(0,0,0)$ from all directions in 3D space at once**.
- By Gauss's Law, field lines can only converge on a point if there is an external charge sitting **right at $(0,0,0)$** acting as a drain. Since all environment charges are *outside* Atom A, field lines behave like **incompressible water in a sealed balloon**: whatever pushes in along one axis *must* bulge out along another.
- Mathematically, that rule is Laplace's equation: $V_{xx} + V_{yy} + V_{zz} = 0$ (the three axial curvatures must sum to zero). That kills the $x^2 + y^2 + z^2$ bowl, leaving $6 - 1 = \mathbf{5}$ independent curvature patterns:
  1. $2z^2 - x^2 - y^2$: Compares the $z$-axis against the $xy$-waist equally. If $x^2$ gets weight $-1$ and $y^2$ gets weight $-1$, $z^2$ **must** get weight $+2$ so $+2 - 1 - 1 = 0$! (Top/bottom poles $+$, equatorial donut belt $-$.)
  2. $x^2 - y^2$: Weights $+1 - 1 + 0 = 0$. ($+$ along $\pm x$, $-$ along $\pm y$; on-axis 4-leaf clover.)
  3. $xy$: Axial curvatures $0+0+0=0$; diagonal $45^\circ$ clover in the $xy$-plane.
  4. $xz$: Diagonal $45^\circ$ clover in the $xz$-plane.
  5. $yz$: Diagonal $45^\circ$ clover in the $yz$-plane.

### 3. All 9 Questions Per Atom Explicit ($1 + 3 + 5 = 9$ for $l_{\max}=2$)
1. **Level ($l=0$, 1 question):** Uniform shift ($1$).
2. **Slopes ($l=1$, 3 questions):** $x$-slope ($x$), $y$-slope ($y$), $z$-slope ($z$).
3. **Curvatures ($l=2$, 5 questions):** $2z^2 - x^2 - y^2$, $x^2 - y^2$, $xy$, $xz$, $yz$.
*(Extending to $l=3$ adds $2(3)+1 = 7$ octupole patterns for $1+3+5+7=16$ per atom, following $(l_{\max}+1)^2$.)*

---

## Worked Example C: The 3-Step Experimental Procedure (AND vs. OR + Permanent vs. Induced)

### 1. Fixing the "AND vs. OR" Trap: The 9 Spices Analogy
We use **ALL 9** patterns (**AND**, never OR). Why do explanations accidentally sound like "OR"? Because of **how you test**:
- To learn how 9 spices taste, you taste them **one at a time, separately** during the **Testing Phase** so they don't blur together.
- When cooking a real meal (the **Prediction Phase**), a protein pushes in all 9 ways at once—so you keep **ALL 9 results** and add them together.

### 2. Three Plain-English Steps
- **Step 1 — Frozen Cloud / Permanent Distributed Multipoles ($\mathbf{T}$):** Hold the resting electron cloud fixed in its unperturbed equilibrium shape so it cannot rearrange yet. Lay each of the 9 test pushes across Atom A's cloud, chop the cloud into tiny pieces, and add up the push on every piece (this is all *"integrate"* means). Even when frozen, an already-lopsided cloud feels an immediate electrostatic energy shift. Save **9 permanent multipole numbers**.
- **Step 2 — Induced Relaxation / Non-Local Distributed Polarizabilities ($\boldsymbol{\Pi}$):** Release the frozen constraint so the cloud can respond elastically: feed the same 9 unit pushes into the quantum response solver (CPHF / CPKS) to measure how charge polarizes locally on Atom A *and* flows across bonds to other atoms. Save a **$9 \times 9$ distributed polarizability lookup table** (in conceptual DFT, the atom-projected static linear response kernel $\chi$).
- **Step 3 — Prediction in Any Real Environment:**
  1. Measure the real neighbor's 9 push strengths $\mathbf{c}$ right now.
  2. Multiply each by its **Step 1 permanent multipole number** ($\mathbf{T}$) and sum for permanent electrostatics.
  3. Multiply each box in the **Step 2 distributed polarizability table** ($\boldsymbol{\Pi}$) by the neighbor's push strength **twice** ($c_i \times \Pi_{ij} \times c_j$) for induction. Why twice? Because pushing **twice as hard** induces **twice as much charge shift/flow** *AND* makes the neighbor pull on that newly shifted charge **twice as hard** ($2 \times 2 = 4$).

---

## Worked Example D: Why Testing Unit Strength $= 1$ Once Covers Every Scale ($1, 2, 3, \dots$)

We **never** loop over magnitudes $1, 2, 3, \dots$ during compilation. One test at unit scale $= 1$ for each of the 9 patterns covers every voltage scale automatically:
1. **For the Frozen Cloud ($\mathbf{T}$) — The "Price of 1 Apple" Rule:** Asking *"How much does 1 apple cost?"* (\$2/apple) lets you compute 2 apples (\$4), 3 apples (\$6), or $-1.5$ apples (-\$3) by multiplying.
2. **For Induced Polarization ($\boldsymbol{\Pi}$) — The "Spring Stiffness" Rule:** Testing an elastic spring with **1 unit of push** measures its response once. The law of linear response guarantees induced energy scales as $\text{strength}^2$: scale $1 \to 1\times$, scale $2 \to 4\times$, scale $3 \to 9\times$.

Combining both:
$$\text{Total Effect} = (\text{Permanent Baseline for Scale } 1) \times c \;+\; \frac{1}{2}(\text{Polarizability Response for Scale } 1) \times c^2$$

---

## Worked Example E: Physical Units & 1-to-1 Symbol Translation Cheat Sheet

### 1. Dual-Scale Units Table

| Order | Physical Meaning | Everyday Units | Atomic Units (Code) | What "1 Unit" Means Physically |
| :--- | :--- | :--- | :--- | :--- |
| **$l = 0$** | **Voltage Level** | $\text{V}$ | $\text{Ha} / e$ | Shifting baseline voltage uniformly by $1\text{ Ha}/e$ ($\approx 27.2\text{ V}$) |
| **$l = 1$** | **Voltage Slope** *(Electric Field)* | $\text{V} / \text{\AA}$ | $\text{Ha} / (e \cdot \text{Bohr})$ | Ramp changing by $1\text{ Ha}/e$ per $1\text{ Bohr}$ along $x$, $y$, or $z$ |
| **$l = 2$** | **Voltage Curvature** *(Field Gradient)* | $\text{V} / \text{\AA}^2$ | $\text{Ha} / (e \cdot \text{Bohr}^2)$ | Saddle whose slope changes by $1\text{ Ha}/(e\cdot\text{Bohr})$ per Bohr |

### 2. The 1-to-1 Plain-English Translation Cheat Sheet

| Formal Symbol / Term | Plain-English Physical Meaning |
| :--- | :--- |
| **$\int \cdots d\mathbf{r}$ ("Integrate over the cloud")** | Chop the 3D electron cloud into tiny pieces and add up the push on all the pieces |
| **$w_A(\mathbf{r})$ ("Becke weight")** | Nuclear-only dimmer mask ($0 \to 1$) that keeps a voltage pattern ON across Atom A's full room and fades it to $0$ on neighboring atoms (never weighs electron density and never slices Atom A into sub-rooms) |
| **$R_{lm}(\mathbf{r} - \mathbf{R}_A)$ ("Solid harmonics")** | The 9 clean unit test patterns ($1$; $x,y,z$; and the 5 Laplace-allowed $l=2$ saddles) |
| **$\mathbf{T}$ ("1st Derivative / Permanent Distributed Multipoles")** | List of **9 frozen-cloud numbers** (Step 1, MRK Frozen Linear Response): permanent sensitivity *before* electrons rearrange |
| **$\boldsymbol{\Pi}$ ("2nd Derivative / Non-Local Distributed Polarizabilities")** | The **$9 \times 9$ distributed polarizability matrix** (Step 2, static linear response kernel $\chi$ / MRK Relaxed Polarizability): local polarization + interatomic charge-flow |
| **CPHF / CPKS Equation** | The quantum response solver computing how orbitals polarize and transfer charge under push |
| **$\mathbf{c}$ ("Multipole field coefficients")** | The **9 strength numbers** describing how hard a real neighbor pushes right now |
| **$\frac{1}{2}\mathbf{c}^T \boldsymbol{\Pi} \mathbf{c}$** | Induction energy: multiplying the polarizability matrix by the push strength **twice** (induced charge shift $\times$ pull on that shifted charge) |

---

## Worked Example F: Framing the Methodological Pivot — Distributed vdW Surface Points vs. Atom-Centered Operators

### 1. Honor the Old Way First (Pure Idea)
Previously, we drew an imaginary bubble around the molecule—the van der Waals (vdW) surface—and scattered hundreds of sample dots across it, like putting tiny weather stations on a dome around a house. Whenever outside charges moved, we read the voltage at those outer dots and translated those surface readings into how the molecule inside would react.

### 2. Concrete Physical Breakdowns of Outer Surface Dots
1. **The Shell Tears When the Molecule Moves:** Our surface bubble is built by gluing spheres around each atom and deleting points where spheres overlap. The moment a bond bends or stretches, spheres overlap differently: **dots pop in and out of existence**. If your response manual expects 180 dots and one microsecond later a vibration leaves 176 dots, the math breaks or jolts discontinuously.
2. **Dots Fight Symmetry and Each Other:** A scattered cloud of dots on a surface doesn't rotate cleanly with the molecule; tilting a symmetric molecule places the grid in slightly different spots relative to the atoms. Worse, neighboring dots sit so close together that they fight to explain the same electric field, creating numerical noise.
3. **A Hollow Outer Skin Has a Blind Spot Inside:** A surface shell assumes all electrons stay inside the shell and all neighbors stay outside. Real electron clouds have fuzzy tails that spill past the shell, and nearby ions or hydrogen bonds push right into that boundary. Measuring only on a 2D skin misses how the field penetrates the 3D electron volume.

### 3. The New Physical Mechanism (Zero Jargon)
Instead of scattering fragile dots on a hollow outer skin, we move our sensors **directly onto the atoms themselves** and replace "points" with **9 fundamental 3D voltage patterns per atom** (1 Level, 3 Slopes, 5 Curvatures—tested separately at unit scale $= 1$, kept together as **AND**):
- **Nothing disappears when atoms vibrate:** Every atom always owns the exact same 9 shape-dials, whether bonds stretch or bend.
- **Rotation is exact:** Tilts ($p$-like) and curvatures ($d$-like) transform cleanly into mixtures of each other under any rotation with zero re-meshing error.
- **No hollow wall:** Each atom's 9 patterns act directly over its smooth 3D share of the real electron cloud ($w_A(\mathbf{r})$).

### 4. Bridge to the Theory Underneath
- **Old Way (BEM Collocation):** Discretized vdW spheres $\{\mathbf{s}_q\} \to$ solve $\tilde{\mathbf{q}} = \mathbf{A}^{-1}\boldsymbol{\phi}$ $\to$ ill-conditioned $1/|\mathbf{r}-\mathbf{s}_q|$ perturbations in CPKS.
- **New Way ($|A,l,m\rangle$ Operators):** Smooth Becke partition $\sum_A w_A(\mathbf{r}) = 1$ $\to$ perturbation operators $(\hat{h}_{A,lm})_{\mu\nu} = -\int w_A(\mathbf{r}) R_{lm}(\mathbf{r}-\mathbf{R}_A)\chi_\mu(\mathbf{r})\chi_\nu(\mathbf{r})\,d\mathbf{r}$ $\to$ exact $O(3)$ Wigner $D^{(l)}(\mathbf{Q})$ equivariance, smooth analytic forces for molecular dynamics, compact full-rank CPKS response, and exact constant-potential gauge ($\sum_A \hat{h}_{A,00} = -\mathbf{S}$).

### 5. 30-Second Spoken Takeaway
> *"Previously, we painted hundreds of dots on a hollow shell around the molecule. That works for a frozen statue, but the second a molecule vibrates or rotates, overlapping spheres pop dots in and out of existence, breaking symmetry and forces. By generating **operators**, we throw away the fragile outer shell and build 9 fixed 3D shape-dials—1 level, 3 slopes, 5 curvatures—directly into each atom's share of the electron cloud. Nothing ever vanishes when the molecule moves, and rotation becomes mathematically exact."*

---

## Worked Example G: One Running Numeric Chain & Real-Space-to-Matrix Bridge ($\text{H}_2\text{CO}$ `C=O` Ruler)

Use this pattern whenever you explain spatial handles $h_p(\mathbf{r}) = w_A(\mathbf{r})\,R_{\ell m}(\mathbf{r} - \mathbf{R}_A)$ and the frozen integral $\operatorname{Tr}(\mathbf{D}_0 \mathbf{h}_p)$ so every number flows sequentially (`Input → Procedure → Output`) without gaps.

### 1. Fixed 5-Spot Ruler Along Formaldehyde's $\text{C=O}$ Axis
Anchor every calculation step to five explicit positions along one line:
- **Hydrogens:** `-0.6 Å`
- **Carbon:** `0.0 Å`
- **C=O Bond Midpoint:** `+0.6 Å`
- **Oxygen:** `+1.2 Å`
- **Oxygen Outer Edge:** `+2.0 Å`

Goal: Build the Oxygen $z$-ramp handle ($+1$ per $\text{\AA}$ to the right of Oxygen) and compute Oxygen's frozen energy slope $T_p^{(\mathrm{gse})}$.

### 2. Running `Input → Procedure → Output` Chain
- **Step 1 — Raw slope $R_{1,z}$:** Input = spot position $z$ and Oxygen position `1.2 Å`. Procedure = subtract `z - 1.2`. Output = `+0.8` (`+2.0 Å`), `0.0` (`+1.2 Å`), `-0.6` (`+0.6 Å`), `-1.2` (`0.0 Å`), `-1.8` (`-0.6 Å`). *(Notice why masking is mandatory: left unmasked, Oxygen's intended ramp blows up larger on Carbon `-1.2` and Hydrogen `-1.8` than on Oxygen `+0.8`!)*
- **Step 2 — Nuclear-only fade-out mask $w_{\mathrm{O}}(\mathbf{r})$:** Input = nuclear coordinates only. Procedure = read how exclusively each spot belongs to Oxygen (`1.00` nearest O $\to$ `0.50` midpoint $\to$ `0.00` over C and H). *(Every shape $s, p, d, f$ on Oxygen uses this exact same full-room mask—never slicing Oxygen into 16 wedges and never weighing electron density.)*
- **Step 3 — Multiply (`raw slope × w_O`) to form $h_p(\mathbf{r})$:** Output = `(+0.8)(1.00) = +0.80` (`+2.0 Å`), `(0.0)(1.00) = 0.00` (`+1.2 Å`), `(-0.6)(0.50) = -0.30` (`+0.6 Å`), `(-1.2)(0.00) = 0.00` (`0.0 Å`), `(-1.8)(0.00) = 0.00` (`-0.6 Å`). *(And far out in empty vacuum past Oxygen, $w_{\mathrm{O}} = 1$ stays harmless because resting electron density $\rho_0 \to 0$ there.)*
- **Step 4 — Frozen energy sum $T_p^{(\mathrm{gse})}$ (`slice charge × voltage`):** Multiply each cube's negative resting charge ($-\rho_0(\mathbf{r})\,d\mathbf{r}$) by Step 3's final voltage and sum:

| Spot on Ruler | Electron Charge in Slice ($-\rho_0\,d\mathbf{r}$) | Final Oxygen Voltage $h_p$ | Slice Energy (`charge × voltage`) |
| :--- | :---: | :---: | :---: |
| O outer edge (`+2.0 Å`) | `-0.10` | `+0.80` | **`-0.080`** |
| O center (`+1.2 Å`) | `-0.50` | `0.00` | **`0.000`** |
| Midpoint (`+0.6 Å`) | `-0.20` | `-0.30` | **`+0.060`** |
| Carbon (`0.0 Å`) | `-0.50` | `0.00` | **`0.000`** |
| Hydrogens (`-0.6 Å`) | `-0.15` | `0.00` | **`0.000`** |

Sum of last column: `-0.080 + 0.000 + 0.060 + 0.000 + 0.000 =` **`-0.020`** $= T_p^{(\mathrm{gse})}$.

### 3. Two-Stage Bridge From Real Space to Matrix Code
1. **Real-space integral first (every symbol unpacked):**
   $$-\int \rho_0(\mathbf{r})\,h_p(\mathbf{r})\,d\mathbf{r}$$
   - $-\rho_0(\mathbf{r})$: negative electron charge per unit volume at spot $\mathbf{r}$.
   - $d\mathbf{r}$: tiny 3D cube volume at spot $\mathbf{r}$.
   - $-\rho_0(\mathbf{r})\,d\mathbf{r}$ together: the electron charge slice inside that one cube (`-0.10`, `-0.50`, `-0.20`).
   - $h_p(\mathbf{r})$: localized test voltage at that cube (`+0.80`, `0.00`, `-0.30`).
   - $\int$: sum `charge × voltage` over all 3D cubes.
2. **Orbital-basis matrix bridge second ($\operatorname{Tr}(\mathbf{D}_0\mathbf{h}_p)$):**
   - **$\mathbf{D}_0$** is *not* cube volume—it is the resting **orbital-overlap charge recipe** giving how much electron charge sits in overlap pair $(\mu,\nu)$.
   - **$\mathbf{h}_p$** is *where* the 3D cube chopping and summation actually happen: $(\mathbf{h}_p)_{\mu\nu} = -\int \chi_\mu(\mathbf{r})\,h_p(\mathbf{r})\,\chi_\nu(\mathbf{r})\,d\mathbf{r}$ = energy felt by 1 unit of charge in overlap $(\mu,\nu)$.
   - **$\operatorname{Tr}(\mathbf{D}_0\mathbf{h}_p) = \sum_{\mu,\nu}(\mathbf{D}_0)_{\mu\nu}(\mathbf{h}_p)_{\mu\nu}$** multiplies `(resting charge in pair μ,ν) × (energy per charge in pair μ,ν)` and sums over all pairs—returning the exact same `-0.020` sum.

---

## Worked Example H: Untangling Second-Order Pair Response ($\Pi_{pq}$) via "Push $\to$ Photograph $\to$ Listen"

Never describe $\Pi_{pq}$ as putting two spherical harmonics onto the molecule at once. Present it as **two clean sequential beats** using one single moved-charge photograph:

1. **Beat 1 (Push with $p$ alone $\to$ Moved-Charge Photograph $\delta\mathbf{D}^{(p)}$):** Turn on **only** handle $p$ at unit strength (`= 1`) and unfreeze the entire delocalized electron cloud (CPKS solves the orbital twist $\mathbf{U}^{(p)}$). Freeze the resulting density shift $\delta\mathbf{D}^{(p)}$ as a photograph showing where electrons piled up ($+$) and drained away ($-$).
2. **Beat 2 (Hold the photograph still $\to$ Lay measuring stencil $q$ over it):** With **zero second push**, lay any stencil $h_q$ over that single photograph and compute $\Pi_{pq} = \operatorname{Tr}(\delta\mathbf{D}^{(p)}\mathbf{h}_q)$:
   - **Same atom, same shape ($q = p$):** *"After handle $p$ tilted Oxygen's electrons along $z$, how much charge piled into that same $z$ slope?"* $\to$ local self-squish.
   - **Same atom, different shape ($q \neq p$ on atom $A$):** *"While sliding Oxygen's electrons sideways along $p_z$, did the cloud also pinch into a $d$-saddle?"* $\to$ on-atom shape coupling.
   - **Different atom ($B \neq A$):** *"When I lowered Oxygen's voltage floor ($s_{\mathrm{O}}$), how much charge drained out of Carbon ($s_{\mathrm{C}}$) across the $\text{C=O}$ bond?"* $\to$ cross-bond charge flow.
3. **Why $\frac{1}{2}$ appears in $\frac{1}{2}\mathbf{c}^\top\boldsymbol{\Pi}\mathbf{c}$ at runtime:** As real environment push strength ramps cleanly from $0\%$ up to $100\%$ of $\mathbf{c}$, the shifted charge starts at `0` and grows proportionally to the ramp, so the average shifted charge pulled along the whole ramp is **half** the final shifted charge—mirroring $\frac{1}{2}kx^2$ for a stretched spring.
