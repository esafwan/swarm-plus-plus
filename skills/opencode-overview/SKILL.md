---
name: opencode-overview
description: >
  Comprehensive overview of the OpenCode coding agent CLI (`opencode`). Covers
  binary path, config files, flags, prompt passing, model selection (including
  Ollama local models), thinking/reasoning variants, agents and sub-agents,
  permissions, sessions, MCP servers, skills, and general CLI usage. Use this
  skill whenever another agent needs to invoke, orchestrate, or understand
  OpenCode behavior.
license: MIT
compatibility: "OpenCode CLI, Cursor CLI, Claude Code, Kimi Code, Codex, Gemini, Antigravity."
metadata:
  author: OpenCode-CLI
  version: "1.0"
---

# OpenCode — Coding Agent CLI Overview

OpenCode (`opencode`) is a terminal-based autonomous coding agent. It supports
multiple AI providers (Ollama, OpenAI, Google Gemini, OpenRouter, and more), runs
local and remote models, executes tools (file read/write, shell, web search,
MCP), and delegates work to configurable sub-agents.

---

## CLI Path & Executable

- **Primary Binary Path**: `~/.opencode/bin/opencode`
- **Version**: `1.16.2`
- **Global Config**: `~/.config/opencode/opencode.jsonc`
- **Global Data**: `
- **Cache**: `~/.cache/opencode/`
- **State**: `~/.local/state/opencode/`
- **User Skills**: `~/.opencode/skills/` (symlink-friendly)

Run from anywhere:

```bash
opencode
```

---

## Quick Start Reference

```bash
opencode                                     # Start interactive TUI
opencode "Your prompt"                       # Run with an initial prompt
opencode run "Your prompt"                   # Explicit run mode
opencode run -m ollama/qwen3-coder-next "Fix login bug"
opencode run --dangerously-skip-permissions -p "Refactor auth"
opencode -c                                  # Continue last session
opencode -s <session-id>                     # Resume a specific session
opencode --fork -c                           # Continue last session but fork it
opencode models                              # List all available models
opencode providers list                      # List configured providers
opencode mcp list                            # List MCP servers
```

---

## Command Line Flags

Run `opencode --help` for the authoritative list.

| Flag / Option | Alias | Description |
| :--- | :--- | :--- |
| `--version` | `-v` | Show version number. |
| `--help` | `-h` | Show help. |
| `--model <model>` | `-m` | Model to use in `provider/model` format. |
| `--continue` | `-c` | Continue the last session. |
| `--session <id>` | `-s` | Resume a specific session. |
| `--fork` | | Fork the session when continuing (use with `-c` or `-s`). |
| `--prompt <prompt>` | | Prompt to use (for non-interactive / TUI entry). |
| `--agent <agent>` | | Agent to use (defaults to `default_agent` in config). |
| `--variant <variant>` | | Model variant for reasoning effort (`high`, `max`, `minimal`, etc.). |
| `--thinking` | | Show thinking blocks. |
| `--dangerously-skip-permissions` | | Auto-approve permissions that are not explicitly denied. |
| `--format <format>` | | Output format: `default` or `json`. |
| `--file <path>` | `-f` | Attach file(s) to the message (repeatable). |
| `--title <title>` | | Title for the session. |
| `--pure` | | Run without external plugins. |
| `--print-logs` | | Print logs to stderr. |
| `--log-level <level>` | | Log level: `DEBUG`, `INFO`, `WARN`, `ERROR`. |
| `--port`, `--hostname`, `--cors`, `--mdns`, `--mdns-domain` | | Server/network options for `serve`, `web`, `acp`, `attach`. |

### Subcommands

```bash
opencode [project]            # Start TUI (default)
opencode run [message..]      # Run with a message
opencode acp                  # Start Agent Client Protocol server
opencode mcp                  # Manage MCP servers
opencode attach <url>         # Attach to a running opencode server
opencode providers            # Manage AI providers and credentials
opencode agent create/list    # Manage agents
opencode models [provider]    # List all available models
opencode session list/delete  # Manage sessions
opencode export [sessionID]   # Export session data as JSON
opencode import <file>        # Import session data from JSON
opencode stats                # Show token usage and cost statistics
opencode github               # Manage GitHub agent
opencode pr <number>          # Fetch/checkout a GitHub PR branch, then run
opencode plugin <module>      # Install plugin and update config
opencode db                   # Database tools
opencode debug                # Debugging and troubleshooting tools
opencode upgrade [target]     # Upgrade opencode
opencode uninstall            # Uninstall opencode
opencode serve                # Start headless opencode server
opencode web                  # Start server and open web interface
opencode completion           # Generate shell completion script
```

---

## Prompt Passing

OpenCode accepts prompts in several ways:

1. **Positional argument** (quick one-shot):
   ```bash
   opencode "Explain this codebase"
   ```

2. **Explicit run mode**:
   ```bash
   opencode run "Explain this codebase"
   opencode run --file README.md "Summarize this project"
   ```

3. **`--prompt` flag**:
   ```bash
   opencode --prompt "Explain this codebase"
   ```

4. **Interactive TUI**: launch `opencode` with no prompt.

For non-interactive output use `--format json` to get raw JSON events instead of
formatted text.

---

## Model Selection & Providers

Models are referenced as `provider/model`. Run `opencode models` to see every
available model and `opencode models <provider>` to filter by provider.

### Current Default Configuration

```jsonc
{
  "model": "ollama/qwen3-coder-next:latest",
  "small_model": "ollama/gemma4:latest"
}
```

### Configured Providers

| Provider | Source | Notes |
| :--- | :--- | :--- |
| `ollama` | Local `http://localhost:11434/v1` | Local models; requires Ollama running. |
| `openai` | `api.openai.com` | API key from `OPENAI_API_KEY`. |
| `google` | Gemini API | API key from `GOOGLE_API_KEY`. |
| `openrouter` | `openrouter.ai/api/v1` | API key from `OPENROUTER_API_KEY`; provides access to many models including `moonshotai/kimi-k2`. |

