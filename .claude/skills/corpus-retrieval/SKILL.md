---
name: "<app> Corpus Retrieval"
description: "Answers questions about <app> from its own documentation corpus (docs/, playbooks, references/) index-first, in at most five retrieval rounds, with file:line citations, and refuses plainly when the corpus does not answer."
division: core
---

# <app> Corpus Retrieval skill

A workflow for answering questions from the repository's own documentation
corpus — `docs/`, `playbooks/`, `references/` and their like — not from code
behaviour. An agent invokes this skill when the answer lives in prose the
repository already wrote; the skill supplies the navigation, the agent
supplies the question.

## When to Activate

- A question about `<app>` whose answer is written down in the documentation
  corpus and should be traced to it.
- The requester wants the answer cited to the docs, not to a code path.
- A claim "the docs say X" that needs to be pinned to a file and line.

Do not activate when the answer comes from reading the code paths directly, or
for facts outside the repository's corpus.

## Core Principles

- Index first: read the corpus index before grepping, so retrieval follows
  the corpus's own organisation.
- Retrieval is bounded: at most five rounds, then either cite or refuse.
- Every answer cites file:line, never a vague "the docs say".
- An unanswered question gets a plain refusal, not a confabulated answer.

## Rules

- Read the index before the first grep; do not scan files blind.
- Use grep plus windowed reads; do not read a whole document when a window
  around the hit answers the question.
- Stop after five retrieval rounds: give the best cited answer, or refuse.
- Every answer carries file:line; no citation means no answer.
- When the corpus does not answer, say so explicitly and point at what is
  missing, rather than filling the gap from general knowledge.

## Research References

Provenance table, every claim in a finding needs a row.

| claim | source | year | link |
| --- | --- | --- | --- |
| Index-first navigation, a bounded retrieval round count, and file:line citations | kb-retriever skill | 2026 | `skills/kb-retriever/SKILL.md` |

## Output Format

Deliver, in order:

1. The answer, in the corpus's own terms, with a file:line citation for every
   assertion.
2. The retrieval log: how many rounds were used and which files were read.
3. Either the cited answer or the explicit refusal with what is missing.

Example:

```
corpus: answer = "pagination is capped at 50 rows" (docs/api.md:12-14)
corpus: rounds = 2 (index -> docs/api.md)
corpus: cited
```
