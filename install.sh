#!/usr/bin/env bash
# Portable, idempotent installer for Research Brain + pstack across macOS and Linux (local & remote).
# Usage:
#   ./install.sh [--vault PATH] [--skip-pstack] [--with-harness-hooks]
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_PATH="${RESEARCH_BRAIN_VAULT:-}"
SKIP_PSTACK=0
WITH_HARNESS_HOOKS=0

while [ $# -gt 0 ]; do
  case "$1" in
    --vault) VAULT_PATH="$2"; shift 2 ;;
    --skip-pstack) SKIP_PSTACK=1; shift ;;
    --with-harness-hooks) WITH_HARNESS_HOOKS=1; shift ;;
    -h|--help)
      echo "Usage: ./install.sh [--vault PATH] [--skip-pstack] [--with-harness-hooks]"
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

step() { printf '\n== %s\n' "$1"; }

step "1. Ensure uv & install rb CLI"
UV="$(command -v uv 2>/dev/null || true)"
if [ -z "$UV" ]; then
  for c in "$HOME/.local/bin/uv" "$HOME/.cargo/bin/uv" "/opt/homebrew/bin/uv"; do
    [ -x "$c" ] && UV="$c" && break
  done
fi
if [ -z "$UV" ]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  UV="$HOME/.local/bin/uv"
fi
"$UV" tool install --force --editable "$REPO_DIR"
RB_BIN="$("$UV" tool dir --bin)/rb"
echo "Installed rb -> $RB_BIN ($("$RB_BIN" --version))"

step "2. Fetch/update companion pstack skills (cursor/plugins)"
PSTACK_CACHE="$HOME/.local/share/research-brain/cursor-plugins"
if [ "$SKIP_PSTACK" -eq 0 ]; then
  if [ -d "$PSTACK_CACHE/.git" ]; then
    git -C "$PSTACK_CACHE" pull --ff-only -q || echo "Warning: offline; using cached pstack."
  else
    mkdir -p "$(dirname "$PSTACK_CACHE")"
    if GIT_TERMINAL_PROMPT=0 git clone --depth 1 --filter=blob:none --sparse \
      https://github.com/cursor/plugins.git "$PSTACK_CACHE" >/dev/null 2>&1; then
      git -C "$PSTACK_CACHE" sparse-checkout set pstack/skills >/dev/null 2>&1
      echo "Fetched pstack skills -> $PSTACK_CACHE/pstack/skills"
    else
      echo "Warning: could not reach github.com/cursor/plugins; skipping pstack fetch."
    fi
  fi
fi

step "3. Symlink Research Brain & pstack skills across detected harnesses"
HARNESS_DIRS=(
  "$HOME/.agents/skills"
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.cursor/skills"
  "$HOME/.opencode/skills"
  "$HOME/.gemini/config/skills"
)

for target_dir in "${HARNESS_DIRS[@]}"; do
  parent_root="$(dirname "$target_dir")"
  # Always create ~/.agents/skills; create others when their harness directory exists
  if [ "$target_dir" = "$HOME/.agents/skills" ] || [ -d "$parent_root" ]; then
    mkdir -p "$target_dir"
    for skill_path in "$REPO_DIR"/skills/*; do
      [ -d "$skill_path" ] || continue
      skill_name="$(basename "$skill_path")"
      ln -sfn "$skill_path" "$target_dir/$skill_name"
    done
    # Also symlink pstack skills into harnesses that don't already have them
    if [ -d "$PSTACK_CACHE/pstack/skills" ]; then
      if [ "$target_dir" = "$HOME/.gemini/config/skills" ] && [ -d "$HOME/.gemini/config/plugins/pstack-skills" ]; then
        : # Antigravity already loads pstack via ~/.gemini/config/plugins/pstack-skills
      else
        for pskill in "$PSTACK_CACHE"/pstack/skills/*; do
          [ -d "$pskill" ] || continue
          pname="$(basename "$pskill")"
          # Do not overwrite an existing non-broken skill or plugin-managed copy
          if [ ! -e "$target_dir/$pname" ]; then
            ln -sfn "$pskill" "$target_dir/$pname"
          fi
        done
      fi
    fi
    echo "Linked skills -> $target_dir"
  fi
done

step "4. Sync centralized AGENTS.md across harnesses"
python3 "$REPO_DIR/scripts/sync_agents_md.py" "$REPO_DIR/AGENTS.md"

step "5. Initialize Global Research Brain Vault"
if [ -n "$VAULT_PATH" ]; then
  "$RB_BIN" init-vault --path "$VAULT_PATH"
else
  "$RB_BIN" init-vault
fi

if [ "$WITH_HARNESS_HOOKS" -eq 1 ]; then
  step "6. Install thin harness PostToolUse hooks (Claude Code & Cursor)"
  chmod +x "$REPO_DIR/hooks/post-write-verify.sh"
  python3 "$REPO_DIR/scripts/install_harness_hooks.py" "$REPO_DIR/hooks/post-write-verify.sh"
fi

step "Done"
"$RB_BIN" doctor
