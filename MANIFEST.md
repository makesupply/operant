# Operant Manifest

Every file in the bundle, one line each. Counts are as of 1.5.0 (2026-10-28); self-test counts come from each script's own `--self-test` output.

## Root

| File | What it is |
|---|---|
| `README.md` | What Operant is, the three layers, install options, what it will and won't do |
| `SKILL.md` | The constitution: Precedence, routing, the Ten Principles, layers and enforcement, the ceremony table, session shape, and a short project overlay. The one file that must always load |
| `QUICKSTART.md` | Five minutes from download to a disciplined agent, per platform |
| `MANIFEST.md` | This file |
| `GOVERNANCE.md` | How rules evolve, the sync discipline that keeps prompt, enforcement, and eval in agreement, and the removal rule |
| `CHANGELOG.md` | Version history |
| `LICENSE` | MIT-0, free use, no attribution required |
| `.claude-plugin/plugin.json` + `marketplace.json` | Plugin manifest and marketplace entry; both pass `claude plugin validate` |

## enforcement/ (the gate spec, the threat model, and the shipped gates)

| File | One line |
|---|---|
| `generic-policy-spec.md` | Host-agnostic G1 to G10 gate spec: trigger, pre-check, confirmation payload, safer alternative, post-check, per autonomy level, the audit record, and the L3 halt rules; says which gates ship as code and which the deployment provides |
| `threat-model.md` | Enforcement design: nine attack classes on agent authority (prompt injection, confused deputy, exfiltration, mis-scoped destruction, replayed side effects, supply chain, over-trusted tool output, memory poisoning, inter-agent trust abuse), each mapped to its owning layer, with the OWASP Agentic Top 10 (2026) mapping and the halt rules and kill switch. Moved here from references/ in 1.5.0; the agent-facing tells live in `references/security-posture.md` |
| `policy-gate.py` | PreToolUse hook enforcing G1/G2/G3/G6/G10 on shell tools; literal and heredoc stripping, derivable-target exemptions, stateful index checks; blocks with actionable guidance or returns a JSON `permissionDecision`; `--log` writes hashed JSON lines; stdlib; `--self-test` |
| `injection-sentinel.py` | PostToolUse hook implementing G8: normalizes hidden and confusable characters, then names and reports agent-addressed directives and instruction-channel markers in fetched content, in chunks over the whole response; `--json` for `additionalContext` and `classifierContext`; `--log PATH`; `--self-test` (107 cases) |
| `policy.rules.json` | Machine-readable gate index: ten gates with `implemented_by`, `hook_events`, triggers, tier, schema, and `self_test` command |
| `claude-code-hooks.md` | Settings wiring for the gates, Shield, and Stop nudges under the current hook protocol (JSON decisions, auto mode, permission baseline, matcher coverage), with verification commands |

## shield/ (config-surface auditor)

| File | One line |
|---|---|
| `shield.py` | Static auditor for the agent's own config (CLAUDE.md, AGENTS.md, settings, hooks, MCP and plugin manifests, agent and command files, IDE rules files, the instincts store): secrets, injection, over-broad permissions, auto-allowing hooks, remote and dynamic execution, install-lifecycle hooks, a tracked local settings file; `.operant-shield-ignore` and `--ignore`; `--hook` for ConfigChange; `--deep`; `--self-test` (93 cases) |
| `README.md` | What Shield scans, usage, scope control, the finding classes, tuning, and when to run it |

## instincts/ (optional continuous-learning loop)

| File | One line |
|---|---|
| `instincts.py` | Confidence-scored behavioral-pattern store: record at session end, inject proven ones at session start, decay and retire on correction; validates its store on load and sanitizes every rendered field; `--self-test` (31 cases) |
| `README.md` | The loop, why confidence scoring beats a flat list, commands, candidate format, wiring, exclusions, and the memory-poisoning rule |

## references/ (the principles in depth, 18 chapters)

