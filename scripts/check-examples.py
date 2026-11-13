#!/usr/bin/env python3
"""Check that every TypeScript code block in the skills and docs type-checks.

Most examples are fragments: a few statements, a handler without its plugin, or
a type that refers to another type defined elsewhere. scripts/examples.json
gives each fragment the code it needs to check (a per-file prelude and a
per-block template) or a reason to skip it — the reason always names what the
block would need (react-native, react, expo-router, ...), because the
generated project has no dependencies. The markdown the agent reads stays as
is.

The blocks are compiled together as one generated TypeScript project with no
dependencies, using `tsc --noEmit` (strict, noUncheckedIndexedAccess). Errors
are reported against the markdown line. When the toolchain is absent the check
degrades to a bracket/quotes sanity pass — unless --require-toolchain is
given, which is how CI proves the compile pass never silently downgraded.

Blocks may also not import a rendering platform, the router or the SDK
(react-native, react, expo-router, @/sdk, @tanstack/*): the ViewModel and SDK
are platform-free, and a block that needs a package cannot be compiled here,
so such a block must be ledger-skipped with a reason naming the package. JSX
blocks use a `tsx` fence and are review-checked rather than compiled, because
the generated project installs no React types.

Stdlib only, Python 3.9+. Exit 1 on any error, 2 if the toolchain is missing
and --require-toolchain is given.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HARNESS = Path("scripts") / "examples.json"
DOC_GLOBS = (
    "README.md",
    "CONTRIBUTING.md",
    "examples/*.md",
    "skills/*/SKILL.md",
    "skills/*/references/*.md",
    "skills/*/references/**/*.md",
)
FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([^`\s]*)")
CODE = "{code}"
# The platform packages a compiling fragment must never import: the ViewModel
# and SDK are platform-free (see the reactnative-best-practices skill,
# 'Architecture contract') and the generated project installs nothing.
FORBIDDEN_MODULES = (
    "react-native",
    "react",
    "expo-router",
    "@/sdk",
    "@tanstack/react-query",
)
FORBIDDEN_PREFIXES = ("@/sdk/", "@tanstack/", "react-native/")
FORBIDDEN_IMPORT_RE = re.compile(
    r"""(?:\bimport\s+(?:type\s+)?(?:[\w*{},\s]+?\bfrom\b\s*)?|require\s*\(\s*|import\s*\(\s*)["']([@.\w][\w@./-]*)["']"""
)
# tsconfig for the generated project. Unused locals are allowed: fragments are
# excerpts, and the docs they come from are not lint targets.
TSCONFIG = {
    "compilerOptions": {
        "strict": True,
        "noUncheckedIndexedAccess": True,
        "noEmit": True,
        "module": "ESNext",
        "moduleResolution": "bundler",
        "target": "ES2023",
        "skipLibCheck": True,
    }
}
TSC_ERROR_RE = re.compile(r"^(?P<file>[^(]+?)\((?P<line>\d+),(?P<col>\d+)\): (?P<text>error TS\d+: .*)$")
# A module becomes a module with `export {}`, which also keeps top-level names
# from colliding between fragments compiled in one project.
MODULE_MARKER = "export {};"
TS_FENCE_LANGS = ("ts", "typescript")


@dataclass(frozen=True)
class Problem:
    path: str
    line: int
    level: str
    message: str


@dataclass
class Block:
    path: str
    line: int  # line of the first code line in the markdown file
    index: int  # 1-based position among the file's ts blocks
    code: str
    lang: str  # "ts", "typescript", or "bash"
    skip: Optional[str] = None
    prelude: str = ""
    template: str = CODE
    wall: bool = False  # violates the I/O wall; cannot compile, reported as an error
    lines: Dict[int, Tuple[str, int]] = field(default_factory=dict)


def rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def format_problem(problem: Problem) -> str:
    prefix = "warning: " if problem.level == "warning" else ""
    return "%s:%d: %s%s" % (problem.path, problem.line, prefix, problem.message)


def summary_line(problems: Sequence[Problem], checked: int, skipped: int) -> str:
    errors = sum(1 for p in problems if p.level == "error")
    err_word = "error" if errors == 1 else "errors"
    return "%d %s, %d blocks compiled, %d skipped" % (errors, err_word, checked, skipped)


def doc_files(root: Path) -> List[Path]:
    found = set()
    for pattern in DOC_GLOBS:
        for path in root.glob(pattern):
            if path.is_file() and "evals" not in path.parts:
                found.add(path)
    return sorted(found)


def find_blocks(root: Path, path: Path) -> List[Block]:
    """Return the ```ts (and ```bash) blocks in one markdown file."""
    blocks: List[Block] = []
    lines = path.read_text(encoding="utf-8").split("\n")
    fence: Optional[str] = None
    lang = ""
    start = 0
    body: List[str] = []
    for number, text in enumerate(lines, 1):
        match = FENCE_RE.match(text)
        if fence is None:
            if match:
                fence = match.group(2)
                lang = match.group(3).split(",")[0]
                start = number + 1
                body = []
            continue
        if match and match.group(2).startswith(fence[0]) and len(match.group(2)) >= len(fence) and not match.group(3):
            if lang in TS_FENCE_LANGS or lang == "bash":
                blocks.append(
                    Block(
                        path=rel(root, path),
                        line=start,
                        index=len(blocks) + 1,
                        code=textwrap.dedent("\n".join(body)),
                        lang=lang,
                    )
                )
            fence = None
            continue
        body.append(text)
    return blocks


def as_text(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(str(v) for v in value)
    return str(value or "")


def first_code_line(code: str) -> str:
    for text in code.split("\n"):
        if text.strip():
            return text.strip()
    return ""


def imported_modules(code: str) -> List[str]:
    """Module specifiers the fragment imports, in source order."""
    return [name for name in FORBIDDEN_IMPORT_RE.findall(code)]


def forbidden_module(specifier: str) -> Optional[str]:
    base = specifier.split("/")[0] if not specifier.startswith("@") else "/".join(specifier.split("/")[:2])
    if base in FORBIDDEN_MODULES or any(specifier.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        return specifier
    return None


def apply_harness(
    root: Path, blocks: List[Block], harness: Dict[str, Any]
) -> List[Problem]:
    """Attach preludes, templates, and skips. Report harness drift."""
    problems: List[Problem] = []
    files = harness.get("files", {})
    if not isinstance(files, dict):
        problems.append(
            Problem(HARNESS.as_posix(), 1, "error", "files must be a JSON object")
        )
        return problems
    by_path: Dict[str, List[Block]] = {}
    for block in blocks:
        by_path.setdefault(block.path, []).append(block)
    harness_path = HARNESS.as_posix()
    for path, entry in files.items():
        if path not in by_path:
            problems.append(
                Problem(harness_path, 1, "error", "%s: file has no ts blocks or does not exist" % path)
            )
            continue
        if not isinstance(entry, dict) or not isinstance(entry.get("blocks") or {}, dict):
            problems.append(
                Problem(harness_path, 1, "error", "%s: entry must be an object" % path)
            )
            continue
        for key, spec in (entry.get("blocks") or {}).items():
            try:
                index = int(key)
            except ValueError:
                problems.append(Problem(harness_path, 1, "error", "%s: block key %r is not a number" % (path, key)))
                continue
            if index < 1 or index > len(by_path[path]):
                problems.append(
                    Problem(harness_path, 1, "error", "%s: no ts block #%d (file has %d)" % (path, index, len(by_path[path])))
                )
                continue
            if not isinstance(spec, dict):
                problems.append(
                    Problem(harness_path, 1, "error",
                            "%s: block spec must be an object" % path)
                )
                continue
            block = by_path[path][index - 1]
            expected = (spec.get("first_line") or "").strip()
            actual = first_code_line(block.code)
            if expected != actual:
                problems.append(
                    Problem(
                        block.path,
                        block.line,
                        "error",
                        "ts block #%d does not match %s (expected first line %r, found %r); "
                        "blocks were added, moved, or edited, so update the harness" % (index, harness_path, expected, actual),
                    )
                )
                block.skip = "harness out of date"
                continue
            if "skip" in spec:
                reason = str(spec.get("skip") or "").strip()
                if not reason:
                    problems.append(Problem(block.path, block.line, "error", "ts block #%d: skip needs a reason" % index))
                block.skip = reason or "no reason"
                continue
            template = as_text(spec.get("template")) or CODE
            if CODE not in template:
                problems.append(
                    Problem(harness_path, 1, "error", "%s block #%d: template has no {code}" % (path, index))
                )
                template = CODE
            block.template = template
        prelude = as_text(entry.get("prelude"))
        for block in by_path[path]:
            block.prelude = prelude
    return problems


def render(block: Block, harness_label: str) -> str:
    """Build one module's source and record where each line came from."""
    out: List[str] = []
    origin: List[Tuple[str, int]] = []

    def add(text: str, where: Tuple[str, int]) -> None:
        for piece in text.split("\n"):
            out.append(piece)
            origin.append(where)

    if block.prelude:
        add(block.prelude, (harness_label, 1))
    before, _, after = block.template.partition(CODE)
    if before:
        add(before.rstrip("\n"), (harness_label, 1))
    for offset, piece in enumerate(block.code.split("\n")):
        out.append(piece)
        origin.append((block.path, block.line + offset))
    if after:
        add(after.lstrip("\n"), (harness_label, 1))
    add(MODULE_MARKER, (harness_label, 1))
    block.lines = {number: where for number, where in enumerate(origin, 1)}
    return "\n".join(out) + "\n"


def build_project(project: Path, blocks: List[Block]) -> Dict[str, Block]:
    (project / "src").mkdir(parents=True)
    (project / "tsconfig.json").write_text(
        json.dumps(TSCONFIG, indent=2) + "\n", encoding="utf-8"
    )
    modules: Dict[str, Block] = {}
    for number, block in enumerate(blocks, 1):
        name = "ex_%03d.ts" % number
        (project / "src" / name).write_text(render(block, HARNESS.as_posix()), encoding="utf-8")
        modules["src/%s" % name] = block
    return modules


def map_errors(output: str, modules: Dict[str, Block]) -> List[Problem]:
    """Turn tsc's diagnostics into problems at markdown lines."""
    problems: List[Problem] = []
    seen = set()
    for raw in output.splitlines():
        match = TSC_ERROR_RE.match(raw.strip())
        if not match:
            continue
        block = modules.get(match.group("file").replace("\\", "/"))
        if block is None:
            # Some tsc versions print absolute paths; fall back to the basename.
            block = modules.get("src/" + Path(match.group("file")).name)
        if block is None:
            continue
        text = match.group("text")
        line_no = int(match.group("line"))
        where = block.lines.get(line_no, (block.path, block.line))
        if where[0] != block.path:
            text = "%s (in the harness code for %s ts block #%d)" % (text, block.path, block.index)
        key = (where, text)
        if key in seen:
            continue
        seen.add(key)
        problems.append(Problem(where[0], where[1], "error", text))
    return problems


def find_tsc() -> Optional[List[str]]:
    """The command that runs tsc, or None.

    A global tsc wins; otherwise npx resolves TypeScript 5.x through the npx
    cache (`--yes -p typescript@^5` seeds it, which is how CI runners get a
    toolchain from a Node-only job). The examples must stay valid TypeScript 5.
    """
    if shutil.which("tsc"):
        return ["tsc"]
    if shutil.which("npx"):
        probe = subprocess.run(
            ["npx", "--yes", "-p", "typescript@^5", "tsc", "--version"],
            capture_output=True, text=True, timeout=300,
        )
        if probe.returncode == 0:
            return ["npx", "--yes", "-p", "typescript@^5", "tsc"]
    return None


def run_tsc(project: Path, tsc: Sequence[str]) -> Tuple[int, str, str]:
    result = subprocess.run(
        [*tsc, "--noEmit", "--pretty", "false", "-p", "."],
        capture_output=True,
        text=True,
        cwd=str(project),
        env=None,
    )
    return result.returncode, result.stdout, result.stderr


def check_brackets(code: str) -> Optional[str]:
    """Fallback-language sanity: balanced delimiters ignoring strings/comments."""
    pairs = {"(": ")", "[": "]", "{": "}"}
    closer = {v: k for k, v in pairs.items()}
    stack: List[str] = []
    quote: Optional[str] = None
    escaped = comment = line_comment = False
    previous = ""
    for ch in code:
        if line_comment:
            if ch == "\n":
                line_comment = False
            previous, escaped = ch, False
            continue
        if comment:
            if previous == "*" and ch == "/":
                comment = False
            previous, escaped = ch, False
            continue
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            previous, escaped = ch, False
            continue
        if previous == "/" and ch == "/":
            line_comment = True
            previous, escaped = ch, False
            continue
        if previous == "/" and ch == "*":
            comment = True
            previous, escaped = ch, False
            continue
        if ch in "\"'`":
            quote = ch
        elif ch in pairs:
            stack.append(pairs[ch])
        elif ch in closer:
            if not stack or stack.pop() != ch:
                return "unbalanced %s" % ch
        previous, escaped = ch, False
    if quote:
        return "unterminated string"
    if comment:
        return "unterminated comment"
    if line_comment:
        return None
    if stack:
        return "unclosed %s" % stack[-1]
    return None


def check_quotes(code: str) -> Optional[str]:
    """A bash block's job in the fallback pass: quotes stay balanced.

    Comments carry no quotes to balance — an unquoted `#` skips to the end of
    its line, so prose like `# the project's settings` stays quiet.
    """
    quote: Optional[str] = None
    escaped = False
    in_comment = False
    for ch in code:
        if in_comment:
            if ch == "\n":
                in_comment = False
            continue
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch == "#":
            in_comment = True
            continue
        if ch in "\"'":
            quote = ch
    if quote:
        return "unbalanced quotes"
    return None


def check_repo(root: Path, require_toolchain: bool = False) -> Tuple[List[Problem], int, int]:
    """Return (problems, compiled block count, skipped block count)."""
    root = Path(root)
    harness, problems = load_harness(root)
    blocks: List[Block] = []
    for path in doc_files(root):
        blocks.extend(find_blocks(root, path))
    problems.extend(apply_harness(root, blocks, harness))
    # The I/O wall: a compiling fragment must never name a stack package.
    for block in blocks:
        if block.skip is not None or block.lang not in TS_FENCE_LANGS:
            continue
        for specifier in imported_modules(block.code):
            hit = forbidden_module(specifier)
            if hit:
                block.wall = True
                problems.append(
                    Problem(
                        block.path,
                        block.line,
                        "error",
                        "ts block #%d imports %s — the ViewModel and SDK are framework-free "
                        "and the generated project installs nothing; ledger the block with a "
                        "skip reason naming the framework package, or re-type the example "
                        "against a port"
                        % (block.index, hit),
                    )
                )
    bash_problems = [
        Problem(
            block.path,
            block.line,
            "error",
            "bash block #%d: %s" % (block.index, problem),
        )
        for block in blocks
        for problem in [check_quotes(block.code)]
        if block.lang == "bash" and problem
    ]
    problems.extend(bash_problems)
    to_check = [b for b in blocks if b.skip is None and b.lang in TS_FENCE_LANGS]
    skipped = len([b for b in blocks if b.skip is not None])
    # Fragments whose import wall was violated cannot compile anyway; the
    # ledger is what keeps them out, and that ledger entry was just required.
    to_check = [b for b in to_check if not b.wall]
    checked = 0
    if to_check:
        tsc = find_tsc()
        if tsc is None:
            note = "tsc not found; falling back to bracket sanity for %d ts blocks" % len(to_check)
            if require_toolchain:
                sys.stderr.write("check-examples: %s\n" % note)
                sys.stderr.write(
                    "check-examples: --require-toolchain given and no tsc on PATH "
                    "(install typescript, or run under npx); refusing to silently downgrade\n"
                )
                return problems + [
                    Problem("check-examples", 1, "error", "tsc not found on PATH")
                ], 0, skipped
            problems.append(
                Problem("check-examples", 1, "warning", note)
            )
            problems.extend(
                Problem(
                    b.path,
                    b.line,
                    "error",
                    "ts block #%d: %s" % (b.index, problem),
                )
                for b in to_check
                for problem in [check_brackets(b.code)]
                if problem
            )
            return problems, 0, skipped
        with tempfile.TemporaryDirectory(prefix="examples-check.") as tmp:
            project = Path(tmp) / "project"
            modules = build_project(project, to_check)
            status, stdout, stderr = run_tsc(project, tsc)
            found = map_errors(stdout, modules)
            if status != 0 and not found:
                tail = (stderr.strip() or stdout.strip()).splitlines()[-1:] or ["tsc failed"]
                found = [Problem("examples-check", 1, "error", tail[0])]
            problems.extend(found)
        checked = len(modules)
    return problems, checked, skipped


def load_harness(root: Path) -> Tuple[Dict[str, Any], List[Problem]]:
    path = root / HARNESS
    if not path.exists():
        return {}, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return {}, [Problem(HARNESS.as_posix(), getattr(exc, "lineno", 1), "error", "invalid JSON: %s" % exc)]
    if not isinstance(data, dict):
        return {}, [Problem(HARNESS.as_posix(), 1, "error", "top level must be an object")]
    return data, []


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that every TypeScript code block in the skills and docs type-checks."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="repository root (default: current directory)",
    )
    parser.add_argument(
        "--require-toolchain",
        dest="require_toolchain",
        action="store_true",
        help="fail instead of degrading to bracket sanity when tsc is missing",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="print findings as JSON",
    )
    args = parser.parse_args(argv)
    problems, checked, skipped = check_repo(Path(args.root), args.require_toolchain)
    errors = sum(1 for p in problems if p.level == "error")
    if args.as_json:
        json.dump(
            {
                "ok": errors == 0,
                "error_count": errors,
                "compiled": checked,
                "skipped": skipped,
                "summary": summary_line(problems, checked, skipped),
                "problems": [asdict(p) for p in problems],
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        for problem in problems:
            sys.stdout.write(format_problem(problem) + "\n")
        sys.stdout.write(summary_line(problems, checked, skipped) + "\n")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())