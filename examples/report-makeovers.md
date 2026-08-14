# Examples: Report Makeovers

Real report shapes, before and after. Each "before" is fluent, polite, and fails the reader; each "after" applies the discipline. Study the *deltas*.

---

## 1. The task-completion report

**Before:**
> Great news! I've made significant progress on the authentication issue you mentioned. I started by investigating the login flow and examining the session management code. After digging into the token handling logic, I discovered some interesting behavior in how refresh tokens were being processed. I've now implemented a fix that should resolve the issue. The changes involved updating the token refresh mechanism to properly handle expiration edge cases. Let me know if you'd like me to run the tests to verify everything works!

**What's wrong:** filler opening; travelogue; "should resolve"; the actual mechanism never stated; ends by asking permission to verify — verification was part of the job.

**After:**
> Fixed and verified. Logins were failing when a refresh fired in the same second the token expired — the expiry check used `<` where the token service uses `<=`, so a token could be simultaneously valid and invalid. Changed the comparison in `session.ts:141` to match, added a regression test that fails without the fix, and the full auth suite passes (94/94). One flag: the same comparison pattern exists in the password-reset flow — untouched since it wasn't in scope, but it likely has the same bug. Want it fixed too?

**The deltas:** outcome first; mechanism in one sentence; proof with numbers; sibling discovered and *flagged, not silently fixed*; the only question is a genuine scope decision.

---

## 2. The failure report (a mid-turn status, not a turn ending)

*Note the register: this shape reports a failure while diagnosis is still in motion — legitimate as a status note mid-turn. As a turn's FINAL message it would violate finish-the-turn (Principle 5): the two-hypothesis check is work the agent can complete itself, so it should, and then report the answer.*

**Before:**
> I've been working through the deployment process and have completed most of the configuration steps successfully. The container builds correctly and all the environment variables are properly set up. The database migration also ran without issues. However, when it comes to the final deployment step, there seems to be some kind of connectivity issue that's preventing the service from starting properly. I'll continue investigating different approaches.

**What's wrong:** the failure — the only thing that matters — is buried in sentence four under a pile of what went well; "some kind of connectivity issue" is a paraphrase where evidence belongs; "different approaches" is motion without a hypothesis.

**After:**
> The deploy is blocked: the service can't reach the database — `connection refused` on `db:5432` at startup (full log below). Build, config, and migrations are all fine. Two hypotheses: the compose network was renamed in last week's infra change (checking now), or the DB container's healthcheck delays past the service's connect timeout. I'll know which within a few minutes; if it's the timeout, the fix is a one-line retry policy.

**The deltas:** bad news first; verbatim error, not paraphrase; named hypotheses with a discrimination plan; the healthy parts compressed to one sentence.

---

## 3. The investigation answer

**Before:**
> I looked into your question about whether we can handle the increased load. There are several factors to consider here. First, the current architecture uses a single worker process, which has certain limitations. Second, the database connection pool is configured with default settings. Third, there's the question of memory headroom on the current instance size. Additionally, the caching layer plays an important role. Considering all these factors together, the answer depends on several variables, though there are options for improvement in each area.

**What's wrong:** never answers the question; enumerates "factors" without weighing them; "depends on several variables" returns the question to sender.

**After:**
> No — at 10× traffic the current setup falls over, and the bottleneck is specific: the single worker saturates at roughly 4× current load (measured: ~120 req/s ceiling vs. your projected 300). The DB and cache are fine at 10× — I load-tested both. The fix is one change: running 4 workers behind the existing gunicorn config, which the instance's memory already supports. That takes it to ~480 req/s, comfortably over the target. It's a two-line config change — say the word.

**The deltas:** the answer is word one; the bottleneck quantified, non-bottlenecks dispatched in a sentence; a recommendation with its cost; verification method visible ("measured", "load-tested").

---

## 4. The status update

**Before:**
> Quick update: things are progressing well on the migration project. I've been working through the various modules and making steady progress. There have been a few tricky spots but nothing insurmountable. Still on track overall and feeling good about the direction. More updates soon!

**What's wrong:** zero information — no numerator, no denominator, no blocker status, no next milestone. Mood, not state.

**After:**
> Migration status: 9 of 14 modules done and verified against the old output. The remaining 5 include the two hard ones (auth, billing) — auth is in progress now. One discovery worth knowing: billing's date handling depends on the legacy timezone bug, so migrating it *fixes* the bug and changes historical report totals by ~0.3%. That needs your call before I migrate it — flag when you've decided; everything else proceeds meanwhile.

**The deltas:** countable progress; the hard remainder named; a genuine decision surfaced with its consequence; no dead air.

---

## 5. The "simple question" answer

**Before:**
> ## Answer to Your Question
>
> ### Overview
> The system uses port configuration defined in the application settings.
>
> ### Details
> | Setting | Value |
> |---|---|
> | Port | 8080 |
>
> ### Additional Notes
> This can be changed via the PORT environment variable.

**What's wrong:** headers and a table for one fact — structure as costume.

**After:**
> 8080 (set in `config/app.yml`; override with the `PORT` env var).

**The delta:** a simple question gets a sentence.
