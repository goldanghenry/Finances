#!/usr/bin/env python3
"""Re-fill §4a when rows are stub or broken (LaTeX stripped to empty)."""

from __future__ import annotations

from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from populate_section4a import STUB_LINE, build_4a, find_table4, glossary_link, rows_from_table
SKIP = {"scripts", ".tmp_l3", "site", "webdocs", ".venv", "private", ".git", ".github", "docs", "references"}


def needs_repair(text: str) -> bool:
    if STUB_LINE.search(text):
        return True
    return bool(
        __import__("re").search(
            r"^### 4a\.[\s\S]+?\| [^|]+ \| \\ \|",
            text,
            __import__("re").M,
        )
    )


def process(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if not needs_repair(text):
        return False
    m4 = find_table4(text)
    if not m4:
        return False
    rows = rows_from_table(m4.group(1))
    if len(rows) < 3:
        return False
    import re

    new_4a = build_4a(rows, glossary_link(path))
    block_re = re.compile(
        r"### 4a\. 핵심 용어 \(본문 등장 순\)\n\n>[^\n]+\n\n\| 용어 \|[^\n]+\n\|[-| ]+\|\n(?:\|[^\n]+\|\n)+",
        re.M,
    )
    if not block_re.search(text):
        return False
    path.write_text(block_re.sub(new_4a.rstrip() + "\n", text, count=1), encoding="utf-8")
    return True


def main() -> None:
    n = 0
    for path in sorted(ROOT.rglob("*.md")):
        if any(p in SKIP for p in path.parts):
            continue
        if process(path):
            n += 1
    print(f"Repaired §4a in {n} files")


if __name__ == "__main__":
    main()
