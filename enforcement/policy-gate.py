#!/usr/bin/env python3
# operant-shield: ignore-file  (defines detection patterns; scanning it is noise)
"""Operant policy gate — consolidated PreToolUse enforcement for shell tools.

Implements the code-enforceable subset of the generic policy spec:
  G1 destructive commands, G2 history rewrites, G3 unbounded mutations,
  G6 secret staging, G10 whole-tree staging on a shared checkout (added
  2026-09-03). Exit 2 blocks the call and returns gate-specific guidance
  to the model; exit 0 allows.

Wiring (.claude/settings.json):
  "PreToolUse": [{"matcher": "Bash|PowerShell",
    "hooks": [{"type": "command", "command": "python <path>/policy-gate.py"}]}]

Self-test — run it after ANY pattern change, before trusting the change:
  python policy-gate.py --self-test

Design rules (see generic-policy-spec.md): deterministic, tuned narrow,
hands off to judgment with an actionable reason. Stdlib only.

1.4.0 (2026-09-14):
  * G6 key-shaped patterns require a standalone token: a lookbehind rejects a
    match that starts mid-word, and the OpenAI-style pattern also demands a
    tail with both an uppercase letter and a digit. The old pattern blocked
    read-only commands that merely mentioned URL slugs ("...desk-mcp-...",
    "...ersk-freeport-...") and a Slovak locale code. A wrong block teaches
    the operator to route around the gate, so the fix narrows.
  * G2 force-delete-branch is now case-sensitive: `git branch -d` (safe,
    merged-only) no longer trips the `-D` pattern under IGNORECASE.
  * `--self-test` added (the docs had claimed one since 1.1.0).
Keep the secret patterns in step with shield/shield.py.
"""
import json
import re
import sys

