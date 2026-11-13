---
name: reactnative-best-practices
description: >-
  Write idiomatic, robust, maintainable React Native + Expo apps on TypeScript.
  Use this skill whenever you write, review, refactor, debug, or explain a
  mobile app: screens, navigation and deep links, ViewModels, the SDK, server
  state, offline and outbox, device tiers and the quality governor, lists and
  images, 2D/3D scene engines, push notifications, secure storage, or app
  performance. Trigger on any mention of React Native, Expo, RN, Hermes, the
  New Architecture, Expo Router, FlashList, MMKV, expo-image,
  expo-notifications, EAS, a scene engine, or "fix this screen" even when the
  user never says "best practices". Synthesized from the React Native and Expo
  documentation, the facta mobile handbook, and the mobile performance
  guidance.
---

# React Native best practices

Distilled from the React Native/Expo documentation, the facta mobile handbook
(`PLAYBOOK_FRONTEND_MOBILE.md`), and the performance guidance that keeps an app
usable on the phones most people actually own. The digests live in
`references/`; where they disagree, this file says which to follow and why.

## 1. Mindset

- **The app shell is React Native; heavy 3D is a replaceable module.** Auth,
  onboarding, settings, push and the market flows never depend on a specific
  3D engine. Scenes plug in behind a `SceneEngine` port with tiered adapters.
- **Design for the floor, enhance upward.** Every feature has a low-end path.
  High-end devices get more fidelity, never different logic.
- **Capability tiers, not device lists.** Detect and measure; degrade at
  runtime through the quality governor instead of crashing.
- **One variant = one binary.** Each app ships only the native code,
  permissions and assets it needs; a market app must not carry a game engine.
- **Shared ViewModels and SDK** with web and extension; mobile adds ports.
- **Authorization stays on the server.** The client shapes UX; it never
  decides access.
- **Server-authoritative for anything that matters** (game state, prices,
  payments, entitlements); the client is untrusted.
- **Push is a channel, not a data path.** Payloads are minimal; the app fetches
  the truth after a tap.
- **No vendor lock-in for irreplaceable assets** (avatars, models, user data):
  open formats and your own storage.
- **Measure on real low-end devices in CI.** Performance claims without a
  device lab are opinions.

## 2. Before you hand back code

Run these and fix everything they report:

```bash
npx tsc --noEmit
npx eslint .
npx vitest run
npx expo export --platform all     # the JS bundle the app actually loads
```

- Fix a lint rather than silencing it. A `@ts-expect-error` needs a reason on
  the narrowest line; `@ts-ignore`, `@ts-nocheck` and a blanket
  `eslint-disable` are findings.
- Lint config lives once, in `eslint.config.mjs`. If a project has none,
  suggest the BeautifulReactNative drop-in at `lints/eslint.config.mjs` of
  https://github.com/Facta-Dev/beautifulreactnative.
- Test on a release build on a low-tier Android device, not only a dev build
  on a flagship.

## 3. Platform facts

- **New Architecture only** (legacy removed from RN 0.82/0.84 and Expo SDK 55);
  **Hermes V1** is the default engine since RN 0.84. Do not design around the
  old bridge.
- **Expo SDK 58 / RN 0.88** are the current baseline (verify on adoption);
  use Continuous Native Generation and development builds.
- **The JS thread is the bottleneck on low-end phones.** Keep work off it:
  native lists/images, native drivers, `InteractionManager`/transitions for
  non-urgent work, and no heavy computation during render.
- **Memory is the second bottleneck.** Large images, unbounded lists and 3D
  textures are the usual killers; budget them per device tier.
- **One variant, one binary:** `APP_VARIANT` (`game`, `market`, `avatar`) with
  separate bundle IDs, permissions and store listings; a combined super-app is
  not recommended.

## 4. Architecture: View → ViewModel → SDK

| Layer | Responsibility | May import | Must not import |
|---|---|---|---|
| **View** | Render native components, forward events, navigation, a11y | Its ViewModel hook, the UI kit, platform rendering APIs | The SDK, HTTP, tokens, business rules |
| **ViewModel** | Presentation state, commands, derived values, SDK orchestration | The SDK, ports, shared domain types, React hooks | `react-native`, `react-dom`, a UI component |
| **SDK** | Typed API client, DTOs, error normalization, auth headers | Core ports and types | React, React Native, any UI |
| **Ports** | Platform capabilities behind an interface | nothing | platform APIs |

