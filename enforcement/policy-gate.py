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

1.4.2 (2026-10-08):
  * G10 also checks commit SCOPE. A plain `git commit` commits the whole index,
    so a session that staged its own files by explicit path still swept 9 files
    another session had already staged (commit 1f4598d). A `git commit` with no
    `-- <paths>` pathspec is denied when the real index (`git diff --cached`)
    holds a staged path the command does not name. This is the gate's only
    stateful check: it reads git, only for a commit with no pathspec, and
    allows the call if git cannot be read.
  * PowerShell here-strings (@'...'@, @"..."@) are stripped with the other
    literals, so a commit message cannot fake a pathspec or a whole-tree flag.

1.4.3 (2026-10-09):
  * G10 also checks a PATHSPEC commit. `git commit -- <path>` ignores the index
    for <path> and commits its whole working-tree copy. On a shared note that
    holds another session's uncommitted lines, that sweeps their lines in, even
    when the session staged only its own (commit 137a149, undone before push).
    A pathspec commit is denied when a named path is partially staged: it is in
    `git diff --cached` AND in `git diff`. A path that a `git add` earlier in the
    same command stages is exempt, since that add takes the whole file on purpose.
    Like the commit-scope check, it reads git only for this command shape and
    allows the call if git cannot be read.
"""
import json
import os
import re
import subprocess
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
    r"|@(['\"])\r?\n.*?\r?\n\3@"                # PowerShell here-strings
    r"|'[^']*'|\"[^\"]*\"",                     # quoted strings
    re.DOTALL,
)

# --- G10 commit scope (added 1.4.2, 2026-10-08) ---
# Incident 2026-10-08: commit 1f4598d staged its own files by explicit path, then a
# plain `git commit -m ...` committed the WHOLE index, including 9 files another
# session had already staged. Explicit-path staging is not enough
# on a shared index; the commit must carry a pathspec (`git commit -m "..." -- <paths>`),
# which commits only those paths and leaves other entries staged for their owners.
# Matched on the command with literals masked to same-length filler, so offsets line
# up with the original and a quoted path after `--` still counts as a token.
_GIT_COMMIT = re.compile(
    r"\bgit((?:\s+(?:-C|-c|--git-dir|--work-tree)(?:=\S+|\s+(?!commit\b)\S+)?|\s+--no-pager))*"
    r"\s+commit(?![\w-])([^\n;&|]*)",
    re.IGNORECASE)
_PATHSPEC = re.compile(r"(?:^|\s)--(?=\s+\S)|--pathspec-from-file\b", re.IGNORECASE)
_DRY_RUN = re.compile(r"(?:^|\s)--dry-run\b", re.IGNORECASE)
_DASH_C = re.compile(r"\bgit\s+-C\s+(\"[^\"]*\"|'[^']*'|\S+)", re.IGNORECASE)
_CD = re.compile(
    r"(?:^|[;&|\n(]\s*)(?:cd|pushd|Set-Location|sl)\s+(?:-(?:Literal)?Path\s+)?(\"[^\"]*\"|'[^']*'|[^\s;&|)]+)",
    re.IGNORECASE)
COMMIT_SCOPE_WHY = "a commit with no pathspec takes the whole index"

# --- G10 partial staging (added 1.4.3, 2026-10-09) ---
# Incident 2026-10-09: a session staged only its own lines of the shared tracker and
# daily note, then ran `git commit -m ... -- <those paths>`. A pathspec commit takes
# each named file from the WORKING TREE, so another session's uncommitted lines in the
# same files went into the commit (137a149, undone before push).
_PATHSPEC_FILE = re.compile(r"--pathspec-from-file\b", re.IGNORECASE)
_PATHSPEC_SEP = re.compile(r"(?:^|\s)--(?=\s+\S)")
_GIT_ADD = re.compile(
    r"\bgit((?:\s+(?:-C|-c|--git-dir|--work-tree)(?:=\S+|\s+(?!add\b)\S+)?|\s+--no-pager))*"
    r"\s+add(?![\w-])([^\n;&|]*)",
    re.IGNORECASE)
PARTIAL_WHY = "a pathspec commit takes each named file's whole working-tree copy"


def _mask(command: str) -> str:
    return _LITERALS.sub(lambda m: "Q" * len(m.group(0)), command)


def _unquote(s: str) -> str:
    return s[1:-1] if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"" else s


def _native_path(p: str) -> str:
    # Git Bash spells D:\x as /d/x; Python on Windows needs the drive form.
    m = re.match(r"^/([a-zA-Z])(/|$)", p)
    if os.name == "nt" and m:
        p = m.group(1).upper() + ":/" + p[m.end():]
    return os.path.expanduser(p)


def _commit_dir(command: str, masked: str, m, cwd: str) -> str:
    """Directory the commit at match `m` runs in: its own `git -C <dir>`, else the
    `cd` chain before it applied to the hook's cwd."""
    d = _DASH_C.search(command, m.start(), m.start(2))
    if d:
        return os.path.join(cwd, _native_path(_unquote(d.group(1))))
    base = cwd
    for c in _CD.finditer(masked, 0, m.start()):
        base = os.path.join(base, _native_path(_unquote(command[c.start(1):c.end(1)])))
    return base


