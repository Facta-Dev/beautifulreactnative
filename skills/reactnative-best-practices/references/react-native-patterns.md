# React Native patterns

The patterns a mobile app needs, with the failure mode each prevents.

## 1. The ViewModel hook

```tsx
export function useOrders(): {
  state: OrdersState;
  refresh: () => Promise<void>;
  retry: () => Promise<void>;
} {
  const query = useQuery({
    queryKey: ["orders", tenantId],
    queryFn: ({ signal }) => sdk.app.orders.list({ signal }),
  });
  return {
    state: toState(query),
    refresh: query.refetch,
    retry: query.refetch,
  };
}
```

- The hook binds the query to React; the business rules live in the SDK/domain.
- `toState` maps pending/error/empty/data to the five screen states.
- A screen never calls the SDK; it calls `refresh`.

## 2. The five states

```ts
type ScreenState<T> =
  | { status: "loading" }
  | { status: "empty" }
  | { status: "ready"; data: T }
  | { status: "forbidden"; requiredPermission?: string }
  | { status: "offline" }
  | { status: "error"; correlationId?: string };
```

- Every screen renders every state; a `switch` that misses one does not
  compile.
- Offline is a state, not an error; keep the last good data beside it.

## 3. Query keys

- `["orders", tenantId, { status, cursor }]` — every input is in the key.
- Invalidate by prefix after a mutation; never refetch the world.
- Server state lives in the cache, not in a copied `useState`.

## 4. The outbox

1. Write the optimistic row and the queued mutation in one transaction.
2. Send with an idempotency key.
3. On success, write the server's answer and settle the row.
4. On failure, restore the previous value and show why.
5. Drain on reconnect, foreground and a background task.

Without steps 1 and 4 it is data loss with a spinner.

## 5. The deep-link parser

```tsx
export function parseRoute(url: string): Route | undefined {
  const parsed = new URL(url);
  if (!ALLOWED_HOSTS.has(parsed.host)) return undefined;
  switch (parsed.pathname) {
    case "/orders": return { name: "orders" };
    case "/orders/detail": {
      const id = parsed.searchParams.get("id");
      return id && ID_RE.test(id) ? { name: "orderDetail", id } : undefined;
    }
    default: return undefined;
  }
}
```

- Allowlist the host and the routes; validate each parameter.
- Unknown → `undefined` → not-found screen, never a crash.
- The same parser handles push taps.
- A signed-out link is queued and resumed after login.

## 6. The quality governor

```ts
interface QualityGovernor {
  readonly tier: "low" | "mid" | "high";
  readonly limits: { texture: number; particles: number; shadows: boolean };
  report(frameTimeMs: number, memoryMb: number): void;
}
```

- The tier sets the initial limits; `report` lowers them when frame time or
  memory crosses a threshold and raises them when the device recovers.
- It never changes business logic; only fidelity.
- The low-tier path is a real path with a 2D/pre-rendered fallback.

## 7. The SceneEngine port

```ts
type SceneHandle = { readonly id: string };
type SceneAsset = { readonly url: string };
type QualityLimits = { readonly texture: number; readonly particles: number; readonly shadows: boolean };

interface SceneEngine {
  mount(container: SceneHandle, asset: SceneAsset): Promise<void>;
  setQuality(limits: QualityLimits): void;
  unmount(): Promise<void>;
}
```

- Adapters: 2D fallback, native Filament, embedded Godot, Unity.
- The shell chooses the adapter from the tier, never from a device list.
- Assets load from on-demand packs; the shell does not know the engine.
- A scene failure is caught and falls back to the 2D path.

## 8. Push tap

- The payload is `{ v, type, id, route }`; no action.
- The tap goes through the deep-link parser; the screen fetches the resource.
- Foreground, background and cold start have the same handler.
- A deleted resource shows not-found, not a crash.

## 9. Secure storage

- Tokens in Keychain/Keystore behind a `SecretStore` port.
- MMKV for small prefs; never for tokens.
- Clear on sign-out/tenant switch; protect sensitive screens from the app
  switcher where the platform allows.

## 10. Performance patterns

- Virtualize lists; recycle cells; stable keys.
- expo-image with dimensions and a memory budget.
- Lazy-load heavy screens; keep startup light.
- No heavy compute in render; use native drivers/transitions for animation.
- Measure cold start and scroll FPS on the low tier; a regression fails CI.