The contracts below are **unbreakable and non-waivable**: they are the reason
the app survives a low-end device and a store review. Projects can restyle
anything; developers cannot opt out, and neither can you.

1. **The View never talks to the network.** No `fetch`, no `@/sdk` import in a
   screen; the View calls a ViewModel command and renders its state.
2. **The ViewModel is platform-free.** No `react-native`, `react-dom` or UI
   imports; platform differences enter through ports.
3. **The SDK never imports React or React Native.** It is a plain TypeScript
   client shared with web and extension.
4. **Every screen state is rendered:** loading, empty, error, forbidden,
   offline, ready. No blank screen and no infinite spinner.
5. **Authorization is server-side.** Hiding a screen or a button is UX.

When a change would cross a layer, **re-cut the layout**: move the logic to
the layer that owns it. The rule is never to weaken or delete the lints to
make a change pass; a config exception is a contract change.
Review treats a broken contract as an automatic Must fix; `reactnative-review`
ranks it above every other finding.

## 5. Device tiers and the quality governor

- **Detect, don't assume.** Tier from native signals (RAM, CPU cores, GPU,
  benchmark, OS) plus the device's measured budget; cache the tier.
- **Budgets per tier** (Low-class release build, starting points): cold start,
  screen render, list scroll FPS, image memory, 3D frame time. Calibrate on
  your device pool; put the numbers in `docs/device-budgets.md`.
- **A runtime governor** lowers quality (texture size, 3D LOD, particle
  count, animation) when frame time or memory crosses a threshold; it raises
  it again when the device recovers. It never changes business logic.
- **The low-end path is a first-class path:** a 2D/pre-rendered scene, a
  smaller map, fewer images, no particles. Test it in CI.
- **Never ship a flagship-only feature without a fallback** in the same PR.

## 6. Navigation and deep links

- **A typed route table is the source of truth**; Expo Router or a plain app
  entry is the adapter. Routes mirror the URL playbook.
- **Deep links are untrusted input.** Parse the URL against an allowlist,
  validate each parameter against its type and size, and return `undefined`
  for anything unknown.
- **A link received while signed out is queued and resumed after login**, not
  dropped and not replayed blindly.
- **No state-changing action from a link.** A link may open a screen that
  offers an action; the user confirms it.
- **The same parser serves pushes.** Two parsers mean two rule sets, and the
  second one is the one with the bug.
- **Authorization gates the destination**, not just the button; the server
  still authorizes the request.

## 7. Server state, offline and outbox

- **TanStack Query + the shared SDK** for server state: cache keys, retries,
  dedupe, background refresh. No `useEffect` fetch per screen.
- **The query key is the cache identity**: stable, serializable, and it
  contains every input the query depends on.
- **Offline is a designed state.** Show it, keep the last good data, and
  retry with backoff; do not show a generic error for a lost connection.
- **Mutations use an outbox**: write the optimistic row and the queued
  mutation in one transaction, send with an idempotency key, reconcile the
  server's answer, and make rejection visible.
- **The outbox drains on reconnect, foreground and a background task**; it
  survives app restarts.
- **The server wins a conflict**; the local pending change is rejected
  visibly, never silently dropped.
- **Pagination is cursor-based**; a list grows without loading the world.

## 8. Lists, images, 2D and 3D

- **Lists: FlashList v2** (recycling, New Architecture). A stable key, a
  bounded `estimatedItemSize`, and no heavy work in `renderItem`.
- **Images: expo-image** (WebP/AVIF, blurhash/thumbhash, disk cache, memory-
  safe). Correct dimensions; no 4 MB hero on a low-end device.
- **2D/particles: Skia only where needed**; it costs memory and a native
  surface, so it is a per-screen decision, not a default.
- **3D: a tiered `SceneEngine` port.** 2D/pre-rendered fallback → native
  Filament → embedded Godot (Compatibility renderer for low-end) → Unity
  (AR-heavy, high tier only). Never issue GL calls from the JS thread on a
  low-end device.
- **Maps: native vector tiles** (MapLibre/Mapbox GL layers), not hundreds of
  RN Views over a map.
- **Assets: on-demand packs** for models/textures; base binary small. One
  variant ships only its own assets.

## 9. Push notifications

- **expo-notifications with native device tokens** (FCM/APNs); the backend
  sends through FCM HTTP v1 (iOS via APNs). The Expo Push Service is optional,
  not required.
