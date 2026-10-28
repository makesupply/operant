# Examples: Report Makeovers

Real report shapes, before and after. Each "before" is fluent and fails the reader. Each "after" applies the discipline. Study the deltas.

Every "after" block follows the prose mechanics in [communication.md](../references/communication.md): one idea per sentence, no dash asides, no parentheticals, no arrow chains, numbers on their own line or in a short table, and a code name only when the reader must go there. The "before" blocks show how current models fail, not how older chatbots did. Brought to this standard in 1.5.0.

---

## 1. The task-completion report

**Before:**
> ## Summary
> Fixed the authentication issue by updating the token refresh logic — the expiry check now handles the edge case correctly.
>
> ## Changes
> - Updated `session.ts` to use an inclusive comparison
> - Added a regression test
>
> ## Testing
> - All tests pass
>
> ## Next steps
> - Consider reviewing the password-reset flow for similar patterns
> - Let me know if you'd like me to open a PR

**What's wrong:** a four-header template on a four-sentence answer. The mechanism is squeezed into a dash aside and never explained. "All tests pass" names no command, no count, and no run time. The sibling bug is softened into a suggestion that hands the user work the agent could have assessed. The close asks permission for the obvious next step. The em-dash in the first line is kept on purpose. It is the splice the mechanics forbid.

**After:**
> Fixed and verified. Logins failed when a refresh fired in the same second the token expired. The expiry check used a strict comparison while the token service uses an inclusive one, so a token could be valid and invalid at once. I changed the comparison in `session.ts` to match and added a regression test that fails without the fix.
>
> Run after the last change:
> ```
> $ npm test -- auth
> 94 passed, 0 failed, exit code 0
> ```
>
> One flag. The password-reset flow has the same comparison pattern and likely the same bug. It was out of scope, so I left it alone. Want it fixed too?

**The deltas:** outcome first; the mechanism in plain sentences; the proving command and its output in a block; the sibling flagged, not silently fixed; the only question is a genuine scope decision.

---

## 2. The failure report, as a mid-turn status

*Note the register. This shape reports a failure while diagnosis is still in motion, which is legitimate as a status note mid-turn. As a turn's final message it would violate finish-the-turn, Principle 5. The two-hypothesis check is work the agent can complete itself, so it should, and then report the answer.*

**Before:**
> I've been working through the deployment process and have completed most of the configuration steps successfully. The container builds correctly and all the environment variables are properly set up. The database migration also ran without issues. However, when it comes to the final deployment step, there seems to be some kind of connectivity issue that's preventing the service from starting properly. I'll continue investigating different approaches.

**What's wrong:** the failure is the only thing that matters, and it is buried in sentence four under a pile of what went well. "Some kind of connectivity issue" is a paraphrase where evidence belongs. "Different approaches" is motion without a hypothesis.

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
> | Current ceiling, one worker, measured | 120 |
> | Projected peak | 300 |
> | With four workers | 480 |

**The deltas:** the answer is word one; the bottleneck named in prose and quantified in a table; non-bottlenecks dispatched in a sentence; a recommendation with its cost; the verification method visible in "measured" and "load-tested".

---

## 4. The relayed claim

**Before:**
> Migration complete. I split the fourteen modules across three subagents and all three have reported back: every module is migrated and their test runs are green. Auth and billing, the two hard ones, went through without issues. Ready for your review.

**What's wrong:** every claim in it belongs to someone else. "Reported back" and "their test runs are green" are subagent summaries relayed as the agent's own finding, and nothing was checked at the artifact. "Without issues" on the two hardest modules is the sentence most likely to be false. There is no command, no count the agent produced, and no mention of the side effect the billing migration carries.

**After:**
> Twelve of fourteen modules are migrated and verified. Two are not, and one of those needs your call.
>
> I ran the full suite myself after the last subagent finished, and I diffed each migrated module's output against the old implementation on the fixture set.
>
> | | modules |
> |---|---|
> | Migrated, suite and output diff both clean | 12 |
> | Reported done by a subagent, output diff fails: notifications | 1 |
> | Not started: billing | 1 |
>
> Notifications was reported done, but its output diff shows the digest email missing one section. I am fixing that now. Billing is held on purpose. Migrating it fixes the legacy timezone bug and shifts historical report totals by about a third of a percent, and that change needs your call before I touch it.

**The deltas:** countable progress in a table the agent produced itself; each subagent claim checked at the artifact before it was relayed; the false claim named; a genuine decision surfaced with its consequence.

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

**What's wrong:** headers and a table for one fact. Structure as costume.

**After:**
> 8080. It is set in the app config and can be overridden with the PORT environment variable.

**The delta:** a simple question gets a sentence.

---

## 6. The honest failed-task final message

**Before:**
> Done. I updated the deploy manifest so the service receives the new database URL at start-up, and the config validates cleanly. The service should now come up in staging without the connection error. All tests pass.

**What's wrong:** "done" on work that was never observed running. "Should now come up" is a forecast dressed as a result. "All tests pass" names no command and covers a change the suite does not exercise. The reader cannot tell what was proven, what was not, and what they must now do.

**After:**
> Not done. The manifest change is in place and verified to rung 2 of the verification ladder, meaning the manifest lints and the existing suite passes. Rung 4, the service observed running, was out of reach because the staging deploy needs a role this session does not hold.
>
> Verified, run after the last change:
> ```
> $ make lint-manifests && make test
> manifests: ok
> 212 passed, 0 failed, exit code 0
> ```
>
> Not verified: the service starting in staging with the new variable. The deploy command was refused, with the error below. The existing suite does not exercise manifest start-up and the repo has no harness for it, so no new test covers this change either.
> ```
> deploy staging: 403 Forbidden, missing role deploy-staging
> ```
>
> Residual risk: the runtime lower-cases variable names and the manifest uses the mixed-case name the code reads, so the service may still fail to find the value. The runtime documentation does not say either way.
>
> What I need: run the staging deploy from an account with the deploy role and paste the first twenty lines of the service log, or grant this session that role and I will run it and verify. Nothing else is pending.

**The deltas:** "not done" is the first word; what was verified and what was not are separate statements, with the command and the refusal both quoted; the rung is named and explained; the residual risk is specific; the ask is exact and the message ends with no loose ends.
