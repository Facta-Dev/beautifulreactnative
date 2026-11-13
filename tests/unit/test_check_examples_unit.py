#!/usr/bin/env python3
"""Tests for scripts/check-examples.py."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tests._support import REPO_ROOT, load_script, write


ce = load_script("check-examples.py")

HAS_TSC = ce.find_tsc() is not None

README = """\
# Demo

```ts
export function double(x: number): number {
    return x * 2;
}
```

```bash
npm test
```

- A list item with an indented example:

  ```ts
  const y = 2 * 2;
  ```

~~~markdown
```ts
<a template placeholder, not real code>
```
~~~
"""


class RepoTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        write(self.root / "README.md", README)

    def tearDown(self):
        self._tmp.cleanup()

    def blocks(self):
        return ce.find_blocks(self.root, self.root / "README.md")

    def harness(self, data):
        write(self.root / "scripts" / "examples.json", json.dumps(data))


class FindBlocksTest(RepoTest):
    def test_finds_ts_and_bash_blocks(self):
        blocks = self.blocks()
        self.assertEqual([b.index for b in blocks], [1, 2, 3])
        self.assertEqual([b.lang for b in blocks], ["ts", "bash", "ts"])
        self.assertEqual(blocks[0].line, 4)
        self.assertIn("export function double", blocks[0].code)

    def test_typescript_fences_count_as_ts(self):
        write(self.root / "README.md", "```typescript\nexport const a = 1;\n```\n")
        blocks = self.blocks()
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].lang, "typescript")

    def test_dedents_indented_blocks(self):
        self.assertEqual(self.blocks()[2].code, "const y = 2 * 2;")

    def test_bash_blocks_are_extracted_for_quote_sanity(self):
        codes = [(b.lang, b.code) for b in self.blocks()]
        self.assertIn(("bash", "npm test"), codes)

    def test_ignores_ts_fences_nested_in_other_blocks(self):
        codes = " ".join(b.code for b in self.blocks())
        self.assertNotIn("template placeholder", codes)

    def test_skips_eval_fixtures(self):
        write(self.root / "skills" / "demo" / "SKILL.md", "```ts\nconst a = 1;\n```\n")
        write(self.root / "skills" / "demo" / "evals" / "case" / "prompt.md", "```ts\nbroken\n```\n")
        names = [p.relative_to(self.root).as_posix() for p in ce.doc_files(self.root)]
        self.assertIn("skills/demo/SKILL.md", names)
        self.assertNotIn("skills/demo/evals/case/prompt.md", names)


class FallbackTest(RepoTest):
    def test_balanced_block_is_quiet(self):
        code = "const a = { b: [1] };"
        self.assertIsNone(ce.check_brackets(code))

    def test_unbalanced_ts_block_is_a_problem(self):
        self.assertEqual(ce.check_brackets("const a = { b: [1];"), "unclosed }")
        self.assertEqual(ce.check_brackets("const a = [1; b()"), "unclosed ]")

    def test_string_with_brackets_does_not_confuse_the_scan(self):
        self.assertIsNone(ce.check_brackets('const s = "{ [ ( }"; // }'))

    def test_unterminated_string_is_reported(self):
        self.assertEqual(ce.check_brackets("const s = \"oops"), "unterminated string")

    def test_bash_quote_imbalance_is_reported(self):
        self.assertEqual(ce.check_quotes("echo \"oops"), "unbalanced quotes")

    def test_balanced_bash_quotes_pass(self):
        self.assertIsNone(ce.check_quotes('echo "ok" && ls'))


class HarnessTest(RepoTest):
    def apply(self, data):
        blocks = self.blocks()
        problems = ce.apply_harness(self.root, blocks, data)
        return blocks, problems

    def test_template_and_prelude_are_attached(self):
        blocks, problems = self.apply({"files": {"README.md": {
            "prelude": "type Mode = 'fast' | 'slow';",
            "blocks": {"3": {"first_line": "const y = 2 * 2;",
                             "template": ["function wrap(): number {", "{code}", "return y;", "}"]}},
        }}})
        self.assertEqual(problems, [])
        self.assertEqual(blocks[0].prelude, "type Mode = 'fast' | 'slow';")
        self.assertEqual(blocks[2].template, "function wrap(): number {\n{code}\nreturn y;\n}")

    def test_first_line_mismatch_reports_drift_at_the_block(self):
        blocks, problems = self.apply({"files": {"README.md": {
            "blocks": {"3": {"first_line": "const z = 3;", "template": "{code}"}},
        }}})
        self.assertEqual(len(problems), 1)
        self.assertEqual((problems[0].path, problems[0].line), ("README.md", 16))
        self.assertIn("update the harness", problems[0].message)
        self.assertIsNotNone(blocks[2].skip)

    def test_skip_needs_a_reason(self):
        blocks, problems = self.apply({"files": {"README.md": {
            "blocks": {"3": {"first_line": "const y = 2 * 2;", "skip": ""}},
        }}})
        self.assertEqual(len(problems), 1)
        self.assertIn("skip needs a reason", problems[0].message)

    def test_skip_with_reason_is_not_an_error(self):
        blocks, problems = self.apply({"files": {"README.md": {
            "blocks": {"3": {"first_line": "const y = 2 * 2;", "skip": "a fragment"}},
        }}})
        self.assertEqual(problems, [])
        self.assertEqual(blocks[2].skip, "a fragment")

    def test_unknown_block_and_file_are_errors(self):
        _, problems = self.apply({"files": {
            "README.md": {"blocks": {"9": {"first_line": "x"}}},
            "missing.md": {"blocks": {}},
        }})
        messages = " ".join(p.message for p in problems)
        self.assertIn("no ts block #9", messages)
        self.assertIn("missing.md", messages)

    def test_template_without_code_slot_is_an_error(self):
        _, problems = self.apply({"files": {"README.md": {
            "blocks": {"1": {"first_line": "export function double(x: number): number {", "template": "function f() {}"}},
        }}})
        self.assertIn("has no {code}", problems[0].message)

    def test_malformed_ledger_files_list_is_a_problem(self):
        _, problems = self.apply({"files": ["oops"]})
        self.assertEqual([p.message for p in problems], ["files must be a JSON object"])

    def test_block_spec_array_is_a_problem(self):
        _, problems = self.apply({"files": {"README.md": {"blocks": {"1": ["oops"]}}}})
        self.assertIn("block spec must be an object", problems[0].message)


class DomainWallTest(RepoTest):
    def test_stack_import_in_a_compiling_block_is_rejected(self):
        for module in ("react-native", "react", "expo-router", "@/sdk", "@tanstack/react-query"):
            code = 'import { x } from "%s";\nvoid x;' % module
            write(self.root / "README.md", "```ts\n%s\n```\n" % code)
            problems, _checked, _skipped = ce.check_repo(self.root)
            self.assertTrue(
                any(module in p.message and "framework-free" in p.message for p in problems),
                module,
            )

    def test_node_builtin_imports_stay_allowed(self):
        write(self.root / "README.md", "```ts\nexport const host = new URL('https://facta.dev').host;\n```\n")
        problems, _checked, _skipped = ce.check_repo(self.root)
        errors = [p for p in problems if "I/O-free" in p.message]
        self.assertEqual(errors, [])


class MappingTest(RepoTest):
    def test_rendered_lines_map_back_to_markdown_and_harness(self):
        block = self.blocks()[2]
        block.template = "function wrap(): number {\n{code}\nreturn y;\n}"
        source = ce.render(block, "scripts/examples.json").split("\n")
        code_line = source.index("const y = 2 * 2;") + 1
        self.assertEqual(block.lines[code_line], ("README.md", 16))
        self.assertEqual(block.lines[code_line - 1][0], "scripts/examples.json")

    def test_each_fragment_becomes_a_module(self):
        block = self.blocks()[0]
        source = ce.render(block, "scripts/examples.json")
        self.assertIn("export {};", source)

    def test_tsc_errors_map_to_markdown_lines(self):
        block = self.blocks()[0]
        ce.render(block, "scripts/examples.json")
        modules = {"src/ex_001.ts": block}
        output = "src/ex_001.ts(2,21): error TS2322: Type 'string' is not assignable to type 'number'.\n"
        problems = ce.map_errors(output, modules)
        self.assertEqual(len(problems), 1)
        self.assertEqual((problems[0].path, problems[0].line), ("README.md", 5))
        self.assertIn("TS2322", problems[0].message)

    def test_harness_line_errors_name_the_harness(self):
        block = self.blocks()[0]
        ce.render(block, "scripts/examples.json")
        modules = {"src/ex_001.ts": block}
        output = "src/ex_001.ts(4,1): error TS2322: type error in the module marker\n"
        problems = ce.map_errors(output, modules)
        self.assertEqual(len(problems), 1)
        self.assertIn("in the harness code", problems[0].message)


@unittest.skipUnless(HAS_TSC, "tsc is not installed")
class EndToEndTest(RepoTest):
    def test_a_broken_example_reports_its_markdown_line(self):
        write(self.root / "README.md", "# Demo\n\n```ts\nexport function f(): number {\n  return \"not a number\";\n}\n```\n")
        problems, compiled, skipped = ce.check_repo(self.root)
        self.assertEqual((compiled, skipped), (1, 0))
        self.assertEqual(len(problems), 1)
        self.assertEqual((problems[0].path, problems[0].line), ("README.md", 5))

    def test_a_fragment_compiles_with_its_template(self):
        self.harness({"files": {"README.md": {"blocks": {
            "3": {"first_line": "const y = 2 * 2;", "template": ["function wrap(): number {", "{code}", "return y;", "}"]},
        }}}})
        problems, compiled, skipped = ce.check_repo(self.root)
        self.assertEqual(problems, [])
        self.assertEqual((compiled, skipped), (2, 0))

    def test_duplicate_names_across_blocks_do_not_collide(self):
        # Each block is its own module (`export {}`), so block 2 may re-declare
        # what block 1 already declared.
        write(self.root / "README.md", README.replace(
            "    return x * 2;\n}",
            "    return x * 3;\n}",
        ))
        problems, compiled, _skipped = ce.check_repo(self.root)
        self.assertEqual(problems, [])
        self.assertEqual(compiled, 2)

    def test_require_toolchain_fails_loudly_without_tsc(self):
        import contextlib
        from unittest import mock
        write(self.root / "README.md", "# Demo\n\n```ts\nexport const n = 1;\n```\n")
        with mock.patch.object(ce.shutil, "which", return_value=None), \
                contextlib.redirect_stderr(io.StringIO()) as stderr:
            problems, _compiled, _skipped = ce.check_repo(self.root, require_toolchain=True)
        self.assertTrue(any("tsc not found on PATH" in p.message for p in problems))
        self.assertIn("--require-toolchain", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()