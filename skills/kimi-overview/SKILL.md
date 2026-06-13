---
name: kimi-overview
description: >
  Comprehensive overview of the Kimi Code CLI (`kimi`). Details on how to run,
  the binary path, supported flags, permission modes, model selection, thinking
  levels, prompt passing, session management, skills loading, sub-agents, and
  general usage. Use this skill whenever another agent needs to invoke or
  understand Kimi Code CLI behavior.
license: MIT
compatibility: "Kimi Code CLI, Cursor CLI, Claude Code, Codex, OpenCode, Gemini, Antigravity."
metadata:
  author: Kimi-Code-CLI
  version: "1.0"
---

# Kimi Code CLI — Agent Overview

Kimi Code CLI (`kimi`) is a terminal-based autonomous coding agent. It can read
and write files, run shell commands, launch sub-agents, search the web, and
execute multi-step software engineering tasks inside a local workspace.

This skill documents how to run `kimi`, what flags it supports, how to pass
prompts and models, how thinking/reasoning levels work, and how sub-agents are
run and coordinated.

---

## CLI Path & Executable

- **Primary Binary Path**: `~/.kimi-code/bin/kimi`
- **Version**: `0.14.2`
- **Configuration Directory**: `~/.kimi-code/`
  - `config.toml` — runtime/agent settings (model, provider, thinking)
  - `tui.toml` — client UI preferences (theme, editor, notifications)
  - `sessions/` — persisted conversation sessions
  - `skills/` — discovered and user skills

The binary is normally on the user's `PATH`. To run from anywhere:

```bash
kimi
```

---

## Quick Start Reference

```bash
kimi                                          # Start interactive mode
kimi "Your prompt"                            # Pass a prompt as positional argument
kimi -p "Your prompt"                         # Run one prompt non-interactively and print
kimi -p "Your prompt" --output-format text    # Explicit text output (default)
kimi -p "Your prompt" --output-format stream-json
kimi -y -p "Your prompt"                      # Auto-approve all actions (yolo)
kimi --auto -p "Your prompt"                  # Start in auto permission mode
kimi -m kimi-code/kimi-for-coding -p "..."    # Use a specific model alias
kimi -C                                       # Continue the previous session for this directory
kimi -S <session-id>                          # Resume a specific session
kimi --plan                                   # Start in plan mode
kimi --skills-dir /path/to/skills -p "..."    # Load skills from a custom directory
```

---

## Command Line Flags

Run `kimi --help` for the authoritative list.

| Flag / Option | Alias | Description |
| :--- | :--- | :--- |
| `--version` | `-V` | Print the CLI version and exit. |
| `--session [id]` | `-S` | Resume a session. With ID: resume that session. Without ID: interactively pick. |
| `--continue` | `-C` | Continue the previous session for the current working directory. |
| `--yolo` | `-y` | Automatically approve all actions (dangerous; skips permission prompts). |
| `--auto` | | Start in **auto permission mode** (auto-approves tool requests without pausing). |
| `--model <model>` | `-m` | LLM model alias to use for this invocation. Defaults to `default_model` in `config.toml`. |
| `--prompt <prompt>` | `-p` | Run one prompt non-interactively and print the response. |
| `--output-format <format>` | | Output format for prompt mode. Choices: `text` (default), `stream-json`. |
| `--skills-dir <dir>` | | Load skills from this directory instead of auto-discovered ones. Repeatable. |
| `--plan` | | Start in plan mode (ask for approval before implementation). |
| `--help` | `-h` | Show help and exit. |

### Subcommands

```bash
kimi export [sessionId]    # Export a session as a ZIP archive
kimi provider              # Manage LLM providers non-interactively
kimi acp                   # Run kimi-code as an ACP (Agent Client Protocol) server over stdio
kimi login                 # Authenticate with Kimi Code CLI
kimi doctor                # Validate configuration files
kimi migrate               # Migrate data from legacy kimi-cli
kimi upgrade               # Upgrade Kimi Code to the latest version
```

---

## Permission Modes

Kimi supports multiple permission modes that control whether tool calls require
explicit user approval.

| Mode | How to Enter | Behavior |
| :--- | :--- | :--- |
| **Manual** | Default | Each tool call that requires approval pauses and asks the user. |
| **Auto** | `--auto` | Tool approvals are handled automatically; the conversation continues without pausing. |
| **Yolo** | `-y` / `--yolo` | Automatically approve **all** actions, including destructive ones. Use with caution. |

When invoking Kimi non-interactively, prefer `--auto` for routine tasks and `-y`
only when you explicitly want to bypass every safeguard.

---

## Model Selection & Thinking (Reasoning) Levels

Models are configured in `~/.kimi-code/config.toml`.

### Default Configuration

```toml
default_thinking = true
default_model = "kimi-code/kimi-for-coding"
```

### Default Model Details

| Model Alias | Provider | Display Name | Capabilities |
| :--- | :--- | :--- | :--- |
| `kimi-code/kimi-for-coding` | `managed:kimi-code` | K2.7 Code | `thinking`, `always_thinking`, `image_in`, `video_in`, `tool_use` |

### Passing a Model

Use the exact alias as defined in `config.toml`:

```bash
kimi -m kimi-code/kimi-for-coding -p "Refactor the auth module"
```

### Thinking / Reasoning Levels

The default model supports thinking. The behavior is controlled by the model
alias and the `default_thinking` setting:

