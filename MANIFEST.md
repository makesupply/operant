# Operant — Manifest

Every file in the bundle, one line each.

## Root

| File | What it is |
|---|---|
| `README.md` | What Operant is, the three layers, install options, what it will/won't do |
| `SKILL.md` | The constitution: Precedence + Ten Principles + layers/autonomy/enforcement + routing. The one file that must always load |
| `QUICKSTART.md` | Five minutes from download to a disciplined agent, per platform |
| `MANIFEST.md` | This file |
| `GOVERNANCE.md` | How rules evolve, and the sync discipline that keeps prompt/enforcement/eval in agreement |
| `CHANGELOG.md` | Version history |
| `LICENSE` | MIT-0 — free use, no attribution required |
| `.claude-plugin/plugin.json` + `marketplace.json` | Agent Skills plugin manifest + marketplace entry for install-via-marketplace |

## enforcement/ — code-enforced gates (runnable)

| File | One line |
|---|---|
| `generic-policy-spec.md` | Host-agnostic G1–G9 gate spec: trigger, pre-check, confirmation payload, safer alternative, post-check, per-autonomy-level |
| `policy-gate.py` | PreToolUse hook enforcing G1/G2/G3/G6/G10 on shell tools; blocks with actionable guidance; stdlib; `--self-test` (34 cases incl. the mid-word slug false positives as negatives) |
| `injection-sentinel.py` | PostToolUse hook implementing G8 — names and reports prompt injection in fetched content; `--log PATH`; `--self-test` (13 benign API-doc fragments + 7 payloads) |
| `policy.rules.json` | Machine-readable gate index (ten gates); `self_test` field names the command |
| `claude-code-hooks.md` | Copy-paste settings.json wiring for the gates, Shield, Instincts, and Stop-nudges, with verification commands |

## shield/ — config-surface auditor

| File | One line |
|---|---|
| `shield.py` | Static auditor for the agent's own config (CLAUDE.md/settings/hooks/MCP): secrets, injection, over-broad perms, risky hooks; CI-ready; `.operant-shield-ignore` + `--ignore`; skips and reports linked git worktrees; defensively quoted injection phrases downgraded to LOW; `--self-test` |
| `README.md` | What Shield scans, usage, scope control (ignore file, worktrees, defensive quoting), tuning, opt-out marker, and when to run it |

## instincts/ — continuous-learning loop

| File | One line |
|---|---|
| `instincts.py` | Confidence-scored behavioral-pattern store: record at session end, inject proven ones at session start, decay/retire on correction |
| `README.md` | The loop, why confidence-scoring beats a flat list, commands, candidate format, wiring, and exclusions |

## references/ — the principles, in depth (18)

| File | One line |
|---|---|
| `communication.md` | Outcome-first writing, the filler catalogue, selection over compression, calibrated claim language |
| `autonomy.md` | The act/ask boundary, the last-paragraph test, errors-aren't-stop-signs, assessment vs. action mode |
| `autonomy-levels.md` | L0–L3 deployment profiles; higher autonomy requires stronger enforcement; the ratchet rule |
| `verification.md` | The 5-rung verification ladder, faithful failure reporting, evidence-action matching, whole-chain checks |
| `tool-discipline.md` | Parallelism by default, delegate-breadth/keep-depth, instrument hierarchy, never pay twice for a fact |
| `planning-and-decisions.md` | When to plan vs. start, recommend-don't-enumerate, which decisions belong to the user, sunk cost |
| `safety.md` | The 4-tier irreversibility taxonomy, look-before-destroy, informing confirmations, blast radius, mistakes |
| `threat-model.md` | Seven attack classes on agent authority, each mapped to the layer that answers it; structural-not-behavioral |
| `code-quality.md` | Match the codebase, comment discipline, surgical diffs, root causes, test honesty |
| `ambiguity-and-requirements.md` | The 4-type ambiguity taxonomy, the assumption ledger, mid-task requirement changes, the XY problem |
| `context-management.md` | The context budget, re-anchoring, surviving compaction, static vs. perishable facts, long-task pattern |
| `delegation-and-multiagent.md` | What to delegate vs. keep, brief quality, fan-out rules, the verification gradient, orchestration shapes |
| `estimation-and-status.md` | Countable progress, range estimates, "almost done" is banned, blocker reports with escape routes |
| `memory-and-persistence.md` | What deserves persistence, note shape, update-don't-accrete, recall-is-not-truth, session-boundary capture |
| `security-posture.md` | Secret absolutes, untrusted-content-is-data, injection defense, dependency caution, the dual-use line |
| `user-calibration.md` | Reading expertise from evidence, corrections are gold, stakes calibration, pushing back well |
| `environment-awareness.md` | Ground truth before acting, harness rules are physics, cross-platform tax, state-you-create-you-own |
| `failure-modes.md` | Named anti-patterns across all domains, each with a self-recognition tell and a fix — run at the gates |

## playbooks/ — end-to-end task shapes (18)

**Coding (8):** `debugging` · `incident-response` · `refactoring` · `greenfield-builds` · `code-review` · `migrations` · `performance-optimization` · `dependency-upgrades`

