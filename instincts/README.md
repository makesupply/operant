# Operant Instincts: The Continuous-Learning Loop

The bundle is static; what an agent learns about *this* user's work is not. Instincts is the loop that closes that gap. It captures behavioral patterns that proved out in real sessions, scores them by confidence, and re-surfaces only the proven ones at the next session start, so the agent compounds competence on your specific work without anyone editing the bundle.

This is the single feature that changes what Operant *is* rather than what it contains: a discipline that improves itself.

## The loop

```
  session end  -> record candidate instincts -> score & merge (store.json)
                                                        |
  session start <- inject proven (>= 0.70) <------------+
        |
        +-> user corrects one -> correct (negative evidence) -> decay / retire
```

1. **Record (session end).** The agent proposes candidate instincts as JSON, each a `trigger -> action` pair with optional evidence and a seed confidence. `instincts.py record` merges them: a new pattern enters as a low-confidence *candidate*; a repeat of a known pattern gets *corroborated* (confidence steps up, observation count rises).
2. **Score and decay.** Confidence rises with corroboration, falls with contradiction, and decays after long disuse. Nothing is trusted on a single sighting. The threshold exists precisely so one-off coincidences do not become rules.
3. **Inject (session start).** `instincts.py inject` emits a short markdown block of the top-K instincts at or above the confidence threshold. That block goes into the session-start context. Below-threshold candidates stay silent; they are still learning.
4. **Correct.** When the user corrects a behavior, `instincts.py correct` logs it as strong negative evidence against matching instincts. Enough contradictions, or an explicit `--retire`, removes the instinct. A user should never have to give the same correction three times; this is the mechanism that guarantees it.

## Why confidence-scoring, not just a list

A plain "remembered preferences" list has two failure modes this design defends against:

- **The one-off fallacy.** Treating a single session's quirk as a standing rule. The corroboration threshold means a pattern must recur before it is injected.
- **The stale oracle.** Acting on a preference the user has since changed. Decay-on-disuse and contradiction-on-correction both pull stale instincts back below the injection line automatically.

The store is plain, inspectable JSON. The user can read every instinct, its confidence, its evidence, and when it was last seen, and can edit or delete any of it. Nothing is learned that the user cannot see and veto.

## Memory poisoning

An instinct is a write into something the agent reads as context on every later session, which makes the store a persistence target. The rule that keeps it honest is about provenance: **an instinct is never recorded from fetched content.** A web page, an email, a tool result, or another agent's handoff may describe a "preference" or ask the agent to remember something; none of that is evidence. Only two sources may originate an instinct: the user's own correction, and a result the agent verified against the live system. Every candidate the agent writes at session end names which of the two it came from. If a candidate cannot name one, it is not written. Instincts also rank **below written rules**: when a learned pattern contradicts a rule in the bundle, a project rule file, or the user's live instruction, the rule wins and the instinct is a candidate for `correct --retire`. The injected block says this in its own header, and the store sits inside Shield's scan scope, where a planted instruction in it is a HIGH finding.

## Commands

| Command | When | Effect |
|---|---|---|
| `record --file candidates.json` | session end | merge proposed instincts, corroborate repeats |
| `inject [--k 7] [--min 0.70]` | session start | emit the proven-instinct context block |
| `correct --trigger "..." [--retire]` | on user correction | negative evidence; `--retire` kills it outright |
| `list [--all]` | anytime | inspect proven instincts (or the whole store) |
| `prune` | periodically | drop retired or expired instincts, mark proven ones |
| `--self-test` | after any change | hardening and sanitizing checks on a temporary store |

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

Good instincts are **specific and behavioral** (a trigger you can recognize, an action you can take), not vague preferences. "When presenting affiliate data, include the video ID and link" is an instinct; "the user likes good reports" is noise.

## Hardening (1.5.0)

- **The store is validated on load.** A missing store is empty. A store that is not JSON, or whose `instincts` field is not an object, is reported on stderr with a clear message and treated as empty; the file on disk is left alone until the next write. Entries with missing fields are repaired (confidence 0.0, one observation, candidate status); entries without a trigger or an action are dropped and reported.
- **Bad values never crash a command.** A string confidence such as `"high"` becomes the default seed; a string observation count becomes 1; NaN and out-of-range numbers are clamped. A candidate that is not an object is skipped and counted. The Stop hook and the SessionStart hook therefore never fail on one bad entry.
- **Every trigger and action is sanitized** before it is stored and again before it is rendered: newlines, tabs and control characters are removed, fenced blocks, HTML comments and model control tokens are stripped, leading heading, list and quote markers are removed, and each field is capped at 240 characters. A store entry whose trigger carries `\n\n# SYSTEM OVERRIDE` renders as one bullet line with the words visible as text; the only heading in the injected block is the block's own frame.

## Wiring it in

- **Claude Code:** a `Stop` hook runs `record` against a candidates file the agent wrote that session; a `SessionStart` hook runs `inject` and feeds its output into context. See [../enforcement/claude-code-hooks.md](../enforcement/claude-code-hooks.md).
- **Custom agents and orchestrators:** call `inject` when you assemble the system prompt (append its output after the constitution), and `record` in your session-teardown step. The store path is per-user or per-project; keep it wherever that user's state lives.
- **Governance:** instincts are *learned*, so they rank **below** the bundle and the user's live instructions (the [precedence](../SKILL.md) order). The injected block says so in its own header. An instinct never overrides the discipline or a direct instruction; it only fills the space the discipline leaves to judgment.

## What never becomes an instinct

The same exclusions as memory ([../references/memory-and-persistence.md](../references/memory-and-persistence.md)): no secrets, credentials, or personal identifiers; nothing that would reinforce a harmful pattern (an instinct that makes the agent a better sycophant is a bug, not a lesson); nothing about a one-time situation; nothing whose only source is fetched content. Instincts are for *how the agent should work*, learned from evidence, not a dumping ground for session state.

## Safety note

Instincts writes to a file the agent later reads as context, a self-modification loop, which is exactly the surface [Operant Shield](../shield/README.md) audits. Keep the store inside Shield's scan scope (Shield treats `instincts/store.json` as an auto-loaded file), and note that the injected block is framed as advisory and sanitized precisely so a poisoned instinct cannot escalate its own authority.