- `default_thinking = true` in `config.toml` enables thinking by default.
- Models with `always_thinking` capability always run in thinking mode.
- To disable thinking for a specific invocation, use a model alias configured
  without the `thinking` capability, or override the configuration file.

For current provider/model availability, run:

```bash
kimi provider list
```

---

## Prompt Passing

Kimi accepts prompts in three ways:

1. **Positional argument** (recommended for quick one-shots):
   ```bash
   kimi "Explain this codebase"
   ```

2. **`-p` / `--prompt` flag**:
   ```bash
   kimi -p "Explain this codebase"
   ```

3. **Interactive mode**: launch `kimi` with no prompt and type your request.

When using `-p`, Kimi runs non-interactively and prints the final response. Use
`--output-format stream-json` if you need streaming JSON output instead of plain
text.

---

## Sessions

Kimi persists conversations in sessions stored under `~/.kimi-code/sessions/`.

| Action | Command |
| :--- | :--- |
| Continue previous session for current directory | `kimi -C` |
| Resume a specific session | `kimi -S <session-id>` |
| Pick a session interactively | `kimi -S` |
| Export a session | `kimi export <session-id>` |

---

## Skills System

Kimi can load reusable skills from multiple scopes. More specific scopes take
precedence:

**Precedence (highest → lowest)**: Project → User → Extra → Built-in

- **Project skills**: located in the current project (e.g. `.kimi-code/skills/`).
- **User skills**: located in `~/.kimi-code/skills/`.
- **Extra skills**: additional directories passed via `--skills-dir`.
- **Built-in skills**: bundled with the CLI (e.g. `update-config`).

### Loading Custom Skills

```bash
kimi --skills-dir /path/to/skills -p "Use the custom skill"
```

Each skill is a directory containing a `SKILL.md` file with YAML frontmatter and
Markdown content. The frontmatter must include at least `name` and `description`.

---

## Sub-agents & Task Delegation

Kimi can spawn focused sub-agents to parallelize work or isolate research. This
is done with the `Agent` tool.

### Sub-agent Types

| Type | Purpose | Write Access |
| :--- | :--- | :--- |
| `coder` | General software engineering: read files, edit code, run commands, tests. | Yes |
| `explore` | Fast, read-only codebase exploration and search. | No |
| `plan` | Read-only implementation planning and architecture design. | No |

### Agent Tool Parameters

- **`description`** — short task description (3–5 words) for UI display.
- **`prompt`** — full task prompt handed to the sub-agent. The sub-agent starts
  with zero context, so include all necessary background.
- **`subagent_type`** — `coder`, `explore`, or `plan` (defaults to `coder`).
- **`resume`** — optional agent ID to resume an existing sub-agent instead of
  creating a new one.
- **`run_in_background`** — launch the sub-agent detached; the result arrives
  later as a notification.

### Sub-agent Timeout & Lifecycle

- Each sub-agent has a fixed 30-minute timeout.
- If a sub-agent times out, resume the same agent ID instead of starting over.
- Sub-agents return a compact summary to the parent agent.

### Parallel Sub-agents with AgentSwarm

Use `AgentSwarm` to launch many sub-agents from a single prompt template. The
placeholder `{{item}}` is replaced with each value in the `items` list.

Example template:

```text
Review {{item}} for likely regressions.
```

with `items: ["src/a.ts", "src/b.ts"]` launches two sub-agents.

### Best Practices

- Always include exact file paths, commands, and context in the sub-agent prompt.
- Use `explore` agents for read-only research to conserve parent context.
- Use `plan` agents before making multi-file changes.
- Do not re-run searches the sub-agent already performed; include results in the
  prompt.
- Prefer resuming an existing sub-agent over spawning a new one when continuing
  earlier work.

---

## Configuration Files

### `~/.kimi-code/config.toml`

Runtime and agent settings:

```toml
default_thinking = true
default_model = "kimi-code/kimi-for-coding"

[services.moonshot_search]
base_url = "https://api.kimi.com/coding/v1/search"
api_key = ""

[services.moonshot_fetch]
base_url = "https://api.kimi.com/coding/v1/fetch"
api_key = ""

[providers."managed:kimi-code"]
type = "kimi"
api_key = ""
base_url = "https://api.kimi.com/coding/v1"

[models."kimi-code/kimi-for-coding"]
provider = "managed:kimi-code"
model = "kimi-for-coding"
max_context_size = 262144
capabilities = ["thinking", "always_thinking", "image_in", "video_in", "tool_use"]
display_name = "K2.7 Code"
```

### `~/.kimi-code/tui.toml`

Client UI preferences:

```toml
theme = "auto"  # "auto" | "dark" | "light"

[editor]
command = ""  # Empty uses $VISUAL / $EDITOR

[notifications]
enabled = true
notification_condition = "unfocused"  # "unfocused" | "always"

[upgrade]
auto_install = true
```

---

## Troubleshooting

| Issue | Command / Fix |
| :--- | :--- |
| Verify configuration | `kimi doctor` |
| Login / re-authenticate | `kimi login` |
| Update to latest version | `kimi upgrade` |
| Migrate from legacy CLI | `kimi migrate` |
| See available providers/models | `kimi provider list` |

---

## Useful Documentation

- Official docs: https://moonshotai.github.io/kimi-code/
- Run `kimi --help` and `kimi <command> --help` for the latest CLI reference.
