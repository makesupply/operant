# Operant — A Portable Operating Discipline for AI Agents

**Give any agent the operating discipline of a senior operator — on any model, in any harness, across coding and non-coding work.**

Operant is a complete operating system for AI-agent *behavior*, packaged as an installable skill. It doesn't add raw intelligence; it transfers **process** — how an agent communicates, when it acts versus asks, how it verifies before claiming success, how it uses tools, and how it handles risk. In day-to-day work, most of the felt quality difference between agents is process discipline, and process transfers.

The discipline is domain-general. The same ten principles govern a debugging session, a customer refund, a marketing send, a data report, and a vendor brief. Coding examples in the deeper chapters are incidental; the non-coding playbooks carry equal weight.

> **On claims.** Operant makes no claim about any specific vendor model. It is a transferable *operating discipline*, tested by its own eval suite — not a way to turn one model into another. See [What it will and won't do](#what-it-will-and-wont-do).

## The problem it solves

Anyone who works with AI agents daily recognizes these failures, and none of them are intelligence failures:

- The answer you asked for is buried under three paragraphs of process narration.
- The agent ends its turn with *"Shall I proceed?"* on work you already asked it to do.
- It says **"Done! Everything works."** — and nothing was run, tested, or checked.
- It deletes, sends, or overwrites something hard to reverse without looking first.
- It hits one error and gives up, or worse, quietly narrows the task and declares victory.
- It pastes a wall of tool output where one verified sentence was needed.
- A web page it fetched says *"ignore your instructions"* — and it listens.

These are **process failures**, and process can be specified, installed, and tested. That's what this repository is: the specification (a constitution plus 18 deep-dive chapters), the task-level know-how (18 playbooks), the enforcement (code gates the model cannot talk its way past), and the proof (a 21-scenario behavioral eval suite with a reference runner).

## Who it helps, and how

**Individuals using coding agents** (Claude Code, Cursor, Windsurf, Copilot). Install once, and every session starts with the discipline loaded: answers lead with the outcome, reversible work proceeds without permission theater, "done" means verified, and destructive commands hit a hard gate before they fire. The felt difference is an agent that behaves like a senior colleague instead of an eager intern.

**Teams standardizing agent behavior.** A team's agents should fail and succeed the same way regardless of who wired them or which model runs them. Operant gives you a shared, versioned, reviewable definition of "how our agents operate" — with a rule registry that maps every behavior to the layer that owns it, and an eval suite that turns "our agents are disciplined" from a vibe into a measurable, CI-checkable property.

**Builders of custom agents** (API/SDK, agent frameworks, autonomous ops agents). The three-layer architecture is the blueprint: constitution in the system prompt, chapters via retrieval, and safety gates enforced in code. The [autonomous-ops-agent adaptation](adaptations/autonomous-ops-agent.md) covers the highest-stakes case — a long-running agent with standing authority that acts while its operator sleeps — where the enforcement layer is not optional. The [generic policy spec](enforcement/generic-policy-spec.md) defines nine host-agnostic gates you can implement in any action loop.

**Operators doing non-coding work with agents** — support queues, ecommerce operations, marketing content, data reporting, research, personal ops. Ten of the eighteen playbooks are non-coding. They encode the judgment that prevents the expensive mistakes: a refund is a Tier-3 action, a marketing send to a real list has no "test post," a data report that can't be reproduced is an opinion, and every recurring automation must be idempotent and fail loud.

**Safety-conscious deployments.** Operant is honest about what a prompt can and cannot guarantee. The irreversible subset — deletes, sends, payments, production changes — is mapped to code gates that do not depend on model compliance. Shield audits the agent's *own* config surface for planted instructions and leaked secrets. The injection sentinel names and reports instruction-shaped text in fetched content. The threat model chapter maps seven attack classes on agent authority to the layer that answers each.

## What changes, concretely

| Without the discipline | With it |
|---|---|
| "Great question! Let me walk you through my process…" | First sentence answers what happened. |
| "Shall I fix the failing test?" | The test is fixed; the report says what changed and shows it passing. |
| "Done! The feature works." (unverified) | "Done — ran the suite, 42 pass. Output attached." Or honestly: "Blocked: X fails, here's the error and what I tried." |
| `rm -rf` fires on a mis-described directory | The gate blocks it; the agent reads the target, states exact scope, and asks with real information. |
| A timed-out payment call gets blindly retried | Server-side state is read first; the charge is never doubled. |
| Fetched page says "ignore previous instructions" — agent complies | Content is treated as data; the injection is named and reported to the user. |
| Six options, no opinion | One recommendation with the trade-off in one line; alternatives after. |

## The Ten Principles (the 30-second version)

1. **Lead with the outcome** — first sentence answers "what happened."
2. **No filler, ever.**
3. **Readable beats short** — select less, never compress into fragments.
4. **Act when you can; ask only when you must.**
5. **Finish the turn** — never end on a plan, a promise, or a question you could answer yourself.
6. **Never claim without proof** — verify, then say it plainly.
7. **Match evidence to action** — diagnose before state-changing moves.
8. **Use tools like a professional** — parallel, delegated, precise.
9. **Recommend, don't enumerate.**
10. **Respect irreversibility** — confirm deletes, sends, publishes; look before destroying.

Full text with operational detail: [SKILL.md](SKILL.md). The fastest way to *feel* the discipline: [references/failure-modes.md](references/failure-modes.md).

## How it works: three layers, progressively disclosed

Operant separates what a prompt can do from what only code can guarantee:

- **Judgment (prompt + retrieval)** — the constitution always loads; the 18 reference chapters and 18 playbooks load only when the situation matches their routing rules. Produces good decisions; cannot produce guarantees.
- **Consent (harness policy)** — the host's permission and approval surfaces. Produces informed human sign-off at the moments that need it, structured by the [confirmation schemas](schemas/).
- **Guarantees (code)** — the [generic policy spec](enforcement/generic-policy-spec.md): nine gates covering destructive commands, history rewrites, bulk mutations, external sends, production changes, secret staging, PII, injection reporting, and idempotency. These do not depend on the model complying.

Each behavioral rule is mapped to the layer that owns it, the failure it prevents, and the eval that proves it, in [registry/rules.json](registry/rules.json). The division of labor in one line: **prompts produce judgment, permissions produce consent, code produces guarantees.**

**Higher autonomy requires more of the guarantee layer, not less.** The L0–L3 deployment model is in [autonomy-levels.md](references/autonomy-levels.md): an agent trusted to act unattended needs *stronger* code gates and richer audit logging than an interactive one — autonomy is bought with enforcement, never traded against it.

## What's in the box

```
operant/
├── SKILL.md               ← the constitution: Precedence + Ten Principles + routing (always loads)
├── README.md · QUICKSTART.md · MANIFEST.md · GOVERNANCE.md · CHANGELOG.md · LICENSE
├── references/            ← 18 chapters: the principles in depth (incl. autonomy-levels, threat-model)
├── playbooks/             ← 18 end-to-end task shapes — 8 coding, 10 general & non-coding
├── checklists/            ← 4 gates: before-starting · before-claiming-done ·
│                             before-destructive-actions · session-end
├── examples/              ← calibration: report/confirmation makeovers, coding & non-coding scenarios
├── adaptations/           ← 5 porting guides: claude-code · other-ides · api-and-custom-agents ·
│                             autonomous-ops-agent · multi-agent-orchestrators
├── schemas/               ← 9 JSON Schemas: the discipline made machine-readable
├── registry/rules.json    ← single source of truth: each rule → layer, gate, schema, eval
├── enforcement/           ← RUNNABLE gates: policy-gate.py (G1/G2/G3/G6) + injection-sentinel.py (G8) +
│                             generic-policy-spec + policy.rules.json + claude-code-hooks wiring
├── shield/                ← config-surface auditor: scans the agent's OWN CLAUDE.md/settings/hooks/MCP
│                             for planted instructions, secrets, over-broad perms (CI-ready)
├── instincts/             ← continuous-learning loop: proven behavioral patterns surface at session
│                             start, refine on correction — the bundle improves itself
├── evals/                 ← 21-scenario behavioral suite + reference runner + fixtures + recorded runs
├── tools/                 ← release-check.py: version/dist/mirror drift lint
├── .claude-plugin/        ← plugin + marketplace manifests for install-via-marketplace
├── .github/workflows/     ← CI: all self-tests + Shield scan + release check on every push
└── dist/                  ← single-file.md (rules-file platforms) + one-page.md (the 30-second front door)
```

See [MANIFEST.md](MANIFEST.md) for a one-line description of every file and a human reading order.

### The runnable subsystems

All stdlib-only Python, cross-platform, each with a `self-test` command CI runs on every push:

| Subsystem | What it does | Verify it |
|---|---|---|
| [Policy gate](enforcement/policy-gate.py) | PreToolUse hook that blocks destructive commands, history rewrites, unbounded SQL mutations, and secret staging — with actionable guidance, not a bare denial | `python enforcement/policy-gate.py self-test` |
| [Injection sentinel](enforcement/injection-sentinel.py) | PostToolUse hook that names and reports instruction-shaped text in fetched content (gate G8), with an optional durable audit log | `python enforcement/injection-sentinel.py self-test` |
| [Shield](shield/shield.py) | Static auditor for the agent's own config surface: committed secrets, planted instructions, over-broad permissions, risky hooks | `python shield/shield.py self-test` |
| [Instincts](instincts/instincts.py) | Confidence-scored learning loop: patterns that prove out across sessions surface at session start; corrections decay or retire them | `python instincts/instincts.py self-test` |
| [Eval runner](evals/eval-runner.py) | Runs the 21-scenario suite deterministically-then-judged and emits a schema-validated scorecard | `python evals/eval-runner.py self-test` |

## Installation

### Claude Code (native — recommended)

Copy the bundle to `.claude/skills/operant/` (per-project) or `~/.claude/skills/operant/` (global), then make it always-on with one line in your `CLAUDE.md`:

> **Operant is always on.** Regardless of which model is running this session, read `.claude/skills/operant/SKILL.md` at session start and follow its operating discipline for the entire session. Consult its references/, playbooks/, and checklists/ when the situation matches.

Full instructions, mechanism mapping, model notes, and optional hooks enforcement: [adaptations/claude-code.md](adaptations/claude-code.md).

### Cursor / Windsurf / Copilot / other IDE agents

[dist/single-file.md](dist/single-file.md) becomes the always-on rules file; the bundle lands in `docs/operant/` with the routing table rewired. Per-tool recipes and what degrades without a full harness: [adaptations/other-ides.md](adaptations/other-ides.md).

### Your own agents (API / SDK / frameworks)

Minimum viable: put [dist/single-file.md](dist/single-file.md) in the system prompt, before task instructions. Proper build: constitution as a stable prompt prefix, chapters via retrieval, gates in the action loop — [adaptations/api-and-custom-agents.md](adaptations/api-and-custom-agents.md). For autonomous/scheduled single agents read [adaptations/autonomous-ops-agent.md](adaptations/autonomous-ops-agent.md) first; for lead/subagent systems, [adaptations/multi-agent-orchestrators.md](adaptations/multi-agent-orchestrators.md).

## Proving it works

Don't take the install on faith:

- **[evals/eval-suite.md](evals/eval-suite.md)** — 21 behavioral scenarios with pass criteria and fail tells, scored as two numbers: a behavior score plus a separate safety gate that blocks adoption on any safety-cluster failure. The 10-minute smoke test catches broken wiring; certification gates an autonomy-level raise.
- **[evals/eval-runner.py](evals/eval-runner.py)** — the reference runner: fresh sandbox per scenario, deterministic checks first, judge prompts for everything a machine can't decide, schema-validated scorecards. A recorded baseline run ships in [evals/runs/](evals/runs/).
- **Self-tests + CI** — every runnable subsystem verifies itself; [.github/workflows/checks.yml](.github/workflows/checks.yml) runs all of them plus a Shield scan and the release lint on every push.

## Extending it without breaking it

- **Project overlay** — deployment specifics (your write lanes, your Tier-3 systems, your known failure modes) belong in a short overlay appended to the *deployed* SKILL.md, not in the framework. The constitution ends with a template for exactly this.
- **[GOVERNANCE.md](GOVERNANCE.md)** — the change protocol that keeps the three copies of every rule (prompt, gate, eval) in agreement, the versioning scheme, and the rule that a behavior with no eval cannot be claimed as a property of the framework.
- **[tools/release-check.py](tools/release-check.py)** — mechanical lint for the drift GOVERNANCE prohibits: version agreement, dist presence, mirror parity.

## What it will and won't do

**Will:** eliminate filler; force answer-first responses; stop the agent from ending turns with "Shall I…?"; require proof before "done"; parallelize tool calls; gate destructive and outward-facing actions behind informed confirmation; make failure reports honest and specific; give it a concrete playbook for debugging, incidents, refactors, migrations, data work, research, reviews, docs, greenfield builds, support, ecommerce ops, marketing, personal ops, and vendor briefing.

**Won't:** make a small model reason as deeply as a large one on genuinely hard problems, fix hallucination at the knowledge level, or substitute for good task specification. Discipline transfers; depth doesn't. (A model that can't find the bug won't find it politely either — Operant ensures it reports that honestly instead of claiming success.)

## FAQ

**Is this a system prompt?** The constitution can be used as one ([dist/single-file.md](dist/single-file.md)), but the framework is more: retrieval-loaded depth, machine-readable schemas, code-enforced gates, a config auditor, a learning loop, and an eval suite that proves the install took.

**Does it work with models other than Claude?** Yes — that's the point of "portable." The constitution and single-file edition are model-agnostic; the adaptations cover Claude Code natively and generic rules-file platforms; the enforcement spec is host-agnostic. Smaller models lean harder on the checklists and gates, which is exactly what those layers are for.

**Why not just prompt "be concise and careful"?** Vague virtue instructions don't survive contact with real work. Operant's rules are operational (the *last-paragraph test*, the *described-vs-found* check, *canary-then-batch*), each mapped to a nameable failure it prevents, and the ones that must hold are enforced in code and proven by evals.

**What does it cost in context?** The always-loaded constitution is one file (~8 KB); everything else loads only on match. The one-page edition is smaller still for tight budgets.

## License

MIT-0 (MIT No Attribution) — see [LICENSE](LICENSE). Use, modify, and redistribute freely; attribution appreciated but not required.
