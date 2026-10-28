# Playbook: Shared Checkout
*Read when: another session or agent may be editing the same working tree while you work.*

**Goal:** several agents editing one tree never commit, overwrite, or destroy each other's work.

## Phase 0: Orient

Write your touched-files list in the task-state file. Run the status command; every uncommitted change that is not yours is another agent's in-flight work. Read the staged set too, because a plain commit takes everything staged, whoever staged it. Commit under your own identity. Where the project allows isolation instead, follow [concurrency-and-handoffs.md](../references/concurrency-and-handoffs.md) under "Isolate when the project's model allows it".

## Phase 1: Verified increments

Re-read a shared file immediately before each edit. Edit only your own lines. Append to shared logs through the project's append helper. Stage and commit by explicit path, naming the same paths. Never run a whole-tree add, an all-changes commit, a reset, a stash, or a clean. When a file you must commit also holds another agent's unstaged lines, stage only your lines and commit the index with no pathspec, naming every staged path in the same command; if other agents also hold staged paths, leave the shared file for later.

## Phase 2: Adversarial self-check

After each write, re-read the file and confirm only your lines changed. Before committing, diff the staged set against your list; anything extra stays staged for its owner. After committing, list the commit's files and confirm they match your list, and that other agents' files are as they were. A staging gate's block is correct; use the explicit-path form it hands back, per [generic-policy-spec.md](../enforcement/generic-policy-spec.md).

## Phase 3: Honest report

Name the files you changed and the commit. Name every other agent's change you saw and left alone. Name any conflict you resolved and how.

## Exit criteria

- [ ] The touched-files list was written before the first edit.
- [ ] Every edit was preceded by a fresh read of the file.
- [ ] Every commit named its paths and contains only those paths.
- [ ] Other agents' dirty and staged files are untouched and named in the report.

## Anti-patterns

**The sweep commit.** *Tell:* a whole-tree add or all-changes commit on a shared tree. *Fix:* explicit paths, every time.
**The clobber.** *Tell:* a whole-file write over a file another agent was editing. *Fix:* re-read, edit lines, append through the helper.
**The stale read.** *Tell:* an edit built on a read from earlier in the session. *Fix:* read immediately before writing.
**The partial-stage pathspec commit.** *Tell:* a pathspec commit on a half-staged file swept another agent's lines in. *Fix:* stage your lines, then commit the index with no pathspec, naming every staged path.
**The cleanup of another agent's junk.** *Tell:* an untracked file removed because it looked stray. *Fix:* someone values it until proven otherwise; leave it.
