# Playbook: Dependency Upgrades
*Read when: moving a dependency, runtime, or toolchain to a new version, or triaging an automated version bump.*

**Goal:** move to new versions deliberately, knowing what changes, catching what breaks, and keeping the ability to retreat. Upgrades are small migrations, per [migrations.md](migrations.md), with a twist: the change was written by strangers, documented optimistically, and tested against someone else's usage.

## Phase 0: Know what you are actually changing

- **Read the release notes between your version and the target**, especially the sections named breaking, deprecated, behavior changes, and migration. For a multi-major jump, read every major's notes; breakage compounds.
- **Diff the dependency tree, not just the headline package.** The lockfile diff shows what else moves. Transitive bumps are where surprise breakage lives, because nobody read those changelogs.
- **Classify the upgrade**: a security patch is urgent and narrow; a minor release is routine; a major is a small migration project and gets scoped as one, per [estimation-and-status.md](../references/estimation-and-status.md). The classification sets the ceremony.
- **Check the project's constraints first**: pinned-version policies, peer-dependency chains, and runtime minimums the new version raises. The classic case is a new major that silently requires a newer runtime than production has; see [environment-awareness.md](../references/environment-awareness.md).

## Phase 1: Check supply-chain integrity

A version bump is also a trust decision. Before installing anything new, per [security-posture.md](../references/security-posture.md):

- **Confirm the package name exactly** against the registry and the project's existing manifest. A name reconstructed from memory or from a model's suggestion may not exist, or may exist as a lookalike planted for exactly that mistake.
- **Check for a maintainer or ownership change** between your version and the target. A handover followed by a release is the signature of the upgrades that bite.
- **Read any install or post-install script** the new version adds or changes. Install with scripts disabled where the package manager allows it, and enable only what you have read.
- **Verify provenance where the ecosystem offers it**: signatures, attestations, a build that matches the tagged source. Note when none is available.
- **Keep the lockfile's integrity hashes.** Regenerate the lockfile cleanly rather than hand-editing it, and treat a hash change for a version that did not move as a stop.

## Phase 2: Find your exposure

- **Inventory your usage of what changed.** Grep for the APIs the changelog says moved or were removed. The breaking change you do not use is trivia; the deprecated call in forty files is the real scope.
- **Check the escape hatches you depend on**: monkeypatches, reaches into internal APIs, workarounds for old bugs that may now be the bug, and behavior your tests accidentally pinned.
- **Look for the ecosystem's verdict when the upgrade is young.** The issue tracker for the target version tells you in ten minutes what a day of debugging would. Fresh majors earn a deliberate lag unless a security fix forces the pace.

## Phase 3: Upgrade in a revertible increment

- **One package or one coherent group per change.** When something breaks a week later, bisect should land on one dependency, not thirty.
- **Isolate it**: a branch, a clean lockfile regeneration, and a build from scratch. Stale caches make upgrade testing lie in both directions.
- **Fix deprecations rather than suppressing them.** The warnings the new version emits are the next major's breakage list.
- **Data and persistence get the full treatment.** Any dependency that touches storage formats, serialization, or migrations gets the [migrations.md](migrations.md) rules: verified backup, canary data, a tested downgrade path. Those upgrades can be one-way doors.

## Phase 4: Verify like the changelog is lying

- **The suite is necessary, not sufficient.** Tests cover your pinned expectations; upgrades break unpinned behavior such as timing, ordering, defaults, error types, and output formats. Run the app and exercise the surfaces that touch the upgraded dependency, climbing to the observed-behavior rung in [verification.md](../references/verification.md).
- **Diff observable outputs where feasible**: the rendered page, the generated file, the API response, the emitted query, before against after.
- **Test the seams the changelog named**, in your context, with your data.
- **Canary in production shape** for anything user-facing: one instance or percentage first, watched for a real usage cycle, then the fleet.

## Phase 5: Land it honestly

Report what moved, including notable transitives; what broke and how it was fixed; what was verified and how; deprecations fixed and remaining; the supply-chain checks run; and the rollback path, confirmed to work rather than assumed. Update what the upgrade falsified: docs, examples, setup instructions, CI images pinned to the old version. Record anything deferred with its reason and the trigger for revisiting.

## Special cases

- **Security patches under time pressure.** Compress the ceremony, not the verification of the changed surface. Read the advisory, confirm your exposure, upgrade, run the suite, verify the vulnerable path specifically, ship.
- **The abandoned dependency.** When the upgrade path is "the maintainer left," the real task is a replacement evaluation, per [research-and-analysis.md](research-and-analysis.md). Pinning forever is a decision too; make it explicitly.
- **Automated bump streams.** Batch the trivially green patch bumps. Never auto-merge a major, anything touching auth, crypto, or serialization, or anything whose tests do not exercise it.

## Exit criteria

- [ ] Release notes for every version between current and target were read, and the lockfile diff was reviewed for transitive moves.
- [ ] Package names, maintainer changes, install scripts, provenance, and lockfile hashes were checked.
- [ ] Usage of every changed API was inventoried by grep.
- [ ] The change is one package or one coherent group, on a branch, with a clean lockfile.
- [ ] Observed behavior at the upgraded surfaces was exercised, not only the suite.
- [ ] The rollback path was confirmed to work, and docs and CI pins the upgrade falsified are updated.

## Anti-patterns

- **The changelog skip.** *Tell:* upgraded on version number and vibes. *Fix:* read the breaking-changes section.
- **The big-bang bump.** *Tell:* every dependency at once; the break bisects to nothing. *Fix:* one package per change.
- **The suite-green fallacy.** *Tell:* "tests pass" as full verification. *Fix:* exercise the surfaces the tests never pinned.
- **The transitive blind spot.** *Tell:* one package reviewed while twelve moved. *Fix:* review the lockfile diff.
- **The hallucinated package.** *Tell:* a name installed that was never confirmed against the registry. *Fix:* confirm the exact name and its maintainer first.
- **The unread install script.** *Tell:* a post-install script ran because the package manager ran it. *Fix:* install with scripts disabled; read before enabling.
