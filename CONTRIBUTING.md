# Contributing

Thanks for helping make BeautifulReactNative better. Issues and pull requests
are welcome. A few conventions keep the skills consistent and trustworthy.

## The one rule: every rule needs a source

The skills are a synthesis of published React Native, Expo, TypeScript and
mobile-performance guidance, not a list of opinions. Each rule you add or
change should trace back to one of the sources in the README — the React
Native and Expo documentation, the facta mobile handbook, or the mobile
performance guidance — or to another source of similar weight, such as the
Expo SDK docs, the React Native release notes, the typescript-eslint rule docs,
or the platform accessibility guidance. Link it in your pull request. If the
sources disagree, say which one you followed and why.

## Good first contributions

- **A rule the skills get wrong or miss.** Open a "Propose a rule" issue with
  the source, a short example of code the agent writes today, and what it
  should write instead.
- **A review false positive.** If `reactnative-review` flags something that's
  actually fine, open a "Review false positive" issue with the code and the
  finding. These become new eval cases.
- **A new eval case.** A realistic prompt, the input files it needs, and one
  assertion per file. Open an issue and a maintainer will scaffold the case
  with you.
- **A broken install path.** Agents move their skill directories. If an
  install step in the README stopped working, a fix with a link to the agent's
  current docs is very welcome.

## Making a change

1. **Edit the skill.** Each skill is `skills/<name>/SKILL.md`. Keep it under
   about 500 lines; longer material belongs in `references/`. Explain why a
   rule matters, not just what it is.
2. **Compile your examples.** Every `ts` code block in the skills and the
   README must compile under strict `tsc`. Run
   `python3 scripts/check-examples.py`; CI runs it with `--require-toolchain`.
   Most examples are fragments, so `scripts/examples.json` gives each one the
   code around it that it needs. If you add, move, or change the first line of
   a block, update its entry there. A block that needs a platform API or JSX
   uses a `tsx` fence and is review-checked rather than compiled.
3. **Check lint changes.** If you touch `lints/`, every rule entry must keep a
   deliberate violation in `lints/check/` marked with a
   `// expect:<rule-id>` comment, and `bash scripts/check-lints.sh` must still
   pass. Confirm the rule fires and that the clean file stays clean.
4. **Keep the wording contracts green.**
   `tests/contracts/test_skill_wording.py` pins the canonical phrases (the
   unbreakable clause, the silencing-token listings, the review priority
   headings, and the `reactnative-review` cross-reference). If your change
   touches that wording, updating the skill also means updating the test in
   the same PR.
5. **Run the evals if you changed behavior.** These are real model runs and
   are billed, so a maintainer can run them for you if you'd rather not. Say in
   the pull request whether you ran them.
6. **Validate the plugin** with `claude plugin validate .` from the repo root.
7. **Add a line to the Unreleased section of [CHANGELOG.md](CHANGELOG.md).**

## Style

- Write for an agent reading it mid-task: direct, imperative, one idea per
  bullet.
- Prefer a short code example to a paragraph of description.
- No Claude-specific instructions in the skills. They are standard Agent
  Skills and should work in any agent.

## License

By contributing, you agree your contribution is licensed under the MIT
license in [LICENSE](LICENSE).
