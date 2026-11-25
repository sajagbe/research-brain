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


def test_lint_enforces_colored_latex_ref_table_acronyms_and_provenance(tmp_path: Path) -> None:
    vault = init_vault(tmp_path / "vault")
    src = tmp_path / "eq.txt"
    src.write_text("linear response equals trace of density and operator\n", encoding="utf-8")
    ingest_source(vault, src, source_id="eqsrc", area="general")

    # Uncolored equation + missing Reference Table + unexplained acronyms (WHAM/MBAR/FCD) + uncited quantitative claim
    bad_wiki = vault / "wiki" / "general" / "bad_explain.md"
    bad_wiki.write_text(
        "---\nstatus: verified\n---\n\n"
        '> "linear response equals trace of density and operator" [@eqsrc, L.1]\n\n'
        "Run FCD and reweight with WHAM and MBAR. True superexchange coupling is tiny: |H_eff| = 8.96 x 10^-7 eV and changes < 10%.\n\n"
        "$$\nT_p = -\\operatorname{Tr}(D_0 h_p)\n$$\n",
        encoding="utf-8",
    )
    errors = [i.message for i in lint_vault(vault, target_files=[bad_wiki]) if i.severity == "error"]
    assert any("colored LaTeX annotation" in e for e in errors)
    assert any("Reference Table" in e for e in errors)
    assert any("Quantitative claim lacks provenance" in e for e in errors)

    # Has Reference Table, but still leaves MBAR undefined
    missing_acr = vault / "wiki" / "general" / "missing_acr.md"
    missing_acr.write_text(
        "---\nstatus: verified\n---\n\n"
        "## Reference Table (Symbols & Terms)\n"
        "| Symbol / Term | Color | Meaning | Units |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| **WHAM** | — | Weighted Histogram Analysis Method | — |\n\n"
        '> "linear response equals trace of density and operator" [@eqsrc, L.1]\n\n'
        "Reweight frames with WHAM and MBAR [calc: run.py].\n",
        encoding="utf-8",
    )
    acr_errors = [i.message for i in lint_vault(vault, target_files=[missing_acr]) if i.severity == "error"]
    assert any("`MBAR`" in e for e in acr_errors)
    assert not any("`WHAM`" in e for e in acr_errors)

    # Fully compliant Markdown with Reference Table (symbols + acronyms), colored equation, and provenance passes cleanly
    good_wiki = vault / "wiki" / "general" / "good_explain.md"
    good_wiki.write_text(
        "---\nstatus: verified\n---\n\n"
        "# Linear Response\n\n"
        "## Reference Table (Symbols & Terms)\n"
        "| Symbol / Term | Color | Plain-English Physical / Operational Meaning | Units / Scope |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| $\\color{#1B3A5C}{T_p}$ | `#1B3A5C` | Frozen linear rate | Ha |\n"
        "| $\\color{#00798C}{D_0}$ | `#00798C` | Equilibrium density matrix | electrons |\n"
        "| **WHAM** | — | Weighted Histogram Analysis Method combining overlapping biased windows | binned histograms |\n"
        "| **MBAR** | — | Multistate Bennett Acceptance Ratio (binless reweighting across windows) | unbinned samples |\n\n"
        '> "linear response equals trace of density and operator" [@eqsrc, L.1]\n\n'
        "We compare WHAM and MBAR; true superexchange coupling is tiny: $|H_{\\text{eff}}| = 8.96 \\times 10^{-7}$ eV (< 10% shift) [calc: scripts/coupling.py].\n\n"
        "$$\n\\color{#1B3A5C}{\\underbrace{T_p}_{\\text{linear rate}}} = -\\color{#C87D14}{\\operatorname{Tr}}(\\color{#00798C}{D_0}\\,\\color{#D1495B}{h_p})\n$$\n",
        encoding="utf-8",
    )
    assert [i for i in lint_vault(vault, target_files=[good_wiki]) if i.severity == "error"] == []
