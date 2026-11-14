# beautifulreactnative — Architecture Diagrams

Rendered with [Archify](https://github.com/tt-a1i/archify). Each entry is a standalone,
explorable HTML page (inline SVG, dark/light themes, live motion) paired with its source
JSON candidate. The set documents the **React Native + Expo / TypeScript** stack this repo
teaches: the View → ViewModel → SDK → API layer contract, the ports that keep the
ViewModel platform-free, the OS keystore credential boundary, the offline outbox, the
query cache, the device tiers and the quality governor — with `lints/` as the
machine-checkable half of the contract.

| Diagram | Type | What it shows | JSON | HTML |
|---|---|---|---|---|
| c4-containers | architecture | Container view: the Expo app binary (one variant, one bundle), the system browser that runs OIDC + PKCE, the backend API as the server-authoritative system, the push service, and the two platform stores — the OS keystore and the typed local store — with the credential boundary named as a security group | [json](c4-containers.json) | [html](c4-containers.html) |
| services-slices | architecture | The layer topology the contract enforces: the composition root, the feature pack (`features/<name>/{views,viewmodels,ports,assets}`), the ViewModel hooks, the SDK, the shared packages (`sdk · core · ui-native · tokens`), the ports and the platform adapters — each wall labeled with the `no-restricted-imports` rule that pins it | [json](services-slices.architecture.json) | [html](services-slices.architecture.html) |
| auth-algorithm | workflow | The trust algorithm: sign in → system browser (OIDC + PKCE) → token grant → OS keystore behind the SecretStore port → API call → server authorization, with the 401 refresh-rotation branch and the 403 forbidden state | [json](auth-algorithm.workflow.json) | [html](auth-algorithm.workflow.html) |
| outbox-algorithm | workflow | The offline outbox as five steps: write the optimistic row and the queued mutation in one transaction → send with an idempotency key → settle with the server's answer → restore the previous value and show why on failure → drain on reconnect, foreground and a background task | [json](outbox-algorithm.workflow.json) | [html](outbox-algorithm.workflow.html) |
| auth-sequence | sequence | The full sign-in chain across the user, the ViewModel, the system browser, the backend API and the OS keystore — exchange, store, read back, and use | [json](auth-sequence.sequence.json) | [html](auth-sequence.sequence.html) |
| outbox-sequence | sequence | One mutation end to end: enqueue locally, drain with the idempotency key, settle against the server's answer, invalidate the query prefix — and the alternative branch where the server wins the conflict | [json](outbox-sequence.sequence.json) | [html](outbox-sequence.sequence.html) |
| database-dataflow | dataflow | Where persistent and state data goes: the OS keystore for tokens and secrets, MMKV for small persisted preferences, the typed store for the outbox, the TanStack Query cache as the last good data, and the API as the authority | [json](database-dataflow.dataflow.json) | [html](database-dataflow.dataflow.html) |
| runtime-lifecycle | lifecycle | The runtime states of an Expo app: cold start → hydrate the stores → mount the typed route table → the session gate → steady state, with the offline, background and settled branches | [json](runtime-lifecycle.lifecycle.json) | [html](runtime-lifecycle.lifecycle.html) |

The diagrams are conceptual and source-backed: every component, boundary and edge is
traceable to the repository's README, the skill digests
(`skills/reactnative-best-practices/references/`) or the lints config
(`lints/eslint.config.mjs`). No infrastructure is invented — where the series file name
describes a backend mechanism, the role is **adapted** to the real React Native
mechanism and labelled here:

- **auth-*** is adapted to the client's credential boundary: the OS keystore (Keychain /
  Keystore) behind the `SecretStore` / `TokenStore` ports, with OIDC + PKCE in the system
  browser. This repo teaches no authentication server — the backend identity slice is an
  external system.
- **outbox-*** is adapted to the offline outbox: a persisted local queue drained on
  reconnect, foreground and a background task. There is no broker and no server-side
  queue in this stack.
- **database-dataflow** is adapted to the device stores (OS keystore, MMKV, the typed
  local store) plus the API. The contract requires a persisted, versioned, transactional
  store but names no particular database engine, so the diagram names the role, not a
  vendor.
