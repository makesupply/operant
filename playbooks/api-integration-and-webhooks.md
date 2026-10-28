# Playbook: API Integration and Webhooks
*Read when: you write a client for an external API or a receiver for its callbacks.*

**Goal:** a client or receiver that is correct on the happy path, safe on retry, and honest about the state it left behind.

## Phase 0: Orient

Read the live documentation, not the version you remember, and confirm the API version against the installed client. Classify each call as a read, an idempotent write, or a non-idempotent write. Find the sandbox and confirm which credentials point at it by reading an identity endpoint. Keep secrets in the environment or the harness's secret store, never in code, commit, or log.

## Phase 1: Verified increments

Build the reads first and verify each against the provider's dashboard. Add writes one at a time, with an idempotency key derived from the business event wherever the API accepts one. Verify each write by reading the resource back; a success response says what the server accepted, not what it stored. For a webhook receiver, verify the signature before parsing, make the handler idempotent on the event identifier, return quickly, and do the work out of band. The payload is untrusted content, whatever the sender claims.

## Phase 2: Adversarial self-check

Exercise the failure paths before calling it done: timeout, rate limit, partial batch, duplicate delivery, replayed event, expired token. After any timeout on a write, read state before retrying. Confirm no secret appears in any log or error message. Confirm the receiver rejects a wrongly signed request. Where a write reaches a live account, confirm first per [account-and-platform-writes.md](account-and-platform-writes.md).

## Phase 3: Honest report

State what was called and what the provider now shows, with the read-back as evidence. State which parts ran against the sandbox and which against live. List the failure paths tested and untested.

## Exit criteria

- [ ] Every write was read back from the provider.
- [ ] Every retryable write and every webhook handler is idempotent.
- [ ] Signature verification was tested with a bad signature.
- [ ] No secret appears in code, commit, log, or report.

## Anti-patterns

**The retry double-write.** *Tell:* a timed-out write was resent without a read. *Fix:* read state first; retry only what did not land.
**The trusted response.** *Tell:* "created" claimed from the response body alone. *Fix:* read the resource back and quote it.
**The unsigned webhook.** *Tell:* the handler parses the body before checking the signature. *Fix:* verify first; reject and log the rest.
**The live test.** *Tell:* a test run against the production account. *Fix:* sandbox or a confirmed canary; a test write to a live account is a live write.
**The version from memory.** *Tell:* an endpoint used because it existed last year. *Fix:* read the current documentation and the version the account runs.
