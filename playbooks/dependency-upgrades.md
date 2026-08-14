# Playbook: Dependency Upgrades

**Goal:** move to new versions deliberately — knowing what changes, catching what breaks, and keeping the ability to retreat. Upgrades are small migrations ([migrations.md](migrations.md)) with a twist: the change was written by strangers, documented optimistically, and tested against someone else's usage patterns, not yours.

## Phase 0 — Know what you're actually changing

- **Read the changelog/release notes between your version and the target — actually read them**, especially sections named "breaking," "deprecated," "behavior changes," and "migration." For a multi-major-version jump, read *every* major's notes; breakage compounds across them.
- **Diff the dependency tree, not just the headline package**: the lockfile diff shows what *else* moves — transitive bumps are where the surprise breakage lives, because nobody read those changelogs.
- **Classify the upgrade**: security patch (urgent, narrow, low risk), minor/feature (routine), major (a small migration project — scope it as one, per [estimation-and-status.md](../references/estimation-and-status.md)). The classification sets the ceremony; don't run patch-level ceremony on a major, or vice versa.
- **Check the project's constraints first**: pinned-version policies, peer-dependency chains, runtime/platform minimums the new version raises (the classic: the new major silently requires a newer language/runtime than production has — [environment-awareness.md](../references/environment-awareness.md)).

## Phase 1 — Find your exposure

- **Inventory your actual usage of what changed**: grep for the APIs the changelog says moved/removed. The breaking change you don't use is trivia; the deprecated call in 40 files is the real scope. This converts "risky upgrade" into a concrete work list ([migrations.md](migrations.md) inventory rule).
- **Check the escape hatches you depend on**: monkeypatches, internal-API reaches, workarounds for old bugs (now fixed — your workaround may now *be* the bug), version-sniffing code, and behavior your tests accidentally pinned.
- **Look for the ecosystem's verdict** when the upgrade is young: the package's issue tracker for the target version tells you in ten minutes what a day of debugging would — regressions, platform breaks, "wait for x.y.1" signals. Fresh majors earn a deliberate lag unless a security fix forces the pace.

## Phase 2 — Upgrade in a revertible increment

- **One package (or one coherent group) per change** — never the "upgrade everything" commit. When something breaks a week later, `git bisect` should land on one dependency, not thirty.
- **Isolate it**: a branch, a clean lockfile regeneration (not hand-edits), and a build from scratch — stale caches and node_modules ghosts make upgrade testing lie in both directions.
- **Fix deprecations while you're here, not suppressions**: the deprecation warnings the new version emits are next major's breakage list; silencing them converts a scheduled cost into a surprise one.
- **The point of maximum caution is data and persistence**: any dependency that touches storage formats, serialization, or migrations (ORMs, DB drivers, cache clients) gets the [migrations.md](migrations.md) treatment — verified backup, canary data, and a tested downgrade path, because *those* upgrades can be one-way doors.

## Phase 3 — Verify like the changelog is lying

- **The suite is necessary, not sufficient**: tests cover your pinned expectations; upgrades break *unpinned* behavior — timing, ordering, defaults, error types, output formats. Run the app and exercise the surfaces that touch the upgraded dependency directly ([verification.md](../references/verification.md) — climb to the observed-behavior rung).
- **Diff the observable outputs where feasible**: the rendered page, the generated file, the API response, the query the ORM emits — before vs. after. Upgrades that "pass everything" while quietly changing emitted SQL or serialized output are the classic silent regression.
- **Watch the seams the changelog named**: whatever it said changed, test *that* in your context, with your data.
- **Canary in production shape** for anything user-facing: one service/instance/percentage first, watched for a real usage cycle, then the fleet ([safety.md](../references/safety.md) blast-radius rule).

## Phase 4 — Land it honestly

- **The report**: what moved (headline + notable transitives), what broke and how it was fixed, what was verified and how, deprecations fixed vs. remaining, and the rollback path ("revert the lockfile commit" — confirmed to actually work, not assumed).
- **Update what the upgrade falsified**: docs, examples, setup instructions, CI images pinned to the old version ([writing-and-docs.md](writing-and-docs.md)).
- **Leave the trail**: if you deferred anything (a package held back, a deprecation left), record it with the reason and the trigger for revisiting — a held-back version with no explanation becomes permanently frozen infrastructure.

## Special cases

- **Security patches under time pressure**: compress the ceremony, not the verification of the *changed surface* — patch-level security releases are narrow by design; read the advisory, confirm your exposure, upgrade, run the suite, verify the vulnerable path specifically, ship. Days-long full-regression ceremony on a critical CVE is its own risk.
- **The abandoned dependency**: when the upgrade path is "the maintainer left," the real task is a replacement evaluation ([research-and-analysis.md](research-and-analysis.md)) — pinning forever is a decision too, and it should be made explicitly, with its risk stated, not by default.
- **Lockfile-only churn** (renovate/dependabot streams): batch the trivially-green patch bumps, but *never* auto-merge anything major, anything touching auth/crypto/serialization, or anything whose tests don't actually exercise it.

## Anti-patterns

- **The changelog skip.** Upgrading on version number and vibes; the "breaking changes" section was eight lines and unread.
- **The big-bang bump.** Every dependency at once; the break surfaces later and bisects to nothing.
- **The suite-green fallacy.** "Tests pass" as full verification, when the change lives in behavior the tests never pinned.
- **The warning muffler.** Suppressing deprecation warnings instead of fixing them — pre-ordering next year's emergency.
- **The transitive blind spot.** Reviewing the one package you bumped while twelve moved in the lockfile.
- **The stranded workaround.** The monkeypatch for the old bug, still applied to the new version, now *causing* the behavior it once fixed.
