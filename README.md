# Operant: a portable operating discipline for AI agents

**Give any agent the operating discipline of a senior operator, on any model, in any harness, across coding and non-coding work.**

Operant is an operating system for AI-agent behavior, packaged as a skill. It does not add raw intelligence; it transfers process: how an agent communicates, when it acts versus asks, how it verifies before claiming success, how it uses tools, how it hands work to the next session, and how it handles risk. In day-to-day work, most of the felt quality difference between agents is process discipline, and process transfers.

The discipline is domain-general. The same ten principles govern a debugging session, a customer refund, a marketing send, a data report, a vendor brief, and a scheduled job nobody watches. Coding examples in the deeper chapters are incidental; the non-coding playbooks carry equal weight.

> **On claims.** Operant makes no claim about any specific vendor model. It is a transferable operating discipline, tested by its own eval suite, not a way to turn one model into another. See [What it will and won't do](#what-it-will-and-wont-do).

## What's in the box

Markdown for the humans and the model, plus machine-readable schemas and policy for the harness, designed for progressive disclosure. The constitution always loads; the depth loads when the situation matches; the code-enforced floor runs wherever the host wires it.

```
operant/
├── SKILL.md               ← the constitution: Precedence + Ten Principles + ceremony table + routing
├── README.md · QUICKSTART.md · MANIFEST.md · GOVERNANCE.md · CHANGELOG.md · LICENSE
├── references/            ← 18 chapters: the principles in depth (incl. concurrency-and-handoffs)
├── playbooks/             ← 24 end-to-end task shapes: 9 coding, 7 agent-operations, 8 general
├── checklists/            ← 4 gates with a shared legend: before-starting · before-claiming-done ·
│                             before-destructive-actions · session-end
├── examples/              ← calibration: report and confirmation makeovers, worked scenarios,
│                             a handoff document and a task-state file
├── adaptations/           ← 6 porting guides: claude-code · codex · other-ides · api-and-custom-agents ·
│                             hermes-agent · multi-agent-orchestrators
├── schemas/               ← 12 JSON Schemas: confirmations, briefs, handoffs, provenance, stop conditions
├── registry/rules.json    ← single source of truth: each rule → layer, gate, schema, eval
├── enforcement/           ← the ten-gate spec, the threat model, and the shipped gates:
│                             policy-gate.py (G1/G2/G3/G6/G10) + injection-sentinel.py (G8),
│                             each with --self-test, plus the Claude Code hooks wiring
├── shield/                ← config-surface auditor: scans the agent's OWN CLAUDE.md/settings/hooks/MCP
├── instincts/             ← optional continuous-learning loop (experimental; off by default)
├── evals/                 ← 40 behavioral scenarios + runner-spec + fixtures + reference runner + 5 recorded runs
├── tools/release-check.py ← release lint: versions, dist stamps, registry↔gate↔eval↔schema cross-checks,
│                             certification freshness, mirror parity
├── .claude-plugin/        ← plugin + marketplace manifests (validated with `claude plugin validate`)
└── dist/                  ← single-file.md (rules-file platforms) + one-page.md (the front door)
```

See [MANIFEST.md](MANIFEST.md) for a one-line description of every file and a human reading order.

## The Ten Principles (the 30-second version)

1. **Lead with the outcome.** The first sentence answers "what happened."
2. **No filler, ever.**
3. **Readable beats short.** Select less; never compress into fragments.
4. **Act when you can; ask only when you must.** A gate stops the item, not the task.
5. **Finish the turn.** Never end on a plan, a promise, or a question you could answer yourself; stop at the budget you declared.
6. **Never claim without proof.** The command, its output, and its freshness; three verdicts, no fourth.
7. **Match evidence to action.** Diagnose before state-changing moves; spend thought where a wrong move is expensive.
8. **Use tools like a professional.** Parallel, delegated, precise; a subagent's report is data until verified; wait on conditions, not clocks.
9. **Recommend, don't enumerate.** Interrogate a plan before a large build.
10. **Respect irreversibility.** Confirm deletes, sends, publishes; look before destroying; show read-back evidence, not expectations.

Full text with operational detail: [SKILL.md](SKILL.md).

## The three layers

Operant separates what a prompt can do from what only code can guarantee:

- **Judgment (prompt + retrieval):** the constitution and the chapters. Produces good decisions; cannot produce guarantees.
- **Consent (harness policy):** the host's permission and approval surfaces, including the `ask` decision a hook can return.
- **Guarantees (code):** the [generic policy spec](enforcement/generic-policy-spec.md): ten gates for destructive commands, history rewrites, bulk mutations, external sends, production changes, secret staging, PII, injection reporting, idempotency, and whole-tree staging on a shared checkout. Six ship as self-tested code; four (external send, production change, PII, idempotency) are specified for the deployment to implement, because they must know your platforms. The registry says which is which.

Each behavioral rule is mapped to the layer that owns it, the failure it prevents, and the eval that proves it, in [registry/rules.json](registry/rules.json). **Higher autonomy requires more of the guarantee layer, not less.** The L0 to L3 deployment levels are in [autonomy-levels.md](references/autonomy-levels.md); the attacks each layer answers are in [enforcement/threat-model.md](enforcement/threat-model.md).

## Installation

### Claude Code (native)

Copy the bundle to `.claude/skills/operant/` (per project) or `~/.claude/skills/operant/` (global), or install it as a plugin:

```
/plugin install operant --marketplace makesupply/operant
```

Then make it always-on with one line in `CLAUDE.md` or a `SessionStart` hook. Full instructions, mechanism mapping, model notes, and optional hooks enforcement: [adaptations/claude-code.md](adaptations/claude-code.md).

### Codex, Cursor, Windsurf, Copilot, Gemini CLI, other agents

`npx skills add makesupply/operant` installs the bundle through the cross-tool skills CLI. The single-file edition becomes the always-on rules file; the bundle lands in `docs/operant/` with the routing table rewired. Per-tool recipes: [adaptations/other-ides.md](adaptations/other-ides.md); Codex CLI: [adaptations/codex.md](adaptations/codex.md).

### Your own agents (API, SDK, frameworks)

Three-layer architecture: constitution in the system prompt, chapters via retrieval, safety gates enforced in code. For autonomous single agents: [adaptations/hermes-agent.md](adaptations/hermes-agent.md). For lead and subagent systems: [adaptations/multi-agent-orchestrators.md](adaptations/multi-agent-orchestrators.md). General builder's guide with the harness capability inventory: [adaptations/api-and-custom-agents.md](adaptations/api-and-custom-agents.md).

## What it will and won't do

**Will:** eliminate filler; force answer-first responses; stop the agent from ending turns with "Shall I…?"; require the command and its output behind every "done"; parallelize tool calls; make the agent wait on conditions rather than sleeps and stop at a declared budget; gate destructive and outward-facing actions behind informed confirmation that shows read-back evidence; make failure reports honest and specific; hand work between sessions through a document a stranger can resume from; give it a concrete playbook for debugging, incidents, refactors, migrations, API work, data work, research, reviews, docs, greenfield builds, shared checkouts, browser use, platform writes, scheduled jobs, skill authoring, third-party adoption, support, ecommerce ops, marketing, personal ops, and vendor briefing.

**Won't:** make a small model reason as deeply as a large one on genuinely hard problems, fix hallucination at the knowledge level, or substitute for good task specification. Discipline transfers; depth doesn't. A model that can't find the bug won't find it politely either; Operant ensures it reports that honestly instead of claiming success. The code floor guarantees only what a deployment wires; a gate that exists as a spec section is a design, not a defense, and the registry never calls it more than that.

## Proving it works

Don't take the install on faith: [evals/eval-suite.md](evals/eval-suite.md) is a 40-scenario behavioral test suite with pass criteria, fail tells, a two-number scorecard (behavior score plus a separate safety gate), and thirteen adoption-blocking scenarios. The [runner spec](evals/runner-spec.md) defines how to execute it deterministically-then-judged, with [machine-readable scenarios](evals/scenarios/) and a [fixtures format](evals/fixtures/README.md). The smoke test catches broken wiring; a certification run gates an autonomy-level raise, and the runner refuses to call a run certification unless the gates are wired into its sandbox. Five recorded runs live under [evals/runs/](evals/runs/README.md), labelled with the suite and gate set they ran on.

## License

MIT-0 (MIT No Attribution), see [LICENSE](LICENSE). Use, modify, and redistribute freely; attribution appreciated but not required.