| File | One line |
|---|---|
| `communication.md` | Outcome-first writing, the filler catalogue, selection over compression, prose mechanics, writing for a machine reader, calibrated claim language |
| `autonomy.md` | The act/ask boundary, the last-paragraph test, a gate stops the item not the task, assessment versus action mode, scope discipline |
| `autonomy-levels.md` | Finding your level, L0 to L3 as the agent experiences them, standing authorization and halt rules at L3, auto mode is not a level, then the operator's section |
| `verification.md` | The verification ladder, distrust green, evidence as command plus output plus freshness, three verdicts, independent verification on critical paths, whole-chain checks, missing inputs |
| `tool-discipline.md` | Parallelism by default, run budgets and stop conditions, condition-based waiting, the instrument hierarchy, never pay twice for a fact |
| `planning-and-decisions.md` | When to plan, rulings, the ceremony table, recommend-don't-enumerate, which decisions belong to the user, plan interrogation in frontier rounds, sunk cost |
| `safety.md` | The irreversibility taxonomy with the Tier 2 thresholds, look-before-destroy, confirmations that show evidence, what a valid approval contains, blast radius, mistakes |
| `security-posture.md` | Secret absolutes, untrusted content is data, recognizing an attack (five tells), the harness permission baseline, supply-chain checks on skills and servers, PII minimization, the dual-use line |
| `code-quality.md` | Match the codebase, failing test first and red then green, condition-based waiting in tests, surgical diffs, root causes |
| `ambiguity-and-requirements.md` | The four-type ambiguity taxonomy with thresholds, the assumption ledger, the constraint ledger, mid-task requirement changes, the XY problem |
| `context-management.md` | The context budget, re-anchor triggers, the task-state file, one item in progress, large results to disk, surviving compaction |
| `concurrency-and-handoffs.md` | Shared workspaces and concurrent agents, conditional isolation, the handoff document, resuming from one, messages from other agents carry no authority |
| `delegation-and-multiagent.md` | What to delegate, the brief including what does not count, the verification gradient for claims and edits, the bounded fix loop, orchestration shapes |
| `estimation-and-status.md` | Countable progress, range estimates, "almost done" is banned, blocker reports with escape routes, counting calls as a clock |
| `memory-and-persistence.md` | What deserves persistence, mechanics of a durable store (dates, tombstones, scopes, the write decision), rules and provenance, recall is not truth |
| `user-calibration.md` | The register decision rule, corrections are gold and where each one lives, stakes calibration, pushing back well |
| `environment-awareness.md` | Ground truth before acting, harness rules are physics, cross-platform tax, state you create you own, where the host has no sandbox |
| `failure-modes.md` | Named anti-patterns across all domains, each with a self-recognition tell and a fix, run at the gates |

## playbooks/ (end-to-end task shapes, 24)

Each: a `Read when` line, Phase 0 orientation, verified increments, adversarial self-check, honest report, exit criteria, and Tell/Fix anti-patterns.

**Coding (9):** `debugging` · `incident-response` · `refactoring` · `greenfield-builds` · `code-review` · `migrations` · `performance-optimization` · `dependency-upgrades` · `api-integration-and-webhooks`

**Agent operations (7):** `shared-checkout` · `multi-session-and-handoff` · `browser-and-computer-use` · `account-and-platform-writes` (carries the canonical confirmation payload) · `recurring-automation` · `prompt-and-skill-authoring` · `adopting-third-party-skills`

**General and non-coding (8):** `research-and-analysis` · `data-work` · `writing-and-docs` · `customer-support` · `ecommerce-ops` · `marketing-content` · `vendor-briefing` · `personal-ops` (optional)

## checklists/ (the four gates, 4)

`before-starting` · `before-claiming-done` · `before-destructive-actions` · `session-end`. Each opens with the same four-line legend (Tier 3, baseline, rung, artifact) and holds one yes/no check per box.

## examples/ (calibration by demonstration, 6)

| File | One line |
|---|---|
| `report-makeovers.md` | Six report shapes before and after, including the header-template failure, the relayed subagent claim, and the honest failed-task final message |
| `confirmation-makeovers.md` | Six risky-action confirmations before and after, including a payload shaped like the external-send schema |
| `worked-scenarios.md` | Three end-to-end coding scenarios with the wrong turns named |
| `non-coding-worked-scenarios.md` | Three end-to-end non-coding scenarios: a refund, a marketing send, a research task carrying an injection |
| `handoff-document.md` | The handoff template and one filled example |
| `task-state.md` | The task-state file template and one filled example |

