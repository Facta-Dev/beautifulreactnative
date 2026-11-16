---
name: "<app> Verified Status"
description: "Emits a status table for <app> where each row states what works, how it was verified, and what was not verified or run; never claims a live run that did not happen."
division: core
---

# <app> Verified Status skill

A workflow that turns a status report into a table the reader can trust. An
agent invokes this skill before declaring work done or handing off; the skill
supplies the honesty, the agent supplies what actually happened. Every row
says what works, how that was verified, and what was not verified or not run.

## When to Activate

- A status report, handoff, or "is it done" question about `<app>`.
- Before declaring a task complete, so the reader sees exactly what ran and
  what did not.
- A prior report claimed "works" without saying how anyone would know.

Do not activate for a code diff review (the diff is the report), or for a
claim the requester has already verified themselves.

## Core Principles

- Every "works" claim states its verification method.
- Each row separates verified, not verified, and not run.
- A live run that did not happen is never reported as having happened.

## Rules

- Never claim a run, test, or check that you did not actually perform.
- Separate "verified" (you ran it and saw it pass) from "not run" (you did
  not) and from "not verified" (you saw it but could not confirm it works).
- State the command or observation that produced each verification, not just
  the word "passed".
- If the environment could not run something, say so; do not imply it passed.
- Do not borrow another agent's "it works" as your own verification; re-run or
  mark it as their report.

## Research References

Provenance table, every claim in a finding needs a row.

| claim | source | year | link |
| --- | --- | --- | --- |
| Report what you verified and what you did not | Craft Anything | 2026 | `AGENTS.md` |
| The status table format | Craft Anything | 2026 | `docs/STATUS.md` |

## Output Format

Deliver a Markdown table with four columns, then a summary line:

| item | status | how verified | not verified / not run |

`status` is one of `verified`, `not verified`, or `not run`. The summary line
counts how many rows carry a real verification and how many are outstanding.

Example:

```
| item | status | how verified | not verified / not run |
| --- | --- | --- | --- |
| login flow | verified | `npm test auth` green, 14/14 | — |
| dark mode | not run | — | no run in this session |
verified-status: 1 verified, 0 not verified, 1 not run
```
