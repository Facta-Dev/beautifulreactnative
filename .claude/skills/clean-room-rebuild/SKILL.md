---
name: "<app> Clean-Room Rebuild"
description: "Rebuilds a target's behaviour in <app> from observation alone: read only what a user or visitor sees, copy no protected assets, keep a credits table, and state plainly that the work is based on the original."
division: core
---

# <app> Clean-Room Rebuild skill

A workflow for reproducing the behaviour of a product, page or interaction
without reading its implementation. An agent invokes this skill when rights
are absent or restricted; the skill supplies the boundary, the agent supplies
the target. It pairs with the per-stack port skills, which read the source —
this skill forbids that unless the rights exist.

## When to Activate

- An `<app>` feature must reproduce how a target behaves, but the target's
  source is not licensed for reuse.
- A request to "recreate", "match", or "rebuild the look of" something whose
  assets cannot be copied.
- A port is wanted, but the source may not be read directly.

Do not activate when the rights to read and reuse the source exist (use the
per-stack port skill), or when nothing protected is being reproduced and
copying is not a concern.

## Core Principles

- Observation over inspection: read only what a user or visitor sees, never
  the implementation behind it.
- Nothing protected is reproduced: no logos, photos, brand names, or long
  verbatim text.
- Everything reused is recorded in a credits table with its source and
  licence.
- The work states plainly that it is based on the original, never that it is
  an independent creation.

## Rules

- Never bypass protection to observe: no login-wall circumvention, no DRM
  stripping, no rate-limit or scraping-ban evasion.
- Never copy a logo, photo, brand name, or a long passage of text verbatim.
- If the only way to reproduce behaviour is to copy a protected asset, redesign
  that part instead.
- Keep a credits table of everything reused — even a small idea or a colour
  treatment — with its source and its licence.
- State the derivation in the output: name the original and the basis, and do
  not claim independence.

## Research References

Provenance table, every claim in a finding needs a row.

| claim | source | year | link |
| --- | --- | --- | --- |
| The clean-room method: observe, do not read the implementation | Craft Anything | 2026 | `README.md` ("Clean room") |
| Golden rule 4: do not copy without the rights to do so | Craft Anything | 2026 | `AGENTS.md` |
| The rebuild brief that records observation and credits | Craft Anything ai crate | 2026 | `crates/ai/src/rebuild/brief.rs` |

## Output Format

Deliver, in order:

1. The observed behaviour, written from the user's or visitor's point of view.
2. The credits table: each reused element, its source, and its licence.
3. The plain statement of derivation, naming the original and the basis.

Example:

```
clean-room: observed = "cards list a title and an author, newest first"
clean-room: credits = "layout rhythm follows the original grid" (source:
  the target site, licence: none — re-implemented, not copied)
clean-room: this work is based on the target site, built from observation only
```
