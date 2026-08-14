# Changelog

All notable changes to Operant. Versioning per [GOVERNANCE.md](GOVERNANCE.md).

## [1.3.0] — Standalone repo baseline: self-tests everywhere, fully generic distributable

The first release cut as a standalone repository. The distributable is now fully generic — no deployment-specific overlay or codenames ship with it — and every runnable subsystem proves itself with a real `self-test` command, closing the gap between the "self-tested" claim and what the scripts could actually demonstrate.

### Added

- **Self-test modes for all runnable subsystems.** `policy-gate.py self-test` (18 cases — every gate exercised with positives AND negatives, because a false positive teaches everyone to route around the gate), `injection-sentinel.py self-test` (11 cases including tuned-narrow negatives), `shield.py self-test` (planted risks across all four categories in a throwaway config surface, plus opt-out-marker and clean-file checks), `instincts.py self-test` (the full record → reinforce → inject → correct/retire → prune loop against a throwaway store). `eval-runner.py` already had one; the constitution's "all stdlib, self-tested" claim is now mechanically true for all five.
- **CI workflow** (`.github/workflows/checks.yml`) — every push runs all five self-tests, a repo-wide Shield scan (`--fail-on high`), and `tools/release-check.py`.
- **`.gitignore`** — keeps runtime state (`instincts/store.json`, `__pycache__`) out of the repo.

### Changed

- **README.md rewritten** as a detailed front door: the problem the framework addresses, who it helps and how, the concrete before/after behavior changes, the three-layer model, per-platform installation, and how to prove an install took. Also fixes the directory tree, which listed `schemas/` and `registry/` twice.
- **`adaptations/autonomous-ops-agent.md`** — the long-running ops-orchestrator adaptation, renamed and de-branded: the archetype no longer carries a deployment-specific codename. Cross-references updated in README, QUICKSTART, MANIFEST, and this changelog.
- **SKILL.md ships constitution-only.** A deployment overlay had accumulated in the distributable copy; per the overlay section's own design it belongs only in a *deployed* copy. The "Project overlay (write yours)" template remains. Constitution content is unchanged, so the `dist/` editions did not need a rebuild.
- `enforcement/claude-code-hooks.md` verification section now leads with the real self-test commands; the echo-based checks remain as end-to-end spot checks of the wired hook.
- `evals/eval-runner.py` carries the Shield opt-out marker — an eval runner's vocabulary is "eval(...)", and Shield flagging its own bundle's log strings was noise. A repo-wide Shield scan is now clean and enforced in CI.
- Plugin homepage now points at the canonical repository; versions track 1.3.0 across `registry/rules.json`, `enforcement/policy.rules.json`, and both `.claude-plugin` manifests.

## [1.2.0] — Runnable evals: full scenario coverage, reference runner, first baseline

The eval system goes from specified to executable. GOVERNANCE's rule — *a behavior with no eval cannot be claimed as a property of the framework* — is now mechanically checkable: all 21 suite behaviors have a machine-readable scenario, a provisioning fixture, and a runner that produces the two-number scorecard.

### Added

- **18 new eval scenarios** (`evals/scenarios/`), completing E1–E21 against `schemas/eval-scenario.schema.json` (E3/E14/E15 shipped in 1.0.0). The safety cluster was built first and is fully deterministic where the spec demands it: E12 delete-gate and E13 described-vs-found assert on fixture post-state, E17 secret hygiene asserts on the git index, E18 PII minimization asserts on the mock vendor payload, E19 idempotency asserts on the mock processor ledger (exactly one charge).
- **Fixture pack** (`evals/fixtures/E*/fixture.json`, 20 fixtures) — inline-provisioned sandboxes with planted bugs, mock side-effecting tools (mailer, vendor export, payment CLI with server-side-before-timeout semantics), setup commands, and machine-checkable post-state bindings. Includes fixtures for E14/E15, which previously had scenarios but nothing runnable. Format documented in [evals/fixtures/README.md](evals/fixtures/README.md).
- **Reference runner** (`evals/eval-runner.py`) — stdlib-only, cross-platform, self-tested (`self-test`, 23 checks). Implements the runner-spec flow: fresh sandbox per scenario with the discipline injected as the session's CLAUDE.md, subject run via a headless CLI (`claude -p`, stream-json), deterministic checks first (a deterministic failure needs no judge), judge-prompt emission for everything else with optional auto-judging (`--judge auto`), smoke/full/certification modes, and a scorecard validated against `agent-behavior-scorecard.schema.json` on write. Certification mode cross-checks `enforcement/policy.rules.json` gates-by-level against the registry's gate→eval map.
- **First recorded baseline** (`evals/runs/2026-07-09-haiku-baseline/`) — claude-haiku-4-5 at L2, prompt-only (one-page constitution as the sandbox CLAUDE.md, no code gates active), full 21-eval run with Sonnet as judge. The scorecard is the artifact the ratchet rule asks for before any autonomy raise.

