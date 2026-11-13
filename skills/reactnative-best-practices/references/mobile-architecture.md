# Mobile architecture contract

The layer contract from the facta mobile handbook, reduced to what a React
Native app must keep. It is enforced by `lints/eslint.config.mjs`; this file
explains why each wall exists.

## 1. The layers

```text
View (screens, native components)  ──►  ViewModel hook  ──►  SDK  ──►  API
      ▲                                    │                  │
      └──── state + events ────────────────┘                  └── ports: TokenStore,
                                └── ports: Navigator,             Transport, Clock
                                    Notifier, Permissions
```

| Layer | Responsibility | May import | Must not import |
|---|---|---|---|
| **View** | Render, forward events, navigation, a11y | Its ViewModel hook, the UI kit, platform rendering APIs | The SDK, HTTP, tokens, business rules |
| **ViewModel** | Presentation state, commands, derived values, SDK orchestration | The SDK, ports, shared domain types, React hooks | `react-native`, `react-dom`, a UI component |
| **SDK** | Typed API client, DTOs, error normalization, auth headers | Core ports and types | React, React Native, any UI |
| **Ports** | Platform capabilities behind an interface | nothing | platform APIs |
| **Core** | Shared pure types, route builders, error types | nothing | everything else |

A View that calls the SDK cannot be tested without a network and hides the
offline state the user needs. A ViewModel that imports `react-native` cannot
run on web or in a test. An SDK that imports React cannot be shared with the
other clients.

## 2. Ports

| Port | Declared by | Implemented by |
|---|---|---|
| `Navigator` | ViewModel | the router adapter |
| `Notifier` | ViewModel | push/local notification adapter |
| `SecretStore` | ViewModel/SDK | Keychain/Keystore adapter |
| `StoragePort` | ViewModel | MMKV/typed store adapter |
| `LocationPort` | feature | native location adapter |
| `SceneEngine` | feature | tiered 3D adapters + 2D fallback |
| `PushPort` | ViewModel | expo-notifications adapter |
| `Clock` | domain | system clock (tests use a fake) |
| `TokenStore` | SDK | keystore adapter |
| `Transport` | SDK | fetch adapter |

A port belongs to the consumer. A use case that needs "the API" depends on the
SDK interface, not on a concrete client; the composition root wires the
adapter.

## 3. Variants and feature packs

- One monorepo, three apps (`game`, `market`, `avatar`) via `APP_VARIANT`;
  separate bundle IDs, permissions and store listings.
- Shared packages: `sdk`, `core`, `viewmodels`, `ui-native`, `tokens`; each
  app imports only what it ships.
- A feature pack: `features/<name>/{views,viewmodels,ports,assets}`; the
  feature name matches the backend slice, the route module and the permission
  prefix.
- A variant that does not ship a feature does not bundle its native module or
  assets. A market app must not carry a game engine.

## 4. Navigation

- A typed route table is the source of truth; Expo Router or a plain entry is
  the adapter.
- Routes mirror the URL playbook; the `{userType}` segment is an experience
  namespace, never a permission.
- A route guard shapes UX; the server authorizes the request.
- Deep links and push taps use the same parser; unknown routes fall back.
- The navigation state preserves the back stack and the tab context.

## 5. State

- **Server state** in TanStack Query + the SDK.
- **Client state** in selector-based Zustand or local state; no heavy global
  store.
- **Persisted prefs** in MMKV; **secrets** in the keystore.
- **URL/deep-link state** in the route; a link restores the screen.

## 6. Offline and sync

- The query cache is the last good data; offline is a visible state.
- The outbox persists mutations with an idempotency key; it drains on
  reconnect, foreground and a background task.
- The server wins a conflict; the local change is rejected visibly.
- Pagination is cursor-based; the list grows without loading the world.

## 7. Device tiers

- Tier detection, per-tier budgets, a runtime quality governor.
- A low-tier path for every heavy feature; the governor changes fidelity, not
  logic.
- A device lab in CI; a performance budget regression fails the build.
- One variant ships only its own native modules and assets.

## 8. Security

- The client is untrusted; game state, prices, payments and entitlements are
  server-authoritative.
- Auth uses the system browser (OIDC + PKCE) or the identity slice; tokens in
  the keystore.
- No secret in the bundle; deep links and push payloads are validated.
- Jailbreak/root is a server-side risk signal, not a client-side block.
- Certificate pinning only with a rotation plan.

## 9. Testing the layers

- **Domain/ViewModel/SDK:** plain Vitest; no DOM, no native.
- **View:** RN Testing Library with accessibility queries; mock the network
  at the boundary.
- **Parsers/governor/outbox:** unit tests with valid and invalid fixtures.
- **Device-tier smoke:** the low tier on a real device/emulator.
- **E2E:** Maestro/Detox for login, the core flow, push tap and deep link.
- **Performance:** startup/render budgets on the device lab.

## 10. The enforcement map

| Rule | Where |
|---|---|
| View does not import the SDK | `no-restricted-imports` for `src/**/views/**`: `@/sdk` |
| ViewModel does not import a rendering platform | `no-restricted-imports` for `src/**/viewmodels/**`: `react-native`, `react-dom`, `@/views` |
| SDK does not import React | `no-restricted-imports` for `src/sdk/**`: `react`, `react-native`, `@/session` |
| Hooks rules | `react-hooks/rules-of-hooks`, `react-hooks/exhaustive-deps` |
| No remote code / eval | `no-eval`, `no-new-func`, `@typescript-eslint/no-implied-eval` |
| No silenced types | `@typescript-eslint/ban-ts-comment` |
| No unlimited disables | `@eslint-community/eslint-comments/*` |

When a change needs an exception, re-cut the layout; do not add a path to the
exception list. A config exception is a contract change.
