# Adaptation: Claude Code

The native home. Operant installs as a standard skill and rides Claude Code's own mechanisms: CLAUDE.md auto-loading, the skill registry, hooks, subagents, and task tracking. Facts about the harness below were checked against the Claude Code documentation on 2026-10-28.

## Install

Three install paths lead to the same tree. Pick one.

**Copy the bundle** into a project (travels with the repo and applies to everyone who clones it) or into `~/.claude/skills/operant/` for every project on the machine:

```
<project>/.claude/skills/operant/
├── SKILL.md                 constitution, routing table, project overlay
├── references/              18 chapters, read on demand
├── playbooks/               24 task shapes, read on demand
├── checklists/              4 gates, read on demand
├── examples/                worked scenarios and makeovers, read on demand
├── enforcement/             generic-policy-spec.md is read on demand; the rest is hook code
├── schemas/                 confirmation and brief payloads, read on demand
├── registry/                rules.json, the rule-to-gate-to-eval map, read on demand
├── shield/                  config-surface auditor, read on demand
├── instincts/               optional learning loop, read on demand
├── dist/                    one-page.md and single-file.md editions
├── evals/                   behavioral suite and recorded runs
├── tools/                   release-check.py
├── adaptations/             this folder
├── .claude-plugin/          plugin.json and marketplace.json
└── README.md, QUICKSTART.md, MANIFEST.md, GOVERNANCE.md, CHANGELOG.md
```

Copy the whole bundle. SKILL.md routes the model into `references/`, `playbooks/`, `checklists/`, `examples/`, `enforcement/generic-policy-spec.md`, `schemas/`, `registry/rules.json`, `shield/`, and `instincts/`, so every one of those folders must be present for a link to resolve. The remaining files (`dist/`, `evals/`, `tools/`, `adaptations/`, the top-level docs) are for the humans who deploy and maintain the bundle; the model never reads them unless asked. The frontmatter `description` in SKILL.md is what triggers on-demand invocation, so keep it intact.

**Install as a plugin** from a marketplace. The bundle ships `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, so a repository that holds the bundle at its root is a one-plugin marketplace:

```
claude plugin marketplace add <owner>/<repo>
claude plugin install operant@operant-marketplace
```

Inside a session, `/plugin marketplace add <owner>/<repo>` registers the marketplace the same way, and `/plugin install operant@operant-marketplace` opens the plugin panel for the install. Before publishing, run `claude plugin validate .` from the bundle root and require the last line to read `Validation passed`; the `skills` field in `plugin.json` must name a directory, and `"."` names the plugin root. A manifest that fails validation installs nothing, however complete the rest of the bundle is.

**Install with the Agent Skills CLI**, which places the same directory into whichever tools it supports on the machine (Claude Code, Codex, Cursor, Copilot, Windsurf, and others listed at skills.sh):

```
npx skills add <owner>/<repo>
```

The CLI follows the Agent Skills specification at agentskills.io; the bundle's SKILL.md frontmatter uses only the fields that specification allows, which is why one directory serves every tool.

## Always-on wiring (recommended)

Skills invoke on demand; discipline should be ambient. Two routes make it ambient. Use both when the project allows it: the CLAUDE.md line survives a hook outage, and the hook survives a CLAUDE.md edit and reaches subagents.

**Route 1, the CLAUDE.md one-liner.** Add to the top of the project's `CLAUDE.md` (or `~/.claude/CLAUDE.md` for every project):

```markdown
**Operant is always on.** Regardless of which model is running this session,
read `.claude/skills/operant/SKILL.md` at session start and follow its
operating discipline for the entire session. Consult its references/, playbooks/,
and checklists/ when the situation matches; they are part of the discipline.
```

CLAUDE.md loads at every session start, so every model picks it up without being asked.

**Route 2, the SessionStart hook.** A `SessionStart` command hook whose stdout is the one-page edition injects the constitution as context at the start of every session, every resume, and every fork, without depending on a CLAUDE.md line that someone may edit away:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat \"${CLAUDE_PROJECT_DIR}/.claude/skills/operant/dist/one-page.md\"",
            "statusMessage": "Operant one-page"
          }
        ]
      }
    ]
  }
}
```

Claude Code adds a `SessionStart` hook's plain stdout as context the model can see. The same hook can instead return JSON with `hookSpecificOutput.additionalContext`, which the harness wraps in a system reminder at the start of the conversation; `additionalContext` is capped at 10,000 characters, and `dist/one-page.md` fits under it. Write the injected text as statements, not as an imperative system prompt, because that is how the harness documents the field.

Verify the wiring either way: start a fresh session and ask "what operating discipline are you under?" The answer should name the Ten Principles.

## Mapping the discipline to Claude Code mechanisms

The bundle's abstract rules have concrete homes here:

