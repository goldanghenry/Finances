#!/usr/bin/env python3
"""Convert HTML <details> quiz hints to ??? note admonitions (arithmatex-safe)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"scripts", "site", "webdocs", ".venv", "private", ".git", ".github"}

DETAILS_RE = re.compile(
    r"<details>\s*\n<summary>(.*?)</summary>\s*\n(?:<div markdown=\"1\">\s*\n)?(.*?)(?:\n</div>)?\s*\n</details>",
    re.DOTALL,
)


def to_note(match: re.Match[str]) -> str:
    title = match.group(1).strip()
    body = match.group(2).strip()
    if not body:
        return match.group(0)
    indented = "\n".join("    " + line for line in body.splitlines())
    return f'??? note "{title}"\n\n{indented}\n'


def process(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "<details>" not in text:
        return False
    new_text, n = DETAILS_RE.subn(to_note, text)
    if n == 0:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    count = 0
    for path in sorted(ROOT.rglob("*.md")):
        if any(p in SKIP for p in path.parts):
            continue
        if process(path):
            count += 1
    print(f"Converted <details> → ??? note in {count} files")


if __name__ == "__main__":
    main()
