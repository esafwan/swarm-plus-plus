---
name: cursor-overview
description: >
  Comprehensive overview of the Cursor coding agent — IDE agent (Composer) and
  CLI (`cursor-agent` / `agent`). Covers binary paths, flags, prompt passing,
  model selection, thinking/reasoning levels, execution modes, sessions, skills,
  sub-agents, MCP, sandbox, worktrees, and programmatic SDK usage. Use whenever
  another agent needs to invoke, orchestrate, or understand Cursor agent
  behavior. Keywords: cursor, composer, cursor-agent, agent cli, subagent, Task
  tool, --print, --model, plan mode, skills, .cursor/agents.
license: MIT
compatibility: "Cursor IDE, Cursor CLI, Claude Code, Kimi Code, Codex, OpenCode, Gemini, Antigravity."
metadata:
  author: Cursor
  version: "1.0"
---

# Cursor — Coding Agent Overview

Cursor is an AI coding agent available in two surfaces:

| Surface | What it is | When to use |
| :--- | :--- | :--- |
| **Cursor IDE** | GUI agent chat (Composer) inside the editor | Interactive pair-programming, multi-file edits, visual diffs |
| **Cursor CLI** | Terminal agent (`cursor-agent`, also `agent`) | Scripts, CI, headless automation, SSH/remote shells |

Both surfaces share models, tools (read/write files, shell, MCP, web), skills,
sub-agents, and session concepts. This skill documents how to run each surface,
pass prompts, pick models/thinking levels, delegate to sub-agents, and load
skills.

---

## CLI Path & Executable

- **Primary binary**: ``cursor-agent`` (on PATH)
- **Alias**: ``agent`` (on PATH) → same binary
- **Resolved binary**: `
- **Config directory**: `~/.cursor/`
  - `cli-config.json` — CLI runtime settings (model, permissions, sandbox, display)
  - `skills/` — user skills (symlink-friendly; see Skills System)
  - `skills-cursor/` — Cursor-managed built-in skills (**do not edit**)
  - `agents/` — user-level custom subagent definitions
  - `chats/` — persisted CLI chat sessions
  - `projects/` — per-project metadata

Run from anywhere:

```bash
cursor-agent          # or: agent
```

---

## Quick Start Reference

```bash
# Interactive
cursor-agent                                    # Start interactive agent session
cursor-agent "Refactor the auth module"        # Interactive with initial prompt

# Headless / one-shot (print mode)
cursor-agent -p "Explain this codebase"         # Print final response to stdout
cursor-agent -p "Fix the bug" --output-format json
cursor-agent -p "Fix the bug" --output-format stream-json --stream-partial-output

# Model & thinking
cursor-agent --model composer-2.5-fast -p "Quick refactor"
cursor-agent --model claude-opus-4-8-thinking-high -p "Deep architecture review"
cursor-agent --model gpt-5.3-codex-high -p "Implement the parser"
cursor-agent --list-models                      # List all available model IDs

# Execution modes
cursor-agent --plan -p "Design a migration plan"    # Read-only planning
cursor-agent --mode ask -p "How does auth work?"    # Read-only Q&A

# Sessions
cursor-agent --continue                         # Continue previous session
cursor-agent --resume                           # Pick a session interactively
cursor-agent --resume <chatId>                  # Resume specific chat
cursor-agent ls                                 # List/resume chats
cursor-agent resume                             # Resume latest chat

# Permissions (non-interactive)
cursor-agent -p "Run tests" --trust             # Trust workspace (headless only)
cursor-agent -p "Run tests" --force             # Auto-approve tool calls (Run Everything)
cursor-agent -p "Run tests" --yolo              # Alias for --force
cursor-agent -p "..." --approve-mcps            # Auto-approve MCP servers

# Isolation
cursor-agent -w                                 # Start in isolated git worktree
cursor-agent -w feature-x --worktree-base main  # Named worktree from branch
cursor-agent --workspace /path/to/project -p "..."
cursor-agent --sandbox enabled -p "..."           # Force sandbox on

