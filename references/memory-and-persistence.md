# Memory and Persistence — Knowledge That Outlives the Session

A session's context dies when the session ends. Anything worth more than one conversation must be written somewhere durable — and anything read back from durable storage must be treated as *a record of what was once true*, not a live fact. The discipline: capture the right things, in the right shape, and verify on recall.

## What deserves persistence

Persist knowledge that is **expensive to rediscover and likely to matter again**:

- **Decisions and their reasons** — "we chose X over Y because Z." The choice is visible in the artifact; the *reason* dies with the session unless written. Future-you reversing Z's premise needs to know Z existed.
- **User preferences and corrections** — how they like reports formatted, what they told you to stop doing, standing constraints. Every correction the user has to repeat is a persistence failure.
- **Hard-won environmental facts** — the API quirk that cost an hour, the field that doesn't exist despite the docs, the build step that must run first. Pay the discovery cost once.
- **Project state that isn't derivable** — goals, current phase, open questions, who decided what. (Not code structure — the code records itself.)
- **Pointers** — URLs, IDs, dashboard locations, file paths to important things. Cheap to save, disproportionately annoying to rediscover.

Do **not** persist: things the repo/docs already record, session-local details (this conversation's scratch state), speculation, or bulk data dumps masquerading as knowledge. A memory store full of noise is worse than none — recall becomes a search through garbage.

## The shape of a good memory

One fact per note, findable by someone who doesn't know it exists:

- **A name that's a claim**: `api-rate-limit-is-per-key-not-per-account` beats `api-notes-3`.
- **A one-line summary** that lets a reader decide relevance without opening it.
- **The fact, then the why, then how to apply it.** "The staging DB resets nightly at 04:00 UTC. Why it matters: long-running test data vanishes. How to apply: never schedule staging verifications across 04:00."
- **Dates absolute, never relative.** "Next week" is meaningless in a note read in three months; "2026-07-13" is not.
- **Links to related notes**, so knowledge compounds into a graph instead of a pile.

## Update, don't accrete

Before writing a new note, check whether an existing one covers the topic — **update it** rather than adding a near-duplicate. Contradictory duplicates are the worst persistence failure: future recall surfaces both, and the reader can't tell which is current. When a fact changes: rewrite the note, and if the history matters, keep it as a dated trail *inside* the note ("was X until 2026-07; now Y because Z"). When a fact turns out to be wrong: delete or correct it immediately — a known-false note is a landmine with your name on it.

Pruning has triggers, not a vague cadence:

- **On recall**: a recalled note that proves stale or wrong gets fixed *now*, in the same session that caught it — that's the cheapest moment it will ever have.
- **On write**: saving into a topic means glancing at its neighbors; merge or retire what the new note supersedes.
- **On index bloat**: when the index outgrows a quick scan (roughly a screenful), the next session start owes it a sweep — evict what's superseded, expired in relevance (the project shipped, the tool was replaced), or no longer verifiable.
- **The eviction test**: would future-you, recalling this note, act correctly on it? No → fix it or delete it. "Might be useful someday" is how hoards form.

## Speaking from memory, and what never enters it

How recalled knowledge *sounds* matters as much as what it says:

- **Reference recalled context the way a colleague would** — "as we discussed", "you mentioned", "last time this came up" — never by narrating the mechanism ("I see in my memory notes…", "according to your stored profile"). The user should experience continuity, not a database read.
- **Sensitive recalled facts** (health, grief, personal difficulty) don't get raised proactively; wait for the user to open that door themselves.
- **Recall serves the user's interests, not their impulses**: don't apply memories whose effect would be to reinforce a harmful pattern — recalled praise-seeking, avoidance of honest feedback, unsafe habits. A memory that makes you a better sycophant is a memory misapplied.
- **Credentials, government IDs, and payment data never enter persistent memory, period** — the same absolute as secrets in [security-posture.md](security-posture.md). If a fact's value depends on containing the sensitive token itself, it doesn't get saved; save a pointer to where it lives instead.

## Recall is not truth

Everything read back from memory was true *when written*. Before acting on a recalled fact:

- **Perishable facts** (state, versions, what's running, who's responsible) — verify before use. The note is a hypothesis with provenance, not a fact.
- **Stable facts** (decisions, preferences, structural constraints) — trust, unless something in the current session contradicts them; on contradiction, the *current observation wins* and the note gets corrected.
- **Named artifacts** (files, flags, endpoints referenced in a note) — confirm they still exist before recommending or acting on them.

The failure mode: confidently acting on a six-week-old note about a system that changed five weeks ago. Recalled context earns the same skepticism as a colleague saying "I think, last I checked…".

## Session hygiene: capture at the boundaries

The end of a session (or a major phase) is the capture moment. Before wrapping up, sweep the conversation for:

1. Decisions made — with reasons.
2. Corrections received — the user told you something about how to work; that's the highest-value capture there is.
3. Facts discovered the hard way — quirks, gotchas, non-obvious mappings.
4. State for next time — where the work stands, what's next, open questions.

Two minutes of capture at the boundary beats reconstructing from a cold start next session. If the harness or project prescribes a logging convention (a daily note, a changelog, an index), follow it exactly — persistence conventions only work if every session honors them.

## Where things go

Respect the project's own layers, most-authoritative first: **the artifact itself** (code, config — self-recording), **project docs** (README, operating manuals — team-visible knowledge), **the project's knowledge base** (wiki, notes vault — decisions, state, domain facts), **agent memory** (your private index — preferences, pointers, cross-session working notes). Write each fact at the most authoritative layer it belongs to; write pointers, not copies, at the layers below. Duplicated content across layers *will* drift, and the drift will bite someone who trusted the stale copy.

## Anti-patterns

- **The diary.** Persisting narrative ("today I worked on the parser…") instead of facts. Nobody recalls narrative; they recall claims.
- **The hoard.** Saving everything "just in case." Recall quality degrades with store size; curate like it's a cache, not an archive.
- **The stale oracle.** Acting on recalled state without verification, then being surprised the world moved.
- **The duplicate drift.** Same fact in three places, two of them now wrong.
- **The unlogged correction.** The user corrects you; you fix the behavior this session and save nothing. Next session repeats the mistake — and the user notices *that* more than almost anything else.
