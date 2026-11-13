#!/usr/bin/env python3
"""E2E: run the CI entrypoints exactly as the workflow would, against the real
repo. cwd=REPO_ROOT, timeout=300 on every subprocess. The unittest gate
intentionally discovers only tests/unit so it can never recurse into this
suite; the full tests/ recursion is the CI job itself.
"""

from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

from tests._support import REPO_ROOT

SUBPROCESS_TIMEOUT = 300
# Scoped to tests/unit so the gate cannot recurse into this suite.
GATE_ARGS = "-I -m unittest discover -s tests/unit -t ."
CHECK_DIR = REPO_ROOT / "lints" / "check"
_HAS_ESLINT = None


def has_eslint():
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


def run_ci(argv):
    return subprocess.run(
        list(argv),
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )


class CiJobs(unittest.TestCase):
    def test_check_skill_job_green(self):
        proc = run_ci(["python3", "scripts/check-skill.py"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("0 errors", proc.stdout)

    def test_examples_job_green(self):
        proc = run_ci(["python3", "scripts/check-examples.py", "--require-toolchain"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("0 errors, ", proc.stdout)
        # Every ts block is either ledger-skipped with a reason or compiled.
        self.assertIn(" blocks compiled", proc.stdout)

    @unittest.skipUnless(has_eslint(), "eslint is not installed in lints/check")
    def test_lints_job_green(self):
        proc = run_ci(["bash", "scripts/check-lints.sh"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("expected rules fired", proc.stdout)

    def test_unittest_gate_green(self):
        proc = run_ci(["python3", "-I"] + GATE_ARGS.split())
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()