# Auth & maintenance
cursor-agent login
cursor-agent status
cursor-agent models
cursor-agent about
cursor-agent update
```

---

## Command Line Flags

Run `cursor-agent --help` for the authoritative list.

| Flag / Option | Alias | Description |
| :--- | :--- | :--- |
| `--print` | `-p` | Headless mode: run prompt, print response, exit. Full tool access including write and shell. |
| `--output-format <fmt>` | | With `-p`: `text` (default), `json`, or `stream-json`. |
| `--stream-partial-output` | | With `-p` + `stream-json`: emit text deltas as they arrive. |
| `--model <id>` | | Model ID (see Model Selection). Use `--list-models` or `cursor-agent models`. |
| `--list-models` | | Print available models and exit. |
| `--mode <mode>` | | `plan` (read-only planning) or `ask` (read-only Q&A). |
| `--plan` | | Shorthand for `--mode=plan`. |
| `--continue` | | Continue the previous session. |
| `--resume [chatId]` | | Resume a session (with ID) or pick interactively (without). |
| `--force` | `-f` | Run Everything: auto-approve tool calls unless explicitly denied. |
| `--yolo` | | Alias for `--force`. |
| `--trust` | | Trust workspace without prompting (**headless `-p` only**). |
| `--sandbox <mode>` | | Override sandbox: `enabled` or `disabled`. |
| `--approve-mcps` | | Auto-approve all MCP servers. |
| `--workspace <path>` | | Working directory (default: cwd). |
| `--worktree [name]` | `-w` | Isolated git worktree at `~/.cursor/worktrees/<repo>/<name>`. |
| `--worktree-base <ref>` | | Base branch/ref for new worktree (default: current HEAD). |
| `--skip-worktree-setup` | | Skip `.cursor/worktrees.json` setup scripts. |
| `--plugin-dir <path>` | | Load local plugin directory (repeatable). |
| `--api-key <key>` | | API key (or set `CURSOR_API_KEY` env var). |
| `-H, --header <hdr>` | | Custom request header (`Name: Value`, repeatable). |
| `--version` | `-v` | Print CLI version. |

Positional `[prompt...]` arguments set the initial prompt in interactive mode.

### Subcommands

```bash
cursor-agent login / logout / status / whoami
cursor-agent models / about / update
cursor-agent create-chat                         # Create empty chat, return ID
cursor-agent ls / resume                         # Session management
cursor-agent generate-rule / rule                # Interactive Cursor rule generator
cursor-agent mcp login|list|list-tools|enable|disable
cursor-agent worker                              # Private cloud worker (connects to Cursor)
cursor-agent install-shell-integration           # Add integration to ~/.zshrc
```

---

## Model Selection & Thinking (Reasoning) Levels

Models are selected by **exact ID string**. Run `cursor-agent models` for the
current account list.

### Naming Conventions

| Pattern in model ID | Meaning |
| :--- | :--- |
| `*-thinking-*` or `*-thinking` | Extended reasoning / thinking mode enabled |
| `*-low`, `*-medium`, `*-high`, `*-xhigh`, `*-max` | Reasoning effort tier |
| `*-fast` | Lower-latency variant of the same tier |
| `composer-*` | Cursor Composer models (optimized for agentic coding) |
| `gpt-*-codex-*` | OpenAI Codex-family coding models |
| `claude-*-thinking-*` | Anthropic models with thinking |
| `auto` | Cursor picks the model automatically |

### Common Model IDs (examples)

| Model ID | Role |
| :--- | :--- |
| `composer-2.5-fast` | Default fast agentic coding (Composer 2.5) |
| `composer-2.5` | Composer 2.5 (standard) |
| `auto` | Automatic model routing |
| `gpt-5.3-codex` / `gpt-5.3-codex-high` | Codex 5.3 (medium / high reasoning) |
| `claude-4.6-sonnet-medium-thinking` | Sonnet 4.6 with thinking |
| `claude-opus-4-8-thinking-high` | Opus 4.8 deep reasoning |
| `claude-fable-5-thinking-high` | Fable 5 thinking |
| `gpt-5.5-medium` / `gpt-5.5-high` | GPT-5.5 with effort tier |
| `kimi-k2.5` | Kimi K2.5 |

### Examples

```bash
# Fast everyday coding
cursor-agent --model composer-2.5-fast -p "Add input validation to the form"

