# Autonomy Levels — Tuning the Act/Ask Boundary per Deployment

The act/ask boundary in [autonomy.md](autonomy.md) is not one fixed line. Where it sits is a deployment decision the operator makes before the agent runs, weighing the stakes of the work against the strength of the guardrails around it. This reference defines four autonomy profiles the operator selects at deployment time and the enforcement each one requires.

The core thesis, and the one most often gotten backwards: higher autonomy requires stronger code-enforced guardrails and audit, not looser rules. You do not earn autonomy by trusting the model more; you earn it by proving the enforcement layer catches what the model gets wrong. A more capable model tier lowers the rate of errors but never the cost of the ones that land, and the actions that matter — the Tier 3 destructive, outward-facing, financial, and credential-touching ones from [safety.md](safety.md) — are exactly where a confident wrong answer is most expensive. So autonomy is a property of the whole deployment — model tier, plus enforcement, plus audit, plus the stakes of the surface it acts on — not a setting on the model and not a mood the agent is in. A level is a contract about what the surrounding system guarantees, honored in host code per [generic-policy-spec.md](../enforcement/generic-policy-spec.md), not a promise the prompt makes.

## L0 — Advisory / read-only

Proposes and drafts; takes no state-changing action. Every action the agent would take is returned to the human as a recommendation to execute or decline.

- **Unattended:** reading, searching, analysis, drafting content, producing plans and diffs it does not apply.
- **Must confirm:** everything with an effect — which here means everything is handed back, not confirmed and then run.
- **Enforcement (required):** read-only tool scoping. The agent is given no state-changing tools at all; there is nothing to gate because the capability is absent.
- **Audit:** minimal — a record of what was read and recommended.

## L1 — Assisted

Acts on Tier 0 and Tier 1 reversible actions on its own; stops for anything Tier 2 or higher.

- **Unattended:** reads, local edits to version-controlled code, project-local dependency installs, retrying failed idempotent commands — the cheaply reversible band.
- **Must confirm:** Tier 2 and up (shared branches, staging changes, bulk edits) and every Tier 3 action.
- **Enforcement (required):** code-enforced confirmation gates at Tier 2 and Tier 3. The gate blocks the call; the agent cannot talk its way past it.
- **Audit:** an action log recording each state-changing action taken.

## L2 — Standard (the default for most tool-using agents)

Acts through Tier 2 on its own; hard-gates every Tier 3 action. This is the right default for an agent with real tools and a human in reach.

- **Unattended:** the full Tier 0–2 band — including pushing to shared dev branches, staging changes, and bulk edits within the request's scope.
- **Must confirm:** every Tier 3 action, without exception — destructive deletes, anything outward-facing, anything touching money, anything touching credentials.
- **Enforcement (required):** a code-enforced Tier-3 gate, a distinct external-send gate on every outward-facing call, and secret hygiene that blocks credentials from reaching logs, files, or reports. All three live in host code, not the prompt.
- **Audit:** a full action log with before/after state captured for every state change, so any action can be reviewed and, where possible, reversed.

## L3 — Autonomous / unattended

Acts broadly and on a schedule with minimal human-in-the-loop. It still stops for Tier 3 outward-facing or irreversible actions and for genuine scope forks — but because no human is watching live, it routes those confirmations to an asynchronous notification and approval queue rather than blocking on a person who is not there.

- **Unattended:** the L2 band plus scheduled and chained runs with no operator present for each one.
- **Must confirm (asynchronously):** Tier 3 outward/irreversible actions and genuine scope changes, held in an approval queue until a human clears them.
- **Enforcement (required):** everything L2 requires, plus retry-after-side-effect guards and idempotency keys so a timed-out send is never silently repeated (the carve-out from [autonomy.md](autonomy.md), enforced in code), injection detection on all fetched and tool-returned content, rate and blast-radius limits capping how much any single run can touch, and a kill switch that halts the fleet immediately.
- **Audit:** a complete, tamper-evident, reviewable log of every action, with anomaly alerts that fire on out-of-pattern behavior rather than waiting for a human to read the log.

## Choosing a level

Pick by three factors together: the stakes of the surface, the reversibility of what the agent can do there, and how well-verified the enforcement for that level actually is. High stakes and low reversibility pull the level down; strong, tested enforcement is what lets you hold it up. Enforcement you have written but not verified does not count in this calculation — an untested gate is an assumption, not a guardrail. When the three factors disagree, or you are unsure, drop a level. The cost of running one level too low is some avoidable confirmations; the cost of running one level too high is the incident the enforcement was supposed to catch and did not.

**Model tier is not a level.** When a more capable model replaces the one a deployment was certified on, the temptation is to raise the level on capability alone. Do not. A stronger model lowers the error rate and raises how much it will be trusted with, which is exactly the combination that makes the errors that do land more expensive. The scorecard moves the level: re-run certification on the new model with the same gates, and let the numbers decide. Until that run exists, the deployment stays at the level its last certified run supports.

## The ratchet rule

Autonomy moves up in one direction only, and never ahead of its guardrails. You may raise a deployment to the next level only after the enforcement and audit that level requires are in place and tested — never before, never on the promise that the controls are coming. The failure mode is granting the autonomy first and treating the missing gate as a fast-follow; by the time the fast-follow ships, the unguarded action has already had its chance to fire. Lowering a level, by contrast, needs no ceremony: if enforcement is found wanting in production, drop the level immediately and raise it again once the gap is closed and verified.

A level is only real once its required gates pass their eval. Each gate named above — the Tier-3 confirmation, the external-send block, secret hygiene, the retry-after-side-effect guard, injection detection, the kill switch — is a case in the eval suite, and a deployment claims a level only when every gate that level requires passes. Until then the claim is aspirational, and the deployment runs at the highest level whose gates are green.
