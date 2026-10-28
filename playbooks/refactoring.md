# Playbook: Refactoring
*Read when: changing code structure, names, or organization while behavior must stay provably the same.*

**Goal:** change the structure without changing the behavior, provably. Refactoring's defining risk is silent semantic drift: the code that looks equivalent and is not. The whole playbook is defense against that.

## Phase 0: Establish the safety net

No net, no refactor. Before moving anything:

- **Run the existing tests and record the baseline**: which pass and which already fail. You must neither inherit blame for pre-existing failures nor fix or mask them by accident.
- **If coverage over the target is thin, write characterization tests first.** They pin what the code currently does, including its weird behaviors, not what it should do. Drift in untested behavior is undetectable.
- **Capture behavior you cannot test conventionally**: golden outputs, recorded responses, before-and-after runs on real sample data diffed byte for byte.

If no net is feasible, that is a status conversation, per [estimation-and-status.md](../references/estimation-and-status.md). The honest options are "characterize first, slower and safe" or "refactor blind, fast, with this specific risk."

## Phase 1: Scope the seam

- **Map who touches what you are changing**: callers, subclasses, reflection or dynamic access, serialized forms, external consumers of names about to change. The grep is cheap; the missed caller is not.
- **Define the contract that must not move**: the public surface, the persisted formats, the observable timing or ordering if anyone depends on it. Write it in one paragraph; this is your invariant list.
- **Draw the line between refactor and redesign.** Renaming, extracting, deduplicating, and restructuring keep behavior fixed. Changing what the code does, even "obviously for the better," is a behavior change in a refactor's clothes and goes in a separate labeled change.
- **In a shared checkout, list the files you will touch first** and follow [shared-checkout.md](shared-checkout.md); a refactor that sweeps across files other agents are editing is the clobber waiting to happen.

## Phase 2: Move in small, verified steps

Many small transformations, each verified, beat one big rearrangement.

- Each step is one named transformation: extract function, inline variable, move module, rename symbol. Mechanical enough that its correctness is checkable by inspection plus the suite.
- **Run the tests after each step** or each small cluster, and **checkpoint each verified step** with a commit on a working branch or, without git, a copy. The one-minute revert only exists if there is a checkpoint to revert to.
- Keep the code **compiling and green at every intermediate point.** A refactor that transits through three days of broken build has abandoned its net exactly where the risk lives.
- **Behavior discoveries pause the refactor.** When restructuring reveals a real bug, do not fix it silently mid-refactor; that is drift in the good direction and still invisible in review. Note it, checkpoint, fix it as its own change with its own test, and report both.
- **Codemods at agent scale: sample and count, do not read every file.** For a mechanical change across hundreds of files, read a representative handful fully, run the transform, then verify by counting: the grep for the old form returns zero, the grep for the new form returns the expected number, and the suite is green. Spot-check a random sample of the rest.

## Phase 3: The temptations, resisted

- **The improvement creep.** "While I'm in here" widens the diff, dilutes the review, and adds drift surface. Per [autonomy.md](../references/autonomy.md), report discoveries; do not fold them in.
- **The abstraction ladder.** Deduplicate real duplication; do not speculate interfaces for futures that may not come. Abstraction earns its keep at three occurrences.
- **The rename cascade.** One rename revealing five more that "should" follow. Do the closure the task implies and queue the rest as a listed follow-up.
- **The perfect endpoint.** Refactors have no natural finish line. Define done at the start as the invariant list plus the target structure.

## Phase 4: Verify equivalence, then ship

- **Full suite green against the Phase 0 baseline**: same passes, same pre-existing failures, nothing newly broken, and nothing mysteriously newly fixed, since a test that starts passing is drift evidence too.
- **The dynamic-access sweep**: grep for strings that name the things you renamed in config keys, reflection, serialized class names, docs, and CI scripts. The compiler cannot see these.
- **Diff review at the seam.** Read your own diff with one question: could this line behave differently? Flipped conditions, changed defaults, altered ordering, off-by-one extraction boundaries.
- **The report** leads with "behavior unchanged, verified by X," then what moved and why, the bugs discovered and deferred, and the follow-up list.

## Exit criteria

- [ ] Baseline recorded before; the suite matches the baseline after.
- [ ] Every renamed or moved symbol was swept for dynamic references.
- [ ] Zero behavior changes folded in; discovered bugs reported as separate changes.
- [ ] Each verified step was checkpointed.
- [ ] The diff was reviewed once specifically for semantic drift.
- [ ] For a codemod: old-form count is zero, new-form count matches, and a sample was read.
- [ ] Follow-ups are listed, not silently included.

## Anti-patterns

- **The blind refactor.** *Tell:* structure moved with no tests over the target. *Fix:* characterize first or state the risk.
- **The thirty-step dirty tree.** *Tell:* no checkpoint since the first edit. *Fix:* commit each green step.
- **The silent bug fix.** *Tell:* a behavior change hidden inside the refactor. *Fix:* separate change, separate test, both reported.
- **The improvement creep.** *Tell:* the diff tripled with "while I'm here" changes. *Fix:* report them; do not fold them in.
- **The compiler-only sweep.** *Tell:* a rename that missed the config key and the serialized name. *Fix:* grep for the string.
- **The read-everything codemod.** *Tell:* four hundred files opened one by one. *Fix:* sample, transform, count, spot-check.
- **The endless refactor.** *Tell:* no defined target structure. *Fix:* write the invariant list and the endpoint before starting.