# Deep reasoning / architecture
cursor-agent --model claude-opus-4-8-thinking-high -p "Review security of the auth flow"

# Codex for implementation-heavy tasks
cursor-agent --model gpt-5.3-codex-high -p "Implement the SQLite FTS backend"

# In interactive mode, switch mid-session with /model <id>
```

### Model Parameters (CLI config)

Some models accept parameters stored in `~/.cursor/cli-config.json` under
`modelParameters` and `selectedModel.parameters`. Example: Composer 2.5 supports
a `fast` parameter. Prefer `--model` on the command line for one-off overrides;
use `cli-config.json` for session defaults.

---

## Execution Modes

| Mode | Flag | Tools | Use for |
| :--- | :--- | :--- | :--- |
| **Agent** (default) | — | Full read/write/shell/MCP | Implementation, fixes, refactors |
| **Plan** | `--plan` / `--mode plan` | Read-only | Architecture, migration plans, tradeoffs |
| **Ask** | `--mode ask` | Read-only | Explanations, Q&A, code understanding |

In the IDE, use **Agent mode** vs **Plan mode** vs **Ask mode** from the mode
picker in the chat UI (equivalent to CLI `--mode`).

---

## Prompt Passing

| Method | Example | Behavior |
| :--- | :--- | :--- |
| Positional (interactive) | `cursor-agent "Fix the login bug"` | Starts session with initial prompt |
| `-p` / `--print` (headless) | `cursor-agent -p "Fix the login bug"` | Runs to completion, prints response, exits |
| Interactive typing | `cursor-agent` then type | Multi-turn conversation |
| IDE chat | Type in Composer panel | Multi-turn with editor context |

Headless tips:

- Combine `-p` with `--trust` in CI/scripts so workspace trust is not prompted.
- Use `--output-format stream-json --stream-partial-output` for streaming integrations.
- `-p` has full tool access (writes, shell) — not a read-only mode.

---

## Sessions

CLI sessions persist under `~/.cursor/chats/`.

| Action | Command |
| :--- | :--- |
| Continue previous session | `cursor-agent --continue` |
| Resume latest | `cursor-agent resume` |
| Resume specific chat | `cursor-agent --resume <chatId>` |
| Pick session interactively | `cursor-agent --resume` or `cursor-agent ls` |
| Create empty chat (get ID) | `cursor-agent create-chat` |

IDE sessions are tied to the Cursor editor workspace and appear in the chat
history sidebar.

---

## Permission & Approval Modes

| Mode | How | Behavior |
| :--- | :--- | :--- |
| **Allowlist** (default) | `approvalMode: "allowlist"` in `cli-config.json` | Prompt for tools not on the allow list |
| **Run Everything** | `--force` / `--yolo` / non-allowlist approval mode | Auto-approve tool calls |
| **Trust workspace** | `--trust` (with `-p` only) | Skip workspace trust prompt |
| **Sandbox** | `--sandbox enabled` or config | Restricted shell/network environment |

Configure persistent permissions in `~/.cursor/cli-config.json`:

```json
{
  "permissions": {
    "allow": ["Shell(**)"],
    "deny": []
  },
  "approvalMode": "allowlist",
  "sandbox": { "mode": "disabled" }
}
```

Project-level overrides: `.cursor/cli.json` (merged from git root → cwd; deeper
wins; session-only, not written back to home config).

---

## Skills System

Skills teach the agent specialized workflows via `SKILL.md` files.

### Storage Locations

| Scope | Path | Notes |
| :--- | :--- | :--- |
| **User** | `~/.cursor/skills/<skill-name>/SKILL.md` | Available in all projects |
| **Project** | `.cursor/skills/<skill-name>/SKILL.md` | Shared via version control |
| **Built-in** | `~/.cursor/skills-cursor/` | Cursor-managed — **never create skills here** |
| **Global cross-agent** | `~/.ai-skills/<agent>/skills/` + symlinks | Shared across Claude, Kimi, Codex, etc. |

Each skill is a directory with a `SKILL.md` containing YAML frontmatter (`name`,
`description`) and markdown instructions.

### Global Skill Symlinks (this machine)

Other agents can load Cursor docs via:

```
~/.ai-skills/cursor/skills/   ← source of truth
~/.claude/skills/cursor       → symlink
~/.kimi-code/skills/cursor    → symlink
~/.codex/skills/cursor        → symlink
~/.opencode/skills/cursor     → symlink
~/.gemini/config/skills/cursor → symlink
~/.cursor/skills/cursor       → symlink
```

---

## Sub-agents & Task Delegation

Cursor supports two sub-agent mechanisms:

### 1. Built-in Task Sub-agents (IDE & CLI)

The parent agent delegates via the **Task** tool. Each sub-agent runs in an
isolated context with its own tools and prompt.

#### Built-in Sub-agent Types

| `subagent_type` | Purpose |
| :--- | :--- |
| `generalPurpose` | General research and multi-step tasks |
| `cursor-guide` | Cursor product docs (Desktop, IDE, CLI, Cloud Agents, Bugbot) |
| `haiku-fast-discovery` | Cheap/fast: repo search, grep, config inspection, log reading |
| `kimi-primary-coding-agent` | Primary coding agent for larger implementations |
| `sonnet-kimi-steering-review` | Review/steer Kimi output, write tests, verify diffs |
| `opus-architect-reviewer` | Hard architecture, deep debugging, security review |
| `pi-code-ollama-worker` | Cheap local coding via Pi + Ollama |
| `best-of-n-runner` | Isolated git worktree for parallel attempts |
| `fable-orchestration-policy` | Top-level routing across agent tiers |

#### Task Tool Parameters

| Parameter | Description |
| :--- | :--- |
| `description` | Short title (3–5 words) for UI |
| `prompt` | Full task prompt — sub-agent has **no** parent context; include everything |
| `subagent_type` | One of the built-in types above |
| `model` | Optional model override (must be from allowed subagent model list) |
| `resume` | Agent ID to continue a previous sub-agent |
| `run_in_background` | Detach; parent gets notified on completion |
| `readonly` | Restrict to read-only (Ask mode) |

#### Allowed Sub-agent Models (when `model` is set)

Only these slugs are valid for Task sub-agents:

- `claude-4.6-sonnet-medium-thinking`
- `claude-fable-5-thinking-high`
- `claude-opus-4-8-thinking-high`
- `composer-2.5-fast`
- `gpt-5.3-codex`
- `gpt-5.5-medium`

If the user requests an unavailable model, do not substitute — report which
models are available.

#### Sub-agent Best Practices

- Launch **multiple Task calls in parallel** when tasks are independent.
- Put file paths, commands, and prior findings **in the prompt** (sub-agents start fresh).
- Use `haiku-fast-discovery` for search-heavy work; `kimi-primary-coding-agent`
  for multi-file implementation; `opus-architect-reviewer` for hard design/debug.
- Use `resume` to continue a sub-agent instead of re-spawning.
- Do not poll background agents — continue other work; notification arrives on completion.

### 2. Custom Sub-agents (`.cursor/agents/`)

Define reusable subagents as markdown files with YAML frontmatter:

| Location | Scope |
| :--- | :--- |
| `.cursor/agents/<name>.md` | Project (check into git) |
| `~/.cursor/agents/<name>.md` | User (all projects) |

```markdown
---
name: code-reviewer
description: Expert code review. Use proactively after code changes.
---

