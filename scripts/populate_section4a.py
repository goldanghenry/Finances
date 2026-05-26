#!/usr/bin/env python3
"""Fill §4a stub rows from §4 terminology table (when present)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"scripts", ".tmp_l3", "site", "webdocs", ".venv", "private", ".git", ".github", "docs", "references"}

STUB_LINE = re.compile(
    r"^\| \(본문 표 참고\) \| — \| — \| \[glossary\]\([^)]+\) \|\s*$",
    re.M,
)

TABLE4_PATTERNS = [
    re.compile(
        r"^## 4\.[^\n]*\n+?\| 용어 \| English \| 정의 \|\n\|[-| ]+\|\n((?:\|[^\n]+\|\n)+)",
        re.M,
    ),
    re.compile(
        r"^## 4\.[^\n]*\n+?\| 용어 \| 한글 \| English \| 정의 \|\n\|[-| ]+\|\n((?:\|[^\n]+\|\n)+)",
        re.M,
    ),
    re.compile(
        r"^## 4\.[^\n]*\n+?\| 용어 \| 정의 \|\n\|[-| ]+\|\n((?:\|[^\n]+\|\n)+)",
        re.M,
    ),
    re.compile(
        r"^## 4\.[^\n]*\n+?\| 약어 \| English \| 정의 \|\n\|[-| ]+\|\n((?:\|[^\n]+\|\n)+)",
        re.M,
    ),
    re.compile(
        r"^(## 4\.[^\n]*\n+)((?:\|[^\n]+\|\n)+\s*)(?=### 4a\.)",
        re.M,
    ),
    re.compile(
        r"^## 4\.[^\n]*\n+?\| 용어 \| 섹터 \|[^\n]+\n\|[-| ]+\|\n((?:\|[^\n]+\|\n)+)",
        re.M,
    ),
]


def glossary_link(path: Path) -> str:
    rel = path.resolve().relative_to(ROOT.resolve())
    depth = len(rel.parents) - 1
    return "../" * depth + "00-roadmap/glossary.md"


def find_table4(text: str) -> re.Match[str] | None:
    for pat in TABLE4_PATTERNS:
        m = pat.search(text)
        if m:
            if m.lastindex and m.lastindex >= 2:
                # Generic §4 block: group 2 is table body
                class _Wrap:
                    def __init__(self, body: str):
                        self._body = body

                    def group(self, n: int) -> str:
                        return self._body if n == 1 else ""

                return _Wrap(m.group(2))  # type: ignore[return-value]
            return m
    return None


def rows_from_table(block: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in block.strip().splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in ("용어", "------"):
            continue
        if len(cells) >= 4:
            term, ko, eng, definition = cells[0], cells[1], cells[2], cells[3]
            short = ko if ko and not ko.startswith("\\") else eng
            if not short or short.startswith("\\"):
                short = definition
        elif len(cells) == 2:
            term, definition = cells[0], cells[1]
            short = definition
        else:
            term, _eng, definition = cells[0], cells[1], cells[2]
            short = definition
        if term.startswith("("):
            continue
        short = short.split("—")[0].split("(")[0].strip()
        short = re.sub(r"\\[a-zA-Z_{}\s\d^().]+", "", short).strip()
        if not short or short in {"|", "—"}:
            short = definition.replace("|", " ").replace("\\", "")[:48].strip()
        if len(short) > 72:
            short = short[:69] + "…"
        rows.append((term, short, "§4"))
    return rows[:15]


def build_4a(rows: list[tuple[str, str, str]], gloss: str) -> str:
    lines = [
        "### 4a. 핵심 용어 (본문 등장 순)",
        "",
        "> 복습용. 정의는 §4 본표·[glossary](" + gloss + ")·본문 `!!! info` 박스.",
        "",
        "| 용어 | 한 줄 | 관련 이론 | glossary |",
        "|------|-------|-----------|----------|",
    ]
    for term, short, theory in rows:
        anchor = term.split("(")[0].strip().replace(" ", "-").lower()
        lines.append(f"| {term} | {short} | {theory} | [glossary]({gloss}#{anchor}) |")
    return "\n".join(lines) + "\n\n"


def process(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if not STUB_LINE.search(text):
        return False
    m4 = find_table4(text)
    if not m4:
        return False
    rows = rows_from_table(m4.group(1))
    if len(rows) < 3:
        return False
    gloss = glossary_link(path)
    new_4a = build_4a(rows, gloss)
    block_re = re.compile(
        r"### 4a\. 핵심 용어 \(본문 등장 순\)\n\n>[^\n]+\n\n\| 용어 \|[^\n]+\n\|[-| ]+\|\n(?:\|[^\n]+\|\n)+",
        re.M,
    )
    if not block_re.search(text):
        return False
    new_text = block_re.sub(new_4a.rstrip() + "\n", text, count=1)
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    count = 0
    for path in sorted(ROOT.rglob("*.md")):
        if any(p in SKIP for p in path.parts):
            continue
        if process(path):
            count += 1
            print(path.relative_to(ROOT))
    print(f"Updated §4a in {count} files")


if __name__ == "__main__":
    main()
