#!/bin/sh
# Portable PostToolUse hook shim for Claude Code, Cursor, and Codex.
# Reads hook JSON on stdin; if a Markdown file was written/edited, runs `rb verify-quotes` on it.
set -u

RB_BIN="$(command -v rb 2>/dev/null || true)"
if [ -z "$RB_BIN" ] && [ -x "$HOME/.local/bin/rb" ]; then
  RB_BIN="$HOME/.local/bin/rb"
fi
[ -n "$RB_BIN" ] || exit 0

PAYLOAD="$(cat 2>/dev/null || true)"
[ -n "$PAYLOAD" ] || exit 0

TARGET_FILE="$(printf '%s' "$PAYLOAD" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
inp = data.get("tool_input") or data.get("input") or {}
for key in ("file_path", "path", "Path", "target_file"):
    val = inp.get(key)
    if isinstance(val, str) and val.lower().endswith(".md"):
        print(val)
        break
' 2>/dev/null || true)"

[ -n "$TARGET_FILE" ] && [ -f "$TARGET_FILE" ] || exit 0

"$RB_BIN" verify-quotes "$TARGET_FILE"
