# Governance — How Operant Evolves Without Drifting

A framework with a prompt, a set of code gates, and an eval suite has three copies of every rule. They drift. A rule tightened in the constitution but not in the eval is untested; a gate added in code but not in the prompt produces confusing denials; an eval that checks a behavior the prompt no longer requires fails for no reason. This file defines the discipline that keeps them in agreement — the same discipline the framework asks of an agent, applied to the framework itself.

## The single source of truth

[registry/rules.json](registry/rules.json) is authoritative. Every behavioral rule has one entry naming: the principle it serves, the failure it prevents, the layer(s) that own it (PROMPT / RETRIEVAL / HARNESS_POLICY / CODE_GUARD / EVAL_ONLY), the reference chapter that teaches it, the enforcement gate that guarantees it (if any), the schema that structures it (if any), and the eval that proves it. To understand a rule's full footprint, start there.

## The change protocol

When you add, remove, or materially change a rule:

1. **Edit the registry entry first.** Decide which layers own it. A rule that only lives in `PROMPT` is a hope; a rule marked `CODE_GUARD` without a gate is a lie. Resolve that before writing prose.
2. **Update every artifact the entry names.** If the entry lists a reference, a gate, and an eval, all three change together in the same commit. The registry is the checklist.
3. **Keep the confirmation schemas in step.** If the change alters what a human must see before a Tier-3 action, the relevant schema in [schemas/](schemas/) changes too.
4. **Add or update the eval.** A behavior with no eval cannot be claimed as a property of the framework — it is an aspiration. Every anti-pattern in [references/failure-modes.md](references/failure-modes.md) is an eval waiting for a fixture.
5. **Re-run the suite.** At minimum the smoke test; the full suite before you tag a release. A change that drops a safety-cluster eval blocks the release.
6. **Rebuild the compiled editions.** `dist/one-page.md` and `dist/single-file.md` are generated views of the constitution; regenerate them before tagging so they can't drift from the sources.
7. **Run the mechanical checks.** Every touched gate script's `--self-test` (policy-gate, injection-sentinel, shield), `evals/eval-runner.py validate` and `self-test`, then `tools/release-check.py <bundle> --mirror <mirror>`. Since 1.4.0 the release check also enforces steps 1–4 as code: every gate in `policy.rules.json` needs a section in the generic spec and a registry rule that names it; every registry rule's eval needs a scenario file; every scenario with a fixture kind needs its fixture. It refuses the shape of drift that let G10 ship in code with no spec entry, registry rule, eval, or changelog line (2026-09-03 → caught 2026-09-14).

## The sync rule (prompt ↔ enforcement)

Hooks/gates and skill text must agree. A gate blocking something the skill never mentions produces denials the agent can't reason about; a skill rule with no gate is acceptable trust, but should be a deliberate choice, not an oversight. When you edit one, check the other — [enforcement/generic-policy-spec.md](enforcement/generic-policy-spec.md) and [enforcement/policy.rules.json](enforcement/policy.rules.json) are the enforcement half; the registry tells you which prompt rule each gate backs.

## The ratchet rule (autonomy)

Autonomy levels only go up after the enforcement and audit they require are in place and have passed their evals — never before ([references/autonomy-levels.md](references/autonomy-levels.md)). Raising a deployment from L2 to L3 is a governance event: it requires the L3 gate set, the audit log, and a passing certification run, not a config toggle.

## Versioning

Semantic versioning on the bundle as a whole, recorded in [CHANGELOG.md](CHANGELOG.md):

- **Major** — a change to the Ten Principles or the tier/level taxonomy (anything that changes what "compliant" means).
- **Minor** — a new playbook, reference, schema, gate, or eval; a new adaptation.
- **Patch** — wording, fixes, tuning a gate pattern, correcting a link.

The `version` fields in `registry/rules.json` and `enforcement/policy.rules.json` track with the bundle version.

## What not to do

- Don't add a rule because it sounds wise. Every rule costs context budget and eval maintenance; a rule that doesn't prevent a nameable failure is subtraction disguised as addition.
- Don't broaden a gate pattern to catch a near-miss. Every false positive teaches the model and the user to route around the gate. Add a project-specific pattern instead.
- Don't let the prompt grow unbounded. The constitution is always-loaded; depth belongs in retrieved chapters. If the core is growing, something wants to be a reference, not a principle.
- Don't ship a claim the eval suite can't back. The whole point of Operant is that discipline is a tested property, not a vibe.
- Don't ship a gate without its owning rule and proving eval, and don't call a script self-tested until it carries a `--self-test`. Both happened once; the release check now refuses the first, and the second is what the self-test corpus is for.
- Don't raise an autonomy level because the model got smarter. A new model tier means a new certification run, not a new level ([references/autonomy-levels.md](references/autonomy-levels.md)).
