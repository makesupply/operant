# Playbook: Incident Response

**Goal:** stop the bleeding, then find the cause — in that order, with the user informed at every state change. Incidents invert the normal discipline: speed beats elegance, mitigation beats diagnosis, and communication beats both.

## The priority stack (strict order)

1. **Stop ongoing damage** — data loss, money burning, users harmed, secrets exposed.
2. **Restore service** — even degraded, even ugly.
3. **Preserve evidence** — for the diagnosis you'll do once stable.
4. **Diagnose the root cause.**
5. **Fix properly and harden.**

Never let a lower rung delay a higher one. Diagnosing while the system burns is self-indulgence; a root-cause fix can wait for stability, a rollback can't.

## Authority under fire

Incident urgency does not suspend the Tier-3 confirmation rules ([safety.md](../references/safety.md)) — it changes *how* they're satisfied. The reconciliation:

- **Execute autonomously**: mitigations that are both reversible and pre-authorized — a documented runbook step, a rollback mechanism built for exactly this, a feature flag designed to be flipped. These are what standing authorization looks like.
- **Pre-stage and confirm**: everything else that touches production. Prepare the *exact* mitigation (the command, the target, the expected effect), and put the confirmation request inside the first status announcement — "X is down since 14:20; ready to roll back to v341, which is migration-free and safe to re-roll — confirm and it executes in seconds." The user loses no time to a separate round-trip, and no unauthorized production change happens.
- **Never, even under fire**: destructive shortcuts (dropping data, force-anything, irreversible schema surgery) without explicit confirmation. Pressure is when these mistakes happen, which is why the gate exists.

## First five minutes

- **Establish blast radius**: what's affected, since when, how badly, and is it growing? Growing incidents outrank static ones.
- **What changed?** — the last deploy, config change, dependency, data event, or scheduled job before onset. Most incidents are self-inflicted; the change log is suspect #1.
- **Announce state immediately**: "X is down since ~14:20, likely related to the 14:15 deploy; checking rollback viability now." The user makes different decisions when they know — silence during an incident is the cardinal sin (see [estimation-and-status.md](../references/estimation-and-status.md)).

## Mitigation decisions

The fastest lever is usually one of: **rollback** (the change that correlates), **disable** (the feature flag, the failing job), **restart** (for resource exhaustion — but see below), **shed load** (rate limit, queue, degrade gracefully), **failover**.

Rules for choosing:

- **Check the mitigation's own safety before pulling the lever.** The classic trap: rolling back a deploy that bundled a schema migration, or that has already written data in the new format — old code meets new data, and the "safe" rollback is the second incident. Thirty seconds on: does the rollback target read the current schema/data/config? Was anything written since the change that only the new version understands? Flags: do two flags interact? If the answer is unclear, prefer a mitigation that doesn't rewind state (disable, shed load, fail over).
- **Reversible mitigations first.** A clean rollback can be re-rolled; a hasty schema "fix" cannot. Under pressure, the irreversibility rules from [safety.md](../references/safety.md) get *tighter*, not looser.
- **Evidence-match even in a hurry** ([verification.md](../references/verification.md)): a restart "fixes" a memory leak and destroys the heap dump. If the mitigation erases diagnostic state, grab the evidence first — logs, dumps, metrics screenshots — *if* rungs 1 and 2 allow the seconds: evidence-grabbing may cost moments, never minutes, against stopping damage or restoring service. Say the trade explicitly when you skip it: "Restarting without a dump; recurrence will be harder to diagnose, but the queue is backing up."
- **One change at a time.** Two simultaneous mitigations that coincide with recovery mean you don't know which worked — you'll re-learn that at the next occurrence, in production, at night.
- **Verify the mitigation took** — not "rollback executed" but "error rate returned to baseline." Hold the all-clear until the metric has stayed at baseline for at least as long as the incident took to detect (or one full traffic/usage cycle for load-shaped failures); incidents that "resolve" and re-fire in 20 minutes were never resolved.

## Working the diagnosis (post-stabilization)

Now it's the [debugging playbook](debugging.md) with two additions:

- **Timeline first**: build the sequence — change deployed 14:15, errors begin 14:19, alarm 14:26. Causality lives in ordering; half of all incident mysteries dissolve when the timeline is written down.
- **The five whys go one level past the code**: the bug is why it broke; *why did nothing catch it* (test gap? alert gap? review gap?) is what prevents the sequel.

## Communication during incidents

Short, factual, on every state change — not on a timer:

> "14:32 — Mitigated: rolled back to v341, error rate back to baseline at 14:30. Cause not yet confirmed (suspect the new cache path). Evidence preserved. Digging now; will confirm cause before we re-attempt the deploy."

Each update: current user impact, what's been done, what's next, what you need (or "nothing"). Never speculate blame ("probably the vendor") in status updates — say what's *known* and what's *suspected*, labeled as such.

## After the incident

- **Root cause confirmed and stated** in one sentence, with evidence — "correlated with the deploy" is a lead, not a cause.
- **The real fix**, tested, plus the regression test.
- **Hardening pass**: the alert that would have caught it earlier, the validation that would have blocked it, the runbook line for next time. An incident that produces only a fix has wasted its tuition.
- **The write-up**: timeline, cause, impact, resolution, follow-ups. Blameless in tone, precise in mechanism — written for the person who hits the *next* one.

## Anti-patterns under fire

- **The hero diagnosis.** Chasing root cause while users bleed. Mitigate first.
- **The shotgun.** Restarting five things at once; recovery becomes unexplainable.
- **The silent operator.** Twenty minutes of work, zero updates. The user is deciding whether to escalate, wake people, or announce — starve them of state and they decide wrong.
- **The pressure delete.** "Just drop the stuck rows" — destructive shortcuts feel proportionate mid-incident and are how one incident becomes two.
- **The premature all-clear.** Declaring victory at the first good data point. Baseline, sustained, then all-clear.
- **The unfiled lesson.** Everything back to green, nothing written down; the next occurrence starts from zero.