- **The payload is minimal**: an id, a type, a route. No personal data in the
  title/body; the app fetches the truth after a tap.
- **The tap routes through the same parser as a deep link**; the payload
  carries no action of its own.
- **Categories and channels** are declared per platform; the notification's
  interruption level is deliberate.
- **Token lifecycle:** register on login, refresh on change, revoke on
  logout; the server dedupes tokens per user/device.
- **Permission primer:** explain the value before the OS prompt; a denied
  permission is a state, not a crash.
- **Handle all states:** foreground, background, cold start, and a tap on a
  notification whose resource was deleted.

## 10. Storage and secrets

- **MMKV for tiny persisted preferences**; AsyncStorage only for small,
  non-critical data.
- **Tokens live in the OS keystore** (Keychain/Keystore) behind a
  `SecretStore` port; never in AsyncStorage, MMKV, logs or a bundle.
- **Typed storage** with a schema, a version and migrations; run migrations
  on startup and on first read.
- **Clear user data on sign-out and tenant switch**; a shared device is the
  default assumption.
- **Never cache secrets in an image or a screenshot-visible screen**; protect
  sensitive screens from the app switcher where the platform allows.

## 11. Security

- **The client is untrusted.** Game state, prices, payments and entitlements
  are server-authoritative.
- **Auth uses the system browser** (OIDC + PKCE) or the identity slice;
  tokens in the keystore; refresh rotation with reuse detection.
- **No secrets in the bundle.** API keys, signing keys and admin tokens never
  ship.
- **Deep links and push payloads are validated** before they navigate or
  fetch.
- **Jailbreak/root is a risk signal**, evaluated server-side; never a
  client-side block.
- **Certificate pinning only with a rotation plan**; a pinned cert with no
  backup is an outage.
- **Payments follow the store rules** for the good type (digital vs physical);
  verify the current policy.

## 12. Accessibility and i18n

- **Use the platform accessibility props**: `accessible`, `accessibilityLabel`,
  `accessibilityRole`, `accessibilityState`, `accessibilityHint`.
- **Every control has a name**; images have a label or are marked decorative.
- **Dynamic type and screen readers**: layouts survive large text; focus
  moves to the new screen; a modal traps and restores focus.
- **Reduce motion** is honored; no color-only meaning.
- **Strings are keys**, `Intl` for numbers/dates/plurals; layouts survive RTL
  and long translations.

## 13. Performance

- **Startup:** defer non-critical work, lazy-load heavy screens, keep the
  first screen light; measure cold start on a low-tier device.
- **JS thread:** no heavy compute in render; memoize only measured hotspots;
  use `InteractionManager`/transitions for non-urgent updates.
- **Lists:** virtualization and recycling; no unbounded arrays in state.
- **Images:** correct size, modern format, cache; memory is the limit.
- **Bundle/assets:** one variant, on-demand packs, no unused native modules.
- **OTA (EAS Update) only for JS-only changes**; a native change needs a store
  build. Staged rollouts and a kill switch.

## 14. Testing

- **Unit:** ViewModels, the SDK, the deep-link parser, the quality governor,
  the outbox.
- **Component:** React Native Testing Library; query by accessibility role
  and label; mock the network at the boundary (MSW).
- **Device-tier smoke:** the low-end path on a real device or emulator with
  constrained resources.
- **E2E:** Maestro or Detox for the critical journeys (login, the core flow,
  push tap, deep link).
- **Contract:** the message/route/push schemas have valid and invalid
  fixtures.
- **Performance:** a startup/render budget test in CI on the device lab; a
  regression fails the build.

## 15. Cross-skill contract

- `reactnative-review` reviews a change and ranks a broken architecture
  contract above every other finding.
- `reactnative-port` ports a web React app, a bare RN app, or a legacy screen
  to Expo + the New Architecture with the same behavior and tests first.
- The `lints/` config is the machine-checkable half. When this skill and the
  config disagree, the config wins and this file is fixed.

## Sources

- `references/react-native.md` — the platform digest: New Architecture,
  Hermes, JS thread, device tiers, lists, images, storage, push, OTA.
- `references/react-native-patterns.md` — the ViewModel hook, query and
  outbox, the deep-link parser, the quality governor, the SceneEngine port.
- `references/mobile-architecture.md` — the layer contract, ports, variants,
  feature packs and the enforcement map.
- `references/typescript-strict.md` — the strict tsconfig set, discriminated
  unions, branded ids, and the boundary types a mobile app needs.
