# Adaptation: Claude Code

The native home. Operant installs as a standard skill and rides Claude Code's own mechanisms — CLAUDE.md auto-loading, the skill registry, subagents, and task tracking.

## Install

**Per-project** (travels with the repo, applies to everyone who clones it):
```
<project>/.claude/skills/operant/
├── SKILL.md
├── references/
├── playbooks/
├── checklists/
└── examples/
```

**Global** (all your projects): same layout under `~/.claude/skills/operant/`.

Copy the whole bundle — simplest and safe. The model only routes into `SKILL.md`, `references/`, `playbooks/`, `checklists/`, and `examples/`; the human-facing files (`README.md`, `MANIFEST.md`, `QUICKSTART.md`, `adaptations/`, `evals/`, `enforcement/`, `dist/`) are inert noise to it and useful to you. `SKILL.md`'s frontmatter `description` is what triggers on-demand invocation — keep it intact.

## Always-on wiring (recommended)

Skills invoke on demand; discipline should be ambient. Add to the top of the project's `CLAUDE.md` (or `~/.claude/CLAUDE.md` for everywhere):

```markdown
**Operant is always on.** Regardless of which model is running this session,
read `.claude/skills/operant/SKILL.md` at session start and follow its
operating discipline for the entire session. Consult its references/, playbooks/,
and checklists/ when the situation matches — they are part of the discipline.
```

CLAUDE.md auto-loads every session start, so every model — Haiku through Opus — picks it up without being asked. Verify the wiring: start a fresh session and ask "what operating discipline are you under?" — the answer should name the Ten Principles.

## Mapping the discipline to Claude Code mechanisms

The bundle's abstract rules have concrete homes here:

- **"Externalize the plan"** ([context-management.md](../references/context-management.md)) → the TodoWrite/task tools. Multi-step work gets a task list; items marked complete only when verified.
- **"Delegate breadth"** ([delegation-and-multiagent.md](../references/delegation-and-multiagent.md)) → the Agent tool (Explore agents for sweeps, general-purpose for multi-step delegations). Independent agents launch in one message.
- **"Parallel independent calls"** → multiple tool uses per message — the harness executes them concurrently.
- **"Dedicated tools over shell"** → Read/Grep/Glob/Edit over `cat`/`grep`/`find`/`sed`; they integrate with the permission UI and avoid shell-quoting bugs.
- **"Scratch space"** ([environment-awareness.md](../references/environment-awareness.md)) → the session scratchpad directory the system prompt names — not `/tmp`, not the repo.
- **"A denied call is feedback"** → Claude Code's permission modes; a denial means adjust the approach, never re-attempt verbatim.
- **"Persist knowledge"** ([memory-and-persistence.md](../references/memory-and-persistence.md)) → the auto-memory directory and MEMORY.md index where enabled, plus project docs. Follow the one-fact-per-file convention.
- **"Match the project's standing orders"** → CLAUDE.md chains (root + subdirectory). Operant *stacks under* project instructions: where a project rule is more specific (e.g., "always confirm X"), the project rule wins.

## Model notes

The discipline is model-independent by design, but expectations should calibrate:

- **Haiku-class**: follows the communication and safety rules well; on hard multi-step reasoning, expect it to need the checklists more literally. Consider wiring the checklists into hooks (below) rather than trusting recall.
- **Sonnet/Opus-class**: full discipline, including the judgment-heavy parts (evidence grading, scope calls).
- Discipline transfers; depth doesn't. A model that can't find the bug won't find it politely either — Operant ensures it *reports that honestly* instead of claiming success.

## Optional: enforcement via hooks

For teams that want the floor guaranteed rather than requested, this bundle ships a ready-made pack: [enforcement/claude-code-hooks.md](../enforcement/claude-code-hooks.md) — a working Tier-3 command gate (blocks `rm -rf`/force-push/destructive-SQL patterns with the safety.md rationale fed back to the model), a secret-commit tripwire, and Stop-event checklist nudges, plus guidance on what *not* to enforce. Hooks are enforcement of last resort: the skill teaches judgment; hooks catch the misses on the irreversible subset. Keep hook rules and skill text in sync — a hook enforcing what the skill doesn't mention produces confusing denials.

And once installed, prove it took: run the [eval suite](../evals/eval-suite.md) — the 10-minute spot-check catches a broken wiring; the safety cluster (E12–E14) should go 3/3 with the hooks pack on any model tier.
