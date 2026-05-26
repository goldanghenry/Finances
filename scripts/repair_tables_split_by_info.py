#!/usr/bin/env python3
"""Move !!! info blocks out from between markdown table header and body rows."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"scripts", "site", "webdocs", ".venv", "private", ".git", ".github", "docs", "references"}

# | header | ... |\n| --- |\n\n!!! info ...\n\n| row |
BROKEN = re.compile(
    r"(\|[^\n]+\n\|[-: |]+\|\n)\n+((?:!!! info[^\n]+\n(?:    [^\n]+\n)+\n+)+)(\|[^\n]+\n)",
    re.M,
)


def repair(text: str) -> tuple[str, bool]:
    def repl(m: re.Match[str]) -> str:
        header = m.group(1)
        boxes = m.group(2)
        first_row = m.group(3)
        return f"{boxes}{header}{first_row}"

    new_text, n = BROKEN.subn(repl, text)
    return new_text, n > 0


def main() -> int:
    fixed = 0
    for path in sorted(ROOT.rglob("*.md")):
        if any(p in SKIP for p in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        new_text, changed = repair(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            fixed += 1
            print(path.relative_to(ROOT))
    print(f"Repaired {fixed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
