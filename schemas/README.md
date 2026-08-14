# Schemas — the discipline made machine-readable

Prose teaches judgment; these schemas make the judgment implementable in a real harness. Each one is the structured payload behind a behavioral rule — the shape a host system can validate, log, and gate on, so the discipline survives contact with code instead of living only in a prompt.

They are deliberately small. The goal is not bureaucracy; it is to give the irreversible and delegable moments a defined interface. Use the ones your harness actually enforces; ignore the rest.

| Schema | Backs | Used when |
|---|---|---|
| [task-brief.schema.json](task-brief.schema.json) | Principles 4, 9; delegation | Starting a task or spawning a subagent — the scope/done/output contract |
| [risk-classification.schema.json](risk-classification.schema.json) | Principles 7, 10; [safety.md](../references/safety.md) | Before any state-changing action — decides whether to gate |
| [verification-report.schema.json](verification-report.schema.json) | Principle 6; [verification.md](../references/verification.md) | Attached to any done/fixed/works claim |
| [destructive-action-confirmation.schema.json](destructive-action-confirmation.schema.json) | Principle 10 | Before a Tier-3 destructive action (delete, drop, overwrite, prod change) |
| [external-send-confirmation.schema.json](external-send-confirmation.schema.json) | Principle 10 | Before anything crosses the trust boundary (send, publish, external write) |
| [assumption-ledger.schema.json](assumption-ledger.schema.json) | Principle 4; [ambiguity-and-requirements.md](../references/ambiguity-and-requirements.md) | Proceeding under ambiguity; surfaced in the final report |
| [decision-flag.schema.json](decision-flag.schema.json) | Principles 4, 9 | Raising a decision that genuinely belongs to the human |
| [eval-scenario.schema.json](eval-scenario.schema.json) | The eval system | Defining a runnable behavioral test |
| [agent-behavior-scorecard.schema.json](agent-behavior-scorecard.schema.json) | The eval system | Recording a suite run and its adoption verdict |

## How they connect

The confirmation schemas (`destructive-action-confirmation`, `external-send-confirmation`) are the payloads a `risk-classification` of Tier 3 produces before a gate. The `verification-report` is what turns a bare claim into an honest one. The `eval-scenario` and `agent-behavior-scorecard` close the loop: they prove the other schemas are actually being produced and honored. The rule registry ([../registry/rules.json](../registry/rules.json)) ties each behavioral rule to the schema, enforcement guard, and eval that back it — start there to see the whole map.

## Conventions

- Draft 2020-12 JSON Schema. `additionalProperties: false` throughout — a payload with stray fields is a bug, not a courtesy.
- Tier integers (0–3) mean the same thing everywhere: the irreversibility taxonomy in [safety.md](../references/safety.md).
- Autonomy levels (L0–L3) mean the same thing everywhere: [autonomy-levels.md](../references/autonomy-levels.md).
- `$id` hosts are illustrative; re-root them at your own domain if you publish.
