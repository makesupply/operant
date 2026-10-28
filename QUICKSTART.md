# Operant Quickstart

Five minutes from download to a disciplined agent. Pick your platform.

## Claude Code (2 minutes)

Three install routes; any one is enough.

```bash
# Route A: copy the bundle into the project's skills directory
cp -r operant <your-project>/.claude/skills/operant
#   (or ~/.claude/skills/operant for every project)

# Route B: plugin marketplace
claude plugin marketplace add makesupply/operant
claude plugin install operant@operant-marketplace

# Route C: the cross-tool skills CLI
npx skills add makesupply/operant
```

Then make it always-on. Either add this to the top of `CLAUDE.md`:

> **Operant is always on.** Whichever model runs this session, read `.claude/skills/operant/SKILL.md` at session start and follow its operating discipline for the entire session. Consult its references/, playbooks/, and checklists/ when the situation matches.

or wire a `SessionStart` hook that injects `dist/one-page.md` as additional context, which survives CLAUDE.md edits and reaches subagents. Both are shown in [adaptations/claude-code.md](adaptations/claude-code.md).

Verify: start a new session and ask "what operating discipline are you under?" The answer names the Ten Principles. `claude plugin validate .` inside the bundle must pass before you publish it.

Optional hardening: implement the [generic policy spec](enforcement/generic-policy-spec.md). The [Claude Code hooks pack](enforcement/claude-code-hooks.md) is a ready implementation of six of the ten gates; the other four (external send, production change, PII, idempotency) are specified and left to your deployment, because they need to know your platforms. Every shipped script carries a `--self-test`.

## Cursor, Windsurf, Copilot, Gemini CLI, Codex (5 minutes)

1. Copy the bundle to `docs/operant/` in your repo, or install it with `npx skills add`.
2. Put the single-file edition, [dist/single-file.md](dist/single-file.md), into your rules location. The table of locations by tool is in [adaptations/other-ides.md](adaptations/other-ides.md); Codex CLI has its own guide in [adaptations/codex.md](adaptations/codex.md).
3. Verify with a fresh session, same question as above.

## Your own agent (API or SDK)

Minimum viable: put [dist/single-file.md](dist/single-file.md) in the system prompt, before task instructions. The proper build has three layers: the constitution in the prompt, the chapters retrieved on match, and the safety gates enforced in code. Read [adaptations/api-and-custom-agents.md](adaptations/api-and-custom-agents.md), and for an autonomous or scheduled agent read [adaptations/hermes-agent.md](adaptations/hermes-agent.md) first, because the enforcement layer is not optional there.

Pick an autonomy level ([references/autonomy-levels.md](references/autonomy-levels.md)) and implement the gates it requires before you turn the agent loose. Inventory your harness once with the seven questions in the API guide so you know which rules degrade and which never do.

## Did it work?

Run the smoke test from the [eval suite](evals/eval-suite.md): five high-signal scenarios plus the safety cluster, pass or fail each. If the agent leads with outcomes, stops asking permission for reversible work, names the command and output behind every "done", and refuses to delete a file that does not match its description or to send an unconfirmed email to a real list, it is on. The [runner spec](evals/runner-spec.md) turns this into an automated check; a certification run needs the gates wired into the sandbox, and the runner refuses to call a run certification without them.

## Where to go next

- Reading order for humans: [MANIFEST.md](MANIFEST.md), bottom.
- The fastest way to feel the discipline: [references/failure-modes.md](references/failure-modes.md).
- What this can and cannot do: [README.md](README.md), "What it will and won't do".
- How the pieces stay in sync as you edit them: [GOVERNANCE.md](GOVERNANCE.md).
