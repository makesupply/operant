#!/usr/bin/env python3
# operant-shield: ignore-file  (defines detection patterns; scanning it is noise)
"""Operant policy gate — consolidated PreToolUse enforcement for shell tools.

Implements the code-enforceable subset of the generic policy spec:
  G1 destructive commands, G2 history rewrites, G3 unbounded mutations,
  G6 secret staging. Exit 2 blocks the call and returns gate-specific
  guidance to the model; exit 0 allows.

Wiring (.claude/settings.json):
  "PreToolUse": [{"matcher": "Bash|PowerShell",
    "hooks": [{"type": "command", "command": "python <path>/policy-gate.py"}]}]

Design rules (see generic-policy-spec.md): deterministic, tuned narrow,
hands off to judgment with an actionable reason. Stdlib only.
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
    ("G2", r"\bgit\s+branch\s+-D\b", "force-delete branch (unmerged work may be lost)"),
    # --- G3: unbounded-mutation gate (heuristic: statement-level, no WHERE) ---
    ("G3", r"\bDELETE\s+FROM\s+[\w.\"\[\]`]+\s*(;|$)", "DELETE with no WHERE clause"),
    ("G3", r"\bUPDATE\s+[\w.\"\[\]`]+\s+SET\s+[^;]+?(;|$)(?<!WHERE)", None),  # handled specially below
    # --- G6: secret-staging tripwire ---
    ("G6", r"\bgit\s+(add|commit)\b[^\n]*(\.env(\.|\s|$|\")|id_rsa|id_ed25519|\.pem\b|\.key\b|credentials\.json|serviceaccount[^\s]*\.json)", "staging a likely secret file"),
    ("G6", r"AKIA[0-9A-Z]{16}", "AWS access key in command"),
    ("G6", r"ghp_[A-Za-z0-9]{36}", "GitHub token in command"),
    ("G6", r"sk-[A-Za-z0-9\-_]{20,}", "API secret key in command"),
    ("G6", r"xox[baprs]-[A-Za-z0-9\-]{10,}", "Slack token in command"),
    ("G6", r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key material in command"),
]

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
}

# Benign contexts G3's UPDATE heuristic must not fire on (reduce false positives).
UPDATE_SAFE = re.compile(r"\bWHERE\b", re.IGNORECASE)


def check(command: str):
    for gate, pattern, why in GATES:
        if why is None:
            continue  # placeholder rows handled separately
        if re.search(pattern, command, re.IGNORECASE):
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


# (command, expected gate or None). Negatives are as load-bearing as positives:
# every false positive teaches the model and the user to route around the gate.
SELF_TEST_CASES = [
    ("rm -rf /tmp/build", "G1"),
    ("Remove-Item -Recurse -Force C:\\temp", "G1"),
    ("del /s /q build", "G1"),
    ("DROP TABLE users;", "G1"),
    ("git push --force origin main", "G2"),
    ("git push --force-with-lease origin main", None),
    ("git reset --hard HEAD~1", "G2"),
    ("git clean -fd", "G2"),
    ("git branch -D feature/x", "G2"),
    ("DELETE FROM orders;", "G3"),
    ("DELETE FROM orders WHERE id = 7;", None),
    ("UPDATE users SET active = 0", "G3"),
    ("UPDATE users SET active = 0 WHERE id = 3", None),
    ("git add .env", "G6"),
    ("echo AKIAABCDEFGHIJKLMNOP", "G6"),
    ("git commit -m 'docs: update readme'", None),
    ("ls -la", None),
    ("rm notes.txt", None),
]


def self_test() -> int:
    failed = 0
    for command, expected in SELF_TEST_CASES:
        gate, _why = check(command)
        if gate != expected:
            failed += 1
            print("FAIL %r -> %s (expected %s)" % (command, gate, expected))
    total = len(SELF_TEST_CASES)
    print("self-test: %d/%d passed" % (total - failed, total))
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "self-test":
        sys.exit(self_test())
    main()
