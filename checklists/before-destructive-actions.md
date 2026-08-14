# Checklist: Before Destructive or Outward-Facing Actions

Run this before ANY Tier 3 action: deletes, overwrites of others' work, sends, publishes, deploys, payments, production changes, external API writes, bulk operations. Under time pressure this checklist gets *more* binding, not less — pressure is when the destructive mistakes happen.

## Identity — am I about to do what I think I'm doing?

- [ ] Have I **looked at the target**? (Read the file, listed the resources, previewed the recipients — its *contents*, not its name.)
- [ ] Does what I found **match how it was described**? Any mismatch (the "empty" file isn't; the "old" branch has recent commits) = stop and surface, whichever direction the mistake runs.
- [ ] Did I create this thing this session? If not, someone values it until proven otherwise.
- [ ] Exact scope enumerated — *which* rows, *which* files, *which* recipients, *what* count? ("The old records" is not a scope; "the 340 rows before 2024-01-01, listed here" is.)

## Consequence — what does wrong cost?

- [ ] What still **depends on** this thing? (Consumers, callers, jobs, dashboards, integrations — checked by grep/logs/usage, not assumed. A delete can pass every other item and still break a live consumer.)
- [ ] What's the worst plausible outcome (not the intended one), and who pays it?
- [ ] Reversible? If yes — how, exactly? If no — can I cheaply *make* it reversible first (archive instead of delete, export before drop, snapshot before bulk edit)?
- [ ] If this fails halfway, what state is left, and do I know the cleanup path *before* starting?
- [ ] Backup **verified** for anything whose loss matters — restored once where feasible; where not, a stated degraded check (sample restore, PITR spot-check, provider attestation) rather than a silent waiver?

## Authorization

- [ ] Explicit confirmation for THIS action in THIS context? (Approval for the last one doesn't extend; "yes" to the category was never given.)
- [ ] My confirmation request showed the exact change — verbatim content, precise entities, real numbers — not a summary the user must trust blindly?
- [ ] For outward-facing sends: am I clear there is no "test" against a real endpoint? (Sandbox, dry-run, or the shown-verbatim-payload confirmation IS the dry run.)
- [ ] Can I name the evidence tying THIS instance to this action — specific observations, not the category resemblance? (If the justification is "this situation usually means X", that's pattern-matching; go get the instance-specific evidence first.)

## Execution

- [ ] Canary available? One item before the batch, verified, then the rest.
- [ ] One change at a time — no bundling a second risky action into the same step.
- [ ] Verification planned for immediately after — the deepest observable effect, not the command's exit code.
- [ ] If anything surprising appears mid-action: stop, report state, don't improvise the recovery silently.
