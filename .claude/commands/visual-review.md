---
name: visual-review
description: "Delegate to the visual-review skill for the <app> frontend."
division: core
---

# /visual-review

## Delegate

Delegate to the **visual-review** skill.

Activate when a visual change to `<app>` (layout, styling, motion, copy on
screen) must be accepted or rejected. The skill shoots the running artifact
with the project's own harness, scores ten dimensions 0 to 10, fixes the three
weakest and reshoots, at most three rounds, to an average of 8 with no score
under 7. Hard blockers — console errors, horizontal overflow, unreadable text,
unloaded fonts, placeholder copy — fail the review regardless of the average.

Do not activate for a logic-only change with no rendered surface, and never
accept a visual change from code inspection alone.
