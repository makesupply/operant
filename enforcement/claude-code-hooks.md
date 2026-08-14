# Enforcement Pack: Claude Code Hooks

The skill teaches judgment; hooks guarantee a floor. This pack hard-enforces the subset of Operant that should never depend on model compliance — destructive commands, history rewrites, unbounded mutations, secret staging, and prompt injection — and wires in the config auditor and the learning loop. Everything here is optional: the skill works without it, and smaller models benefit from it most.

The gates ship as **ready-to-run, self-tested scripts** — you reference them, you don't paste them. That's the difference between this version and a prose spec: [`policy-gate.py`](policy-gate.py) (gates G1/G2/G3/G6) and [`injection-sentinel.py`](injection-sentinel.py) (gate G8) are real files with passing self-tests; the [generic policy spec](generic-policy-spec.md) defines all nine gates host-agnostically.

**Sync rule:** hooks and skill text must agree. A hook blocking something the skill never mentions produces confusing denials; a skill rule with no hook is just (acceptable) trust. When you edit one, check the other.

## How Claude Code hooks work (30 seconds)

Hooks are shell commands configured in `.claude/settings.json` (project) or `~/.claude/settings.json` (global), fired on events like `PreToolUse` (before a tool runs), `PostToolUse` (after), `Stop` (turn end), and `SessionStart`. A `PreToolUse` hook receives the pending tool call as JSON on stdin; **exit code 2 blocks the call** and feeds stderr back to the model as guidance; exit 0 allows it. Full schema: Claude Code docs → Hooks.

## 1. The policy gate — G1/G2/G3/G6 (the one that matters)

[`policy-gate.py`](policy-gate.py) is a single `PreToolUse` hook covering destructive commands (G1), history rewrites (G2), unbounded SQL mutations (G3), and secret staging (G6). It blocks the catastrophic subset and returns gate-specific, actionable guidance to the model — a code-level backstop for [safety.md](../references/safety.md)'s Tier 3, catching the cases a model might rationalize past. It is stdlib-only and cross-platform.

**Wiring, in `.claude/settings.json`:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|PowerShell",
        "hooks": [
          { "type": "command", "command": "python enforcement/policy-gate.py" }
        ]
      }
    ]
  }
}
```

(Use `python3` on systems where that's the Python 3 launcher; `python` on Windows.)

**Verify it before trusting it** — every runnable subsystem ships a real self-test:
```bash
python enforcement/policy-gate.py self-test          # gate patterns, positives AND negatives
python enforcement/injection-sentinel.py self-test   # G8 patterns, tuned-narrow negatives included
python shield/shield.py self-test                    # planted-risk scan in a throwaway config surface
python instincts/instincts.py self-test              # the full record/inject/correct/prune loop
python evals/eval-runner.py self-test                # the eval runner itself
```

Manual spot checks of the wired hook, end to end:
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /x"}}' | python enforcement/policy-gate.py; echo "exit=$?"   # → guidance + exit 2
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}'   | python enforcement/policy-gate.py; echo "exit=$?"   # → exit 0
```

**Tuning:** the pattern list is deliberately narrow — high-certainty catastrophic patterns only. Every false positive teaches the model (and the user) to route around the gate, which is worse than no gate. Add project-specific patterns (your deploy commands, your prod database name) *inside* the script rather than broadening the generic ones. The gate is a *backstop*, not a guarantee — a determined command can evade regexes; the skill's behavioral layer is the primary defense, the hook catches the reflexive miss.

## 2. The injection sentinel — G8

[`injection-sentinel.py`](injection-sentinel.py) is a `PostToolUse` hook on fetch/search tools. It can't block (the content already arrived) but it scans the returned content for agent-targeting instructions and, on a hit, returns a warning so the model names the injection, treats it as data, and reports it to the user.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "WebFetch|WebSearch",
        "hooks": [
          { "type": "command", "command": "python enforcement/injection-sentinel.py" }
        ]
      }
    ]
  }
}
```

## 3. Config-surface audit — Operant Shield (pre-commit / CI)

[`../shield/shield.py`](../shield/README.md) audits the agent's own config surface (CLAUDE.md, settings, hooks, MCP configs) for planted instructions, committed secrets, over-broad permissions, and risky hooks. It's not a per-tool hook — run it in CI or a pre-commit hook, especially before adopting any third-party skill bundle:

```bash
python shield/shield.py . --fail-on high    # exit 1 fails the build on any HIGH finding
```

## 4. The learning loop — Instincts (SessionStart + Stop)

[`../instincts/`](../instincts/README.md) injects proven behavioral patterns at session start and records candidates at session end.

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "python instincts/instincts.py inject" } ] }
    ],
    "Stop": [
      { "hooks": [ { "type": "command", "command": "python instincts/instincts.py record --file .operant/candidates.json" } ] }
    ]
  }
}
```

(The `SessionStart` hook's stdout is added to the session context; the agent writes `candidates.json` during the session for the `Stop` hook to ingest. See the [Instincts README](../instincts/README.md) for the candidate format.)

## 5. Soft nudges (Stop-event reminders)

A `Stop` hook can't verify quality, but it can put the right checklist in front of the model at the right moment — useful for smaller models that follow checklists better than they recall them:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Operant gate: before ending — did you (1) verify rather than assume, (2) lead the final message with the outcome, (3) leave no promise/plan as your last paragraph? See checklists/before-claiming-done.md'"
          }
        ]
      }
    ]
  }
}
```

Use nudges sparingly — one short reminder at Stop. A hook that lectures on every event becomes noise the model (correctly) tunes out.

## 4. What NOT to enforce

Tempting but counterproductive as hooks:

- **Communication rules** (outcome-first, no filler) — unenforceable mechanically without absurd false positives; this is what the skill text and the [eval suite](../evals/eval-suite.md) are for.
- **Verification requirements** ("must run tests before claiming done") — a hook can't know whether the claim is done-shaped or whether tests are runnable; forcing test runs on every Stop punishes conversation turns.
- **Broad command denylists** — blocking `curl`, `pip install`, etc. belongs in Claude Code's native permission system (`settings.json` → `permissions`), which has proper allow/deny/ask UX. Hooks are for the patterns permissions can't express.

The division of labor stands: **prompts produce judgment, permissions produce consent, hooks produce guarantees** — each layer doing only what it's actually good at.

## Verifying the pack works

1. Fresh session, ask the agent to `rm -rf` a scratch directory → the gate should block with the safety.md message, and the agent should respond by *looking at the target and asking properly* (that's the skill layer catching the hook's handoff).
2. Stage a fake `.env` and ask for a commit → tripwire fires.
3. Run evals E12–E14 from the [eval suite](../evals/eval-suite.md) — the pass rate on the safety cluster should be 3/3 with the pack installed, on any model tier.
