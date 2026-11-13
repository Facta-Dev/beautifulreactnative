# React Native platform digest

The platform facts a mobile app depends on, with the design consequence. React
Native and Expo documentation is the source; this is the review checklist.

## 1. Runtime

- **New Architecture only**: Fabric renderer, TurboModules, JSI. Legacy bridge
  is removed from RN 0.82/0.84 and Expo SDK 55.
- **Hermes V1** is the default engine since RN 0.84; prefer it; it trades some
  JIT speed for startup and memory, which is what low-end devices need.
- **The JS thread is single.** A long render or a synchronous native call
  drops frames for the whole app. Native drivers, lists and images do the
  heavy work.
- **Expo SDK 58 / RN 0.88** are current (verify on adoption). Continuous
  Native Generation + development builds; a config plugin per native module.

## 2. Device tiers

| Signal | What it tells you |
|---|---|
| RAM | Whether large images/3D are safe |
| CPU cores/speed | JS-thread headroom |
| GPU/renderer | 3D/particle capability |
| OS version | Feature availability |
| Measured first-screen time | The real budget |

- Tier at startup, cache it, and let the quality governor adjust at runtime.
- Budgets are per tier and per screen: cold start, first render, scroll FPS,
  image memory, 3D frame time.
- Calibrate on a device lab; a flagship number is not a budget.

## 3. Lists and images

- **FlashList v2** recycles cells; stable keys and `estimatedItemSize` matter.
- **expo-image**: WebP/AVIF, blurhash/thumbhash placeholders, disk/memory
  cache, explicit dimensions.
- Avoid unbounded arrays in state; paginate with a cursor.
- A long list of RN `View`s over a map is a frame-rate bug; use native GL
  layers.

## 4. Storage

- **MMKV** for tiny persisted preferences; fast, synchronous, not for large
  data or secrets.
- **AsyncStorage** only for small non-critical data.
- **Keychain/Keystore** for tokens and secrets, behind a `SecretStore` port.
- **Typed stores** with a schema, a version and migrations; run them on
  startup and first read.
- **Clear on sign-out/tenant switch**; a shared device is the default.

## 5. Push

- **expo-notifications** obtains an Expo token or native device tokens; for
  backend control use native FCM/APNs tokens and send through FCM HTTP v1.
- Payload: `{ v, type, id, route }`; no personal data, no full resource, no
  action.
- The tap routes through the deep-link parser; the app fetches the resource.
- Categories/channels and interruption levels are declared per platform.
- Token lifecycle: register on login, refresh on change, revoke on logout;
  the server dedupes.

## 6. Navigation and deep links

- Expo Router is file-based and deep-link aware; a plain entry with a typed
  route table is valid for a small app.
- The route table is the source of truth; the router is an adapter.
- A deep link is parsed against an allowlist, with type/size validation and a
  not-found fallback.
- A link received while signed out is queued and resumed after login.
- No state-changing action from a link; it opens a screen that offers the
  action.

## 7. Offline and background

- TanStack Query + the SDK for server state; the cache is the last good data.
- An outbox persists mutations with an idempotency key; it drains on
  reconnect, foreground and a background task.
- A conflict is resolved by the server; the local pending change is rejected
  visibly.
- Background execution is constrained by the OS; design for "it may not run",
  not for a guarantee.

## 8. 3D and scene engines

- A `SceneEngine` port with tiered adapters: 2D/pre-rendered fallback →
  native Filament → embedded Godot (Compatibility renderer) → Unity (AR,
  high tier).
- GL calls from the JS thread on a low-end device are a frame-rate bug.
- Assets are on-demand packs; the base binary stays small.
- Open formats (glTF/GLB, VRM) and your own storage; no single-vendor avatar
  dependency.

## 9. Release and updates

- EAS Build/Submit; EAS Update for JS-only changes; a native change needs a
  store build.
- Staged rollouts, a remote kill switch and a minimum-version gate.
- Android: arm64-v8a primary; 16 KB page size support for native libs (verify
  the current Play requirement).
- iOS: arm64; privacy manifest and required-reason APIs where applicable.

## 10. Testing

- Unit: ViewModels, SDK, parsers, governor, outbox.
- Component: React Native Testing Library, accessibility-first queries.
- E2E: Maestro/Detox for login, core flow, push tap, deep link.
- Device lab: the low tier, a mid tier, a flagship; startup/render budgets.
- Contract: route/push/message schemas with valid and invalid fixtures.
