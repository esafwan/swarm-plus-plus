---
name: add-agent
description: >
  Onboard any new coding-agent CLI into the swarm++ fleet. Discovers the binary,
  reads its --help and config docs, extracts print-mode flags, model selection,
  permission/auto-approve flags, and session-resume commands, then writes a fleet
  entry in swarm-plus-plus SKILL.md, creates a <agent>-overview SKILL.md, and
  wires up symlinks across all installed agent skills directories.
  Use when the user says "add <agent> to swarm", "register <agent>", or installs
  a new coding CLI and wants it in the rotation. Keywords: add agent, register
  agent, new agent, onboard, swarm fleet, agent overview, swarm++.
license: MIT
compatibility: "Claude Code, Cursor, Kimi, OpenCode, Pi, Antigravity, any POSIX shell."
metadata:
  author: swarm
  version: "1.0"
---

# add-agent — Onboard a New Agent CLI into swarm++

Use this skill to add any coding-agent CLI to the swarm++ fleet. It works by
discovering the binary, extracting its interface via `--help` and related docs,
and writing two artifacts: a fleet entry in `swarm-plus-plus` and a standalone
`<agent>-overview` SKILL.md that other skills can reference.

---

## When to use

- User installs a new coding-agent CLI and says "add it to swarm".
- User says "register `<binary>`", "add `<agent>` to the fleet", or similar.
- A new agent CLI becomes available and you want failover to include it.

---

## Discovery steps

Work through these in order, stopping as soon as you have enough to fill the
fleet entry and overview template.

### 1. Locate the binary

```bash
which <agent>                          # fastest path
find ~/.local/bin /opt/homebrew/bin /usr/local/bin -name '<agent>' 2>/dev/null
ls -la ~/.local/share/<agent>/versions/ 2>/dev/null   # versioned install dirs
```

Record the **absolute resolved path** (`readlink -f $(which <agent>)`).

### 2. Read --help

```bash
<agent> --help 2>&1 | head -120
<agent> -h    2>&1 | head -120
```

From the output, extract:

| Item | What to look for |
| :--- | :--- |
| **Print / non-interactive flag** | `-p`, `--print`, `--non-interactive`, `run`, `exec` |
| **Model flag** | `--model`, `-m` |
| **Auto-approve / yolo flag** | `--force`, `--yolo`, `-y`, `--auto`, `--dangerously-skip-permissions`, `--trust` |
| **Continue/resume flag** | `-c`, `--continue`, `-C`, `-S`, `--resume`, `--conversation` |
| **Effort / thinking level flag** | `--effort`, `--thinking`, `--level`, `--reasoning` |
| **Output format flag** | `--output-format`, `--format`, `--json` |
| **Subcommands** | list all top-level subcommands (auth, mcp, agents, models, etc.) |

### 3. Enumerate models

```bash
<agent> models        2>&1 | head -40
<agent> models list   2>&1 | head -40
<agent> --list-models 2>&1 | head -40
```

Note default model, available aliases, and whether thinking/reasoning levels are
embedded in model names (e.g. `"Gemini 3.5 Flash (High)"`) or separate flags.

### 4. Check config / skills location

```bash
ls -la ~/.<agent>/
ls -la ~/.<agent>/skills/ 2>/dev/null
<agent> --version 2>&1
```

Record:
- **Config directory** (where settings, sessions, and skills live)
- **Skills dir** (for adding the swarm symlink)
- **Version**

### 5. Check existing overview skill

```bash
ls ~/.ai-skills/<agent>/skills/ 2>/dev/null
```

If a `<agent>-overview/SKILL.md` already exists, read it and skip to step 6.

---

## Write the overview SKILL.md

Create `~/.ai-skills/<agent>/skills/<agent>-overview/SKILL.md` using this
template. Fill every `<placeholder>` from the discovery above.

