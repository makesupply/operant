# Checklist: Before Claiming Done

"Done" is a factual claim. Run this before making it. Standard: the user could act on the report without checking anything themselves.

> **Tier 3** = any delete, overwrite of someone else's work, send, publish, deploy, payment, production change, external API write, or bulk edit.
> **Baseline** = the pre-change state, written down: which tests fail, the current metric, the current value.
> **Rung** = how strongly the work is verified, 1 to 5. 1: reads and compiles. 2: the existing suite passes. 3: a new test for this change passes. 4: observed running. 5: the original failure re-run and gone.
> **Artifact** = the file, output, or live state itself, not a message about it.

## Completeness

- [ ] Every ask on my before-starting list is checked off.
- [ ] No ask was reinterpreted into something easier than the user's words.
- [ ] Every stated constraint is met, and I can point to where.
- [ ] My draft report contains no "just needs", "should", or "remaining" describing work I could do now.

## Verification

- [ ] I state the rung reached, and it is the highest the environment allowed.
- [ ] The claim names the command that proves it, quotes its output and exit code, and that run happened after the last change.
- [ ] Anything I could not run is marked "not verified" with the reason, never "not applicable".
- [ ] If I fixed a bug: the original failing case was re-run and passes.
- [ ] If I fixed a bug: the regression test was run without the fix and failed.
- [ ] If I enabled, deployed, or published anything: I read back the deepest observable effect, meaning it serves, it spends, or it runs, not only its status flag.
- [ ] Results compared against the baseline: same passes, same prior failures, nothing newly broken, nothing newly and unexpectedly fixed.
- [ ] Every "done" that came from a subagent, a tool summary, or another agent was verified by me at the artifact.

## Hygiene

- [ ] Debug prints, scratch files, and temporary scaffolding are removed, or each is listed in the report with its reason.
- [ ] No process, server, or half-applied config is left running or pending without a note.
- [ ] Every doc, comment, index, mirror, changelog, or sibling note this change made false is updated.
- [ ] For each shared file I wrote, I re-read it after the write and only my lines changed.
- [ ] Every changed line is one I can explain as needed for this task.

## The report

- [ ] The first sentence is the outcome.
- [ ] It names what was verified and how, and what was not verified and why.
- [ ] Every assumption or guess made along the way is listed.
- [ ] Every plan deviation and every finding I chose not to fix has a ruling, one line with what I decided, why, and what it costs if wrong, and the report lists all of them.
- [ ] Every skip, workaround, and discovered-but-deferred issue is listed.
- [ ] Everything important is in this final message, in complete sentences, with no dash asides, arrow chains, or labels coined this session.
- [ ] The last paragraph is not a plan, a promise, or a permission request for work already asked for.
