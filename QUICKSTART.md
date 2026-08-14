# Operant — Quickstart

Five minutes from download to a disciplined agent. Pick your platform:

## Claude Code (2 minutes)

```bash
# 1. Copy the bundle into your project's skills directory
cp -r operant <your-project>/.claude/skills/operant
#    (or ~/.claude/skills/operant for all projects)

# 2. Make it always-on: add to the top of <your-project>/CLAUDE.md:
```

> **Operant is always on.** Regardless of which model is running this session, read `.claude/skills/operant/SKILL.md` at session start and follow its operating discipline for the entire session. Consult its references/, playbooks/, and checklists/ when the situation matches.

```bash
# 3. Verify: start a NEW session and ask
#    "what operating discipline are you under?"
#    → the answer should name the Ten Principles.
```

Optional hardening: implement the [generic policy spec](enforcement/generic-policy-spec.md); the [Claude Code hooks pack](enforcement/claude-code-hooks.md) is a ready implementation that blocks `rm -rf`-class commands at the harness level. Details and model notes: [adaptations/claude-code.md](adaptations/claude-code.md).

## Cursor / Windsurf / Copilot (5 minutes)

1. Copy the bundle to `docs/operant/` in your repo.
2. Put the **single-file edition** — [dist/single-file.md](dist/single-file.md) — into your rules location:
   - Cursor: `.cursor/rules/operant.mdc` with `alwaysApply: true` frontmatter
   - Windsurf: `.windsurf/rules/operant.md`
   - Copilot: `.github/copilot-instructions.md`
3. Verify with a fresh session, same question as above.

Full recipes, size-limit workarounds, and what degrades on each platform: [adaptations/other-ides.md](adaptations/other-ides.md).

## Your own agent (API / SDK)

Minimum viable: put [dist/single-file.md](dist/single-file.md) in your system prompt, before task instructions. Proper build (three-layer architecture, code-enforced safety gates, chapter retrieval): [adaptations/api-and-custom-agents.md](adaptations/api-and-custom-agents.md). For an autonomous/scheduled agent, read [adaptations/autonomous-ops-agent.md](adaptations/autonomous-ops-agent.md) first — the enforcement layer is not optional there.

Pick an autonomy level ([references/autonomy-levels.md](references/autonomy-levels.md)) and implement the gates it requires ([enforcement/generic-policy-spec.md](enforcement/generic-policy-spec.md)) before you turn it loose.

## Did it work?

Run the 10-minute smoke test from the [eval suite](evals/eval-suite.md): five high-signal scenarios plus the safety cluster, pass/fail each. If the agent leads with outcomes, stops asking permission for reversible work, and refuses to delete a file that doesn't match its description or send an unconfirmed email to a real list — it's on. The [runner spec](evals/runner-spec.md) turns this into an automated check.

## Where to go next

- Reading order for humans: [MANIFEST.md](MANIFEST.md) (bottom).
- The fastest way to *feel* the discipline: [references/failure-modes.md](references/failure-modes.md).
- What this can and can't do: [README.md](README.md) § What it will and won't do.
- How the pieces stay in sync as you edit them: [GOVERNANCE.md](GOVERNANCE.md).
