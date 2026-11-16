---
name: "diagnosing-bugs"
description: "Diagnoses a hard <app> bug or performance regression with a red-capable feedback loop, a minimised repro, ranked falsifiable hypotheses, targeted instrumentation, and a regression test."
division: testing
---

# <app> Diagnosing Bugs skill

> Reusable diagnosis loop for hard bugs and performance regressions in
> `<app>`. An agent invokes this skill; the agent supplies domain judgement,
> the skill supplies the phase discipline.

## When to Activate

Activate this skill when a bug in `<app>` is hard to pin down: a wrong
result, a crash, a hang, or a performance regression. Typical triggers:

- The request says "diagnose", "debug this", "why does this fail", or
  reports something broken, throwing, failing or slow.
- A test fails intermittently, or only in CI, or only under load.
- A regression appeared between two known states (a commit, a migration, a
  dependency bump) and the cause is not obvious.

Do NOT activate this skill when the cause is already known and the work is
the fix itself (go straight to `/tdd`), or when the request is a code
review of a known diff (use `/review`).

## Core Principles

- **The feedback loop is the skill.** Everything else consumes it. Build
  one command that goes red on this bug and green once fixed, before forming
  any theory. Reading code to build a theory first is the failure this
  skill prevents.
- **Tighten the loop.** Treat it as a product: faster (cache setup, narrow
  scope), sharper (assert the exact symptom, not "did not crash"), more
  deterministic (pin time, seed randomness, isolate the filesystem, freeze
  the network). A 30-second flaky loop is barely better than no loop.
- **Reproduce, then minimise.** Cut inputs, callers, config, data and steps
  one at a time, re-running the loop after each cut, until every remaining
  element is load-bearing (removing any one turns the loop green). The
  minimised repro is the regression test later.
- **Rank before testing.** Generate 3 to 5 hypotheses and make each
  falsifiable ("if X is the cause, then changing Y makes the bug
  disappear"). A hypothesis whose prediction cannot be stated is a vibe.
- **One variable at a time.** Every probe maps to one prediction. For
  performance regressions, measure a baseline first (timing, profiler, query
  plan) and bisect; logs are usually the wrong tool.
- **The symptom, not a neighbour.** The loop must reproduce what the user
  described. Catching a different nearby failure means fixing the wrong bug.

## Rules

- Redact every secret before showing commands, output or captured
  artifacts: write `<REDACTED>` in place of the value, build loops against
  environment variables so credentials stay in the environment, and quote
  only the lines carrying the signal (captured traces carry auth headers).
- Never proceed to hypothesis without a loop. If no loop can be built, say
  so explicitly, list what you tried, and ask for access to the reproducing
  environment, a redacted captured artifact (HAR, log dump, core dump,
  timestamped recording), or permission to add temporary instrumentation.
- For non-deterministic bugs, aim for a higher reproduction rate, not a clean
  repro: loop the trigger, parallelise, add stress, narrow timing windows.
  A 50% flake is debuggable, 1% is not.
- Prefer a debugger or REPL inspection over logs; one breakpoint beats ten
  log lines. Never "log everything and grep".
- Tag every temporary debug log with a unique prefix such as `[DEBUG-a4f2]`
  so cleanup is one grep. Untagged logs survive.
- Write the regression test before the fix, but only at a correct seam: one
  where the test exercises the real bug pattern as it occurs at the call
  site. If no correct seam exists, that absence is the finding and must be
  reported, not worked around with a shallow test.
- No fabricated data: never invent a stack trace, a log line, a timing, a
  file path or a command output that was not actually observed.

## Research References

| Claim | Source | Year | Link |
|-------|--------|------|------|
| Diagnosis phases, loop-first discipline and falsifiable-hypothesis rule | `skills/engineering/diagnosing-bugs/SKILL.md` (upstream, MIT) | 2026 | local file |
| Jest selection for a single failing case | `npx jest -t <name>` | n/a | local tool |

## Output Format

Raw structured prose, not a code fence:

```
### <app> diagnosis, <symptom in one line>

Loop: <one command>, red: <observed failure> | green after fix: <expected>
Minimised repro: <the smallest failing scenario>
Hypotheses (ranked): 1. <hypothesis>, predicts: <prediction>
Probes run: <probe> → <result> (supports/refutes <hypothesis n>)
Root cause: <the hypothesis that survived>
Fix: <what changed, where>
Regression test: <file>:<test> at seam <seam> | no correct seam exists: <why>
Cleanup: [DEBUG-*] logs removed: <yes/no> | throwaway harnesses removed: <yes/no>
```
