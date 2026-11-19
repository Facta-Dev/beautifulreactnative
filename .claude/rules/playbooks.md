---
paths:
  - "skills/**"
  - "lints/**"
  - "tests/**"
  - "examples/**"
  - "docs/**"
---

# Playbooks for `beautifulreactnative` — load on demand

Before editing a skill, linter config, test or doc, read the playbook that
governs it. Do not `@`-import a playbook: this rule is the routing entry and
the always-on instruction set stays inside the harness budget.

- [`PLAYBOOK_MASTER.md`](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_MASTER.md) — the master index, precedence
  and cross-playbook invariants (`§3` is the constitution).
- [`PLAYBOOK_FRONTEND.md`](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_FRONTEND.md) — the shared architecture contract.
- [`PLAYBOOK_FRONTEND_MOBILE.md`](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_FRONTEND_MOBILE.md) — the React Native contract this repo implements.
- [`PLAYBOOK_SECURITY.md`](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_SECURITY.md) — shared contract.
- [`PLAYBOOK_TESTS.md`](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_TESTS.md) — shared contract.
- [`PLAYBOOK_URLS.md`](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_URLS.md) — shared contract.
- [`PLAYBOOK_AUDIT.md`](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_AUDIT.md) — shared contract.
- [`PLAYBOOK_CLAUDE_CODE.md`](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_CLAUDE_CODE.md) — the kit contract.

The set is split into `_PART<n>` files where needed; `PLAYBOOK_MASTER.md` and
`manifest.json` in the playbook repo map each part.

## Cross-repo relationship (1:n)

The playbook set is one contract with twelve implementations. The **1** is
[`ai-coding-playbook`](https://github.com/Facta-Dev/ai-coding-playbook); the
**n** are the twelve Beautiful repositories. This repository is one of the n
and implements [`PLAYBOOK_FRONTEND_MOBILE.md`](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_FRONTEND_MOBILE.md).

- **n → 1**: this repo implements the contract; it never redefines it. The
  master, the stack playbook and the shared contracts are the source of truth.
  A divergence is a bug in this repo, not a new rule.
- **1 → n**: a contract change in the playbook requires an impact check in
  this repo and in the other implementations before release.
- A gap found here is reported upstream as an issue or a patch; it is not
  patched silently in this repo.

The normative rule and the registry are in
[`PLAYBOOK_MASTER_PART3.md` §12](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_MASTER_PART3.md).
