# Graph Report - .  (2026-11-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 918 nodes · 1230 edges · 124 communities (76 shown, 48 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `32ed81f6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- _support.py
- write
- Beautiful React Native
- Path
- check-examples.py
- interface
- test_checker_failure_paths.py
- What You Must Do When Invoked
- YamlParser
- GateScript
- React Native best practices
- 2. Categories, in ranking order
- package.json
- compilerOptions
- workflow_text
- React Native platform digest
- React Native patterns
- BestPractices
- A worked review: the orders screen
- graphify reference: extra exports and benchmark
- TypeScript strict for React Native
- React Native port
- _load
- CiJobs
- `<app>` Mobile Performance Reviewer
- `<app>` Mobile Platform Reviewer
- `<app>` React Native Reviewer
- `<app>` Architect
- `<app>` Build Resolver
- `<app>` Code Explorer
- `<app>` Code Reviewer
- `<app>` Planner
- `<app>` TDD Guide
- `<app>` Mobile Security Reviewer
- `<app>` Test Author
- `<app>` add-port skill
- `<app>` add-route skill
- `<app>` add-screen skill
- `<app>` add-slice skill
- <app> Claim Check skill
- <app> Clean-Room Rebuild skill
- <app> Corpus Retrieval skill
- <app> Diagnosing Bugs skill
- <app> Domain Modeling skill
- <app> Grilling skill
- `<app>` learn skill
- `<app>` plan skill
- <app> Research skill
- `<app>` review skill
- `<app>` ship skill
- `<app>` spec skill
- <app> TDD skill
- <app> Verified Status skill
- <app> Visual Review skill
- graphify reference: query, path, explain
- build
- hooks.ts
- beautifulreactnative — agent instructions
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- consistent-type-imports.ts
- check-lints.sh
- guard-bash.sh
- /add-port
- /add-route
- /add-screen
- /add-slice
- /claim-check
- /clean-room-rebuild
- /corpus-retrieval
- /diagnosing-bugs
- /domain-modeling
- /grilling
- /learn
- /plan
- /research
- /review
- /ship
- /spec
- /tdd
- /verified-status
- /visual-review
- Playbooks for `beautifulreactnative` — load on demand
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- bad-platform.ts
- bad-sdk.ts
- bad-session.ts
- switch-exhaustiveness.ts
- CLAUDE.md
- README.md
- CREDITS.md
- CREDITS.md
- CREDITS.md
- CREDITS.md
- CREDITS.md
- extraction-spec.md
- CREDITS.md
- CREDITS.md
- CREDITS.md
- CREDITS.md
- CREDITS.md
- eval.ts
- new-func.ts
- no-unnecessary-type-assertion.ts
- second
- os
- client
- captured

## God Nodes (most connected - your core abstractions)
1. `write()` - 35 edges
2. `CheckSkillTests` - 35 edges
3. `build_valid_repo()` - 32 edges
4. `Checker` - 26 edges
5. `check_repo()` - 17 edges
6. `React Native best practices` - 17 edges
7. `YamlParser` - 16 edges
8. `Beautiful React Native` - 15 edges
9. `interface` - 14 edges
10. `What You Must Do When Invoked` - 12 edges

## Surprising Connections (you probably didn't know these)
- `add_portable_plugin()` --calls--> `write()`  [EXTRACTED]
  tests/unit/test_check_skill_unit.py → tests/_support.py
- `build_valid_repo()` --calls--> `write()`  [EXTRACTED]
  tests/unit/test_check_skill_unit.py → tests/_support.py

## Import Cycles
- None detected.

## Communities (124 total, 48 thin omitted)

### Community 0 - "_support.py"
Cohesion: 0.05
Nodes (19): ledger_data(), ledger_paths(), ledger_skip_count(), LedgerAgrees, LedgerShape, path -> the file entry, only for entries that are objects., Count of block specs that ledger a skip (the checker must match it)., The checker's skipped count must equal the ledger's skip count. (+11 more)

### Community 1 - "write"
Cohesion: 0.14
Nodes (11): write(), DomainWallTest, EndToEndTest, add_portable_plugin(), build_valid_repo(), CheckSkillTests, error_messages(), formatted() (+3 more)

### Community 2 - "Beautiful React Native"
Cohesion: 0.04
Nodes (41): Added, Changelog, [Unreleased], Contributing, Good first contributions, License, Making a change, Style (+33 more)

### Community 3 - "Path"
Cohesion: 0.16
Nodes (17): check_repo(), Checker, _fold_block(), format_problem(), _is_relative(), _json_key_line(), main(), _normalize_url() (+9 more)

### Community 4 - "check-examples.py"
Cohesion: 0.13
Nodes (33): apply_harness(), as_text(), Block, build_project(), check_brackets(), check_quotes(), check_repo(), doc_files() (+25 more)

