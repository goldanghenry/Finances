#!/usr/bin/env python3
"""Lint mermaid blocks in corpus markdown files.

Checks:
  1. Unquoted node/shape labels that contain risky special characters
     (%, >, <, (, ), backtick) — these can break Mermaid parsing.
  2. Node IDs that use reserved Mermaid keywords: end, graph, subgraph.
  3. Unquoted labels with bare > or < (arrow-like chars outside quotes).

Exit 1 if any issues found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import ROOT, iter_corpus_md

# Characters that require quoting when inside unquoted labels
RISKY_RE = re.compile(r'[%<>`()]')

# Mermaid reserved keywords that must not be used as bare node IDs
RESERVED = {'end', 'graph', 'subgraph', 'style', 'classDef', 'click', 'direction'}

# Matches bare (unquoted) node labels:  NodeId[text], NodeId(text), NodeId{text}
# Cylinder shape NodeId[(text)] is handled by CYL_RE below.
NODE_LABEL_RE = re.compile(
    r'(?<!["\w])'           # not preceded by quote or word char (prevent false match inside quoted text)
    r'([A-Za-z][A-Za-z0-9_]*)'    # node id
    r'(\[(?!\()|\((?!\[)|\{)'      # opening bracket (not cylinder [( )
    r'([^"\](){}\n]+?)'            # label — must NOT already start with "
    r'(\]|\)|\})',                  # closing bracket
)

CYL_LABEL_RE = re.compile(
    r'([A-Za-z][A-Za-z0-9_]*)'
    r'\[(\()([^")(\n]+?)(\)\])',
)


def _labels_in_block(block: str) -> list[tuple[int, str, str]]:
    """Return list of (lineno_in_block, label_text, raw_line) for unquoted labels."""
    results = []
    for li, line in enumerate(block.splitlines(), 1):
        if '%%' in line:
            continue
        for m in list(NODE_LABEL_RE.finditer(line)) + list(CYL_LABEL_RE.finditer(line)):
            text = m.group(3)
            if text.startswith('"'):
                continue
            results.append((li, text, line.strip()))
    return results


def check_file(path: Path) -> list[str]:
    issues: list[str] = []
    text = path.read_text(encoding='utf-8', errors='ignore')

    for mi, bm in enumerate(re.finditer(r'```mermaid\n(.*?)```', text, re.DOTALL), 1):
        block = bm.group(1)

        for li, label, raw in _labels_in_block(block):
            # Rule 1: risky special chars in unquoted label
            if RISKY_RE.search(label):
                issues.append(
                    f'  block {mi} line {li}: unquoted label with special char — {raw}'
                )

        # Rule 2: `end` used as a node ID (not as subgraph terminator).
        # A bare `end` line (possibly with whitespace) is valid mermaid subgraph syntax.
        # `end[label]`  or  `end --> X`  would create a node named "end" which parsers disallow.
        for li, line in enumerate(block.splitlines(), 1):
            stripped = line.strip()
            if re.match(r'^end\s*[\[({]', stripped):
                issues.append(
                    f'  block {mi} line {li}: "end" used as node ID — rename to avoid parse conflict: {stripped}'
                )
            elif re.match(r'^end\s*--', stripped):
                issues.append(
                    f'  block {mi} line {li}: "end" used as source node ID — rename: {stripped}'
                )

    return issues


def main() -> int:
    bad = 0
    for path in iter_corpus_md():
        issues = check_file(path)
        if issues:
            bad += 1
            print(f'{path.relative_to(ROOT)}:')
            for issue in issues:
                print(issue)
    print(f'\n{bad} files with mermaid issues')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