```markdown
---
name: <agent>-overview
description: >
  Comprehensive overview of the <Agent Name> CLI (`<binary>`). Covers binary
  path, config files, flags, prompt passing, model selection, thinking/reasoning
  levels, permission modes, agents and sub-agents, MCP servers, sessions, and
  skills. Use this skill whenever another agent needs to invoke or orchestrate
  <Agent Name>.
license: MIT
compatibility: "swarm++, Claude Code, Cursor, Kimi, OpenCode, Pi, Antigravity."
metadata:
  author: <agent>
  version: "1.0"
---

# <Agent Name> — Coding Agent CLI Overview

<One-sentence description from --help preamble.>

---

## CLI Path & Executable

- **Binary**: `<binary>` (resolved: `<absolute-path>`)
- **Version**: `<version>`
- **Config directory**: `~/.<agent>/`
  - `<config-file>` — runtime settings
  - `sessions/` — persisted sessions (if applicable)
  - `skills/` — user skills (symlink-friendly)

---

## Quick Start

```bash
<binary>                           # Interactive mode
<binary> <print-flag> "PROMPT"     # Non-interactive (print) mode
<binary> <continue-flag>           # Continue last session
<binary> <model-flag> <model-id> <print-flag> "PROMPT"
<binary> <autoapprove-flag> <print-flag> "PROMPT"
```

---

## Command Line Flags

| Flag | Description |
| :--- | :--- |
| `<print-flag>` | Non-interactive: run prompt, print response, exit. |
| `<model-flag> <id>` | Select model by alias or full ID. |
| `<effort-flag> <level>` | Reasoning depth (`low` / `medium` / `high` / …). |
| `<autoapprove-flag>` | Auto-approve all tool calls (trusted workspaces only). |
| `<continue-flag>` | Continue the most recent session. |
| `<resume-flag> <id>` | Resume a specific session by ID. |

*(Run `<binary> --help` for the full authoritative list.)*

---

## Model Selection

```bash
<binary> <model-flag> <default-model-alias> <print-flag> "PROMPT"
```

Available aliases / IDs (run `<binary> models` to refresh):

| Alias / ID | Notes |
| :--- | :--- |
| `<model-1>` | Default |
| `<model-2>` | Faster / cheaper |
| `<model-3>` | Highest reasoning |

---

## Session Management

| Action | Command |
| :--- | :--- |
| Continue last | `<binary> <continue-flag>` |
| Resume specific | `<binary> <resume-flag> <session-id>` |

---

## Sub-agents (if supported)

<Describe sub-agent invocation if --help mentions it; otherwise write "Not supported natively — delegate via shell from the orchestrating agent.">

---

## swarm++ integration

Print-mode invocation (used by swarm++ for orchestrated steps):

```bash
<binary> <print-flag> "PROMPT"
<binary> <autoapprove-flag> <print-flag> "PROMPT"   # fully headless
```

Suggested ladder rung: **<cheap|mid|strong|deep>** — <one-line rationale>.
```

---

## Update the swarm-plus-plus fleet table

Open `~/.ai-skills/swarm/skills/swarm-plus-plus/SKILL.md` and add a row to the
**The agent fleet** table:

```
| **<Agent Name>** | `<binary>` | `<binary> <print-flag> "PROMPT"` | `<autoapprove-flag>` | <best-for> |
```

Then insert the agent into the **routing ladder** at the correct cost/capability
rung. Use this guide:

| Rung | Criteria |
| :--- | :--- |
| **cheapest** | Local model (Ollama/OSS), near-zero API cost |
| **mid** | Fast hosted model, good for standard feature work |
| **strong** | Reliable hosted model, multi-file, architecture |
| **deep** | High-reasoning model, security/review/complex debug |
| **max** | Most capable model, last-resort fallback |

---

## Wire up symlinks

For every agent skills directory that exists on this machine, add a symlink so
the new `<agent>-overview` skill and the updated `swarm-plus-plus` skill are
accessible:

```bash
# Discover existing agent skills dirs
for d in ~/.claude ~/.cursor ~/.kimi-code ~/.opencode ~/.codex ~/.gemini/config ~/.pi \
          ~/.<new-agent>; do
  skills_dir="$d/skills"
  if [ -d "$skills_dir" ]; then
    # Link the new agent's own skill pack
    ln -sfn ~/.ai-skills/<agent>/skills "$skills_dir/<agent>"
    echo "linked: $skills_dir/<agent>"
  fi
done
```

Also verify the `swarm` symlink exists in the new agent's own skills dir (if it
has one):

```bash
ls -la ~/.<new-agent>/skills/swarm 2>/dev/null || \
  ln -sfn ~/.ai-skills/swarm/skills ~/.<new-agent>/skills/swarm && \
  echo "swarm symlink added to <new-agent>"
```

---

## Verify

```bash
# 1. Overview SKILL.md exists
cat ~/.ai-skills/<agent>/skills/<agent>-overview/SKILL.md | head -5

# 2. Fleet entry added
grep "<agent>" ~/.ai-skills/swarm/skills/swarm-plus-plus/SKILL.md

# 3. Symlinks resolve correctly
for d in ~/.claude ~/.cursor ~/.kimi-code ~/.opencode ~/.codex ~/.gemini/config; do
  printf "%-22s " "$d/skills/<agent>:"
  ls -ld "$d/skills/<agent>" 2>/dev/null | awk '{print $NF}' || echo "MISSING"
done
```

---

## Quick checklist

- [ ] Binary discovered and absolute path confirmed
- [ ] `--help` read; print flag, model flag, auto-approve flag, continue flag extracted
- [ ] Models enumerated (default + aliases)
- [ ] Config / skills directory confirmed
- [ ] `<agent>-overview/SKILL.md` written under `~/.ai-skills/<agent>/skills/`
- [ ] Fleet table row added to `swarm-plus-plus/SKILL.md`
- [ ] Ladder rung assigned
- [ ] Symlinks created in all existing agent skills dirs
- [ ] `swarm` symlink added to new agent's own skills dir (if it has one)
- [ ] Verify grep + symlink checks pass
