# Governance: how Operant evolves without drifting

A framework with a prompt, a set of code gates, and an eval suite has three copies of every rule. They drift. A rule tightened in the constitution but not in the eval is untested; a gate added in code but not in the prompt produces confusing denials; an eval that checks a behavior the prompt no longer requires fails for no reason. This file defines the discipline that keeps them in agreement: the same discipline the framework asks of an agent, applied to the framework itself.

## The single source of truth

[registry/rules.json](registry/rules.json) is authoritative. Every behavioral rule has one entry naming: the principle it serves, the failure it prevents, the layers that own it (PROMPT, RETRIEVAL, HARNESS_POLICY, CODE_GUARD, EVAL_ONLY), the reference chapter that teaches it, the enforcement gate that guarantees it (if any), the schema that structures it (if any), and the eval that proves it. To understand a rule's full footprint, start there.

Two words in that vocabulary carry a promise. `CODE_GUARD` means a script in this bundle enforces the rule; the gate's `implemented_by` field in [enforcement/policy.rules.json](enforcement/policy.rules.json) names the script, and the release check refuses a `CODE_GUARD` rule whose gate names none. `HARNESS_POLICY` means the host or the deployment provides the guard; the rule's note says which one. A spec section is a design, not a guard, and the registry never calls it one.

## The change protocol

When you add, remove, or materially change a rule:

1. **Edit the registry entry first.** Decide which layers own it. A rule that only lives in `PROMPT` is a hope; a rule marked `CODE_GUARD` without a shipped gate is a lie. Resolve that before writing prose.
2. **Update every artifact the entry names.** If the entry lists a reference, a gate, and an eval, all three change together in the same commit. The registry is the checklist.
3. **Keep the confirmation schemas in step.** If the change alters what a human must see before a Tier 3 action, the relevant schema in [schemas/](schemas/) changes too.
4. **Add or update the eval.** A behavior with no eval cannot be claimed as a property of the framework; it is an aspiration. Every anti-pattern in [references/failure-modes.md](references/failure-modes.md) is an eval waiting for a fixture. A scenario whose deterministic rule is prose must carry its `tool_rules` mapping, or the validator rejects it, because an unmapped rule passes vacuously.
5. **Re-run the suite.** At minimum the smoke test; the full suite before you tag a release. A change that drops a safety-cluster eval blocks the release. A recorded run is tied to the scenario and fixture hashes it ran on; the release check warns when an adoption-blocking scenario has changed since the newest certification run, and the certification claims in the bundle name the suite version they were earned on.
6. **Rebuild the compiled editions.** `dist/one-page.md` and `dist/single-file.md` are hand-maintained views of the constitution. Each carries a version stamp line, `<!-- operant-dist: x.y.z -->`, that the release check compares to the bundle version; update both in the same commit as SKILL.md so they cannot drift a release behind. SKILL.md is the superset: no principle wording may appear in a dist edition that the core lacks.
7. **Run the mechanical checks.** Every touched gate script's `--self-test` (policy-gate, injection-sentinel, shield), `evals/eval-runner.py validate` and `self-test`, `claude plugin validate .`, then `tools/release-check.py <bundle> --mirror <mirror>`. The release check enforces steps 1 to 4 and 6 as code: version agreement across seven fields, every gate in `policy.rules.json` has a spec section and a registry rule, every `CODE_GUARD` gate names its script, every registry rule's eval has a scenario file whose filename prefix equals its id, every scenario with a fixture kind has its fixture, every reference and schema path exists, the dist stamps match, and the mirror is byte-identical except for the deployment overlay.

## The sync rule (prompt and enforcement)

Hooks, gates, and skill text must agree. A gate blocking something the skill never mentions produces denials the agent cannot reason about; a skill rule with no gate is acceptable trust, but it should be a deliberate choice, not an oversight. When you edit one, check the other: [enforcement/generic-policy-spec.md](enforcement/generic-policy-spec.md) and [enforcement/policy.rules.json](enforcement/policy.rules.json) are the enforcement half; the registry tells you which prompt rule each gate backs. The same rule binds a deployment: a deployment that gates a surface the bundle does not, or chooses not to gate a surface the bundle recommends, records that choice in its deployment notes.

## The ratchet rule (autonomy)

Autonomy levels only go up after the enforcement and audit they require are in place and have passed their evals, never before ([references/autonomy-levels.md](references/autonomy-levels.md)). Raising a deployment from L2 to L3 is a governance event: it requires the L3 gate set, the audit log, and a passing certification run, not a config toggle. The runner refuses a certification run without sandbox settings and reports every required gate that is not wired, so a scorecard can no longer say `ready` with a required gate absent.

## Versioning

Semantic versioning on the bundle as a whole, recorded in [CHANGELOG.md](CHANGELOG.md):

- **Major:** a change to the Ten Principles or the tier and level taxonomy (anything that changes what "compliant" means).
- **Minor:** a new playbook, reference, schema, gate, or eval; a new adaptation.
- **Patch:** wording, fixes, tuning a gate pattern, correcting a link.

The version lives in seven places that must agree: the `meta.version` fields of `registry/rules.json` and `enforcement/policy.rules.json`, `.claude-plugin/plugin.json`, both fields of `.claude-plugin/marketplace.json`, `SUITE_VERSION` in `evals/eval-runner.py`, the top CHANGELOG entry, and the two dist stamps. The top changelog entry names every gate and eval id whose file changed in the release; the release check warns when one is missing.

## What not to do

- Don't add a rule because it sounds wise. Every rule costs context budget and eval maintenance; a rule that doesn't prevent a nameable failure is subtraction disguised as addition.
- Don't broaden a gate pattern to catch a near-miss. Every false positive teaches the model and the user to route around the gate. Normalize the input or add a project-specific pattern instead.
- Don't let the prompt grow unbounded. The constitution is always loaded; depth belongs in retrieved chapters, and deployment facts belong in the deployment's own notes, not in the overlay. If the core is growing, something wants to be a reference, not a principle.
- Don't ship a claim the eval suite can't back. The whole point of Operant is that discipline is a tested property, not a vibe. A certification claim names the suite version and the gate set it was earned on.
- Don't ship a gate without its owning rule and proving eval, and don't call a script self-tested until it carries a `--self-test`. Both happened once; the release check now refuses the first, and the second is what the self-test corpus is for.
- Don't raise an autonomy level because the model got smarter. A new model tier means a new certification run, not a new level.
- **Remove what stopped firing.** Every rule and every gate pattern costs context, false positives, and maintenance. At each minor release, list the rules that produced no eval failure and no gate hit since the last release, consider disabling them one at a time in the suite, and keep only those whose removal drops a score. A harness only grows unless something prunes it, and a rule the model no longer needs teaches it to route around the rest.
- Don't let the bundle break its own style. Every quoted model-output block under `examples/` follows the prose mechanics in [references/communication.md](references/communication.md); the chapters were brought to the same style in 1.5.0, and a chapter that splices again is wrong, not exempt.
