# Playbook: Prompt and Skill Authoring
*Read when: you write or edit an instruction file for an agent: a project manual, a skill, or a system prompt.*

**Goal:** an instruction file that a weaker model follows correctly without the author present.

## Phase 0: Orient

Name the reader and the one job: which model, which harness, which trigger. Read the skills and rules it will sit beside; update an existing one before creating a twin. A prompt produces judgment, a permission produces consent, and code produces a guarantee; never write a guarantee as a sentence.

## Phase 1: Verified increments

Write the trigger, the steps in order, the stop conditions, and the exact output shape. Give one worked example with real input and output. Keep every rule testable; an untestable rule is an aspiration. Explain the why in a clause; stacked emphasis degrades compliance. For a skill file, meet the specification: frontmatter holds only name, description, license, metadata, and allowed-tools, the last declared for the least reach; the description stays under 1,024 characters and says what the skill does and when to use it, with matching phrases; the body stays under 500 lines and about 5,000 tokens; supporting files sit one level deep.

## Phase 2: Adversarial self-check

Run the skill in a fresh context on the weakest target model with one case it should handle and one it should refuse. Build a trigger set of twenty queries, half that should load the skill and half near misses, and run them. Run one task with and without the skill and compare. Read it as a hostile reader: what is assumed, and which sentence could be obeyed literally and wrongly?

## Phase 3: Honest report

State what the tests showed, which cases failed, and what the skill does not cover. If no test ran, say the skill is untested.

## Exit criteria

- [ ] One job, one trigger, one worked example.
- [ ] Frontmatter and size meet the specification.
- [ ] A should-handle and a should-refuse case ran on the weakest target model.
- [ ] The trigger set ran and the with-versus-without comparison was read.

## Anti-patterns

**The untested prompt.** *Tell:* a skill shipped because it read well. *Fix:* run it cold on the weakest model first.
**The aspiration list.** *Tell:* "be thorough", "always verify" with no procedure. *Fix:* replace each with the step and the check.
**The twin skill.** *Tell:* a new file that overlaps an existing one by half. *Fix:* edit the existing one.
**The vague trigger.** *Tell:* a description that says what the skill is, not when to load it. *Fix:* name the situations and the phrases.
**The guarantee in a sentence.** *Tell:* "never delete production data" in prose and nowhere else. *Fix:* a deny rule or a hook; the prose stays as the reason.
