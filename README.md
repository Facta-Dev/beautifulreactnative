<p align="center">
  <img src="assets/icon.png" alt="Beautiful React Native: a phone with a React atom" width="160">
</p>

# Beautiful React Native

Three standard [Agent Skills](https://agentskills.io) and a lints config that
teach coding agents to write, review, port, and enforce idiomatic
**React Native + Expo** apps on TypeScript:

- **`reactnative-best-practices`** loads whenever an agent writes or changes a
  mobile app, and steers it toward the View → ViewModel → SDK contract, the
  five screen states, device tiers and a safe offline path.
- **`reactnative-review`** reviews existing code — a screen, ViewModel,
  deep-link parser, offline path, push handler, or diff — and writes a
  prioritized report where every finding cites the rule it breaks and shows
  the fix.
- **`reactnative-port`** ports a web React app, a bare RN app, or a legacy
  screen to Expo + the New Architecture with the same behavior, porting the
  original tests first.
- **`lints/`** is a drop-in ESLint 9 flat config whose layer walls and
  no-remote-code rules run in CI.

They work with Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI,
and any other agent that reads the Agent Skills format.

## Why

Mobile failures are usually the same few contracts:

- A screen calls the SDK, so the offline, forbidden and error states never
  exist.
- A flagships-only feature ships with no low-end fallback.
- A deep link or push payload navigates without validation, or performs an
  action.
- A token lands in AsyncStorage/MMKV instead of the OS keystore.
- A mutation is optimistic with no rollback, and the outbox is lost on
  restart.
- A list or image budget is fine on a flagship and fatal on the phones most
  people own.

Beautiful React Native is the contract that catches those before review.

## Install

### Claude Code

```bash
/plugin marketplace add Facta-Dev/beautifulreactnative
/plugin install beautiful-reactnative@beautiful-reactnative
```

### OpenAI Codex and ChatGPT

The repository ships a portable `plugin.json` with the `com.openai` interface
block. Point Codex at the repository, or package it with:

```bash
python3 scripts/package-openai-plugin.py --out beautiful-reactnative.zip
```

### Any agent

Copy `skills/reactnative-best-practices`, `skills/reactnative-review`, and
`skills/reactnative-port` into your agent's skills directory. Each skill is a
`SKILL.md` plus a `references/` digest; no runtime, no network.

## A worked example

Without the skill, an agent writes a screen that works on a flagship dev
build:

```tsx
// Without the skill: fetch in the screen, two booleans, no offline state.
export function OrdersScreen() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetch("/api/v1/app/orders")
      .then((r) => r.json())
      .then((data) => { setOrders(data); setLoading(false); });
  }, []);
  if (loading) return <Text>Loading...</Text>;
  return <FlatList data={orders} renderItem={({ item }) => <Text>{item.id}</Text>} />;
}
```

Problems: the screen talks to the network, loading is a boolean with no
error/offline/empty state, the list is not virtualized with recycling, and a
network loss shows a blank screen.

With the skill, the screen renders one state and calls one ViewModel:

```tsx
// With the skill: ViewModel state, five states, recycled list.
export function OrdersScreen(): React.ReactElement {
  const { state, refresh } = useOrders();
  switch (state.status) {
    case "loading": return <Text>Loading…</Text>;
    case "empty": return <Text>No orders yet.</Text>;
    case "offline": return <Text>You are offline. Pull to retry.</Text>;
    case "forbidden": return <Text>You do not have permission to view orders.</Text>;
    case "error": return <Pressable accessibilityRole="button" onPress={() => void refresh()}><Text>Retry</Text></Pressable>;
    case "ready": return <FlashList data={state.data} renderItem={renderOrder} estimatedItemSize={72} />;
  }
}
```

The ViewModel owns the query, the states and the retry; the View renders and
forwards. The layer contract is in
[`skills/reactnative-best-practices/references/mobile-architecture.md`](skills/reactnative-best-practices/references/mobile-architecture.md).

## The architecture contract

```text
View (screens)  ──►  ViewModel hook  ──►  SDK  ──►  API
     ▲                  │                  │
     └── state/events ──┘                  └── ports: TokenStore, Transport, Clock
                        └── ports: Navigator, Notifier, Permissions
```

| Layer | Owns | Must not import |
|---|---|---|
| **View** | Native components, navigation, a11y, event forwarding | the SDK, `fetch`, tokens |
| **ViewModel** | Presentation state, commands, derived values | `react-native`, `react-dom`, views |
| **SDK** | Typed HTTP client, DTOs, error normalization | React, React Native |
| **Ports** | Platform capabilities behind an interface | platform APIs |

The unbreakable rules:

1. The View never talks to the network.
2. The ViewModel is platform-free.
3. The SDK never imports React or React Native.
4. Every screen renders every state, including offline.
5. Authorization is server-side.

## The lints config

[`lints/eslint.config.mjs`](lints/eslint.config.mjs) is a copy-in ESLint 9
flat config. It pins:

- **Layer walls:** `no-restricted-imports` for views, viewmodels and the SDK.
- **Hooks:** `react-hooks/rules-of-hooks`, `react-hooks/exhaustive-deps`.
- **No remote code:** `no-eval`, `no-new-func`, `no-implied-eval`.
- **Type discipline:** `ban-ts-comment`, `consistent-type-imports`,
  `explicit-module-boundary-types`, `no-unnecessary-type-assertion`,
  `switch-exhaustiveness-check`.
- **Async discipline:** `no-floating-promises`, `no-misused-promises`.
- **Silencing:** eslint-comments requires a description and rejects an
  unlimited disable.
- **One logger:** `no-console`.

[`lints/check/`](lints/README.md) is the violation harness: one deliberate
file per rule with a `// expect:<rule>` marker, plus a clean control.
[`scripts/check-lints.sh`](scripts/check-lints.sh) fails if a marked rule stays
quiet, if anything unmarked fires, or if `tsc --noEmit` fails on the same
files.

## What it does not do

- The skills contain instructions and reference text only. They make no
  network calls and collect no data ([PRIVACY.md](PRIVACY.md)).
- When a Node.js toolchain is available, the skills run `tsc`, `eslint`, and
  `vitest` on your project; without one, they work from the code alone.
- The lint config is a copy-in unit, not a dependency.
- The skills do not replace a device lab or a store review; they tell the
  agent what those must prove.

## Repository layout

```text
skills/
  reactnative-best-practices/  SKILL.md + references/ (platform, patterns,
                               architecture, strict TypeScript)
  reactnative-review/          SKILL.md (report format, ranking, waived gates)
  reactnative-port/            SKILL.md (web/bare RN/native → Expo RN)
lints/
  eslint.config.mjs            the drop-in
  check/                       the violation harness + byte-identical config
scripts/
  check-skill.py               frontmatter, links, evals, manifests
  check-lints.sh               every pinned rule fires
  check-examples.py            TypeScript blocks compile
  examples.json                the ledger of deliberately skipped blocks
  package-openai-plugin.py
tests/                         unit, contracts, integration, e2e
examples/
  review-mobile-screen.md      a full worked review
```

## Sources

- The React Native and Expo documentation (New Architecture, Hermes, lists,
  images, notifications, EAS).
- The facta mobile handbook (`PLAYBOOK_FRONTEND_MOBILE.md`): device tiers, the
  quality governor, offline/outbox, push, navigation, scene engines.
- The mobile performance guidance: JS-thread discipline, memory budgets, the
  low-end path.

## Contributing

Rule proposals are welcome; open an issue with the
[rule template](.github/ISSUE_TEMPLATE/propose-a-rule.yml) and a source. A
rule without a source and a failing example is a preference, not a rule. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## Siblings

Beautiful React Native is part of the Beautiful series for the facta
playbooks: [beautiful-j2ee](https://github.com/Facta-Dev/beautiful-j2ee),
[beautifulandroid](https://github.com/Facta-Dev/beautifulandroid),
[beautifulcli](https://github.com/Facta-Dev/beautifulcli),
[beautifulextension](https://github.com/Facta-Dev/beautifulextension),
[beautifulgo](https://github.com/Facta-Dev/beautifulgo),
[beautifulios](https://github.com/Facta-Dev/beautifulios),
[beautifulnodejs](https://github.com/Facta-Dev/beautifulnodejs),
[beautifulpython](https://github.com/Facta-Dev/beautifulpython),
[beautifulqt](https://github.com/Facta-Dev/beautifulqt),
[beautifulreact](https://github.com/Facta-Dev/beautifulreact),
[beautifulrust](https://github.com/Facta-Dev/beautifulrust).

## License

MIT — see [LICENSE](LICENSE).
