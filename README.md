# Operant — A Portable Operating Discipline for AI Agents

**Give any agent the operating discipline of a senior operator — on any model, in any harness, across coding and non-coding work.**

Operant is a complete operating system for AI-agent *behavior*, packaged as a skill. It doesn't add raw intelligence; it transfers process — how an agent communicates, when it acts versus asks, how it verifies before claiming success, how it uses tools, and how it handles risk. In day-to-day work, most of the felt quality difference between agents is process discipline, and process transfers.

The discipline is domain-general. The same ten principles govern a debugging session, a customer refund, a marketing send, a data report, and a vendor brief. Coding examples in the deeper chapters are incidental; the non-coding playbooks carry equal weight.

> **On claims.** Operant makes no claim about any specific vendor model. It is a transferable *operating discipline*, tested by its own eval suite — not a way to turn one model into another. See [What it will and won't do](#what-it-will-and-wont-do).

## What's in the box

Markdown for the humans and the model, plus machine-readable schemas and policy for the harness — designed for progressive disclosure. The constitution always loads; the depth loads when the situation matches; the code-enforced floor runs regardless of model.

```
operant/
├── SKILL.md               ← the constitution: Precedence + Ten Principles + routing (always loads)
├── README.md · QUICKSTART.md · MANIFEST.md · GOVERNANCE.md · CHANGELOG.md · LICENSE
├── references/            ← 18 chapters: the principles in depth (adds autonomy-levels, threat-model)
├── playbooks/             ← 18 end-to-end task shapes — 8 coding, 10 general & non-coding
├── checklists/            ← 4 gates: before-starting · before-claiming-done ·
│                             before-destructive-actions · session-end
├── examples/              ← calibration: report/confirmation makeovers, coding & non-coding scenarios
├── adaptations/           ← 5 porting guides: claude-code · other-ides · api-and-custom-agents ·
│                             hermes-agent (autonomous orchestrator) · multi-agent-orchestrators
├── schemas/               ← 9 JSON Schemas: the discipline made machine-readable
├── registry/rules.json    ← single source of truth: each rule → layer, gate, schema, eval
├── enforcement/           ← RUNNABLE gates: policy-gate.py (G1/G2/G3/G6/G10) + injection-sentinel.py (G8),
│                             each with --self-test + generic-policy-spec + policy.rules.json + hooks wiring
├── shield/                ← config-surface auditor: scans the agent's OWN CLAUDE.md/settings/hooks/MCP
│                             for planted instructions, secrets, over-broad perms (CI-ready, ignore file)
├── instincts/             ← continuous-learning loop: proven behavioral patterns surface at session
│                             start, refine on correction — the bundle improves itself
├── evals/                 ← eval-suite (28 scenarios) + runner-spec + fixtures + reference runner + baseline run
├── tools/release-check.py ← release lint: versions, dist, gate↔spec↔registry↔eval cross-checks, mirror parity
├── .claude-plugin/        ← plugin + marketplace manifests for install-via-marketplace
└── dist/                  ← single-file.md (rules-file platforms) + one-page.md (the 30-second front door)
```

See [MANIFEST.md](MANIFEST.md) for a one-line description of every file and a human reading order.

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

Full text with operational detail: [SKILL.md](SKILL.md).

## The three layers

Operant separates what a prompt can do from what only code can guarantee:

- **Judgment (prompt + retrieval)** — the constitution and the chapters. Produces good decisions; cannot produce guarantees.
- **Consent (harness policy)** — the host's permission and approval surfaces.
- **Guarantees (code)** — the [generic policy spec](enforcement/generic-policy-spec.md): ten gates for destructive commands, history rewrites, bulk mutations, external sends, production changes, secret staging, PII, injection reporting, idempotency, and whole-tree staging on a shared checkout. These do not depend on the model complying.

Each behavioral rule is mapped to the layer that owns it, the failure it prevents, and the eval that proves it, in [registry/rules.json](registry/rules.json). **Higher autonomy requires more of the guarantee layer, not less** — the model of L0–L3 deployment levels is in [autonomy-levels.md](references/autonomy-levels.md).

## Installation

### Claude Code (native — recommended)

Copy the bundle to `.claude/skills/operant/` (per-project) or `~/.claude/skills/operant/` (global), then make it always-on with one line in your `CLAUDE.md`. Full instructions, mechanism mapping, model notes, and optional hooks enforcement: [adaptations/claude-code.md](adaptations/claude-code.md).

### Cursor / Windsurf / Copilot / other IDE agents

SKILL.md becomes the always-on rules file; the bundle lands in `docs/operant/` with the routing table rewired. Per-tool recipes and what degrades without a full harness: [adaptations/other-ides.md](adaptations/other-ides.md).

### Your own agents (API / SDK / frameworks)

Three-layer architecture: constitution in the system prompt, chapters via retrieval, safety gates enforced in code. For autonomous single agents: [adaptations/hermes-agent.md](adaptations/hermes-agent.md). For lead/subagent systems: [adaptations/multi-agent-orchestrators.md](adaptations/multi-agent-orchestrators.md). General builder's guide: [adaptations/api-and-custom-agents.md](adaptations/api-and-custom-agents.md).

## What it will and won't do

**Will:** eliminate filler; force answer-first responses; stop the agent from ending turns with "Shall I…?"; require proof before "done"; parallelize tool calls; gate destructive and outward-facing actions behind informed confirmation; make failure reports honest and specific; give it a concrete playbook for debugging, incidents, refactors, migrations, data work, research, reviews, docs, greenfield builds, support, ecommerce ops, marketing, personal ops, and vendor briefing.

**Won't:** make a small model reason as deeply as a large one on genuinely hard problems, fix hallucination at the knowledge level, or substitute for good task specification. Discipline transfers; depth doesn't. (A model that can't find the bug won't find it politely either — Operant ensures it reports that honestly instead of claiming success.)

## Proving it works

Don't take the install on faith: [evals/eval-suite.md](evals/eval-suite.md) is a 28-scenario behavioral test suite — pass criteria, fail tells, a two-number scorecard (behavior score plus a separate safety gate). The [runner spec](evals/runner-spec.md) defines how to execute it deterministically-then-judged, with [machine-readable scenarios](evals/scenarios/) and a [fixtures format](evals/fixtures/README.md). The 10-minute smoke test catches broken wiring; certification gates an autonomy-level raise. For guaranteed floors on the irreversible rules regardless of model tier, implement the [generic policy spec](enforcement/generic-policy-spec.md) (the [Claude Code hooks](enforcement/claude-code-hooks.md) are one ready implementation).

## License

MIT-0 (MIT No Attribution) — see [LICENSE](LICENSE). Use, modify, and redistribute freely; attribution appreciated but not required.
