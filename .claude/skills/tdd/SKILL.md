---
name: "tdd"
description: "Drives an <app> change test-first through the red, green, refactor loop, one seam at a time, with integration tests at the boundaries."
division: testing
---

# <app> TDD skill

> Reusable workflow for building `<app>` features and fixes test-first.
> An agent invokes this skill; the agent supplies the domain knowledge, the
> skill supplies the loop discipline.

## When to Activate

Activate this skill when a change to `<app>` is driven test-first. Typical
triggers:

- The request is to build a feature or fix a bug test-first, or mentions
  red, green, refactor.
- The request asks for integration tests, or for the boundary between unit
  tests and integration tests in `<app>`.
- A change is being made where a regression test must land at the right
  seam.

Do NOT activate this skill when the change is documentation-only, a
mechanical rename, or a configuration edit with no behaviour to pin down.

## Core Principles

- **Red before green.** Write the failing test first, then only the
  minimum code that makes it pass. Do not anticipate future tests.
- **Test behaviour through public interfaces.** The implementation may
  change entirely; the test should not. A good test reads like a
  specification ("user can check out with a valid cart") and survives
  refactors because it does not care about internal structure.
- **Tests live at seams.** A seam is the public boundary where behaviour
  is observed without reaching inside. Agree the seams up front, then test
  only there.
- **One vertical slice at a time.** One test, one minimal implementation,
  repeat. Each test is a tracer bullet that responds to what the previous
  cycle taught.
- **Refactoring belongs to the review stage**, not to the red-green
  implementation cycle.
- **Use the project's own vocabulary.** Test names and interfaces match the
  domain language recorded in `GLOSSARY.md` and the decisions recorded in
  the ADRs for the area being touched.

## Rules

- **No horizontal slicing.** Writing all the tests first and then all the
  implementation produces tests that verify imagined behaviour and go
  insensitive to real changes.
- **No tautological assertions.** The expected value must come from an
  independent source of truth (a known-good literal, a worked example, the
  spec). An assertion that recomputes the expected value the way the code
  does passes by construction and can never disagree with the code.
- **No implementation-coupled tests.** Mocking internal collaborators,
  testing private methods, or verifying through a side channel (querying
  the database instead of calling the interface) makes the test break on
  refactors while behaviour is unchanged.
- **Agree the seams before writing tests.** State the public interfaces
  under test and confirm them with the requester; give each seam a
  one-line note on what it catches and what it misses. No test is written
  at an unconfirmed seam.
- **Integration tests exercise the real boundary.** In `<app>` that means
  the wired mux over fakes (no database) or the container-backed suite
  (`make test-int`), with fixtures that are explicit about which layer
  they stand in for.
- **No fabricated results:** never claim a test passes without running it,
  and never assert on a behaviour the test does not actually exercise.
- Leave the suite green at the end of every slice: a red test in the tree
  is a broken contract, not a to-do.

## Research References

| Claim | Source | Year | Link |
|-------|--------|------|------|
| Red-green loop, seam agreement, anti-patterns (implementation-coupled, tautological, horizontal slicing) | `skills/engineering/tdd/SKILL.md` (upstream, MIT) | 2026 | local file |
| `<app>` test layers and commands | `docs/architecture/11-testing-and-ci.md` | n/a | local file |

## Output Format

Raw structured prose, not a code fence:

```
### <app> tdd, <change in one line>

Seams under test (agreed): <seam> -> catches <x>, misses <y>
Slice 1: test <file>:<name> -> red: <failure> -> green: <implementation> -> <command run>: <result>
Slice 2: test <file>:<name> -> red: <failure> -> green: <implementation> -> <command run>: <result>
Integration coverage: <what runs against the real boundary>
Suite state: <command> -> <result>
```
