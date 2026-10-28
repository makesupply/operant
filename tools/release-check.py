#!/usr/bin/env python3
"""Operant release check - mechanical lint for the drift GOVERNANCE prohibits.

Checks, in order:
  1. Version agreement: registry/rules.json, enforcement/policy.rules.json,
     .claude-plugin/plugin.json, .claude-plugin/marketplace.json (both fields),
     evals/eval-runner.py SUITE_VERSION, and the top CHANGELOG.md entry must
     all name the same version.
  2. Compiled editions exist and are current (H7): dist/one-page.md and
     dist/single-file.md each carry the line `<!-- operant-dist: <version> -->`
     naming the bundle version. A compile with no provenance line is stale by
     definition; the evals inject dist/one-page.md, so a stale compile
     certifies a constitution nobody ships.
  3. Governance cross-checks (added 1.4.0 after G10 shipped in code with no
     spec entry, registry rule, eval, or changelog line; extended 1.5.0 after
     the C5 review found CODE_GUARD claimed for four gates no script
     implements):
       a. every gate in policy.rules.json has a `## G<id>` section in
          enforcement/generic-policy-spec.md;
       b. every gate is referenced by at least one registry rule (`gate`);
       c. every registry rule's eval_id (and additional_eval_ids) has a
          scenario file evals/scenarios/<id>-*.json;
       d. every scenario whose fixture.kind is not `none` has
          evals/fixtures/<id>/fixture.json;
       e. every scenario file's id appears in at least one registry rule
          (an eval nothing claims is dead weight - warning only);
       H1. a registry rule may carry CODE_GUARD only when its gate's
           `implemented_by` is non-null and that script exists; a gate with
           `implemented_by: null` is a spec the deployment must provide, and
           the rule's layer is HARNESS_POLICY;
       H8. registry -> policy: a rule's `gate` must exist in policy.rules.json;
           `reference` and `schema` paths must exist; the scenario's
           `principle` must equal the rule's (int rendered as string; null is
           "Security"; a rule may set `scenario_principle` when the scenario
           files itself under a label such as "Calibration");
       H9. a scenario file's name prefix must equal its `id` field (the runner
           keys by `id`, this check used to key by filename, and the two could
           disagree); two files with one id is a violation;
       H3. with --sandbox-settings PATH: for every scenario that declares a
           `vector` and is claimed by a gate-backed registry rule, the hook
           that implements the gate must have a matcher covering every tool in
           the vector (a sentinel wired on WebFetch cannot fire on a Read).
  4. Changelog and runs (warnings and notes; never flip the exit code):
       H11. every G<n>/E<n> id whose file changed since the previous
            `## [x.y.z]` changelog version (git diff against that version's
            tag, when one exists) must be mentioned in the top entry;
       H4.  every blocks_adoption scenario whose sha256 (scenario and fixture)
            differs from results[].scenario_sha256 / fixture_sha256 recorded in
            the newest certification run's scorecard is reported as changed;
       H12. the newest certification run's suite_version behind the bundle
            version is noted.
  5. Mirror parity (--mirror PATH): every file in the bundle exists in the
     mirror with identical content (SHA-256), and vice versa. Files that may
     legitimately differ or exist on one side only are declared below, not
     silently skipped.

Exit 0 = release-clean; exit 1 = drift found. Warnings and notes never change
the exit code. Stdlib only. `--self-test` exercises every 1.5.0 check on
temporary fixtures.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# The deployed bundle's SKILL.md may carry a project overlay on top of the
# constitution; content difference is a deployment feature, not drift.
ALLOW_CONTENT_DIFF = {"SKILL.md"}
SKIP_DIRS = (".git", "__pycache__")
DIST_FILES = ("dist/one-page.md", "dist/single-file.md")
DIST_MARK = re.compile(r"<!--\s*operant-dist:\s*(\d+\.\d+\.\d+)\s*-->")
SCENARIO_NAME = re.compile(r"^(E\d+[a-z]?)-.*\.json$")
ID_WORD = re.compile(r"\b([GE]\d+[a-z]?)\b")


def mirror_only_allowed(rel: str) -> bool:
    # The public mirror may carry extras the installable bundle does not ship.
    return rel.startswith("docs/") or rel.endswith(".zip")


def bundle_only_allowed(rel: str) -> bool:
    # The installable bundle may carry tooling the mirror regenerates.
    return False


def sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(root: str) -> dict:
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith((".pyc", ".pyo")):
                continue
            p = os.path.join(dirpath, name)
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            out[rel] = p
    return out


def read_json(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return json.load(f)


def read_text(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return f.read()


def version_tuple(v):
    try:
        return tuple(int(x) for x in v.split("."))
    except Exception:
        return (0,)


# ---------------------------------------------------------------------------
# 1. Versions
# ---------------------------------------------------------------------------

def check_versions(root: str, violations: list, notes: list):
    """Returns the bundle version (registry meta.version when readable)."""
    versions = {}
    for rel, extract in (
        ("registry/rules.json", lambda d: d["meta"]["version"]),
        ("enforcement/policy.rules.json", lambda d: d["meta"]["version"]),
        (".claude-plugin/plugin.json", lambda d: d["version"]),
        (".claude-plugin/marketplace.json (metadata)", lambda d: d["metadata"]["version"]),
        (".claude-plugin/marketplace.json (plugin)", lambda d: d["plugins"][0]["version"]),
    ):
        try:
            versions[rel] = extract(read_json(root, rel.split(" ")[0]))
        except Exception as e:
            violations.append("version: cannot read %s: %s" % (rel, e))
    try:
        m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", read_text(root, "CHANGELOG.md"), re.MULTILINE)
        if m:
            versions["CHANGELOG.md (top entry)"] = m.group(1)
        else:
            violations.append("version: no '## [x.y.z]' heading found in CHANGELOG.md")
    except Exception as e:
        violations.append("version: cannot read CHANGELOG.md: %s" % e)
    try:
        m = re.search(r'^SUITE_VERSION\s*=\s*"(\d+\.\d+\.\d+)"', read_text(root, "evals/eval-runner.py"), re.MULTILINE)
        if m:
            versions["evals/eval-runner.py (SUITE_VERSION)"] = m.group(1)
        else:
            violations.append("version: SUITE_VERSION not found in evals/eval-runner.py")
    except Exception as e:
        violations.append("version: cannot read evals/eval-runner.py: %s" % e)
    if versions and len(set(versions.values())) == 1:
        notes.append("version: all %d sources agree on %s" % (len(versions), next(iter(versions.values()))))
    elif len(set(versions.values())) > 1:
        violations.append("version drift: " + ", ".join(
            "%s=%s" % (k, v) for k, v in sorted(versions.items())))
    return versions.get("registry/rules.json")


# ---------------------------------------------------------------------------
# 2. Dist provenance (H7)
# ---------------------------------------------------------------------------

def check_dist(root: str, version, violations: list, notes: list):
    for rel in DIST_FILES:
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            violations.append("dist: missing %s" % rel)
            continue
        m = DIST_MARK.search(read_text(root, rel))
        if not m:
            violations.append("H7 dist: %s carries no '<!-- operant-dist: <version> -->' line; the compile is unprovenanced and counts as stale" % rel)
        elif version and m.group(1) != version:
            violations.append("H7 dist: %s was built for %s, bundle is %s; regenerate the compiled editions" % (rel, m.group(1), version))
        else:
            notes.append("H7 dist: %s built for %s" % (rel, m.group(1)))


# ---------------------------------------------------------------------------
# 3. Governance
# ---------------------------------------------------------------------------

def rule_principle(rule) -> str:
    """The principle label a scenario must carry to match this rule."""
    if rule.get("scenario_principle"):
        return str(rule["scenario_principle"])
    p = rule.get("principle")
    if p is None:
        return "Security"
    return str(p)


def rule_eval_ids(rule) -> list:
    ids = []
    if rule.get("eval_id"):
        ids.append(rule["eval_id"])
    for e in rule.get("additional_eval_ids") or []:
        if e not in ids:
            ids.append(e)
    return ids


def load_scenarios(root: str, violations: list):
    """H9: filename prefix == id; duplicate ids violate. Returns {id: (name, scenario)}."""
    scen_dir = os.path.join(root, "evals", "scenarios")
    out = {}
    if not os.path.isdir(scen_dir):
        return out
    for name in sorted(os.listdir(scen_dir)):
        m = SCENARIO_NAME.match(name)
        if not m:
            continue
        prefix = m.group(1)
        try:
            s = read_json(root, "evals/scenarios/" + name)
        except Exception as e:
            violations.append("governance: scenario %s unreadable: %s" % (name, e))
            continue
        sid = s.get("id")
        if sid != prefix:
            violations.append("H9 governance: scenario file %s has id %r; the runner keys by id and would file it as %s" % (name, sid, sid))
        key = sid if isinstance(sid, str) and sid else prefix
        if key in out:
            violations.append("H9 governance: scenario id %s is declared by both %s and %s; the runner keeps one and silently drops the other" % (key, out[key][0], name))
            continue
        out[key] = (name, s)
    return out


def matcher_covers(matcher, tool: str) -> bool:
    if matcher in (None, "", "*"):
        return True
    try:
        return re.fullmatch(matcher, tool) is not None
    except re.error:
        return tool in [x.strip() for x in str(matcher).split("|")]


def load_sandbox_hooks(path: str):
    """Flatten a Claude Code settings file into [(event, matcher, command, statusMessage)]."""
    with open(path, encoding="utf-8") as f:
        settings = json.load(f)
    out = []
    for event, entries in (settings.get("hooks") or {}).items():
        for entry in entries or []:
            matcher = entry.get("matcher", "")
            for h in entry.get("hooks") or []:
                out.append((event, matcher, h.get("command", ""), h.get("statusMessage", "")))
    return out


def gate_hooks(gate, hooks):
    """The sandbox hooks that implement a gate: by script basename, else by gate id in the status message."""
    gid = gate["id"]
    impl = gate.get("implemented_by")
    found = []
    for event, matcher, command, status in hooks:
        if impl and os.path.basename(impl) in command:
            found.append((event, matcher))
        elif re.search(r"\b%s\b" % re.escape(gid), status or ""):
            found.append((event, matcher))
    return found


def check_governance(root: str, violations: list, warnings: list, notes: list, sandbox_settings=None):
    try:
        policy = read_json(root, "enforcement/policy.rules.json")
        registry = read_json(root, "registry/rules.json")
    except Exception as e:
        violations.append("governance: cannot read policy/registry: %s" % e)
        return
    try:
        spec_headings = set(re.findall(r"^## (G\d+)\b", read_text(root, "enforcement/generic-policy-spec.md"), re.MULTILINE))
    except Exception as e:
        violations.append("governance: cannot read generic-policy-spec.md: %s" % e)
        spec_headings = set()

    gates = {g["id"]: g for g in policy.get("gates", [])}
    rules = registry.get("rules", [])
    registry_gates = {r.get("gate") for r in rules if r.get("gate")}
    registry_evals = set()
    for r in rules:
        registry_evals.update(rule_eval_ids(r))

    # a, b, and the implemented_by contract on the gate side
    for gid, g in gates.items():
        if gid not in spec_headings:
            violations.append("governance: gate %s is in policy.rules.json but has no '## %s' section in generic-policy-spec.md" % (gid, gid))
        if gid not in registry_gates:
            violations.append("governance: gate %s is in policy.rules.json but no registry rule names it (gate) - it has no owning rule or proving eval" % gid)
        if "implemented_by" not in g:
            violations.append("H1 governance: gate %s has no implemented_by field (a script path, or null for a spec-only gate)" % gid)
        elif g["implemented_by"] and not os.path.isfile(os.path.join(root, g["implemented_by"])):
            violations.append("H1 governance: gate %s names implemented_by %s but that file does not exist" % (gid, g["implemented_by"]))
        if not g.get("hook_events"):
            violations.append("H1 governance: gate %s has no hook_events" % gid)
    if gates:
        notes.append("governance: %d gate(s) in policy.rules.json checked against spec + registry" % len(gates))

    scenarios = load_scenarios(root, violations)

    # H1 and H8 on the registry side
    for r in rules:
        rid = r.get("id")
        gid = r.get("gate")
        layers = r.get("layers") or []
        if gid and gid not in gates:
            violations.append("H8 governance: registry rule %s names gate %s, which is not in policy.rules.json" % (rid, gid))
        if "CODE_GUARD" in layers:
            if not gid:
                violations.append("H1 governance: registry rule %s claims CODE_GUARD with no gate" % rid)
            elif gid in gates and not gates[gid].get("implemented_by"):
                violations.append("H1 governance: registry rule %s claims CODE_GUARD but gate %s has implemented_by: null; the bundle ships the spec only, so the layer is HARNESS_POLICY and the note names the deployment's guard" % (rid, gid))
        for field in ("reference", "schema"):
            path = r.get(field)
            if path and not os.path.isfile(os.path.join(root, path)):
                violations.append("H8 governance: registry rule %s names %s %s, which does not exist" % (rid, field, path))
        for eid in rule_eval_ids(r):
            if eid not in scenarios:
                violations.append("governance: registry rule %s names eval %s but evals/scenarios/%s-*.json does not exist" % (rid, eid, eid))
                continue
            sp = scenarios[eid][1].get("principle")
            want = rule_principle(r)
            if str(sp) != want:
                violations.append("H8 governance: registry rule %s is principle %s but scenario %s says principle %r" % (rid, want, eid, sp))

    # c, d, e on the scenario side
    for eid, (name, s) in sorted(scenarios.items()):
        kind = (s.get("fixture") or {}).get("kind", "none")
        if kind != "none" and not os.path.isfile(os.path.join(root, "evals", "fixtures", eid, "fixture.json")):
            violations.append("governance: scenario %s has fixture.kind=%s but evals/fixtures/%s/fixture.json is missing" % (eid, kind, eid))
        if eid not in registry_evals:
            warnings.append("scenario %s is claimed by no registry rule" % eid)
    if scenarios:
        notes.append("governance: %d registry rule(s) and %d scenario(s) cross-checked" % (len(rules), len(scenarios)))

    # H3: sandbox wiring covers each gate-proving scenario's vector
    if sandbox_settings:
        try:
            hooks = load_sandbox_hooks(sandbox_settings)
        except Exception as e:
            violations.append("H3 sandbox: cannot read %s: %s" % (sandbox_settings, e))
            hooks = None
        if hooks is not None:
            checked = 0
            for r in rules:
                gid = r.get("gate")
                if not gid or gid not in gates:
                    continue
                for eid in rule_eval_ids(r):
                    if eid not in scenarios:
                        continue
                    vector = scenarios[eid][1].get("vector") or []
                    if not vector:
                        continue
                    checked += 1
                    found = gate_hooks(gates[gid], hooks)
                    if not found:
                        violations.append("H3 sandbox: gate %s (rule %s, scenario %s) is not wired in %s; the scenario's pass would be a prompt-layer pass" % (gid, r.get("id"), eid, os.path.basename(sandbox_settings)))
                        continue
                    for tool in vector:
                        if not any(matcher_covers(m, tool) for _, m in found):
                            violations.append("H3 sandbox: gate %s is wired on matcher(s) %s, which do not cover vector tool %r that scenario %s uses" % (gid, ", ".join(repr(m) for _, m in found), tool, eid))
            notes.append("H3 sandbox: %d gate-proving scenario vector(s) checked against %s" % (checked, os.path.basename(sandbox_settings)))


# ---------------------------------------------------------------------------
# 4. Changelog and runs
# ---------------------------------------------------------------------------

def git(root, *args):
    r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip() or "git exit %d" % r.returncode)
    return r.stdout


def check_changelog_ids(root: str, warnings: list, notes: list):
    """H11: ids whose files changed since the previous version must appear in the top entry."""
    try:
        text = read_text(root, "CHANGELOG.md")
    except Exception:
        return
    heads = list(re.finditer(r"^## \[(\d+\.\d+\.\d+)\]", text, re.MULTILINE))
    if len(heads) < 2:
        notes.append("H11 changelog: fewer than two version headings; nothing to diff against")
        return
    top_entry = text[heads[0].start():heads[1].start()]
    prev = heads[1].group(1)
    try:
        tags = set(git(root, "tag", "-l").split())
    except Exception as e:
        notes.append("H11 changelog: skipped (git unavailable: %s)" % str(e).splitlines()[0])
        return
    tag = next((t for t in ("v" + prev, prev, "operant-" + prev, "operant-v" + prev) if t in tags), None)
    if not tag:
        notes.append("H11 changelog: skipped (no tag for previous version %s; tag releases as v%s to enable it)" % (prev, prev))
        return
    try:
        prefix = git(root, "rev-parse", "--show-prefix").strip().replace("\\", "/")
        changed = [l.strip().replace("\\", "/") for l in git(root, "diff", "--name-only", tag, "--", ".").splitlines() if l.strip()]
    except Exception as e:
        notes.append("H11 changelog: skipped (git diff failed: %s)" % str(e).splitlines()[0])
        return
    rels = [c[len(prefix):] if prefix and c.startswith(prefix) else c for c in changed]
    ids = set()
    for rel in rels:
        m = re.match(r"^evals/scenarios/(E\d+[a-z]?)-", rel) or re.match(r"^evals/fixtures/(E\d+[a-z]?)/", rel)
        if m:
            ids.add(m.group(1))
            continue
        if rel == "enforcement/policy.rules.json":
            try:
                old = json.loads(git(root, "show", "%s:%s%s" % (tag, prefix, rel)))
                old_gates = {g["id"]: json.dumps(g, sort_keys=True) for g in old.get("gates", [])}
            except Exception:
                old_gates = {}
            try:
                new_gates = {g["id"]: json.dumps(g, sort_keys=True) for g in read_json(root, rel).get("gates", [])}
            except Exception:
                new_gates = {}
            for gid in set(old_gates) | set(new_gates):
                if old_gates.get(gid) != new_gates.get(gid):
                    ids.add(gid)
            continue
        if rel in ("enforcement/policy-gate.py", "enforcement/injection-sentinel.py", "enforcement/generic-policy-spec.md"):
            try:
                diff = git(root, "diff", "-U0", tag, "--", rel)
            except Exception:
                continue
            for line in diff.splitlines():
                if (line.startswith("+") and not line.startswith("+++")) or (line.startswith("-") and not line.startswith("---")):
                    ids.update(ID_WORD.findall(line))
    missing = sorted(i for i in ids if not re.search(r"\b%s\b" % re.escape(i), top_entry))
    for i in missing:
        warnings.append("H11 changelog: %s changed since %s but the top CHANGELOG entry does not mention it" % (i, tag))
    notes.append("H11 changelog: %d gate/eval id(s) changed since %s, %d unmentioned" % (len(ids), tag, len(missing)))


def newest_certification_run(root: str):
    runs_dir = os.path.join(root, "evals", "runs")
    best = None
    if not os.path.isdir(runs_dir):
        return None
    for name in sorted(os.listdir(runs_dir)):
        p = os.path.join(runs_dir, name, "scorecard.json")
        if not os.path.isfile(p):
            continue
        try:
            card = read_json(root, "evals/runs/%s/scorecard.json" % name)
        except Exception:
            continue
        run = card.get("run") or {}
        if run.get("mode") != "certification":
            continue
        key = (run.get("timestamp") or "", name)
        if best is None or key > best[0]:
            best = (key, name, card)
    return None if best is None else (best[1], best[2])


def check_runs(root: str, version, warnings: list, notes: list):
    """H12 (suite version behind) and H4 (blocks_adoption eval changed since its certification run)."""
    found = newest_certification_run(root)
    if not found:
        notes.append("H12 runs: no certification run under evals/runs/")
        return
    name, card = found
    suite = (card.get("run") or {}).get("suite_version", "")
    st, bt = version_tuple(suite), version_tuple(version or "")
    if version and st < bt:
        level = "major" if st[:1] != bt[:1] else ("minor" if st[:2] != bt[:2] else "patch")
        notes.append("H12 runs: newest certification run %s is on suite %s; bundle is %s (a %s version behind). Certification claims cite that run, not this version." % (name, suite, version, level))
    else:
        notes.append("H12 runs: newest certification run %s is on suite %s" % (name, suite))
    results = {r.get("eval_id"): r for r in card.get("results") or []}
    scen_dir = os.path.join(root, "evals", "scenarios")
    if not os.path.isdir(scen_dir):
        return
    unhashed, compared = 0, 0
    for fname in sorted(os.listdir(scen_dir)):
        m = SCENARIO_NAME.match(fname)
        if not m:
            continue
        try:
            s = read_json(root, "evals/scenarios/" + fname)
        except Exception:
            continue
        if not s.get("blocks_adoption"):
            continue
        eid = s.get("id") or m.group(1)
        rec = results.get(eid) or {}
        if not rec.get("scenario_sha256"):
            unhashed += 1
            continue
        compared += 1
        changed = sha(os.path.join(scen_dir, fname)) != rec["scenario_sha256"]
        fx = os.path.join(root, "evals", "fixtures", eid, "fixture.json")
        if rec.get("fixture_sha256") and os.path.isfile(fx) and sha(fx) != rec["fixture_sha256"]:
            changed = True
        if changed:
            warnings.append("H4 runs: eval %s changed since its last certification run (%s)" % (eid, name))
    if unhashed:
        notes.append("H4 runs: %s records no scenario hash for %d blocks_adoption eval(s); they cannot be compared (the runner records results[].scenario_sha256 and fixture_sha256 from 1.5.0)" % (name, unhashed))
    if compared:
        notes.append("H4 runs: %d blocks_adoption eval(s) compared against %s" % (compared, name))


# ---------------------------------------------------------------------------
# 5. Mirror parity (unchanged since 1.4.0)
# ---------------------------------------------------------------------------

def check_mirror(bundle: str, mirror: str, violations: list, notes: list):
    b, m = walk(bundle), walk(mirror)
    for rel in sorted(set(b) | set(m)):
        if rel in b and rel in m:
            if sha(b[rel]) != sha(m[rel]):
                if rel in ALLOW_CONTENT_DIFF:
                    notes.append("parity: %s differs (allowed: deployment overlay)" % rel)
                else:
                    violations.append("parity: %s differs between bundle and mirror" % rel)
        elif rel in m:
            if mirror_only_allowed(rel):
                notes.append("parity: %s mirror-only (allowed)" % rel)
            else:
                violations.append("parity: %s missing from bundle" % rel)
        else:
            if bundle_only_allowed(rel):
                notes.append("parity: %s bundle-only (allowed)" % rel)
            else:
                violations.append("parity: %s missing from mirror" % rel)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def run_checks(bundle: str, mirror=None, sandbox_settings=None):
    violations, warnings, notes = [], [], []
    version = check_versions(bundle, violations, notes)
    check_dist(bundle, version, violations, notes)
    check_governance(bundle, violations, warnings, notes, sandbox_settings)
    check_changelog_ids(bundle, warnings, notes)
    check_runs(bundle, version, warnings, notes)
    if mirror:
        check_mirror(bundle, mirror, violations, notes)
    return violations, warnings, notes


def report(violations, warnings, notes) -> int:
    for n in notes:
        print("   ok  " + n)
    for w in warnings:
        print("WARN   " + w)
    for v in violations:
        print("DRIFT  " + v)
    tail = "" if not warnings else ", %d warning(s)" % len(warnings)
    print("release-check: " + ("CLEAN" if not violations else "%d violation(s)" % len(violations)) + tail)
    return 1 if violations else 0


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _write(root, rel, content):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(content if isinstance(content, str) else json.dumps(content, indent=2))


def _fixture_bundle(root, version="1.5.0"):
    """A minimal release-clean bundle."""
    _write(root, "registry/rules.json", {"meta": {"version": version}, "rules": [
        {"id": "P1-a", "principle": 1, "layers": ["PROMPT", "EVAL_ONLY"], "reference": "references/a.md",
         "gate": None, "schema": "schemas/x.schema.json", "eval_id": "E1"},
        {"id": "P10-b", "principle": 10, "layers": ["PROMPT", "CODE_GUARD"], "reference": "references/a.md",
         "gate": "G1", "schema": None, "eval_id": "E2"},
        {"id": "X-c", "principle": None, "layers": ["PROMPT", "HARNESS_POLICY"], "reference": "references/a.md",
         "gate": "G4", "schema": None, "eval_id": "E3"},
    ]})
    _write(root, "enforcement/policy.rules.json", {"meta": {"version": version}, "gates": [
        {"id": "G1", "name": "destructive", "implemented_by": "enforcement/policy-gate.py", "hook_events": ["PreToolUse"]},
        {"id": "G4", "name": "external-send", "implemented_by": None, "hook_events": ["PreToolUse"]},
    ]})
    _write(root, "enforcement/generic-policy-spec.md", "## G1 x\n\n## G4 y\n")
    _write(root, "enforcement/policy-gate.py", "# stub\n")
    _write(root, ".claude-plugin/plugin.json", {"version": version})
    _write(root, ".claude-plugin/marketplace.json", {"metadata": {"version": version}, "plugins": [{"version": version}]})
    _write(root, "CHANGELOG.md", "# Changelog\n\n## [%s] - now\n\n- E1, G1 touched.\n\n## [1.4.3] - before\n\n- old\n" % version)
    _write(root, "evals/eval-runner.py", 'SUITE_VERSION = "%s"\n' % version)
    for rel in DIST_FILES:
        _write(root, rel, "# Operant\n\n<!-- operant-dist: %s -->\n" % version)
    _write(root, "references/a.md", "# a\n")
    _write(root, "schemas/x.schema.json", {"type": "object"})
    _write(root, "evals/scenarios/E1-a.json", {"id": "E1", "principle": "1", "fixture": {"kind": "none"}, "blocks_adoption": False})
    _write(root, "evals/scenarios/E2-b.json", {"id": "E2", "principle": "10", "fixture": {"kind": "repo"}, "blocks_adoption": True, "vector": ["Bash"]})
    _write(root, "evals/scenarios/E3-c.json", {"id": "E3", "principle": "Security", "fixture": {"kind": "none"}, "blocks_adoption": True})
    _write(root, "evals/fixtures/E2/fixture.json", {"eval_id": "E2"})


def _run(root, **kw):
    v, w, n = run_checks(root, **kw)
    return v, w, n


def _assert(cond, label, detail=""):
    print(("PASS  " if cond else "FAIL  ") + label + ("" if cond or not detail else "\n        " + detail))
    return 1 if cond else 0


def self_test() -> int:
    passed = total = 0
    tmp = tempfile.mkdtemp(prefix="operant-rc-")
    try:
        def fresh(name):
            root = os.path.join(tmp, name)
            _fixture_bundle(root)
            return root

        # 0. clean fixture
        root = fresh("clean")
        v, w, n = _run(root)
        total += 1; passed += _assert(not v and not w, "clean fixture: no violations, no warnings", "\n".join(v + w))

        # H1: CODE_GUARD on a spec-only gate
        root = fresh("h1")
        reg = read_json(root, "registry/rules.json"); reg["rules"][2]["layers"] = ["PROMPT", "CODE_GUARD"]
        _write(root, "registry/rules.json", reg)
        v, w, n = _run(root)
        total += 1; passed += _assert(any(x.startswith("H1 ") and "X-c" in x for x in v), "H1: CODE_GUARD with implemented_by null is a violation", "\n".join(v))
        root = fresh("h1b")
        pol = read_json(root, "enforcement/policy.rules.json"); pol["gates"][0]["implemented_by"] = "enforcement/missing.py"
        _write(root, "enforcement/policy.rules.json", pol)
        v, w, n = _run(root)
        total += 1; passed += _assert(any(x.startswith("H1 ") and "missing.py" in x for x in v), "H1: implemented_by naming an absent script is a violation", "\n".join(v))

        # H7: dist provenance
        root = fresh("h7")
        _write(root, "dist/one-page.md", "# no mark\n")
        _write(root, "dist/single-file.md", "<!-- operant-dist: 1.4.3 -->\n")
        v, w, n = _run(root)
        total += 1; passed += _assert(sum(x.startswith("H7 ") for x in v) == 2, "H7: missing mark and wrong-version mark are two violations", "\n".join(v))

        # H8: registry -> policy, paths, principle
        root = fresh("h8")
        reg = read_json(root, "registry/rules.json")
        reg["rules"][1]["gate"] = "G99"
        reg["rules"][0]["reference"] = "references/missing.md"
        reg["rules"][0]["schema"] = "schemas/missing.schema.json"
        reg["rules"][0]["principle"] = 2
        _write(root, "registry/rules.json", reg)
        v, w, n = _run(root)
        h8 = [x for x in v if x.startswith("H8 ")]
        total += 1; passed += _assert(len(h8) == 4 and any("G99" in x for x in h8) and any("missing.md" in x for x in h8)
                                      and any("missing.schema" in x for x in h8) and any("principle 2" in x for x in h8),
                                      "H8: unknown gate, missing reference, missing schema, principle mismatch", "\n".join(v))
        root = fresh("h8b")
        reg = read_json(root, "registry/rules.json"); reg["rules"][0]["principle"] = 2; reg["rules"][0]["scenario_principle"] = "1"
        _write(root, "registry/rules.json", reg)
        v, w, n = _run(root)
        total += 1; passed += _assert(not v, "H8: scenario_principle override and null->Security normalisation match", "\n".join(v))

        # H9: filename prefix vs id, duplicate ids
        root = fresh("h9")
        _write(root, "evals/scenarios/E5-x.json", {"id": "E1", "principle": "1", "fixture": {"kind": "none"}})
        v, w, n = _run(root)
        total += 1; passed += _assert(any(x.startswith("H9 ") and "E5-x.json" in x for x in v) and any("declared by both" in x for x in v),
                                      "H9: prefix/id mismatch and duplicate id are violations", "\n".join(v))

        # H3: sandbox wiring covers the vector
        root = fresh("h3")
        bad = os.path.join(root, "bad-settings.json")
        _write(root, "bad-settings.json", {"hooks": {"PreToolUse": [{"matcher": "PowerShell", "hooks": [{"type": "command", "command": "python policy-gate.py"}]}]}})
        v, w, n = _run(root, sandbox_settings=bad)
        total += 1; passed += _assert(any(x.startswith("H3 ") and "'Bash'" in x for x in v), "H3: matcher that misses the vector tool is a violation", "\n".join(v))
        good = os.path.join(root, "good-settings.json")
        _write(root, "good-settings.json", {"hooks": {"PreToolUse": [{"matcher": "Bash|PowerShell", "hooks": [{"type": "command", "command": "python policy-gate.py"}]}]}})
        v, w, n = _run(root, sandbox_settings=good)
        total += 1; passed += _assert(not v, "H3: matcher covering the vector is clean", "\n".join(v))
        none = os.path.join(root, "none-settings.json")
        _write(root, "none-settings.json", {"hooks": {}})
        v, w, n = _run(root, sandbox_settings=none)
        total += 1; passed += _assert(any(x.startswith("H3 ") and "not wired" in x for x in v), "H3: gate absent from the sandbox is a violation", "\n".join(v))

        # H4 + H12: certification run hashes and suite version
        root = fresh("h4")
        e2 = sha(os.path.join(root, "evals/scenarios/E2-b.json"))
        _write(root, "evals/runs/2026-09-x/scorecard.json", {"run": {"mode": "certification", "suite_version": "1.4.1", "timestamp": "2026-09-14T00:00:00+00:00"},
                                                             "results": [{"eval_id": "E2", "verdict": "pass", "scenario_sha256": e2, "fixture_sha256": "0" * 64},
                                                                         {"eval_id": "E3", "verdict": "pass", "scenario_sha256": "f" * 64}]})
        _write(root, "evals/runs/2026-07-y/scorecard.json", {"run": {"mode": "full", "suite_version": "1.2.0", "timestamp": "2026-07-01T00:00:00+00:00"}, "results": []})
        v, w, n = _run(root)
        h4 = [x for x in w if x.startswith("H4 ")]
        total += 1; passed += _assert(not v and len(h4) == 2 and all("2026-09-x" in x for x in h4) and any("E2 " in x for x in h4) and any("E3 " in x for x in h4),
                                      "H4: fixture-hash drift (E2) and scenario-hash drift (E3) warn, exit stays clean", "\n".join(v + w))
        total += 1; passed += _assert(any(x.startswith("H12 ") and "1.4.1" in x and "behind" in x for x in n), "H12: suite version behind the bundle is noted", "\n".join(n))

        # H11: changelog mentions changed ids (needs git)
        root = fresh("h11")
        try:
            git(root, "init", "-q")
            git(root, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
            git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base")
            git(root, "tag", "v1.4.3")
            _write(root, "evals/scenarios/E3-c.json", {"id": "E3", "principle": "Security", "fixture": {"kind": "none"}, "blocks_adoption": True, "title": "changed"})
            pol = read_json(root, "enforcement/policy.rules.json"); pol["gates"][1]["name"] = "renamed"
            _write(root, "enforcement/policy.rules.json", pol)
            _write(root, "enforcement/policy-gate.py", "# stub\n# G1 pattern tightened\n")
            v, w, n = _run(root)
            h11 = [x for x in w if x.startswith("H11 ")]
            total += 1; passed += _assert(not v and sorted(re.search(r": (\S+) changed", x).group(1) for x in h11) == ["E3", "G4"],
                                          "H11: E3 and G4 changed and unmentioned warn; E1 and G1 mentioned do not", "\n".join(v + w + n))
        except Exception as e:
            print("SKIP  H11: git not usable here (%s)" % str(e).splitlines()[0])

        # exit semantics: warnings never flip the exit code
        root = fresh("exit")
        _write(root, "evals/scenarios/E4-orphan.json", {"id": "E4", "principle": "1", "fixture": {"kind": "none"}})
        v, w, n = _run(root)
        total += 1; passed += _assert(not v and any("E4" in x for x in w), "exit: an orphan scenario warns and leaves the exit clean", "\n".join(v + w))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("release-check self-test: %d/%d" % (passed, total))
    return 0 if passed == total else 1


def main():
    ap = argparse.ArgumentParser(description="Operant release check")
    ap.add_argument("bundle", nargs="?", help="bundle root (the installable skill)")
    ap.add_argument("--mirror", help="public mirror/export root to compare against")
    ap.add_argument("--sandbox-settings", help="Claude Code settings file used for certification runs; enables H3 (gate matcher covers each scenario's vector)")
    ap.add_argument("--self-test", action="store_true", help="exercise every check on temporary fixtures and exit")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())
    if not args.bundle:
        ap.error("bundle root is required (or pass --self-test)")
    violations, warnings, notes = run_checks(args.bundle, args.mirror, args.sandbox_settings)
    sys.exit(report(violations, warnings, notes))


if __name__ == "__main__":
    main()
