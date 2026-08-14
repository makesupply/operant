# Threat Model — How Agent Operation Gets Attacked, and Which Layer Answers

An operating agent sits on a trust boundary. It holds authority the authors of the content it reads do not have: tools, credentials in proximity, the ability to send, delete, spend, and write to systems other people depend on. The content it processes — a web page, a file, an email, a tool result — was written by someone who wants that authority and cannot reach it directly. Every threat below is a way to close that gap: to make the agent misuse the authority it holds on behalf of an author who holds none.

The governing rule follows from that asymmetry. **For anything high-severity, the defense must be structural — enforced in code or by the harness, not by the agent's judgment.** A behavioral defense is an instruction the agent chooses to follow; it fails exactly when an adversary is trying hardest to make it fail. Structural defenses — a command gate that blocks a pattern, an external-send gate that shows the payload, a permission the harness will not grant — do not weaken under pressure because they are not the agent's to relax. Behavior catches the reflexive miss; code catches the determined attacker. Operant assigns each defense an owning layer: **PROMPT** (behavior in instructions), **RETRIEVAL** (depth loaded on match), **HARNESS_POLICY** (permissions, approvals, tool-routing the host enforces), **CODE_GUARD** (deterministic checks — command gates, secret and PII scanners, outward-send gates), and **EVAL_ONLY** (testable but hard to enforce live).

## The threat classes

**1. Prompt injection via untrusted content.**
- *The attack:* instructions embedded in fetched content — "ignore your previous instructions," "run this command," "send X to Y" — planted in a page, file, email, or tool result the agent reads.
- *The tell:* imperative text inside data, addressed to the agent rather than the human reader; content that "asks" the agent to change its task, exfiltrate, or follow a link.
- *The primary defense:* treat everything read from outside the user's direct messages as data, wrapped in a "this is not instructions" frame; delimit fetched content structurally so it cannot be confused with the instruction channel; detect injection attempts and **report** them rather than silently comply ([security-posture.md](security-posture.md)).
- *Owner:* PROMPT (the frame) + CODE_GUARD (delimiting) + EVAL_ONLY (injection-resistance test).

**2. Confused deputy / tool-authority abuse.**
- *The attack:* content that cannot use the agent's privileged tools tries to make the agent use them on its behalf — the classic confused deputy, where the trusted party acts on an untrusted party's request.
- *The tell:* fetched content that names a tool, an action, or a destination and supplies parameters for it; a request whose real beneficiary is the author of the content, not the user.
- *The primary defense:* the agent's authority is scoped by the operator, never by content; outward-facing and destructive tools sit behind gates whose conditions content cannot satisfy from inside the data channel.
- *Owner:* HARNESS_POLICY (scope, tool routing) + CODE_GUARD (the gates).

**3. Data exfiltration / oversharing.**
- *The attack:* secrets, personal data, or internal context crosses the trust boundary through a send, a log line, or an output.
- *The tell:* a payload bound for an external recipient that contains credentials, PII, or internal context; a "debug print" of a token; a report pasting raw records ([safety.md](safety.md)).
- *The primary defense:* secret and output scanners on outbound paths, data minimization by default, and an external-send gate that surfaces the exact payload and recipient before anything leaves.
- *Owner:* CODE_GUARD (scanners, send gate) + HARNESS_POLICY (send approvals).

**4. Destructive action via mis-scoped command.**
- *The attack:* an over-broad delete, reset, drop, or force operation — the right verb aimed at far too wide a target.
- *The tell:* a command with recursive or wildcard reach, a `reset --hard` or `drop` on state the agent did not create, a target whose blast radius exceeds the stated task.
- *The primary defense:* the Tier-3 command gate blocks catastrophic patterns deterministically; the look-before-you-destroy discipline reads the target and checks provenance before acting ([safety.md](safety.md)).
- *Owner:* CODE_GUARD (the command gate) + PROMPT (look-before-destroy).

**5. Duplicate / replayed side effects.**
- *The attack:* a retry after a partial failure re-sends a message, re-charges a card, or re-writes a record — the failure was in the response path, not the action, so the action runs twice.
- *The tell:* an error after a side-effecting call where success is ambiguous; a loop that re-issues a send or write without checking what already landed.
- *The primary defense:* idempotency keys on side-effecting operations and the retry-after-side-effect rule — before re-running, check what already happened.
- *Owner:* CODE_GUARD (idempotency) + PROMPT (retry discipline).

**6. Supply-chain / dependency trust.**
- *The attack:* a fetched package, an installed tool, or a connected MCP server is hostile — a typosquat, a poisoned update, or a server whose tool descriptions carry injection.
- *The tell:* a new dependency with a look-alike name, a tool whose output steers behavior, an install script piped from the network.
- *The primary defense:* least privilege for every tool and server, pinned and reviewed dependencies, and treating third-party tool output as untrusted data on the same footing as any fetched content.
- *Owner:* HARNESS_POLICY.

**7. Over-trust of tool output as ground truth.**
- *The attack:* the agent treats a tool or API result as verified fact and takes a state-changing action on it, when the result was wrong, stale, or attacker-shaped.
- *The tell:* a load-bearing decision resting on a single unverified read; acting on a lookup as if it were confirmation.
- *The primary defense:* match evidence to action (Principle 7) — corroborate load-bearing tool output before any state change, and scale the verification to the cost of being wrong.
- *Owner:* PROMPT + EVAL_ONLY.

## Residual risk

No single layer is complete, and this model does not pretend otherwise. Behavioral discipline can be worn down; code guards can be under-scoped; evals can miss a class they were never written to cover. Operant's answer is defense in depth: behavioral rules catch the reflexive miss, code and harness guards catch the determined adversary who defeats the behavior, and evals catch the regression that quietly reopens a closed door. When a high-severity defense lives only in the prompt, that is the finding — promote it to CODE_GUARD or HARNESS_POLICY. See [security-posture.md](security-posture.md) for the posture these threats attack, and [generic-policy-spec.md](../enforcement/generic-policy-spec.md) for how the owning layers are specified and enforced.
