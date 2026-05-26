#!/usr/bin/env python3
"""Insert variable legend before first display math in ## 6 if missing."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"scripts", ".tmp_l3", "site", "webdocs", ".venv", "private", ".git", ".github", "docs", "references"}

GENERIC_TABLE = """
| 기호 | 이름 | 이 식에서 의미 |
|------|------|----------------|
| (아래 식 참고) | — | §4 본표·§0 기호 열 확인 |

"""


def process(text: str) -> str:
    m = re.search(r"^## 6[\.\s].*$", text, re.M)
    if not m:
        return text
    rest = text[m.end() :]
    chunk = rest[:1200]
    if "기호" in chunk and "이 식에서" in chunk:
        return text
    if "해당 없음" in chunk[:300]:
        return text
    dm = re.search(r"\\\[\s*\n", rest)
    if not dm:
        return text
    pos = m.end() + dm.start()
    return text[:pos] + GENERIC_TABLE + text[pos:]


def main() -> None:
    n = 0
    for path in sorted(ROOT.rglob("*.md")):
        if any(p in SKIP for p in path.parts) or path.name == "README.md":
            continue
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            continue
        if rel.parts[0] not in {
            "01-foundations",
            "02-economics",
            "03-markets",
            "04-portfolio",
            "05-behavioral",
            "06-korea-policy",
            "07-real-estate",
            "08-advanced",
            "09-corporate-finance",
            "00-roadmap",
        }:
            continue
        text = path.read_text(encoding="utf-8")
        if "## 6" not in text:
            continue
        new = process(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            n += 1
    print(f"Enhanced §6 tables in {n} files")


if __name__ == "__main__":
    main()
