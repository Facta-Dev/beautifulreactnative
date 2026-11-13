# A worked review: the orders screen

The subject is a small orders screen with a detail deep link. It works on a
flagship dev build and has five findings that a review must rank in a useful
order. The fixed version follows the contract in
`reactnative-best-practices`.

## The module under review

```tsx
// src/features/orders/views/OrdersScreen.tsx
import { useEffect, useState } from "react";
import { FlatList, Text, View } from "react-native";
import { sdk } from "@/sdk";

export function OrdersScreen() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    sdk.app.orders.list().then((data) => {
      setOrders(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <Text>Loading...</Text>;

  return (
    <View>
      <FlatList
        data={orders}
        renderItem={({ item }) => (
          <View onClick={() => sdk.app.orders.archive(item.id)}>
            <Text>{item.id}</Text>
            <Image source={{ uri: item.image }} />
          </View>
        )}
      />
    </View>
  );
}

// app links
export function onLink(url: string) {
  const id = url.split("id=")[1];
  navigation.navigate("OrderDetail", { id });
}
```

## The report

### Verdict

The screen renders on a fast connection and a flagship phone, and fails on
the states most users hit: offline, forbidden, error. Not safe to ship; the
layer violation is first because it is the one every other screen copies.

### Must fix

1. `OrdersScreen.tsx:3` — the **View** imports the SDK and calls it directly.
   Rule: *the View never talks to the network; the ViewModel calls the SDK*.
   Fix: `useOrders()` returns the state and commands; the screen renders them.
2. `OrdersScreen.tsx:10` — loading is a boolean; offline, error, forbidden and
   empty never render. Rule: *every screen renders every state*. Fix: one
   discriminated union and a `switch` that misses a state does not compile.
3. `OrdersScreen.tsx:23` — a `View` with `onClick` (not a prop on RN), no
   `accessibilityRole`, and an archive mutation fired from the row. Rule:
   *an interactive element is a `Pressable` with a role; a mutation goes
   through a command*. Fix: `Pressable` with `accessibilityRole="button"`,
   `onPress={() => void archive(item.id)}`.
4. `onLink:30` — the deep link is split on `id=` with no host allowlist, no
   type/size validation, and an unknown URL still navigates. Rule: *a deep
   link is untrusted; parse it against the route table*. Fix: `parseRoute`
   returns `Route | undefined`; unknown → not-found.
5. `OrdersScreen.tsx:26` — an `Image` without dimensions or a memory budget,
   inside a `FlatList` that does not recycle. Rule: *lists and images have a
   per-tier budget*. Fix: FlashList + expo-image with dimensions and a
   placeholder.

### Should fix

6. `OrdersScreen.tsx:10` — no offline state and no last-good data; a network
   loss clears the list. Fix: the query cache is the last-good data; offline
   is a state.
7. `OrdersScreen.tsx:20` — the archive mutation is optimistic with no
   rollback and no idempotency key. Fix: the outbox pattern (write + queue +
   reconcile + visible rejection).
8. `sdk` — the token is read in the screen in the full version; it must come
   from the keystore behind the SDK, never the View. Fix: `SecretStore` port.

### Waived gates

None. The diff does not touch the lint config, the tests, or the device
budgets.

## The fixed module

```tsx
// src/features/orders/viewmodels/useOrders.ts
export function useOrders(): {
  state: OrdersState;
  refresh: () => Promise<void>;
  archive: (id: string) => Promise<void>;
} {
  const query = useQuery({
    queryKey: ["orders", tenantId],
    queryFn: ({ signal }) => sdk.app.orders.list({ signal }),
  });
  return {
    state: toState(query),
    refresh: query.refetch,
    archive: (id) => archiveOrder(id),
  };
}
```

```tsx
// src/features/orders/views/OrdersScreen.tsx
export function OrdersScreen(): React.ReactElement {
  const { state, refresh, archive } = useOrders();
  switch (state.status) {
    case "loading":
      return <Text>Loading…</Text>;
    case "empty":
      return <Text>No orders yet.</Text>;
    case "offline":
      return <Text>You are offline. Pull to retry.</Text>;
    case "forbidden":
      return <Text>You do not have permission to view orders.</Text>;
    case "error":
      return <Pressable accessibilityRole="button" onPress={() => void refresh()}><Text>Retry</Text></Pressable>;
    case "ready":
      return (
        <FlashList
          data={state.data}
          estimatedItemSize={72}
          renderItem={({ item }) => (
            <Pressable accessibilityRole="button" onPress={() => void archive(item.id)}>
              <Text>{item.id}</Text>
              <Image source={{ uri: item.image }} style={{ width: 64, height: 64 }} />
            </Pressable>
          )}
        />
      );
  }
}
```

```tsx
// src/features/orders/routes/parse.ts — the one parser for links and pushes.
export function parseRoute(url: string): Route | undefined {
  const parsed = new URL(url);
  if (!ALLOWED_HOSTS.has(parsed.host)) return undefined;
  if (parsed.pathname === "/orders") return { name: "orders" };
  if (parsed.pathname === "/orders/detail") {
    const id = parsed.searchParams.get("id");
    return id && ID_RE.test(id) ? { name: "orderDetail", id } : undefined;
  }
  return undefined;
}
```

## What changed, and why it matters

| Finding | The fixed version |
|---|---|
| View imports/calls the SDK | `useOrders()` owns the query and commands |
| Loading boolean, no other states | one union, five states rendered |
| `View` with `onClick` | `Pressable` with `accessibilityRole` |
| Unvalidated deep link | host + route + parameter validation |
| FlatList + unbounded image | FlashList + expo-image with dimensions |
| Optimistic archive, no rollback | the outbox with idempotency + visible rejection |

The review is short on purpose. Five Must-fix findings, each with a location,
a rule, and a fix, is a better review than twenty comments that repeat the
same contract in different words.