def _staged_paths(directory: str):
    """Paths staged in the index at `directory`, or None when git cannot say."""
    try:
        r = subprocess.run(["git", "-C", directory, "diff", "--cached", "--name-only", "-z"],
                           capture_output=True, timeout=5,
                           env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]


def _git_names(directory: str, *args):
    try:
        r = subprocess.run(["git", "-C", directory] + list(args) + ["--name-only", "-z"],
                           capture_output=True, timeout=5,
                           env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]


def _partial_paths(directory: str):
    """Paths both staged and further modified in the working tree, or None when git cannot say."""
    staged = _git_names(directory, "diff", "--cached")
    dirty = _git_names(directory, "diff")
    if staged is None or dirty is None:
        return None
    unstaged = set(dirty)
    return [p for p in staged if p in unstaged]


def _named(path: str, command: str) -> bool:
    return re.search(r"(?<![\w.-])" + re.escape(path) + r"(?![\w.-])", command, re.IGNORECASE) is not None


def _partial_scope(command: str, masked: str, m, cwd: str, partial):
    """For a pathspec commit at match `m`: the named paths that are partially staged and
    not re-staged whole by a `git add` earlier in the same command."""
    tail_start = m.start(2)
    sep = _PATHSPEC_SEP.search(masked, tail_start, m.end(2))
    if not sep:
        return None
    paths = partial(_commit_dir(command, masked, m, cwd))
    if not paths:
        return None  # nothing partially staged, or git unreadable: never block on our own failure
    spec = command[sep.end():m.end(2)].replace("\\", "/")
    added = " ".join(command[a.start(2):a.end(2)]
                     for a in _GIT_ADD.finditer(masked, 0, m.start())).replace("\\", "/")
    hits = [p for p in paths if _named(p, spec) and not _named(p, added)]
    if not hits:
        return None
    shown = ", ".join(hits[:8]) + (" (+%d more)" % (len(hits) - 8) if len(hits) > 8 else "")
    return "%s, and %d named path(s) are staged with further unstaged changes that would ride along: %s" % (
        PARTIAL_WHY, len(hits), shown)


