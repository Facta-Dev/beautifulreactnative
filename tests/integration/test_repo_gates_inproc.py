#!/usr/bin/env python3
"""In-process gates against the real repo: all three checkers must report zero
problems, and the package builder must ship a reproducible ZIP.
"""

from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from tests._support import REPO_ROOT, load_script


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packager = load_script("package-openai-plugin.py")
        cls.HAS_MANIFEST = (REPO_ROOT / "plugin.json").is_file()

    def build(self, tmp):
        out = Path(tmp) / "plugin.zip"
        self.packager.build(REPO_ROOT, out)
        with zipfile.ZipFile(out) as archive:
            return out, archive.namelist()

    @unittest.skipUnless((REPO_ROOT / "plugin.json").is_file(), "plugin.json does not exist yet")
    def test_package_holds_manifest_skills_and_icon(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, names = self.build(tmp)
        self.assertIn("plugin.json", names)
        for skill in sorted((REPO_ROOT / "skills").iterdir()):
            if (skill / "SKILL.md").is_file():
                self.assertIn("skills/%s/SKILL.md" % skill.name, names)

    @unittest.skipUnless((REPO_ROOT / "plugin.json").is_file(), "plugin.json does not exist yet")
    def test_package_leaves_out_evals(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, names = self.build(tmp)
        self.assertFalse([n for n in names if "/evals/" in n], names)

    @unittest.skipUnless((REPO_ROOT / "plugin.json").is_file(), "plugin.json does not exist yet")
    def test_package_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, _ = self.build(tmp)
            first_bytes = first.read_bytes()
            second, _ = self.build(tmp)
            self.assertEqual(first_bytes, second.read_bytes())


class RepoGates(unittest.TestCase):
    """The self-check: the repo always passes its own gates."""

    def test_check_skill_zero_errors(self):
        checker = load_script("check-skill.py")
        problems = checker.check_repo(REPO_ROOT)
        errors = [p for p in problems if p.level == "error"]
        self.assertEqual(errors, [], "\n".join(
            "%s:%d: %s" % (p.path, p.line, p.message) for p in errors
        ))

    def test_check_examples_zero_errors(self):
        checker = load_script("check-examples.py")
        problems, checked, skipped = checker.check_repo(REPO_ROOT)
        errors = [p for p in problems if p.level == "error"]
        self.assertEqual(errors, [], "\n".join(
            "%s:%d: %s" % (p.path, p.line, p.message) for p in errors
        ))
        self.assertGreaterEqual(checked + skipped, 1, "no example blocks discovered")


if __name__ == "__main__":
    unittest.main()