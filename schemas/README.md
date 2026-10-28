# Schemas: the discipline made machine-readable

Prose teaches judgment; these schemas give the irreversible and delegable moments a defined interface. Each one is the structured payload behind a behavioral rule in [../registry/rules.json](../registry/rules.json). They are deliberately small. Use the ones your harness enforces; treat the rest as the shape a payload should take.

## What code consumes and what is a reference shape

Be honest about which of these a program reads. The audit of 2026-10-28 (the C5 review) found two of nine consumed by code; the rest were documentation in JSON Schema clothing. The table says which is which so nobody mistakes a reference shape for a guarantee.

| Schema | Backs (rule, eval) | Consumed by code | Status |
|---|---|---|---|
| [eval-scenario.schema.json](eval-scenario.schema.json) | the eval system | `evals/eval-runner.py validate` and its self-test; `tools/release-check.py` reads `vector` for the sandbox-wiring check | **consumed** |
| [agent-behavior-scorecard.schema.json](agent-behavior-scorecard.schema.json) | the eval system | `evals/eval-runner.py` validates every scorecard it writes; `tools/release-check.py` reads `run.mode`, `run.suite_version`, and the per-result `scenario_sha256` / `fixture_sha256` fields | **consumed** |
| [verification-report.schema.json](verification-report.schema.json) | P6-verify-before-claim (E9), P6-disclose-unverifiable (E10), P6-faithful-failure-report (E4), P6-show-the-evidence (E29) | nothing | reference shape; since 1.5.0 each verified item requires the literal `command` and `output` |
| [task-brief.schema.json](task-brief.schema.json) | P8-tool-discipline (E32, E34, E39), X-delegation-brief (E21), X-least-privilege-brief (E39) | nothing | reference shape; `allowed_tools` and `denied_paths` added 1.5.0 for least privilege |
| [risk-classification.schema.json](risk-classification.schema.json) | P7-evidence-to-action (E11), P10-bulk-mutation (E28, G3), P10-production-change (E27, G5) | nothing | reference shape |
| [destructive-action-confirmation.schema.json](destructive-action-confirmation.schema.json) | P10-destructive-gate (E12, G1), P10-described-vs-found (E13), P10-history-rewrite (E26, G2) | nothing | reference shape; optional `evidence` block added 1.5.0 |
| [external-send-confirmation.schema.json](external-send-confirmation.schema.json) | P10-external-send (E14, G4), X-idempotency (E19, G9) | nothing | reference shape; optional `evidence` block added 1.5.0 |
| [assumption-ledger.schema.json](assumption-ledger.schema.json) | X-assumption-ledger (E20), X-missing-input-no-substitution (E24) | nothing | reference shape |
| [decision-flag.schema.json](decision-flag.schema.json) | P4-act-dont-ask (E5), P9-recommend-dont-enumerate (E16), P9-plan-interrogation (E37) | nothing | reference shape |
| [handoff-document.schema.json](handoff-document.schema.json) | X-handoff-document (E33) | nothing | reference shape, new in 1.5.0; template in `../examples/handoff-document.md` |
| [tool-result-provenance.schema.json](tool-result-provenance.schema.json) | X-provenance-labeling (E35) | nothing | reference shape, new in 1.5.0 |
| [stop-condition.schema.json](stop-condition.schema.json) | X-stop-conditions (E31) | nothing | reference shape, new in 1.5.0 |

"Consumed by code" means a shipped program validates payloads against the schema or reads fields from it. "Reference shape" means the schema defines what a conforming payload looks like and the evals judge whether the agent's prose carries those fields, but no program in this bundle parses the payload. A deployment that renders its own confirmation (an account-write gate, an approval queue) decides for itself whether to emit these shapes; the shapes are here so that choice is available, not to claim it was made.

## How they connect

The confirmation schemas (`destructive-action-confirmation`, `external-send-confirmation`) are the payloads a `risk-classification` of Tier 3 produces before a gate; their `evidence` block is the before-picture a human needs, read from the live target before the question is asked. The `verification-report` turns a bare claim into an honest one, and since 1.5.0 the evidence is a command plus its output, never a paraphrase. The `handoff-document` carries that same evidence across a session boundary. The `tool-result-provenance` list says where every figure came from and how far it is trusted. The `stop-condition` is declared before an autonomous loop so the loop ends on a rule, not on the harness's turn limit. The `eval-scenario` and `agent-behavior-scorecard` close the loop: they prove the other shapes are produced and honored. The rule registry ties each rule to the schema, gate, and eval that back it; start there to see the whole map.

## Conventions

- Draft 2020-12 JSON Schema. `additionalProperties: false` throughout; a payload with stray fields is a bug, not a courtesy. The one exception is `evidence.read_back_values` in the two confirmation schemas, a free object keyed by the target's own field names.
- Tier integers (0-3) mean the same thing everywhere: the irreversibility taxonomy in [safety.md](../references/safety.md).
- Autonomy levels (L0-L3) mean the same thing everywhere: [autonomy-levels.md](../references/autonomy-levels.md).
- The eval runner's built-in validator understands `type`, `required`, `properties`, `additionalProperties`, `items`, `enum`, `pattern`, and `minItems`. Keywords outside that set (`minLength`, `minProperties`, `minimum`) are honored by a full validator and ignored by the runner; do not rely on them for a check the runner must perform.
- `$id` hosts are illustrative; re-root them at your own domain if you publish.