### Example Model Identifiers

| Identifier | Provider | Use Case |
| :--- | :--- | :--- |
| `ollama/qwen3-coder-next:latest` | Ollama | Default coding model |
| `ollama/gemma4:latest` | Ollama | Default small/fast model |
| `ollama/deepseek-r1:32b` | Ollama | Local reasoning |
| `ollama/gpt-oss:20b` | Ollama | Lightweight local worker |
| `google/gemini-2.5-pro` | Google | Strong reasoning, large context |
| `google/gemini-2.5-flash` | Google | Faster, cheaper |
| `openai/gpt-5-codex` | OpenAI | Coding agent model |
| `openai/o3-pro` | OpenAI | Deep reasoning |
| `openrouter/moonshotai/kimi-k2` | OpenRouter | Kimi K2 via OpenRouter |

### Passing a Model

```bash
opencode -m ollama/deepseek-r1:32b "Debug this race condition"
opencode run -m openai/gpt-5-codex --variant high "Design this module"
```

### Reasoning / Thinking Levels

- Use `--variant <level>` to control provider-specific reasoning effort. Common
  values include `minimal`, `low`, `medium`, `high`, `max`.
- Use `--thinking` to surface thinking/reasoning blocks in the output.
- Reasoning models (e.g. `ollama/deepseek-r1`, `openai/o3`) expose internal
  reasoning automatically when supported.

### Ollama-Specific Notes

- Ollama models must be pulled locally before use:
  ```bash
  ollama pull qwen3-coder-next:latest
  ```
- The provider base URL is `http://localhost:11434/v1` by default.
- If a model is missing, `opencode models` may still list it but calls will fail
  until `ollama pull` succeeds.

---

## Agents & Sub-agents

OpenCode agents are defined in `~/.config/opencode/opencode.jsonc`
under the `"agent"` key. Agents control which model is used, how many steps the
agent may take, and what tools/permissions it has.

### Default Agents

| Agent | Mode | Default Model | Purpose |
| :--- | :--- | :--- | :--- |
| `build` | primary | Config default | Default agent; executes tools based on configured permissions. |
| `oc-router` | primary | `ollama/deepseek-r1:32b` | Parent routing agent. Plans, classifies tasks, delegates to sub-agents, synthesizes results. |
| `oc-explore-local` | subagent | `ollama/gemma4:31b` | Read-only local codebase explorer. |
| `oc-kimi-explore` | subagent | `ollama/gemma4:31b` | Large-context exploration and synthesis (read-only). |
| `oc-qwen-coder` | subagent | `ollama/qwen3-coder-next:latest` | Primary coding implementation agent (edit + safe test commands). |
| `oc-deepseek-reasoner` | subagent | `ollama/deepseek-r1:32b` | Reasoning-heavy debugging and analysis. |
| `oc-cheap-worker` | subagent | `ollama/gpt-oss:20b` | Cheap local worker for summaries and small tasks. |
| `oc-reviewer` | subagent | `ollama/deepseek-r1:32b` | Read-only review agent for git diffs, bugs, security. |

### Running a Specific Agent

