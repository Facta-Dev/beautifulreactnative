---
name: "<app> Claim Check"
description: "Guards every substantive claim in an <app> deliverable: each claim cites a resolvable evidence id, carries a confidence tier, and open questions stay in a ledger until cited evidence closes them."
division: core
---

# <app> Claim Check skill

A workflow that forces a deliverable about `<app>` to earn its claims. An
agent invokes this skill before signing off on a plan, brief, report or
recommendation; the skill supplies the evidence discipline, the agent
supplies the claims. The goal is not more words, it is claims a reader can
trace.

## When to Activate

- An `<app>` deliverable (plan, brief, report, README, PR description) states
  something a reader will act on.
- The request asks for a verdict, recommendation, or status that needs
  evidence behind it.
- A claim looks confident but no source is visible next to it.

Do not activate for a code change whose diff is itself the evidence, for pure
transcription of an existing source, or for a claim the requester has already
verified and cited.

## Core Principles

- Every substantive claim carries an evidence id that resolves to a real
  source.
- Confidence is tiered: observed (seen directly), derived (computed from
  observed facts), inferred (a judgement not directly witnessed).
- Unknowns live in an open-questions ledger and close only when a cited id
  answers them.
- A reader should be able to follow every claim to its source without asking
  a second time.

## Rules

- No claim without an id: a claim that cannot point at a resolvable source is
  either downgraded to a question or dropped.
- Never fabricate an id or point it at a source you have not read yourself.
- Label the tier honestly: a number derived from two measurements is derived,
  not observed; a guess about the future is inferred.
- An open question stays open until an evidence id closes it; do not quietly
  resolve it with your own assumption.
- Cite repository evidence as file:line and external evidence as a URL, not a
  bare name.
- When the same claim recurs across a batch of deliverables, share the
  evidence id rather than restating it differently each time.

## Research References

Provenance table, every claim in a finding needs a row.

| claim | source | year | link |
| --- | --- | --- | --- |
| Evidence ids and the observed/derived/inferred confidence tiers | Craft Anything evidence doctrine | 2026 | `crates/evidence/src/lib.rs` |
| The unknowns ledger and its closure rule | Craft Anything evidence doctrine | 2026 | `crates/evidence/src/unknown.rs` |
| Comparing observed against derived evidence | Craft Anything engine | 2026 | `crates/engine/src/tools/compare_tools.rs` |

## Output Format

Deliver, in order:

1. The claim list, one claim per line: the claim, its tier, and the evidence
   id it resolves to.
2. The open-questions ledger: every unanswered question, and for each, the
   evidence id that would close it (or a note that none exists yet).
3. The summary line: how many claims carry an id, how many were downgraded,
   and how many questions remain open.

Example:

```
claim-check: claim = "the API returns 401 on an expired token" (observed,
  src/api/client.ts:34)
claim-check: open = "is the refresh path also covered?" (closes with a test
  or a run of src/api/client.ts)
claim-check: 3 claims cited, 1 downgraded, 1 open
```