def _commit_scope(command: str, cwd: str, staged, partial=None):
    masked = _mask(command)
    flat = command.replace("\\", "/")
    for m in _GIT_COMMIT.finditer(masked):
        tail = m.group(2)
        if _DRY_RUN.search(tail):
            continue
        if _PATHSPEC.search(tail):
            if partial is not None and not _PATHSPEC_FILE.search(tail):
                why = _partial_scope(command, masked, m, cwd, partial)
                if why:
                    return why
            continue
        paths = staged(_commit_dir(command, masked, m, cwd))
        if not paths:
            continue  # empty index, or git unreadable: never block on our own failure
        foreign = [p for p in paths if not _named(p, flat)]
        if foreign:
            shown = ", ".join(foreign[:8]) + (" (+%d more)" % (len(foreign) - 8) if len(foreign) > 8 else "")
            return "%s, and the index holds %d staged path(s) this command does not name: %s" % (
                COMMIT_SCOPE_WHY, len(foreign), shown)
    return None

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
    "G10-commit": ("Operant gate G10 (commit scope on a shared index): {why}.\n"
                   "A plain `git commit` commits everything staged, including files another session "
                   "staged and has not committed yet (2026-10-08 incident: commit 1f4598d swept 9 such "
                   "files). Commit by pathspec instead; it commits only the named paths and leaves the "
                   "rest staged for their owners:\n"
                   "  git add -- \"<file>\" ... then  git commit -m \"<label>\" -- \"<file>\" ...\n"
                   "Name only files THIS session created or edited (a new file must be added first; a "
                   "rename needs both paths). Do not unstage, reset, or stash the paths listed above; "
                   "report them as left for their owners. See .claude/skills/commit/SKILL.md."),
    "G10-partial": ("Operant gate G10 (partial staging on a shared checkout): {why}.\n"
                    "`git commit -- <path>` ignores what you staged for <path> and commits the whole "
                    "file as it is on disk. The unstaged part may be another session's uncommitted "
                    "lines (2026-10-09 incident: commit 137a149). Run `git diff -- <path>` and decide:\n"
                    "  - every unstaged change is yours: `git add -- <path>` in the same command, "
                    "then the pathspec commit;\n"
                    "  - some are another session's: keep only your lines staged, then commit the "
                    "index with NO pathspec and name every staged path in the same command, e.g.\n"
                    "    git diff --cached --name-only -- \"<path>\" ... && git commit -F <msgfile>\n"
                    "Never discard, stash, or overwrite the other session's lines. If other sessions "
                    "also have paths staged, that route is blocked too: commit your other files now "
                    "and leave the shared file for later, or ask the user. See "
                    ".claude/skills/commit/SKILL.md."),
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


def check(command: str, cwd: str = None, staged=_staged_paths, partial=_partial_paths):
    # G10 first, on the command with quoted strings / heredoc bodies stripped.
    stripped = _LITERALS.sub(" ", command)
    for pattern, why in G10_PATTERNS:
        if re.search(pattern, stripped, re.IGNORECASE):
            return "G10", why
    why = _commit_scope(command, cwd or os.getcwd(), staged, partial)
    if why:
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
    gate, why = check(command, cwd=data.get("cwd"))
    if gate:
        key = ("G10-commit" if why.startswith(COMMIT_SCOPE_WHY)
               else "G10-partial" if why.startswith(PARTIAL_WHY) else gate)
        print(GUIDANCE[key].format(why=why), file=sys.stderr)
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
        ("git commit -m @'\nthe owner's rule: never git add -A\n'@ -- 'a.md'", None),  # here-string, apostrophe inside
    ]


