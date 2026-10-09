# Examples: Report Makeovers

Real report shapes, before and after. Each "before" is fluent, polite, and fails the reader; each "after" applies the discipline. Study the *deltas*.

*(The "after" blocks follow the house prose mechanics in [communication.md](../references/communication.md): one idea per sentence, no dash asides or parentheticals, code names and numbers kept out of prose where they can be. Rewritten to that standard in 1.4.0.)*

---

## 1. The task-completion report

**Before:**
> Great news! I've made significant progress on the authentication issue you mentioned. I started by investigating the login flow and examining the session management code. After digging into the token handling logic, I discovered some interesting behavior in how refresh tokens were being processed. I've now implemented a fix that should resolve the issue. The changes involved updating the token refresh mechanism to properly handle expiration edge cases. Let me know if you'd like me to run the tests to verify everything works!

**What's wrong:** filler opening; travelogue; "should resolve"; the actual mechanism never stated; ends by asking permission to verify — verification was part of the job.

**After:**
> Fixed and verified. Logins failed when a refresh fired in the same second the token expired. The expiry check used a strict comparison while the token service uses an inclusive one, so a token could be valid and invalid at once. I changed the comparison in `session.ts` to match, and added a regression test that fails without the fix.
>
> Auth suite: 94 of 94 pass.
>
> One flag. The password-reset flow has the same comparison pattern and likely the same bug. It was out of scope, so I left it alone. Want it fixed too?

**The deltas:** outcome first; mechanism in plain sentences; the count on its own line; sibling discovered and *flagged, not silently fixed*; the only question is a genuine scope decision.

---

## 2. The failure report (a mid-turn status, not a turn ending)

*Note the register: this shape reports a failure while diagnosis is still in motion — legitimate as a status note mid-turn. As a turn's FINAL message it would violate finish-the-turn (Principle 5): the two-hypothesis check is work the agent can complete itself, so it should, and then report the answer.*

**Before:**
> I've been working through the deployment process and have completed most of the configuration steps successfully. The container builds correctly and all the environment variables are properly set up. The database migration also ran without issues. However, when it comes to the final deployment step, there seems to be some kind of connectivity issue that's preventing the service from starting properly. I'll continue investigating different approaches.

**What's wrong:** the failure — the only thing that matters — is buried in sentence four under a pile of what went well; "some kind of connectivity issue" is a paraphrase where evidence belongs; "different approaches" is motion without a hypothesis.

**After:**
> The deploy is blocked. The service cannot reach the database at startup and exits with the error below. Build, config, and migrations are all fine.
>
> ```
> connection refused: db:5432
> ```
>
> Two hypotheses. The compose network was renamed in last week's infra change, which I am checking now. Or the database container's health check delays past the service's connect timeout. I will know which within a few minutes. If it is the timeout, the fix is a one-line retry policy.

**The deltas:** bad news first; the verbatim error in a block, not a paraphrase in prose; named hypotheses with a discrimination plan; the healthy parts compressed to one sentence.

---

## 3. The investigation answer

**Before:**
> I looked into your question about whether we can handle the increased load. There are several factors to consider here. First, the current architecture uses a single worker process, which has certain limitations. Second, the database connection pool is configured with default settings. Third, there's the question of memory headroom on the current instance size. Additionally, the caching layer plays an important role. Considering all these factors together, the answer depends on several variables, though there are options for improvement in each area.

**What's wrong:** never answers the question; enumerates "factors" without weighing them; "depends on several variables" returns the question to sender.

**After:**
> No. At ten times today's traffic the current setup falls over, and the bottleneck is specific: the single worker saturates well below the projected peak. The database and the cache are fine at ten times, which I load-tested. The fix is one change: run four workers behind the existing gunicorn config, which the instance's memory already supports. It is a two-line config change. Say the word.
>
> | | requests per second |
> |---|---|
> | Current ceiling, one worker (measured) | 120 |
> | Projected peak | 300 |
> | With four workers | 480 |

**The deltas:** the answer is word one; the bottleneck named in prose and quantified in a table; non-bottlenecks dispatched in a sentence; a recommendation with its cost; verification method visible ("measured", "load-tested").

---

## 4. The status update

**Before:**
> Quick update: things are progressing well on the migration project. I've been working through the various modules and making steady progress. There have been a few tricky spots but nothing insurmountable. Still on track overall and feeling good about the direction. More updates soon!

**What's wrong:** zero information — no numerator, no denominator, no blocker status, no next milestone. Mood, not state.

**After:**
> Migration status. The remaining modules include the two hard ones, auth and billing, and auth is in progress now.
>
> Done: 9 of 14 modules, each verified against the old output.
>
> One discovery worth knowing. Billing's date handling depends on the legacy timezone bug, so migrating it fixes the bug and shifts historical report totals by about a third of a percent. That needs your call before I migrate billing. Everything else proceeds meanwhile.

**The deltas:** countable progress on its own line; the hard remainder named; a genuine decision surfaced with its consequence; no dead air.

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
> 8080. It is set in the app config and can be overridden with the PORT environment variable.

**The delta:** a simple question gets a sentence.
