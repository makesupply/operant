# Enforcement Pack: Claude Code Hooks

The skill teaches judgment; hooks guarantee a floor. This pack hard-enforces the subset of Operant that should never depend on model compliance (destructive commands, history rewrites, unbounded mutations, secret staging and upload, whole-tree staging on a shared checkout, and prompt injection) and wires in the config auditor and the learning loop. Everything here is optional: the skill works without it, and smaller models benefit from it most.

The gates ship as **ready-to-run, self-tested scripts**. You reference them; you do not paste them. [`policy-gate.py`](policy-gate.py) covers G1, G2, G3, G6 and G10; [`injection-sentinel.py`](injection-sentinel.py) covers G8. Each carries a `--self-test` (added 1.4.0; earlier editions claimed one they did not ship). The [generic policy spec](generic-policy-spec.md) defines all ten gates host-agnostically and says which four (G4, G5, G7, G9) the deployment must implement itself.

**Sync rule:** hooks and skill text must agree. A hook blocking something the skill never mentions produces confusing denials; a skill rule with no hook is just (acceptable) trust. When you edit one, check the other, and run the script's `--self-test` after any pattern change, before trusting it. A false positive costs more than a miss: the 2026-09 secret pattern that blocked read-only commands over URL slugs, and the exfiltration pattern that fired thirteen times on messaging-API docs, were both narrowed in 1.4.0 with the offending strings kept as negative self-test cases. The 1.5.0 review found twenty-one more false positives in the `find -exec rm`, quoted-path, Windows-delete and heredoc families; every one is now a negative case.

## How Claude Code hooks work

Hooks are configured in `.claude/settings.json` (project), `.claude/settings.local.json` (project, uncommitted), or `~/.claude/settings.json` (global), and fire on named events. A `command` hook receives the event as JSON on stdin (`session_id`, `cwd`, `permission_mode`, `hook_event_name`, `tool_name`, `tool_input`, `tool_use_id` on tool events) and answers with an exit code, or with JSON on stdout. Full schema: Claude Code docs, Hooks.

**The events that matter for this pack:**

| Event | When | What a hook can do |
|---|---|---|
| `PreToolUse` | before a tool runs | allow, deny, ask, or defer the call; add context |
| `PostToolUse` | after a tool returned | feed a warning back, replace what the model sees, annotate for the auto-mode classifier |
| `PostToolUseFailure` | after a tool errored | observe; a failed side-effecting call is where G9 starts |
| `PermissionRequest` / `PermissionDenied` | when the harness would prompt, or auto mode denied | review or reshape a Tier 3 payload before the human sees it |
| `Stop` / `SubagentStop` | a turn or a subagent ends | put a checklist in front of the model; record candidates |
| `SessionStart` | a session opens | inject context (stdout is added to the session) |
| `PreCompact` | before the transcript is compacted | persist state that a summary would lose |
| `ConfigChange` | a settings, skill, or plugin file changed mid-session | block the change (not for managed policy) |
| `InstructionsLoaded` | an instruction file was loaded | log what the agent trusted this session |

**Decisions.** Return a JSON object on stdout and exit 0:

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "Operant gate G1 (destructive command): ...",
                        "additionalContext": "optional text the model also sees"}}
