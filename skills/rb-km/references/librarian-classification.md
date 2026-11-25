# Librarian Classification & Cataloging Rules

Apply library-science principles (controlled vocabulary, faceted subject areas, immutable accession records) so sources stay retrievable across years and remote machines.

## 1. Controlled Source IDs (`--id`)
- Format: `<firstauthor><year><shortslug>` (lowercase ASCII, digits, `.`, `_`, `-` only), e.g., `lamport2012-proofs`, `stone2013-intermolecular`, `rfc9110-http`.
- Never rename an existing `source_id` once cited in `wiki/` or `projects/`; add aliases in notes instead so provenance links never rot.

## 2. Subject Areas (`--area`)
- Keep top-level areas broad and mutually exclusive (aim for 5–12 total areas across the vault, e.g., `proofs`, `quantum-chem`, `ml-systems`, `agents`, `statistics`, `general`).
- Before creating a new area, check existing directories under `library/` and `wiki/`. When a new area is created, ensure `GARDEN_POLICY.md` exists (`rb ingest` creates it automatically for `library/<area>/`).

## 3. Accession Integrity
- Originals inside `library/<area>/<source_id>.<ext>` are **immutable**: never edit a cataloged PDF or text snapshot in place.
- Human-confirmed highlights live strictly in sidecars (`<source_id>.annotated.pdf` and `<source_id>.highlights.md`).
- If a source is updated externally (e.g., arXiv v2), ingest it as a distinct versioned ID (`author2026-v2`) and cross-link the superseded version in the Wiki.

## 4. Subagent Dispatch Pattern (Librarian)
When a task requires searching 3+ Library documents:
1. Spawn a fresh-context Librarian subagent with only the research question and `library/catalog.json`.
2. Require the subagent to return **only**: matching `source_id`s, exact verbatim quotes with `[@source-id, p.X, L.Y]`, and a 3-bullet synthesis.
3. Keep raw PDF dumps out of the main agent's context window.
