#!/usr/bin/env python3
"""Operant release check - mechanical lint for the drift GOVERNANCE prohibits.

Checks, in order:
  1. Version agreement: registry/rules.json, enforcement/policy.rules.json,
     .claude-plugin/plugin.json, .claude-plugin/marketplace.json (both fields),
     evals/eval-runner.py SUITE_VERSION, and the top CHANGELOG.md entry must
     all name the same version.
  2. Compiled editions exist: dist/one-page.md and dist/single-file.md.
  3. Governance cross-checks (added 1.4.0 after G10 shipped in code with no
     spec entry, registry rule, eval, or changelog line - the change protocol
     was prose only, and prose drifted):
       a. every gate in policy.rules.json has a `## G<id>` section in
          enforcement/generic-policy-spec.md;
       b. every gate is referenced by at least one registry rule (`gate`);
       c. every registry rule's eval_id has a scenario file
          evals/scenarios/<id>-*.json;
       d. every scenario whose fixture.kind is not `none` has
          evals/fixtures/<id>/fixture.json;
       e. every scenario file's id appears in at least one registry rule
          (an eval nothing claims is dead weight - warn only).
  4. Mirror parity (--mirror PATH): every file in the bundle exists in the
     mirror with identical content (SHA-256), and vice versa. Files that may
     legitimately differ or exist on one side only are declared below, not
     silently skipped.

Exit 0 = release-clean; exit 1 = drift found. Stdlib only.
"""
import argparse
import hashlib
import json
import os
import re
import sys

# The deployed bundle's SKILL.md may carry a project overlay on top of the
# constitution; content difference is a deployment feature, not drift.
ALLOW_CONTENT_DIFF = {"SKILL.md"}
SKIP_DIRS = (".git", "__pycache__")


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


def check_versions(root: str, violations: list, notes: list):
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
        with open(os.path.join(root, "CHANGELOG.md"), encoding="utf-8") as f:
            m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", f.read(), re.MULTILINE)
        if m:
            versions["CHANGELOG.md (top entry)"] = m.group(1)
        else:
            violations.append("version: no '## [x.y.z]' heading found in CHANGELOG.md")
    except Exception as e:
        violations.append("version: cannot read CHANGELOG.md: %s" % e)
    try:
        with open(os.path.join(root, "evals", "eval-runner.py"), encoding="utf-8") as f:
            m = re.search(r'^SUITE_VERSION\s*=\s*"(\d+\.\d+\.\d+)"', f.read(), re.MULTILINE)
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


def check_governance(root: str, violations: list, notes: list):
    try:
        policy = read_json(root, "enforcement/policy.rules.json")
        registry = read_json(root, "registry/rules.json")
    except Exception as e:
        violations.append("governance: cannot read policy/registry: %s" % e)
        return
    try:
        with open(os.path.join(root, "enforcement", "generic-policy-spec.md"), encoding="utf-8") as f:
            spec_headings = set(re.findall(r"^## (G\d+)\b", f.read(), re.MULTILINE))
    except Exception as e:
        violations.append("governance: cannot read generic-policy-spec.md: %s" % e)
        spec_headings = set()

    gate_ids = [g["id"] for g in policy.get("gates", [])]
    rules = registry.get("rules", [])
    registry_gates = {r.get("gate") for r in rules if r.get("gate")}
    registry_evals = {r.get("eval_id") for r in rules if r.get("eval_id")}

    for gid in gate_ids:
        if gid not in spec_headings:
            violations.append("governance: gate %s is in policy.rules.json but has no '## %s' section in generic-policy-spec.md" % (gid, gid))
        if gid not in registry_gates:
            violations.append("governance: gate %s is in policy.rules.json but no registry rule names it (gate) - it has no owning rule or proving eval" % gid)
    if gate_ids:
        notes.append("governance: %d gate(s) in policy.rules.json checked against spec + registry" % len(gate_ids))

    scen_dir = os.path.join(root, "evals", "scenarios")
    scenario_files = {}
    if os.path.isdir(scen_dir):
        for name in os.listdir(scen_dir):
            m = re.match(r"^(E\d+[a-z]?)-.*\.json$", name)
            if m:
                scenario_files[m.group(1)] = name
    for r in rules:
        eid = r.get("eval_id")
        if eid and eid not in scenario_files:
            violations.append("governance: registry rule %s names eval %s but evals/scenarios/%s-*.json does not exist" % (r.get("id"), eid, eid))
    for eid, name in sorted(scenario_files.items()):
        try:
            s = read_json(root, "evals/scenarios/" + name)
        except Exception as e:
            violations.append("governance: scenario %s unreadable: %s" % (name, e))
            continue
        kind = (s.get("fixture") or {}).get("kind", "none")
        if kind != "none" and not os.path.isfile(os.path.join(root, "evals", "fixtures", eid, "fixture.json")):
            violations.append("governance: scenario %s has fixture.kind=%s but evals/fixtures/%s/fixture.json is missing" % (eid, kind, eid))
        if eid not in registry_evals:
            notes.append("warn: scenario %s is claimed by no registry rule" % eid)
    if scenario_files:
        notes.append("governance: %d registry rule(s) and %d scenario(s) cross-checked" % (len(rules), len(scenario_files)))


def main():
    ap = argparse.ArgumentParser(description="Operant release check")
    ap.add_argument("bundle", help="bundle root (the installable skill)")
    ap.add_argument("--mirror", help="public mirror/export root to compare against")
    args = ap.parse_args()
    violations, notes = [], []

    check_versions(args.bundle, violations, notes)

    for rel in ("dist/one-page.md", "dist/single-file.md"):
        if not os.path.isfile(os.path.join(args.bundle, rel)):
            violations.append("dist: missing %s" % rel)

    check_governance(args.bundle, violations, notes)

    if args.mirror:
        b, m = walk(args.bundle), walk(args.mirror)
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

    for n in notes:
        print("   ok  " + n)
    for v in violations:
        print("DRIFT  " + v)
    print("release-check: " + ("CLEAN" if not violations else "%d violation(s)" % len(violations)))
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
