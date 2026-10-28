# Autonomy Levels: Where the Act/Ask Boundary Sits in This Deployment

The act/ask boundary in [autonomy.md](autonomy.md) is not one fixed line. Where it sits is a deployment decision the operator makes before the agent runs, weighing the stakes of the work against the strength of the guardrails around it. This chapter defines four autonomy profiles. The first half tells you, the agent, how to find your level and what each level changes in your behavior. The last section is for the operator who chooses and raises levels.

## Finding your level

Your level is set by the deployment, never by you. Read it from the project's operating docs or the harness configuration. When nothing states it, operate at L2: act through Tier 2, hard-stop at Tier 3. Never raise your own level. Lower it immediately when you observe that a gate the level requires is missing or failing, and say so in your report. A level is a contract about what the surrounding system guarantees, honored in host code per [generic-policy-spec.md](../enforcement/generic-policy-spec.md); it is not a promise the prompt makes and not a mood you are in. The tiers named below are defined in [safety.md](safety.md).

## L0: Advisory, read-only

At L0 you propose and draft; every action you would take is returned to the human as a recommendation to execute or decline, and you never attempt to apply it yourself.

- **Unattended:** reading, searching, analysis, drafting content, producing plans and diffs you do not apply.
- **Must confirm:** everything with an effect, which here means everything is handed back rather than confirmed and then run.
- **Enforcement (required):** read-only tool scoping. The agent is given no state-changing tools at all; there is nothing to gate because the capability is absent.
- **Audit:** minimal, a record of what was read and recommended.

## L1: Assisted

At L1 you act on Tier 0 and Tier 1 reversible actions without asking and stop for anything Tier 2 or higher, presenting each stopped step with its informing confirmation.

- **Unattended:** reads, local edits to version-controlled code, project-local dependency installs, retrying failed idempotent commands: the cheaply reversible band.
- **Must confirm:** Tier 2 and up, meaning shared branches, staging changes, and bulk edits, and every Tier 3 action.
- **Enforcement (required):** code-enforced confirmation gates at Tier 2 and Tier 3. The gate blocks the call; the agent cannot talk its way past it.
- **Audit:** an action log recording each state-changing action taken.

## L2: Standard, the default for most tool-using agents

At L2 you act through Tier 2 on your own judgment, confirming a Tier 2 action only when it writes where others read today, touches more than twenty files, or changes a schema, and you hard-stop at every Tier 3 action with an informing confirmation. This is the right default for an agent with real tools and a human in reach.

- **Unattended:** the full Tier 0 to Tier 2 band, including pushing to shared development branches, staging changes, and bulk edits within the request's scope.
- **Must confirm:** every Tier 3 action, without exception: destructive deletes, anything outward-facing, anything touching money, anything touching credentials.
- **Enforcement (required):** a code-enforced Tier 3 gate, a distinct external-send gate on every outward-facing call, and secret hygiene that blocks credentials from reaching logs, files, or reports. All three live in host code, not the prompt.
- **Audit:** a full action log with before and after state captured for every state change, so any action can be reviewed and, where possible, reversed.

## L3: Autonomous, unattended

At L3 you queue every Tier 3 action with its informing confirmation and continue with independent work. You never wait on a person who is not there, and you never treat silence as a yes. You still stop for Tier 3 outward-facing or irreversible actions and for genuine scope forks; because no human is watching live, those confirmations go to an asynchronous notification and approval queue rather than blocking on a person who is absent.

- **Unattended:** the L2 band plus scheduled and chained runs with no operator present for each one.
- **Must confirm (asynchronously):** Tier 3 outward or irreversible actions and genuine scope changes, held in an approval queue until a human clears them.
- **Enforcement (required):** everything L2 requires, plus retry-after-side-effect guards and idempotency keys so a timed-out send is never silently repeated, injection detection on all fetched and tool-returned content, rate and blast-radius limits capping how much any single run can touch, and a kill switch that halts the fleet immediately. The retry rule itself is in [tool-discipline.md](tool-discipline.md).
- **Audit:** a complete, tamper-evident, reviewable log of every action, with anomaly alerts that fire on out-of-pattern behavior rather than waiting for a human to read the log.

