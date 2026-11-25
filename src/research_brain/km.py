"""Single owner of Vault initialization, Project Notebooks, Worklogs, Gardener policies, and KM linting."""

from __future__ import annotations

import re
import stat
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from research_brain.citations import CITATION_RE, verify_file
from research_brain.library import load_catalog, save_catalog

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
GARDEN_STATUS_RE = re.compile(r"^status:\s*(ask-first|converged)\s*$", re.MULTILINE)
VERIFIED_STATUS_RE = re.compile(r"^status:\s*verified\s*$", re.MULTILINE)
DISPLAY_MATH_RE = re.compile(
    r"(\$\$(?P<dollar>.+?)\$\$|\\begin\{(?:equation|align)\*?\}(?P<env>.+?)\\end\{(?:equation|align)\*?\})",
    re.DOTALL,
)
INLINE_MATH_RE = re.compile(r"(?<!\$)\$(?!\$)([^$\n]*?[A-Za-z\\][^$\n]*?)(?<!\$)\$(?!\$)")
COLOR_ANNOT_RE = re.compile(r"\\(?:color|textcolor|eqnmarkbox|eqnmark)\b")
GLOSSARY_HEADING_RE = re.compile(
    r"^#{1,3}\s+(?:(?:Master\s+)?(?:Symbol|Term|Symbol\s*&\s*Term)\s+(?:Glossary|Reference)|Reference\s+Table)\b",
    re.MULTILINE | re.IGNORECASE,
)
GLOSSARY_BLOCK_RE = re.compile(
    r"(?m)^#{1,3}\s+(?:(?:Master\s+)?(?:Symbol|Term|Symbol\s*&\s*Term)\s+(?:Glossary|Reference)|Reference\s+Table)\b[^\n]*\n(?:[ \t]*\n)*(?:[ \t]*\|[^\n]*\n?)+",
    re.IGNORECASE,
)
ACRONYM_RE = re.compile(r"\b([A-Z]{3,8})\b")
COMMON_NON_DOMAIN_ACRONYMS = frozenset({
    "PDF", "URL", "CLI", "API", "UTC", "JSON", "HTML", "YAML", "TOML", "SHA",
    "CSV", "TSV", "SVG", "PNG", "XML", "HTTP", "HTTPS", "SSH", "VCS", "GIT",
    "README", "INDEX", "TODO", "NOTE", "PASS", "FAIL", "WARN", "ERROR", "INFO",
    "UNVERIFIED", "AND", "NOT", "THE", "ALL", "ANY", "FOR", "USE", "DOI",
    "USA", "USD", "MIT", "QED", "LLM", "LLMS", "MCP",
})
PROVENANCE_TAG_RE = re.compile(
    r"\[@[a-z0-9][a-z0-9._-]{1,80}[^\]]*\]|\[(?:calc|worklog):\s*[^\]]+\]|\[(?:example|UNVERIFIED)\]",
    re.IGNORECASE,
)
QUANT_CLAIM_RE = re.compile(
    r"(?:\b\d+(?:\.\d+)?\s*(?:×|x|\\times)\s*10\^?\{?-?\d+\}?|\b\d+(?:\.\d+)?e[+-]?\d+\b|"
    r"[<>≤≥≈]?\s*\d+(?:\.\d+)?\s*%|"
    r"\b\d+(?:\.\d+)?\s*(?:eV|meV|kcal/mol|kJ/mol|Ha|Hartree|Bohr|Debye|nm|ps|ns|fs|Å|Angstrom)\b|"
    r"\b\d+\.\d+\s*/\s*\d+\.\d+\s*=\s*\d+\.\d+\b)"
)

PRE_COMMIT_SCRIPT = """#!/bin/sh
# Managed by Research Brain (rb) — deterministic out-of-model verification hook.
set -eu
if command -v rb >/dev/null 2>&1; then
  rb verify-quotes --staged
  rb lint --staged
elif [ -x "$HOME/.local/bin/rb" ]; then
  "$HOME/.local/bin/rb" verify-quotes --staged
  "$HOME/.local/bin/rb" lint --staged
else
  echo "research-brain: 'rb' CLI not found on PATH; skipping hook." >&2
fi
"""


