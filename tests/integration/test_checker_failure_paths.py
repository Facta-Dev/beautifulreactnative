#!/usr/bin/env python3
"""Failure-path tests for the checkers: mutate a COPY of the repo, never the
real one, and prove each hardened guard fires. Each test copies the repo with
shutil.copytree; a sha256 snapshot of the real gate files self-reports in
tearDown if any test mutated the real repo.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._support import REPO_ROOT

GUARDED = (
    "lints/eslint.config.mjs",
    "lints/check/eslint.config.mjs",
    ".github/workflows/check.yml",
    ".claude-plugin/plugin.json",
    "scripts/examples.json",
    "plugin.json",
)
COPY_IGNORE = shutil.ignore_patterns(
    ".git", "__pycache__", ".ruff_cache", ".pytest_cache",
    "dist", "target", "node_modules",
)
SUBPROCESS_TIMEOUT = 300


def _has_tsc():
    import importlib.util

    path = REPO_ROOT / "scripts" / "check-examples.py"
    spec = importlib.util.spec_from_file_location("bn_ce_probe", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.find_tsc() is not None


HAS_TSC = _has_tsc()
CHECK_DIR = REPO_ROOT / "lints" / "check"
_HAS_ESLINT = None


def has_eslint():
    """Probe once for a working eslint install inside lints/check."""
    global _HAS_ESLINT
    if _HAS_ESLINT is None:
        if shutil.which("npx") is None or not (CHECK_DIR / "node_modules").is_dir():
            _HAS_ESLINT = False
        else:
            probe = subprocess.run(
                ["npx", "--no-install", "eslint", "--version"],
                cwd=str(CHECK_DIR), capture_output=True, text=True,
            )
            _HAS_ESLINT = probe.returncode == 0
    return _HAS_ESLINT


def run_checker(argv, root_arg=None):
    """Run a python checker with python3 -I; return (returncode, combined output)."""
    args = ["python3", "-I"] + list(argv)
    if root_arg is not None:
        args.append(str(root_arg))
    proc = subprocess.run(
        args, cwd=str(REPO_ROOT), capture_output=True, text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )
    return proc.returncode, proc.stdout + proc.stderr


def run_bash(argv):
    """Run a repo shell script (its ROOT comes from its own path)."""
    proc = subprocess.run(
        list(argv), cwd=str(REPO_ROOT), capture_output=True, text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )
    return proc.returncode, proc.stdout + proc.stderr


class GuardedRepoCase(unittest.TestCase):
    """Snapshot the real gate files; copy the repo for mutation."""

    def setUp(self):
        self._snapshot = {rel: _sha256(REPO_ROOT / rel) for rel in GUARDED
                          if (REPO_ROOT / rel).is_file()}
        self.addCleanup(self._verify_real_repo_untouched)
        self.tmp = Path(tempfile.mkdtemp(prefix="bnfailpath."))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.copy = self.tmp / "repo"
        shutil.copytree(REPO_ROOT, self.copy, ignore=COPY_IGNORE)
        self.assertFalse((self.copy / ".git").exists(), "copy must not carry .git")

    def _verify_real_repo_untouched(self):
        mutated = [
            rel for rel, digest in self._snapshot.items()
            if not (REPO_ROOT / rel).is_file() or _sha256(REPO_ROOT / rel) != digest
        ]
        self.assertEqual(
            mutated, [],
            "TEST BUG: the real repo's gate files were mutated: %s" % mutated,
        )


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BrokenTsBlock(GuardedRepoCase):
    """A broken ```ts block in a bare doc tree fails check-examples."""

    @unittest.skipUnless(HAS_TSC, "tsc is not installed")
    def test_broken_ts_block_fails_check_examples(self):
        md = self.tmp / "README.md"
        md.write_text(
            "# Demo\n\n```ts\nexport function f(): number {\n  return let;\n}\n```\n",
            encoding="utf-8",
        )
        rc, out = run_checker(["scripts/check-examples.py"], root_arg=self.tmp)
        self.assertEqual(rc, 1)
        self.assertIn("README.md", out)

    def test_stack_import_wall_fails_without_a_toolchain(self):
        # The framework wall is enforced statically, so it holds even where
        # tsc is missing: the failing mode is the fallback, not a silent pass.
        md = self.tmp / "README.md"
        md.write_text(
            "# Demo\n\n```ts\nimport { useState } from \"react\";\nexport const h = useState;\n```\n",
            encoding="utf-8",
        )
        rc, out = run_checker(["scripts/check-examples.py"], root_arg=self.tmp)
        self.assertEqual(rc, 1, out)
        self.assertIn("framework-free", out)


