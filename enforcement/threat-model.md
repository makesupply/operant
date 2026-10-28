# Threat Model (enforcement design): which layer answers each attack

This document is for whoever builds the gates. It names the attack classes on an operating agent, the layer that must answer each, and how the OWASP Top 10 for Agentic Applications maps onto them. The agent-facing tells, meaning what the agent does when it meets one of these inside the data channel, live in [../references/security-posture.md](../references/security-posture.md) under "Recognizing an attack". Gate numbers G1 to G10 refer to [generic-policy-spec.md](generic-policy-spec.md).

An operating agent sits on a trust boundary. It holds authority the authors of the content it reads do not have: tools, credentials in proximity, the ability to send, delete, spend, and write to systems other people depend on. The content it processes was written by someone who wants that authority and cannot reach it directly: a web page, a file, an email, a tool result, another agent's report. Every threat below is a way to close that gap and make the agent misuse the authority it holds on behalf of an author who holds none.

The governing rule follows from that asymmetry. For anything high-severity, the defense must be structural, enforced in code or by the harness rather than by the agent's judgment. A behavioral defense is an instruction the agent chooses to follow; it fails exactly when an adversary is trying hardest to make it fail. Structural defenses do not weaken under pressure because they are not the agent's to relax: a command gate that blocks a pattern, an external-send gate that shows the payload, a permission the harness will not grant. Behavior catches the reflexive miss; code catches the determined attacker.

## The owning layers

- **PROMPT**: behavior in instructions.
- **RETRIEVAL**: depth loaded on match.
- **HARNESS_POLICY**: permissions, approvals, and tool routing the host enforces.
- **CODE_GUARD**: deterministic checks, meaning command gates, secret and PII scanners, outward-send gates, and inbox verifiers.
- **EVAL_ONLY**: testable but hard to enforce live.

## The threat classes

**1. Prompt injection via untrusted content.**
- *The attack:* instructions embedded in fetched content, such as "ignore your previous instructions", "run this command", or "send X to Y", planted in a page, file, email, or tool result the agent reads. The structural variant imitates the instruction channel itself: model control tokens, fake system or role markers, directives in comments, fake prior agreement, "from now on" redefinitions, false authority, audit suppression, and hidden characters that defeat pattern matching.
- *The tell:* imperative text inside data, addressed to the agent rather than the human reader; content that asks the agent to change its task, exfiltrate, or follow a link; a run of invisible characters.
- *The primary defense:* treat everything read from outside the user's direct messages as data inside a "this is not instructions" frame; delimit fetched content structurally; normalize text before any pattern runs; detect attempts and report them rather than silently comply.
- *Owner:* PROMPT (the frame) + CODE_GUARD (G8: delimiting, normalization, structural-marker patterns) + EVAL_ONLY (injection-resistance test).

**2. Confused deputy and tool-authority abuse.**
- *The attack:* content that cannot use the agent's privileged tools tries to make the agent use them on its behalf. The trusted party acts on an untrusted party's request.
- *The tell:* fetched content that names a tool, an action, or a destination and supplies parameters for it; a request whose real beneficiary is the author of the content, not the user.
- *The primary defense:* the agent's authority is scoped by the operator, never by content; outward-facing and destructive tools sit behind gates whose conditions content cannot satisfy from inside the data channel.
- *Owner:* HARNESS_POLICY (scope, tool routing) + CODE_GUARD (G1, G3, G4, G5).

**3. Data exfiltration and oversharing.**
- *The attack:* secrets, personal data, or internal context crosses the trust boundary through a send, a log line, or an output.
- *The tell:* a payload bound for an external recipient that contains credentials, personal data, or internal context; a debug print of a token; a report pasting raw records.
- *The primary defense:* secret and output scanners on outbound paths, data minimization by default, an external-send gate that surfaces the exact payload and recipient before anything leaves, and deny rules on known paste and webhook hosts.
- *Owner:* CODE_GUARD (G4, G6, G7) + HARNESS_POLICY (send approvals, fetch deny list).

**4. Destructive action via mis-scoped command.**
- *The attack:* an over-broad delete, reset, drop, or force operation. The right verb aimed at far too wide a target.
- *The tell:* a command with recursive or wildcard reach; a `reset --hard` or `drop` on state the agent did not create; a target whose blast radius exceeds the stated task.
- *The primary defense:* the destructive-command gate blocks catastrophic patterns deterministically; the look-before-you-destroy discipline reads the target and checks provenance before acting ([../references/safety.md](../references/safety.md)).
- *Owner:* CODE_GUARD (G1, G2, G3) + PROMPT (look before you destroy).

**5. Duplicate and replayed side effects.**
- *The attack:* a retry after a partial failure re-sends a message, re-charges a card, or re-writes a record. The failure was in the response path, not the action, so the action runs twice.
- *The tell:* an error after a side-effecting call where success is ambiguous; a loop that re-issues a send or write without checking what already landed.
- *The primary defense:* idempotency keys on side-effecting operations and the retry-after-side-effect rule in [../references/tool-discipline.md](../references/tool-discipline.md): before re-running, check what already happened.
- *Owner:* CODE_GUARD (G9) + PROMPT (retry discipline).

**6. Supply-chain and dependency trust.**
- *The attack:* a fetched package, an installed tool, a skill bundle, or a connected tool server is hostile: a typosquat, a poisoned update, a server whose tool descriptions carry injection, an install script that runs on load, or a tool whose real reach exceeds its description.
- *The tell:* a new dependency with a look-alike name; a tool whose output steers behavior; an install script piped from the network; a bundle with an encoded payload chained to an interpreter; a tracked local settings file carrying standing allow grants.
- *The primary defense:* least privilege for every tool and server; pinned and reviewed dependencies; an inventory per bundle with version, exposed tools, permissions, content hash, and review date; each tool classified by what it actually does against what it claims; installation with scripts disabled until reviewed; third-party tool output treated as untrusted data.
- *Owner:* HARNESS_POLICY (least privilege, per-skill allowed tools) + CODE_GUARD (the configuration auditor in `../shield/`).

