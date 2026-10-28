# Playbook: Debugging
*Read when: something that used to work, or should work, fails and you need the mechanism, the fix, and the proof.*

**Goal:** find the mechanism, prove it, fix it, and prove the fix. A debugging session that ends without a one-sentence causal explanation has paused, not ended.

## Phase 0: Capture the failure and build the loop

State what is observed and what was expected: the verbatim error, the failing input, the environment. "It's broken" is not a starting state; "POST /orders returns 500 with `KeyError: 'sku'` for carts created before 2026-10-21" is. If you cannot state the failure precisely, making it precise is the first task.

**Record the baseline now.** Run the suite once before touching anything and note what already fails, so you neither inherit blame for pre-existing failures nor mask them.

**Build the loop before you theorize.** A bug with a tight pass/fail signal gets found; one without gets guessed at. Construct the loop from the cheapest route that reaches the bug: a failing test at the nearest seam, a script against a running server, a command on a fixture input diffed against known-good output, a headless browser assertion, a captured payload replayed in isolation, `git bisect run` between two known states, or a differential run of old against new. Then tighten it: faster, sharper by asserting on the exact symptom, deterministic by pinning time, seeding randomness, and freezing the network. A two-second deterministic loop finds the bug; a thirty-second flaky one is barely a loop.

For intermittent bugs, raise the reproduction rate: loop the trigger a hundred times, add contention, narrow the timing window. Fifty percent is debuggable; one percent is not. When you cannot reproduce at all, classify the likely cause as timing, environment, shared state, or randomness, make the matching move, and say what you tried.

**Phase 0 is done when you can name one command** you have already run with its output shown, that asserts the user's exact symptom, would go green when fixed, is deterministic or pinned at a high rate, and runs fast without a human. Reading code to build a theory before that command exists is the failure this phase prevents. If no loop can be built, say so, list what you tried, and ask for the reproducing environment, a redacted captured artifact, or permission to add temporary instrumentation. When reproduction stays out of reach, work from the evidence that exists, instrument the next occurrence, and label any forward fix as unverified against the original with a monitoring plan.

## Phase 1: Localize before hypothesizing

Resist the leap to "I bet it's X." Shrink the search space mechanically first.

- **Walk the failure backward** from the error site: which value was wrong, who produced it, who produced that. Verbatim error strings are the best search queries you own.
- **Bisect** by commit, by data, and by path.
- **Check what changed.** Most bugs are new, and most new bugs correlate with a recent commit, dependency bump, or config edit.
- **Compare against a working instance.** Find the same operation succeeding elsewhere and list every difference between the two paths. The bug lives in the differences.
- **In a multi-component path, probe every boundary.** Add a tagged probe at each boundary, run once, and theorize from the evidence.

## Phase 2: Hypothesis discipline

- **Generate three to five hypotheses before testing any.** One hypothesis anchors you to the first plausible idea; a ranked list forces you to find the check that discriminates between them. Each states its prediction: "if X is the cause, changing Y makes the bug disappear." Show the list to a present user, who often re-ranks it from knowledge you lack; otherwise proceed with your ranking.
- **Test one hypothesis at a time and change one variable per test.** Two changes with one observation is a result you cannot read.
- **Tag every probe.** Prefer a debugger where one exists. When you add logs, put them at the boundaries that separate hypotheses and prefix each with a unique tag such as `[DEBUG-a4f2]`, so cleanup is one grep.
- **Two contradictions and you re-anchor.** If evidence has contradicted your theory twice and you are explaining the evidence away, stop. Write down what you would expect to observe if you were wrong and go look for exactly that.
- **Say the mechanism sentence before writing the fix**: "The handler re-registers on every reconnect without deregistering, so after N drops each event fires N times." If you cannot say it, you are still in Phase 2; see the perturbation loop in [failure-modes.md](../references/failure-modes.md).

## Phase 3: Fix at the right depth

- Fix the **cause**, not the frame where the symptom surfaced. A null check at the crash site that lets a corrupt value flow onward is symptom relocation.
- **Revert a failed fix completely before the next attempt.** Never stack a second fix on a first that did not make the loop pass.
- **Three failed fixes means the design is wrong, not the hypothesis.** When each fix reveals new coupling elsewhere, needs a large refactor to land, or creates a new symptom, stop. Say so, name the pattern, and discuss before any fourth attempt.
- **Place the fix in depth.** Decide whether validation belongs at the entry point, at the operation, or at the output, and add the layer that makes this class of bug impossible rather than this instance absent.
- **Then look for siblings.** Grep for the shape of the bug wherever it was copied; fixing one of three instances is a third of a fix. If a symptom patch is forced, label it as such, with the real cause.

## Phase 4: Prove it, both directions

1. **Write the failing test first, watch it fail, then fix.** A regression test that passed on its first run has proved nothing. If it was written after the fix, revert the fix, watch it go red, restore the fix, watch it go green.
2. **The reproduction now passes**, the same exact scenario that failed. Where reproduction was out of reach, the instrumented evidence and monitoring plan stand in, labeled as such.
3. **Nothing adjacent broke.** The suite matches the Phase 0 baseline: nothing newly broken, nothing newly and mysteriously fixed.

## Special cases

- **Heisenbugs and races.** Reason about the interleaving: list the shared state, the writers, and the missing ordering guarantee, then stress the suspected window.
- **The bug that "can't happen."** A premise is false: wrong version, wrong deployment, or a stale build. Verify you are looking at what actually runs.
- **Flaky tests.** Retry-until-green suppresses evidence. Find the race or mark the test flaky with the suspected reason; never loosen the assertion.
- **The test itself may be wrong.** When code and test disagree, check the test's expectation against the spec or a known-good example before changing the code.
- **A failure mid-sequence stops the line.** Never push past a red test, a broken build, or a failed step to the next one. Preserve the evidence, diagnose, fix, guard, then resume.

## Exit criteria

The report leads with the mechanism sentence, then the fix, the proof, and any siblings and follow-ups, per [verification.md](../references/verification.md).

- [ ] The mechanism is stated in one sentence and is in the commit message, so the next debugger inherits it.
- [ ] The original reproduction is verified fixed, or the fix is labeled unverified with instrumentation and monitoring in place.
- [ ] The regression test was seen failing before the fix and passing after it, and the suite matches the Phase 0 baseline.
- [ ] Siblings are checked and symptom patches are labeled.
- [ ] Every tagged probe is removed by grepping the tag; throwaway harnesses are deleted.

## Anti-patterns

- **The theory before the loop.** *Tell:* reading code to explain a bug no command reproduces. *Fix:* build the loop first.
- **The shotgun test.** *Tell:* two changes before one observation. *Fix:* one hypothesis, one variable, one run.
- **The stacked fix.** *Tell:* a second patch on a first that never made the loop pass. *Fix:* revert fully first.
- **The fourth attempt.** *Tell:* three fixes failed and each revealed new coupling. *Fix:* stop and discuss the design.
- **The green that never went red.** *Tell:* the regression test passed on its first run. *Fix:* revert the fix, watch red, restore, watch green.
