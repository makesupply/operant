# Playbook: Greenfield Builds
*Read when: building something new from nothing, from a one-off script to a service, where the first version has no code or tests behind it yet.*

**Goal:** ship something real that works end to end, structured so the second version is cheap. Greenfield's defining risk is misdirection: building the wrong thing well, or the right thing so speculatively that it collapses under its own architecture before doing anything.

## Phase 0: Nail the target before the stack

- **Write the one-paragraph spec** from the user's words: what it does, for whom, and the single scenario that proves it works, such as "a user can paste a URL and get the summary emailed." That sentence is the acceptance test; everything not serving it is deferrable. Save it as a file in the project so the next session reads the same target, not a memory of it.
- **Extract the real constraints**: platform, integrations that already exist, data that already lives somewhere, who maintains this after you. Greenfield is never truly green; it lands in someone's existing world, and that world's constraints outrank your preferences.
- **Ask the scope and money questions now**, per [ambiguity-and-requirements.md](../references/ambiguity-and-requirements.md). They are cheapest at minute zero and most expensive at hour ten.

## Phase 1: Choose boring, choose few

- **Default to the boring stack**: the mainstream framework, the standard database, the user's existing ecosystem. Novel tech in a greenfield project is a loan against future maintenance taken out on day one.
- **Pick a stack the harness can verify.** If the environment can run the tests, the type checker, and the app itself, every later claim can be proven. A stack you cannot execute here turns the whole build into faith.
- **Minimize dependency count.** Each one is a supply-chain, upgrade, and understanding cost, per [security-posture.md](../references/security-posture.md). Standard library first.
- **Make the reversible choices fast and the irreversible ones carefully**, per [planning-and-decisions.md](../references/planning-and-decisions.md). The web framework is swappable; the data model and the public API shape are the two decisions you will live with.
- **State each choice in one line** in the report: "SQLite because single-writer and zero ops; a swap to Postgres is a config change the way this is written."

## Phase 2: Walking skeleton first

Build the thinnest end-to-end path through the whole system before making any part good: input arrives, gets processed, and a result comes out, with real wiring and stub logic. Then flesh out. Integration risk at the seams is where greenfield projects die, and the skeleton flushes it out in hour one instead of day five. From the first hour you have something that runs, so every later step is verifiable, per [verification.md](../references/verification.md), and the user can steer while corrections are cheap. The inverse, perfecting module A before module B exists, produces a week of polished components that do not fit together.

## Phase 3: Flesh out in verified increments

- **One capability at a time, verified as you go.** Run the type check, the lint, and the tests after every increment. Batching five features between runs means the failure, when it comes, has five suspects.
- **Hardcode honestly, then un-hardcode deliberately.** Stubs and fixed values are legitimate scaffolding when tracked. Keep a running list; shipped hardcodes nobody listed are how demos become production incidents.
- **Error handling at the boundaries as you build them**, not as a hardening pass that never comes.
- **Write the seams you will want**: separate the core logic from input and output even in version one. Not speculative abstraction, just the one cut that makes the logic testable and the storage or transport swappable.

## Phase 4: The finish line is operational

"It works when I run it" is Phase 3. Done means:

- **The proving scenario runs end to end**, demonstrated, with the output shown to the user.
- **The core logic has tests**: the proving scenario automated plus the boundary cases Phase 3 handled. Greenfield is where the suite every other playbook presumes gets born.
- **Someone else can run it.** The README covers setup, config, run, and the one command that verifies it works, written by doing a clean setup, not from memory.
- **Secrets and config are externalized**, with an example environment file in place of anything real.
- **The scaffolding ledger is disclosed**: what is stubbed, what is hardcoded, where it will bite.
- **The deliberate non-features are named**: "no auth, no pagination, single-user assumption, all listed so they are decisions rather than surprises."

## Self-check

Re-read the spec file. Does the proving scenario still match the user's words, or did it narrow while building? Does any shortcut in the ledger silently invalidate the scenario? Would a cold reader of the README get to a running system?

## Exit criteria

- [ ] The spec and proving scenario exist as a file in the project.
- [ ] The proving scenario was demonstrated end to end with output shown.
- [ ] Type check, lint, and tests pass, and the proving scenario is automated.
- [ ] The README was produced by a clean setup and names the verifying command.
- [ ] No secret is committed; an example config stands in.
- [ ] The scaffolding ledger and the deliberate non-features are in the report.

## Anti-patterns

- **The framework safari.** *Tell:* two hours comparing seven libraries for a reversible choice. *Fix:* pick boring, move.
- **The cathedral foundation.** *Tell:* plugin systems and config layers for requirements nobody has. *Fix:* build what the proving scenario needs.
- **The demo cliff.** *Tell:* the happy path works; the first real input dies. *Fix:* boundary validation as you build each boundary.
- **The undocumented birth.** *Tell:* a system only you can start. *Fix:* write the README by doing the setup.
- **The silent 80 percent.** *Tell:* done declared at "works for me." *Fix:* README, scaffolding ledger, and proving run before done.
- **The spec in your head.** *Tell:* the target lived only in context and drifted during the build. *Fix:* the spec is a file, re-read before done.
