#!/usr/bin/env bash
# Prove the drop-in lint config fires: every // expect: rule in the check
# project's violation files must report on its marked line, nothing unmarked
# may report, `tsc --noEmit` must stay green on the same files, and
# lints/check/eslint.config.mjs must stay byte-identical to
# lints/eslint.config.mjs — the file users copy next to their package.json.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DROP_IN="$ROOT/lints/eslint.config.mjs"
CHECK="$ROOT/lints/check"
CONFIG="$CHECK/eslint.config.mjs"

fail() {
  echo "check-lints: $1" >&2
  exit 1
}

[ -f "$DROP_IN" ] || fail "missing lints/eslint.config.mjs"
[ -f "$CONFIG" ] || fail "missing lints/check/eslint.config.mjs (the byte-identical replica)"
if ! cmp -s "$DROP_IN" "$CONFIG"; then
  fail "lints/check/eslint.config.mjs has drifted: it must stay byte-identical to lints/eslint.config.mjs (import path rewrite only is allowed, and nothing needs one)."
fi

if ! command -v node >/dev/null 2>&1; then
  fail "node not found on PATH"
fi
if ! command -v python3 >/dev/null 2>&1; then
  fail "python3 not found on PATH"
fi

# The harness needs its devDependencies (eslint, typescript-eslint and the
# stack packages so projectService can resolve). Install them when absent;
# a failed install is a hard failure with the reason on stderr.
if [ ! -d "$CHECK/node_modules" ]; then
  echo "check-lints: lints/check/node_modules missing; running npm ci" >&2
  (
    cd "$CHECK"
    if command -v timeout >/dev/null 2>&1; then
      timeout 600 npm ci --no-audit --no-fund 2>&2 || npm install --no-audit --no-fund 2>&2
    else
      npm ci --no-audit --no-fund 2>&2 || npm install --no-audit --no-fund 2>&2
    fi
  ) || fail "npm install inside lints/check failed; see the output above"
fi

cd "$CHECK"

# Bound every tool run (GNU coreutils timeout on Linux; a perl alarm wrapper
# where timeout is missing, e.g. macOS), and always surface stderr.
bounded() {
  local seconds="$1"
  shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "$seconds" "$@"
  else
    perl -e 'alarm shift; exec @ARGV' "$seconds" "$@"
  fi
}

REPORT="$(mktemp "${TMPDIR:-/tmp}/lints-check-json.XXXXXX")"
TSC_OUT="$(mktemp "${TMPDIR:-/tmp}/lints-check-tsc.XXXXXX")"
trap 'rm -rf "$REPORT" "$TSC_OUT"' EXIT

TSC_STATUS=0
bounded 240 npx --no-install tsc --noEmit --pretty false -p "$CHECK" >"$TSC_OUT" 2>&1 || TSC_STATUS=$?
if [ "$TSC_STATUS" -ne 0 ]; then
  echo "check-lints: tsc --noEmit failed on the check project (exit $TSC_STATUS):" >&2
  cat "$TSC_OUT" >&2
  fail "the violation harness must stay type-clean; fix the harness, never the tsc config"
fi

ESLINT_STATUS=0
bounded 240 npx --no-install eslint --format json src >"$REPORT" 2>"$REPORT.err" || ESLINT_STATUS=$?
# eslint exits nonzero whenever a marked rule fires (that is the point); a
# failed run still needs a parseable JSON report.
if ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$REPORT" >/dev/null 2>&1; then
  echo "check-lints: non-JSON report from eslint (exit $ESLINT_STATUS):" >&2
  if [ -s "$REPORT.err" ]; then
    cat "$REPORT.err" >&2
  fi
  head -5 "$REPORT" >&2
  fail "eslint did not produce a JSON report; check its stderr above"
fi
if [ -s "$REPORT.err" ]; then
  echo "check-lints: eslint stderr (surfaced on every run):" >&2
  cat "$REPORT.err" >&2
fi

python3 - "$REPORT" "$CONFIG" "$CHECK" <<'PY'
"""Correlate // expect: markers with the eslint JSON report.

A marker line is a standalone comment `// expect:<rule>[,<rule>...]`. It marks
the next line. Stacked markers on consecutive lines each point at that same
next line.
"""

import json
import os
import re
import sys
from pathlib import Path

report_path, config_path, check_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])

MARKER_RE = re.compile(r"^// expect:([\w@./-]+(?:\s*,\s*[\w@./-]+)*)\s*$")


def marker_files():
    for pattern in ("*.ts", "*.tsx"):
        for path in sorted((check_dir / "src").rglob(pattern)):
            yield path


expected: dict[str, dict[int, set[str]]] = {}
total = 0
for path in marker_files():
    lines = path.read_text(encoding="utf-8").split("\n")
    relative = os.path.relpath(os.path.realpath(path), os.path.realpath(check_dir))
    for index, text in enumerate(lines):
        match = MARKER_RE.match(text.strip())
        if not match:
            continue
        line_no = index + 2  # the marker points at the next line
        rules = [rule.strip() for rule in match.group(1).split(",")]
        bucket = expected.setdefault(relative, {}).setdefault(line_no, set())
        bucket.update(rules)
        total += len(rules)

if not expected:
    print("check-lints: no // expect: markers found in lints/check/src")
    sys.exit(1)

problems: list[str] = []

config_text = Path(config_path).read_text(encoding="utf-8")
named = {rule for lines in expected.values() for rules in lines.values() for rule in rules}
for rule in sorted(named):
    if '"%s"' % rule.split("/")[-1] not in config_text and '"%s"' % rule not in config_text:
        problems.append(
            "marker %s is not enabled in the drop-in config (rule id not found in lints/eslint.config.mjs)" % rule
        )

messages = []
for row in json.loads(Path(report_path).read_text(encoding="utf-8")):
    relative = os.path.relpath(
        os.path.realpath(row["filePath"]),
        os.path.realpath(check_dir),
    )
    for message in row["messages"]:
        messages.append((relative, int(message.get("line", 0)), message.get("ruleId"), str(message.get("message", "")).split("\n")[0]))

matched = 0
for relative, lines in expected.items():
    for line_no, rules in lines.items():
        hit = {rule: False for rule in rules}
        for file, msg_line, rule_id, _text in messages:
            if file != relative or msg_line != line_no or rule_id is None:
                continue
            if rule_id in hit and not hit[rule_id]:
                hit[rule_id] = True
        for rule, fired in hit.items():
            if fired:
                matched += 1
            else:
                problems.append(
                    "%s:%d: expected %s did not fire (marker quotes it)" % (relative, line_no, rule)
                )

for file, line, rule_id, text in messages:
    if rule_id is None:
        continue
    want = expected.get(file, {}).get(line)
    if not want or rule_id not in want:
        problems.append("%s:%d: unexpected %s: %s" % (file, line, rule_id, text))

width = max((len("%s:%d" % (p, l)) for p, l, *_ in messages), default=8)
for file, line, rule_id, text in sorted(messages, key=lambda m: (m[0], m[1], m[2] or "")):
    print("%-*s  %s  %s" % (width, "%s:%d" % (file, line), rule_id, text))

if problems:
    print()
    for problem in problems:
        print("check-lints: %s" % problem)
    sys.exit(1)

print()
print("%d expected rules fired on their marked line; config matches lints/eslint.config.mjs" % total)
PY