@dataclass(frozen=True)
class LintIssue:
    file: Path
    severity: str  # "error" | "warn"
    message: str


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "-", name.strip().lower()).strip("-")
    if not slug:
        raise ValueError(f"Invalid name: {name!r}")
    return slug


def install_git_pre_commit_hook(repo_path: Path) -> Path | None:
    """Install a portable git pre-commit hook into repo_path if it is a git repository."""
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        return None
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_file = hooks_dir / "pre-commit"
    hook_file.write_text(PRE_COMMIT_SCRIPT, encoding="utf-8")
    hook_file.chmod(hook_file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return hook_file


def ensure_garden_policy(area_dir: Path, area_label: str) -> Path:
    """Create a default ask-first GARDEN_POLICY.md in a Library or Wiki sub-area."""
    area_dir.mkdir(parents=True, exist_ok=True)
    policy_path = area_dir / "GARDEN_POLICY.md"
    if not policy_path.exists():
        policy_path.write_text(
            "---\n"
            f"area: {area_label}\n"
            "status: ask-first\n"
            "---\n\n"
            f"# Garden Policy — {area_label}\n\n"
            "## Mode\n"
            "- Current mode: `ask-first` (propose diffs on a branch and request human approval before merging).\n"
            "- Promote to `converged` only via `rb garden converge <area> --approved` after human confirmation.\n\n"
            "## Approved Rules\n"
            "- Keep one canonical page per concept; merge duplicates only with preserved source citations.\n"
            "- Never drop verbatim quotes or `[@source-id, p.X]` provenance links.\n\n"
            "## Decision Log\n",
            encoding="utf-8",
        )
    return policy_path


def get_garden_status(policy_path: Path) -> str:
    if not policy_path.is_file():
        return "missing"
    text = policy_path.read_text(encoding="utf-8")
    match = GARDEN_STATUS_RE.search(text)
    return match.group(1) if match else "unknown"


def set_garden_converged(vault_path: Path, area_rel: str, approved: bool) -> Path:
    """Mark a wiki/<area> or library/<area> GARDEN_POLICY.md as converged."""
    if not approved:
        raise PermissionError(
            "Refusing to mark sub-area converged without explicit human approval (--approved)."
        )
    target_dir = vault_path / area_rel
    if not target_dir.is_dir():
        raise FileNotFoundError(f"Sub-area directory not found in vault: {target_dir}")
    policy_path = ensure_garden_policy(target_dir, area_rel)
    text = policy_path.read_text(encoding="utf-8")
    updated = GARDEN_STATUS_RE.sub("status: converged", text, count=1)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    updated += f"- {stamp}: Promoted to `converged` by human approval.\n"
    policy_path.write_text(updated, encoding="utf-8")
    return policy_path


def init_vault(vault_path: Path) -> Path:
    """Initialize a git-backed, Obsidian-compatible Global Research Brain Vault."""
    vault_path = vault_path.expanduser().resolve()
    for sub in ("library/general", "wiki/general", "projects"):
        (vault_path / sub).mkdir(parents=True, exist_ok=True)

    if not (vault_path / "library" / "catalog.json").exists():
        save_catalog(vault_path, load_catalog(vault_path))

    ensure_garden_policy(vault_path / "library" / "general", "library/general")
    ensure_garden_policy(vault_path / "wiki" / "general", "wiki/general")

    index_file = vault_path / "wiki" / "INDEX.md"
    if not index_file.exists():
        index_file.write_text(
            "---\n"
            "status: verified\n"
            "---\n\n"
            "# Research Brain Wiki Index\n\n"
            "Verified ground-truth pages backed by exact Library sources (`[@source-id, p.X, L.Y]`).\n\n"
            "## Areas\n"
            "- `wiki/general/`\n",
            encoding="utf-8",
        )

    readme_file = vault_path / "README.md"
    if not readme_file.exists():
        readme_file.write_text(
            "# Research Brain Vault\n\n"
            "- `library/` — Immutable external sources, `catalog.json`, annotated PDFs, and `.highlights.md`.\n"
            "- `wiki/` — Verified ground-truth synthesis with exact Library citations.\n"
            "- `projects/<name>/notebook/` — Living per-project synthesis across sessions.\n"
            "- `projects/<name>/worklogs/` — Append-only chronological session audit logs.\n",
            encoding="utf-8",
        )

    gitignore = vault_path / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(".DS_Store\n.obsidian/workspace*.json\n", encoding="utf-8")

    if not (vault_path / ".git").exists():
        subprocess.run(["git", "init", "-q"], cwd=vault_path, check=True)
    install_git_pre_commit_hook(vault_path)
    return vault_path


def init_project(
    vault_path: Path, project_name: str, repo_path: Path | None = None
) -> dict[str, str]:
    """Create a project's Notebook and Worklog folders in the Global Vault and link its code repo."""
    init_vault(vault_path)
    slug = _slugify(project_name)
    proj_root = vault_path / "projects" / slug
    nb_dir = proj_root / "notebook"
    wl_dir = proj_root / "worklogs"
    proofs_dir = nb_dir / "proofs"
    nb_dir.mkdir(parents=True, exist_ok=True)
    wl_dir.mkdir(parents=True, exist_ok=True)
    proofs_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    nb_readme = nb_dir / "README.md"
    if not nb_readme.exists():
        nb_readme.write_text(
            f"# Project Notebook — {project_name}\n\n"
            f"- Created: {today}\n"
            f"- Worklogs: `../worklogs/`\n"
            f"- Active proofs: `proofs/`\n\n"
            "## Current Synthesis\n"
            "*(Update across sessions with concise, current state so fresh agents avoid reading old worklogs.)*\n\n"
            "## Open Questions\n"
            "- \n\n"
            "## Verified Candidates for Wiki Promotion\n"
            "- \n",
            encoding="utf-8",
        )

    hyp_file = nb_dir / "HYPOTHESES.md"
    if not hyp_file.exists():
        hyp_file.write_text(
            f"# Hypotheses & Lamport Proofs — {project_name}\n\n"
            "Every major implementation claim is decomposed into numbered Lamport assertions (`1.`, `1.1.`, `1.1.1.`) "
            "and adversarially reviewed before coding.\n",
            encoding="utf-8",
        )

    marker_str = ""
    hook_str = ""
    if repo_path is not None:
        repo_path = repo_path.expanduser().resolve()
        repo_path.mkdir(parents=True, exist_ok=True)
        marker = repo_path / ".research-brain.toml"
        marker.write_text(
            f'project = "{slug}"\n\n'
            "[vault]\n"
            f'path = "{vault_path}"\n',
            encoding="utf-8",
        )
        marker_str = str(marker)
        if not (repo_path / ".git").exists():
            subprocess.run(["git", "init", "-q"], cwd=repo_path, check=True)
        hook = install_git_pre_commit_hook(repo_path)
        hook_str = str(hook) if hook else ""

    return {
        "project": slug,
        "notebook": str(nb_dir),
        "worklogs": str(wl_dir),
        "marker": marker_str,
        "hook": hook_str,
    }


def append_worklog(
    vault_path: Path,
    project_name: str,
    kind: str,
    text: str,
    citations: list[str] | None = None,
) -> Path:
    """Append an immutable timestamped entry to projects/<slug>/worklogs/YYYY-MM-DD.md."""
    slug = _slugify(project_name)
    wl_dir = vault_path / "projects" / slug / "worklogs"
    wl_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    log_file = wl_dir / f"{now.strftime('%Y-%m-%d')}.md"
    if not log_file.exists():
        log_file.write_text(f"# Worklog — {project_name} ({now.strftime('%Y-%m-%d')})\n\n", encoding="utf-8")

    stamp = now.strftime("%H:%M:%S UTC")
    entry = f"## [{stamp}] `{kind}`\n\n{text.strip()}\n"
    if citations:
        entry += "\n- Sources: " + ", ".join(citations) + "\n"
    entry += "\n"

    with log_file.open("a", encoding="utf-8") as fh:
        fh.write(entry)
    return log_file


def _collect_all_stems(vault_path: Path) -> set[str]:
    stems: set[str] = set()
    for p in vault_path.rglob("*.md"):
        if ".git" in p.parts:
            continue
        stems.add(p.stem)
        stems.add(str(p.relative_to(vault_path).with_suffix("")))
    return stems


def lint_vault(vault_path: Path, target_files: list[Path] | None = None) -> list[LintIssue]:
    """Check KM structural invariants:
    1. Every verbatim quote block verifies against library/catalog.json.
    2. Wiki pages (except INDEX.md and GARDEN_POLICY.md) carry `status: verified` and at least one Library citation.
    3. Every wiki/ and library/ sub-area directory has a GARDEN_POLICY.md.
    4. Internal [[wikilinks]] inside the vault resolve to existing pages.
    """
    issues: list[LintIssue] = []
    if not vault_path.is_dir():
        return [LintIssue(vault_path, "error", f"Vault directory does not exist: {vault_path}")]

    # 3. Sub-area garden policies
    if target_files is None:
        for top in ("wiki", "library"):
            top_dir = vault_path / top
            if top_dir.is_dir():
                for child in sorted(top_dir.iterdir()):
                    if child.is_dir() and not child.name.startswith("."):
                        if not (child / "GARDEN_POLICY.md").is_file():
                            issues.append(
                                LintIssue(
                                    child,
                                    "error",
                                    f"Missing GARDEN_POLICY.md in sub-area {top}/{child.name}",
                                )
                            )

    md_files = (
        [f for f in target_files if f.suffix.lower() == ".md" and f.is_file()]
        if target_files is not None
        else [p for p in vault_path.rglob("*.md") if ".git" not in p.parts]
    )

    known_stems = _collect_all_stems(vault_path)
    vault_resolved = vault_path.resolve()

    for md in md_files:
        # 1. Verify verbatim quotes
        for res in verify_file(vault_path, md):
            if not res.ok:
                issues.append(
                    LintIssue(
                        md,
                        "error",
                        f"Line {res.claim.line_no} (@{res.claim.source_id}): {res.reason}",
                    )
                )

        content = md.read_text(encoding="utf-8", errors="replace")
        md_resolved = md.resolve()

        # 2. Wiki page ground-truth check (only for files under vault/wiki/)
        try:
            rel = md_resolved.relative_to(vault_resolved)
            in_vault = True
        except ValueError:
            rel = md_resolved
            in_vault = False

        if in_vault and len(rel.parts) >= 2 and rel.parts[0] == "wiki":
            if md.name not in ("INDEX.md", "GARDEN_POLICY.md"):
                if not VERIFIED_STATUS_RE.search(content):
                    issues.append(
                        LintIssue(
                            md,
                            "error",
                            "Wiki page missing frontmatter `status: verified` (unverified notes belong in projects/<name>/notebook/).",
                        )
                    )
                if not CITATION_RE.search(content):
                    issues.append(
                        LintIssue(
                            md,
                            "error",
                            "Wiki page must cite at least one Library source using [@source-id, p.X] or [@source-id, L.Y].",
                        )
                    )

        # 4. Wikilink check inside vault
        if in_vault:
            for m in WIKILINK_RE.finditer(content):
                target = m.group(1).strip()
                if target and target not in known_stems:
                    issues.append(
                        LintIssue(md, "warn", f"Unresolved wikilink [[{target}]] in vault.")
                    )

        # 5. Colored LaTeX annotation check on displayed equations (outside fenced code blocks)
        is_wiki_page = (
            in_vault
            and len(rel.parts) >= 2
            and rel.parts[0] == "wiki"
            and md.name not in ("INDEX.md", "GARDEN_POLICY.md")
        )
        stripped_frontmatter = re.sub(r"\A---\n.*?\n---\n?", "", content, flags=re.DOTALL)
        stripped_code = re.sub(r"(?ms)^```.*?^```|^~~~.*?^~~~", "", stripped_frontmatter)
        display_matches = list(DISPLAY_MATH_RE.finditer(stripped_code))
        for idx, m in enumerate(display_matches, start=1):
            eq_body = m.group("dollar") or m.group("env") or ""
            if eq_body.strip() and not COLOR_ANNOT_RE.search(eq_body):
                sev = "error" if is_wiki_page else "warn"
                issues.append(
                    LintIssue(
                        md,
                        sev,
                        f"Display equation #{idx} lacks colored LaTeX annotation (\\color / \\textcolor / \\eqnmarkbox); see rb-explain.",
                    )
                )

        # 6. Markdown Reference Table presence whenever math symbols or technical acronyms appear
        has_math = bool(display_matches) or bool(INLINE_MATH_RE.search(stripped_code))
        glossary_match = GLOSSARY_BLOCK_RE.search(stripped_code)
        glossary_text = glossary_match.group(0) if glossary_match else ""
        prose_no_glossary = GLOSSARY_BLOCK_RE.sub("", stripped_code)
        # Strip provenance tags like [UNVERIFIED] before scanning acronyms
        prose_for_acronyms = PROVENANCE_TAG_RE.sub("", prose_no_glossary)
        prose_acronyms = {
            m.group(1)
            for m in ACRONYM_RE.finditer(prose_for_acronyms)
            if m.group(1) not in COMMON_NON_DOMAIN_ACRONYMS
        }

        if (has_math or prose_acronyms) and not glossary_match:
            sev = "error" if is_wiki_page else "warn"
            issues.append(
                LintIssue(
                    md,
                    sev,
                    "Document uses math symbols or technical acronyms without a Markdown `## Reference Table` (symbols & terms); define every symbol and new idea before use (see rb-explain).",
                )
            )
        elif prose_acronyms:
            for acr in sorted(prose_acronyms):
                in_ref = re.search(rf"\b{re.escape(acr)}\b", glossary_text) is not None
                spelled_inline = re.search(rf"\(\s*{re.escape(acr)}\s*\)", prose_no_glossary) is not None
                if not in_ref and not spelled_inline:
                    sev = "error" if is_wiki_page else "warn"
                    issues.append(
                        LintIssue(
                            md,
                            sev,
                            f"Acronym `{acr}` is neither defined in `## Reference Table` nor spelled out inline `(e.g., Full Name ({acr}))`.",
                        )
                    )

        # 7. Quantitative claim provenance check (outside Reference Table & headings)
        if md.name not in ("INDEX.md", "GARDEN_POLICY.md") and not md.name.endswith(".highlights.md"):
            for para in re.split(r"\n\s*\n", prose_no_glossary):
                p_strip = para.strip()
                if not p_strip or p_strip.startswith("#") or p_strip.startswith("|") or p_strip.startswith("$$"):
                    continue
                if QUANT_CLAIM_RE.search(p_strip) and not PROVENANCE_TAG_RE.search(p_strip):
                    sev = "error" if is_wiki_page else "warn"
                    snippet = p_strip.splitlines()[0][:80]
                    issues.append(
                        LintIssue(
                            md,
                            sev,
                            f"Quantitative claim lacks provenance tag ([@id, p.X] / [calc: ...] / [worklog: ...] / [example] / [UNVERIFIED]): {snippet!r}",
                        )
                    )

    return issues
