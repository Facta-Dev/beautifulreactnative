# Changelog

All notable changes to this project are listed here. Versions follow
[Semantic Versioning](https://semver.org/), and the version lives in
`.claude-plugin/plugin.json`.

## [Unreleased]

### Added

- **Three skills for React Native + Expo.** `reactnative-best-practices`
  steers new mobile code toward the View → ViewModel → SDK contract, the five
  screen states, TanStack Query and the outbox, deep-link and push parsing,
  device tiers and the quality governor, recycled lists and memory-safe
  images, the tiered `SceneEngine` port, secure storage, accessibility and
  the unbreakable layer contract. `reactnative-review` reviews a screen,
  ViewModel, parser, offline path, push handler, or diff and ranks
  architecture and device tiers first. `reactnative-port` ports a web React
  app, a bare RN app, or a native screen to Expo + the New Architecture.
- **A drop-in ESLint config.** `lints/eslint.config.mjs` (ESLint 9 flat
  config + typescript-eslint 8, strictTypeChecked) turns the layer contract
  into red-on-save output: `no-restricted-imports` keeps the View off the SDK
  and the ViewModel off the platform; hooks rules, promise discipline and the
  silencing requirements are pinned as errors.
- **Proof that every rule fires.** `lints/check/` holds one deliberate
  violation per rule plus a clean file, and `scripts/check-lints.sh` runs
  eslint and tsc over both, bounded and with stderr surfaced.
- **A skill validator, an example compiler, and a test suite.**
  `scripts/check-skill.py` checks frontmatter, links, eval cases and the
  plugin manifests; `scripts/check-examples.py` compiles every `ts` block;
  `tests/` covers the unit, contract, integration and CI-gate layers.
- **A worked review.** `examples/review-mobile-screen.md` shows the report
  shape and the architecture-first ranking on a small orders screen.

[Unreleased]: https://github.com/Facta-Dev/beautifulreactnative/compare/v0.1.0...HEAD
