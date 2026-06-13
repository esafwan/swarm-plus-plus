# swarm-plus-plus

> Resilient multi-agent orchestration — work continues no matter what.

**swarm++** coordinates a fleet of local coding-agent CLIs so that a task never
stalls due to token limits, rate limits, or agent failures. It routes by cost
and capability, splits oversized work to dodge context caps, retries with
backoff, and fails over to the next agent — preserving progress across every
handoff.

Because each CLI has its **own provider account and token budget**, spreading
work across binaries is itself the primary way around any single provider's
limits.

---

## Skills in this repo

| Skill | Purpose |
| :--- | :--- |
| [`swarm-plus-plus`](skills/swarm-plus-plus/SKILL.md) | Master orchestration policy — routing ladder, failure loop, fan-out patterns |
| [`add-agent`](skills/add-agent/SKILL.md) | Onboard any new agent CLI into the swarm++ fleet via `--help` discovery |
| [`claude-overview`](skills/claude-overview/SKILL.md) | Claude Code CLI — all flags, models, effort levels, MCP, sessions, sub-agents |
| [`cursor-overview`](skills/cursor-overview/SKILL.md) | Cursor CLI (`cursor-agent`) — flags, models, thinking levels, worktrees, MCP |
| [`kimi-overview`](skills/kimi-overview/SKILL.md) | Kimi Code CLI — flags, models, thinking levels, sessions, sub-agents |
| [`opencode-overview`](skills/opencode-overview/SKILL.md) | OpenCode CLI — flags, Ollama/multi-provider models, agents, MCP |
| [`antigravity-overview`](skills/antigravity-overview/SKILL.md) | Antigravity (`agy`) — flags, Gemini/Claude models, thinking levels, sub-agents |

All overview skills are installed as individual slash commands (e.g. `/claude-overview`,
`/kimi-overview`) so any agent in the fleet can look up how to invoke any other agent.

---

## Supported agents (out of the box)

| Agent | Binary | Best for |
| :--- | :--- | :--- |
| **Pi** | `pi` | Cheapest local edits (Ollama / GPT-OSS) |
| **Claude Code** | `claude` | Strong general coding, deep reasoning |
| **Cursor** | `cursor-agent` | Fast multi-file edits, Composer models |
| **Kimi** | `kimi` | Large / complex implementation, repo-heavy loops |
| **OpenCode** | `opencode` | Multi-provider, local Ollama fallback |
| **Antigravity** | `agy` | Gemini / Claude via Google SDK, sub-agent branching |
| **Codex** *(optional)* | `codex` | GPT-Codex implementation |
| **Gemini** *(optional)* | `gemini` | Gemini reasoning |

New agents can be added at any time with the `add-agent` skill.

---

## Install

```bash
git clone git@github.com:esafwan/swarm-plus-plus.git ~/.ai-skills/swarm
bash ~/.ai-skills/swarm/install.sh
```

`install.sh` auto-detects which agent CLIs are installed on your machine and
creates **two levels of symlinks** per agent:

- `~/.claude/skills/swarm/` — the whole pack under one namespace
- `~/.claude/skills/swarm-plus-plus/` — individual skill at root
- `~/.claude/skills/claude-overview/` — individual skill at root
- … one per skill, for every agent found

This guarantees `/skill-name` works in every agent regardless of how deep it
scans its skills directory.

Preview what it will do without making changes:

```bash
bash ~/.ai-skills/swarm/install.sh --dry-run
```

Editing `~/.ai-skills/swarm/skills/` propagates to every linked agent instantly
— no re-install needed.

---

## How it works (TL;DR)

```
Pi → OpenCode-local → Kimi / Cursor → Claude(sonnet) → Claude(opus)/agy → Claude(fable)
cheap, local          mid              strong             deep               max
```

1. **Plan** — split the task into small, file-scoped steps; persist state to disk.
2. **Route** — start each step at the cheapest agent that can plausibly do it.
3. **Fail over** — on rate/token/failure: classify → split or backoff → climb the ladder.
4. **Fan out** — run independent chunks in parallel across binaries (separate token budgets).
5. **Report** — only stop when the whole ladder is exhausted; never stall silently.

---

## Adding a new agent

Use the `add-agent` skill — it discovers the binary, reads its `--help`, and
writes the fleet entry plus an overview SKILL.md:

```
/add-agent
```

Then follow the prompts or describe the agent in your message.

---

## License

MIT
