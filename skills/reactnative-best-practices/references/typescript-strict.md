# TypeScript strict for React Native

The tsconfig set and the type patterns that make a mobile app hard to break.
The point is not "more types"; it is that an invalid screen state or an
unvalidated deep link fails to compile.

## 1. The strict set

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "moduleResolution": "bundler",
    "module": "ESNext",
    "target": "ES2022",
    "jsx": "react-jsx",
    "skipLibCheck": true
  }
}
```

- `noUncheckedIndexedAccess` turns `rows[0]` into `Row | undefined`; the
  compiler forces the check the screen needs.
- `exactOptionalPropertyTypes` distinguishes an absent field from an explicit
  `undefined`; route params and push payloads depend on the difference.
- `verbatimModuleSyntax` makes `import type` explicit.
- `jsx: react-jsx` matches the RN/Expo transform.

## 2. Screen states

```ts
type ScreenState<T> =
  | { status: "loading" }
  | { status: "empty" }
  | { status: "ready"; data: T }
  | { status: "forbidden"; requiredPermission?: string }
  | { status: "offline" }
  | { status: "error"; correlationId?: string };
```

- A literal `status` is the discriminant; narrow with `switch`.
- Every switch is exhaustive: `default: { const _never: never = state; }` or
  `satisfies never`. A new state is a compile error.
- Never model a screen with independent booleans; impossible combinations
  still compile.

## 3. Branded ids

```ts
type Brand<T, B extends string> = T & { readonly __brand: B };
type OrderId = Brand<string, "OrderId">;
type TenantId = Brand<string, "TenantId">;
```

A function that takes `OrderId` cannot receive a `TenantId` or a raw route
param. Brand at the deep-link/SDK boundary, not in every screen.

## 4. Result types

```ts
type Result<T, E> = { ok: true; data: T } | { ok: false; error: E };
```

- Use cases return `Result` for expected failures; throw only for programmer
  errors.
- A push/deep-link parser returns `Route | undefined`, never throws for an
  unknown URL.
- Every error carries a stable `code` and a `correlationId`.

## 5. Boundary types

- Parse the deep link, the push payload, the config, the storage value and the
  API response once; `unknown` at the boundary, never `any`.
- A route param is parsed and branded before it reaches a screen.
- A DTO is not a view model: map it in the SDK/ViewModel, not in JSX.

## 6. Async discipline

- `no-floating-promises` and `no-misused-promises` are errors: await, `void`
  with an internal catch, or return the promise.
- A query/mutation returns a typed result; a screen never sees a raw thrown
  error.
- A background task handles failure and retries with an idempotency key.

## 7. Type-level review questions

1. Could this screen be a union instead of booleans?
2. Is every switch exhaustive?
3. Is this `as` justified and commented?
4. Is the id branded, or can a raw string stand in?
5. Is every external value parsed once (link, push, config, API)?
6. Does the type survive `noUncheckedIndexedAccess`?
7. Does the error path return a `Result` instead of throwing?
