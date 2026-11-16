---
name: claim-check
description: "Delegate to the claim-check skill for the <app> frontend."
division: core
---

# /claim-check

## Delegate

Delegate to the **claim-check** skill.

Activate when an `<app>` deliverable makes claims a reader will act on, and
each claim must resolve to an evidence id with a confidence tier. The skill
downgrades or drops uncited claims, labels every tier honestly, and keeps
unanswered questions in an open-questions ledger that closes only with cited
evidence.

Do not activate for a code change whose diff is itself the evidence, for
transcription, or for a claim the requester has already verified and cited.