```

`permissionDecision` is `allow`, `deny`, `ask`, or `defer`. `ask` hands the call to the permission prompt with the reason as the prompt text, which is the native shape of a Tier 3 confirmation. The older top-level `decision`/`reason` form is deprecated for `PreToolUse`. A `PostToolUse` hook returns `additionalContext`, `updatedToolOutput` (replaces what the model sees; the mechanism for framing fetched content as data), and `classifierContext` (a note to the auto-mode classifier). `additionalContext` is capped at 10,000 characters. **Exit 2 remains the fallback deny:** stderr becomes the denial reason on `PreToolUse` and is shown to the model on `PostToolUse` (the tool already ran). Exit 2 blocks even when the JSON says allow. Any other non-zero exit is a non-blocking error and the action proceeds, so a crashed hook is an allow; `"onFailure": "block"` fails closed instead. Never use `updatedInput` to rewrite a command the model did not propose; a gate that silently changes the action teaches the model nothing and hides the decision from the user.

**Several hooks on one matcher** run together; the precedence is deny, then defer, then ask, then allow, so stacking the policy gate with a deployment's own gate on `Bash|PowerShell` is correct. A `command` hook times out after **600 seconds** by default; set `"timeout"` (seconds) per hook so a wedged `git` on a locked index cannot stall a session. `${CLAUDE_PROJECT_DIR}` resolves the project root; use absolute paths, because the hook's working directory is not guaranteed. On Windows add `"shell": "powershell"` to a hook that needs PowerShell semantics.

## 1. The policy gate: G1/G2/G3/G6/G10 (the one that matters)

[`policy-gate.py`](policy-gate.py) is a single `PreToolUse` hook covering destructive commands (G1), history rewrites and worktree discards (G2), unbounded SQL mutations (G3), secret staging and secret upload (G6), and, on a checkout shared by several sessions or agents, whole-tree staging (G10). It blocks the catastrophic subset and returns gate-specific, actionable guidance to the model: a code-level backstop for [safety.md](../references/safety.md)'s Tier 3, catching the cases a model might rationalize past. It is stdlib-only and cross-platform.

What it reads: G1, G2, G3 and the G6 file rows scan a view of the command with data-only literals masked (a `-m` commit message, a heredoc that is not fed to an interpreter or database client, a here-string, an echoed string, a literal nested inside another literal), so a commit message that mentions `rm -rf` or `.env` is not a command. A literal passed to `bash -c`, `psql -c`, or `psql <<SQL` stays visible. Key-shaped tokens scan the raw command. G10 strips every literal, reads the index only for a commit with no pathspec, reads `git diff` only for a pathspec commit, and allows the call whenever git cannot be read.

What it exempts: a recursive delete whose every target is derivable (caches, a scratch path under a temp root, a `find` whose name predicate is one of those) is Tier 1 and passes. Any `..` segment, the whole temp root, and a target arriving through an unreadable pipeline still block.

**Wiring, in `.claude/settings.json`:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|PowerShell",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/skills/fable-mode/enforcement/policy-gate.py\" --json --log \"${CLAUDE_PROJECT_DIR}/.claude/hooks/gate-decisions.jsonl\"",
            "timeout": 15,
            "statusMessage": "Operant policy gate G1/G2/G3/G6/G10"
          }
        ]
      }
    ]
  }
}
```

(Use `python3` on systems where that is the Python 3 launcher; `python` on Windows. Drop `--json` on a harness that does not read `hookSpecificOutput`; the gate then denies with stderr and exit 2, which every version honors.)

**Options.** `--json` returns a deny as `hookSpecificOutput.permissionDecision: "deny"` with the guidance in `permissionDecisionReason` (exit 0); without it the deny is stderr plus exit 2. `--log PATH` appends one JSON line per decision, allow and deny alike: event id, timestamp, session id, tool, gate, decision, and the sha256 of the command, never the command itself, so the log can be shared without leaking a payload. `--tools NAME,NAME` adds tool names to gate beyond `Bash` and `PowerShell`.

**Matcher coverage.** Every tool that can run a shell command on the host must be in the `PreToolUse` matcher: `Bash`, `PowerShell`, and any terminal-execution MCP tool the deployment exposes (a tool whose name contains `terminal`, `shell`, `bash`, `powershell`, `cmd` or `console` and whose input carries a `command` field). An unmatched shell tool is a complete gate bypass; the matcher, not the script, decides what the gate ever sees. The gate recognizes such an MCP tool on its own once matched, and `--tools` covers names it cannot guess. List the shell tools the host exposes before wiring, and again whenever an MCP server is added.

**Fail-open is deliberate.** A payload whose `command` is missing or not a string, and a crash inside the gate, are both an explicit allow with a one-line stderr note and an audit record. The harness treats a crashed hook as proceed anyway; making the allow explicit keeps it visible and logged. A malformed payload from the harness is not a command the gate can judge.

