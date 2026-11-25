"""Behavioral tests for Research Brain deterministic verification, highlighting, and KM invariants."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pymupdf
import pytest

from research_brain.citations import highlight_source, verify_file
from research_brain.km import (
    append_worklog,
    get_garden_status,
    init_project,
    init_vault,
    lint_vault,
    set_garden_converged,
)
from research_brain.library import ingest_source


def _make_sample_pdf(path: Path) -> Path:
    doc = pymupdf.open()
    p1 = doc.new_page()
    p1.insert_text((72, 72), "Page one introduces structured proofs and hierarchical numbering.")
    p2 = doc.new_page()
    p2.insert_text((72, 72), "Every claim must be independently verifiable by a zero-context reviewer.")
    doc.save(path)
    doc.close()
    return path


def test_pdf_ingest_quote_verification_and_human_highlight(tmp_path: Path) -> None:
    vault = init_vault(tmp_path / "vault")
    pdf = _make_sample_pdf(tmp_path / "lamport.pdf")

    rec = ingest_source(vault, pdf, source_id="lamport2012", area="proofs", title="How to Write a 21st Century Proof")
    orig_bytes = (vault / rec.rel_path).read_bytes()

    good_md = vault / "wiki" / "general" / "structured-proofs.md"
    good_md.write_text(
        "---\nstatus: verified\n---\n\n# Structured Proofs\n\n"
        '> "Every claim must be independently verifiable by a zero-context reviewer." [@lamport2012, p.2]\n',
        encoding="utf-8",
    )
    results = verify_file(vault, good_md)
    assert len(results) == 1 and results[0].ok

    # Fabricated quote must fail deterministically
    bad_md = vault / "wiki" / "general" / "fabricated.md"
    bad_md.write_text(
        "---\nstatus: verified\n---\n\n"
        '> "This sentence does not exist anywhere in the paper." [@lamport2012, p.2]\n',
        encoding="utf-8",
    )
    bad_results = verify_file(vault, bad_md)
    assert len(bad_results) == 1 and not bad_results[0].ok

    # Highlighting refuses without human confirmation
    with pytest.raises(PermissionError):
        highlight_source(vault, "lamport2012", "independently verifiable", page=2, confirmed_by_human=False)

    # Highlighting succeeds with confirmation and preserves immutable original PDF
    hl = highlight_source(
        vault,
        "lamport2012",
        "independently verifiable",
        page=2,
        note="Core design requirement for adversarial proof subagents.",
        confirmed_by_human=True,
    )
    assert (vault / rec.rel_path).read_bytes() == orig_bytes
    assert (vault / hl["annotated_pdf"]).is_file()
    assert "==independently verifiable==" in (vault / hl["sidecar"]).read_text(encoding="utf-8")


def test_text_line_range_verification_and_wiki_lint(tmp_path: Path) -> None:
    vault = init_vault(tmp_path / "vault")
    src = tmp_path / "notes.txt"
    src.write_text("line one\nalpha beta gamma\nline three\n", encoding="utf-8")
    ingest_source(vault, src, source_id="spec1", area="general")

    # Unverified wiki page must fail lint
    unverified = vault / "wiki" / "general" / "draft.md"
    unverified.write_text("# Draft\n\nNo status header and no citation.\n", encoding="utf-8")
    issues = lint_vault(vault, target_files=[unverified])
    errors = [i for i in issues if i.severity == "error"]
    assert len(errors) == 2

    # Correct line-range quote passes
    verified = vault / "wiki" / "general" / "ok.md"
    verified.write_text(
        "---\nstatus: verified\n---\n\n> \"alpha beta gamma\"\n— [@spec1, L.2-2]\n",
        encoding="utf-8",
    )
    assert [i for i in lint_vault(vault, target_files=[verified]) if i.severity == "error"] == []


def test_project_notebook_worklog_and_gardener_convergence(tmp_path: Path) -> None:
    vault = init_vault(tmp_path / "vault")
    code_repo = tmp_path / "my-proj"
    info = init_project(vault, "Quantum Kernel", repo_path=code_repo)

    assert (Path(info["notebook"]) / "README.md").is_file()
    assert (Path(info["notebook"]) / "HYPOTHESES.md").is_file()
    assert (code_repo / ".research-brain.toml").is_file()
    assert (code_repo / ".git" / "hooks" / "pre-commit").is_file()

    wl = append_worklog(vault, "Quantum Kernel", "exp", "Ran baseline sweep.", ["[@spec1, L.2]"])
    assert "Ran baseline sweep." in wl.read_text(encoding="utf-8")

    # Gardener defaults to ask-first and requires approval to converge
    policy = vault / "wiki" / "general" / "GARDEN_POLICY.md"
    assert get_garden_status(policy) == "ask-first"
    with pytest.raises(PermissionError):
        set_garden_converged(vault, "wiki/general", approved=False)
    set_garden_converged(vault, "wiki/general", approved=True)
    assert get_garden_status(policy) == "converged"


def test_git_pre_commit_hook_blocks_fabricated_quote(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vault = init_vault(tmp_path / "vault")
    src = tmp_path / "doc.txt"
    src.write_text("exact ground truth sentence\n", encoding="utf-8")
    ingest_source(vault, src, source_id="doc1", area="general")

    bad_note = vault / "wiki" / "general" / "bad.md"
    bad_note.write_text(
        "---\nstatus: verified\n---\n\n> \"hallucinated quote\" [@doc1, L.1]\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "wiki/general/bad.md"], cwd=vault, check=True)
    # Run hook directly via python -m research_brain.cli to verify exit code != 0
    monkeypatch.setenv("RESEARCH_BRAIN_VAULT", str(vault))
    proc = subprocess.run(
        ["python3", "-m", "research_brain.cli", "verify-quotes", "--staged"],
        cwd=vault,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "hallucinated quote" not in proc.stderr or "Verbatim quote not found" in proc.stderr
