# Playbook: Refactoring

**Goal:** change the structure without changing the behavior — provably. Refactoring's defining risk is silent semantic drift: the code that looks equivalent and isn't. The whole playbook is defense against that.

## Phase 0 — Establish the safety net

**No net, no refactor.** Before moving anything:

- **Run the existing tests and record the baseline** — which pass, which already fail (pre-existing failures you must not "inherit" blame for, and must not accidentally fix-or-mask either).
- **If coverage over the target is thin, write characterization tests first** — tests that pin down what the code *currently does* (including its weird behaviors), not what it should do. You're about to rely on tests to detect drift; drift in untested behavior is undetectable.
- **Capture behavior you can't test conventionally** — golden outputs, recorded responses, before/after runs on real sample data diffed byte-wise.

If the user asks for a refactor where no net is feasible, that's a status conversation ([estimation-and-status.md](../references/estimation-and-status.md)): the honest options are "characterize first (slower, safe)" or "refactor blind (fast, and here is the specific risk)."

## Phase 1 — Scope the seam

- **Map who touches what you're changing**: callers, subclasses, reflection/dynamic access, serialized forms, external consumers of names you're about to change. The grep is cheap; the missed caller is not.
- **Define the contract that must not move**: the public surface, the persisted formats, the observable timing/ordering if anyone depends on it. Write it down in one paragraph — this is your invariant list.
- **Draw the line between refactor and redesign.** Renaming, extracting, deduplicating, restructuring = refactoring (behavior fixed). Changing what the code *does* — even "obviously for the better" — is a behavior change wearing a refactor's clothes, and it goes in a separate, labeled change. Mixing them makes both unreviewable.

## Phase 2 — Move in small, verified steps

The cardinal rule: **many small transformations, each verified, beats one big rearrangement.**

- Each step is one named transformation (extract function, inline variable, move module, rename symbol) — mechanical enough that its correctness is checkable by inspection *plus* the suite.
- **Run the tests after each step**, or after each small cluster — **and checkpoint each verified step** (a commit on a working branch, or where git isn't available, a copy/stash). The one-minute revert only exists if there's a checkpoint to revert *to*; thirty unverified steps in a dirty working tree make the revert manual unpicking — exactly the archaeology this phase exists to prevent.
- Keep the code **compiling and green at every intermediate point**. A refactor that transits through three days of broken build has abandoned its safety net exactly where the risk lives.
- **Behavior discoveries pause the refactor**: when restructuring reveals a genuine bug, don't fix it silently mid-refactor (that's semantic drift in the good direction — still drift, still invisible in review). Note it, finish or checkpoint the refactor, fix the bug as its own change with its own test. Report both.

## Phase 3 — The temptations, resisted

- **The improvement creep.** "While I'm in here" — API tweaks, defensive additions, style modernization beyond the target. Every unasked improvement widens the diff, dilutes the review, and adds drift surface. Per [autonomy.md](../references/autonomy.md): report the discoveries, don't fold them in.
- **The abstraction ladder.** Refactoring toward an abstraction the codebase doesn't need yet. Deduplicate real duplication; don't speculate interfaces for futures that may not come. Twice is coincidence; abstraction earns its keep at three.
- **The rename cascade.** One rename revealing five more that "should" follow. Do the closure the task implies; queue the rest as a listed follow-up, not a silently tripled diff.
- **The perfect endpoint.** Refactors have no natural finish line — define done at the start (the invariant list plus the target structure) or the task runs forever.

## Phase 4 — Verify equivalence, then ship

- **Full suite green**, compared against the Phase-0 baseline: same passes, same pre-existing failures, nothing newly broken *and nothing mysteriously newly fixed* (a test that starts passing is drift evidence too).
- **The dynamic-access sweep**: strings that name the things you renamed — config keys, reflection, serialized class names, docs, CI scripts. The compiler can't see these; grep can.
- **Diff review at the seam**: read your own diff specifically hunting behavior change — flipped conditions, changed defaults, altered ordering, off-by-one extraction boundaries. This read has one question: "could this line behave differently?"
- **The report**: what moved and why, proof of equivalence (baseline vs. after), the bug(s) discovered and deferred, the follow-up list. Lead with "behavior unchanged, verified by X" — that's the claim the whole task was about.

## Exit criteria

- [ ] Baseline recorded before; suite matches baseline after.
- [ ] Every renamed/moved symbol swept for dynamic references.
- [ ] Zero behavior changes folded in (discovered bugs reported separately).
- [ ] Diff reviewed once specifically for semantic drift.
- [ ] Follow-ups listed, not silently included.
