"""Single owner of the Library catalog and source text extraction."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

CATALOG_REL = Path("library") / "catalog.json"
SOURCE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,80}$")


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    title: str
    area: str
    rel_path: str
    sha256: str
    kind: str
    added_at: str
    authors: str = ""
    year: str = ""
    origin_url: str = ""


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_catalog(vault_path: Path) -> dict[str, SourceRecord]:
    catalog_file = vault_path / CATALOG_REL
    if not catalog_file.is_file():
        return {}
    raw = json.loads(catalog_file.read_text(encoding="utf-8"))
    sources = raw.get("sources", {})
    return {sid: SourceRecord(**data) for sid, data in sources.items()}


def save_catalog(vault_path: Path, catalog: dict[str, SourceRecord]) -> Path:
    catalog_file = vault_path / CATALOG_REL
    catalog_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "sources": {sid: asdict(rec) for sid, rec in sorted(catalog.items())},
    }
    catalog_file.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return catalog_file


def ingest_source(
    vault_path: Path,
    src_file: Path,
    source_id: str,
    area: str,
    title: str = "",
    authors: str = "",
    year: str = "",
    origin_url: str = "",
) -> SourceRecord:
    """Copy an external source into library/<area>/<source_id>.<ext> and catalog it."""
    if not SOURCE_ID_RE.match(source_id):
        raise ValueError(
            f"Invalid source_id {source_id!r}: use lowercase letters, digits, '.', '_', or '-'."
        )
    if not src_file.is_file():
        raise FileNotFoundError(f"Source file not found: {src_file}")

    area_slug = re.sub(r"[^a-z0-9_-]+", "-", area.strip().lower()).strip("-") or "general"
    ext = src_file.suffix.lower() or ".txt"
    dest_dir = vault_path / "library" / area_slug
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / f"{source_id}{ext}"

    if src_file.resolve() != dest_file.resolve():
        shutil.copy2(src_file, dest_file)

    record = SourceRecord(
        source_id=source_id,
        title=title or src_file.stem,
        area=area_slug,
        rel_path=str(dest_file.relative_to(vault_path)),
        sha256=_sha256_file(dest_file),
        kind="pdf" if ext == ".pdf" else "text",
        added_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        authors=authors,
        year=year,
        origin_url=origin_url,
    )

    catalog = load_catalog(vault_path)
    catalog[source_id] = record
    save_catalog(vault_path, catalog)
    return record


def resolve_source_path(vault_path: Path, source_id: str) -> tuple[SourceRecord, Path]:
    catalog = load_catalog(vault_path)
    if source_id not in catalog:
        raise KeyError(f"Source '{source_id}' is not registered in library/catalog.json.")
    rec = catalog[source_id]
    path = vault_path / rec.rel_path
    if not path.is_file():
        raise FileNotFoundError(f"Cataloged file missing on disk: {path}")
    return rec, path


def extract_text(
    source_path: Path,
    page: int | None = None,
    line_start: int | None = None,
    line_end: int | None = None,
) -> str:
    """Extract text from a PDF (1-indexed page) or plain-text file (1-indexed lines)."""
    if source_path.suffix.lower() == ".pdf":
        import pymupdf  # Lazy import so non-PDF commands never pay import cost

        doc = pymupdf.open(source_path)
        try:
            if page is not None:
                if page < 1 or page > len(doc):
                    raise ValueError(
                        f"Page {page} out of range for {source_path.name} (1..{len(doc)})."
                    )
                text = doc[page - 1].get_text("text")
            else:
                text = "\n".join(p.get_text("text") for p in doc)
        finally:
            doc.close()

        if line_start is not None:
            lines = text.splitlines()
            end = line_end if line_end is not None else line_start
            start_idx = max(0, line_start - 1)
            end_idx = min(len(lines), end)
            return "\n".join(lines[start_idx:end_idx])
        return text

    text = source_path.read_text(encoding="utf-8", errors="replace")
    if line_start is not None:
        lines = text.splitlines()
        end = line_end if line_end is not None else line_start
        if line_start < 1 or line_start > len(lines):
            raise ValueError(
                f"Line {line_start} out of range for {source_path.name} (1..{len(lines)})."
            )
        return "\n".join(lines[line_start - 1 : min(len(lines), end)])
    return text