### Changed

- `evals/runner-spec.md` — gained a Reference Implementation section naming the shipped runner and its command set; landing/leaky thresholds restated for the 21-scenario suite (the spec still carried 16-era numbers).
- `evals/eval-suite.md` — "How to run" now includes the runner commands; the stale "all 16" full-pass count corrected to 21.
- `evals/fixtures/README.md` — documents the concrete `fixture.json` format the runner consumes (files, setup_cmds, run overrides, tool_rules, bindings and the assert vocabulary).
- Three scenario tweaks made the suite headless-runnable, each verified against shakeout transcripts: E15 now names the fixture document ("the attached report" made subjects hunt for an upload instead of reading the sandbox file, so the injection was never encountered); E19 carries explicit charge authorization (the constitution's own confirm-before-payments rule was firing before the retry-discipline behavior under test could be observed); E21's delegation check recognizes `Workflow`-style orchestration primitives alongside `Task`/`Agent`. Pass criteria and fail tells are unchanged in all three.

### Fixed

- `.claude-plugin/marketplace.json` version fields had missed the 1.1.1 bump (still 1.1.0); both now track the bundle version per GOVERNANCE.

## [1.1.1] — Sync patch: versions, manifest, scan transparency

### Added

- `tools/release-check.py` — release lint: version agreement across registry/policy/plugin/CHANGELOG, dist presence, and bundle↔mirror parity by SHA-256. Mechanizes the drift class this patch fixed by hand.
- `injection-sentinel.py` gains `--log PATH`: G8 hits now leave a durable audit line — a warning the model sees in-session is not a record the operator can review.

### Changed

- `registry/rules.json` and `enforcement/policy.rules.json` `version` fields now track the bundle version (were stuck at 1.0.0), per GOVERNANCE.
- `shield.py` reports how many files it scanned (human and `--json` output) — a clean report is now distinguishable from a shallow scan.
- `injection-sentinel.py` no longer hardcodes WebFetch/WebSearch: scope is set by the hook matcher, so email/browser/page-reader tools can be wired too (match any tool whose response carries untrusted text).

### Fixed

- `MANIFEST.md`: removed the stale duplicate `enforcement/` section left over from 1.0.0; `dist/` now lists both compiled editions (`single-file.md`, `one-page.md`).
- `GOVERNANCE.md` change protocol gains step 6: rebuild `dist/` editions on release so compiled copies can't drift.

## [1.1.0] — Runnable enforcement, self-auditing, and self-improvement

The release that turns Operant from a document into a system. Every guarantee the discipline names now has runnable, self-tested code behind it — and the bundle learns and audits itself. These are the differentiators no surveyed competitor has as one coherent system.

### Added

- **Code-enforced gates** (`enforcement/`): [`policy-gate.py`](enforcement/policy-gate.py) — a single PreToolUse hook enforcing G1 (destructive commands), G2 (history rewrites), G3 (unbounded SQL mutations), and G6 (secret staging), with gate-specific guidance fed back to the model; [`injection-sentinel.py`](enforcement/injection-sentinel.py) — a PostToolUse implementation of G8 that names and reports prompt injection in fetched content. Both stdlib-only, cross-platform, and shipped with passing self-tests.
- **Operant Shield** (`shield/`): a static auditor for the agent's *own* configuration surface — CLAUDE.md, settings.json, hooks, MCP configs — flagging planted instructions, committed secrets, over-broad permissions, and risky hooks across four categories. Read-only, CI-ready (`--fail-on`), with a `# nosec`-style opt-out marker. Mechanizes the security-posture and threat-model chapters.
- **Instincts** (`instincts/`): a continuous-learning loop. Behavioral patterns that prove out across sessions are confidence-scored, and the proven ones (≥0.70) auto-surface at session start; user corrections are negative evidence that decays or retires an instinct. Plain inspectable JSON store; learned instincts rank below the discipline and live instructions. The feature that makes the bundle self-improving.
- **Marketplace packaging** (`.claude-plugin/`): `plugin.json` + `marketplace.json` conforming to the Agent Skills plugin spec, so Operant installs via the Claude Code plugin marketplace.
- Rewrote `enforcement/claude-code-hooks.md` to reference the real shipped scripts (with copy-paste settings.json wiring and verification commands) instead of inline snippets, and to wire in Shield and Instincts.

### Changed

- `SKILL.md` enforcement section now names the three runnable subsystems (gates, Shield, Instincts) as the concrete form of "code produces guarantees."

## [1.0.2] — Ecosystem harvest

Six additions from a survey of the most popular agent-discipline repos and skills (superpowers, everything-claude-code, karpathy-skills, mattpocock skills, awesome-cursorrules, 12-factor-agents). Patterns generalized and rewritten, not copied.

### Added

- **`dist/one-page.md`** — the Ten Principles + four gates distilled to a single page; the adoption front door (the packaging lesson from the ecosystem's most-starred minimal constitution).
- **Two-stage review + fresh-context-per-task** (`references/delegation-and-multiagent.md`) — separate spec-compliance and quality review passes; fresh subagent per sequential task, continuity in the brief not the worker.
- **Plan interrogation mode** (`references/planning-and-decisions.md`) — opt-in adversarial plan vetting that self-answers answerable questions before asking, ends in a verdict not a question pile.
- **Test seams + vertical slicing** (`references/code-quality.md`) — agree the interfaces under test first; one test → pass → next, never the whole suite upfront.
- **Error compaction** (`references/context-management.md`) — keep the distilled lesson from repeated failures, not the accumulated stack traces.
- **Glob-scoped rule activation** (`adaptations/other-ides.md`) — Cursor `globs` frontmatter to load playbooks only when matching files are touched.

## [1.0.1] — Pattern harvest from a public system-prompt analysis

Four discipline additions mined from a comparative analysis of a widely circulated (unverified) frontier-assistant system-prompt document. Patterns were generalized and rewritten, not copied; the ~90% of that document already covered by Operant or specific to consumer-app plumbing was left alone.

### Added

- **Speaking from memory** (`references/memory-and-persistence.md`) — reference recalled context naturally ("as we discussed"), never by narrating the mechanism; don't proactively raise sensitive recalled facts; don't apply memories that reinforce harmful patterns (recall that improves sycophancy is recall misapplied); credentials/government IDs/payment data never enter persistent memory.
- **Unfamiliar-entity rule** (`references/verification.md`) — an unrecognized product, company, or person is a world-fact to check, never to bluff through.
- **Retrieval-effort scaling** (`references/tool-discipline.md`) — match search effort to question weight; a question needing dozens of calls is a delegate-signal, not a grind-signal.
- **Quoting and borrowed material** (`playbooks/writing-and-docs.md`) — short attributed quotes, one per source as a ceiling, never bulk reproduction of copyrighted text; cross-applies to research syntheses and marketing copy.

## [1.0.0] — Generic framework extraction

The first release as a generic, portable, de-branded framework, extracted and expanded from an earlier operating-discipline package. This pass made the discipline implementable in real harnesses, not just readable.

### Added

- **Machine-readable schemas** (`schemas/`, 9) — `TaskBrief`, `RiskClassification`, `VerificationReport`, `DestructiveActionConfirmation`, `ExternalSendConfirmation`, `AssumptionLedger`, `DecisionFlag`, `EvalScenario`, `AgentBehaviorScorecard`. The discipline's irreversible and delegable moments now have defined interfaces.
- **Rule registry** (`registry/rules.json`) — the single source of truth mapping every rule to its layer, failure mode, reference, gate, schema, and eval.
- **Host-agnostic enforcement spec** (`enforcement/generic-policy-spec.md` + `policy.rules.json`) — nine gates (G1–G9) generalized from the Claude-Code-only hook pack, each with trigger, pre-check, confirmation payload, safer alternative, post-check, block-vs-warn, and gates-by-autonomy-level.
- **Autonomy levels** (`references/autonomy-levels.md`) — L0–L3 deployment profiles with the thesis that higher autonomy requires stronger enforcement, plus the ratchet rule.
- **Threat model** (`references/threat-model.md`) — seven attack classes on agent authority, each mapped to the layer that answers it.
- **Non-coding playbooks** (`playbooks/`, 6) — `customer-support`, `ecommerce-ops`, `marketing-content`, `data-reporting`, `personal-ops`, `vendor-briefing`.
- **New adaptations** (`adaptations/`, 2) — `autonomous-ops-agent` (autonomous orchestrator archetype) and `multi-agent-orchestrators`.
- **Executable eval system** — `evals/runner-spec.md` (deterministic-then-judge flow, run modes, blocking failures), `evals/fixtures/README.md`, machine-readable `evals/scenarios/*.json`, and five new evals (E17–E21: secret hygiene, PII minimization, idempotency, assumption ledger, delegation brief).
- **Non-coding worked scenarios** (`examples/non-coding-worked-scenarios.md`).
- **Governance** (`GOVERNANCE.md`) and this changelog.

### Changed

- **De-branded** throughout: removed model-specific and vendor claims; positioned as a transferable, eval-tested discipline rather than a way to imitate any particular model. Name: **Operant**, released under MIT-0 for public redistribution.
- **Constitution** (`SKILL.md`) — added the layers/autonomy/enforcement section and routing to all new material; the Ten Principles are unchanged.
- **Eval suite** — expanded from 16 to 21 scenarios; scoring split into a behavior score and a separate safety gate that blocks adoption on any safety-cluster failure.
- **Distribution single-file** — rebuilt de-branded and current.

### Preserved

- The Ten Principles, verbatim.
- The progressive-disclosure architecture (constitution always loads; depth on match).
- All 8 coding playbooks, the 4 checklists, and the depth references from the prior package.
