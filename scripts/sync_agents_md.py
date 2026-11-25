"""Idempotently sync the Research Brain AGENTS.md block into global harness instruction files."""

from __future__ import annotations

import sys
from pathlib import Path

START_MARKER = "<!-- RESEARCH-BRAIN:START -->"
END_MARKER = "<!-- RESEARCH-BRAIN:END -->"


def sync_block(target: Path, body: str, frontmatter: str = "") -> None:
    block = f"{START_MARKER}\n{body.strip()}\n{END_MARKER}\n"
    target.parent.mkdir(parents=True, exist_ok=True)

    if not target.exists():
        prefix = f"{frontmatter.strip()}\n\n" if frontmatter else ""
        target.write_text(prefix + block, encoding="utf-8")
        return

    existing = target.read_text(encoding="utf-8")
    if START_MARKER in existing and END_MARKER in existing:
        before, rest = existing.split(START_MARKER, 1)
        _, after = rest.split(END_MARKER, 1)
        updated = before + block + after.lstrip("\n")
        target.write_text(updated, encoding="utf-8")
    else:
        sep = "\n\n" if existing and not existing.endswith("\n\n") else ""
        target.write_text(existing + sep + block, encoding="utf-8")


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: sync_agents_md.py <path-to-AGENTS.md>", file=sys.stderr)
        return 1

    agents_src = Path(sys.argv[1]).resolve()
    body = agents_src.read_text(encoding="utf-8")
    home = Path.home()

    targets: list[tuple[Path, str]] = [
        (home / ".codex" / "AGENTS.md", ""),
        (home / ".claude" / "CLAUDE.md", ""),
        (home / ".gemini" / "GEMINI.md", ""),
        (home / ".config" / "opencode" / "AGENTS.md", ""),
        (
            home / ".cursor" / "rules" / "research-brain.mdc",
            "---\ndescription: Research Brain operating discipline and skill pointers\nalwaysApply: true\n---",
        ),
    ]

    for target, fm in targets:
        # Only sync into harnesses whose parent config root exists (plus .agents/gemini/codex/claude)
        if target.parent.parent.exists() or target.parent.exists():
            sync_block(target, body, frontmatter=fm)
            print(f"Synced AGENTS.md -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