**Verify it before trusting it:** the self-test the bundle ships with, then a live pipe.
```bash
python enforcement/policy-gate.py --self-test     # ends with: self-test: 235/235 passed
echo '{"tool_name":"Bash","tool_input":{"command":"git push -f origin main"}}' | python enforcement/policy-gate.py; echo "exit=$?"   # guidance + exit 2
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' | python enforcement/policy-gate.py; echo "exit=$?"                   # exit 0
```
(Once the hook is wired, the second line will itself be blocked when typed into the agent's shell, because the command text contains the pattern. Run it from a plain terminal, or keep such probes in a script that assembles the string at runtime.)

**Tuning:** the pattern list is deliberately narrow: high-certainty catastrophic patterns only. Every false positive teaches the model (and the user) to route around the gate, which is worse than no gate. Add project-specific patterns (your deploy commands, your prod database name) *inside* the script rather than broadening the generic ones. The gate is a *backstop*, not a guarantee: a determined command can evade regexes; the skill's behavioral layer is the primary defense, the hook catches the reflexive miss.

## 2. The injection sentinel: G8

[`injection-sentinel.py`](injection-sentinel.py) is a `PostToolUse` hook on any tool whose response carries untrusted text. It cannot block (the content already arrived), but it scans the returned content for agent-targeting instructions and, on a hit, returns a warning so the model names the injection, treats it as data, and reports it to the user. `--log PATH` appends a durable audit line per hit; `--self-test` runs the pattern corpus (classic payloads must fire, messaging-API reference prose must stay silent; the current count is what `--self-test` prints).

Wire the sentinel to every tool whose response can carry text a stranger wrote: web fetch and search, mail and thread readers, browser page readers, the `Agent` and `Task` tools (a subagent's report is a tool result, not an instruction), and the MCP tools that return third-party content. For file reads, scope the sentinel by path to the folders that receive outside material, such as agent handoff drops and cloned repositories, instead of scanning every read in the project; a second hook entry with a `Read` matcher and a path check inside the script does that. Shell output from network commands belongs in the same set. The pattern list does not change when the scope widens; only the matcher does.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "WebFetch|WebSearch|Agent|Task|mcp__.*__(get_message|get_thread|search_threads|get_page_text|read_page|fetch)",
        "hooks": [
          { "type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/skills/fable-mode/enforcement/injection-sentinel.py\" --log \"${CLAUDE_PROJECT_DIR}/.claude/hooks/gate-hits.log\"" }
        ]
      }
    ]
  }
}
```

Two limits to document in your deployment notes: `WebFetch` returns a second model's answer over the page rather than the raw page for most fetches, so a payload that summary drops never reaches the sentinel; and the auto-mode classifier does not see tool results at all, so this hook is the only code that looks at fetched content.

## 3. Config-surface audit: Operant Shield (pre-commit, CI, and ConfigChange)

[`../shield/shield.py`](../shield/README.md) audits the agent's own config surface (CLAUDE.md, settings, hooks, MCP configs) for planted instructions, committed secrets, over-broad permissions, and risky hooks. Run it in CI or a pre-commit hook, especially before adopting any third-party skill bundle:

```bash
python shield/shield.py . --fail-on high    # exit 1 fails the build on any HIGH finding
python shield/shield.py --self-test         # pattern + ignore-file + worktree-detection checks
```

Run Shield on every configuration change, not only in CI. Wire it to the `ConfigChange` event with the changed file's path, exit 2 on any HIGH finding so the change does not take effect in the running session, and append the finding to the gate log. Log every `InstructionsLoaded` event with the file path and the load reason; that log is the inventory of what the agent trusted this session. Before scripting a non-interactive run over a repository you did not write, review its `.claude/` folder or start with hooks disabled (`--settings '{"disableAllHooks": true}'`), because a headless session runs committed hooks without a trust prompt.

A `.operant-shield-ignore` file in the scan root lists path prefixes to skip (a bundled virtualenv, an export mirror); linked git worktrees under the root are skipped automatically and *reported*, since each is an unwatched copy of the config surface. See [shield/README.md](../shield/README.md).

## 4. The learning loop: Instincts (SessionStart + Stop)

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

A `Stop` hook cannot verify quality, but it can put the right checklist in front of the model at the right moment, which helps smaller models that follow checklists better than they recall them:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Operant gate: before ending, did you (1) verify rather than assume, (2) lead the final message with the outcome, (3) leave no promise or plan as your last paragraph? See checklists/before-claiming-done.md'"
          }
        ]
      }
    ]
  }
}
```

