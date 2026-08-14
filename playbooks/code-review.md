# Playbook: Code Review

**Goal:** find the defects that matter, verify they're real, and report them so the author can act — ranked, reproducible, and free of noise. A review's value is measured by confirmed findings per reader-minute, not by comment count.

## Phase 0 — Understand the change before judging it

- **Read the intent first**: the PR description, the linked issue, the commit messages. A review that doesn't know what the change is *for* can only critique style.
- **Map the blast radius**: what does this diff touch, and who touches what it touches? The bug is as often in the *unchanged* caller that now receives different behavior as in the changed lines themselves.
- **Establish the review's altitude from the ask**: "quick sanity check" and "thorough security review" are different jobs with different depths — confirm which one you're doing before doing either.

## Phase 1 — Multiple passes, one lens each

One combined pass finds the loudest issue per file and goes blind to the rest. Sweep the same diff several times, each with a single question:

1. **Correctness**: does this code do what the intent says? Trace the data through the changed paths — actual values, not vibes. Off-by-ones, inverted conditions, wrong variable, missed early return.
2. **Edges and failure modes**: empty, null, zero, negative, huge, concurrent, duplicate, malformed. What happens when the external call fails, the list is empty, the user double-clicks?
3. **Contract drift**: does the change alter behavior someone depends on — API shapes, serialized formats, event ordering, error types? Check the *consumers* of anything whose signature or semantics moved.
4. **Security** ([security-posture.md](../references/security-posture.md)): injection surfaces, authz on new paths, secrets, unvalidated boundary input.
5. **Tests**: do the new tests actually pin the new behavior (would they fail without the change?), or do they restate the mocks? What's *not* covered that the change makes newly possible?
6. **Simplification** (when asked, or when large): duplication with existing code the author didn't know about, complexity that a stdlib call replaces.

## Phase 2 — Verify before reporting

The cardinal review sin is the plausible-but-wrong finding — it costs the author an investigation to refute and costs the reviewer their credibility.

- **For every suspected bug, construct the failure scenario**: the concrete input/state that makes the wrong thing happen. If you can't construct it, it's a question, not a finding — ask it as one.
- **Check your assumption against the code, not your memory of the framework** — the API you remember may not be the version in the lockfile ([environment-awareness.md](../references/environment-awareness.md)).
- **Run what's runnable**: the suite, the reproduction, the type checker. A finding verified by execution outranks ten verified by inspection.
- Label residual uncertainty honestly: **confirmed** (traced or executed) vs. **plausible** (couldn't rule out — stated with what would settle it).

## Phase 3 — Report for action

- **Rank by severity, worst first** — data loss and security above correctness, correctness above robustness, robustness above style. The author should be able to stop reading at any point and have handled everything above it.
- **Each finding: claim, location, failure scenario, suggested direction.** "`retry()` re-wraps the exception, so the caller's `except TimeoutError` never matches — any timeout now surfaces as a generic 500 (`client.py:88`). Preserve the original type or catch the wrapper."
- **Separate must-fix from take-or-leave** explicitly. An undifferentiated list of 15 items reads as noise; three blockers plus a labeled nice-to-have list reads as judgment.
- **Zero findings is a valid result** — say what you checked and found sound, so the clean bill means something. Padding with style nits to justify the review is the reviewer's version of filler.
- **Don't relitigate the design** the author was told to build. Design objections attach to the *decision record*, once, briefly — not to line 47.

## Reviewing your own work

Before handing off any non-trivial change of your own, run Phase 1 lenses 1–3 and 5 on your own diff *as if hostile*. You will find something often enough to make it standing practice; the cheapest review comment is the one nobody had to write. For high-stakes changes, a fresh-context subagent with an adversarial brief ("find what's wrong with this diff") sees what you can't — see [delegation-and-multiagent.md](../references/delegation-and-multiagent.md).

## Anti-patterns

- **The style tribunal.** Twelve formatting comments, zero traced data paths. Linters do style; reviewers do behavior.
- **The drive-by "looks good".** Approval without evidence of reading — worse than no review, because it launders risk as diligence.
- **The unconstructed finding.** "This might have issues with concurrency" — no scenario, no location, no way to act on it.
- **The rewrite-in-comments.** Redesigning the author's approach line by line when the approach was settled. Review the change that was made.
- **The severity blender.** Blocker and bikeshed in one undifferentiated stream, forcing the author to triage the reviewer.
- **The memory-based API claim.** "This method doesn't exist" — in the version you remember; the lockfile disagrees. Check before claiming.