GATES = [
    # --- G1: destructive command gate ---
    ("G1", r"\brm\s+(-[a-zA-Z]*[rf][a-zA-Z]*\s+)+", "recursive/forced delete"),
    ("G1", r"\bRemove-Item\b.*-Recurse.*-Force|\bRemove-Item\b.*-Force.*-Recurse", "recursive forced delete"),
    ("G1", r"\bdel\s+/[sq]", "recursive/quiet Windows delete"),
    ("G1", r"\brd\s+/s|\brmdir\s+/s", "recursive directory delete"),
    ("G1", r"\bmkfs\.", "filesystem format"),
    ("G1", r">\s*/dev/sd[a-z]", "raw device write"),
    ("G1", r"\bDROP\s+(TABLE|DATABASE|SCHEMA)\b", "destructive SQL DROP"),
    ("G1", r"\bTRUNCATE\s+TABLE\b", "destructive SQL TRUNCATE"),
    # --- G2: history-rewrite gate ---
    ("G2", r"\bgit\s+push\s+[^\n]*--force(?!-with-lease)", "force push (use --force-with-lease)"),
    ("G2", r"\bgit\s+reset\s+--hard", "hard reset discards uncommitted work"),
    ("G2", r"\bgit\s+clean\s+-[a-zA-Z]*f", "git clean -f deletes untracked files"),
    ("G2", r"\bgit\s+checkout\s+\.(\s|$|;)", "checkout . discards all local changes"),
    ("G2", r"\bgit\s+(filter-branch|filter-repo)\b", "history rewrite across commits"),
    # Case-sensitive on purpose: `-d` refuses to delete an unmerged branch, `-D` does not.
    ("G2", r"\bgit\s+branch\s+(?-i:-D)\b", "force-delete branch (unmerged work may be lost)"),
    # --- G3: unbounded-mutation gate (heuristic: statement-level, no WHERE) ---
    ("G3", r"\bDELETE\s+FROM\s+[\w.\"\[\]`]+\s*(;|$)", "DELETE with no WHERE clause"),
    ("G3", r"\bUPDATE\s+[\w.\"\[\]`]+\s+SET\s+[^;]+?(;|$)(?<!WHERE)", None),  # handled specially below
    # --- G6: secret-staging tripwire ---
    ("G6", r"\bgit\s+(add|commit)\b[^\n]*(\.env(\.|\s|$|\")|id_rsa|id_ed25519|\.pem\b|\.key\b|credentials\.json|serviceaccount[^\s]*\.json)", "staging a likely secret file"),
    ("G6", r"(?<![A-Za-z0-9_])(?-i:AKIA)[0-9A-Z]{16}", "AWS access key in command"),
    ("G6", r"(?<![A-Za-z0-9_])ghp_[A-Za-z0-9]{36}", "GitHub token in command"),
    # Standalone lowercase `sk-` (the gate runs IGNORECASE; real keys are never `SK-`),
    # tail carries an uppercase letter AND a digit (real keys are mixed base62; URL
    # slugs are lowercase words). `sk-SK` is the Slovak locale code.
    ("G6", r"(?<![A-Za-z0-9_])(?-i:sk-)(?!SK\b)(?=[A-Za-z0-9\-_]{20,})(?=[A-Za-z0-9\-_]*[A-Z])(?=[A-Za-z0-9\-_]*\d)[A-Za-z0-9\-_]{20,}", "API secret key in command"),
    ("G6", r"(?<![A-Za-z0-9_])xox[baprs]-[A-Za-z0-9\-]{10,}", "Slack token in command"),
    ("G6", r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key material in command"),
]

# --- G10: whole-tree staging gate (added 2026-09-03) ---
# Several Claude sessions share this working tree. `git add -A/./--all/-u` and
# `git commit -a` sweep other sessions' in-flight files into the committer's
# snapshot (incident 2026-09-03: commit e7430d2 carried another session's
# finished deliverable). Patterns run on the command with quoted strings and
# heredoc bodies removed, so a commit MESSAGE that merely mentions "git add -A"
# does not trip the gate. The scheduled Tools/protection/daily_maintenance.py
# snapshot runs outside these hooks and is the only sanctioned whole-tree committer.
G10_PATTERNS = [
    (r"\bgit\s+add\b[^\n;&|]*\s-[a-zA-Z]*A[a-zA-Z]*(?=\s|$)", "git add -A stages every file in the tree"),
    (r"\bgit\s+add\b[^\n;&|]*\s--all(?=\s|$)", "git add --all stages every file in the tree"),
    (r"\bgit\s+add\b[^\n;&|]*\s(-u|--update)(?=\s|$)", "git add -u stages every tracked change"),
    (r"\bgit\s+add\b[^\n;&|]*\s(\.|:/|\*)(?=\s|$)", "git add . stages the whole tree"),
    (r"\bgit\s+commit\b[^\n;&|]*\s(-[a-zA-Z]*a[a-zA-Z]*|--all)(?=\s|$)", "git commit -a stages every tracked change"),
]
_LITERALS = re.compile(
    r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\2\b"  # heredoc bodies (commit messages, scripts)
    r"|'[^']*'|\"[^\"]*\"",                     # quoted strings
    re.DOTALL,
)

GUIDANCE = {
    "G1": ("Operant gate G1 (destructive command): {why}.\n"
           "Per safety.md: read the target's contents, state exact scope (count + names) "
           "and consequence, and get explicit user confirmation — or use the safer "
           "alternative (archive/move instead of delete, a scoped path instead of a "
           "recursive wildcard). If the user already approved this exact action, ask "
           "them to approve it through the permission prompt."),
    "G2": ("Operant gate G2 (history rewrite): {why}.\n"
           "Capture the working state first (what uncommitted/unpushed work exists, who "
           "shares this branch), then prefer: --force-with-lease, a revert commit, a "
           "stash, or a new branch. Confirm with the user before rewriting anything shared."),
    "G3": ("Operant gate G3 (unbounded mutation): {why}.\n"
           "Resolve the exact affected count from the real data, produce a preview/dry-run, "
           "and add the missing filter or an explicit full-table confirmation. Canary first: "
           "1 row, then 10, then the rest, reconciling counts each step."),
    "G6": ("Operant gate G6 (secret staging): {why}.\n"
           "Secrets never enter commits, commands, or new files. Move the value to the "
           "secret store / env var and reference it; add the file to ignore rules. If this "
           "secret was already exposed anywhere durable, tell the user now — rotation is "
           "time-sensitive."),
    "G10": ("Operant gate G10 (whole-tree staging): {why}.\n"
            "This checkout is shared by several concurrent Claude sessions, so a whole-tree "
            "add sweeps other sessions' in-flight files into your commit (2026-09-03 incident, "
            "commit e7430d2). Stage only the files THIS session created or edited, by explicit "
            "path: git add -- \"<file>\" \"<file>\" ... then commit. Run git status --short first "
            "and report the other dirty files as left for their owners. See "
            ".claude/skills/commit/SKILL.md. The scheduled daily_maintenance.py snapshot is the "
            "only sanctioned whole-tree committer."),
}

# Benign contexts G3's UPDATE heuristic must not fire on (reduce false positives).
UPDATE_SAFE = re.compile(r"\bWHERE\b", re.IGNORECASE)

# G1 exemption (1.4.1, from the 2026-09-14 Opus certification run, where the gate blocked
# `rm -rf __pycache__` twice and `rm -f /tmp/out_*.txt` once): deleting DERIVABLE state is
# Tier 1 per safety.md — build/tool caches and scratch under /tmp regenerate on demand.
# The exemption applies only when EVERY target of every rm in the command is derivable;
# `rm -rf /tmp` (the whole dir), `dist`, `build`, or any real path still blocks.
_RM_CALL = re.compile(r"\brm\s+((?:-[a-zA-Z]+\s+)+)([^;&|\n]*)", re.IGNORECASE)
DERIVABLE_TARGET = re.compile(
    r"^(\./)?(__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.tox|node_modules)/?$"
    r"|^/tmp/[^/\s.][^\s]*$")


def _rm_targets_all_derivable(command: str) -> bool:
    calls = list(_RM_CALL.finditer(command))
    if not calls:
        return False
    for m in calls:
        targets = [t.strip("'\"") for t in m.group(2).split() if not t.startswith("-")]
        if not targets or not all(DERIVABLE_TARGET.match(t) for t in targets):
            return False
    return True


def check(command: str):
    # G10 first, on the command with quoted strings / heredoc bodies stripped.
    stripped = _LITERALS.sub(" ", command)
    for pattern, why in G10_PATTERNS:
        if re.search(pattern, stripped, re.IGNORECASE):
            return "G10", why
    for gate, pattern, why in GATES:
        if why is None:
            continue  # placeholder rows handled separately
        if re.search(pattern, command, re.IGNORECASE):
            if gate == "G1" and why == "recursive/forced delete" and _rm_targets_all_derivable(command):
                continue  # Tier-1 derivable state: caches and /tmp scratch
            return gate, why
    # Special-case UPDATE-without-WHERE: only flag single-statement updates lacking WHERE.
    m = re.search(r"\bUPDATE\s+[\w.\"\[\]`]+\s+SET\b[^;]*", command, re.IGNORECASE)
    if m and not UPDATE_SAFE.search(m.group(0)):
        return "G3", "UPDATE with no WHERE clause"
    return None, None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # malformed input: never block on our own failure
    if data.get("tool_name") not in ("Bash", "PowerShell"):
        sys.exit(0)
    command = (data.get("tool_input") or {}).get("command", "") or ""
    gate, why = check(command)
    if gate:
        print(GUIDANCE[gate].format(why=why), file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Self-test. Token-shaped strings are assembled at runtime so that neither this
# file nor a shell command quoting it carries a key-shaped literal.
# ---------------------------------------------------------------------------

def _cases():
    real_key = "sk-" + "proj-" + "Ab3" * 6 + "Zz9" * 4          # mixed case + digits, 42 chars
    aws_key = "AKIA" + "IOSFODNN7EXAMPLE"
    zendesk = "https://geckoboard.com/blog/" + "zendesk" + "-mcp-the-different-options-compared-2026"
    maersk = "https://www.myshiptracking.com/vessels/" + "maersk" + "-freeport-mmsi-123456789-imo-9999999"
    slovak = '"voice": "' + "sk-SK" + '-x-sfg-network-tts-Default-2024-standard-A"'
    return [
        # (command, expected gate or None)
        ("ls -la", None),
        ("git status --short", None),
        ("rm -rf /tmp/scratch", None),          # scratch under /tmp is derivable
        ("rm -rf /tmp", "G1"),                  # the whole temp dir is not
        ("rm -r build/", "G1"),
        ("rm -rf __pycache__", None),           # Tier-1 derivable cache (Opus run, 2026-09-14)
        ("rm -rf __pycache__ && git status --porcelain", None),
        ("rm -f /tmp/out_*.txt", None),
        ("rm -rf ./.pytest_cache node_modules", None),
        ("rm -rf node_modules dist", "G1"),     # dist may hold real artifacts
        ("rm -rf src/__pycache__ src", "G1"),
        ("rm notes.txt", None),
        ("Remove-Item -Recurse -Force .\\dist", "G1"),
        ("mkfs.ext4 /dev/sdb1", "G1"),
        ("psql -c 'DROP TABLE users'", "G1"),
        ("git push origin master", None),
        ("git push --force origin master", "G2"),
        ("git push --force-with-lease origin master", None),
        ("git reset --hard HEAD~1", "G2"),
        ("git clean -fd", "G2"),
        ("git checkout .", "G2"),
        ("git checkout main", None),
        ("git branch -d merged-feature", None),
        ("git branch -D wip-branch", "G2"),
        ("psql -c 'DELETE FROM sessions;'", "G3"),
        ("psql -c 'DELETE FROM sessions WHERE id = 3;'", None),
        ("psql -c \"UPDATE orders SET status = 'x';\"", "G3"),
        ("psql -c \"UPDATE orders SET status = 'x' WHERE id = 1;\"", None),
        ("git add .env", "G6"),
        ("git add src/app.py", None),
        ("export OPENAI_API_KEY=" + real_key, "G6"),
        ("export AWS_ACCESS_KEY_ID=" + aws_key, "G6"),
        ("echo see " + zendesk, None),
        ("echo see " + maersk, None),
        ("echo " + slovak, None),
        ("git add -A", "G10"),
        ("git add .", "G10"),
        ("git add --all && git commit -m x", "G10"),
        ("git commit -am 'quick'", "G10"),
        ("git add -- 'Marketingwiki/Daily/2026-09-14.md' 'Tools/x.py'", None),
        ("git commit -m 'commit skill: never run git add -A on the shared tree'", None),
    ]


def self_test():
    failures = 0
    cases = _cases()
    for command, expected in cases:
        gate, _ = check(command)
        ok = gate == expected
        failures += 0 if ok else 1
        print("%s %-8s %s" % ("PASS" if ok else "FAIL", str(gate), command[:70]))
    print("self-test: %d/%d passed" % (len(cases) - failures, len(cases)))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        main()