class CopiedRepoFailures(GuardedRepoCase):
    """Failure paths that mutate a full copy of the repo."""

    def test_malformed_harness_list_is_reported_not_crashed(self):
        harness = self.copy / "scripts" / "examples.json"
        harness.write_text('{"files": ["oops"]}', encoding="utf-8")
        rc, out = run_checker(["scripts/check-examples.py"], root_arg=self.copy)
        self.assertEqual(rc, 1)
        self.assertIn("files must be a JSON object", out)

    @unittest.skipUnless(
        any((REPO_ROOT / "skills").glob("*/evals/*/place-files.sh")),
        "no eval place-files.sh exists yet",
    )
    def test_place_files_escape_is_rejected(self):
        script = sorted(self.copy.glob("skills/*/evals/*/place-files.sh"))[0]
        with script.open("a", encoding="utf-8") as fh:
            fh.write("\ncp files/../../outside.py .\n")
        rc, out = run_checker(["scripts/check-skill.py"], root_arg=self.copy)
        self.assertEqual(rc, 1)
        self.assertIn("escapes files/", out)

    @unittest.skipUnless((REPO_ROOT / "plugin.json").is_file(), "plugin.json does not exist yet")
    def test_interface_bogus_key_rejected(self):
        manifest = self.copy / "plugin.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["extensions"]["com.openai"]["interface"]["bogusInterfaceKey"] = "x"
        manifest.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        rc, out = run_checker(["scripts/check-skill.py"], root_arg=self.copy)
        self.assertEqual(rc, 1)
        self.assertIn("is not in the schema", out)

    @unittest.skipUnless(HAS_TSC, "tsc is not installed")
    def test_nested_reference_compiled(self):
        skill_dirs = [d for d in (REPO_ROOT / "skills").glob("*") if (d / "SKILL.md").is_file()]
        self.assertTrue(skill_dirs, "skills are not written yet")
        sub = self.copy / "skills" / skill_dirs[0].name / "references" / "sub"
        sub.mkdir(parents=True, exist_ok=True)
        (sub / "broken.md").write_text(
            "# Nested reference\n\n```ts\nexport function f(): number {\n  return let;\n}\n```\n",
            encoding="utf-8",
        )
        rc, out = run_checker(["scripts/check-examples.py"], root_arg=self.copy)
        self.assertEqual(rc, 1)
        self.assertIn("references/sub/broken.md", out)


class DeletedLints(GuardedRepoCase):
    """Text surgery on a copy's lints: removing a pinned rule from BOTH the
    drop-in and its byte-identical replica must fail the lints gate."""

    @unittest.skipUnless(has_eslint(), "eslint is not installed in lints/check")
    def test_deleted_pinned_rule_fails_check_lints(self):
        self._remove_pinned_rule()
        rc, out = run_bash(["bash", str(self.copy / "scripts" / "check-lints.sh")])
        self.assertEqual(rc, 1)
        self.assertIn("no-console", out)

    @unittest.skipUnless(has_eslint(), "eslint is not installed in lints/check")
    def test_replica_drift_fails_check_lints(self):
        config = self.copy / "lints" / "check" / "eslint.config.mjs"
        text = config.read_text(encoding="utf-8")
        config.write_text(text.replace('"no-console": "error",', '"no-console": "off",'))
        rc, out = run_bash(["bash", str(self.copy / "scripts" / "check-lints.sh")])
        self.assertEqual(rc, 1)
        self.assertIn("byte-identical", out)

    def test_replica_drift_is_detectable_offline(self):
        config = self.copy / "lints" / "check" / "eslint.config.mjs"
        text = config.read_text(encoding="utf-8")
        config.write_text(text.replace('"no-console": "error",', '"no-console": "warn",'))
        drop_in = (self.copy / "lints" / "eslint.config.mjs").read_bytes()
        self.assertNotEqual(drop_in, config.read_bytes())

    def _remove_pinned_rule(self):
        for rel in ("lints/eslint.config.mjs", "lints/check/eslint.config.mjs"):
            path = self.copy / rel
            text = path.read_text(encoding="utf-8")
            kept = [ln for ln in text.splitlines(keepends=True)
                    if '"no-console": "error",' not in ln]
            assert len(kept) < len(text.splitlines(keepends=True)), "could not remove no-console"
            path.write_text("".join(kept), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()