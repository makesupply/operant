# Playbook: Incident Response
*Read when: something is broken in production right now and users, money, data, or secrets are at risk.*

**Goal:** stop the bleeding, then find the cause, in that order, with the user informed at every state change. Incidents invert the normal discipline: speed beats elegance, mitigation beats diagnosis, and communication beats both.

## The priority stack, in strict order

1. **Stop ongoing damage**: data loss, money burning, users harmed, secrets exposed.
2. **Restore service**, even degraded, even ugly.
3. **Preserve evidence** for the diagnosis you will do once stable.
4. **Diagnose the root cause.**
5. **Fix properly and harden.**

A root-cause fix can wait for stability; a rollback cannot.

## Authority under fire

Incident urgency does not suspend the Tier 3 confirmation rules in [safety.md](../references/safety.md); it changes how they are satisfied.

- **Execute autonomously**: mitigations that are both reversible and pre-authorized, such as a documented runbook step, a rollback mechanism built for exactly this, or a feature flag designed to be flipped. That is what standing authorization looks like.
- **Pre-stage and confirm** everything else that touches production. Prepare the exact mitigation, meaning the command, the target, and the expected effect, and put the confirmation request inside the first status announcement: "X is down since 14:20; ready to roll back to v341, which is migration-free and safe to re-roll; confirm and it executes in seconds." The user loses no time to a separate round-trip, and no unauthorized production change happens.
- **Never, even under fire**: destructive shortcuts such as dropping data, force operations, or irreversible schema surgery without explicit confirmation. Pressure is when these mistakes happen, which is why the gate exists.

## When nobody is present

An unattended run that detects an incident is the first responder, with narrower authority than a human. It may act alone on reads, on pausing its own job, and on rolling back a change it made itself in this run through a mechanism built for that. It pages a human immediately with the blast radius, the suspected change, and the mitigation it is ready to execute. It may not touch production beyond its own change, delete anything, or take any Tier 3 step without a human's yes. When nobody answers within the window the project states, it halts in the safest state those actions can reach and reports exactly what it did, saw, and did not do. The halt rules in [autonomy-levels.md](../references/autonomy-levels.md) under L3 apply in full.

## First five minutes

- **Establish blast radius**: what is affected, since when, how badly, and whether it is growing. Growing incidents outrank static ones.
- **What changed?** The last deploy, config change, dependency, or scheduled job before onset. Most incidents are self-inflicted; the change log is suspect number one.
- **Announce state immediately**: "X is down since about 14:20, likely related to the 14:15 deploy; checking rollback viability now." Silence during an incident is the cardinal sin; see [estimation-and-status.md](../references/estimation-and-status.md).

## Mitigation decisions

The fastest lever is usually rollback, disable, restart, shed load, or failover.

- **Check the mitigation's own safety before pulling the lever.** The classic trap is rolling back a deploy that bundled a schema migration or already wrote data in the new format; old code meets new data, and the "safe" rollback is the second incident. Ask whether the rollback target reads the current schema and config, and whether anything was written that only the new version understands. If unclear, prefer a mitigation that does not rewind state.
- **Reversible mitigations first.** Under pressure the irreversibility rules get tighter, not looser.
- **Evidence-match even in a hurry**, per [verification.md](../references/verification.md). A restart "fixes" a memory leak and destroys the heap dump. Grab the evidence first if it costs seconds, never minutes, and say the trade when you skip it.
- **One change at a time.** Two simultaneous mitigations that coincide with recovery mean you do not know which worked.
- **Verify the mitigation took.** Not "rollback executed" but "error rate returned to baseline." Hold the all-clear until the metric has stayed at baseline for at least as long as the incident took to detect, or one full usage cycle for load-shaped failures.

## Working the diagnosis, after stabilization

Now it is the [debugging playbook](debugging.md) with two additions. Build the timeline first: change deployed 14:15, errors begin 14:19, alarm 14:26. Causality lives in ordering, and half of all incident mysteries dissolve when the timeline is written down. And push the five whys one level past the code: the bug is why it broke; why nothing caught it is what prevents the sequel.

## Communication during incidents

Short, factual, on every state change: current user impact, what has been done, what is next, what you need. Label known and suspected apart; never speculate blame.

## After the incident

Root cause confirmed in one sentence with evidence; "correlated with the deploy" is a lead, not a cause. The real fix, tested, plus the regression test. A hardening pass: the alert that would have caught it earlier, the validation that would have blocked it, the runbook line for next time. The write-up: timeline, cause, impact, resolution, follow-ups, blameless in tone and precise in mechanism.

## Exit criteria

- [ ] Damage stopped and service restored before diagnosis began.
- [ ] Every production change was pre-authorized or confirmed with its exact command, target, and expected effect.
- [ ] The mitigation was verified by the metric returning to baseline and holding.
- [ ] Evidence was preserved, or the trade was stated when it was not.
- [ ] Root cause is stated in one sentence with evidence, the fix ships with a regression test, and the hardening pass names what was added.
- [ ] For an unattended first responder: only reads, own-job pause, and own-change rollback were taken alone, a human was paged, and the halt was reported.

## Anti-patterns

- **The hero diagnosis.** *Tell:* chasing root cause while users bleed. *Fix:* mitigate first.
- **The silent operator.** *Tell:* twenty minutes of work, zero updates. *Fix:* announce on every state change.
- **The pressure delete.** *Tell:* "just drop the stuck rows." *Fix:* no destructive shortcut without confirmation.
- **The premature all-clear.** *Tell:* victory declared at the first good data point. *Fix:* baseline, sustained, then all-clear.
- **The rollback into the second incident.** *Tell:* old code rolled onto data only the new version understands. *Fix:* check the mitigation's safety before pulling it.
- **The self-authorized responder.** *Tell:* an unattended run took a Tier 3 step because it was urgent. *Fix:* page, pause, halt; never execute what should be queued.
