---
name: swarm-plus-plus
description: >
  swarm++ — master orchestration skill that coordinates a fleet of local coding
  agent CLIs (Claude Code, Cursor, Kimi, OpenCode, Pi, Antigravity/agy, and
  optionally Codex/Gemini) to keep work moving despite token limits, rate limits,
  and failures. Use whenever a long or large task risks hitting context/token
  caps, when an agent returns a rate-limit/quota/5xx error, or when the user asks
  to "swarm", "fan out", "fall back", or "keep going no matter what". Routes by
  cost and capability, splits oversized work, retries with backoff, and fails over
  to a different agent so progress never stalls. Keywords: swarm, swarm++, multi-agent,
  fallback, failover, rate limit, token limit, context overflow, orchestration,
  agent ladder, resume, continue.
license: MIT
compatibility: "Claude Code, Cursor CLI, Kimi Code, OpenCode, Pi, Antigravity (agy), Codex, Gemini."
metadata:
  author: swarm
  version: "1.0"
---

# swarm++ — Resilient Multi-Agent Orchestration

swarm++ lets one driving agent get a job done by **logically coordinating a mix
of other agent CLIs** on the same machine. Its single promise: **work continues
no matter what.** When the active agent hits a token cap, a rate/quota limit, or
fails, swarm++ splits the work, retries with backoff, and fails over to another
agent — preserving progress across the handoff.

This skill is the **policy + playbook**. The per-agent invocation details live in
the sibling `*-overview` skills:
[[antigravity-overview]], `claude-overview`, `cursor-overview`, `kimi-overview`,
`opencode-overview`, `pi-overview`. Read the relevant overview before invoking an
agent you have not used this session.

---

## When to engage swarm++

Engage when **any** of these is true:

- The task is large/long enough to risk a **context or token-output cap**.
- An agent returns a **rate limit / quota / 429 / overloaded / 5xx** error.
- An agent **stalls, times out, or crashes** mid-task.
- The user explicitly says **swarm / fan out / fall back / keep going no matter what**.
- You want to **parallelize** independent sub-tasks across agents.

If a task is small and one agent can clearly finish it, do **not** over-engineer
— just run it. swarm++ is for resilience and scale, not ceremony.

---

## The agent fleet

All paths are local to this machine. "Print mode" = non-interactive one-shot that
prints the result and exits — the unit swarm++ orchestrates.

| Agent | Binary | Print-mode invocation | Auto-approve flag | Best for |
| :--- | :--- | :--- | :--- | :--- |
| **Pi** | `pi` | `pi -p "PROMPT"` | `defaultProjectTrust=always` | Cheapest; tiny single-file edits, mechanical fixes (local Ollama/GPT-OSS) |
| **Claude Code** | `claude` | `claude -p "PROMPT"` | `--dangerously-skip-permissions` or `--permission-mode auto` | Strong general coding, deep reasoning (`--model opus/fable`, `--effort`) |
| **Cursor** | `cursor-agent` (alias `agent`) | `cursor-agent -p "PROMPT"` | `--force` / `--yolo` (+`--trust`) | Fast multi-file edits, Composer models |
| **Kimi** | `kimi` | `kimi -p "PROMPT"` | `-y` (yolo) / `--auto` | Larger/complex implementation, repo-heavy loops |
| **OpenCode** | `opencode` | `opencode run "PROMPT"` | `--dangerously-skip-permissions` | Multi-provider, local Ollama models, cheap fallback |
| **Antigravity** | `agy` | `agy -p "PROMPT"` | `--dangerously-skip-permissions` | Gemini/Claude via Google SDK, sub-agent branching |
| **Codex** *(if installed)* | `codex` | `codex exec "PROMPT"` | `--dangerously-bypass-approvals-and-sandbox` | GPT-Codex implementation |
| **Gemini** *(if installed)* | `gemini` | `gemini -p "PROMPT"` | `--yolo` | Gemini reasoning |

> Before relying on Codex/Gemini, confirm the binary exists (`which codex`,
> `which gemini`); they may not be on PATH. Skip silently if absent.

---

## Routing ladder (cost-first, capability-aware)

Default to the **cheapest agent that can plausibly do the step**, and climb the
ladder only on failure or when the step clearly needs more capability:

```
Pi  →  Haiku/OpenCode-local  →  Kimi / Cursor  →  Claude(sonnet)  →  Claude(opus) / agy  →  Claude(fable)
cheap, local                    mid                strong              deep                 max
```

Pick the **entry rung** from the task, don't always start at the bottom:

- Trivial/mechanical (rename, format, one-line fix) → **Pi / OpenCode-local**.
- Normal feature work, multi-file → **Kimi** or **Cursor**.
- Architecture, security, tricky debugging, final review → **Claude opus** or **agy**.
- Anything that previously failed at rung N → retry once, then **climb to N+1**.

This ladder is the orchestration default; the user's review/instruction overrides
it at any point.