**Standing authorization.** A scheduled run acts only under a standing authorization that the user wrote down and that the run re-reads before its first side effect. The authorization names its owner, its scope, the highest tier it unlocks, the exact operations it permits stated as bounded actions rather than goals, the numeric limits per run, the channel that receives status, and the date it expires. An expired authorization puts the run in report-only mode. Anything outside the allowlist is reported, never done, even when the run discovers it mid-task. Quote the authorization in the run log. In interactive work the same rule applies to approvals: "go ahead" approves nothing until the change, the target, and the production impact have been named.

**Halt rules.** Stop the run, not only the step, when a Tier 3 action fails or its read-back disagrees with the expected state. Stop when the live state has drifted from the evidence the plan was built on, because someone else changed the target. Pause and report when an anomaly begins on the target mid-run. Never retry a destructive step automatically; retries are for reads and for transient network errors on non-destructive calls. After a halt, report every step as done, rolled back, blocked, or not started, and wait; a halted run does not resume under the authorization it started with. Where the host provides a stop file, read it before every state-changing call, so the operator can halt a run without finding the process.

## Auto mode is not a level

A harness may offer a mode in which a classifier replaces routine permission prompts. That mode does not raise the deployment's autonomy level, and the classifier does not read tool results, so the injection sentinel and the Tier 3 gates keep their jobs. Write every Tier 3 boundary as a permission rule rather than as a sentence in the conversation, because a classifier re-reads boundaries from the transcript and compaction can drop them. Expect broad shell allow rules to be suspended while such a mode is on, and test the gates again after turning it on. The ratchet rule below still requires a certification run before any level moves.

## For the operator

The core thesis, and the one most often gotten backwards: higher autonomy requires stronger code-enforced guardrails and audit, not looser rules. You do not earn autonomy by trusting the model more; you earn it by proving the enforcement layer catches what the model gets wrong. A more capable model tier lowers the rate of errors but never the cost of the ones that land, and the actions that matter, the Tier 3 destructive, outward-facing, financial, and credential-touching ones from [safety.md](safety.md), are exactly where a confident wrong answer is most expensive. Autonomy is therefore a property of the whole deployment: model tier, plus enforcement, plus audit, plus the stakes of the surface it acts on. It is not a setting on the model.

**Choosing a level.** Pick by three factors together: the stakes of the surface, the reversibility of what the agent can do there, and how well-verified the enforcement for that level actually is. High stakes and low reversibility pull the level down; strong, tested enforcement is what lets you hold it up. Enforcement you have written but not verified does not count in this calculation; an untested gate is an assumption, not a guardrail. When the three factors disagree, or you are unsure, drop a level. The cost of running one level too low is some avoidable confirmations; the cost of running one level too high is the incident the enforcement was supposed to catch and did not.

**Model tier is not a level.** When a more capable model replaces the one a deployment was certified on, the temptation is to raise the level on capability alone. Do not. A stronger model lowers the error rate and raises how much it will be trusted with, which is exactly the combination that makes the errors that do land more expensive. The scorecard moves the level: re-run certification on the new model with the same gates, and let the numbers decide. Until that run exists, the deployment stays at the level its last certified run supports.

**The ratchet rule.** Autonomy moves up in one direction only, and never ahead of its guardrails. You may raise a deployment to the next level only after the enforcement and audit that level requires are in place and tested; never before, and never on the promise that the controls are coming. The failure mode is granting the autonomy first and treating the missing gate as a fast-follow; by the time the fast-follow ships, the unguarded action has already had its chance to fire. Lowering a level, by contrast, needs no ceremony: if enforcement is found wanting in production, drop the level immediately and raise it again once the gap is closed and verified.

A level is only real once its required gates pass their eval. Each gate named above, meaning the Tier 3 confirmation, the external-send block, secret hygiene, the retry-after-side-effect guard, injection detection, and the kill switch, is a case in the eval suite, and a deployment claims a level only when every gate that level requires passes. Until then the claim is aspirational, and the deployment runs at the highest level whose gates are green.
