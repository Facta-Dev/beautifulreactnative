---
name: "domain-modeling"
description: "Sharpens the <app> domain model in place: challenges fuzzy terminology, records exact terms in GLOSSARY.md, and writes ADRs only for hard-to-reverse decisions."
division: core
---

# <app> Domain Modeling skill

> Reusable workflow for keeping the `<app>` domain vocabulary and the
> recorded decisions honest. An agent invokes this skill; the agent supplies
> the domain knowledge, the skill supplies the discipline.

## When to Activate

Activate this skill when the `<app>` domain model itself is changing:
a term is disputed or overloaded, a new concept is being introduced, or a
decision worth recording is being made. Typical triggers:

- The request discusses codebase terminology, or asks what something means
  in `<app>`.
- The request is to write or edit `GLOSSARY.md`.
- The request is to record or edit an architecture decision record.
- A new slice, entity, or state machine is being named for the first time.

Do NOT activate this skill merely to read `GLOSSARY.md` for vocabulary
before another task (that is a one-line habit any skill can do), and not for
pure implementation choices with no domain consequence.

## Core Principles

- **The glossary is the language, the code is the truth.** When the two
  disagree, surface the contradiction instead of silently picking one.
- **Precision beats fluency.** Vague, overloaded words ("account", "user",
  "order", "active") are the defect. Propose one canonical term per
  concept.
- **A resolved term is written down immediately.** Update `GLOSSARY.md` in
  place as terms crystallise; do not batch the edits to the end of the
  session.
- **A glossary is not a spec.** `GLOSSARY.md` holds terms and their
  meaning only: no implementation detail, no requirements, no design
  discussion.
- **ADRs are rare by design.** Offer one only when all three conditions
  hold (hard to reverse, surprising without context, the result of a real
  trade-off). Meeting two out of three is not enough.
- **Create files lazily.** If no glossary or ADR directory exists, create it
  when there is genuinely something to write, not as empty scaffolding.

## Rules

- No fabricated data: never invent a term, a definition, a decision or an
  ADR number that was not agreed in the session.
- Every term in `GLOSSARY.md` must map to something in the `<app>` codebase
  or be explicitly marked as a domain concept not yet implemented.
- Keep definitions free of implementation detail (no table names, no
  framework names, no file paths) unless the term genuinely names an
  implementation concept, in which case name it explicitly.
- When the user states how something works, check the code before
  accepting it; report the mismatch and ask which side is right.
- Never renumber existing ADRs. A new ADR takes the next unused number.
- Files are created lazily and only where the repository already keeps
  such files: check for an existing `GLOSSARY.md`, `GLOSSARY-MAP.md`, or
  ADR directory before creating anything.
- A repository with multiple contexts keeps a `GLOSSARY-MAP.md` at the root
  pointing at each context's glossary and ADR directory. Do not flatten a
  multi-context repo into one glossary.

## Research References

| Claim | Source | Year | Link |
|-------|--------|------|------|
| Glossary and ADR conventions (challenge, sharpen, update inline, three ADR conditions) | `skills/engineering/domain-modeling/SKILL.md` (upstream, MIT) | 2026 | local file |
| Existing `<app>` architecture vocabulary | `docs/architecture/14-glossary.md` | n/a | local file |

## Output Format

Raw structured prose, not a code fence:

```
### <app> domain model, <what changed>

Terminology challenges:
- <term as used> vs <term as defined> → proposed canonical term: <term> | agreed: <yes/no/open>

Code cross-check:
- <statement>, code says: <finding> (file:line) | consistent/discrepant

GLOSSARY.md updates:
- <term>: <one-line definition>
- <term>: <one-line definition>

ADR:
- docs/adr/<NNNN>-<slug>.md, <decision in one line> | no ADR needed: <why not>
```
