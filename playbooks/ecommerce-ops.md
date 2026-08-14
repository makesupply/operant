# Playbook: Ecommerce Operations

**Goal:** change store state safely — read the current state before mutating, stage before publishing, and gate every money-moving or bulk action behind an exact-scope confirmation with its blast radius stated. A store is a live system with real customers and real spend; the difference between a routine edit and an incident is whether you knew the current numbers before you touched them.

## Phase 0 — Orient before you touch anything

- **Identify the system of record.** Where does truth live — the storefront platform, the ad platform, a separate inventory or ERP system? A price shown in a report is a copy; the price that charges customers lives in one place, and that place is the only one worth confirming against.
- **Read current state before any mutation**: the live prices, the on-hand stock, the active campaigns and their budgets, the open order queue. "Set the price to $29" needs the current price first — you cannot confirm scope, reconcile a delta, or notice a fat-finger without the before-value in hand.
- **Know what is live versus draft.** A draft listing, a paused campaign, and a staged price change touch no customer and no dollar. A published listing, an active campaign, and a live price do. Establish which state every object is in before you plan the change; the tier of the action depends on it.
- **Establish scope from the data, not the phrasing.** "Update the summer collection" is a sentence; the collection is 340 SKUs or 3,400, and you find out by querying, not by guessing. Count the affected set before you act on it ([safety.md](../references/safety.md)).

## Phase 1 — Map reversibility before you plan the change

Sort every intended action by what it costs to undo ([safety.md](../references/safety.md)):

- **Reversible — proceed and report.** Drafting a listing, staging a price change, building a performance report, previewing an audience or segment, running a dry-run export. These touch no customer and move no money; treat them as Tier 0–1 and do them freely.
- **Tier 3 — confirm first, every time.** Publishing price changes to the live storefront, bulk-editing or deleting products, launching or raising paid-ad budgets, pushing any change to the live storefront, fulfilling / cancelling / refunding orders, and emailing customer lists. Each is outward-facing, money-moving, or destructive — often all three.
- **The tier is set by the worst plausible outcome, not the intended one.** A single price edit that a pricing rule cascades across a whole catalog is Tier 3, not Tier 0. When you can't tell whether a change stays local, assume it doesn't.
- **Lower the cost to undo first, when it's cheap.** Stage the price change and preview it before publishing; export the current catalog before a bulk edit; duplicate a campaign into a paused state before touching the live one. A two-minute export that turns a bulk overwrite into a recoverable one is the correct implementation of the edit, not optional caution.

## Phase 2 — State the blast radius, then confirm on the numbers

Before any bulk or money-moving action, state the exact scope and confirm with those numbers in the request ([communication.md](../references/communication.md)):

- **Name the count and the delta.** "This changes price on 3,412 SKUs, average −18%." "This raises daily ad spend from $200 to $500 across 4 campaigns." "This emails 12,840 customers." Not "update prices," not "scale up spend," not "notify the list."
- **The confirmation must let the user veto without trusting you** ([safety.md](../references/safety.md)): the exact entities, the exact numbers, what changes in the world, and what happens if they say no. Approval for one bulk action does not extend to the next — re-confirm each Tier 3 action unless the user wrote down a standing authorization.
- **Canary before the fleet.** Apply the change to one product, one campaign, one order first; verify it landed as intended; then run the batch. A bulk operation validated on a sample of one is a bulk operation you can trust.

## Phase 3 — Execute with idempotency and the retry-after-side-effect rule

- **Never blindly re-run a partially-failed bulk operation.** A bulk price push that errors at row 900 of 3,412 may have applied the first 899. Re-running from the top re-applies them — and if the action moves money (a budget raise, a charge, a fulfillment), the retry double-charges or double-publishes ([safety.md](../references/safety.md)).
- **After a partial failure, read state before retrying.** Query what actually applied, compute the remaining set, and act only on the unapplied remainder. The question is never "did the call return an error" — it's "what did the world commit before it errored."
- **Prefer operations that carry their own idempotency**: an upload keyed by SKU that upserts, a batch with a client-side idempotency token, an API that reports per-row success. Where the platform offers no such guarantee, you supply it — track applied IDs yourself and diff against them on retry.
- **One in-flight bulk mutation at a time.** Concurrent budget raises or overlapping catalog pushes race, and the losing write is silent.

## Phase 4 — Reconcile the delta against intent

- **Capture totals before and after.** Record the pre-change count and aggregate (SKUs affected, total list value, sum of daily budgets, orders in the queue) before acting, and the same totals after. The change is verified only when the observed delta matches the intended one ([data-work.md](data-work.md)).
- **A delta that doesn't match is a stop sign.** You meant to reprice 3,412 SKUs and 3,600 changed — a pricing rule caught more than you scoped. Halt and surface it; do not smooth it over ([safety.md](../references/safety.md)).
- **Reconcile money moves explicitly.** Daily spend went from $200 to $500 as intended, not $200 to $1,500 because a budget applied per-adgroup instead of per-campaign. Confirm the live figure in the system of record, not the value you submitted.

## Phase 5 — Report performance honestly

- **Answer first, precision matched to reliability** ([data-work.md](data-work.md)): "ROAS ~3.1x (±0.3, attribution window unsettled)" beats a false-precise "3.14x" the pipeline can't support. Every comparison carries its baseline and denominator — "+50% conversions, but n=6" gets the caveat inline.
- **Attribution is a modeling choice, not a fact.** State the window and model; the same campaign is profitable or not depending on 1-day versus 7-day, last-click versus view-through. The methodology footnote — source, date range, attribution basis, known exclusions — is not optional.
- **Never present platform-reported conversions as ground truth** without noting they are the platform's self-graded homework. Anchor against the store's own order data where you can.

## Anti-patterns

- **The bulk-apply-then-blind-retry double charge.** *Tell:* a batch errored partway and the fix was to run the whole thing again. *Fix:* read what committed before the error; act only on the unapplied remainder; prefer idempotent upserts.
- **The live-price fat-finger.** *Tell:* a price published to the live storefront with no statement of how many SKUs it touched or what the before-values were. *Fix:* read current prices, state the count and the delta, confirm on those numbers, stage before publish.
- **The unbounded ad budget.** *Tell:* a budget raised without a stated ceiling, or an auto-scaling rule with no cap. *Fix:* every budget change names the exact new daily and lifetime figure; no open-ended "scale until it works."
- **The "test" on a live paying account.** *Tell:* a trial campaign launched against the real ad account "just to see." *Fix:* there is no test post to a live account — it spends real money and publishes to real feeds. Use draft/paused state, sandboxes, or explicit confirmation of the real spend.
- **The blind inventory overwrite.** *Tell:* stock levels set to absolute values without reading current on-hand first. *Fix:* read current stock, compute the intended delta, reconcile after — an overwrite that never read the current count silently erases real inventory movement.
- **The delete of products you didn't create.** *Tell:* removing listings, campaigns, or records this session didn't author, on the assumption they're junk. *Fix:* read the target's contents and check provenance; someone values it until proven otherwise; archive or unpublish before hard-delete.
