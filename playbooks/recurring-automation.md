# Playbook: Recurring Automation

**Goal:** work that runs correctly *unattended* — scheduled jobs, cron agents, pipelines, bots. Interactive work gets a human catching its mistakes in real time; automation's mistakes compound silently at schedule frequency. Everything in this playbook derives from one fact: **nobody is watching.**

## Phase 0 — Decide it deserves automation

- **Automate the stabilized, not the exploratory.** A report you've produced by hand three times with a settled format is automatable; a task still changing shape every run isn't — automation freezes decisions, so the decisions must be done evolving.
- **Price the failure, not just the success**: what happens when it runs wrong at 6am Saturday? Wrong-but-plausible output shipped to stakeholders is worse than no output. High-blast-radius tasks keep a human gate (draft-for-review beats auto-send) even when full automation is technically trivial.
- **Idempotence is a requirement, not a feature**: the job *will* eventually double-run (retries, overlapping schedules, manual re-triggers). Design so running twice equals running once — or the second run detects the first and exits.

## Phase 1 — Build for the unattended case

- **Explicit inputs, checked at start**: an interactive session can ask when something's missing; a job can't. Validate every precondition (data present? fresh enough? credentials valid? disk space?) at the top and **fail loudly** on any miss — a job that limps forward on stale input produces confident garbage on schedule.
- **Fail loudly, not partially**: half-completed runs that report success are the automation nightmare. Make the run atomic where possible (write to temp, swap on success); where not, make partial state detectable and the next run capable of resuming or cleaning up.
- **Fixed decisions, flagged surprises**: encode the settled judgment (thresholds, formats, recipients); when the job encounters something outside its settled territory — a new category, an anomalous value, a schema surprise — it flags for a human rather than improvising. An unattended job improvising is an incident with a timestamp.
- **Timestamps, timezones, and boundaries**: schedule-time vs. data-time confusion is the classic recurring-job bug. Be explicit about which timezone the schedule means, which period the data covers, and what happens at month boundaries and DST transitions (see [data-work.md](data-work.md) on partial periods).
- **Secrets and permissions per least privilege** ([security-posture.md](../references/security-posture.md)): the job gets the narrowest credentials that work; unattended credentials are the ones that leak longest.

## Phase 2 — Observability: the job must testify

An unattended job needs to answer three questions without being asked:

1. **Did I run?** — a log/heartbeat per run, timestamped, somewhere durable. Silence must be distinguishable from success.
2. **Did I succeed?** — an explicit success/failure record with the run's key numbers (rows processed, items sent, totals). Numbers make silent drift visible: when "processed 12,000 rows" becomes "processed 4" the log itself raises the eyebrow.
3. **What did I change?** — outputs and side effects listed, so any run can be audited after the fact.

And the mirror requirement: **someone must notice the silence.** A failure alert only covers detected failures; the job that stops running entirely (scheduler broke, credentials expired) emits nothing. Staleness detection — "no successful run in >25 hours" — catches the failure mode that failure alerts structurally can't.

## Phase 3 — Verify like it's unattended

- **Test the failure paths, not just the happy one**: missing input, empty data, expired credential, double-run. The happy path gets exercised every day in production; the failure paths get exercised only when it matters — unless you exercise them now.
- **Run it as it will run**: same environment, same credentials, same *absence of your interactive session* — jobs that work in your shell and fail headless (missing env, no TTY, different user, different PATH) are a cliché for a reason ([environment-awareness.md](../references/environment-awareness.md)).
- **Verify the first scheduled runs for real** — not just the manual trigger, the actual 6am execution. You won't be awake in a session at 6am; verify after the fact instead: check the run's heartbeat, log, and outputs at the next opportunity (or schedule a follow-up verification task for just after the first firing). The gap between "works when I run it" and "works when the scheduler runs it" is where the first week's failures live — and it's only visible in the scheduled run's own evidence.
- **Then verify the ratchet monthly-ish**: outputs still consumed? recipients still right? thresholds still sane? Automation drifts from usefulness silently — the report nobody reads anymore still costs its failure-handling forever.

## Maintenance and retirement

- **Every job has an owner and a written purpose** — a job whose reason nobody remembers can be neither trusted nor safely deleted; it becomes permanent haunted machinery.
- **Change it like production code**: version-controlled, tested, canaried where the blast radius warrants ([migrations.md](migrations.md) for changing a live pipeline's shape).
- **Retire deliberately**: when the need ends, remove the job, its credentials, its alerts, and its docs — a disabled-but-present job with live credentials is a security liability that no longer even pays rent.

## Anti-patterns

- **The optimist.** No input validation; garbage in, confident garbage out, on schedule, to stakeholders.
- **The silent success.** No heartbeat; dead for three weeks before anyone asks where the report went.
- **The improviser.** Encounters a novel case at 6am and guesses — the guess ships.
- **The double-tap.** Non-idempotent job + retry logic = duplicate sends/charges/rows.
- **The shell-only worker.** Works interactively, dies headless; debugged at 6am by someone who didn't write it.
- **The immortal zombie.** Consumers long gone, job still running, still alerting, still holding credentials.