You are a senior code reviewer. When invoked, run git diff, focus on modified
files, and return prioritized feedback (critical / warning / suggestion).
```

Project agents override user agents when names collide.

---

## MCP (Model Context Protocol)

Configure MCP servers in `~/.cursor/mcp.json` or `.cursor/mcp.json`.

```bash
cursor-agent mcp list
cursor-agent mcp list-tools <identifier>
cursor-agent mcp login <identifier>
cursor-agent mcp enable <identifier>
cursor-agent mcp disable <identifier>
```

Use `--approve-mcps` in headless mode to skip MCP approval prompts.

---

## Git Worktree Isolation

Use worktrees for isolated agent runs without touching the main working tree:

```bash
cursor-agent -w my-experiment -p "Try a different approach to caching"
cursor-agent -w --worktree-base develop -p "Prototype on develop"
```

Worktrees live at `~/.cursor/worktrees/<reponame>/<name>`. Setup hooks can be
defined in `.cursor/worktrees.json`.

---

## Programmatic Usage (Cursor SDK)

For scripts, CI, GitHub Actions, and backend services **outside** the IDE/CLI
interactive loop, use the Cursor SDK:

- **TypeScript**: `@cursor/sdk` (npm)
- **Python**: `cursor-sdk` (pip)

Quick patterns:

```typescript
// One-shot
import { Agent } from "@cursor/sdk";
const result = await Agent.prompt("Refactor auth.ts", {
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "composer-2.5" },
  local: { cwd: process.cwd() },
});
```

```python
# One-shot
from cursor_sdk import Agent, AgentOptions, LocalAgentOptions
result = Agent.prompt(
    "Refactor auth.py",
    AgentOptions(
        api_key=os.environ["CURSOR_API_KEY"],
        model="composer-2.5",
        local=LocalAgentOptions(cwd=os.getcwd()),
    ),
)
```

For SDK details, read the `sdk` skill in `~/.cursor/skills-cursor/sdk/SKILL.md`.

---

## IDE-Specific Features (Composer)

When running inside Cursor IDE (not CLI):

- **Editor context**: open files, selections, diagnostics, and `@` references
  are automatically available.
- **Diffs**: agent edits appear as reviewable diffs before apply.
- **Background agents**: Cloud Agents run asynchronously on Cursor infrastructure.
- **Rules**: `.cursor/rules/` and `AGENTS.md` / `CLAUDE.md` provide persistent
  project instructions.
- **Hooks**: `.cursor/hooks.json` automates agent lifecycle events.
- **Canvas**: agent can render rich interactive UI in the editor panel.

---

## Configuration Reference

| File | Purpose |
| :--- | :--- |
| `~/.cursor/cli-config.json` | CLI defaults: model, permissions, sandbox, display |
| `.cursor/cli.json` | Per-project CLI overrides (layered from repo root) |
| `~/.cursor/mcp.json` | User MCP server definitions |
| `.cursor/mcp.json` | Project MCP servers |
| `.cursor/rules/` | Cursor rules (`.mdc` / markdown) |
| `AGENTS.md` / `CLAUDE.md` | Project-level agent instructions |

Key `cli-config.json` fields: `permissions`, `approvalMode`, `sandbox`, `model`,
`modelParameters`, `display.showThinkingBlocks`, `attribution`.

For detailed CLI config editing, see the `update-cli-config` skill.

---

## Troubleshooting

| Issue | Fix |
| :--- | :--- |
| Not authenticated | `cursor-agent login` |
| Check auth / account | `cursor-agent status` or `cursor-agent about` |
| List models | `cursor-agent models` or `--list-models` |
| Update CLI | `cursor-agent update` |
| MCP not loading | `cursor-agent mcp list` — enable/login as needed |
| Permission prompts in CI | Use `-p --trust --force` (and `--approve-mcps` if using MCP) |
| Wrong model | Verify exact ID with `cursor-agent models` |

---

## Related Skills

| Skill | Location | Topic |
| :--- | :--- | :--- |
| `sdk` | `~/.cursor/skills-cursor/sdk/` | Programmatic Agent SDK |
| `update-cli-config` | `~/.cursor/skills-cursor/update-cli-config/` | CLI config fields |
| `create-skill` | `~/.cursor/skills-cursor/create-skill/` | Authoring skills |
| `create-subagent` | `~/.cursor/skills-cursor/create-subagent/` | Custom `.cursor/agents/` |
| `create-rule` | `~/.cursor/skills-cursor/create-rule/` | Cursor rules |
| `create-hook` | `~/.cursor/skills-cursor/create-hook/` | Agent hooks |
| `babysit` | `~/.cursor/skills-cursor/babysit/` | PR/CI triage loop |
| `split-to-prs` | `~/.cursor/skills-cursor/split-to-prs/` | Split work into PRs |

Official docs: https://cursor.com/docs
