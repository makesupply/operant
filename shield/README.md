# Operant Shield — Auditing the Agent's Own Configuration Surface

The security chapter tells the agent to distrust untrusted input. Shield turns that same suspicion on the agent's *own configuration* — the CLAUDE.md files, `settings.json`, hook scripts, MCP configs, and rule files it auto-loads and trusts implicitly. That surface is the highest-leverage place to plant an attack: a hidden instruction in an auto-loaded CLAUDE.md retasks the agent on every run; a leaked credential in a committed config is exfiltration-ready; an over-broad permission is a standing liability. Shield is a static linter for exactly those four risks.

It is the mechanized form of the [security-posture](../references/security-posture.md) and [threat-model](../references/threat-model.md) chapters: prose becomes a check you can run in CI.

## What it scans for

| Category | Catches |
|---|---|
| **secrets** | AWS keys, GitHub/Slack/Shopify/Google/OpenAI-style tokens, private-key blocks, inline `password=`/`api_key=` credentials committed into config |
| **injection** | instruction-shaped text ("ignore previous instructions", "reveal your system prompt", "don't tell the user") hidden in **auto-loaded** files (CLAUDE.md, SKILL.md, `.mdc` rules) |
| **permissions** | over-broad allow-rules in `settings.json` — `Bash(*)`, `WebFetch(*)`, wildcard-everything |
| **hook-risk** | hooks that pipe remote scripts into a shell, disable safety flags (`--no-verify`), `eval()` dynamic code, or hint at disabling gates |

The design follows the same rules as the enforcement gates: **deterministic** (structural patterns, not inferred intent), **tuned narrow** (a placeholder filter skips documentation examples so `your_api_key_here` doesn't cry wolf), and **read-only** — Shield reports, it never edits.

## Usage

```bash
python shield/shield.py [root]                 # human report; exit 1 if HIGH found
python shield/shield.py [root] --json          # machine-readable findings
python shield/shield.py [root] --fail-on medium  # stricter CI gate
python shield/shield.py self-test              # verify the scanner against planted risks
```

Findings are ranked most-severe-first, each with category, label, file, line, and the offending excerpt. Exit code is 1 when anything at or above `--fail-on` (default `high`) is present — so it drops straight into a pre-commit hook or CI job:

```yaml
# CI: fail the build if the agent's config surface carries a HIGH risk
- run: python operant/shield/shield.py . --fail-on high
```

## Tuning and opt-out

- **Opt a file out** (a scanner's own pattern-definition source, a fixtures file, docs that quote the patterns) with `operant-shield: ignore-file` in its first 15 lines — the same idea as `# nosec`/`# noqa`. Operant's own tool sources carry this marker so Shield doesn't flag its own regex strings.
- **Project-specific patterns** (your deploy tokens, your prod database names) belong added to the pattern lists directly, not bought by broadening the generic ones — every false positive teaches people to ignore the tool.
- **Placeholder filter**: lines containing `example`, `placeholder`, `your_key`, `<...>`, `xxxx`, or `redact` are skipped for secrets, so documentation and templates don't generate noise. The trade-off: a real secret literally named like a placeholder slips through — acceptable, because such a secret is already broken by being guessable.

## What Shield is and isn't

- **Is**: a config-surface auditor — the *files that configure the agent*.
- **Isn't**: a general SAST tool for the application code the agent writes. That's the [code-review playbook](../playbooks/code-review.md)'s job and your existing linters'. Shield's scope is deliberately the agent's own trusted-input surface, which nothing else watches.

Run it after any change to your CLAUDE.md, hooks, or settings — and especially before adopting a third-party skill/rules bundle, where a planted instruction or an over-broad permission is exactly the supply-chain risk the [security posture](../references/security-posture.md) warns about. Auditing a bundle's config surface *before* trusting it is the single highest-value time to run Shield.
