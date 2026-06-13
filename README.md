# swarm-plus-plus

**swarm++** — a master orchestration skill that coordinates a fleet of local
coding-agent CLIs (Claude Code, Cursor, Kimi, OpenCode, Pi, Antigravity, and
optionally Codex/Gemini) so that work continues **no matter what** — through
token limits, rate limits, and agent failures.

It routes by cost and capability, splits oversized tasks to dodge context caps,
retries with backoff, and fails over to a different agent so progress never
stalls. Because each CLI has its own provider account and token budget, spreading
work across binaries is itself the way around any single provider's limits.

## What's here

- `skills/swarm-plus-plus/SKILL.md` — the skill (policy + playbook).

## Install

This follows the portable "shared skills" convention: keep the source in one
place and symlink it into each agent's skills directory.

```bash
# 1. Clone anywhere (e.g. ~/.ai-skills/swarm)
git clone git@github.com:esafwan/swarm-plus-plus.git ~/.ai-skills/swarm

# 2. Symlink into whichever agents you use
ln -sfn ~/.ai-skills/swarm/skills ~/.claude/skills/swarm
ln -sfn ~/.ai-skills/swarm/skills ~/.cursor/skills/swarm
ln -sfn ~/.ai-skills/swarm/skills ~/.kimi-code/skills/swarm
ln -sfn ~/.ai-skills/swarm/skills ~/.opencode/skills/swarm
ln -sfn ~/.ai-skills/swarm/skills ~/.codex/skills/swarm
ln -sfn ~/.ai-skills/swarm/skills ~/.gemini/config/skills/swarm
```

Each agent then discovers `swarm-plus-plus` as a skill. Editing the source file
propagates to every agent through the symlinks.

## How it works (TL;DR)

1. Plan → split into small, file-scoped steps with disk-persisted state.
2. Start each step at the cheapest capable agent.
3. On rate/token/failure: classify → split or backoff → climb the agent ladder.
4. Spread chunks across binaries to dodge any single provider's limits.
5. Never stall silently; only stop once the whole ladder is exhausted, then report.

See the skill for the full routing ladder, failure-handling loop, and examples.

## License

MIT
