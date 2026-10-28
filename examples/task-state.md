# Example: The Task-State File

Any task expected to outlive one context window, or to span more than one session, gets a task-state file before the first long stretch of work. The rule and its trigger live in [context-management.md](../references/context-management.md) § The task-state file. Put the file in the harness scratchpad or the project's designated working folder, never in the repository root.

Five sections and no others. Goal, in the user's words. Done, each item with the evidence that made it done. In progress, at most one item. Next, in order. Decisions and gotchas, each with the reason and an absolute date.

Update it after every verified item and after every commit, not at the end. Re-read it at the start of every turn after a compaction, a resume, or a detour longer than a few tool calls, and before claiming done. After a compaction, trust the file and the artifact over the summary. Re-run any check whose evidence you cannot point at in the file.

The task-state file is for you, mid-task. The handoff document in [handoff-document.md](handoff-document.md) is for the next agent, at the end. When a session ends mid-task, the handoff is written from the task-state file, not from memory.

## Template

```markdown
# Task state: <task name> (<YYYY-MM-DD>)

## Goal
"<the request verbatim, with the constraints the user stated>"

## Done, with evidence
- <item> · <command run and the result seen, or the file path and what it contains> · <YYYY-MM-DD HH:MM>

## In progress
<exactly one item: its exact state, the last command and what it returned, the hypothesis under test if any>

## Next
1. <next step>
2. <the step after that>
3. <the step after that>

## Decisions and gotchas
- <decision or fact> · <why, or how to apply it> · <YYYY-MM-DD>
```

## Filled example: a weekly report moved to a new data source

```markdown
# Task state: weekly sales report on the warehouse API (2026-10-28)

## Goal
"Switch the weekly sales report from the exported spreadsheet to the warehouse API, and make sure the numbers match the last four published reports before you swap it over."

## Done, with evidence
- API client reads the four weekly windows · `python report/fetch.py --weeks 4` exits 0 and writes 4 files under `scratch/api/` · 2026-10-28 10:12
- Reconciled week 1 of 4 to the published report · `python report/reconcile.py --week 2026-09-28` prints `match: 100.0%` on 312 rows · 2026-10-28 10:40
- Reconciled week 2 of 4 · same command for 2026-10-05 prints `match: 100.0%` on 298 rows · 2026-10-28 10:52

## In progress
Reconciling week 3 of 4, the week of 2026-10-12. The first run printed `match: 97.4%`, with 8 rows differing, all in the returns column. Hypothesis under test: the API reports returns on the refund date and the spreadsheet on the order date. Checking the 8 rows against the orders table now.

## Next
1. Resolve the week 3 difference, then reconcile week 4.
2. Swap the report's data source behind the existing flag, run once, diff against the spreadsheet build.
3. Remove the spreadsheet path, update the runbook, write the final report with all four reconciliation outputs.

## Decisions and gotchas
- Reconcile row by row, not totals only, because two offsetting errors passed a totals check in week 1 before the row check caught them · 2026-10-28
- The API paginates at 500 rows and the last page carries no next-page token, so the client stops on an empty page, not on a missing token · 2026-10-28
- The user said the returns column is the one the finance team reads first, so a returns mismatch is never "close enough" · 2026-10-28
```

What the example shows. Each done item names the command and the result, so a post-compaction re-read can re-run it rather than trust it. The in-progress section holds one item and its exact state, including the hypothesis under test. The gotchas carry the reason, so the next turn does not re-derive them.
