# Examples: Confirmation Makeovers

Confirmation requests for risky actions, before and after. A good confirmation lets the user decide *without trusting you blindly*: exact scope, real consequence, honest alternative. A bad one extracts a "yes" that means nothing.

*(The "after" blocks follow the house prose mechanics in [communication.md](../references/communication.md). A confirmation must still carry its exact numbers — that is the safety rule, and it outranks the style rule — so the counts sit on their own scope line rather than woven through the prose. Rewritten to that standard in 1.4.0.)*

---

## 1. The bulk delete

**Before:**
> I found a number of old records that appear to be safe to clean up. Should I go ahead and remove them?

**What's wrong:** "a number" (how many?), "appear to be" (by what test?), "old" (defined how?), no reversibility statement. The user's "yes" would authorize an unknown.

**After:**
> Ready to delete the session records that are older than 2025 and have no linked order. The linked-order check matters: it excludes rows a naive date cut would have removed.
>
> Scope: 1,847 rows to delete · 214 rows excluded by the order check · full set exported to the backup folder and verified restorable (row count matches, a 5-record spot check reads back intact).
>
> This is permanent, since the table has no soft delete. Alternative: archive the rows to a cold table instead, which is reversible forever and costs about 40 MB. Delete, or archive?

**The deltas:** exact count and criteria; the near-miss that proves care; irreversibility stated; verified backup; a genuinely different alternative offered.

---

## 2. The outward-facing send

**Before:**
> The email campaign is ready to go. I've set everything up according to the plan we discussed. Shall I send it?

**What's wrong:** "according to the plan we discussed" asks the user to trust memory; no recipient count, no content shown, no acknowledgment that send is unrecallable.

**After:**
> The campaign is staged and nothing has been sent. The exact facts are on the next line, and the full rendered email follows them. This exact content goes out, and sends cannot be recalled.
>
> Recipients: 2,314 in the active-last-90-days segment (list attached) · Subject: "Your July update" · From: the news address · Timing: immediately on your go.
>
> One thing I would change first: the call-to-action still links to the staging URL. Fix and send, or review the render first?

**The deltas:** verbatim payload shown (the shown-payload confirmation *is* the dry run); the count; the un-recallability named; and the agent's own review surfaced a real defect before asking.

---

## 3. The production change

**Before:**
> To fix the performance issue we should increase the database connection pool size. I can make this change now if you'd like.

**What's wrong:** no current→new values, no blast radius, no rollback story, and "should" — has the diagnosis been verified or is this pattern-matching?

**After:**
> Recommendation for the latency issue, pending your go because it is production: raise the API connection pool from 10 to 25. The evidence points at the pool rather than the database. Pool wait accounts for most of the p95, and connection count is what is pinned, not CPU or query time. The metrics screenshot is below.
>
> Evidence: pool wait 340 ms of the 400 ms p95 · connections pinned · CPU and query time flat · database at under a third of its connection limit.
>
> Rollback is the same one-line change, live on the next deploy in about two minutes. If p95 has not moved fifteen minutes after the deploy, the diagnosis is wrong and I revert and dig further. Go?

**The deltas:** evidence-action match shown, not asserted; exact values both directions; rollback path and *falsification criterion* pre-committed.

---

## 4. The scope-change confirmation

**Before:**
> While working on this I noticed some other issues that I went ahead and fixed as well, since I was already in the code. I also refactored a few things to make them cleaner. Hope that's okay! Here's everything that changed.

**What's wrong:** this isn't a confirmation at all — it's a confession. The approval is requested *after* the scope expanded, bundled with the requested work so declining is expensive.

**After (what should have happened, mid-task):**
> The fix you asked for is done and verified, and it ships regardless of what follows. While in there I found two adjacent problems. I have touched neither, because they are out of scope. The retry loop never backs off, which will hammer the API during an outage. That one is urgent and takes about fifteen minutes. A config parser is duplicated in three files, and that can be a cleanup task whenever. Ship just the fix, or the fix plus the backoff?

**The deltas:** requested work delivered independently; discoveries reported, not folded in; urgency differentiated; the user chooses scope *before* the diff grows.

---

## 5. The "described vs. found" mismatch

**Before:**
> Done — I deleted the temp folder as requested.

**What's wrong:** if the folder matched its description, fine — but the report gives no evidence anyone looked. The failure this invites: "temp" contained the only copy of something.

**After (when the look revealed a mismatch):**
> Stopping before the delete. You described the exports folder as scratch files, but it holds a large zip named like final client contracts, modified last week, and that does not look like scratch. The other thirteen files match the description: all temporary, all older than six months. I can delete the thirteen and leave the zip, or you can confirm the whole folder goes. Which?

**The deltas:** the look happened; the contradiction surfaced instead of steamrolled; a split option that honors both the request and the evidence.