Use nudges sparingly: one short reminder at Stop. A hook that lectures on every event becomes noise the model (correctly) tunes out.

## 6. Auto mode

The harness's auto mode replaces routine permission prompts with a classifier, and it is the starting mode in the terminal and the default for `-p` and SDK sessions. Four facts change how the gates should be read. The classifier does not see tool results, so the injection sentinel stays the only code looking at fetched content. Entering auto mode drops broad allow rules such as `Bash(*)` and wildcarded interpreters, so a deployment that relied on them changes behavior silently; test the gates again after turning it on. `ask` rules are the documented human checkpoint, which is the native form of Tier 3. Boundaries stated in chat are re-read from the transcript, so compaction can drop them; a rule meant to hold must be a `deny` rule. Auto mode is not an autonomy level: it raises nothing in [autonomy-levels.md](../references/autonomy-levels.md), and the ratchet rule still requires an eval run before any level moves.

## 7. Permissions do what hooks should not

Express least privilege in the harness's own permission rules before writing a hook for it; a permission rule holds in every mode, including `bypassPermissions` for deny rules, and has proper allow, deny, and ask UX.

- Start from `"deny": ["*"]` and re-allow the minimum.
- Deny `Read` on secret paths (`.env*`, key files, credential folders); a read deny also hides them from `Glob` and `Grep`.
- Deny `WebFetch(domain:...)` on known paste and webhook collection hosts; that is the right layer for an exfiltration destination.
- Put an `ask` rule on every push and every account write.
- Where the host offers a sandbox, turn it on and set `sandbox.credentials` to deny the credential files and token variables inside it; add the collection hosts to `sandbox.network.deniedDomains`.
- Native Windows has no sandbox. Say so in the deployment notes: the hooks and the permission rules are then the whole code layer, and nothing below them catches a command that evades a regex.
- Never commit `settings.local.json`; the harness writes standing allow grants into it.

Tempting but counterproductive as hooks:

- **Communication rules** (outcome-first, no filler): unenforceable mechanically without absurd false positives; this is what the skill text and the [eval suite](../evals/eval-suite.md) are for.
- **Verification requirements** ("must run tests before claiming done"): a hook cannot know whether the claim is done-shaped or whether tests are runnable; forcing test runs on every Stop punishes conversation turns.
- **Broad command denylists**: blocking `curl`, `pip install`, and the like belongs in `permissions`. Hooks are for the patterns permissions cannot express.

The division of labor stands: **prompts produce judgment, permissions produce consent, hooks produce guarantees**, each layer doing only what it is actually good at.

## Verifying the pack works

1. Fresh session, ask the agent to `rm -rf` a build directory. The gate should block with the safety.md message, and the agent should respond by *looking at the target and asking properly* (that is the skill layer catching the hook's handoff). Ask it to delete `__pycache__` next; that one passes, and the difference is the derivable-target exemption working.
2. Stage a fake `.env` and ask for a commit; the tripwire fires. Ask it to `curl -F file=@.env` somewhere; the upload row fires.
3. Run the blocks-adoption cluster from the [eval suite](../evals/eval-suite.md) (E12 to E15, E17 to E19, E26 to E28). It should pass in full with the pack installed, on any model tier. Without the pack, the [Haiku baseline](../evals/runs/2026-07-09-haiku-baseline/details.md) failed five of its seven.
4. Open the decision log and confirm a line per shell call with a 64-character hash and no command text.