def _commit_cases():
    # (command, paths the stubbed index holds or None for "git unreadable", expected gate).
    # The 2026-10-08 shape: own files added by path, then a plain commit over a foreign entry.
    foreign = ["tools/overlay/overlay.json", "tools/sync-skill.ps1"]
    return [
        ("git commit -m 'x'", foreign, "G10"),
        ("git commit -m 'x'", [], None),                       # empty index: plain commit is harmless
        ("git commit -m 'x'", None, None),                     # git unreadable: fail open
        ("git commit -m 'x' -- 'a.md'", foreign, None),           # pathspec commits only a.md
        ("git commit -m \"x\" -- \"docs/Project Index & Propagation Map.md\"", foreign, None),
        ("git add -- a.md b.md && git commit -m 'x'", ["a.md", "b.md"], None),  # every staged path named
        ("git add -- 'Hand offs/a.md' && git commit -m 'thesis screens'", ["Hand offs/a.md"] + foreign, "G10"),
        ("git add -- data.md && git commit -m x", ["a.md"], "G10"),   # a.md is not named by data.md
        ("git add -- Tools\\x.py && git commit -m x", ["Tools/x.py"], None),  # backslash spelling
        ("git commit --amend --no-edit", foreign, "G10"),
        ("git commit -m 'fix -- see notes'", foreign, "G10"),     # `--` inside the message is not a pathspec
        ("git commit -F - <<'EOF'\nsubject -- with dashes\nEOF", foreign, "G10"),
        ("git commit -m @'\nthe owner's fix -- see notes\n'@", foreign, "G10"),
        ("git -C \"D:/x y\" commit -m 'x'", foreign, "G10"),
        ("git -c user.name=codex commit -m x", foreign, "G10"),
        ("git commit -m x --pathspec-from-file=paths.txt", foreign, None),
        ("git commit --dry-run", foreign, None),
        ("git log --grep commit --oneline", foreign, None),        # not a commit
        ("git commit-tree HEAD^{tree} -m x", foreign, None),
        ("git status --short", foreign, None),
    ]


def _partial_cases():
    # (command, partially staged paths the stub reports or None for "git unreadable", expected gate).
    # The 2026-10-09 shape: own lines staged in a shared note, then a pathspec commit of that note.
    tracker = "MarketingWiki/Areas/Open Items Tracker.md"
    return [
        ("git commit -F msg.txt -- \"%s\"" % tracker, [tracker], "G10"),
        ("git commit -F msg.txt -- \"%s\"" % tracker, [], None),            # fully staged: nothing rides along
        ("git commit -F msg.txt -- \"%s\"" % tracker, None, None),          # git unreadable: fail open
        ("git commit -m x -- a.md b.md", ["b.md"], "G10"),
        ("git commit -m x -- b.md", ["a.md"], None),                        # a.md is not in this commit
        ("git commit -m 'touches a.md' -- b.md", ["a.md"], None),           # named only in the message
        ("git add -- a.md && git commit -m x -- a.md", ["a.md"], None),     # the add takes the whole file on purpose
        ("git add -- data.md && git commit -m x -- a.md", ["a.md"], "G10"), # data.md does not name a.md
        ("git commit -m x -- Tools\\x.py", ["Tools/x.py"], "G10"),          # backslash spelling
        ("git -C \"D:/x y\" commit -m x -- a.md", ["a.md"], "G10"),
        ("git commit --amend --no-edit -- a.md", ["a.md"], "G10"),
        ("git commit --dry-run -- a.md", ["a.md"], None),
        ("git commit -m x --pathspec-from-file=paths.txt", ["a.md"], None),
        ("git diff --cached --name-only -- a.md && git commit -F msg.txt", ["a.md"], None),  # the documented route
    ]


def _live_partial_case():
    """End to end: a tracked file whose first edit is staged and whose second edit is not.
    A pathspec commit of it is denied; add-then-commit and the documented plain commit pass."""
    import shutil
    import tempfile
    repo = tempfile.mkdtemp(prefix="operant-g10p-")
    try:
        def git(*a):
            subprocess.run(["git", "-C", repo] + list(a), check=True, capture_output=True)
        path = os.path.join(repo, "shared.md")
        git("init", "-q")
        git("config", "user.email", "t@operant.local")
        git("config", "user.name", "t")
        git("config", "core.autocrlf", "false")
        with open(path, "w", encoding="utf-8") as f:
            f.write("base\n")
        git("add", "--", "shared.md")
        git("commit", "-q", "-m", "base")
        with open(path, "a", encoding="utf-8") as f:
            f.write("my line\n")
        git("add", "--", "shared.md")
        with open(path, "a", encoding="utf-8") as f:
            f.write("another session's line\n")
        results = [
            (check("git commit -m 'mine' -- shared.md", cwd=repo)[0], "G10"),
            (check("git add -- shared.md && git commit -m 'mine' -- shared.md", cwd=repo)[0], None),
            (check("git diff --cached --name-only -- shared.md && git commit -m 'mine'", cwd=repo)[0], None),
        ]
    except (OSError, subprocess.CalledProcessError) as e:
        print("SKIP live partial case (git unavailable: %s)" % e)
        return 0, 0
    finally:
        shutil.rmtree(repo, ignore_errors=True)
    failed = sum(1 for got, want in results if got != want)
    for i, (got, want) in enumerate(results):
        print("%s %-8s live partial case %d" % ("PASS" if got == want else "FAIL", str(got), i + 1))
    return len(results), failed


