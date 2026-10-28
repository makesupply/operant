# Example: The Handoff Document

A handoff document lets a fresh session or another agent resume a half-finished task from the document and the disk alone, without this conversation. The shape is defined in [concurrency-and-handoffs.md](../references/concurrency-and-handoffs.md) § Handing off. [multi-session-and-handoff.md](../playbooks/multi-session-and-handoff.md) says when to write one, and the session-end gate in [session-end.md](../checklists/session-end.md) asks whether it was written.

Three rules shape every section. Reference what already exists by path, URL, commit hash, or ID, and never restate it, because a restated artifact drifts from its source. Redact every secret, token, and personal identifier, because the document becomes a prompt. Save it where the harness keeps session files, never loose in the repository.

Tailor it to what the next session will do, not to everything this one did. The test of a good handoff: a new agent resumes using only this document and what is on disk.

## Template

```markdown
# Handoff: <task name> (<YYYY-MM-DD>)

## Goal, in the user's words
<the request verbatim, then the constraints the user stated>

## Done and verified
- <item> · evidence: <command run, result seen, commit hash or file path>

## Done, not verified
- <item> · why unverified: <reason> · how to verify: <command or observation>

## In progress
<exactly one item, with its exact state: which file, which step, what the last command returned, what is committed and what is not>

## Next three steps
1. <the step you would take next>
2. <the step after that>
3. <the step after that>

## Decisions and rulings
- <decision> · why: <reason> · cost if wrong: <one phrase> · <YYYY-MM-DD>

## Open questions
- <question> · owner: <user, next session, or a named team>

## Gotchas
- <non-obvious fact that cost time, with how to apply it>

## Load first
- <playbook, skill, or project note, by path>

## References
- <spec, plan, tracker row, diff, decision record: path or ID only, never restated>
```

## Filled example: a half-finished API client migration

```markdown
# Handoff: Payments client migration to SDK v2 (2026-10-28)

## Goal, in the user's words
"Move the payments client off the v1 REST SDK onto v2 before the v1 shutdown on 2026-11-15. Keep the public interface of our wrapper unchanged so the checkout service does not need a release."

Constraints stated: no change to the wrapper's public interface; no new runtime dependency beyond the v2 SDK; the sandbox account only, never the live account, until the user says otherwise.

## Done and verified
- Charges and refunds moved to v2 · evidence: `pytest tests/payments -k "charge or refund"` after the last change, 48 passed, 0 failed, exit 0 · commit a41c9e2
- Wrapper public interface unchanged · evidence: `scripts/api-diff.sh payments-v1-baseline HEAD` reports no signature changes · commit a41c9e2
- Sandbox round trip for one charge and its refund · evidence: the sandbox dashboard shows charge ch_test_7Qk and refund re_test_2Lm, both succeeded, viewed 2026-10-28 15:40

## Done, not verified
- Webhook signature verification rewritten for the v2 header format · why unverified: the sandbox has not delivered a webhook since the change, so the new parser has only run against the SDK's example payload · how to verify: trigger a sandbox refund and watch `logs/webhooks.log` for a `signature ok` line

## In progress
Idempotency keys for retried charges. `src/payments/client.py` has the key generator written and unit-tested. The v2 charge call at line 212 does not yet pass the key. The last run of `pytest tests/payments -k idempot` fails 2 of 5 with "idempotency_key missing". Nothing is committed for this item.

## Next three steps
1. Pass the idempotency key on the v2 charge call, make the 2 failing tests pass, commit.
2. Trigger a sandbox refund and verify the webhook parser on a real delivery, as listed under Done, not verified.
3. Run the full suite, update `CHANGELOG.md`, and write the final report with the command outputs.

## Decisions and rulings
- Keep the wrapper's own retry loop and do not adopt the SDK's built-in retry · why: the SDK retries on timeouts, which would double-charge without idempotency keys · cost if wrong: one redundant retry layer, removable later · 2026-10-28
- Ruling: skipped the SDK's recommended migration script · why: it rewrites import paths across the whole repo, outside the stated scope · cost if wrong: manual import fixes in two modules · 2026-10-28

## Open questions
- Does the live account have the v2 webhook endpoint registered? · owner: user, who holds the live dashboard
- Should the v1 fallback path stay until 2026-11-15 or be removed now? · owner: user

## Gotchas
- The v2 SDK reads the API key from an environment variable with a different name than v1. Both names are listed in `.env.example`. The real values live in the secret manager and appear in no file this handoff references.
- `tests/payments/conftest.py` pins the sandbox base URL. Running the SDK's own examples outside that fixture hits the live base URL by default. Do not run them.

## Load first
- `playbooks/api-integration-and-webhooks.md`
- `playbooks/migrations.md`
- the project's operating doc, section on payments

## References
- Migration plan: `docs/plans/payments-v2.md`
- Interface baseline for the diff: git tag `payments-v1-baseline`
- Tracker row: PAY-212
```

What the example shows. Every verified item carries the command and the result, so the next agent can re-run it instead of trusting it. The unverified item says how to verify it. The in-progress section has one item with its exact state, including what is not committed. The secret is named by where it lives, not by its value. Nothing that lives in the plan, the tag, or the tracker row is restated.