**General & non-coding (10):** `research-and-analysis` · `data-work` · `data-reporting` · `writing-and-docs` · `recurring-automation` · `customer-support` · `ecommerce-ops` · `marketing-content` · `personal-ops` · `vendor-briefing`

Each follows the same shape: Phase 0 orientation → verified increments → adversarial self-check → honest report → a named anti-pattern list.

## checklists/ — the four gates (4)

`before-starting` · `before-claiming-done` · `before-destructive-actions` · `session-end`

## examples/ — calibration by demonstration (4)

| File | One line |
|---|---|
| `report-makeovers.md` | Five report shapes before/after: completion, failure, investigation, status, simple answer |
| `confirmation-makeovers.md` | Five risky-action confirmations before/after: delete, send, prod change, scope, described-vs-found |
| `worked-scenarios.md` | Three end-to-end coding scenarios with the wrong turns named |
| `non-coding-worked-scenarios.md` | Three end-to-end non-coding scenarios: a refund, a marketing send, a research task carrying an injection |

## adaptations/ — porting guides (5)

| File | One line |
|---|---|
| `claude-code.md` | Native install, CLAUDE.md wiring, mapping to Claude Code mechanisms, model notes, hooks enforcement |
| `other-ides.md` | Cursor / Windsurf / Copilot recipes, the generic rules-file port, what degrades and how to compensate |
| `api-and-custom-agents.md` | Three-layer architecture, multi-agent notes, non-coding mapping, token economics, evals |
| `hermes-agent.md` | Long-running autonomous orchestrator archetype; why enforcement must be code; the wiring checklist |
| `multi-agent-orchestrators.md` | Lead/subagent systems: the brief-as-schema, the verification gradient, centralized gates, failure isolation |

## schemas/ — the discipline made machine-readable (9 + index)

`task-brief` · `risk-classification` · `verification-report` · `destructive-action-confirmation` · `external-send-confirmation` · `assumption-ledger` · `decision-flag` · `eval-scenario` · `agent-behavior-scorecard`, plus `schemas/README.md` mapping each to the rule it backs.

## registry/ — the single source of truth (1)

| File | One line |
|---|---|
| `rules.json` | Every behavioral rule mapped to its layer (PROMPT/RETRIEVAL/HARNESS_POLICY/CODE_GUARD/EVAL_ONLY), failure mode, reference, gate, schema, and eval. Change a rule, and this tells you every artifact that must move with it |

## evals/ — is it actually working? (3 + fixtures + scenarios + runs)

| File | One line |
|---|---|
| `eval-suite.md` | 28 behavioral scenarios with pass criteria and fail tells; a two-number scorecard (behavior score + safety gate); every code gate has a proving eval |
| `runner-spec.md` | How to run the suite as a system: fixtures, deterministic-then-judge flow, scoring, run modes, blocking failures |
| `eval-runner.py` | Reference implementation: stdlib-only runner — validate / run (smoke, full, certification) / score / self-test; deterministic checks first, judge prompts always emitted, optional auto-judge, schema-validated scorecards |
| `fixtures/README.md` | The fixture format: minimal, fresh-per-run, sandboxed side effects — plus the fixture.json contract the runner consumes |
| `fixtures/E*/fixture.json` | 26 provisioning fixtures: planted bugs, mock side-effecting tools (mailer, vendor export, payment CLI, deployer), shared-checkout and shared-log sandboxes, a sqlite order store, post-state bindings |
| `scenarios/*.json` | All 28 machine-readable eval scenarios (E1–E28) matching `eval-scenario.schema.json` |
| `runs/` | Recorded scorecards: `2026-07-09-haiku-baseline/` (claude-haiku-4-5, prompt-only, L2 — 12/21, blocked) · `2026-09-fable-cert/` (claude-fable-5-1, gates active — 26/28, ready) · `2026-09-opus-cert/` (claude-opus-5 — 26/28, ready) · `2026-09-sonnet-cert/` (claude-sonnet-5 — 22/28, blocked) · `2026-09-haiku-gates-cert/` (claude-haiku-4-5 with gates — 17/28, blocked) |

## dist/ — compiled editions (2)

| File | One line |
|---|---|
| `single-file.md` | The whole discipline compiled into one self-contained file for rules-file platforms and system prompts |
| `one-page.md` | The Ten Principles + four gates on a single page — the adoption front door, paste-anywhere |

## tools/ — release hygiene (1)

| File | One line |
|---|---|
| `release-check.py` | Release lint: version agreement across registry/policy/plugin/marketplace/runner/CHANGELOG, dist presence, governance cross-checks (every gate → spec section + registry rule; every rule's eval → scenario file; every fixture-kind scenario → fixture), and bundle↔mirror parity by SHA-256; stdlib, exit 1 on drift |

## Reading order for humans

1. `README.md` → 2. `QUICKSTART.md` → 3. `SKILL.md` → 4. `references/failure-modes.md` (the fastest way to *feel* the discipline) → 5. `examples/` → 6. whichever playbook matches your work → 7. `references/autonomy-levels.md` + `enforcement/generic-policy-spec.md` (the layer model) → 8. your platform's adaptation guide → 9. `evals/eval-suite.md` to prove it took.
