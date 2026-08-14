# Playbook: Greenfield Builds

**Goal:** ship something real that works end-to-end, structured so the second version is cheap. Greenfield's defining risk is the opposite of refactoring's: not drift, but *misdirection* — building the wrong thing well, or the right thing so speculatively that it collapses under its own architecture before doing anything.

## Phase 0 — Nail the target before the stack

Before any technology choice:

- **Write the one-paragraph spec** from the user's words: what it does, for whom, and the single scenario that proves it works ("a user can paste a URL and get the summary emailed"). This sentence is the acceptance test; everything not serving it is deferrable.
- **Extract the real constraints**: platform, integrations that already exist, data that already lives somewhere, who maintains this after you. Greenfield is never truly green — it lands in someone's existing world, and the constraints of that world outrank your preferences.
- **Ask the Type-4 questions now** ([ambiguity-and-requirements.md](../references/ambiguity-and-requirements.md)): scope forks and money forks are cheapest at minute zero and most expensive at hour ten.

## Phase 1 — Choose boring, choose few

- **Default to the boring stack**: the mainstream framework, the standard database, the user's existing ecosystem. Novel tech in a greenfield project is a loan against future maintenance taken out on day one. The burden of proof is on the exciting choice.
- **Minimize dependency count** — each one is a supply-chain, upgrade, and understanding cost ([security-posture.md](../references/security-posture.md)). Standard library first; a dependency when it earns its keep.
- **Make the reversible choices fast and the irreversible ones carefully** ([planning-and-decisions.md](../references/planning-and-decisions.md)): the web framework is swappable; the data model and the public API shape are the two decisions you'll live with. Spend your deliberation budget there, in roughly that order.
- **State your choices in one line each** in the report — "SQLite because single-writer and zero ops; swap to Postgres is a config change the way this is written."

## Phase 2 — Walking skeleton first

Build the **thinnest end-to-end path** through the whole system before making any part good: input arrives → gets processed → result comes out, with real wiring, stub logic. Then flesh out.

Why this order always wins:
- Integration risk — the seams between components — is where greenfield projects die, and the skeleton flushes it out in hour one instead of day five.
- From the first hour, you always have *something that runs*, which means every later step is verifiable ([verification.md](../references/verification.md)) instead of faith-based.
- The user can see and steer the skeleton — course corrections arrive when they're cheap.

The inverse anti-pattern — perfecting module A before module B exists — produces a week of polished components that don't fit together, discovered at the deadline.

## Phase 3 — Flesh out in verified increments

- **One capability at a time, verified as you go**: make it work, confirm against the running system, then next. Batching five features between test runs means the failure, when it comes, has five suspects.
- **Hardcode honestly, then un-hardcode deliberately.** Stubs and fixed values are legitimate scaffolding — *tracked* scaffolding. Keep a running list (in the task tracker or a TODO sweep at the end); shipped hardcodes that nobody listed are how demos become production incidents.
- **Error handling at the boundaries as you build them** — input validation, external-call failures — not as a "hardening pass" that history shows never comes.
- **Write the seams you'll want**: separate the core logic from the I/O even in v1. Not speculative abstraction — just the one cut that makes the logic testable and the storage/transport swappable. This is the 20% of architecture that buys 80% of v2's cheapness.

## Phase 4 — The finish line is operational, not functional

"It works when I run it" is Phase 3. Done means:

- **The proving scenario from Phase 0 runs end-to-end**, demonstrated, with the output shown to the user.
- **The core logic has tests** — not full coverage, but the proving scenario automated plus the boundary cases that Phase 3 handled. Greenfield is where the suite every other playbook presumes gets *born*; a v1 with zero tests hands the first refactor request a "no net, no refactor" bill ([refactoring.md](refactoring.md)) at the worst possible time.
- **Someone else can run it**: the README covers setup, config, run, and the one command that verifies it's working. Write it by *doing* a clean-ish setup, not from memory.
- **Secrets and config are externalized** — nothing real committed, an example env file in its place.
- **The scaffolding ledger is disclosed**: what's stubbed, what's hardcoded, what shortcuts were taken and where they'll bite. V1 honesty is the foundation of v2 planning.
- **The deliberate non-features are named**: "no auth, no pagination, single-user assumption — all fine for the stated use, all listed so they're decisions rather than surprises."

## Anti-patterns

- **The framework safari.** Two hours comparing seven libraries for a choice that's reversible in twenty minutes. Pick boring, move.
- **The cathedral foundation.** Abstractions, plugin systems, and config layers for requirements nobody has. YAGNI is a discipline, not a slogan.
- **The demo cliff.** Everything works in the happy path shown; the first real input dies. Boundary validation is part of the build, not the future.
- **The undocumented birth.** A working system only you can start. If the run instructions live in your context window, the project dies with the session.
- **The silent 80%.** Declaring done at "works for me" — skipping the README, the scaffolding ledger, and the proving run. The last 20% is the difference between a deliverable and a liability.
