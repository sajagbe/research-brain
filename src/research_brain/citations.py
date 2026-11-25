"""Single owner of verbatim quote parsing, deterministic verification, and source highlighting."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from research_brain.library import extract_text, resolve_source_path

# Matches citations such as:
#   [@smith2024, p.12]
#   [@smith2024, p.12, L.4-9]
#   [@smith2024, L.10-22]
#   [@smith2024, L.10]
CITATION_RE = re.compile(
    r"\[@(?P<source_id>[a-z0-9][a-z0-9._-]{1,80})"
    r"(?:,\s*p\.(?P<page>\d+))?"
    r"(?:,\s*L\.(?P<line_start>\d+)(?:-(?P<line_end>\d+))?)?"
    r"(?:,\s*[^\]]+)?\]"
)


@dataclass(frozen=True)
class QuoteClaim:
    file: Path
    line_no: int
    quote_text: str
    source_id: str
    page: int | None
    line_start: int | None
    line_end: int | None


@dataclass(frozen=True)
class VerificationResult:
    claim: QuoteClaim
    ok: bool
    reason: str


def normalize_text(text: str) -> str:
    """Normalize PDF hyphenation line-breaks and whitespace while preserving exact words."""
    # Join soft hyphenated line-wraps like "inter-\naction" -> "interaction"
    cleaned = re.sub(r"-\s*\n\s*", "", text)
    # Normalize curly quotes/apostrophes and dashes for deterministic substring checks
    cleaned = (
        cleaned.replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u00a0", " ")
    )
    return re.sub(r"\s+", " ", cleaned).strip()


def _strip_outer_quotes(text: str) -> str:
    s = text.strip()
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "\u201c" and s[-1] == "\u201d")):
        return s[1:-1].strip()
    return s


def parse_quotes(markdown_path: Path) -> list[QuoteClaim]:
    """Extract blockquote + [@source-id, ...] pairs from a Markdown document.

    Supported layouts:
    1) Citation inside the last line of the blockquote:
       > "exact quote" [@source-id, p.3, L.10-12]
    2) Citation on the line immediately following the blockquote:
       > "exact quote"
       — [@source-id, p.3]
    """
    lines = markdown_path.read_text(encoding="utf-8", errors="replace").splitlines()
    claims: list[QuoteClaim] = []
    i = 0
    in_fence = False

    while i < len(lines):
        stripped = lines[i].lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue

        if stripped.startswith(">"):
            start_line = i + 1
            block_lines: list[str] = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                content = lines[i].lstrip()[1:]
                if content.startswith(" "):
                    content = content[1:]
                block_lines.append(content)
                i += 1

            raw_block = "\n".join(block_lines).strip()
            match = CITATION_RE.search(raw_block)
            if match:
                quote_body = _strip_outer_quotes(raw_block[: match.start()].rstrip(" —-"))
            else:
                # Check the immediately following non-empty line for attribution
                if i < len(lines):
                    next_match = CITATION_RE.search(lines[i])
                    if next_match:
                        match = next_match
                        quote_body = _strip_outer_quotes(raw_block)
                        i += 1
                    else:
                        quote_body = ""
                else:
                    quote_body = ""

            if match and quote_body:
                claims.append(
                    QuoteClaim(
                        file=markdown_path,
                        line_no=start_line,
                        quote_text=quote_body,
                        source_id=match.group("source_id"),
                        page=int(match.group("page")) if match.group("page") else None,
                        line_start=int(match.group("line_start")) if match.group("line_start") else None,
                        line_end=int(match.group("line_end")) if match.group("line_end") else None,
                    )
                )
            continue

        i += 1

    return claims


def verify_claim(vault_path: Path, claim: QuoteClaim) -> VerificationResult:
    """Deterministically verify that claim.quote_text exists in the cataloged source."""
    if claim.page is None and claim.line_start is None:
        return VerificationResult(
            claim=claim,
            ok=False,
            reason="Citation must include a page (p.X) or line range (L.Y or L.Y-Z).",
        )

    try:
        rec, src_path = resolve_source_path(vault_path, claim.source_id)
    except (KeyError, FileNotFoundError) as exc:
        return VerificationResult(claim=claim, ok=False, reason=str(exc))

    try:
        haystack_raw = extract_text(
            src_path,
            page=claim.page,
            line_start=claim.line_start,
            line_end=claim.line_end,
        )
    except ValueError as exc:
        return VerificationResult(claim=claim, ok=False, reason=str(exc))

    needle = normalize_text(claim.quote_text)
    haystack = normalize_text(haystack_raw)

    if not needle:
        return VerificationResult(claim=claim, ok=False, reason="Empty quote text.")

    if needle in haystack:
        return VerificationResult(claim=claim, ok=True, reason=f"Matched in {rec.rel_path}")

    loc = []
    if claim.page is not None:
        loc.append(f"p.{claim.page}")
    if claim.line_start is not None:
        loc.append(
            f"L.{claim.line_start}-{claim.line_end}" if claim.line_end else f"L.{claim.line_start}"
        )
    return VerificationResult(
        claim=claim,
        ok=False,
        reason=f"Verbatim quote not found in {rec.rel_path} ({', '.join(loc)}).",
    )


def verify_file(vault_path: Path, markdown_path: Path) -> list[VerificationResult]:
    claims = parse_quotes(markdown_path)
    return [verify_claim(vault_path, claim) for claim in claims]


def highlight_source(
    vault_path: Path,
    source_id: str,
    quote: str,
    page: int | None = None,
    line_start: int | None = None,
    line_end: int | None = None,
    note: str = "",
    confirmed_by_human: bool = False,
) -> dict[str, str]:
    """Highlight a human-understood passage in a sidecar index and (for PDFs) an annotated PDF copy.

    Never mutates the original source file in library/ so SHA-256 provenance stays intact.
    """
    if not confirmed_by_human:
        raise PermissionError(
            "Refusing to highlight: pass --confirmed only after the human explicitly confirms understanding."
        )

    rec, src_path = resolve_source_path(vault_path, source_id)
    haystack = normalize_text(
        extract_text(src_path, page=page, line_start=line_start, line_end=line_end)
    )
    needle = normalize_text(quote)
    if not needle or needle not in haystack:
        raise ValueError(
            f"Quote could not be verified verbatim in {rec.rel_path}; refusing to highlight."
        )

    annotated_pdf_rel = ""
    if src_path.suffix.lower() == ".pdf":
        import pymupdf

        annotated_path = src_path.with_name(f"{src_path.stem}.annotated.pdf")
        if not annotated_path.exists():
            shutil.copy2(src_path, annotated_path)

        doc = pymupdf.open(annotated_path)
        try:
            target_pages = [page - 1] if page is not None else list(range(len(doc)))
            hit_count = 0
            for idx in target_pages:
                if 0 <= idx < len(doc):
                    pg = doc[idx]
                    rects = pg.search_for(quote.strip())
                    if not rects:
                        # Fallback to normalized whitespace snippet search
                        rects = pg.search_for(needle)
                    if rects:
                        annot = pg.add_highlight_annot(rects)
                        if note:
                            annot.set_info(content=note)
                        annot.update()
                        hit_count += len(rects)
            # Save incrementally or via temp file so PyMuPDF can overwrite cleanly
            tmp_out = annotated_path.with_suffix(".tmp.pdf")
            doc.save(tmp_out)
        finally:
            doc.close()
        tmp_out.replace(annotated_path)
        annotated_pdf_rel = str(annotated_path.relative_to(vault_path))

    sidecar_path = src_path.with_name(f"{src_path.stem}.highlights.md")
    if not sidecar_path.exists():
        sidecar_path.write_text(
            f"# Highlights: {rec.title} (`@{source_id}`)\n\n"
            f"- Source: `{rec.rel_path}`\n"
            f"- Original SHA-256: `{rec.sha256}`\n\n",
            encoding="utf-8",
        )

    loc_parts = []
    if page is not None:
        loc_parts.append(f"p.{page}")
    if line_start is not None:
        loc_parts.append(f"L.{line_start}-{line_end}" if line_end else f"L.{line_start}")
    loc_str = ", ".join(loc_parts) if loc_parts else "full"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    entry = f"## {stamp} (`{loc_str}`)\n\n> =={quote.strip()}== [@{source_id}, {loc_str}]\n\n"
    if note:
        entry += f"- **Human understanding note:** {note}\n\n"

    with sidecar_path.open("a", encoding="utf-8") as fh:
        fh.write(entry)

    return {
        "source_id": source_id,
        "sidecar": str(sidecar_path.relative_to(vault_path)),
        "annotated_pdf": annotated_pdf_rel,
    }
