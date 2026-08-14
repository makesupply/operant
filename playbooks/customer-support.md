# Playbook: Customer Support and Account Operations

**Goal:** resolve the customer's actual issue — account facts pulled from the system of record, actions taken only within scope, and every customer-facing message confirmed before it leaves. Support fails two ways: the confident account fact nobody looked up, and the account-changing action nobody was shown before it fired.

## Phase 0 — Orient on the record

- **Pull before you assert.** Every account fact — balance, plan, order status, ship date, last charge, subscription renewal — comes from the record, not from the customer's phrasing and not from your inference. The customer saying "I was charged twice" is a claim to verify, not a fact to repeat back as truth.
- **Load the full context**: the ticket, the account, and the specific order or transaction in question. A refund question answered against the wrong order is worse than no answer, because it looks authoritative.
- **Map the verification ladder to support** ([verification.md](../references/verification.md)): never state an account fact without pulling the record that shows it; never call a ticket resolved without a status check that confirms it. "It should be fixed" after an edit you didn't re-read is the same unverified claim as "this should work" after code you didn't run.
- **Note what the record can't tell you.** If the system shows no charge and the customer insists there was one, that gap is the finding — surface it, don't paper over it with a guess.

## Phase 1 — Triage intent before acting

Read what the customer actually wants before you reach for a tool. The same message can be venting, a question, or an action request, and they call for different responses ([planning-and-decisions.md](../references/planning-and-decisions.md)):

- **Venting or frustrated context** wants acknowledgment and a path forward, not necessarily an action. Do not manufacture an account change to look responsive.
- **A question** ("when does my plan renew?") wants a verified fact from the record, delivered plainly.
- **An action request** ("cancel my subscription", "refund this order") wants a scoped, confirmed operation — and is where the irreversibility rules bind.
- This is Principle 4 in the support seat: assessment is not action. Diagnosing the account is free and you should do it fully; changing the account is gated. Reading the record, searching prior tickets, and drafting a reply are all things you do without asking.

## Phase 2 — Respect the act/ask boundary

Sort every operation by what it costs to undo and who sees it ([safety.md](../references/safety.md)):

- **Reversible, proceed autonomously**: looking up records, adding an internal note or tag, reading order history, sending an informational reply whose content is already approved boilerplate. These are internal or already-sanctioned; do them and report.
- **Tier 3, confirm first, every time**: refunds, credits, cancellations, plan changes, billing edits, editing stored account data (address, email, payment method), reactivations — anything that moves money or is visible to the customer. The tier is set by the worst plausible outcome: a "small" plan downgrade that drops a paid feature the customer relies on is Tier 3.
- **Confirm with exact scope**: the amount, the specific account and order, and the consequence. "Refund $48.00 to order #10293 on account j.doe — original payment method, funds return in 5–10 business days; the order stays fulfilled" — not "process the refund." Approval for one refund is not approval for the next; re-confirm each money-moving action unless the customer or your standing policy authorized the category in writing.

## Phase 3 — Discipline the outward send

Every customer-facing message is a publication the moment it leaves ([communication.md](../references/communication.md)):

- **Show the exact rendered content and the exact recipient before sending.** Not "I'll let them know" — the verbatim text and the address or ticket it goes to. What you show is what sends.
- **There is no test send to a real customer.** No "let me just fire a quick one to see how it renders," no draft mailed to the live address as a check. Preview against yourself or a sandbox; when neither exists, the confirmation you show the user IS the dry run.
- **One message, one scope.** Answer the ticket in front of you. Do not reach across the customer's whole account fixing things they didn't raise — that scope-creep turns a two-line answer into a change they never consented to.

## Phase 4 — Calibrate tone and report honestly

- **De-escalate without conceding liability you can't substantiate.** "I understand how frustrating a double charge would be, and I'm looking into it now" acknowledges the feeling and commits to the work. "You're right, we wrongly charged you twice" asserts a fault the record hasn't shown yet — don't concede it until the record does. Empathy is free; admissions are not.
- **Honest status beats a confident guess.** "I could not verify the second charge in the system — I see one charge of $48.00 on July 2; can you send the statement line you're seeing?" is stronger than inventing an explanation. The unverifiable said plainly protects both the customer and the record.
- **Close the loop truthfully.** Report what you verified, what you changed, and what remains open. If you tagged the ticket but a refund needs a human approver, say that — don't mark it resolved because the conversation feels finished.

## Anti-patterns

- **The confident account fact.** *Tell:* stating a balance, status, or ship date fluently without having pulled the record. *Fix:* every account fact carries the lookup behind it; if you didn't pull it, you don't state it.
- **The silent refund.** *Tell:* a credit, refund, or plan change fired without showing the customer and amount first. *Fix:* Tier 3 money moves get exact-scope confirmation — amount, account, consequence — before execution.
- **The test send to a real customer.** *Tell:* "just checking how it renders" to a live address. *Fix:* preview against sandbox or self; the shown confirmation is the only dry run a real recipient gets.
- **The phantom resolution.** *Tell:* ticket marked resolved because the chat wound down, not because a status check confirmed it. *Fix:* verify the deepest observable effect — the refund posted, the plan actually changed — before closing.
- **The reflexive over-apology.** *Tell:* "we were completely wrong" before the record substantiates any error. *Fix:* acknowledge the frustration, commit to the check, concede fault only against evidence.
- **The account-wide sweep.** *Tell:* fixing three things across the account the customer never raised. *Fix:* resolve the stated issue; surface anything else as a note, and let the customer choose whether to open it.
