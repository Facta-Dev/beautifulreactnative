---
name: "research"
description: "Investigates a question about <app> against primary sources and captures the findings as a cited Markdown brief in the repo."
division: core
---

# <app> Research skill

> Reusable workflow for answering a technical question with primary
> sources and leaving a cited brief behind. An agent invokes this skill; the
> agent supplies the question, the skill supplies the sourcing discipline.

## When to Activate

Activate this skill when a question needs evidence from sources outside the
working session: a protocol, a library's real behaviour, a spec, an API
contract, a competitor's design. Typical triggers:

- The request says "research", "find out", "look up", or asks what a
  dependency, standard, or upstream project actually does.
- Documentation in the repo is stale or ambiguous and the answer decides an
  implementation.
- A background agent is asked to gather reading legwork and report back.

Do NOT activate this skill for facts available in the repo itself (read the
code or the vendored docs), and not to gather general background that no
decision depends on.

## Core Principles

- **Primary sources only.** Official docs, the source code itself,
  specifications, and first-party API references. A blog post about a
  library is not a source for that library's behaviour; the library's own
  docs and code are.
- **Follow every claim back to its owner.** Each statement in the brief
  names the source that owns it (the spec section, the doc page, the file
  and line).
- **Delegation, not absorption.** Run the reading in a background agent
  with a fresh context window so the main session keeps its own context for
  the decision the research informs.
- **The brief is the deliverable.** The research ends in a Markdown file in
  the repository, not in a chat answer that evaporates.
- **Ship the file where the repo already keeps such notes.** Match the
  existing convention; if there is none, put it in a sensible place and
  state where in the summary.
- **Read the whole source when it matters.** A partial read of a spec is
  how confident wrong answers get written.

## Rules

- No fabricated data: never invent a citation, a URL, a version number, a
  benchmark figure, or a quotation. A claim without a source that was
  actually read is either dropped or tagged "unverified".
- Every factual claim in the brief carries its source inline (a link, a
  file path with line, or a spec section).
- Distinguish clearly between what the source states and what the agent
  infers from it.
- Record the version or date the source was read at; APIs and defaults
  change.
- Never write a "brief" that is a summary of a summary. Second-hand
  write-ups are leads, not sources: follow them to the primary source
  before citing them.
- One question, one brief file. Do not accumulate unrelated findings in the
  same document.
- The brief is Markdown in the repository, so it follows the repository
  conventions: English only, no secrets, no invented URLs, and no
  credentials quoted from the sources.

## Research References

| Claim | Source | Year | Link |
|-------|--------|------|------|
| Primary-source rule, cited-brief deliverable, background-agent delegation | `skills/engineering/research/SKILL.md` (upstream, MIT) | 2026 | local file |
| Repository docs a brief may cite | `docs/architecture/` | n/a | local file |

## Output Format

Raw structured prose, not a code fence:

```
### <app> research, <question in one line>

Brief written to: <path in the repo>
Sources consulted: <n> (<primary>/<secondary>)
Key findings:
- <finding> (<source>)
- <finding> (<source>)
Unverified or disputed: <claim> (<what is missing>)
Open questions: <what was not answered, and what would answer it>
```
