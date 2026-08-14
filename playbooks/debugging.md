# Playbook: Debugging

**Goal:** find the mechanism, prove it, fix it, prove the fix. A debugging session that ends without a one-sentence causal explanation didn't end — it paused.

## Phase 0 — Capture the failure precisely

Before touching anything: what *exactly* is observed, versus what was expected? Get the verbatim error, the failing input, the environment it fails in. "It's broken" is not a starting state; "POST /orders returns 500 with `KeyError: 'sku'` for carts created before Tuesday" is. If you can't state the failure precisely, your first task is making it precise — not fixing.

**Reproduce before diagnosing.** A failure you can't trigger on demand can't be verified fixed. Find the minimal reliable reproduction; minimizing it *is* diagnosis (each thing you remove that keeps the failure alive is a cleared suspect).

**Also record the baseline now**: run the suite once before touching anything and note what already fails — you'll verify against this later, and you must neither inherit blame for pre-existing failures nor accidentally mask them.

**When reproduction is genuinely out of reach** (production-only failure, no access to the failing environment or data), say so and switch modes: work from the evidence that exists (logs, traces, the failure's fingerprint), instrument so the *next* occurrence is diagnosable, and if you fix forward on best evidence, label the fix explicitly as unverified-against-the-original with a stated monitoring plan for recurrence. The exit criteria below adjust accordingly — verified at the highest *reachable* rung, with the gap named.

## Phase 1 — Localize before hypothesizing

Resist the leap to "I bet it's X." First shrink the search space mechanically:

- **Walk the failure backward** from the error site: what value was wrong, who produced it, who produced *that*.
- **Bisect** — by commit (when did it start?), by data (which inputs fail?), by path (does the simpler adjacent route work?). Each cut halves the territory.
- **Check what changed** — recent commits, dependency bumps, config, data shape. Most bugs are new; most new bugs correlate with a change.
- **Read the actual error carefully** — the answer lives at the error site's *immediate caller* more often than anywhere else (mind the trace ordering: some ecosystems print innermost frame last, others first). Verbatim error strings are also the best search queries you own.

## Phase 2 — Hypothesis discipline

Now hypothesize — with rules:

- **State it falsifiably**: "the cache returns stale entries after a write" implies a test that could refute it. "Something's wrong with the cache" doesn't.
- **Design the cheapest discriminating check** — the observation that gives a different result depending on whether the hypothesis is true. Prefer reads (logs, state inspection, a targeted print) over perturbations.
- **Two contradictions and you re-anchor**: if evidence has contradicted your theory twice and you're now explaining the evidence away, stop — write down what you'd expect to observe if you were wrong, and go look for exactly that. Anchoring is the debugger's chief occupational disease.
- **Say the mechanism sentence before writing the fix**: "The handler re-registers on every reconnect without deregistering, so after N drops each event fires N times." Can't say it? You're still in Phase 2 — see the perturbation-loop anti-pattern in [failure-modes.md](../references/failure-modes.md).

## Phase 3 — Fix at the right depth

- Fix the **cause**, not the frame where the symptom surfaced. A null-check at the crash site that lets a corrupt value flow onward is symptom relocation.
- **Then look for siblings**: the same wrong pattern usually exists wherever it was copy-pasted. `grep` for the shape of the bug; fixing one of three instances is a third of a fix.
- If circumstances force a symptom patch (hotfix window, upstream bug), **label it as such** in the report and leave the trail: what the real cause is, where the patch will bite later.

## Phase 4 — Prove it, both directions

1. **The reproduction now passes** — the same exact scenario that failed. (If reproduction was out of reach: the instrumented evidence and monitoring plan stand in, labeled as such.)
2. **Nothing adjacent broke** — the suite matches the Phase-0 baseline: same passes, same pre-existing failures, nothing newly broken.
3. **The fix ships with the test that would have caught it** — written to fail without the fix (run it against the unfixed code if practical; a regression test that never failed proves nothing).

Then the report, per [verification.md](../references/verification.md): the mechanism sentence, the fix, the proof, and any siblings or follow-ups flagged.

## Special cases

- **Heisenbugs / race conditions**: stop trying to catch it live; reason about the interleaving. List the shared state, the writers, and the missing ordering guarantee. Stress the suspected window (loop the test, add contention) to convert "sometimes" into "reliably."
- **"It works on my machine"**: the diff between environments *is* the bug's address — versions, env vars, data, locale, timezone. Diff them mechanically before theorizing.
- **The bug that "can't happen"**: when the code provably can't produce the observed behavior, one of your premises is false — you're reading the wrong version, the wrong deployment, the wrong file, or the build is stale. Verify you're looking at what's actually running before doubting logic itself.
- **Flaky tests**: a retry-until-green is evidence *suppression*. Either find the race or mark it honestly as flaky with the reason suspected — never quietly loosen the assertion.

## Exit criteria

- [ ] Mechanism stated in one sentence.
- [ ] Original reproduction verified fixed — or, where reproduction was unreachable, the fix labeled unverified with instrumentation + monitoring in place.
- [ ] Suite matches the Phase-0 baseline; regression test added.
- [ ] Siblings checked; symptom patches labeled.
- [ ] Report leads with the cause, not the journey.
