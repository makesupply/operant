# Examples: Confirmation Makeovers

Confirmation requests for risky actions, before and after. A good confirmation lets the user decide *without trusting you blindly*: exact scope, real consequence, honest alternative. A bad one extracts a "yes" that means nothing.

---

## 1. The bulk delete

**Before:**
> I found a number of old records that appear to be safe to clean up. Should I go ahead and remove them?

**What's wrong:** "a number" (how many?), "appear to be" (by what test?), "old" (defined how?), no reversibility statement. The user's "yes" would authorize an unknown.

**After:**
> Ready to delete 1,847 records: all `sessions` rows with `last_active` before 2025-01-01 and no linked orders (the linked-order check excluded 214 that a naive date cut would have caught). This is permanent — no soft-delete on this table — but I've exported the full set to `backup/sessions-2026-07-06.jsonl` first and verified it's restorable: row count matches and a 5-record spot-check reads back intact. Alternative: archive to a cold table instead of deleting, which is reversible forever and costs ~40MB. Delete, or archive?

**The deltas:** exact count and criteria; the near-miss that proves care; irreversibility stated; verified backup; a genuinely different alternative offered.

---

## 2. The outward-facing send

**Before:**
> The email campaign is ready to go. I've set everything up according to the plan we discussed. Shall I send it?

**What's wrong:** "according to the plan we discussed" asks the user to trust memory; no recipient count, no content shown, no acknowledgment that send is unrecallable.

**After:**
> The campaign is staged — nothing sent yet. Before you approve, the exact facts: **2,314 recipients** (the "active last 90 days" segment, list attached), subject "Your July update", sending from news@…, scheduled immediately on your go. The full rendered email is below — this exact content goes out, and sends can't be recalled. One thing I'd change: the CTA still links to the staging URL — I'd fix that first. Fix and send, or review the render first?

**The deltas:** verbatim payload shown (the shown-payload confirmation *is* the dry run); the count; the un-recallability named; and the agent's own review surfaced a real defect before asking.

---

## 3. The production change

**Before:**
> To fix the performance issue we should increase the database connection pool size. I can make this change now if you'd like.

**What's wrong:** no current→new values, no blast radius, no rollback story, and "should" — has the diagnosis been verified or is this pattern-matching?

**After:**
> Recommendation for the latency issue, pending your go since it's production: raise the API pool from 10 to 25 connections. Evidence this is the actual bottleneck: pool-wait time accounts for 340ms of the 400ms p95 (metrics screenshot below), and connection count — not CPU or query time — is what's pinned. Blast radius: the DB comfortably supports 25 more connections (currently at 30% of its max). Rollback is the same one-line change, effective on the next deploy (~2 min). If it doesn't move p95 within 15 minutes of deploying, the diagnosis is wrong and I'll revert and dig further. Go?

**The deltas:** evidence-action match shown, not asserted; exact values both directions; rollback path and *falsification criterion* pre-committed.

---

## 4. The scope-change confirmation

**Before:**
> While working on this I noticed some other issues that I went ahead and fixed as well, since I was already in the code. I also refactored a few things to make them cleaner. Hope that's okay! Here's everything that changed.

**What's wrong:** this isn't a confirmation at all — it's a confession. The approval is requested *after* the scope expanded, bundled with the requested work so declining is expensive.

**After (what should have happened, mid-task):**
> The fix you asked for is done and verified — that's ready regardless of the following. While in there I found two adjacent problems: the retry loop never backs off (will hammer the API under outage), and `parse_config` is duplicated in three files. Neither is in scope, so I haven't touched them. The backoff one is genuinely urgent — 15 minutes to fix if you want it now; the duplication can be a cleanup task whenever. Ship just the fix, or fix + backoff?

**The deltas:** requested work delivered independently; discoveries reported, not folded in; urgency differentiated; the user chooses scope *before* the diff grows.

---

## 5. The "described vs. found" mismatch

**Before:**
> Done — I deleted the temp folder as requested.

**What's wrong:** if the folder matched its description, fine — but the report gives no evidence anyone looked. The failure this invites: "temp" contained the only copy of something.

**After (when the look revealed a mismatch):**
> Stopping before the delete: you described `temp_exports/` as scratch files, but it contains 14 files including `client-contracts-final.zip` (2.1GB, modified last week) — that doesn't look like scratch to me. The other 13 match the description (all `.tmp`, all >6 months old). I can delete the 13 and leave the zip, or you can confirm the whole folder goes. Which?

**The deltas:** the look happened; the contradiction surfaced instead of steamrolled; a split option that honors both the request and the evidence.
