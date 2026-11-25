"""Thin CLI entrypoint (`rb`) for Research Brain."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

from research_brain import __version__
from research_brain.citations import highlight_source, verify_file
from research_brain.config import load_config, write_default_config
from research_brain.km import (
    append_worklog,
    ensure_garden_policy,
    get_garden_status,
    init_project,
    init_vault,
    lint_vault,
    set_garden_converged,
)
from research_brain.library import ingest_source, load_catalog


def _staged_markdown_files(cwd: Path) -> list[Path]:
    proc = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    files: list[Path] = []
    for line in proc.stdout.splitlines():
        p = (cwd / line.strip()).resolve()
        if p.suffix.lower() == ".md" and p.is_file():
            files.append(p)
    return files


def cmd_init_vault(args: argparse.Namespace) -> int:
    cfg = load_config(Path.cwd())
    target = Path(args.path).expanduser().resolve() if args.path else cfg.vault_path
    vault = init_vault(target)
    cfg_file = write_default_config(vault)
    print(f"Initialized Research Brain vault: {vault}")
    print(f"Config: {cfg_file}")
    return 0


def cmd_init_project(args: argparse.Namespace) -> int:
    cfg = load_config(Path.cwd())
    repo = Path(args.repo).expanduser().resolve() if args.repo else None
    info = init_project(cfg.vault_path, args.name, repo_path=repo)
    print(json.dumps(info, indent=2))
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    cfg = load_config(Path.cwd())
    init_vault(cfg.vault_path)
    rec = ingest_source(
        vault_path=cfg.vault_path,
        src_file=Path(args.file).expanduser().resolve(),
        source_id=args.id,
        area=args.area,
        title=args.title or "",
        authors=args.authors or "",
        year=args.year or "",
        origin_url=args.url or "",
    )
    ensure_garden_policy(cfg.vault_path / "library" / rec.area, f"library/{rec.area}")
    print(f"Ingested @{rec.source_id} -> {rec.rel_path} (sha256: {rec.sha256[:12]})")
    return 0


def cmd_verify_quotes(args: argparse.Namespace) -> int:
    cfg = load_config(Path.cwd())
    if args.staged:
        paths = _staged_markdown_files(Path.cwd())
    elif args.paths:
        paths = []
        for raw in args.paths:
            p = Path(raw).expanduser().resolve()
            if p.is_dir():
                paths.extend(f for f in p.rglob("*.md") if ".git" not in f.parts)
            elif p.is_file():
                paths.append(p)
    else:
        paths = [f for f in cfg.vault_path.rglob("*.md") if ".git" not in f.parts]

    total = 0
    failures = 0
    for md in paths:
        for res in verify_file(cfg.vault_path, md):
            total += 1
            if not res.ok:
                failures += 1
                print(
                    f"[FAIL] {res.claim.file}:{res.claim.line_no} (@{res.claim.source_id}): {res.reason}",
                    file=sys.stderr,
                )
            elif args.verbose:
                print(f"[PASS] {res.claim.file}:{res.claim.line_no} (@{res.claim.source_id}): {res.reason}")

    if failures:
        print(f"verify-quotes: {failures}/{total} quote check(s) FAILED.", file=sys.stderr)
        return 1
    if args.verbose or total > 0:
        print(f"verify-quotes: {total}/{total} quote check(s) passed.")
    return 0


def cmd_highlight(args: argparse.Namespace) -> int:
    cfg = load_config(Path.cwd())
    try:
        res = highlight_source(
            vault_path=cfg.vault_path,
            source_id=args.source_id,
            quote=args.quote,
            page=args.page,
            line_start=args.line_start,
            line_end=args.line_end,
            note=args.note or "",
            confirmed_by_human=args.confirmed,
        )
    except (PermissionError, KeyError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(res, indent=2))
    return 0


def cmd_log(args: argparse.Namespace) -> int:
    cfg = load_config(Path.cwd())
    log_file = append_worklog(
        vault_path=cfg.vault_path,
        project_name=args.project,
        kind=args.kind,
        text=args.text,
        citations=args.cite or [],
    )
    print(f"Logged entry -> {log_file}")
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    cfg = load_config(Path.cwd())
    targets = None
    if args.staged:
        targets = _staged_markdown_files(Path.cwd())
    elif args.paths:
        targets = [Path(p).expanduser().resolve() for p in args.paths]

    issues = lint_vault(cfg.vault_path, target_files=targets)
    errors = [i for i in issues if i.severity == "error"]
    warns = [i for i in issues if i.severity != "error"]

    for issue in issues:
        stream = sys.stderr if issue.severity == "error" else sys.stdout
        print(f"[{issue.severity.upper()}] {issue.file}: {issue.message}", file=stream)

    if errors:
        print(f"lint: {len(errors)} error(s), {len(warns)} warning(s).", file=sys.stderr)
        return 1
    print(f"lint: 0 errors, {len(warns)} warning(s).")
    return 0


def cmd_garden(args: argparse.Namespace) -> int:
    cfg = load_config(Path.cwd())
    if args.garden_cmd == "status":
        for top in ("wiki", "library"):
            top_dir = cfg.vault_path / top
            if not top_dir.is_dir():
                continue
            for child in sorted(top_dir.iterdir()):
                if child.is_dir() and not child.name.startswith("."):
                    st = get_garden_status(child / "GARDEN_POLICY.md")
                    print(f"{top}/{child.name}: {st}")
        return 0

    if args.garden_cmd == "converge":
        try:
            policy = set_garden_converged(cfg.vault_path, args.area, approved=args.approved)
        except (PermissionError, FileNotFoundError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"Marked converged: {policy}")
        return 0
    return 1


def cmd_doctor(_args: argparse.Namespace) -> int:
    cfg = load_config(Path.cwd())
    checks: list[tuple[str, bool, str]] = []
    checks.append(("git", shutil.which("git") is not None, shutil.which("git") or "missing"))
    checks.append(("pymupdf", importlib.util.find_spec("pymupdf") is not None, "PDF extraction & highlighting"))
    checks.append(("vault", cfg.vault_path.is_dir(), str(cfg.vault_path)))
    catalog_count = len(load_catalog(cfg.vault_path)) if cfg.vault_path.is_dir() else 0
    checks.append(("library-catalog", (cfg.vault_path / "library" / "catalog.json").is_file(), f"{catalog_count} source(s)"))
    checks.append(("vault-hook", (cfg.vault_path / ".git" / "hooks" / "pre-commit").is_file(), "pre-commit hook"))

    failed = 0
    for name, ok, detail in checks:
        tag = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"[{tag}] {name}: {detail}")
    print(f"config: max_context={cfg.max_context_percent}%, proof=(depth={cfg.proof.max_depth}, reviewers={cfg.proof.reviewers_per_round}, rounds={cfg.proof.max_rounds}), spelling={cfg.spelling}")
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rb", description="Research Brain deterministic CLI.")
    parser.add_argument("--version", action="version", version=f"rb {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_iv = sub.add_parser("init-vault", help="Initialize the git-backed Global Research Brain Vault.")
    p_iv.add_argument("--path", help="Custom vault directory (default: config or ~/research-brain-vault).")
    p_iv.set_defaults(func=cmd_init_vault)

    p_ip = sub.add_parser("init-project", help="Create Project Notebook & Worklog and link a code repo.")
    p_ip.add_argument("name", help="Project name.")
    p_ip.add_argument("--repo", help="Optional code repository path to link and install pre-commit hook.")
    p_ip.set_defaults(func=cmd_init_project)

    p_in = sub.add_parser("ingest", help="Catalog an external source file in library/<area>/.")
    p_in.add_argument("file", help="Path to PDF, Markdown, or text file.")
    p_in.add_argument("--id", required=True, help="Stable source ID (e.g. lamport2012).")
    p_in.add_argument("--area", default="general", help="Library subject area slug.")
    p_in.add_argument("--title", help="Human-readable title.")
    p_in.add_argument("--authors", help="Authors.")
    p_in.add_argument("--year", help="Publication year.")
    p_in.add_argument("--url", help="Canonical origin URL or DOI.")
    p_in.set_defaults(func=cmd_ingest)

    p_vq = sub.add_parser("verify-quotes", help="Deterministically verify verbatim blockquotes against library/.")
    p_vq.add_argument("paths", nargs="*", help="Markdown files or directories to verify.")
    p_vq.add_argument("--staged", action="store_true", help="Verify git-staged Markdown files in cwd.")
    p_vq.add_argument("-v", "--verbose", action="store_true", help="Print passing checks too.")
    p_vq.set_defaults(func=cmd_verify_quotes)

    p_hl = sub.add_parser("highlight", help="Highlight a human-understood quote in library/ (non-destructive).")
    p_hl.add_argument("source_id", help="Cataloged source ID.")
    p_hl.add_argument("--quote", required=True, help="Exact verbatim quote to highlight.")
    p_hl.add_argument("--page", type=int, help="1-indexed PDF page number.")
    p_hl.add_argument("--line-start", type=int, help="1-indexed starting line number.")
    p_hl.add_argument("--line-end", type=int, help="1-indexed ending line number.")
    p_hl.add_argument("--note", help="Short explanation of why the human marked this passage.")
    p_hl.add_argument("--confirmed", action="store_true", help="Required flag attesting human confirmation.")
    p_hl.set_defaults(func=cmd_highlight)

    p_lg = sub.add_parser("log", help="Append an immutable worklog entry for a project.")
    p_lg.add_argument("project", help="Project name or slug.")
    p_lg.add_argument("--kind", choices=["exp", "decision", "quote", "dead-end", "note"], default="note")
    p_lg.add_argument("--text", required=True, help="Entry body.")
    p_lg.add_argument("--cite", action="append", help="Optional citation tags like '[@id, p.3]'.")
    p_lg.set_defaults(func=cmd_log)

    p_lt = sub.add_parser("lint", help="Lint vault quotes, wiki verification headers, wikilinks, and garden policies.")
    p_lt.add_argument("paths", nargs="*", help="Specific Markdown files to lint.")
    p_lt.add_argument("--staged", action="store_true", help="Lint git-staged Markdown files in cwd.")
    p_lt.set_defaults(func=cmd_lint)

    p_gd = sub.add_parser("garden", help="Inspect or converge sub-area Gardener policies.")
    gd_sub = p_gd.add_subparsers(dest="garden_cmd", required=True)
    gd_sub.add_parser("status", help="Show ask-first / converged status for every sub-area.")
    p_gc = gd_sub.add_parser("converge", help="Promote a sub-area from ask-first to converged.")
    p_gc.add_argument("area", help="Relative sub-area path, e.g. wiki/general or library/general.")
    p_gc.add_argument("--approved", action="store_true", help="Required flag attesting human approval.")
    p_gd.set_defaults(func=cmd_garden)

    p_dr = sub.add_parser("doctor", help="Check Research Brain tools, vault, and hooks.")
    p_dr.set_defaults(func=cmd_doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
