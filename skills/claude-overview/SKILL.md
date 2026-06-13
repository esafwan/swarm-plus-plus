---
name: claude-overview
description: >
  Comprehensive overview of the Claude Code CLI (`claude`). Covers binary path,
  config files, flags, prompt passing, model selection, effort/thinking levels,
  permission modes, agents and sub-agents, MCP servers, sessions, skills, and
  general CLI usage. Use this skill whenever another agent needs to invoke,
  orchestrate, or understand Claude Code behavior.
license: MIT
compatibility: "Claude Code CLI, Cursor CLI, Kimi Code, Codex, OpenCode, Gemini, Antigravity."
metadata:
  author: Claude-Code-CLI
  version: "1.0"
---

# Claude Code — Coding Agent CLI Overview

Claude Code (`claude`) is Anthropic's terminal-based autonomous coding agent. It
reads and writes files, runs shell commands, uses MCP servers, delegates to
sub-agents, and supports structured output and multiple model aliases.

---

## CLI Path & Executable

- **Primary Binary Path**: ``claude`` (on PATH)
- **Resolved Binary**: `
- **Version**: `2.1.177 (Claude Code)`
- **Config Directory**: `~/.claude/`
  - `settings.json` — user settings (model, effort level, theme)
  - `sessions/` — persisted conversation sessions
  - `projects/` — per-project state
  - `skills/` — discovered skills (symlink-friendly)
  - `plugins/` — installed plugins

Run from anywhere:

```bash
claude
```

---

## Quick Start Reference

```bash
claude                                       # Start interactive session
claude "Your prompt"                         # Interactive with initial prompt
claude -p "Your prompt"                      # Non-interactive print mode
claude -c                                    # Continue most recent session in this directory
claude -r <session-id>                       # Resume a specific session
claude --fork-session -c                     # Continue but fork into a new session
claude --model sonnet "Your prompt"          # Use a specific model alias
claude --effort high -p "Deep reasoning task"
claude --permission-mode auto -p "Routine task"
claude --dangerously-skip-permissions -p "..."
claude --bare -p "Minimal, no customizations"
```

---

## Command Line Flags

Run `claude --help` for the authoritative list.

| Flag / Option | Alias | Description |
| :--- | :--- | :--- |
| `--version` | `-v` | Output version number. |
| `--help` | `-h` | Display help. |
| `--print` | `-p` | Print response and exit (non-interactive). |
| `--continue` | `-c` | Continue the most recent conversation in the current directory. |
| `--resume [value]` | `-r` | Resume a conversation by session ID or open picker. |
| `--fork-session` | | When resuming, create a new session ID. |
| `--session-id <uuid>` | | Use a specific UUID for the session. |
| `--model <model>` | | Model alias (`sonnet`, `opus`, `fable`) or full name (`claude-fable-5`). |
| `--fallback-model <models>` | | Comma-separated fallback models (only with `--print`). |
| `--effort <level>` | | Effort level: `low`, `medium`, `high`, `xhigh`, `max`. |
| `--permission-mode <mode>` | | Permission mode: `acceptEdits`, `auto`, `bypassPermissions`, `default`, `dontAsk`, `plan`. |
| `--dangerously-skip-permissions` | | Bypass all permission checks. |
| `--allow-dangerously-skip-permissions` | | Make bypass mode available without defaulting to it. |
| `--allowed-tools <tools>` | | Comma/space-separated tool allowlist. |
| `--disallowed-tools <tools>` | | Comma/space-separated tool denylist. |
| `--add-dir <dirs>` | | Additional directories to allow tool access to. |
| `--agent <agent>` | | Agent for the current session. |
| `--agents <json>` | | JSON object defining custom agents. |
| `--mcp-config <configs>` | | Load MCP servers from JSON files/strings. |
| `--strict-mcp-config` | | Only use MCP servers from `--mcp-config`. |
| `--file <specs>` | | File resources to download at startup. |
| `--output-format <format>` | | Output format with `--print`: `text` (default), `json`, `stream-json`. |
| `--input-format <format>` | | Input format with `--print`: `text` (default), `stream-json`. |
| `--json-schema <schema>` | | JSON Schema for structured output validation. |
| `--system-prompt <prompt>` | | System prompt to use for the session. |
| `--append-system-prompt <prompt>` | | Append to the default system prompt. |
| `--settings <file-or-json>` | | Load additional settings from file or JSON. |
| `--setting-sources <sources>` | | Setting sources to load: `user`, `project`, `local`. |
| `--name <name>` | `-n` | Display name for the session. |
| `--bare` | | Minimal mode: skip hooks, LSP, plugins, skills auto-discovery, etc. |
| `--safe-mode` | | Disable all customizations for troubleshooting. |
| `--no-session-persistence` | | Don't save session to disk (only with `--print`). |
| `--disable-slash-commands` | | Disable all skills. |
| `--worktree [name]` | `-w` | Create a new git worktree for this session. |
| `--tmux` | | Create a tmux session for the worktree. |
| `--verbose` | | Override verbose mode setting. |
| `--debug [filter]` | `-d` | Enable debug mode with optional filtering. |
| `--debug-file <path>` | | Write debug logs to a file. |
| `--chrome` / `--no-chrome` | | Enable/disable Claude in Chrome integration. |
| `--remote-control [name]` | | Start with Remote Control enabled. |
| `--brief` | | Enable `SendUserMessage` tool for agent-to-user communication. |
| `--max-budget-usd <amount>` | | Max API spend (only with `--print`). |
| `--plugin-dir <path>` | | Load a plugin from a directory or zip. |
| `--plugin-url <url>` | | Fetch a plugin zip from a URL. |
| `--prompt-suggestions [value]` | | Enable/disable prompt suggestions. |
| `--from-pr [value]` | | Resume a session linked to a PR. |
| `--betas <betas>` | | Beta headers for API requests (API key users only). |
| `--exclude-dynamic-system-prompt-sections` | | Move machine-specific sections to the first user message. |
| `--replay-user-messages` | | Re-emit user messages for stream-json mode. |

### Subcommands

```bash
claude agents [options]        # Manage background agents
claude auth [login|logout|status]  # Manage authentication
claude auto-mode               # Inspect auto mode classifier config
claude doctor                  # Check auto-updater health
claude install [target]        # Install native build (stable, latest, version)
claude mcp                     # Configure and manage MCP servers
claude plugin|plugins          # Manage plugins
claude project purge [path]    # Delete Claude Code state for a project
claude setup-token             # Set up a long-lived auth token
claude ultrareview [target]    # Cloud-hosted multi-agent code review
```

---

## Prompt Passing

Claude accepts prompts in three ways:

1. **Positional argument**:
   ```bash
   claude "Refactor the auth module"
   ```

2. **`-p` / `--print` flag** (non-interactive):
   ```bash
   claude -p "Refactor the auth module"
   ```

3. **Interactive TUI**: launch `claude` with no prompt.

For scripting, combine `-p` with `--output-format json` or `stream-json`.

---

## Model Selection & Effort Levels

### Model Aliases

| Alias | Typical Model | Notes |
| :--- | :--- | :--- |
| `sonnet` | Latest Claude Sonnet | Fast, strong coding |
| `opus` | Latest Claude Opus | Deep reasoning |
| `fable` | Claude Fable 5 | Most capable; deep reasoning / agentic. Availability varies — check `claude --help` or official Anthropic docs before relying on it. |

You can also pass a full model name such as `claude-fable-5`. Other full
IDs: `claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`.

### Passing a Model

```bash
claude --model sonnet "Implement the feature"
claude --model opus --effort high "Analyze this architecture"
```

### Effort / Reasoning Levels

Use `--effort <level>` to control reasoning depth:

| Level | Use Case |
| :--- | :--- |
| `low` | Quick, cheap responses |
| `medium` | Balanced |
| `high` | Deeper analysis |
| `xhigh` | Extensive reasoning |
| `max` | Maximum effort |

Current user default in `~/.claude/settings.json`:

```json
{
  "includeCoAuthoredBy": false,
  "model": "opus",
  "effortLevel": "low",
  "theme": "dark"
}
```

---

## Permission Modes

| Mode | Behavior |
| :--- | :--- |
| `default` | Standard interactive approval flow. |
| `auto` | Auto-approve routine tool requests. |
| `acceptEdits` | Automatically accept file edits, ask for others. |
| `dontAsk` | Don't ask for most permissions. |
| `plan` | Plan mode — ask before implementation. |
| `bypassPermissions` | Bypass all permission checks (dangerous). |

Use `--permission-mode auto` for headless automation and `--dangerously-skip-permissions` only in trusted sandboxes.

---

## Agents & Sub-agents

Claude Code supports background agents via the `claude agents` command and
inline agents via `--agent` / `--agents`.

### Run with a Specific Agent

```bash
claude --agent <agent-name> "Task for the agent"
```

### Define Custom Agents Inline

```bash
claude --agents '{"reviewer": {"description": "Reviews code", "prompt": "You are a code reviewer"}}' "Review this file"
```

### Manage Background Agents

```bash
claude agents --json          # List active background sessions
claude agents --cwd <path>    # Filter by working directory
```

Background agents can be dispatched with their own `--model`, `--effort`,
`--permission-mode`, `--mcp-config`, and `--settings`.

---

## Sessions

| Action | Command |
| :--- | :--- |
| Continue most recent | `claude -c` |
| Resume specific session | `claude -r <session-id>` |
| Resume with new ID | `claude --fork-session -c` |
| Set session name | `claude -n "My session"` |
| Use specific session ID | `claude --session-id <uuid>` |
| No persistence | `claude -p --no-session-persistence "..."` |
| Linked to PR | `claude --from-pr <number/url>` |

Sessions are stored in `~/.claude/sessions/`.

---

## MCP Servers

Claude supports MCP (Model Context Protocol) servers.

```bash
claude mcp list                                    # List configured servers
claude mcp add <name> <commandOrUrl> [args...]     # Add a server
claude mcp add-from-claude-desktop                 # Import from Claude Desktop
claude mcp add-json <name> <json>                  # Add from JSON
claude mcp get <name>                              # Show server details
claude mcp remove <name>                           # Remove a server
claude mcp reset-project-choices                   # Reset project-scoped choices
claude mcp serve                                   # Start Claude Code MCP server
```

Load servers at runtime:

```bash
claude --mcp-config /path/to/mcp.json "Use my server"
```

---

## Skills System

Claude Code discovers skills from the user skills directory
`~/.claude/skills/` and project-level skill directories. The
directory is symlink-friendly.

Skills are directories containing a `SKILL.md` file with YAML frontmatter
(`name`, `description`) and Markdown guidance.

Disable skills entirely:

```bash
claude --disable-slash-commands -p "Run without skills"
```

Use `--bare` to skip CLAUDE.md auto-discovery and other customizations while
still resolving skills explicitly via `/skill-name`.

---

## Configuration Files

### `~/.claude/settings.json`

User-level settings example:

```json
{
  "includeCoAuthoredBy": false,
  "model": "opus",
  "effortLevel": "low",
  "theme": "dark"
}
```

### Project-Level Configuration

Claude Code also reads project-local settings (commonly in `CLAUDE.md` or
project config). Use `--setting-sources user,project,local` to control which
sources load.

---

## Special Modes

| Mode | Flag | Purpose |
| :--- | :--- | :--- |
| **Bare** | `--bare` | Skip hooks, LSP, plugins, skills auto-discovery, attribution, memory, etc. Auth is strictly `ANTHROPIC_API_KEY` or `--settings`. |
| **Safe mode** | `--safe-mode` | Disable all customizations for troubleshooting. |
| **Plan mode** | `--permission-mode plan` | Ask before implementing. |
| **Non-interactive** | `-p` | Print response and exit; skips workspace trust dialog. |

---

## Troubleshooting

| Issue | Command / Fix |
| :--- | :--- |
| Check auto-updater health | `claude doctor` |
| Show auth status | `claude auth status` |
| Login / logout | `claude auth login` / `claude auth logout` |
| List MCP servers | `claude mcp list` |
| List active agents | `claude agents --json` |
| Purge project state | `claude project purge [path]` |
| Install / upgrade | `claude install [stable\|latest\|<version>]` |
| Multi-agent code review | `claude ultrareview [target]` |

---

## Useful Documentation

- Official docs: https://docs.anthropic.com/en/docs/claude-code/
- Run `claude --help` and `claude <command> --help` for the latest CLI reference.
