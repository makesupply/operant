# Examples: Confirmation Makeovers

Confirmation requests for risky actions, before and after. A good confirmation lets the user decide without trusting you blindly: exact scope, real consequence, honest alternative. A bad one extracts a "yes" that means nothing.

Every "after" block follows the prose mechanics in [communication.md](../references/communication.md). A confirmation must still carry its exact numbers. That is the safety rule, and it outranks the style rule, so the counts sit on their own scope line rather than woven through the prose. Makeover 6 shows the same facts in the shape the send gate parses. Brought to this standard in 1.5.0.

---

## 1. The bulk delete

**Before:**
> I found a number of old records that appear to be safe to clean up. Should I go ahead and remove them?

**What's wrong:** "a number" says nothing about how many. "Appear to be" names no test. "Old" is undefined. There is no reversibility statement. The user's "yes" would authorize an unknown.

**After:**
> Ready to delete the old session records that have no linked order. The linked-order check matters: it excludes rows a plain date cut would have removed.
>
> Criterion: created before 2025-01-01 and no linked order · 1,847 rows to delete · 214 rows excluded by the order check · full set exported to the backup folder.
>
> The export is verified restorable. Its row count matches, and a spot check of five records reads back intact.
>
> This is permanent, since the table has no soft delete. The alternative is to archive the rows to a cold table instead, which is reversible forever.
>
> Archive cost: about 40 MB of cold storage.
>
> Delete, or archive?

**The deltas:** exact count and criteria on the scope line; the near-miss that proves care; irreversibility stated; the backup verified, with the check named; a genuinely different alternative offered with its cost.

---

## 2. The outward-facing send

**Before:**
> The email campaign is ready to go. I've set everything up according to the plan we discussed. Shall I send it?

**What's wrong:** "according to the plan we discussed" asks the user to trust memory. No recipient count, no content shown, no acknowledgment that a send cannot be recalled.

**After:**
> The campaign is staged and nothing has been sent. The exact facts are on the next line, and the full rendered email follows them. This exact content goes out, and sends cannot be recalled.
>
> Recipients: 2,314 in the active-last-90-days segment · Subject: "Your July update" · From: the news address · Timing: immediately on your go.
>
> The recipient list is attached.
>
> One thing I would change first: the call-to-action still links to the staging URL. Fix and send, or review the render first?

**The deltas:** the verbatim payload shown, and the shown payload is the dry run; the count; the un-recallability named; the agent's own review surfaced a real defect before asking.

---

## 3. The production change

**Before:**
> To fix the performance issue we should increase the database connection pool size. I can make this change now if you'd like.

**What's wrong:** no current and new values, no blast radius, no rollback story. "Should" leaves open whether the diagnosis was verified or pattern-matched.

**After:**
> Recommendation for the latency issue, pending your go because it is production: raise the API connection pool. The evidence points at the pool rather than the database. Pool wait accounts for most of the 95th-percentile latency, and the connection count is what is pinned, not processor time or query time. The metrics screenshot is below.
>
> Change: pool size 10 now, 25 after.
>
> Evidence: pool wait 340 ms of the 400 ms 95th-percentile latency · connections pinned · processor and query time flat · database under a third of its connection limit.
>
> Rollback is the same one-line change, live on the next deploy in about two minutes. If the 95th-percentile latency has not moved fifteen minutes after the deploy, the diagnosis is wrong and I revert and dig further. Go?

**The deltas:** the evidence-action match shown, not asserted; exact values in both directions on their own line; the rollback path and the falsification criterion committed in advance.

---

## 4. The scope-change confirmation

**Before:**
> While working on this I noticed some other issues that I went ahead and fixed as well, since I was already in the code. I also refactored a few things to make them cleaner. Hope that's okay! Here's everything that changed.

**What's wrong:** this is not a confirmation. It is a confession. The approval is requested after the scope expanded, bundled with the requested work so that declining is expensive.

**After, what should have happened mid-task:**
> The fix you asked for is done and verified, and it ships regardless of what follows. While in there I found two adjacent problems. I have touched neither, because they are out of scope. The retry loop never backs off, which will hammer the API during an outage. That one is urgent and takes about fifteen minutes. A config parser is duplicated in three files, and that can be a cleanup task whenever. Ship just the fix, or the fix plus the backoff?

**The deltas:** the requested work delivered independently; discoveries reported, not folded in; urgency differentiated; the user chooses scope before the diff grows.

---

## 5. The "described vs. found" mismatch

**Before:**
> Done, I deleted the temp folder as requested.

**What's wrong:** if the folder matched its description, fine. But the report gives no evidence anyone looked. The failure this invites: "temp" contained the only copy of something.

**After, when the look revealed a mismatch:**
> Stopping before the delete. You described the exports folder as scratch files, but it holds a large zip named like final client contracts, modified last week, and that does not look like scratch. The other thirteen files match the description: all temporary, all older than six months. I can delete the thirteen and leave the zip, or you can confirm the whole folder goes. Which?

**The deltas:** the look happened; the contradiction surfaced instead of steamrolled; a split option that honors both the request and the evidence.

---

## 6. The send-gate payload

**Before:**
> Ready to send the restock email to the back-in-stock list. Content is final, the segment is set, and nothing goes out until you say go. Send?

**What's wrong:** every fact a gate needs is missing, and the prose shape cannot be parsed by one. No resolved segment, no live count, no sending account, no rendered content, no statement of what "no" does, no undo path. "The back-in-stock list" is the label the agent was given, not what it resolved to.

**After:**
> Nothing has been sent. The facts are on the lines below. Under them is the same content in the shape of the send gate's schema, [external-send-confirmation.schema.json](../schemas/external-send-confirmation.schema.json), as [account-and-platform-writes.md](../playbooks/account-and-platform-writes.md) § The confirmation payload requires. The full rendered email is attached.
>
> What: the rendered email, subject "The slim comb is back", rendered against a sample recipient and attached in full · To whom: segment "Back in stock: slim comb", ID seg_8c21, 1,206 profiles resolved live at 14:02 today · From which account: the store's main sending account, not the test account · When: on your go, within this hour, not scheduled · Before and after: 3 campaign sends this month, 4 after; the volume is inside the plan, so no added charge · On no: nothing happens, and the draft stays unscheduled in the platform · Undo after send: none.
>
> ```json
> {
>   "channel": "email",
>   "recipients": {
>     "resolved": ["segment: Back in stock: slim comb (seg_8c21)"],
>     "count": 1206,
>     "is_real_audience": true
>   },
>   "rendered_content": "Subject: The slim comb is back. Hi Dana, the slim comb you asked about is back in stock at 14.00 USD and ships in two days. Product page: https://store.example/combs/slim. Unsubscribe: https://store.example/u/a81f",
>   "reach": "1,206 subscribers, one send",
>   "claims_checked": true,
>   "sensitive_data_scan": "clean",
>   "reversible": false,
>   "idempotency_key": "restock-slim-comb-2026-10-28",
>   "authorization": "awaiting"
> }
> ```
>
> One thing to settle before go. Some profiles in the segment have no first name on file and would read "Hi ,". I can switch those to "Hi there".
>
> Profiles with no first name: 38 of 1,206.
>
> Send with the fallback, or hold?

**The deltas:** every field the gate parses is present once, in a shape a parser reads and a human reads; the segment is the resolved one with its ID and live count, not the label; the "no" path and the undo path are stated even when the answer is "none"; the agent's own review still surfaces a defect before asking.
