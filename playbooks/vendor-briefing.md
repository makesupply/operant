# Playbook: Vendor / Contractor / Freelancer Briefing

**Goal:** give an external party exactly what they need to deliver the right thing on the first try — complete acceptance criteria, unambiguous scope — while leaking nothing internal, secret, or beyond need-to-know, and confirming the recipient and attachments before the brief leaves. A brief is an outward-facing artifact; sending it is a Tier 3 action ([safety.md](../references/safety.md)), where the outcome is hard to recall once someone outside your organization has read it.

## Phase 0 — Orient

Before writing a word, pin down four things:

- **The deliverable and its acceptance criteria.** What is being produced, and how will you know it's right? "Three source files, editable, brand fonts embedded, delivered by the 14th" is a criterion; "good design work" is a wish. If you can't state the pass condition, the vendor is guessing.
- **The recipient and their context.** They lack all your internal knowledge — the naming conventions, the reasons behind the request, the history. Assume they know nothing you haven't written down, and nothing you shouldn't write down.
- **The constraints.** Budget, deadline, format, brand rules, revision rounds, licensing of the output. Unstated constraints become disputes.
- **What must NOT be shared.** Internal strategy, credentials, customer data, system names, unrelated context. Decide this now, before it slips into "background."

## Phase 1 — One reader, one job

The brief is written for someone with none of your context, per the single-reader discipline in [writing-and-docs.md](writing-and-docs.md):

- **Front-load the objective.** The first paragraph states what you want made and what success looks like. A vendor who reads only that should already be pointed the right way.
- **Specify acceptance criteria so the vendor cannot guess wrong.** Enumerate the deliverables, formats, dimensions, quantities, deadline, and the definition of done. Every criterion you omit is a coin-flip the vendor will lose ([ambiguity-and-requirements.md](../references/ambiguity-and-requirements.md)).
- **Bound the scope explicitly.** State what is in and what is out. "Homepage hero only; no interior pages" prevents both under-delivery and the scope dispute that follows an open-ended ask.
- **Give one concrete example** of the standard you expect — a reference, a sample, a "like this, not that." An example teaches faster than a paragraph of adjectives.

## Phase 2 — Need-to-know and data minimization

Include only what the task requires. The brief is an outward artifact, and you should assume it may be forwarded, quoted, or stored beyond your control ([security-posture.md](../references/security-posture.md)):

- **Strip internal-only strategy and reasoning.** The vendor needs the specification, not the roadmap behind it. "For background" is where over-sharing hides.
- **Never include credentials, API keys, tokens, or access details.** If the vendor needs access, provision it through the proper channel with least privilege, not by pasting a key into a document.
- **Remove customer and personal data.** Use synthetic or masked examples; real records never become brief material.
- **Rename or omit internal system names.** Describe the interface the vendor works against, not your internal architecture.

Share the one file the task needs, not the folder it lives in.

## Phase 3 — Redaction pass

Before anything is sent, re-read the brief once more with a single purpose: hunting for sensitive material that snuck in. This is a distinct pass, not a side effect of proofreading.

- **Read the body specifically for secrets, internal names, and over-shared context** — not for tone or typos.
- **Open every attachment and example file.** A screenshot with a URL bar, a spreadsheet with hidden columns or extra tabs, a document with tracked changes or comments, image metadata — the leak is usually in the file you didn't re-open, not the text you wrote.
- **Confirm each attachment is the one file intended,** not a bundle that dragged along an entire internal directory.

If the redaction pass finds something already sent, treat it as an exposure and escalate immediately ([security-posture.md](../references/security-posture.md)); rotation or recall is time-sensitive and only the user can authorize it.

## Phase 4 — The send is Tier 3

Sending to an external party is outward-facing and effectively irreversible. Before it leaves, confirm three things out loud:

- **The exact recipient.** The right vendor, the right address, no autocomplete substitution. A brief for one contractor sent to another is both a wrong delivery and a leak.
- **The exact attachments.** The files you intend, and only those.
- **That the redaction pass ran.** Not "probably fine" — actually done.

State these back to the user and get confirmation before dispatch. The thirty seconds of read-back is cheaper than any recall.

## Anti-patterns

- **The pasted secret.** *Tell:* a credential, key, or token sits in the brief "so they can get started." *Fix:* provision access through the proper channel with least privilege; reference it, never embed it.
- **The background dump.** *Tell:* paragraphs of internal strategy included "for context" the vendor doesn't need. *Fix:* include only what the task requires; the specification, not the reasoning behind it.
- **The missing criteria.** *Tell:* the brief describes a vibe but never states the pass condition. *Fix:* enumerate deliverables, formats, deadline, and definition of done before sending — a wrong first draft is otherwise guaranteed.
- **The open scope.** *Tell:* no line separates what's in from what's out. *Fix:* state boundaries explicitly, so neither side argues over them later.
- **The wrong vendor.** *Tell:* the recipient was picked by autocomplete or muscle memory. *Fix:* confirm the exact address against the intended party before dispatch.
- **The whole-folder attachment.** *Tell:* the send bundles an internal directory to deliver one asset. *Fix:* attach the single file the task needs, and open it first.
