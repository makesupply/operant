# Checklist: Before Destructive or Outward-Facing Actions

Run this before ANY Tier 3 action. Under time pressure it binds harder, not softer.

> **Tier 3** = any delete, overwrite of someone else's work, send, publish, deploy, payment, production change, external API write, or bulk edit.
> **Baseline** = the pre-change state, written down: which tests fail, the current metric, the current value.
> **Rung** = how strongly the work is verified, 1 to 5. 1: reads and compiles. 2: the existing suite passes. 3: a new test for this change passes. 4: observed running. 5: the original failure re-run and gone.
> **Artifact** = the file, output, or live state itself, not a message about it.

## Target

- [ ] I opened the target within the last few minutes, not earlier in the session. Opened means I read the file contents, listed the resources, or previewed the recipients.
- [ ] What I saw matches the user's description. Any mismatch stops me here and goes in a message.
- [ ] If I did not create the target this session, I have specific evidence it is unwanted.
- [ ] The exact scope is written as a count plus a list or query: which rows, which files, which recipients.

## Consequence

- [ ] I checked by grep, logs, or usage data what still depends on the target, and that list is in my confirmation.
- [ ] The worst plausible outcome is written in one sentence.
- [ ] The undo path is written in one sentence, or I first made the action reversible by an archive, an export, a snapshot, or a paused copy.
- [ ] If the action can fail halfway, I know how I will see what applied, and I will act only on the remainder, never re-run from the top.
- [ ] If loss matters, the backup was restored once, or the degraded check I ran instead is named.

## Authorization

- [ ] The user said yes to this exact action, in this session, after seeing the confirmation.
- [ ] The confirmation showed the verbatim content, the exact entities or IDs, the exact numbers, and what happens on "no".
- [ ] For a send, publish, or platform write: the confirmation carries the fields of the project's schema, per [account-and-platform-writes.md](../playbooks/account-and-platform-writes.md) § The confirmation payload.
- [ ] For a send, publish, or platform write: there is no "test" against the real endpoint; the shown payload is the dry run.
- [ ] The evidence for this action is specific to this instance, not "this situation usually means X".

## Execution

- [ ] One item first, verified, then the batch.
- [ ] This step contains exactly one risky action.
- [ ] Immediately after, I will read back the deepest observable effect and compare the delta to the confirmed scope.
- [ ] If anything unexpected appears mid-action, I stop and report state. I do not improvise recovery.