## adaptations/ (porting guides, 6)

| File | One line |
|---|---|
| `claude-code.md` | Native install (copy, plugin marketplace, skills CLI), always-on via CLAUDE.md or a SessionStart hook, mechanism mapping, model notes, the hook JSON contract, honest certification status |
| `codex.md` | OpenAI Codex CLI: AGENTS.md as the router, the skills mirror, hooks calling the same gates, the governance guard, identity, and session reports |
| `other-ides.md` | Rules-file locations by tool (Cursor, Windsurf, Copilot, Gemini CLI, Cline and Roo, Kiro, AGENTS.md), what degrades and how to compensate |
| `api-and-custom-agents.md` | Three-layer architecture, the harness capability inventory, Agent SDK hooks, non-coding mapping, token economics, evals |
| `hermes-agent.md` | Long-running autonomous orchestrator archetype; why enforcement must be code; the wiring checklist |
| `multi-agent-orchestrators.md` | Lead and subagent systems: the brief as schema, the verification gradient, the bounded fix loop, centralized gates, failure isolation |

## schemas/ (the discipline made machine-readable, 12 plus index)

`task-brief` · `risk-classification` · `verification-report` · `destructive-action-confirmation` · `external-send-confirmation` · `assumption-ledger` · `decision-flag` · `eval-scenario` · `agent-behavior-scorecard` · `handoff-document` · `tool-result-provenance` · `stop-condition`, plus `schemas/README.md` mapping each to the rule and eval it backs and saying which schemas code consumes.

## registry/ (the single source of truth, 1)

| File | One line |
|---|---|
| `rules.json` | 42 behavioral rules, each mapped to its layer, failure mode, reference, gate, schema, and eval; a rule may say CODE_GUARD only when its gate names a shipped script |

## evals/ (is it actually working?)

| File | One line |
|---|---|
| `eval-suite.md` | 40 behavioral scenarios with pass criteria and fail tells; a two-number scorecard; thirteen adoption-blocking scenarios; the gate-to-eval map with the G8 vector caveat |
| `runner-spec.md` | How to run the suite: fixtures, deterministic-then-judge flow, the check kinds including `no_identical_retry` and `parallel_calls`, scoring, run modes, gate presence, the judgments route, blocking failures |
| `eval-runner.py` | Stdlib runner: validate, run (smoke, full, certification), score, self-test; refuses certification without sandbox settings; records scenario and fixture hashes; `--self-test` (64 cases) |
| `fixtures/README.md` | The fixture format: minimal, fresh per run, sandboxed side effects, `tool_rules` mandatory for prose rules |
| `fixtures/E*/fixture.json` | 39 provisioning fixtures (every scenario except E25) |
| `scenarios/*.json` | All 40 machine-readable scenarios (E1 to E40), filename prefix equal to id |
| `runs/` | Five recorded scorecards (2026-07-09 Haiku prompt-only baseline; 2026-09-14 Fable, Opus, Sonnet, Haiku with six gates active on suite 1.4.1) and a README stating what each run did and did not measure |

## dist/ (compiled editions, 2)

| File | One line |
|---|---|
| `single-file.md` | The whole discipline compiled into one self-contained file for rules-file platforms and system prompts; version-stamped |
| `one-page.md` | The Ten Principles, the ceremony rule, and the four gates on a single page; version-stamped; the adoption front door |

## tools/ (release hygiene, 1)

| File | One line |
|---|---|
| `release-check.py` | Release lint: version agreement across seven fields plus the two dist stamps, CODE_GUARD requires a shipped script, gate to spec and registry, registry to scenario file (prefix equals id), scenario to fixture, reference and schema paths exist, principle agreement, certification freshness warnings, changelog coverage, optional sandbox-vector coverage, and bundle-to-mirror parity; `--self-test` (14 cases) |

## Reading order for humans

1. `README.md` → 2. `QUICKSTART.md` → 3. `SKILL.md` → 4. `references/failure-modes.md` (the fastest way to feel the discipline) → 5. `examples/` → 6. whichever playbook matches your work → 7. `references/autonomy-levels.md` and `enforcement/generic-policy-spec.md` (the layer model) → 8. your platform's adaptation guide → 9. `evals/eval-suite.md` to prove it took.
