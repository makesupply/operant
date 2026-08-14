#!/usr/bin/env python3
"""Operant release check - mechanical lint for the drift GOVERNANCE prohibits.

Checks, in order:
  1. Version agreement: registry/rules.json, enforcement/policy.rules.json,
     .claude-plugin/plugin.json, and the top CHANGELOG.md entry must all name
     the same version.
  2. Compiled editions exist: dist/one-page.md and dist/single-file.md.
  3. Mirror parity (--mirror PATH): every file in the bundle exists in the
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
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for name in filenames:
            p = os.path.join(dirpath, name)
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            out[rel] = p
    return out


def check_versions(root: str, violations: list, notes: list):
    versions = {}
    for rel, extract in (
        ("registry/rules.json", lambda d: d["meta"]["version"]),
        ("enforcement/policy.rules.json", lambda d: d["meta"]["version"]),
        (".claude-plugin/plugin.json", lambda d: d["version"]),
    ):
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as f:
                versions[rel] = extract(json.load(f))
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
    if versions and len(set(versions.values())) == 1:
        notes.append("version: all sources agree on %s" % next(iter(versions.values())))
    elif len(set(versions.values())) > 1:
        violations.append("version drift: " + ", ".join(
            "%s=%s" % (k, v) for k, v in sorted(versions.items())))


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
