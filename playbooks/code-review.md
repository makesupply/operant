# Playbook: Code Review
*Read when: you are reviewing a change, reviewing your own diff before handoff, or responding to review findings on your work.*

**Goal:** find the defects that matter, verify they are real, and report them so the author can act. A review's value is measured by confirmed findings per reader-minute, not by comment count.

## Phase 0: Understand the change before judging it

- **Read the intent first**: the pull request description, the linked issue, the commit messages. A review that does not know what the change is for can only critique style.
- **Map the blast radius**: what the diff touches, and who touches that. The bug is as often in the unchanged caller that now receives different behavior as in the changed lines.
- **Set the altitude from the ask.** A quick sanity check and a thorough security review are different jobs; confirm which one you are doing.
- **Recommend a split when the change is too large to review honestly**, rather than a shallower review that pretends to be a full one.

## Phase 1: Multiple passes, one lens each

One combined pass finds the loudest issue per file and goes blind to the rest. Sweep the same diff several times, each with a single question.

1. **Correctness.** Does the code do what the intent says? Trace actual values through the changed paths: off-by-ones, inverted conditions, the wrong variable, a missed early return.
2. **Edges and failure modes.** Empty, null, zero, negative, huge, concurrent, duplicate, malformed. What happens when the external call fails or the user double-clicks?
3. **Contract drift.** Does the change alter behavior someone depends on: API shapes, serialized formats, event ordering, error types? Check the consumers of anything that moved.
4. **Security**, per [security-posture.md](../references/security-posture.md): injection surfaces, authorization on new paths, secrets, unvalidated boundary input.
5. **Tests.** Do the new tests pin the new behavior, so that they would fail without the change, or do they restate the mocks?
6. **Simplification**, when asked or when the change is large: duplication the author did not know about, complexity a library call replaces.

For agent-generated diffs at volume, sample and count rather than read every line. Read one representative file per kind of change fully, then grep for the pattern across the rest and count the matches against the expected number.

## Phase 2: Verify before reporting

The cardinal review sin is the plausible-but-wrong finding. It costs the author an investigation and the reviewer their credibility.

- **For every suspected bug, construct the failure scenario**: the concrete input or state that makes the wrong thing happen. If you cannot construct it, ask it as a question.
- **Check your assumption against the code, not your memory of the framework.** The API you remember may not be the version in the lockfile; see [environment-awareness.md](../references/environment-awareness.md).
- **Run what is runnable**: the suite, the reproduction, the type checker. A finding verified by execution outranks ten verified by inspection.
- Label residual uncertainty: **confirmed** when traced or executed, **plausible** when you could not rule it out, with what would settle it.

## Phase 3: Report for action

- **Rank by severity, worst first.** Data loss and security above correctness, correctness above robustness, robustness above style.
- **Each finding carries a claim, a location, a failure scenario, and a direction.** "`retry()` re-wraps the exception, so the caller's `except TimeoutError` never matches and any timeout surfaces as a generic 500 at `client.py:88`. Preserve the original type or catch the wrapper."
- **Separate must-fix from take-or-leave.** Three blockers plus a labeled nice-to-have list read as judgment; fifteen undifferentiated items read as noise.
- **Zero findings is a valid result.** Say what you checked and found sound; padding with style nits is filler.
- **Do not relitigate the design** the author was told to build. Design objections attach to the decision record, once.

## Reviewing your own work

Before handing off any non-trivial change, run lenses 1 to 3 and 5 on your own diff as if hostile. For high-stakes changes, a fresh-context subagent with an adversarial brief sees what you cannot; see [delegation-and-multiagent.md](../references/delegation-and-multiagent.md).

Bound the pass. Reread only the files you touched, with fresh eyes. Cleanup is the default: dead code, debug residue, names that read wrong now, nesting a guard clause flattens. Refactors are proposed, not applied, and the bar for proposing one is that a senior engineer would call the current state wrong. Keep additional changes under a fifth of the original diff, and add at most five one-line why-comments. Re-run the covering checks after any edit the pass made; a pass that touched code and did not re-verify has unverified the change.

## Receiving a review

Feedback is a claim to verify, not an instruction to execute and not an occasion for agreement. Read all of it before reacting. For each item, restate the requirement in your own words, check it against the codebase, and then fix it or push back with evidence. Clarify every unclear item before implementing any, since items are often related. Implement blocking issues first, then simple fixes, then complex ones, one at a time, each tested. Acknowledge a correct finding by stating the fix, such as "Fixed: `retry()` now preserves the exception type," never with thanks or "you're right." If your pushback turns out wrong, say so in one sentence with what you checked, and move on.

## Exit criteria

- [ ] Every finding has a location, a constructed failure scenario, a severity, and a confirmed or plausible label.
- [ ] Must-fix and take-or-leave are separated.
- [ ] For a self-review: only touched files were reread, extra changes stay under a fifth of the diff, and the covering checks were re-run.
- [ ] For a received review: every item was restated, verified, and either fixed with a test or declined with evidence.

## Anti-patterns

- **The style tribunal.** *Tell:* twelve formatting comments, zero traced data paths. *Fix:* leave style to the linter; review behavior.
- **The drive-by approval.** *Tell:* "looks good" with no evidence of reading. *Fix:* name what you checked, or do not approve.
- **The unconstructed finding.** *Tell:* "this might have concurrency issues," no scenario, no location. *Fix:* construct the failure or ask a question.
- **The severity blender.** *Tell:* blocker and bikeshed in one stream. *Fix:* rank worst first and label the must-fix set.
- **The self-pass that became a rewrite.** *Tell:* the cleanup pass doubled the diff. *Fix:* propose refactors, apply only cleanup.
- **The reflexive agreement.** *Tell:* "you're absolutely right" before checking. *Fix:* verify, then state the fix or the evidence against it.
