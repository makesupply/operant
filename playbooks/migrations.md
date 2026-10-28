# Playbook: Migrations
*Read when: moving from state A to state B across a schema, API, platform, framework, or data store without losing anything or being stranded mid-way.*

**Goal:** move from state A to state B without losing anything and without a moment where things are broken and unrescuable. Migrations combine refactoring's drift risk with operations' irreversibility risk; the playbook is mostly about never being stranded in the middle. The same shape serves a framework or vendor migration: the inventory is call sites and integrations rather than rows, the expand step is the adapter that lets both run, and the contract step is the removal of the old one.

## Phase 0: Inventory before itinerary

- **Enumerate everything that must move, mechanically.** Grep, query, scan; do not estimate. "About 30 call sites" becomes exactly 47, including the three in the cron scripts nobody remembers. Every missed item is a production surprise scheduled for later.
- **Find the consumers you do not own**: external API clients, downstream jobs reading the table, dashboards parsing the export, the partner integration. The things you cannot update on your schedule define the migration's real shape and usually force a compatibility window.
- **Classify each item**: mechanically transformable, individually reviewable, and unknown. The ratio decides whether this is an afternoon or a quarter; report that sizing before starting, per [estimation-and-status.md](../references/estimation-and-status.md).
- **Define done and verified done.** Not "the script ran" but "zero references to the old form remain, all consumers on the new path, old path removed." Write the verification query now; it is your finish-line detector.

## Phase 1: Design for reversibility at every step

The cardinal rule: at every intermediate point the system works and you can retreat.

- **Expand, migrate, contract.** Add the new alongside the old, move consumers over incrementally in small testable steps, and remove the old only when verifiably unused. Contract is the only irreversible phase; do it last, when it is boring.
- **Expand is only safe at your scale if you check.** On large tables the additive step itself can be the outage: a column with a default on older engines, an index built without the concurrent option, an unthrottled backfill. Know your engine's locking behavior for the specific statement, throttle backfills, and rehearse anything table-shaped on a production-scale copy.
- **Never modify in place when add-alongside is possible.** Renaming a column in place is a cliff; adding the new column, dual-writing, backfilling, switching readers, then dropping is a staircase.
- **Schedule the point of no return.** Identify exactly which step is irreversible and gate it behind explicit confirmation, per [safety.md](../references/safety.md), plus the verification that nothing still depends on what is being removed.
- **Verify the backup before the irreversible step.** Verified means restored once, not "the backup job said OK." When a full restore is infeasible, degrade explicitly: restore a sample to scratch, spot-check point-in-time recovery, or cite the provider's attestation, and state which level you got.

## Phase 2: Execute in ratcheting increments

- **Canary first, always.** One call site, one table, one service through the new path, verified end to end, before the fleet.
- **Batch the mechanical, review the exceptional.** Scripted transforms with spot-checks per batch for the mechanical items; individual attention for the hand-work list.
- **Keep the ratchet visible**: a running count against the Phase 0 inventory, such as "312 of 347 call sites migrated; remaining: 3 cron scripts and 32 in the deprecated admin panel." That is also your status report.
- **Dual-running means comparison.** While old and new paths both run, diff their outputs on real data. That is the strongest verification a migration ever gets; silent dual-running wastes it.
- **No new features mid-migration** in the migrating surface. Every concurrent change muddies the comparison.

## Phase 3: Contract and clean up

The migration is done when the old thing is gone. Prove zero usage before removal with logs or metrics over a real usage cycle, a week that includes the monthly job rather than a quiet Tuesday, and run the Phase 0 verification check. Remove the scaffolding: dual-write code, compatibility shims, feature flags, temp tables. Update everything that described the old world, per [writing-and-docs.md](writing-and-docs.md). The closing report gives inventory count against migrated count, what was verified and how, what was removed, and the deliberate leftovers with reasons and removal dates.

## Exit criteria

- [ ] The inventory was counted mechanically, consumers outside your control included.
- [ ] The verification check was written before the first step.
- [ ] Every intermediate state was working and retreatable.
- [ ] The backup was restored once, or the degraded check is named.
- [ ] The irreversible step was confirmed explicitly after proving zero usage over a real cycle.
- [ ] Inventory count equals migrated count, or the gap is explained.
- [ ] Scaffolding removed and docs updated.

## Anti-patterns

- **The big bang.** *Tell:* everything cut over in one unrescuable step. *Fix:* expand, migrate, contract.
- **The estimated inventory.** *Tell:* "roughly 30 sites." *Fix:* count; grep is free.
- **The eternal dual-write.** *Tell:* expand executed, contract never scheduled. *Fix:* schedule contract with its verification check.
- **The quiet cliff.** *Tell:* the irreversible step buried as item 7 of 12. *Fix:* name it and gate it.
- **The unrestored backup.** *Tell:* a backup trusted because the job succeeded. *Fix:* restore once before the drop.
- **The 95 percent migration.** *Tell:* stragglers left for later; the shim outlives everyone who remembers it. *Fix:* the ratchet count reaches the inventory, or the gap has a date.
- **The locking expand.** *Tell:* the "additive" column took the primary down. *Fix:* rehearse the statement at production scale.
