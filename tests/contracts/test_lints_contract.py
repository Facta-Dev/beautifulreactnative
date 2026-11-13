#!/usr/bin/env python3
"""Contract tests: the drop-in lints ship as a three-part unit that must stay
paired — lints/eslint.config.mjs (the config agents copy), its byte-identical
replica in lints/check/, and the violation harness under lints/check/src whose
// expect: markers prove every pinned rule fires. Read-only on the real repo.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from tests._support import REPO_ROOT

DROP_IN = REPO_ROOT / "lints" / "eslint.config.mjs"
REPLICA = REPO_ROOT / "lints" / "check" / "eslint.config.mjs"
CHECK = REPO_ROOT / "lints" / "check"
GATE = REPO_ROOT / "scripts" / "check-lints.sh"
MARKER_RE = re.compile(r"^// expect:([\w@./-]+(?:\s*,\s*[\w@./-]+)*)\s*$")

# The rules the config pins on top of the typescript-eslint presets. Preset
# rules stay enforced too, but they arrive with the preset (the counterpart of
# beautifulrust's clippy `all`/`pedantic` groups) and take no markers.
EXPLICIT_RULES = frozenset({
    "no-console",
    "no-restricted-imports",
    "no-eval",
    "no-new-func",
    "@typescript-eslint/no-implied-eval",
    "@typescript-eslint/ban-ts-comment",
    "@typescript-eslint/no-floating-promises",
    "@typescript-eslint/no-misused-promises",
    "@typescript-eslint/switch-exhaustiveness-check",
    "@typescript-eslint/consistent-type-imports",
    "@typescript-eslint/explicit-module-boundary-types",
    "@typescript-eslint/no-unnecessary-type-assertion",
    "@eslint-community/eslint-comments/no-unlimited-disable",
    "@eslint-community/eslint-comments/require-description",
    "react-hooks/rules-of-hooks",
    "react-hooks/exhaustive-deps",
})


def marker_names() -> set:
    names = set()
    for pattern in ("*.ts", "*.tsx"):
        for path in sorted((CHECK / "src").rglob(pattern)):
            for line in path.read_text(encoding="utf-8").splitlines():
                match = MARKER_RE.match(line.strip())
                if match:
                    names.update(rule.strip() for rule in match.group(1).split(","))
    return names


def explicit_rules(config_text: str) -> set:
    """Rule ids configured at the top level of any rules block in the config."""
    rules = set()
    depth = 0
    in_rules = False
    rules_depth = None
    for line in config_text.splitlines():
        stripped = line.strip()
        opens, closes = stripped.count("{"), stripped.count("}")
        if not in_rules and re.match(r"^rules:\s*\{", stripped):
            in_rules, rules_depth = True, depth + 1
        if in_rules and rules_depth is not None and depth == rules_depth:
            match = re.match(r'^"([^"\s:]+)":', stripped)
            if match:
                rules.add(match.group(1))
        depth += opens - closes
        if in_rules and rules_depth is not None and depth < rules_depth:
            in_rules, rules_depth = False, None
    return rules


class ConfigPairing(unittest.TestCase):
    def test_replica_is_byte_identical_to_the_drop_in(self):
        self.assertEqual(
            DROP_IN.read_bytes(),
            REPLICA.read_bytes(),
            "lints/check/eslint.config.mjs must stay byte-identical to lints/eslint.config.mjs",
        )

    def test_pinned_rules_are_exactly_the_explicit_config(self):
        self.assertEqual(
            explicit_rules(DROP_IN.read_text(encoding="utf-8")),
            EXPLICIT_RULES,
            "the config's hand-pinned rule set drifted from the contract",
        )


class HarnessCoverage(unittest.TestCase):
    def test_markers_are_all_pinned_rules(self):
        extra = marker_names() - EXPLICIT_RULES
        self.assertEqual(extra, set(), "// expect: markers for unpinned rules: %s" % sorted(extra))

    def test_every_pinned_rule_has_a_marker(self):
        missing = EXPLICIT_RULES - marker_names()
        self.assertEqual(missing, set(), "pinned rules without a // expect: marker: %s" % sorted(missing))

    def test_silencing_rules_are_pinned(self):
        self.assertLessEqual({
            "@typescript-eslint/ban-ts-comment",
            "@eslint-community/eslint-comments/no-unlimited-disable",
            "@eslint-community/eslint-comments/require-description",
        }, EXPLICIT_RULES)

    def test_the_io_wall_is_among_the_pinned_rules(self):
        self.assertIn("no-restricted-imports", EXPLICIT_RULES)


class GateScript(unittest.TestCase):
    """The shell contract: bounded runs, surfaced stderr, explicit non-JSON."""

    def setUp(self):
        self.text = GATE.read_text(encoding="utf-8")

    def test_gate_exists_with_markers_and_identity(self):
        self.assertIn("cmp -s", self.text, "the gate must prove byte-identity")
        self.assertIn("expect:", self.text)

    def test_every_tool_run_is_bounded_by_a_timeout(self):
        # `bounded <seconds>` wraps tsc/eslint; npm ci uses timeout directly.
        self.assertIn("timeout \"$seconds\" \"$@\"", self.text)
        self.assertIn("bounded 240", self.text)
        self.assertIn("timeout 600", self.text)

    def test_stderr_is_surfaced(self):
        self.assertGreaterEqual(self.text.count(">&2"), 5)

    def test_a_non_json_report_is_an_explicit_error(self):
        self.assertIn("non-JSON report from eslint", self.text)


if __name__ == "__main__":
    unittest.main()