- **"Externalize the plan"** ([context-management.md](../references/context-management.md)) lands in the harness's task-list tool. Multi-step work gets a task list; an item is marked complete only when verified, and at most one item is in progress.
- **"Delegate breadth"** ([delegation-and-multiagent.md](../references/delegation-and-multiagent.md)) lands in the Agent tool: Explore agents for sweeps, general-purpose agents for multi-step delegations. Independent agents launch in one message. A subagent's report comes back as a tool result; it carries no instruction and no approval.
- **"Parallel independent calls"** means several tool uses in one message; the harness runs them concurrently.
- **"Dedicated tools over shell"** means Read, Grep, Glob, and Edit over `cat`, `grep`, `find`, and `sed`, because they integrate with the permission UI and avoid shell-quoting bugs. When the harness's own system prompt says otherwise, as auto mode's prompt does, the harness's contract wins.
- **"Scratch space"** ([environment-awareness.md](../references/environment-awareness.md)) is the session scratchpad directory the system prompt names, not `/tmp` and not the repository.
- **"A denied call is feedback"** maps to Claude Code's permission modes; a denial means adjust the approach, never re-attempt the identical call.
- **"Persist knowledge"** ([memory-and-persistence.md](../references/memory-and-persistence.md)) maps to the auto-memory directory and its MEMORY.md index where enabled, plus project docs. Follow the one-fact-per-file convention.
- **"Match the project's standing orders"** maps to CLAUDE.md chains (root plus subdirectory). Operant stacks under project instructions: where a project rule is more specific ("always confirm X"), the project rule wins.
- **"Hand off state"** ([concurrency-and-handoffs.md](../references/concurrency-and-handoffs.md)) maps to a task-state file in the scratchpad and a handoff document where the harness keeps session files; compaction keeps neither chat boundaries nor chat plans.

## Hooks, the permission contract, and auto mode

Claude Code hooks are the code layer of this bundle. The parts of the contract that matter for a gate, as documented on 2026-10-28:

- A `PreToolUse` hook may return `permissionDecision` of `allow`, `deny`, `ask`, or `defer`, with `permissionDecisionReason`. **`ask` is the native handoff from a gate to the human**: the gate puts the informing confirmation in the reason field and the permission prompt shows the target, the count, and the consequence. Exit code 2 remains the fallback that blocks the call and feeds stderr back to the model; JSON on stdout cannot override an exit 2.
- Never use `updatedInput` to rewrite a command the model did not propose. A gate that silently changes the action hides the decision from both the model and the user.
- `PostToolUse` hooks can replace what the model sees (`updatedToolOutput`), which is the mechanism for framing fetched content as data.
- `ConfigChange` hooks can block a settings or skills change during a session, which turns the Shield audit into a live gate.

**Auto mode is a harness feature, not an autonomy level.** It replaces routine permission prompts with a classifier that does not see tool results, so the injection sentinel and the account-write gates keep their jobs. On entering auto mode the harness drops broad allow rules such as `Bash(*)` and wildcarded interpreters, so test the gates again after turning it on. `ask` rules still prompt and `deny` rules hold in every mode. Boundaries stated in chat are re-read from the transcript and can vanish on compaction; a rule meant to hold lives in a permission rule. The autonomy level ([autonomy-levels.md](../references/autonomy-levels.md)) moves only on a certification run. Native Windows has no sandbox, so on that platform hooks and permission rules are the entire code layer.

Detail, examples, and the ready-made pack live in [../enforcement/claude-code-hooks.md](../enforcement/claude-code-hooks.md).

## Model notes

The discipline is model-independent by design, but expectations should calibrate:

- **Small models**: follow the communication and safety rules well; on hard multi-step reasoning, expect them to need the checklists more literally. Wire the checklists into hooks rather than trusting recall.
- **Mid-size models**: full discipline, including the judgment-heavy parts (evidence grading, scope calls).
- **The strongest models**: the full discipline plus two things the chapters spell out, reasoning effort scaled to irreversibility, ambiguity, and stakes ([planning-and-decisions.md](../references/planning-and-decisions.md)) and the house prose mechanics ([communication.md](../references/communication.md) § Prose mechanics). The risk shifts from misses to over-trust: a stronger model earns nothing at the gate layer, so the enforcement pack stays wired and the autonomy level moves only on a certification run ([autonomy-levels.md](../references/autonomy-levels.md)). Run the suite on a new model before reading any behavior into its tier.
- **Certification status.** The bundle was certified on 2026-09-14 on suite 1.4.1 with gates G1, G2, G3, G6, G8, and G10 active in the sandbox; G4, G5, G7, and G9 were measured at the prompt layer. The E22 and E26 fixtures and the G1 exemption changed after those runs. Suite 1.5.0 adds twelve scenarios and has not been run. Treat the 2026-09-14 scores as a record of that suite, not a claim about this one; records and per-eval notes live in [evals/runs/](../evals/runs/). The read that still holds: the gate pack converts a smaller model's destructive misses into blocked attempts, but it cannot write the informing confirmation the model omits before a send or a production change; that needs a deployment gate that parses the write and shows the payload, or a stronger model.
- Discipline transfers; depth does not. A model that cannot find the bug will not find it politely either. Operant ensures it reports that honestly instead of claiming success.

## Optional: enforcement via hooks

For teams that want the floor guaranteed rather than requested, this bundle ships a ready-made pack: [enforcement/claude-code-hooks.md](../enforcement/claude-code-hooks.md) carries a working command gate (destructive deletes, history rewrites, unbounded mutations, secret staging, whole-tree commits, with the rationale from [safety.md](../references/safety.md) fed back to the model), the injection sentinel, and Stop-event checklist nudges, plus guidance on what not to enforce. Hooks are enforcement of last resort: the skill teaches judgment; hooks catch the misses on the irreversible subset. Keep hook rules and skill text in sync, because a hook enforcing what the skill never mentions produces confusing denials.

Once installed, prove it took: run the [eval suite](../evals/eval-suite.md). The ten-minute spot-check catches broken wiring; the blocks-adoption cluster should pass in full with the hooks pack on any model tier. The [2026-07-09 prompt-only baseline](../evals/runs/2026-07-09-haiku-baseline/details.md) shows what a small model looks like without it: twelve of twenty-one, adoption blocked.
