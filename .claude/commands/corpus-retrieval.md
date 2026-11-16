---
name: corpus-retrieval
description: "Delegate to the corpus-retrieval skill for the <app> frontend."
division: core
---

# /corpus-retrieval

## Delegate

Delegate to the **corpus-retrieval** skill.

Activate when a question about `<app>` is answered in its own documentation
corpus (docs/, playbooks, references/) and should be traced there. The skill
reads the index first, greps and window-reads, stops after at most five
retrieval rounds, and cites file:line for every answer — or refuses plainly
when the corpus does not answer.

Do not activate for facts available by reading the code paths directly.
