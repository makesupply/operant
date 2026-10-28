# Playbook: Performance Optimization
*Read when: something must get faster or cheaper, including latency, throughput, memory, or the token cost and latency of model calls.*

**Goal:** make it measurably faster without making it wrong. Intuition about where time goes is usually mistaken, and unverified optimizations routinely ship complexity while moving nothing. The discipline is a measurement sandwich: measure, change, measure, with correctness guarded throughout.

## Phase 0: Define fast enough, and measure the now

- **Get a target, or set one and state it**, per [ambiguity-and-requirements.md](../references/ambiguity-and-requirements.md). "Make it faster" becomes "p95 under 500 ms at current traffic" or "the batch finishes inside the nightly window." Optimization without a stop condition runs forever.
- **Establish the baseline before touching anything**: the metric, measured the way you will measure success, with the same environment, data shape, and load. Record the number and the method; a baseline you cannot reproduce is a rumor.
- **Measure what the user feels**: wall-clock end to end first, component timings second. A tenfold win in a component that is 2 percent of the total is a 1.9 percent win wearing a costume.
- **Sanity-check the environment.** A debug build, a cold cache, an undersized dev database, or a contended laptop produces numbers that evaporate in production; see [environment-awareness.md](../references/environment-awareness.md). Match production shape or state the divergence.
- **Load-testing production is Tier 3.** Generating load against a live system can be the outage. Confirm it explicitly, per [safety.md](../references/safety.md), or load-test a production-shaped copy.
- **For agent and model pipelines, the axis is often tokens.** Count the calls one operation makes, the tokens per call, and the latency per call; cost and latency scale with the same two numbers, and a prompt that grew by accident is the usual hot spot.

## Phase 1: Profile before hypothesizing

The profiler tells you where; you do not guess.

- Profile the actual slow case: the slow request, the big input, the real query mix. Profiling the happy path finds the happy path's costs.
- **Look for the shape of the problem**: one hot function means an algorithmic fix; death by a thousand cuts means architecture; waiting-not-working means I/O, locks, or N+1 queries, which are the most common in practice and invisible to CPU profilers. Use tracing and query logs for those.
- **Distrust a flat profile.** If nothing dominates, the cost may be where the profiler cannot see: garbage collection, network round-trips, lock contention, cold caches. Change instruments before changing code.
- **Run the N+1 check.** Count the queries or calls one operation makes. If the count scales with the data, that is the bug, whatever the profiler says about CPU.

## Phase 2: One change, measured, kept or reverted

- **One optimization at a time**, re-measured against the baseline each time. Two changes at once with one measurement is an experiment with no readable result.
- **The keep-or-revert rule.** A change that does not move the target metric gets reverted, even if it should help, even if it was clever. Keep a short log of each change, its delta, and whether it was kept.
- **Order attempts by leverage**: algorithm and data-structure fixes first, then doing less work through caching, batching, early exit, or pagination, then doing it later or in parallel, and micro-optimizations last, only when the profiler names a genuine hot loop.
- **Correctness rides along.** The suite runs after every kept change. Caching in particular is a correctness decision about staleness, invalidation, and memory ceiling disguised as a performance one; state the invalidation story or do not cache.

## Phase 3: Verify at the level that matters, then stop

- **Confirm the end-to-end win** against the Phase 0 baseline with the same method. Component wins that do not move the total get reported as exactly that.
- **Check the other axes.** Latency wins that cost memory, throughput wins that cost tail latency, read speed bought with write amplification.
- **Stop at the target.** Past it, every further change trades maintainability for headroom nobody asked for. Note the next bottleneck and park it.
- **Report with numbers and method**: baseline, result, how measured, what changed, what was tried and reverted, and the complexity cost of what was kept. "40 percent faster" without the method is marketing. The honesty rules in [data-work.md](data-work.md) apply to performance numbers.

## Exit criteria

- [ ] A numeric target and a reproducible baseline were recorded before any change.
- [ ] The slow case was profiled, not guessed.
- [ ] Every change was measured alone, and every flat change was reverted.
- [ ] The suite passes after every kept change.
- [ ] The end-to-end metric met the target and the other axes were checked.
- [ ] Any load test against production was confirmed as Tier 3 first.
- [ ] The report states baseline, result, method, and the reverted attempts.

## Anti-patterns

- **The intuition strike.** *Tell:* optimizing the code that looks slow. *Fix:* profile the slow case first.
- **The unmeasured before.** *Tell:* "it feels snappier." *Fix:* record the baseline number and method.
- **The shotgun sprint.** *Tell:* five optimizations, one measurement, one hidden regression. *Fix:* one change, one measurement.
- **The kept lottery ticket.** *Tell:* a flat change kept because it was interesting. *Fix:* revert it.
- **The cache reflex.** *Tell:* caching as the first move, with a staleness bug attached. *Fix:* cheaper wins first; state the invalidation story.
- **The benchmark mirage.** *Tell:* a win that exists only in a microbenchmark. *Fix:* measure in production shape.
- **The production load test.** *Tell:* synthetic load fired at the live system to "see what happens." *Fix:* confirm as Tier 3 or test a copy.
- **The infinite polish.** *Tell:* no target, so no finish line. *Fix:* stop at the target and park the next bottleneck.