### Community 5 - "interface"
Cohesion: 0.07
Nodes (29): author, name, url, interface, publication, description, extensions, com.openai (+21 more)

### Community 6 - "test_checker_failure_paths.py"
Cohesion: 0.10
Nodes (15): BrokenTsBlock, CopiedRepoFailures, DeletedLints, GuardedRepoCase, has_eslint(), A broken ```ts block in a bare doc tree fails check-examples., Failure paths that mutate a full copy of the repo., Text surgery on a copy's lints: removing a pinned rule from BOTH the     drop-in (+7 more)

### Community 7 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 8 - "YamlParser"
Cohesion: 0.25
Nodes (8): Exception, _parse_quoted(), parse_yaml(), Any, Small YAML subset: maps, lists, quoted scalars, | and > blocks., _split_flow(), YamlError, YamlParser

### Community 9 - "GateScript"
Cohesion: 0.12
Nodes (7): ConfigPairing, explicit_rules(), GateScript, HarnessCoverage, marker_names(), The shell contract: bounded runs, surfaced stderr, explicit non-JSON., Rule ids configured at the top level of any rules block in the config.

### Community 10 - "React Native best practices"
Cohesion: 0.11
Nodes (17): 10. Storage and secrets, 11. Security, 12. Accessibility and i18n, 13. Performance, 14. Testing, 15. Cross-skill contract, 1. Mindset, 2. Before you hand back code (+9 more)

### Community 11 - "2. Categories, in ranking order"
Cohesion: 0.12
Nodes (15): 1. Report shape, 2. Categories, in ranking order, 3. Waived gates, 4. How to review, 5. Worked example, 6. Cross-skill contract, Accessibility and i18n, Architecture contracts (always Must fix, ranked first) (+7 more)

### Community 12 - "package.json"
Cohesion: 0.13
Nodes (14): description, devDependencies, eslint, @eslint-community/eslint-plugin-eslint-comments, @eslint/js, eslint-plugin-react-hooks, typescript, typescript-eslint (+6 more)

### Community 13 - "compilerOptions"
Cohesion: 0.13
Nodes (14): compilerOptions, baseUrl, lib, module, moduleResolution, noEmit, noUncheckedIndexedAccess, paths (+6 more)

### Community 14 - "workflow_text"
Cohesion: 0.22
Nodes (5): CheckerSteps, Every existing CI job keeps its exact entrypoint and pin., The unittest gate: the full discovery is the CI job itself., TestsJob, workflow_text()

### Community 15 - "React Native platform digest"
Cohesion: 0.17
Nodes (11): 10. Testing, 1. Runtime, 2. Device tiers, 3. Lists and images, 4. Storage, 5. Push, 6. Navigation and deep links, 7. Offline and background (+3 more)

### Community 16 - "React Native patterns"
Cohesion: 0.17
Nodes (11): 10. Performance patterns, 1. The ViewModel hook, 2. The five states, 3. Query keys, 4. The outbox, 5. The deep-link parser, 6. The quality governor, 7. The SceneEngine port (+3 more)

### Community 17 - "BestPractices"
Cohesion: 0.29
Nodes (4): BestPractices, bp_body(), ReviewSkill, rv_body()

### Community 18 - "A worked review: the orders screen"
Cohesion: 0.20
Nodes (9): A worked review: the orders screen, Must fix, Should fix, The fixed module, The module under review, The report, Verdict, Waived gates (+1 more)

### Community 19 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 20 - "TypeScript strict for React Native"
Cohesion: 0.22
Nodes (8): 1. The strict set, 2. Screen states, 3. Branded ids, 4. Result types, 5. Boundary types, 6. Async discipline, 7. Type-level review questions, TypeScript strict for React Native

### Community 21 - "React Native port"
Cohesion: 0.22
Nodes (8): 1. The order of work, 2. Web React → React Native mapping, 3. Bare RN → Expo + New Architecture, 4. Native screen (Android/iOS) → React Native, 5. Behavior parity checklist, 6. What not to do, 7. Cross-skill contract, React Native port

### Community 22 - "_load"
Cohesion: 0.36
Nodes (4): _load(), ManifestPairing, Path, skill_dirs()

### Community 24 - "`<app>` Mobile Performance Reviewer"
Cohesion: 0.29
Nodes (6): `<app>` Mobile Performance Reviewer, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 25 - "`<app>` Mobile Platform Reviewer"
Cohesion: 0.29
Nodes (6): `<app>` Mobile Platform Reviewer, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 26 - "`<app>` React Native Reviewer"
Cohesion: 0.29
Nodes (6): `<app>` React Native Reviewer, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 27 - "`<app>` Architect"
Cohesion: 0.29
Nodes (6): `<app>` Architect, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 28 - "`<app>` Build Resolver"
Cohesion: 0.29
Nodes (6): `<app>` Build Resolver, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 29 - "`<app>` Code Explorer"
Cohesion: 0.29
Nodes (6): `<app>` Code Explorer, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 30 - "`<app>` Code Reviewer"
Cohesion: 0.29
Nodes (6): `<app>` Code Reviewer, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 31 - "`<app>` Planner"
Cohesion: 0.29
Nodes (6): `<app>` Planner, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 32 - "`<app>` TDD Guide"
Cohesion: 0.29
Nodes (6): `<app>` TDD Guide, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 33 - "`<app>` Mobile Security Reviewer"
Cohesion: 0.29
Nodes (6): `<app>` Mobile Security Reviewer, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 34 - "`<app>` Test Author"
Cohesion: 0.29
Nodes (6): `<app>` Test Author, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 35 - "`<app>` add-port skill"
Cohesion: 0.29
Nodes (6): `<app>` add-port skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 36 - "`<app>` add-route skill"
Cohesion: 0.29
Nodes (6): `<app>` add-route skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 37 - "`<app>` add-screen skill"
Cohesion: 0.29
Nodes (6): `<app>` add-screen skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 38 - "`<app>` add-slice skill"
Cohesion: 0.29
Nodes (6): `<app>` add-slice skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 39 - "<app> Claim Check skill"
Cohesion: 0.29
Nodes (6): <app> Claim Check skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 40 - "<app> Clean-Room Rebuild skill"
Cohesion: 0.29
Nodes (6): <app> Clean-Room Rebuild skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 41 - "<app> Corpus Retrieval skill"
Cohesion: 0.29
Nodes (6): <app> Corpus Retrieval skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 42 - "<app> Diagnosing Bugs skill"
Cohesion: 0.29
Nodes (6): <app> Diagnosing Bugs skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 43 - "<app> Domain Modeling skill"
Cohesion: 0.29
Nodes (6): <app> Domain Modeling skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 44 - "<app> Grilling skill"
Cohesion: 0.29
Nodes (6): <app> Grilling skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 45 - "`<app>` learn skill"
Cohesion: 0.29
Nodes (6): `<app>` learn skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 46 - "`<app>` plan skill"
Cohesion: 0.29
Nodes (6): `<app>` plan skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 47 - "<app> Research skill"
Cohesion: 0.29
Nodes (6): <app> Research skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 48 - "`<app>` review skill"
Cohesion: 0.29
Nodes (6): `<app>` review skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 49 - "`<app>` ship skill"
Cohesion: 0.29
Nodes (6): `<app>` ship skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 50 - "`<app>` spec skill"
Cohesion: 0.29
Nodes (6): `<app>` spec skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 51 - "<app> TDD skill"
Cohesion: 0.29
Nodes (6): <app> TDD skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 52 - "<app> Verified Status skill"
Cohesion: 0.29
Nodes (6): <app> Verified Status skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 53 - "<app> Visual Review skill"
Cohesion: 0.29
Nodes (6): <app> Visual Review skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 54 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 55 - "build"
Cohesion: 0.53
Nodes (5): build(), main(), package_files(), Path, Files to package, relative to root, in a stable order.

### Community 56 - "hooks.ts"
Cohesion: 0.70
Nodes (4): Conditional(), Deps(), useEffect(), useState()

### Community 57 - "beautifulreactnative — agent instructions"
Cohesion: 0.50
Nodes (3): beautifulreactnative — agent instructions, graphify, Model routing (Claude Code + Ollama)

### Community 58 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 59 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 60 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 62 - "check-lints.sh"
Cohesion: 0.83
Nodes (3): bounded(), fail(), check-lints.sh script

### Community 63 - "guard-bash.sh"
Cohesion: 0.83
Nodes (3): has(), has_i(), guard-bash.sh script

## Knowledge Gaps
- **387 isolated node(s):** `name`, `version`, `private`, `type`, `description` (+382 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `write()` connect `write` to `_support.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `render()` connect `check-examples.py` to `Path`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Why does `load_script()` connect `_support.py` to `write`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **What connects `name`, `version`, `private` to the rest of the system?**
  _417 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `_support.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05222734254992319 - nodes in this community are weakly interconnected._
- **Should `write` be split into smaller, more focused modules?**
  _Cohesion score 0.13574660633484162 - nodes in this community are weakly interconnected._
- **Should `Beautiful React Native` be split into smaller, more focused modules?**
  _Cohesion score 0.041666666666666664 - nodes in this community are weakly interconnected._