```bash
opencode --agent oc-router "Plan the refactor"
opencode run --agent oc-qwen-coder "Implement the plan"
```

### Sub-agent Delegation

Sub-agents are spawned by the parent agent using the **`task`** tool with the
sub-agent name. The parent must have permission to call that agent under its own
`task` permission rules.

Example from `oc-router` config:

```jsonc
"task": {
  "*": "deny",
  "oc-explore-local": "allow",
  "oc-kimi-explore": "allow",
  "oc-qwen-coder": "allow",
  "oc-deepseek-reasoner": "allow",
  "oc-cheap-worker": "allow",
  "oc-reviewer": "allow"
}
```

This means `oc-router` can delegate to those named agents and no others.

### Creating Custom Agents

```bash
opencode agent create
```

Custom agents are also added directly in `opencode.jsonc` under `"agent"`.

---

## Permission System

Permissions are configured per agent in `opencode.jsonc`. Each permission can be
`allow`, `deny`, or `ask`. Patterns support wildcards.

### Common Permission Keys

| Permission | Controls |
| :--- | :--- |
| `read` | File reads (supports glob patterns like `*.env`). |
| `edit` | File edits/writes. |
| `bash` | Shell command execution. |
| `task` | Delegation to sub-agents. |
| `glob` | File globbing. |
| `grep` | Text/code search. |
| `lsp` | Language server tools. |
| `webfetch` / `websearch` | Web fetch/search. |
| `external_directory` | Access outside the project directory. |
| `question` | Asking the user questions. |
| `doom_loop` | Repeated retry loops. |
| `skill` | Loading skills. |
| `todowrite` | Writing todo lists. |

### Example Permission Block

```jsonc
"permission": {
  "read": { "*": "allow", "*.env": "deny" },
  "edit": "deny",
  "bash": { "*": "deny", "git status*": "allow" },
  "task": { "*": "deny", "oc-explore-local": "allow" },
  "external_directory": "deny"
}
```

### Bypassing Permissions

```bash
opencode run --dangerously-skip-permissions "Do everything"
```

This auto-approves any permission that is not explicitly `deny`. Use with
caution.

---

## Sessions

Sessions are persisted automatically.

| Action | Command |
| :--- | :--- |
| Continue last session | `opencode -c` |
| Continue specific session | `opencode -s <session-id>` |
| Fork session on continue | `opencode --fork -c` |
| List sessions | `opencode session list` |
| Delete a session | `opencode session delete <session-id>` |
| Export session | `opencode export [sessionID]` |
| Import session | `opencode import <file>` |

---

## MCP Servers

OpenCode supports MCP (Model Context Protocol) servers for extended tools.

```bash
opencode mcp list     # List MCP servers
opencode mcp add      # Add an MCP server
opencode mcp auth     # Authenticate OAuth-enabled MCP server
opencode mcp logout   # Remove OAuth credentials
opencode mcp debug    # Debug OAuth connection
```

---

## Skills System

OpenCode loads skills from the user skills directory
`~/.opencode/skills/` and from project-level skill directories. The
directory is symlink-friendly, so a global skill symlink works like any other
skill.

Each skill is a directory containing a `SKILL.md` file with YAML frontmatter
(`name`, `description`) and Markdown guidance.

---

## Configuration File

### `~/.config/opencode/opencode.jsonc`

Key sections:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ollama/qwen3-coder-next:latest",
  "small_model": "ollama/gemma4:latest",
  "default_agent": "oc-router",
  "instructions": [
    "
    "
  ],
  "share": "disabled",
  "provider": { /* provider definitions */ },
  "enabled_providers": ["ollama", "openai", "google", "openrouter"],
  "permission": { /* global/default permission rules */ },
  "agent": { /* agent definitions */ }
}
```

### Config Commands

```bash
opencode debug config   # Show resolved configuration
opencode debug paths    # Show global paths
opencode debug skill    # List all available skills
opencode debug agent <name>   # Show agent configuration
```

---

## Troubleshooting

| Issue | Command / Fix |
| :--- | :--- |
| Verify config | `opencode debug config` |
| Show paths | `opencode debug paths` |
| List skills | `opencode debug skill` |
| List models | `opencode models` |
| Login to provider | `opencode providers login [url]` |
| Logout provider | `opencode providers logout` |
| Upgrade OpenCode | `opencode upgrade` |
| Export session | `opencode export [sessionID]` |

---

## Useful Documentation

- Official docs: https://opencode.ai/
- Config schema: https://opencode.ai/config.json
- Run `opencode --help` and `opencode <command> --help` for the latest CLI reference.
