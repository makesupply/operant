# Playbook: Performance Optimization

**Goal:** make it measurably faster without making it wrong. Performance work has a unique pathology: intuition about where time goes is *usually mistaken*, and unverified "optimizations" routinely ship complexity while moving nothing. The discipline is a measurement sandwich — measure, change, measure — with correctness guarded throughout.

## Phase 0 — Define fast enough, and measure the now

- **Get a target, or set one and state it** ([ambiguity-and-requirements.md](../references/ambiguity-and-requirements.md)): "make it faster" becomes "p95 under 500ms at current traffic" or "the batch finishes inside the nightly window." Optimization without a stop condition runs forever and trades ever-worse complexity for ever-smaller wins.
- **Establish the baseline before touching anything**: the metric, measured the way you'll measure success — same environment, same data shape, same load. Record the *number* and the *method*; a baseline you can't reproduce is a rumor.
- **Measure what the user feels, not what's easy to time**: wall-clock end-to-end first (the p95 request, the full batch), component timings second. A 10× win in a component that's 2% of the total is a 1.9% win wearing a costume.
- **Sanity-check the environment**: measuring a debug build, a cold cache, an undersized dev database, or your own contended laptop produces numbers that evaporate in production ([environment-awareness.md](../references/environment-awareness.md)). Match production shape or state the divergence.

## Phase 1 — Profile before hypothesizing

The cardinal rule: **the profiler tells you where; you don't guess.**

- Profile the *actual slow case* — the slow request, the big input, the real query mix. Profiling the happy path finds the happy path's costs.
- **Look for the shape of the problem**: one hot function (algorithmic fix), death by a thousand cuts (architectural), waiting-not-working (I/O, locks, N+1 queries — the most common in practice and invisible to CPU profilers; use tracing/query logs for these).
- **Distrust a flat profile**: if nothing dominates, the cost may be in what the profiler can't see — GC pressure, network round-trips, lock contention, cold caches. Change instruments before changing code.
- The N+1 check is cheap and pays constantly: count the queries/calls one operation makes. If the count scales with the data, that's the bug, whatever the profiler says about CPU.

## Phase 2 — One change, measured, kept or reverted

- **One optimization at a time**, re-measured against the baseline each time. Two changes at once with one measurement is an experiment with no readable result — and when one of them regresses something, you can't tell which ([verification.md](../references/verification.md) evidence-matching applies).
- **The keep/revert rule**: a change that doesn't move the target metric gets *reverted*, even if it "should" help, even if it was clever. Unmeasurable improvements are complexity with no receipts. Keep a short log: change → delta → kept/reverted.
- **Order attempts by leverage over cleverness**: algorithm/data-structure fixes (the O(n²) hiding in a loop), doing less work (caching, batching, early exit, pagination), doing it later (async, deferred), doing it in parallel — and micro-optimizations last, only when the profiler names a genuine hot loop.
- **Correctness rides along**: the test suite runs after every kept change. An optimization that changes behavior is a bug with good latency — and caching specifically is a *correctness* decision (staleness, invalidation, memory ceiling) disguised as a performance one; state the invalidation story or don't cache.

## Phase 3 — Verify at the level that matters, then stop

- **Confirm the end-to-end win**: the user-felt metric against the Phase-0 baseline, same method. Component wins that don't move the total get reported as exactly that.
- **Check you didn't rob Peter**: latency wins that cost memory, throughput wins that cost tail latency, read speed bought with write amplification. Measure the other axes before declaring victory.
- **Stop at the target.** Past it, every further optimization trades maintainability for headroom nobody asked for. Note the *next* bottleneck (you now know it) and park it: "target met; if it ever needs another 2×, the candidate is the serializer."
- **Report with numbers and method**: baseline → result, how measured, what changed, what was tried and reverted, the complexity cost of what was kept. "40% faster" without the method is marketing, not engineering ([data-work.md](data-work.md) honesty rules apply to performance numbers too).

## Anti-patterns

- **The intuition strike.** Optimizing the code that *looks* slow. The profiler disagrees with intuition most of the time — that's why it exists.
- **The unmeasured before.** No baseline, so the claimed win is unfalsifiable. "It feels snappier" is not a delta.
- **The shotgun sprint.** Five optimizations in one pass, one measurement at the end, no idea what worked, one hidden regression.
- **The kept lottery ticket.** The clever change that measured flat but stayed because it was interesting. Revert it.
- **The cache reflex.** Caching as the first move instead of the last — buying speed with a staleness bug and an invalidation problem before cheaper wins were even tried.
- **The benchmark mirage.** Optimizing a microbenchmark that doesn't resemble production shape; the win exists only in the benchmark.
- **The infinite polish.** No target, so no finish line — the task consumes whatever time is given and the codebase pays in complexity.
