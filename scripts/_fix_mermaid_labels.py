#!/usr/bin/env python3
"""Fix risky unquoted mermaid node/shape labels in corpus files.

Wraps labels that contain %, >, <, or backtick in double-quotes, and
normalises underscores → spaces, _to_ / NNtoNN → ~.
Edge labels (|...|) are also fixed for consistency.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Characters that need quoting when present in unquoted labels
RISKY = re.compile(r'[%<>`]|(?<!\-)\>(?!\>)')


def normalise_text(text: str) -> str:
    """Convert underscore-separated label text to readable form."""
    # NNtoNN range  → NN~NN
    text = re.sub(r'(\d+)to(\d+)', r'\1~\2', text)
    # Remove stray backticks
    text = text.replace('`', '')
    # Underscores → spaces
    text = text.replace('_', ' ')
    return text.strip()


def quote_label(text: str) -> str:
    return f'"{normalise_text(text)}"'


# ------------------------------------------------------------------ node labels

# Matches:  NodeId[text]  NodeId(text)  NodeId{text}  NodeId[(text)]
# Groups: (node_id, open_delim, label_text, close_delim)
NODE_RE = re.compile(
    r'([A-Za-z0-9_]+)'           # node id
    r'(\[|(?<!\[)\(|\{)'          # opening bracket (not already inside [...])
    r'([^[\](){}\n]+?)'           # label text
    r'(\]|(?<!\))\)|\})',         # closing bracket
)

# Cylinder shape  NodeId[(text)]  — must be handled separately
CYL_RE = re.compile(
    r'([A-Za-z0-9_]+)'
    r'\[(\()'
    r'([^)\n]+?)'
    r'(\)\])',
)


def fix_node_labels(line: str) -> str:
    """Fix unquoted node/shape labels on a single mermaid source line."""
    # Skip lines that are already using quoted labels or are pure comments
    # (lines with %% are mermaid comments – skip)
    if '%%' in line:
        return line

    # --- cylinder shape  NodeId[(text)]  ---
    def _fix_cyl(m: re.Match) -> str:
        nid, _, text, _ = m.groups()
        if text.startswith('"'):
            return m.group(0)
        if not RISKY.search(text) and '_' not in text:
            return m.group(0)
        return f'{nid}[({quote_label(text)})]'

    line = CYL_RE.sub(_fix_cyl, line)

    # --- regular node label ---
    def _fix_node(m: re.Match) -> str:
        nid, ob, text, cb = m.groups()
        if text.startswith('"'):
            return m.group(0)
        # Only fix if text contains risky chars or underscores
        if not RISKY.search(text) and '_' not in text:
            return m.group(0)
        return f'{nid}{ob}{quote_label(text)}{cb}'

    line = NODE_RE.sub(_fix_node, line)
    return line


# ------------------------------------------------------------------ edge labels

# Matches  -->|label|  (and variants -.->, -.-, etc.)
EDGE_LABEL_RE = re.compile(r'\|([^|"\n]+)\|')


def fix_edge_labels(line: str) -> str:
    """Fix unquoted edge labels that contain underscores or special chars."""
    if '%%' in line:
        return line

    def _fix_edge(m: re.Match) -> str:
        text = m.group(1)
        if text.startswith('"'):
            return m.group(0)
        if '_' not in text and not RISKY.search(text):
            return m.group(0)
        return f'|"{normalise_text(text)}"|'

    return EDGE_LABEL_RE.sub(_fix_edge, line)


# ------------------------------------------------------------------ block-level

def fix_mermaid_block(block: str) -> str:
    lines = block.splitlines(keepends=True)
    fixed = []
    for ln in lines:
        ln = fix_node_labels(ln)
        ln = fix_edge_labels(ln)
        fixed.append(ln)
    return ''.join(fixed)


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    original = text

    def _fix_block(m: re.Match) -> str:
        return '```mermaid\n' + fix_mermaid_block(m.group(1)) + '```'

    text = re.sub(r'```mermaid\n(.*?)```', _fix_block, text, flags=re.DOTALL)

    if text != original:
        path.write_text(text, encoding='utf-8')
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    targets = argv or []
    changed = 0
    if targets:
        paths = [Path(t) for t in targets]
    else:
        paths = list(ROOT.rglob('*.md'))

    for p in sorted(paths):
        if any(part in ('site', 'webdocs', '.venv', 'scripts', '.git') for part in p.parts):
            continue
        if fix_file(p):
            changed += 1
            print(f'fixed: {p.relative_to(ROOT)}')

    print(f'\n{changed} files updated')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
