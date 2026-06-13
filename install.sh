#!/usr/bin/env bash
# swarm++ install — auto-detects installed agents and wires up skill symlinks.
# Usage: bash install.sh [--dry-run]

set -euo pipefail

SWARM_SKILLS="$(cd "$(dirname "$0")/skills" && pwd)"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

link() {
  local target="$1" linkpath="$2"
  if $DRY_RUN; then
    echo "  [dry-run] ln -sfn $target $linkpath"
  else
    mkdir -p "$(dirname "$linkpath")"
    ln -sfn "$target" "$linkpath"
    echo "  linked: $linkpath"
  fi
}

echo "swarm++ installer"
echo "  source: $SWARM_SKILLS"
echo

# Map of: agent_binary -> skills_dir
declare -A AGENTS=(
  ["claude"]="$HOME/.claude/skills"
  ["cursor-agent"]="$HOME/.cursor/skills"
  ["kimi"]="$HOME/.kimi-code/skills"
  ["opencode"]="$HOME/.opencode/skills"
  ["codex"]="$HOME/.codex/skills"
  ["agy"]="$HOME/.gemini/config/skills"
  ["pi"]="$HOME/.pi/skills"
)

linked=0
skipped=0

for binary in "${!AGENTS[@]}"; do
  skills_dir="${AGENTS[$binary]}"
  if command -v "$binary" &>/dev/null || [ -d "$skills_dir" ]; then
    echo "✓ $binary — found"
    link "$SWARM_SKILLS" "$skills_dir/swarm"
    ((linked++)) || true
  else
    echo "  $binary — not installed, skipping"
    ((skipped++)) || true
  fi
done

echo
echo "Done. Linked into $linked agent(s), skipped $skipped."
echo
echo "To add a new agent to the fleet later, invoke the 'add-agent' skill:"
echo "  /add-agent"
