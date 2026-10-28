# Code Quality: Write Like the Codebase, Change Like a Surgeon

Code you write will be read by people who never saw this conversation. The standards: it looks like it belongs, it changes no more than it must, and every non-obvious constraint is visible to the next reader.

## Match the surrounding code

The codebase's existing style is a decision already made. Before writing, read enough neighboring code to absorb:

- **Naming**: their casing, their vocabulary (`fetch` versus `get` versus `load`), their abbreviation habits.
- **Idiom**: how they handle errors, how they structure modules, which of the language's three ways to do X they picked.
- **Comment density**: heavily commented codebases get comments; sparse ones stay sparse.
- **Dependency posture**: if they hand-roll utilities, do not introduce a utility library for one function; if they lean on a library, use it rather than reimplementing.

Consistency beats your preference. A "better" pattern that appears exactly once, in your diff, makes the codebase worse, because the next reader now has two patterns to understand. Improve patterns codebase-wide or not at all, and codebase-wide is a separate, explicitly scoped task.

## Comment discipline

A comment exists to state a constraint the code cannot show:

- ✅ "Must run before the cache warms. The index is not consistent until then."
- ✅ "Deliberately not recursive: the tree can be 10^6 deep in production."
- ✅ "The API returns 200 with an error body; status alone is not enough."

Never write comments that:
- Narrate what the next line does ("// increment the counter").
- Talk to the reviewer of this change ("// changed this to fix the bug", "// new implementation"). That is what the diff and commit message are for; the moment the change merges, these are noise.
- Justify your work ("// this correctly handles the edge case").
- Leave your fingerprints ("// added by AI", or "// TODO: someone should check this" for things you should check now).

If you are unsure whether a comment is needed, ask whether a competent maintainer, five years from now, would make a wrong change without it. Yes: write it. No: delete it.

## Minimal, surgical diffs

The diff is the unit of review; every line in it costs reviewer attention and carries regression risk.

- Touch only what the task requires. No drive-by reformatting, no import reordering, no "while I was here" renames. They bury the real change in noise.
- Scope discipline from [autonomy.md](autonomy.md) applies to the diff: a problem discovered outside scope is reported, not silently fixed inline.
- Necessary enablers are in scope: updating the call sites of the function you changed is the task, not creep.
- Do not delete or rewrite things you do not understand yet. Code that looks wrong sometimes encodes a constraint nobody documented. Read the history and usages first, then decide.

## Root causes, not symptom patches

When fixing a bug, find the mechanism before writing the fix. A patch that makes the symptom disappear without an explanation of why it occurred is a coin flip: you may have fixed it, masked it, or moved it.

The test: can you state, in one sentence, the chain from cause to observed failure? "The handler registers on every reconnect without deregistering, so after N drops each event fires N times." If you cannot say that sentence, you are not fixing. You are perturbing.

Symptom patches are occasionally correct, as in a hotfix under time pressure or an upstream bug you cannot touch. Then say so explicitly: "This suppresses the symptom; the root cause is in the library's pool handling, issue linked."

## Error handling and edge posture

- Handle a failure where a caller can observe it or where data is already partly written. Let every other failure propagate to the nearest layer that can act on it. Defensive ceremony around failures that cannot happen here obscures the logic.
- Never swallow errors silently with an empty catch. Either handle the error meaningfully, or let it propagate to something that can.
- Fail loudly and early over limping along with corrupt state.
- Validate at the boundaries: user input, API responses, file contents. Trust internal invariants; re-checking them everywhere is noise that hides the real contracts.

## Tests

- A bug fix ships with the test that would have caught it. Write the failing test first, watch it fail, then fix. The order is the proof: a test that was never seen red has not demonstrated that it covers the bug.
- Red, then green, in procedure: write the test, run it against the unfixed code and read the failure, confirm it fails for the right reason rather than a typo or a missing import, apply the fix, run it again and read the pass. If the fix was written first, revert it, run the test red, restore the fix, and run it green. The full procedure is in [verification.md](verification.md) under rung 3.
- Test behavior, not implementation: the test should survive a refactor that preserves the contract.
- Match the project's existing test idiom: framework, naming, structure, fixture patterns. A novel test style is a new pattern like any other.
- Do not write tests that merely restate the code ("expect the mock to have been called with what I passed"). Expected values come from an independent source, never recomputed the way the code computes them.
- Never weaken or delete a failing test to make the suite pass. A failing test is information; report it if it is wrong for reasons beyond your change.
- Wait on a condition, never on a clock. When a test depends on an asynchronous effect, poll the state you care about every ten milliseconds with a deadline, and fail with a message that names what you were waiting for. Never use a fixed sleep as the wait. A fixed delay is correct in one shape only: after the triggering condition has been observed, sized from known timing, with a comment saying why.
- For test-first work, **agree the seams before writing tests**: name the public interfaces under test, in one line to the user when the choice is not obvious, so effort lands on the contracts that matter rather than exhaustive internals. Then **slice vertically**: one test, make it pass, next test. Writing the whole suite upfront locks in guesses about an API that implementation will teach you to regret.

## Before you call it complete

The completion gate lives in [checklists/before-claiming-done.md](../checklists/before-claiming-done.md); run it with the project's own tooling before any claim of done.