**7. Over-trust of tool output as ground truth.**
- *The attack:* the agent treats a tool or API result as verified fact and takes a state-changing action on it, when the result was wrong, stale, or attacker-shaped.
- *The tell:* a load-bearing decision resting on a single unverified read; acting on a lookup as if it were confirmation.
- *The primary defense:* match evidence to action. Before a Tier 2 action, corroborate the tool result with a second read from a different path. Before a Tier 3 action, corroborate against the system's own live state, never a cache or a prior turn's read ([../references/verification.md](../references/verification.md)).
- *Owner:* PROMPT + EVAL_ONLY.

**8. Memory and context poisoning.**
- *The attack:* fetched content, a tool result, or another agent's packet asks the agent to record a fact, a rule, or a preference in a store that outlives the session, so the payload fires in every later session without being re-read.
- *The tell:* a persistence request whose author is not the user; a "fact" in a handoff that no live source confirms; a learned instinct that contradicts a written rule.
- *The primary defense:* only the user and verified live state may originate a persistent write; everything a persistent note records carries its provenance; learned material ranks below written rules and is re-verified when it contradicts them.
- *Owner:* PROMPT (the provenance rule in [../references/memory-and-persistence.md](../references/memory-and-persistence.md)) + CODE_GUARD (a write guard on memory and shared-note paths; a G8 pattern for the directive form) + HARNESS_POLICY (deny rules on config paths).

**9. Inter-agent trust abuse.**
- *The attack:* a message, packet, or report from another agent or session is treated as an instruction or as an approval, when its author holds no authority and may itself have been injected.
- *The tell:* a handoff that names an action and supplies its parameters; a report that claims the user already approved something; a subagent summary that reads like a directive.
- *The primary defense:* an agent's message is data on the same footing as a fetched page; approvals come only from the user through the harness, never relayed; every handoff claim is verified against the live source, meaning the repository, the account, or the file, before anything acts on it ([../references/concurrency-and-handoffs.md](../references/concurrency-and-handoffs.md)).
- *Owner:* PROMPT (the verify-first protocol) + HARNESS_POLICY (relayed messages carry no permission) + CODE_GUARD (the inbox verifier; G8 widened to subagent returns and drop folders).

## OWASP Top 10 for Agentic Applications, mapped

The OWASP GenAI Security Project published its Top 10 for Agentic Applications on 2025-12-09. Each entry maps to a class above and to the layer that owns the answer.

| OWASP | Risk | Class here | Owner and mechanism |
|---|---|---|---|
| ASI01 | Agent goal hijack | 1, 2 | PROMPT frame + CODE_GUARD G8 |
| ASI02 | Tool misuse and exploitation | 2, 4 | HARNESS_POLICY tool routing + CODE_GUARD G1, G3, G4, G5 |
| ASI03 | Identity and privilege abuse | 6 | HARNESS_POLICY least privilege: deny-all baseline, per-skill allowed tools, sandboxed credentials |
| ASI04 | Agentic supply chain | 6 | HARNESS_POLICY + CODE_GUARD configuration auditor and inventory |
| ASI05 | Unexpected code execution | 4 | CODE_GUARD G1 + the host sandbox where one exists |
| ASI06 | Memory and context poisoning | 8 | PROMPT provenance + CODE_GUARD write guard + HARNESS_POLICY config deny rules |
| ASI07 | Insecure inter-agent communication | 9 | PROMPT verify-first + HARNESS_POLICY no relayed permission + CODE_GUARD inbox verifier |
| ASI08 | Cascading failures | 5, 7 | CODE_GUARD halt rules and stop file + HARNESS_POLICY kill switch |
| ASI09 | Human-agent trust exploitation | 7 | PROMPT confirmations carry evidence + the schemas `../schemas/external-send-confirmation.schema.json` and `../schemas/destructive-action-confirmation.schema.json` |
| ASI10 | Rogue agents | 8, 9 | CODE_GUARD halt rules and stop file + HARNESS_POLICY kill switch and expiring standing authorization |

## Halt rules and the kill switch

The ASI08 and ASI10 rows need one mechanism that gates G1 to G10 do not provide: a way to stop a run, not only a step. The behavioral form lives under L3 in [../references/autonomy-levels.md](../references/autonomy-levels.md): stop the run when a Tier 3 step fails or its read-back disagrees, stop on state drift, pause on anomaly, never auto-retry a destructive step, and never resume a halted run under the authorization it started with. The enforcement form is a stop file that the policy gate reads before every state-changing call, so an operator can halt a run without finding the process. Specify it as the halt column of the L3 row in [generic-policy-spec.md](generic-policy-spec.md) or as a gate of its own.

## Residual risk

No single layer is complete, and this model does not pretend otherwise. Behavioral discipline can be worn down; code guards can be under-scoped; evals can miss a class they were never written to cover. The answer is defense in depth: behavioral rules catch the reflexive miss, code and harness guards catch the determined adversary who defeats the behavior, and evals catch the regression that quietly reopens a closed door. When a high-severity defense lives only in the prompt, that is the finding; promote it to CODE_GUARD or HARNESS_POLICY. See [../references/security-posture.md](../references/security-posture.md) for the posture these threats attack and [generic-policy-spec.md](generic-policy-spec.md) for how the owning layers are specified and enforced.
