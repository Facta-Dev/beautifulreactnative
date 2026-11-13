---
name: reactnative-port
description: >-
  Port an existing UI to an idiomatic React Native + Expo app with the same
  behavior: a web React app, a bare React Native app moving to Expo and the
  New Architecture, a legacy screen, or a native screen from another stack.
  Use this skill whenever the user asks to migrate, convert, rewrite, or port
  an app or screen to React Native/Expo, modernize a legacy RN app, or move a
  web flow to mobile. Trigger on port, migrate, convert, rewrite in React
  Native, "turn this web app into an app", "move this to Expo", or a pasted
  component. Port the original tests first, keep behavior identical, and write
  a PORTING.md.
---

# React Native port

A port preserves behavior while changing the platform. The output is not a web
app rendered in a mobile shell; it is a mobile app a React Native developer
would have written, with the same observable behavior and tests proving it.

## 1. The order of work

1. **Read the source and its tests.** The tests are the specification. If
   there are none, write characterization tests against the current behavior
   first.
2. **Port the tests first.** Same cases, same assertions, expressed in RN
   Testing Library or Vitest. A port without a failing test is a rewrite with
   hope.
3. **Map the screens, state and data flow.** List every screen, input,
   output, navigation path, network call and local-storage key.
4. **Define the layers.** View → ViewModel → SDK; platform capabilities behind
   ports; a typed route table.
5. **Port one screen at a time**, with the five states (loading, empty,
   error, forbidden, offline, ready).
6. **Run the gates.** tsc, eslint, tests, export, a release build on a
   low-tier device.
7. **Write `PORTING.md`.** Every deliberate difference, every web/native
   capability not reproduced, every permission/asset change, and why.

## 2. Web React → React Native mapping

| Web | React Native / Expo |
|---|---|
| `div`/`span` | `View`/`Text`; text must be inside `Text` |
| `button` | `Pressable`/`TouchableOpacity` with `accessibilityRole="button"` |
| `img` | `expo-image` with dimensions and a memory-aware size |
| `a href` | The router (`Link`/`router.push`) with a typed route |
| CSS/flexbox | `StyleSheet`/NativeWind; flexbox defaults differ (`flexDirection: column`) |
| `window`/`document` | Platform APIs behind a port; no DOM |
| `localStorage` | MMKV for small prefs; the keystore for secrets |
| `fetch` in a component | The SDK through the ViewModel/query layer |
| `useEffect` routing | The route table and deep-link parser |
| Browser back/forward | The navigation stack; Android hardware back |
| Service worker | Background tasks/alarms; no persistent JS |
| `aria-*` | `accessibilityLabel`/`Role`/`State`/`Hint` |
| Hover/focus-visible | Press states; keyboard only where a hardware keyboard exists |
| Unbounded DOM list | `FlashList` with recycling |
| 3D on the GPU | A tiered `SceneEngine` port with a 2D fallback |

## 3. Bare RN → Expo + New Architecture

- **Move to Continuous Native Generation** and development builds; keep a
  config plugin for each custom native module.
- **Replace bridge-era libraries** with New Architecture/Fabric-compatible
  versions; a library without a Fabric/TurboModule path is a blocker.
- **Move navigation to the typed route table** (Expo Router or a plain
  entry); deep links use one parser.
- **Move storage** to the typed store + keystore; migrate the old keys with a
  versioned migration.
- **Move images/lists** to expo-image/FlashList; measure on a low tier.
- **Keep the native modules that are still needed** behind ports; remove the
  ones a JS library replaces.

## 4. Native screen (Android/iOS) → React Native

- **Map the screen state and events**, not the widget tree; the RN screen
  renders the same states with the same labels.
- **Map platform affordances**: Android back, iOS swipe-back, safe areas,
  dynamic type, dark mode, RTL.
- **Keep accessibility parity**: labels, roles, focus order, large text.
- **Port the tests** against the same behavior; add an E2E for the journey.
- **Do not reproduce a native transition with a JS timer**; use the platform
  navigation transition or a native driver.

## 5. Behavior parity checklist

- [ ] Every screen exists with the five states (loading, empty, error,
      forbidden, offline, ready).
- [ ] Every input, command and callback has the same effect.
- [ ] Every route and deep link resolves to the same screen; unknown links
      fall back.
- [ ] Every network call has the same method, path, payload and headers.
- [ ] Offline behavior is designed; the outbox is persisted and drained.
- [ ] Push uses the same parser as deep links; the payload is minimal.
- [ ] Tokens are in the keystore; no secret in the bundle.
- [ ] Accessibility labels/roles and dynamic type are preserved.
- [ ] The low-tier path exists and was tested on a device/emulator.
- [ ] The original tests pass, ported; new tests cover the RN-only paths.
- [ ] `PORTING.md` lists every deliberate difference.

## 6. What not to do

- **Do not keep the web shape.** A screen with `div`s and CSS ports, or a
  `fetch` in a component, is a port that will be rewritten again.
- **Do not assume a flagship.** A feature without a low-end path is not
  ported.
- **Do not skip the keystore.** A web app's `localStorage` token is not a
  mobile token.
- **Do not use one 3D engine for every tier.** Port the scene behind the
  `SceneEngine` port; add the low-end fallback first.
- **Do not silently change behavior.** Reproduce the source quirk, pin it with
  a test, and list the fix as a follow-up — or fix it deliberately and say so.

## 7. Cross-skill contract

- `reactnative-best-practices` is the target style; every ported screen
  follows it.
- `reactnative-review` reviews the port before release and ranks a broken
  architecture contract above every other finding.
- The `lints/` config is the machine-checkable half; a port that needs a lint
  exception is a port that has not finished.
