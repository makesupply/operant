# Playbook: Account and Platform Writes
*Read when: you are about to write to an ad account, a storefront, a messaging platform, or any live system others depend on.*

**Goal:** every platform write is confirmed on exact entities and numbers, executed once, and read back.

## Phase 0: Orient

Read the current state of every entity you will change and record it with the source and time of the read. Resolve every name to an identifier. Classify the call as reversible, like a pause, or not, like a publish, send, budget raise, or delete. Confirm the account and environment the credentials resolve to by reading an identity endpoint.

## Phase 1: Verified increments

Build the payload below, present it, and wait for the yes; a yes approves the payload shown and nothing else. Execute one entity first as the canary and read it back; then run the rest, one in-flight mutation at a time. A timeout or an ambiguous error means unknown state; read before retrying.

## Phase 2: Adversarial self-check

After each write, read the entity back and compare every changed field to the payload. For anything hierarchical, confirm every level is live and the leaf is delivering or spending. Compare the delta to the confirmed scope; a larger delta is a stop.

## Phase 3: Honest report

Report before and after per entity, with identifiers and the read-back as evidence. Report anything not read back as unverified. Name the undo path or say there is none.

## The confirmation payload

Every playbook that sends, publishes, or writes to a platform points here and adds only its domain lines. Use [external-send-confirmation.schema.json](../schemas/external-send-confirmation.schema.json) for anything that reaches a recipient or a feed and [destructive-action-confirmation.schema.json](../schemas/destructive-action-confirmation.schema.json) for anything that deletes, overwrites, or changes production. The gate in [generic-policy-spec.md](../enforcement/generic-policy-spec.md) parses the same shape.

- **What, verbatim.** The exact operation, or the rendered content as it will arrive. Schema: `action`, `rendered_content`.
- **To whom.** Resolved recipients or entities with identifiers, and the live count as queried. Schema: `recipients.resolved`, `recipients.count`, `target.identity`, `target.count`.
- **From which account.** The account and environment the credentials resolved to.
- **When.** Now, or an absolute scheduled time.
- **Each field, before and after.** As read and as intended.
- **Money, before and after.** Daily and lifetime figures and the ceiling.
- **Reach, where it applies.** Subscribers, a public post, one vendor. Schema: `reach`.
- **What happens on no.** The state that stays as it is.
- **Undo path, or none.** Schema: `reversible`, `recoverable`.
- **Evidence.** The source and time of every value read back from the live system, and the name of any value that came from reasoning instead. Show it before the recommendation; a confident explanation is not evidence.

The schemas also require `channel`, `blast_radius`, `consequence`, and `looked_at_target`; fill them, and set `description_mismatch` when the target differs from its description. Authorization is single-use.

## Exit criteria

- [ ] Before-state recorded with source and time.
- [ ] The payload was shown and the yes named it.
- [ ] A canary ran and was read back before the batch.
- [ ] Every write was read back and the report separates verified from unverified.

## Anti-patterns

**The name-only confirmation.** *Tell:* "pause the summer campaign" confirmed with no identifier or count. *Fix:* resolve the ID and query the count.
**The double bump.** *Tell:* a budget raised twice after a timeout. *Fix:* read state before any retry.
**The top level enabled with zero spend.** *Tell:* the campaign shows active and the ad set is paused. *Fix:* read every level to the leaf.
**The carried-over approval.** *Tell:* a second write ran on the yes given for the first. *Fix:* one payload, one yes, one write.
**The typed value.** *Tell:* a count or amount in the payload came from reasoning. *Fix:* every value cites its read.
