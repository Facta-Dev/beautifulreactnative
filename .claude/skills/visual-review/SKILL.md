---
name: "<app> Visual Review"
description: "Reviews a rendered <app> surface, not a diff: shoot the running artifact with the project's own harness, score ten dimensions, fix the three weakest, reshoot, at most three rounds, to an average of 8 with no score under 7."
division: core
---

# <app> Visual Review skill

A workflow for accepting or rejecting a visual change by looking at what was
actually rendered, never at the patch. An agent invokes this skill on any
layout, styling, motion, or on-screen copy change in `<app>`; the skill
supplies the rubric, the agent supplies the running artifact.

## When to Activate

- A visual change to `<app>` (layout, styling, motion, copy on screen) is to
  be accepted or rejected.
- The question is "does it look right" rather than "does the code change
  correctly".
- A previous sign-off was made from code inspection alone.

Do not activate for a logic-only change with no rendered surface, or when code
inspection alone is genuinely enough.

## Core Principles

- Review the rendered artifact, never the diff: capture the running thing,
  not the patch.
- Score ten dimensions 0 to 10, then fix the three weakest, then reshoot.
- Hard blockers fail the review regardless of the average.
- Acceptance: an average of 8 or more and no single dimension under 7.

## Rules

- Never claim visual acceptance from code inspection alone; always shoot the
  running artifact.
- Use the project's own capture harness; do not substitute a screenshot of a
  different render or a stale build.
- At most three fix-and-reshoot rounds; if the bar is still unmet, report the
  blockers and do not lower the bar.
- Fix the three weakest dimensions each round; never skip a hard blocker to
  chase a nice-to-have.
- Report the scores and the shot evidence, not just a pass or fail word.

## Research References

Provenance table, every claim in a finding needs a row.

| claim | source | year | link |
| --- | --- | --- | --- |
| Ten-dimension rubric, fix-three, reshoot, and the acceptance bar | MotionSites review rubric | 2026 | `references/review.md` |
| The capture harness for shooting the running artifact | MotionSites scripts | 2026 | `scripts/shoot.py` |

## Output Format

Deliver, in order:

1. The scorecard: ten dimensions, each scored 0 to 10, with the three weakest
   named.
2. The hard-blocker list: console errors, horizontal overflow, unreadable
   text, unloaded fonts, placeholder copy.
3. The fix-and-reshoot log, one entry per round, capped at three.
4. The verdict: accept only when the average is 8 or more and no dimension is
   under 7; otherwise the blockers that still stand.

Example:

```
visual-review: contrast 4, spacing 5, hierarchy 6 -> weakest three
visual-review: hard blockers: none
visual-review: round 1 fixed contrast, spacing, hierarchy -> reshoot
visual-review: verdict = accept (avg 8.4, min 8)
```
