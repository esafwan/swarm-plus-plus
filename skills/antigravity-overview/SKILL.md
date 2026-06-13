---
name: antigravity-overview
description: >
  Comprehensive overview of the Antigravity coding agent CLI (`agy`). Details on how to run, path, flags, prompt, model, thinking levels, sub-agents, and general usage.
license: MIT
compatibility: "Agy CLI, Claude Code, Kimi Code, Codex, OpenCode."
metadata:
  author: Antigravity-Team
  version: "1.0"
---

# Antigravity (`agy`) — Coding Agent CLI Overview

Antigravity is a terminal-based autonomous coding agent powered by the Google Antigravity SDK. It provides LLM-driven file manipulation, shell command execution, and sub-agent coordination to pair-program on local workspaces.

## CLI Path & Executable

- **Primary Binary Path**: ``agy`` (on PATH)
- **Helper Wrapper**: `~/.gemini/antigravity-cli/bin/agentapi` (executes ``agy` (on PATH) agentapi "$@"`)

To run the agent from anywhere, invoke `agy`.

---

## Quick Start Reference

```bash
agy                              # Start interactive mode
agy -i                           # Interactive mode with initial prompt (e.g. `agy -i "Refactor this file"`)
agy -p "Your prompt"             # Print mode (one-shot query execution)
agy -c                           # Continue the most recent conversation session
agy --conversation <session-id> # Resume a specific conversation session by ID
agy --model "Gemini 3.5 Flash (Medium)" # Start a session with a specific model configuration
agy --dangerously-skip-permissions     # Auto-approve all tool permission requests (no prompts)
agy --sandbox                    # Run in sandbox mode (terminal restrictions enabled)
```

---

## Command Line Flags

| Flag / Option | Alias | Description |
| :--- | :--- | :--- |
| `--prompt` | `-p`, `--print` | Run a single prompt non-interactively and print the response. |
| `--prompt-interactive` | `-i` | Run an initial prompt interactively and continue the session. |
| `--continue` | `-c` | Continue the most recent conversation session. |
| `--conversation <id>` | | Resume a previous conversation by its unique ID. |
| `--model <model>` | | Model for the current CLI session (see Model selection below). |
| `--add-dir <path>` | | Add a directory to the workspace (repeatable). |
| `--dangerously-skip-permissions` | | Auto-approve all tool permissions without interactive prompting. |
| `--sandbox` | | Run in a sandboxed environment with strict terminal command restrictions. |
| `--log-file <path>` | | Override the default log file path. |
| `--print-timeout <duration>` | | Timeout for print mode wait (default: `5m0s`). |

### Subcommands

```bash
agy changelog       # Show changelog and release notes
agy help            # Show help for CLI subcommands
agy install         # Configure environment paths and shell settings
agy models          # List available models
agy plugin          # Manage plugins (install, uninstall, list, enable, disable)
agy update          # Update CLI
```

---

## Model Selection & Thinking (Reasoning) Levels

Run `agy models` to see the currently available models in your environment. Model selection controls both the LLM provider and the thinking/reasoning effort level.

Pass the chosen model string exactly as listed in the models output to the `--model` flag.

### Available Models & Reasoning Configurations

| Model Identifier (Exact String) | Provider | Reasoning / Thinking Level |
| :--- | :--- | :--- |
| `"Gemini 3.5 Flash (Medium)"` | Google | Medium effort (Standard default) |
| `"Gemini 3.5 Flash (High)"` | Google | High effort |
| `"Gemini 3.5 Flash (Low)"` | Google | Low effort / High speed |
| `"Gemini 3.1 Pro (Low)"` | Google | Low effort / Fast reasoning |
| `"Gemini 3.1 Pro (High)"` | Google | High effort / Deep reasoning |
| `"Claude Sonnet 4.6 (Thinking)"` | Anthropic | Deep reasoning (thinking mode enabled) |
| `"Claude Opus 4.6 (Thinking)"` | Anthropic | Deep reasoning (thinking mode enabled) |
| `"GPT-OSS 120B (Medium)"` | Open Source | Medium effort |

### Examples

```bash
# Run one-shot query using high-reasoning Gemini 3.5 Flash
agy --model "Gemini 3.5 Flash (High)" -p "Analyze the authentication logic for race conditions"

# Start interactive session with Claude Sonnet 4.6 (Thinking enabled)
agy --model "Claude Sonnet 4.6 (Thinking)"
```

---

## Sub-agents & Task Delegation

Within an active session, Antigravity can spawn and coordinate sub-agents to parallelize tasks or perform isolated research.

### Sub-agent Invocation via SDK/Tools
The agent uses the `invoke_subagent` tool with the following configurations:
- **`TypeName`**:
  - `research`: A read-only sub-agent designed to browse the codebase, search the web, and read documents without write capabilities. Great for isolating research tasks and conserving token context.
  - `self`: A sub-agent inheriting the parent agent's full tools, system prompt, and model configuration.
- **`Role`**: A short description of the sub-agent's role (e.g. `Codebase Researcher`, `API Auditor`).
- **`Prompt`**: The specific task the sub-agent should execute.
- **`Workspace`**:
  - `inherit` (default): Uses the same workspace directory.
  - `branch`: Creates an isolated directory workspace branched/cloned from the parent.
  - `share`: Shares the underlying repository directory (similar to a Git worktree), allowing independent branch management.

### Sub-agent Communication
- Spawned sub-agents run in the background.
- The parent agent communicates with sub-agents using `send_message` targeting their `Conversation ID`.
- The system automatically notifies the parent agent when the sub-agent completes its task or responds.

### Programmatic Setup (Python SDK)
To enable sub-agents in a custom python script using the SDK:
```python
from google.antigravity import Agent, LocalAgentConfig, types

config = LocalAgentConfig(
    capabilities=types.CapabilitiesConfig(
        enable_subagents=True,  # Enable delegation
    )
)

async with Agent(config=config) as agent:
    response = await agent.chat("Use a subagent to research the file format in details")
    print(await response.text())
```
