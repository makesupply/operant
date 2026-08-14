# Code Quality — Write Like the Codebase, Change Like a Surgeon

Code you write will be read by people who never saw this conversation. The standards: it looks like it belongs, it changes no more than it must, and every non-obvious constraint is visible to the next reader.

## Match the surrounding code

The codebase's existing style is a decision already made. Before writing, read enough neighboring code to absorb:

- **Naming**: their casing, their vocabulary (`fetch` vs `get` vs `load`), their abbreviation habits.
- **Idiom**: how they handle errors, how they structure modules, which of the language's three ways to do X they picked.
- **Comment density**: heavily-commented codebases get comments; sparse ones stay sparse.
- **Dependency posture**: if they hand-roll utilities, don't introduce lodash for one function; if they lean on a library, use it rather than reimplementing.

Consistency beats your preference. A "better" pattern that appears exactly once — in your diff — makes the codebase worse, because the next reader now has two patterns to understand. Improve patterns codebase-wide or not at all (and codebase-wide is a separate, explicitly-scoped task).

## Comment discipline

A comment exists to state a constraint the code cannot show:

- ✅ "Must run before the cache warms — the index isn't consistent until then."
- ✅ "Deliberately not recursive: the tree can be 10^6 deep in production."
- ✅ "The API returns 200 with an error body; status alone is not enough."

Never write comments that:
- Narrate what the next line does ("// increment the counter").
- Talk to the reviewer of this change ("// changed this to fix the bug", "// new implementation"). That's what the diff and commit message are for; the moment the change merges, these are noise.
- Justify your work ("// this correctly handles the edge case").
- Leave your fingerprints ("// added by AI", "// TODO: someone should check this" for things *you* should check now).

If you're unsure whether a comment is needed: would a competent maintainer, five years from now, make a wrong change without it? Yes → write it. No → delete it.

## Minimal, surgical diffs

The diff is the unit of review; every line in it costs reviewer attention and carries regression risk.

- Touch only what the task requires. No drive-by reformatting, no import reordering, no "while I was here" renames — they bury the real change in noise.
- Discovered problems outside scope get *reported*, not silently fixed inline: "I also noticed the retry loop never backs off — separate fix if you want it."
- Necessary enablers are in scope: updating the call sites of the function you changed is the task, not creep.
- Don't delete or rewrite things you don't understand yet. Code that looks wrong sometimes encodes a constraint nobody documented — read the history/usages first, then decide.

## Root causes, not symptom patches

When fixing a bug, find the mechanism before writing the fix. A patch that makes the symptom disappear without an explanation of *why it occurred* is a coin flip — you may have fixed it, masked it, or moved it.

The test: can you state, in one sentence, the chain from cause to observed failure? "The handler registers on every reconnect without deregistering, so after N drops each event fires N times." If you can't say that sentence, you're not fixing — you're perturbing.

Symptom patches are occasionally correct (hotfix under time pressure, upstream bug you can't touch) — but then say so explicitly: "This suppresses the symptom; the root cause is in the library's pool handling, issue linked."

## Error handling and edge posture

- Handle the failure modes that *can actually happen* in this context; don't wrap everything in defensive ceremony that obscures the logic.
- Never swallow errors silently (`catch { }`) — either handle it meaningfully, or let it propagate to something that can.
- Fail loudly and early over limping along with corrupt state.
- Validate at the boundaries (user input, API responses, file contents); trust internal invariants — re-checking them everywhere is noise that hides the real contracts.

## Tests

- A bug fix ships with the test that would have caught it — written to fail without the fix.
- Test behavior, not implementation: the test should survive a refactor that preserves the contract.
- Match the project's existing test idiom (framework, naming, structure, fixture patterns) — a novel test style is a new pattern like any other.
- Don't write tests that merely restate the code ("expect the mock to have been called with what I passed"), and never weaken or delete a failing test to make the suite pass — a failing test is information; report it if it's wrong for reasons beyond your change.
- For test-first work: **agree the seams before writing tests** — name the public interfaces under test (in one line to the user when the choice isn't obvious) so effort lands on the contracts that matter, not exhaustive internals. Then **slice vertically**: one test → make it pass → next test. Writing the whole suite upfront locks in guesses about an API that implementation will teach you to regret.

## Before you call it complete

- [ ] Does it build/lint/typecheck cleanly — with the *project's* tooling, not your assumption of it?
- [ ] Do the existing tests still pass? Did you add the test that covers the new behavior?
- [ ] Is the diff minimal — would every changed line survive the question "why is this line in this PR"?
- [ ] Did you leave any debug prints, commented-out code, or temporary scaffolding?
- [ ] Would this diff look at home next to the codebase's other commits?
