# Beautiful React Native lints

The two-file unit that turns the reactnative-best-practices skill into
red-on-save output:

- `eslint.config.mjs` — the drop-in. Paste it next to your `package.json`; it
  makes eslint enforce the machine-checkable rules from the skill: the layer
  walls (the View never imports the SDK; the ViewModel never imports
  `react-native`/`react-dom`/views; the SDK never imports React or React
  Native), hooks rules (`rules-of-hooks`, `exhaustive-deps`), the
  no-remote-code rule, promise discipline and the silencing requirements.
  Everything else rides the typescript-eslint `strictTypeChecked` +
  `stylisticTypeChecked` presets. Adjust the layer globs when your project
  renames its folders, never the rule.
- `check/` — the violation harness that proves every pinned rule fires:
  `src/` holds one file per rule family, each violating line carrying a
  `// expect:<rule>` comment on the line above it. `clean.ts` carries no
  markers and must stay fully quiet.

The harness files are layer-shaped on purpose (`src/features/orders/views/`,
`src/features/orders/viewmodels/`, `src/sdk/`): the `no-restricted-imports`
overrides key on those file globs, so the violations must sit in files the
drop-in actually targets. `scripts/check-lints.sh` fails if a marked rule
stays quiet, if anything unmarked fires, or if `tsc --noEmit` fails on the
same files — every eslint/tsc invocation is bounded by a timeout, stderr is
always surfaced, and a non-JSON eslint report is an explicit error, never a
guess.

To wire it in CI:

```bash
npx eslint .
bash scripts/check-lints.sh   # only in the BeautifulReactNative repo itself
```

Add the repo as a dependency of nothing — it is a copy-in config. Keep the
check project's `eslint.config.mjs` byte-identical to the drop-in; the lints
gate, `scripts/check-lints.sh` and
`tests/contracts/test_lints_contract.py` all enforce it.
