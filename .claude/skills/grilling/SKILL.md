---
name: "grilling"
description: "Grills an <app> plan, decision or idea round by round against a design tree, resolving assumptions, failure modes and scope before any code is written."
division: core
---

# <app> Grilling skill

> Reusable workflow for stress-testing a plan before implementation. An
> agent invokes this skill; the agent supplies the domain judgement, the
> skill supplies the questioning discipline.

## When to Activate

Activate this skill when a plan, decision or idea for `<app>` needs to be
challenged before code is written. Typical triggers:

- The request is to stress-test, review, poke holes in, or "grill" a plan.
- The request asks about assumptions, failure modes, scope or trade-offs
  before implementation starts.
- A design is described but the boundaries, edge cases or rollback are
  still undefined.

Do NOT activate this skill to answer a factual question about the codebase
(read the code instead), or to grind a plan into the ground after the
decisions are already settled.

## Core Principles

- **Map the design tree.** Every decision branches into the decisions that
  hang off it. The tree, not a question list, is the unit of work.
- **Work in rounds, frontier first.** The frontier is every decision whose
  prerequisites are already settled: the questions that can be asked now
  without guessing at answers not yet heard. Ask the whole frontier in one
  round, then wait for the answers before recomputing the frontier.
- **A question whose answer depends on another open question belongs to a
  later round**, never the current one.
- **Facts are the agent's job; decisions are the user's.** Never ask the
  user for something that can be looked up (filesystem, code, tooling).
  Dispatch a background exploration for it and keep asking the rest of the
  frontier while it runs.
- **Every question carries a recommendation.** Word each one so "yes"
  accepts the recommended answer, and state the recommendation explicitly.
- **No implementation before shared understanding.** The session ends when
  the frontier is empty and the user confirms the shared understanding.

## Rules

- Never fabricate facts to answer your own questions: read the file, run
  the command, or ask a sub-agent with a fresh context.
- Do not silently assume an unanswered branch. An unsettled decision stays
  visible until it is answered or explicitly deferred by the user.
- Ask one round at a time and wait for the answers; do not fire the whole
  tree at once.
- Number the questions within a round and keep each round's questions
  self-contained (the user may answer out of order).
- Keep the questions relentless but finite: the frontier empties, it does
  not expand forever. Close a branch as soon as it is settled.
- No invented commitments: never record a decision the user did not make.
  If the user is silent on a branch, mark it open.
- Never implement, scaffold or edit code during the grilling session.

## Research References

| Claim | Source | Year | Link |
|-------|--------|------|------|
| Design-tree, frontier and round structure; facts-vs-decisions split | `skills/productivity/grilling/SKILL.md` (upstream, MIT) | 2026 | local file |
| `<app>` slice boundaries used to seed the tree | `docs/architecture/02-vertical-slicing.md` | n/a | local file |

## Output Format

Raw structured prose, not a code fence. One round per block:

```
### <app> grilling, round <n>

**Q1** - <question title>: <question body, including the choices>

Recommendation: <recommended answer>

**Q2** - <question title>: <question body, including the choices>

Recommendation: <recommended answer>

Open branches carried to the next round: <list>
```

When the frontier empties, close with:

```
### <app> grilling, shared understanding

Settled: <decision> → <answer>
Deferred: <decision> → <explicitly deferred by the user>
Open: <branch> → <why it is still open>
```
