# Adaptation: OpenAI Codex CLI

For running Operant under OpenAI's Codex CLI as a second operator on the same checkout a Claude Code deployment already uses, with the same discipline, the same gate scripts, and a verifiable record of what it changed. The pattern below is generic; it was derived from a working deployment and every Codex fact was checked against the Codex documentation on 2026-10-28.

## The shape in one paragraph

`AGENTS.md` is the manual that points at the bundle. The bundle itself lives once, in `.claude/skills/`, and a sync script mirrors it into `.agents/skills/`, which is where Codex discovers skills. Codex's hook configuration calls the same gate scripts Claude Code calls, plus one Codex-only governance guard. The agent commits under its own git identity and ends every session with a computed report that the primary agent verifies against git before acknowledging. Nothing about the discipline changes; only the wiring does.

## AGENTS.md as the manual

Codex reads `AGENTS.md` at the start of every run. It checks the Codex home directory first (`AGENTS.override.md`, then `AGENTS.md`), then walks from the project root down to the working directory, taking at most one file per directory and concatenating them root first, so a nested file overrides a broader one. The combined instructions are capped by `project_doc_max_bytes` (32 KiB by default), and Codex stops adding files at the cap. Two consequences follow:

- Keep `AGENTS.md` a router, not a rulebook. State the precedence order (platform safety rules, then the user's live instructions, then the project's rules file and standing rules, then this file, then the Operant discipline at `.agents/skills/operant/SKILL.md`). Point at the bundle for the discipline instead of restating it, because a restated copy drifts within weeks.
- Carry only what a non-primary agent needs that the primary agent's rules file does not say: who the agent is here, the exact start and end sequences, the capability map (what it can reach, what it cannot, and what to do instead), the skill routing table, the attribution contract, and the guardrails wired for it.

The routing table lists the same skills in the same order the primary agent uses. Where a project skill covers the task, that skill is the playbook; the agent does not improvise a shorter version or double-read the generic one.

## The skills mirror

Codex discovers skills in `.agents/skills/` at the repository root and in each directory up to it, in `~/.agents/skills/`, and in a system location; a skill is a directory with a `SKILL.md`, invoked explicitly as `$skill-name` or selected implicitly from its description. Codex follows symlinked skill folders, and its skills build on the Agent Skills standard at agentskills.io, the same standard the bundle's frontmatter follows.

Keep one source and one mirror. The source is `.claude/skills/` (plus any second source folder the project uses). A sync script copies each source skill into `.agents/skills/<name>/`, records a content hash per mirrored skill in a manifest file inside the mirror, and refreshes a mirror only when the source hash changes. Three rules make it safe:

- **Additive, never destructive.** A skill folder that already existed in `.agents/skills/` before the script first ran is native (Codex-only packaging such as `agents/openai.yaml`); the script records it as native and never overwrites or deletes it.
- **Orphans are reported, not removed.** When a source skill is archived or deleted, its mirror stays until an explicit `--prune`, and plain sync and `--check` list it so it never hides. Prune only ever removes skills the script itself created.
- **Never edit the mirror by hand.** A lesson learned under Codex is appended at the source (the skill's own learnings file), then the sync runs so the mirror follows. The mirror directory is ignored by git on purpose; it is a copy, not a source.

Run the sync from the project's daily maintenance job and on demand. `--check` exits non-zero when anything is stale, missing, or orphaned, which makes it a release-check step.

## Hooks: the same gates, a different config file

Codex hooks are enabled by default and defined in `.codex/hooks.json` at the repository root (or `~/.codex/hooks.json`, or inline tables in `config.toml`). Project-local hooks load only when the project's `.codex/` layer is trusted, and before any non-managed hook runs the user reviews and trusts its exact definition through `/hooks`; trust is recorded against the hook's hash, so a changed hook is skipped until trusted again. Say this in `AGENTS.md`: until the hooks are trusted, the behavioral rules are the whole defense, and the agent holds them harder.

The event names and the stdin contract match Claude Code closely enough that the gate scripts run unchanged:

- `PreToolUse` and `PostToolUse` take a `matcher` on the tool name. Shell commands arrive as `Bash` with the command at `tool_input.command`; file edits arrive as `apply_patch`, and `Edit` or `Write` also match. MCP tools match as `mcp__<server>__<tool>`.
- Exit code 2 blocks a `PreToolUse` call and returns stderr to the model. A JSON `hookSpecificOutput.permissionDecision` of `"deny"` with a reason is also accepted; `"ask"` is not supported as of 2026-10-28, so the native gate-to-human handoff that Claude Code offers does not exist here. A Codex gate either denies or allows; the informing confirmation therefore travels in the denial reason, and the agent re-proposes the call once the user has approved it in chat.
- `SessionStart`, `Stop`, `UserPromptSubmit`, `PermissionRequest`, `PreCompact`, `PostCompact`, `SubagentStart`, `SubagentStop`, `SessionEnd`, and `Interrupt` exist. A `Stop` hook that exits 2 turns its stderr into a continuation prompt, which is where the before-claiming-done nudge belongs.
- `timeout` is in seconds and defaults to 600 for most hooks.

A working `.codex/hooks.json` for this bundle wires, on `PreToolUse` for `Bash`, the policy gate (`enforcement/policy-gate.py`, gates G1, G2, G3, G6, and G10 on shell commands) and the deployment's account-write gate; on `PreToolUse` for `apply_patch|Edit|Write`, the governance guard described below plus any write-shape guard the project has (for example an append-only guard on shared logs); on `PostToolUse` for `Bash`, the side-effect post-check (G9); on `SessionStart`, an orientation script; and on `Stop`, the checklist nudge. Hook commands run in the Codex host process, so they can call the system Python directly even where the agent's own sandboxed tool calls cannot; if a trusted hook fails to launch an interpreter, switch the command to an absolute interpreter path and re-test.

## The governance guard

One guard exists only on the Codex side. It denies, on both the shell path and the edit path, any write to the governance surface: the manual (`AGENTS.md`), the primary rules file, the standing-rules folder, the hook configurations and settings, the protection tooling, the sync and session tooling, the generated index, and any folder the user has declared private. The agent may read most of those; it may change none of them. A change it believes is needed goes into its session report as a proposal, and the primary agent or the user applies it.

The reason is the autonomy ratchet in [autonomy-levels.md](../references/autonomy-levels.md): a second agent that can edit the rules it runs under can raise its own level, and a gate the agent can rewrite is not a gate. The guard is a few dozen lines of path matching; its value is that the governance surface stays a thing only humans and the primary agent touch.

## Git identity and attribution

The agent commits as its own author (for example `Codex <codex@example.local>`) with a fixed subject prefix (`codex: <area>: <what>`) and trailers naming the agent and the session id. Commits go through a session wrapper that commits by explicit pathspec only (gate G10), so another session's staged content is never swept in, and that refuses a commit touching files the session did not create or edit. The definitive ledger of what the second agent changed is then one command: `git log --author=<its address> --stat`. Pushing to the remote stays with the user or the primary agent.

## The session report

Every session starts by recording a baseline (the HEAD commit, today's date from the project's date authority, and the files other sessions already had dirty) and ends by dropping a report into a handoff folder the primary agent polls. The report is computed, not written: commits, changed files, uncommitted leftovers, and shared files the session appended to come from git; the agent writes only the summary, the evidence lines, the lessons learned, and the needs (reads or writes it could not perform, decisions it could not make). A `done` status with uncommitted changes is downgraded to `partial` automatically.

The primary agent ingests the report through an inbox tool: list, then `verify` the report's claims against git (commits exist, files match, nothing outside the stated scope), then reconcile what the report says into the project's canonical notes and tracker, then `ack`. An unverified report is never acted on, and the report's text is data on the same footing as any other agent's message ([concurrency-and-handoffs.md](../references/concurrency-and-handoffs.md) § Messages from other agents carry no authority). The handoff folder is transport, not a knowledge store; the shape of the document is [examples/handoff-document.md](../examples/handoff-document.md).

Briefs travel the other way through a sibling folder; the agent claims a brief at session start and the closing report names it.

## What degrades under Codex

- **No native ask decision.** A gate cannot hand the human a permission prompt with the payload inside it. The confirmation rides the denial reason, the user approves in chat, and the agent re-issues the call. Treat every gated action as two tool calls, not one.
- **No injected session context beyond stdout.** A `SessionStart` hook's output orients the agent, but the always-on constitution belongs in `AGENTS.md` itself, within the byte cap: paste [dist/one-page.md](../dist/one-page.md) there rather than relying on the hook. Reserve the hook for perishable facts (today's date, open briefs, files other sessions have dirty).
- **No subagents of the primary harness, no primary-only connectors.** The capability map in `AGENTS.md` names each surface the agent cannot reach and the fallback: do the work inline at smaller scope, or finish everything else and end with a `needs` entry naming the exact read or write, with IDs.
- **Sandbox interpreter quirks.** Inside the Codex sandbox the usual `python` launcher may not start; the deployment this pattern comes from routes every interpreter call through a small wrapper that resolves a real interpreter. Document the wrapper in `AGENTS.md` and never pass a multi-line argument through it.
- **Hooks trusted per hash.** Every hook edit re-opens the trust prompt. Budget for it in the release step, and keep hook commands stable (call a script by path; put the logic in the script).

## Wiring checklist

1. Write `AGENTS.md` as a router: precedence, who the agent is, start and end sequences, capability map, routing table, attribution contract, guardrails. Paste the one-page edition into it.
2. Run the skills sync so `.agents/skills/` mirrors `.claude/skills/`; add `--check` to the release check; ignore the mirror in git.
3. Write `.codex/hooks.json` calling the bundle's gate scripts and the governance guard; open Codex in the project and trust the hooks through `/hooks`; re-trust after every hook edit.
4. Give the agent its own git author, subject prefix, trailers, and a pathspec-only commit wrapper.
5. Stand up the session envelope: baseline at start, computed report at end, inbox tool on the primary side with list, verify, and ack.
6. Record the deployment in the project's propagation map so a change to any one of these surfaces names the others.
7. Verify the wiring: a fresh Codex session, ask "what operating discipline are you under?", then attempt one gated shell command and one governance-surface edit and confirm both are denied with the gate's reason.