---

## Failure & limit handling (the core loop)

For every delegated step, wrap the call in this policy:

1. **Classify the outcome** from exit code + stderr/stdout:
   - `success` → capture result, continue.
   - `rate_limit` / `quota` / `429` / `overloaded` / `insufficient_quota` → **switch agent** (don't burn retries on the same provider).
   - `context/token cap` (`context length`, `max tokens`, `too long`, truncated) → **split the work** (see below), then retry.
   - `transient` (`5xx`, `timeout`, `ECONNRESET`, `stream error`) → **retry same agent** with exponential backoff (e.g. 2s, 8s, 30s), max 3, then switch.
   - `auth` (`401`, `not logged in`) → skip that agent for the session, switch.
   - `hard error` (compile/logic) → keep the agent, **fix the prompt** with the error text and retry once.

2. **Switch agent** = move to the next rung (or a same-rung sibling) per the
   ladder, re-issuing the *same* sub-task with the accumulated context summary.

3. **Never let the job die.** If every agent fails a step, stop and report the
   step, the agents tried, and the last error — but only after exhausting the
   ladder.

### Pseudo-policy

```
for step in plan:
    for agent in ladder_from(entry_rung_for(step)):
        for attempt in 1..3:
            res = run(agent, step, context=summary)
            kind = classify(res)
            if kind == success: record(res); break_to_next_step
            if kind == rate_limit or auth: break   # switch agent now
            if kind == context_cap: step = split(step); continue
            if kind == transient: sleep(backoff(attempt)); continue
            if kind == hard_error: step.prompt += res.error; continue
        # agent exhausted -> next agent in ladder
    else:
        report_blocked(step)   # only reached if all agents failed
```

---

## Beating the token / context limit

When a step is too big for one context window:

1. **Decompose first.** Break the task into independent, file-scoped or
   function-scoped sub-tasks. Smaller prompts ≈ smaller context ≈ no cap.
2. **Carry a compact running summary**, not full transcripts. Pass each agent a
   short "state so far + what to do next + acceptance check" instead of history.
3. **Persist progress to disk** (a scratch file / TODO list / the repo itself) so
   a fresh agent with zero context can resume from the artifact, not the chat.
4. **Map-reduce for fan-out:** dispatch independent sub-tasks to several agents in
   parallel (different binaries = independent token budgets), then have one agent
   reduce/merge the outputs.
5. **Round-robin across providers** to spread rate-limit pressure: alternate Pi /
   Kimi / OpenCode / Cursor for successive independent chunks.

Because each CLI has its **own provider account and token budget**, spreading
work across binaries is itself the primary way swarm++ "gets around" a single
provider's limits.

---

## Resuming & handing off cleanly

- Prefer `-p` print mode for orchestrated steps; capture stdout as the result.
- Each agent supports session continuation if you need stateful follow-ups:
  `claude -c`, `cursor-agent` resume, `kimi -C`, `opencode -c`, `pi` sessions,
  `agy -c`. But for cross-agent handoff, **state must live in files**, not a
  single agent's session.
- After a switch, give the new agent: (a) the goal, (b) the running summary,
  (c) the exact sub-task, (d) how success is verified.

---

## Driving swarm++ from the orchestrator

If *you* are the driving agent (e.g. Claude Code) and have a Task/sub-agent tool,
prefer launching the CLIs via shell in print mode so each runs in its **own
process with its own token budget**:

```bash
# cheap first pass
pi -p "Add null checks to @src/util.ts" || \
  kimi -y -p "Add null checks to src/util.ts" || \
  claude --permission-mode auto -p "Add null checks to src/util.ts"
```

The `||` chain is the minimal failover; the full policy above (classify → split →
backoff → switch) is what you apply when you need real resilience rather than a
blind retry.

### Parallel fan-out example

```bash
pi -p "Document module A" &
kimi -y -p "Document module B" &
opencode run "Document module C" &
wait    # then merge the three outputs with one reducer agent
```

---

## Guardrails

- **Auto-approve flags run tools without prompting.** Only use `--force`/`-y`/
  `--dangerously-*` in a trusted workspace the user controls.
- **Honor the user's review.** swarm++ routing is a default; if the user picks an
  agent or vetoes one, that overrides the ladder.
- **Don't thrash.** Cap retries (3/agent) and total ladder climbs; report when
  genuinely blocked instead of looping forever.
- **Keep secrets in env**, never inline API keys into prompts.
- **Verify the merged result** — fan-out outputs must be reconciled and checked
  before declaring success.

---

## TL;DR

1. Plan → split into small, file-scoped steps with disk-persisted state.
2. Start each step at the cheapest capable rung.
3. On rate/token/failure: classify → split or backoff → climb the ladder.
4. Spread chunks across binaries to dodge any single provider's limits.
5. Never stall silently; only stop after the whole ladder is exhausted, then report.