def _live_case():
    """End to end against a real index: a foreign staged file, the session's own file added by
    path, then a plain commit (denied) and a pathspec commit (allowed). Also checks that a
    `cd <repo> &&` prefix is followed from an unrelated cwd. Skipped when git is unavailable."""
    import shutil
    import tempfile
    repo = tempfile.mkdtemp(prefix="operant-g10-")
    try:
        def git(*a):
            subprocess.run(["git", "-C", repo] + list(a), check=True, capture_output=True)
        git("init", "-q")
        git("config", "user.email", "t@operant.local")
        git("config", "user.name", "t")
        for name in ("other-session.md", "mine.md"):
            with open(os.path.join(repo, name), "w", encoding="utf-8") as f:
                f.write("x\n")
        git("add", "--", "other-session.md")
        outside = os.path.dirname(repo)
        fwd = repo.replace("\\", "/")
        results = [
            (check("git add -- mine.md && git commit -m 'mine'", cwd=repo)[0], "G10"),
            (check("git add -- mine.md && git commit -m 'mine' -- mine.md", cwd=repo)[0], None),
            (check("cd \"%s\" && git add -- mine.md && git commit -m 'mine'" % fwd, cwd=outside)[0], "G10"),
            (check("git -C \"%s\" commit -m 'mine'" % fwd, cwd=outside)[0], "G10"),
        ]
    except (OSError, subprocess.CalledProcessError) as e:
        print("SKIP live index case (git unavailable: %s)" % e)
        return 0, 0
    finally:
        shutil.rmtree(repo, ignore_errors=True)
    failed = sum(1 for got, want in results if got != want)
    for i, (got, want) in enumerate(results):
        print("%s %-8s live index case %d" % ("PASS" if got == want else "FAIL", str(got), i + 1))
    return len(results), failed


def _no_index(_directory):
    return []


def self_test():
    failures = 0
    total = 0
    for command, expected in _cases():
        gate, _ = check(command, staged=_no_index, partial=_no_index)
        ok = gate == expected
        total += 1
        failures += 0 if ok else 1
        print("%s %-8s %s" % ("PASS" if ok else "FAIL", str(gate), command[:70].replace("\n", " ")))
    for command, paths, expected in _commit_cases():
        gate, why = check(command, staged=lambda _d, p=paths: p, partial=_no_index)
        ok = gate == expected and (gate is None or why.startswith(COMMIT_SCOPE_WHY))
        total += 1
        failures += 0 if ok else 1
        print("%s %-8s %s" % ("PASS" if ok else "FAIL", str(gate), command[:70].replace("\n", " ")))
    for command, paths, expected in _partial_cases():
        gate, why = check(command, staged=lambda _d, p=paths: p or [], partial=lambda _d, p=paths: p)
        ok = gate == expected and (gate is None or why.startswith(PARTIAL_WHY))
        total += 1
        failures += 0 if ok else 1
        print("%s %-8s %s" % ("PASS" if ok else "FAIL", str(gate), command[:70].replace("\n", " ")))
    for live in (_live_case, _live_partial_case):
        n, failed = live()
        total += n
        failures += failed
    print("self-test: %d/%d passed" % (total - failures, total))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        main()
