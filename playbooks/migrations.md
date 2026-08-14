# Playbook: Migrations

**Goal:** move from state A to state B — schema, API, platform, framework, data store — without losing anything and without a moment where things are broken and unrescuable. Migrations combine refactoring's drift risk with operations' irreversibility risk; the playbook is mostly about never being stranded in the middle.

## Phase 0 — Inventory before itinerary

- **Enumerate everything that must move, mechanically**: grep, query, scan — don't estimate. "About 30 call sites" becomes exactly 47, including the three in the cron scripts nobody remembers. The migration plan is only as complete as this inventory, and every missed item is a production surprise scheduled for later.
- **Find the consumers you don't own**: external API clients, downstream jobs reading the table, dashboards parsing the export, that one partner integration. The things *you* can't update on your schedule define the migration's real shape (and usually force a compatibility window).
- **Classify each item**: mechanically transformable (scriptable), individually reviewable (hand work), and unknown (investigate first). The ratio determines whether this is an afternoon or a quarter — report that sizing before starting ([estimation-and-status.md](../references/estimation-and-status.md)).
- **Define "done" and "verified done"**: not "the script ran" but "zero references to the old form remain, all consumers on the new path, old path removed." Write the verification query/check *now* — it's your finish line detector.

## Phase 1 — Design for reversibility at every step

The cardinal design rule: **at every intermediate point, the system works and you can retreat.**

- **Expand → migrate → contract**, the pattern that carries almost every migration: add the new alongside the old (expand), move consumers over incrementally (migrate — each step small and testable), remove the old only when *verifiably* unused (contract — the only irreversible phase, done last, when it's boring).
- **"Expand" is only safe at your scale if you check.** On large tables, the "additive" step itself can be the outage: `ADD COLUMN` with defaults on older engines, index builds without `CONCURRENTLY`, and unthrottled backfills take locks or saturate the primary. Know your engine's locking behavior for the specific DDL, throttle backfills, and rehearse anything table-shaped on a production-scale copy — duration and locks don't show up on the dev database's 10k rows.
- **Never modify-in-place when add-alongside is possible.** Renaming a column in place is a cliff; adding the new column, dual-writing, backfilling, switching readers, then dropping is a staircase.
- **The point of no return gets scheduled, not stumbled into**: identify exactly which step is irreversible (the drop, the cutover, the format change), and gate it behind explicit confirmation ([safety.md](../references/safety.md)) plus the verification that nothing still depends on what's being removed.
- **Backups verified before the irreversible step** — "verified" means *restored once*, not "the backup job said OK." When a full test restore is infeasible (the 2TB managed database), degrade explicitly rather than waive silently: restore a sample to scratch, spot-check point-in-time recovery, or cite the provider's restore attestation — and state in the plan which level you got.

## Phase 2 — Execute in ratcheting increments

- **Canary first, always**: one call site, one table, one service through the new path — verified end-to-end — before the fleet. The canary flushes out the misunderstanding while it's one unit wide ([safety.md](../references/safety.md) blast-radius rule).
- **Batch the mechanical, review the exceptional**: scripted transforms for the classified-mechanical items, with spot-checks per batch; individual attention for the hand-work list. Don't hand-review 400 identical changes, and don't script the 12 weird ones.
- **Keep the ratchet visible**: a running count against the Phase-0 inventory ("312/347 call sites migrated; remaining: the 3 cron scripts + 32 in the deprecated admin panel"). This is also your status report, per [estimation-and-status.md](../references/estimation-and-status.md).
- **Dual-running means comparison, not coexistence**: while old and new paths both run, *diff their outputs* on real traffic/data — that's the strongest verification a migration ever gets. Silent dual-running wastes the one period where wrongness is directly observable.
- **No new features mid-migration** in the migrating surface — every concurrent change extends the diff between old and new and muddies the comparison. Queue them for after contract.

## Phase 3 — The contract step and the cleanup

The migration isn't done when the new thing works — it's done when the old thing is *gone*:

- **Prove zero usage before removal**: logs/metrics on the old path over a real usage cycle (a week that includes the monthly job, not a quiet Tuesday). The verification check from Phase 0 runs here.
- **Remove the scaffolding**: dual-write code, compatibility shims, feature flags, the migration script's temp tables. Scaffolding left "just in case" becomes permanent mystery infrastructure within a quarter.
- **Update everything that described the old world**: docs, runbooks, examples, onboarding material ([writing-and-docs.md](writing-and-docs.md)) — a migration that leaves the docs describing state A has manufactured future confusion.
- **The closing report**: inventory count vs. migrated count (they match, or the gap is explained), what was verified and how, what was removed, and the deliberate leftovers with their reasons and removal dates.

## Anti-patterns

- **The big bang.** Everything cut over in one unrescuable step because incremental "takes longer." It takes longer the way seatbelts slow the trip.
- **The estimated inventory.** "Roughly 30 sites" — the migration plan's foundation, guessed. Count, don't estimate; grep is free.
- **The eternal dual-write.** Expand executed, contract never scheduled; two systems of record drift apart and *both* are now wrong.
- **The quiet cliff.** The irreversible step buried mid-sequence as item 7 of 12, executed on autopilot.
- **The unrestored backup.** A backup trusted because the job succeeded, discovered corrupt at the only moment it's needed.
- **The 95% migration.** The last stragglers left "for later"; the compatibility shim outlives everyone who remembers why it exists.
