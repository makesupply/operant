# Operant Instincts — The Continuous-Learning Loop

The bundle is static; what an agent learns about *this* user's work is not. Instincts is the loop that closes that gap: it captures behavioral patterns that proved out in real sessions, scores them by confidence, and re-surfaces only the proven ones at the next session start — so the agent compounds competence on your specific work without anyone editing the bundle.

This is the single feature that changes what Operant *is* rather than what it contains: a discipline that improves itself.

## The loop

```
  session end ──▶ record candidate instincts ──▶ score & merge (store.json)
                                                        │
  session start ◀── inject proven (≥0.70) ◀────────────┘
        │
        └──▶ user corrects one ──▶ correct (negative evidence) ──▶ decay / retire
```

1. **Record (session end).** The agent proposes candidate instincts as JSON — each a `trigger → action` pair with optional evidence and a seed confidence. `instincts.py record` merges them: a genuinely new pattern enters as a low-confidence *candidate*; a repeat of a known pattern gets *corroborated* (confidence steps up, observation count rises).
2. **Score & decay.** Confidence rises with corroboration, falls with contradiction, and decays after long disuse. Nothing is trusted on a single sighting — the threshold exists precisely so one-off coincidences don't become "rules."
3. **Inject (session start).** `instincts.py inject` emits a short markdown block of the top-K instincts at or above the confidence threshold. That block goes into the session-start context. Below-threshold candidates stay silent — they're still learning.
4. **Correct.** When the user corrects a behavior, `instincts.py correct` logs it as strong negative evidence against matching instincts — enough contradictions (or an explicit `--retire`) removes the instinct. A user should never have to give the same correction three times; this is the mechanism that guarantees it.

## Why confidence-scoring, not just a list

A plain "remembered preferences" list has two failure modes this design defends against:

- **The one-off fallacy** — treating a single session's quirk as a standing rule. The corroboration threshold means a pattern must recur before it's injected.
- **The stale oracle** — acting on a preference the user has since changed. Decay-on-disuse and contradiction-on-correction both pull stale instincts back below the injection line automatically.

The store is plain, inspectable JSON. The user can read every instinct, its confidence, its evidence, and when it was last seen — and edit or delete any of it. Nothing is learned that the user can't see and veto.

## Commands

| Command | When | Effect |
|---|---|---|
| `record --file candidates.json` | session end | merge proposed instincts, corroborate repeats |
| `inject [--k 7] [--min 0.70]` | session start | emit the proven-instinct context block |
| `correct --trigger "…" [--retire]` | on user correction | negative evidence; `--retire` kills it outright |
| `list [--all]` | anytime | inspect proven instincts (or the whole store) |
| `prune` | periodically | drop retired/expired instincts, mark proven ones |

## Candidate format

What the agent writes at session end (`candidates.json`):

```json
[
  {
    "trigger": "presenting affiliate video data",
    "action": "include the video ID and TikTok link",
    "evidence": "user corrected a report that omitted them",
    "confidence": 0.5
  }
]
```

Good instincts are **specific and behavioral** (a trigger you can recognize, an action you can take), not vague preferences. "When presenting affiliate data → include the video ID and link" is an instinct; "the user likes good reports" is noise.

## Wiring it in

- **Claude Code:** a `Stop` hook runs `record` against a candidates file the agent wrote that session; a `SessionStart` hook runs `inject` and feeds its output into context. See [../enforcement/claude-code-hooks.md](../enforcement/claude-code-hooks.md).
- **Custom agents / orchestrators:** call `inject` when you assemble the system prompt (append its output after the constitution), and `record` in your session-teardown step. The store path is per-user (or per-project); keep it wherever that user's state lives.
- **Governance:** instincts are *learned*, so they rank **below** the bundle and the user's live instructions (the [precedence](../SKILL.md) order). The injected block says so in its own header — an instinct never overrides the discipline or a direct instruction; it only fills the space the discipline leaves to judgment.

## What never becomes an instinct

The same exclusions as memory ([../references/memory-and-persistence.md](../references/memory-and-persistence.md)): no secrets, credentials, or personal identifiers; nothing that would reinforce a harmful pattern (an instinct that makes the agent a better sycophant is a bug, not a lesson); nothing about a one-time situation. Instincts are for *how the agent should work*, learned from evidence — not a dumping ground for session state.

## Safety note

Instincts writes to a file the agent later reads as context — a self-modification loop, which is exactly the surface [Operant Shield](../shield/README.md) audits. Keep the store inside Shield's scan scope, and note that the injected block is framed as advisory (below the discipline) precisely so a poisoned instinct can't escalate its own authority.
