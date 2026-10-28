# Playbook: Ecommerce Operations
*Read when: changing storefront state such as prices, listings, inventory, orders, or discounts, or reporting on store performance.*

**Goal:** change store state safely. Read the current state before mutating, stage before publishing, and gate every money-moving or bulk action behind an exact-scope confirmation. The difference between a routine edit and an incident is whether you knew the current numbers before you touched them. Writes to ad, email, and social platforms follow [account-and-platform-writes.md](account-and-platform-writes.md); this playbook owns the storefront.

## Phase 0: Orient before you touch anything

- **Identify the system of record.** A price shown in a report is a copy; the price that charges customers lives in one place, the only one worth confirming against.
- **Read current state before any mutation**: live prices, on-hand stock, the open order queue, the active discounts. You cannot confirm scope, reconcile a delta, or notice a fat-finger without the before-value in hand.
- **Know what is live and what is draft.** A draft listing and a staged price change touch no customer and no dollar. A published listing and a live price do. Establish which state every object is in; the tier depends on it.
- **Establish scope from the data, not the phrasing.** "Update the summer collection" is a sentence; the collection is 340 SKUs or 3,400, and you find out by querying. Count the affected set before you act on it.

## Phase 1: Map reversibility before you plan the change

Sort every intended action by what it costs to undo, per [safety.md](../references/safety.md).

- **Tier 0 to 1, meaning reversible and invisible to customers: proceed and report.** Drafting a listing, staging a price change, building a report, previewing a segment, running a dry-run export.
- **Tier 3: confirm first, every time.** Publishing price changes, bulk-editing or deleting products, pushing any change to the live theme, fulfilling or cancelling or refunding orders, and emailing customer lists.
- **The tier is set by the worst plausible outcome.** A single price edit that a pricing rule cascades across a catalog is Tier 3. When you cannot tell whether a change stays local, assume it does not.
- **Lower the cost to undo first, when it is cheap.** Stage and preview before publishing; export the current catalog before a bulk edit. A two-minute export that makes a bulk overwrite recoverable is the correct implementation of the edit.

## Phase 2: State the blast radius, then confirm on the numbers

The confirmation payload is defined once in [account-and-platform-writes.md](account-and-platform-writes.md) § The confirmation payload. A storefront write adds the count and the delta in one sentence, such as "this changes price on 3,412 SKUs, average minus 18 percent" or "this emails 12,840 customers," and names the canary: apply the change to one product or one order first, verify it landed, then run the batch. Approval for one bulk action does not extend to the next.

## Phase 3: Execute with idempotency and the retry-after-side-effect rule

- **Never blindly re-run a partially failed bulk operation.** A price push that errors at row 900 of 3,412 may have applied the first 899. Re-running from the top re-applies them, and if the action moves money, the retry double-charges.
- **After a partial failure, read state before retrying.** Query what applied, compute the remaining set, and act only on the unapplied remainder. The question is never "did the call return an error" but "what did the world commit before it errored."
- **Prefer operations that carry their own idempotency**: an upsert keyed by SKU, a batch with a client-side idempotency token, an API that reports per-row success. Where the platform offers none, track applied IDs yourself and diff against them on retry.
- **One in-flight bulk mutation at a time.** Overlapping pushes race, and the losing write is silent.

## Phase 4: Reconcile the delta against intent

Record the pre-change count and aggregate, such as SKUs affected, total list value, or orders in the queue, and the same totals after. The change is verified only when the observed delta matches the intended one. A delta that does not match is a stop sign: you meant to reprice 3,412 SKUs and 3,600 changed, so a rule caught more than you scoped. Halt and surface it. Confirm the live figure in the system of record, not the value you submitted.

## Phase 5: Report performance honestly

Performance reporting follows [data-work.md](data-work.md). Two rules are specific to stores. Attribution is a modelling choice, not a fact: state the window and the model, because the same campaign is profitable or not depending on a one-day or seven-day window and last-click or view-through. And platform-reported conversions are the platform's self-graded homework; anchor against the store's own order data wherever you can.

## Exit criteria

- [ ] The before-state of every entity was read and recorded before any mutation.
- [ ] The affected set was counted from the data, not estimated from the phrasing.
- [ ] Every Tier 3 action was confirmed with the payload plus count, delta, and canary.
- [ ] A partial failure was handled by reading state and acting on the remainder only.
- [ ] The observed delta matches the intended delta in the system of record.
- [ ] Any performance figure states its attribution window and model and is anchored to store order data.

## Anti-patterns

- **The blind retry.** *Tell:* a batch errored partway and was run again from the top. *Fix:* read what committed; act only on the remainder.
- **The live-price fat-finger.** *Tell:* a price published with no count and no before-values. *Fix:* read, count, state the delta, confirm, stage before publish.
- **The "test" on the live store.** *Tell:* a change pushed live "just to see." *Fix:* draft, staged, or sandbox state; there is no test on a live storefront.
- **The delete of what you did not create.** *Tell:* listings removed on the assumption they are junk. *Fix:* read the target and check provenance; archive or unpublish before deleting.
