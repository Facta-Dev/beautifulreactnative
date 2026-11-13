---
name: reactnative-review
description: >-
  Review a React Native + Expo app on TypeScript — a screen, a ViewModel, the
  navigation and deep-link parser, the SDK, offline and outbox code, push
  handling, the quality governor, a scene adapter, or a diff — and produce a
  prioritized report where every finding cites the file and line, the rule it
  breaks, and the smallest fix. Use this skill whenever the user asks to
  review, audit, critique, or "find problems in" a mobile app or a screen.
  Trigger on review, audit, code review, PR review, "what is wrong with this
  screen", "check this deep link", "review this RN feature", or a pasted
  component/ViewModel. Architecture and device-tier contracts always rank
  first.
---

# React Native review

A review is a prioritized list of findings, not a rewrite. Read the whole
change first. Every finding has four parts: **location** (file and line),
**severity**, **the rule it breaks** (named or quoted), and **the smallest
fix**. If you cannot cite a rule or a user-visible consequence, it is not a
finding; it is a preference for the Notes section, if anywhere.

## 1. Report shape

```text
## Verdict
<one paragraph: what this change does, whether it is safe to ship, and the
single most important thing to fix>

## Must fix
1. <file>:<line> — <finding>. Rule: <rule or contract>. Fix: <smallest fix>.

## Should fix
...

## Notes
...

## Waived gates
...
```

- **Must fix** blocks merge or release: a broken layer, a missing screen
  state, an unvalidated deep link or push, a token outside the keystore, an
  outbox that loses a mutation, a flagship-only path with no fallback.
- **Should fix** is worth doing in this change or the next: a list without
  recycling, an image without dimensions, a slow startup on the low tier.
- **Notes** is optional. Do not pad the report to look thorough.

## 2. Categories, in ranking order

### Architecture contracts (always Must fix, ranked first)

A broken architecture contract (ranked above everything) is a Must fix even
when the screen works. Check:

- A **View** imports the SDK, calls `fetch`, reads a token, or re-implements a
  domain rule. The View calls its ViewModel.
- A **ViewModel** imports `react-native`, `react-dom` or a UI component.
  Platform differences enter through ports.
- The **SDK** imports React or React Native; it must stay a plain TypeScript
  client shared with web and extension.
- A screen state is missing: loading, empty, error, forbidden, offline, ready.
- Authorization decided in the client as a security control.

Name the violated rule and quote it; the fix is to move the logic to the layer
that owns it.

### Device tiers and performance

- A feature with no low-end path; a flagship-only assumption.
- The quality governor not consulted before loading a heavy asset/scene; a
  governor that changes business logic instead of fidelity.
- Heavy compute on the JS thread; a list without virtualization/recycling; an
  unbounded array in state.
- Images without dimensions or a memory budget; a 4 MB hero on a low tier.
- Startup work that blocks the first screen; a heavy screen not lazy-loaded.
- A performance claim with no device-lab evidence.

### Navigation and deep links

- A deep link parsed without an allowlist, type/size validation, or an
  unknown-route fallback.
- A link that performs a state-changing action instead of offering it.
- A link received while signed out that is dropped or replayed blindly.
- A second route parser for push (it will drift from the deep-link one).
- A route guard presented as access control; the server must authorize.
- A navigation state that loses the back stack or the tab context.

### Server state, offline and outbox

- A `useEffect` fetch per screen instead of the query layer.
- A query key that omits an input, or changes every render.
- No offline state; the last good data is dropped on a network error.
- A mutation without an idempotency key; an optimistic update without a
  rollback; an outbox that is not persisted or not drained on reconnect.
- A conflict silently overwritten; a rejected mutation invisible to the user.
- Pagination that loads the world, or a cursor that is not stable.

### Push

- A payload with personal data, a full resource, or an action of its own.
- A tap that does not go through the same parser as a deep link.
- No handler for foreground/background/cold start; a notification whose
  resource was deleted crashes.
- Token not refreshed/revoked; the server not deduping tokens.
- A permission prompt without a primer; a denied permission treated as a
  crash.

### Security

- A secret, signing key or admin token in the bundle or config.
- A token in AsyncStorage/MMKV/logs instead of the OS keystore.
- A client-side entitlement/payment/game-state decision; the server must be
  authoritative.
- An auth flow in an embedded webview instead of the system browser with PKCE.
- A deep link or push payload that navigates or fetches without validation.
- Certificate pinning without a rotation plan; jailbreak/root as a client-side
  block.

### Accessibility and i18n

- A control without `accessibilityLabel`/`accessibilityRole`; an interactive
  `View` with `onPress` and no accessibility state.
- Layouts that break with large text; a modal without focus handling.
- Reduce-motion ignored; color-only meaning.
- Literal strings concatenated; RTL/long translations not considered.

### Tests

- No test for the ViewModel states, the deep-link parser, the outbox, or the
  quality governor.
- A component test that asserts implementation instead of accessibility
  behavior; a network mock below the boundary.
- No low-tier smoke test; no E2E for login, the core flow, push tap, deep
  link.
- A performance budget test missing from CI.

## 3. Waived gates

If the diff deletes or weakens a lint, a test, a type, a budget or an
accessibility check, flag the deletion itself, loudly — even when the new
code looks fine. Look for:

- A removed `eslint-disable` **or a new one without a description**; a
  `@ts-expect-error` that suppresses a real error; `@ts-ignore` or
  `@ts-nocheck`.
- A lint rule turned off in `eslint.config.mjs`, a layer wall removed, or a
  `no-restricted-imports` exception for one file.
- A skipped low-tier smoke test; a performance budget raised without a
  device-lab run; a deep-link/push fixture deleted.
- A `tsconfig` strictness flag turned off; `any` introduced at a boundary.
- A kill switch or a fallback removed to ship a flagship feature.

State the deletion, the reason it claims, and what it would take to keep the
gate. "Temporarily" is not a reason; an expiring waiver with an owner is.

## 4. How to review

1. **Read the change twice.** First for intent, then for the diff.
2. **Run the gates if you can:** `npx tsc --noEmit`, `npx eslint .`,
   `npx vitest run`, the export, a release build on a low-tier device.
3. **Check the architecture and device-tier path first.** They are the
   expensive findings; style is cheap.
4. **Cite evidence.** File and line for every Must fix; a rule name or a
   quoted contract for every finding.
5. **Propose the smallest fix.** "Rewrite the screen" is not a fix; "move the
   fetch to `useLeadDetail` and render the five states" is.
6. **Stop when the change is safe.** An empty Should-fix section is a valid
   review.

## 5. Worked example

`examples/review-mobile-screen.md` is a full review of a small orders screen:
the buggy component and ViewModel, the findings in ranking order, and the
fixed module. It shows the layer violation first, then the missing offline
state, then the list/image budget, then the deep-link gap.

## 6. Cross-skill contract

- `reactnative-best-practices` defines the rules this review cites. When a
  finding and the skill disagree, the skill is the source.
- `reactnative-port` produces the change; this review checks it before
  release.
- The `lints/` config is the machine-checkable subset. A finding the config
  can catch should become a rule, not a repeated comment.
