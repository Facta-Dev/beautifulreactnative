# .claude — this repo's Claude Code kit

The playbooks live in the playbook repo, not here. Read them there; do not
restate or import them into this file.

Start with the master playbook — the catalog, precedence and cross-playbook
invariants — then the architecture, stack and shared contracts this repo is
held to:

| Playbook | Governs |
| --- | --- |
| [PLAYBOOK_MASTER.md](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_MASTER.md) | the constitution: catalog, precedence, invariants, Claude Code operating model |
| [PLAYBOOK_FRONTEND.md](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_FRONTEND.md) | the shared architecture contract |
| [PLAYBOOK_FRONTEND_MOBILE.md](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_FRONTEND_MOBILE.md) | the React Native contract this repo implements |
| [PLAYBOOK_URLS.md](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_URLS.md) | route/URL, permission and error-envelope contract |
| [PLAYBOOK_TESTS.md](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_TESTS.md) | testing contract and gates |
| [PLAYBOOK_SECURITY.md](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_SECURITY.md) | security contract, per-language profiles |
| [PLAYBOOK_AUDIT.md](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_AUDIT.md) | SOC 2 / ISO 27001 controls and evidence |
| [PLAYBOOK_CLAUDE_CODE.md](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/PLAYBOOK_CLAUDE_CODE.md) | the kit this repo must have |

The set is split into parts where a playbook exceeds the reference size; the
master index and `manifest.json` in the playbook repo map each part.

Runbook: [CLAUDE_CODE_ROUTING_MODELS_OLLAMA.md](https://github.com/Facta-Dev/ai-coding-playbook/blob/main/CLAUDE_CODE_ROUTING_MODELS_OLLAMA.md)
— model tiers, the routing block, `~/.claude/settings.json`.

Repo-local kit files live next to this file: `agents/`, `skills/`, `commands/`,
`rules/`, `settings.json`. Verify the wiring with:

```bash
bash ~/ai-coding-playbook/scripts/claude-kit/configure-repo.sh <repo> --check
```
