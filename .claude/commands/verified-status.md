---
name: verified-status
description: "Delegate to the verified-status skill for the <app> frontend."
division: core
---

# /verified-status

## Delegate

Delegate to the **verified-status** skill.

Activate when a status report, handoff, or "is it done" question about `<app>`
needs every claim separated into verified, not verified, and not run. The
skill emits a table where each row states what works, how it was verified, and
what was never run, and it never reports a live run that did not happen.

Do not activate for a code diff review, or for a claim the requester has
already verified themselves.
