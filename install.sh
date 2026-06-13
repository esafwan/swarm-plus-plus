#!/usr/bin/env bash
# swarm++ install — auto-detects installed agents and wires up skill symlinks.
#
# Creates two levels of symlinks per agent:
#   1. Bundle:     ~/.<agent>/skills/swarm       -> this repo's skills/ dir
#   2. Individual: ~/.<agent>/skills/<skill-name> -> each skill dir directly
#
# Individual symlinks guarantee /skill-name works in every agent regardless
# of how deep each agent scans its skills directory.
#
# Usage:
#   bash install.sh            # install
#   bash install.sh --dry-run  # preview without changes

set -euo pipefail

SWARM_SKILLS="$(cd "$(dirname "$0")/skills" && pwd)"
DRY_RUN=false
if [ "${1:-}" = "--dry-run" ]; then DRY_RUN=true; fi

do_link() {
  local target="$1" linkpath="$2"
  if [ "$DRY_RUN" = "true" ]; then
    echo "    [dry-run] ln -sfn $target $linkpath"
  else
    mkdir -p "$(dirname "$linkpath")"
    ln -sfn "$target" "$linkpath"
    echo "    linked: $(basename "$linkpath")"
  fi
}

echo "swarm++ installer"
echo "  source: $SWARM_SKILLS"
echo

# "binary:skills_dir" pairs — one per line
AGENTS="claude:$HOME/.claude/skills
cursor-agent:$HOME/.cursor/skills
kimi:$HOME/.kimi-code/skills
opencode:$HOME/.opencode/skills
codex:$HOME/.codex/skills
agy:$HOME/.gemini/config/skills
pi:$HOME/.pi/skills"

while IFS=: read -r binary skills_dir; do
  if command -v "$binary" >/dev/null 2>&1 || [ -d "$skills_dir" ]; then
    echo "✓ $binary"
    # 1. Bundle symlink
    do_link "$SWARM_SKILLS" "$skills_dir/swarm"
    # 2. Individual skill symlinks
    for skill_dir in "$SWARM_SKILLS"/*/; do
      skill_name="$(basename "$skill_dir")"
      do_link "$skill_dir" "$skills_dir/$skill_name"
    done
  else
    echo "  $binary — not installed, skipping"
  fi
done <<< "$AGENTS"

echo
echo "Skills now available as slash commands in every linked agent:"
for skill_dir in "$SWARM_SKILLS"/*/; do
  echo "  /$(basename "$skill_dir")"
done
echo
echo "To add a new agent to the fleet:  /add-agent"
