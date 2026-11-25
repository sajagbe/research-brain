"""Safely and idempotently register the thin Research Brain post-write quote-check hook in Claude Code and Cursor."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

TAG = "research-brain/hooks/post-write-verify.sh"


def _patch_claude(settings_path: Path, hook_cmd: str) -> bool:
    if not settings_path.is_file():
        return False
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    hooks = data.setdefault("hooks", {})
    post_list = hooks.setdefault("PostToolUse", [])

    for entry in post_list:
        for h in entry.get("hooks", []):
            if TAG in str(h.get("command", "")):
                return False

    shutil.copy2(settings_path, settings_path.with_suffix(".json.rb-bak"))
    post_list.append(
        {
            "matcher": "Write|Edit|MultiEdit",
            "hooks": [
                {
                    "type": "command",
                    "command": hook_cmd,
                    "timeout": 10,
                }
            ],
        }
    )
    settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def _patch_cursor(hooks_path: Path, hook_cmd: str) -> bool:
    if not hooks_path.is_file():
        return False
    data = json.loads(hooks_path.read_text(encoding="utf-8"))
    hooks = data.setdefault("hooks", {})
    post_list = hooks.setdefault("postToolUse", [])

    for entry in post_list:
        if TAG in str(entry.get("command", "")):
            return False

    shutil.copy2(hooks_path, hooks_path.with_suffix(".json.rb-bak"))
    post_list.append({"command": hook_cmd, "timeout": 10})
    hooks_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: install_harness_hooks.py <path-to-post-write-verify.sh>", file=sys.stderr)
        return 1
    hook_cmd = str(Path(sys.argv[1]).resolve())
    home = Path.home()

    if _patch_claude(home / ".claude" / "settings.json", hook_cmd):
        print("Installed Claude Code PostToolUse hook -> ~/.claude/settings.json")
    else:
        print("Claude Code PostToolUse hook already installed (or settings.json absent).")

    if _patch_cursor(home / ".cursor" / "hooks.json", hook_cmd):
        print("Installed Cursor postToolUse hook -> ~/.cursor/hooks.json")
    else:
        print("Cursor postToolUse hook already installed (or hooks.json absent).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
