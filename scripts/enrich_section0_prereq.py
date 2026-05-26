#!/usr/bin/env python3
"""Replace §0 선수 placeholder with links from ## 2 선수 block."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import ROOT, iter_corpus_md

PLACEHOLDER = "§2 선수 문서 참고"
SECTION0_PREREQ = re.compile(
    r"(\| \*\*선수\*\* \| )([^|]+)( \|)",
)
SECTION2 = re.compile(r"^## 2\.[^\n]*\n", re.M)
PREREQ_BLOCK = re.compile(
    r"\*\*선수\*\*:\s*\n((?:- \[[^\]]+\]\([^)]+\)[^\n]*\n)+)",
    re.M,
)
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def extract_prereq_links(text: str) -> list[str]:
    m2 = SECTION2.search(text)
    if not m2:
        return []
    rest = text[m2.end() :]
    nxt = re.search(r"^## [^2]", rest, re.M)
    block = rest[: nxt.start()] if nxt else rest
    pm = PREREQ_BLOCK.search(block)
    if not pm:
        return []
    links: list[str] = []
    for label, href in LINK_RE.findall(pm.group(1)):
        label = label.replace(".md", "").strip()
        links.append(f"[{label}]({href})")
    return links[:2]


def process(text: str, path: Path) -> str:
    if PLACEHOLDER not in text:
        return text
    if path.name == "compound-interest-and-time-value.md":
        return text
    links = extract_prereq_links(text)
    if not links:
        if path.name == "cash-flow-basics.md":
            links = ["[compound-interest-and-time-value](compound-interest-and-time-value.md)"]
        else:
            links_str = "없음"
            return SECTION0_PREREQ.sub(rf"\1{links_str}\3", text, count=1)
    links_str = ", ".join(links)
    return SECTION0_PREREQ.sub(rf"\1{links_str}\3", text, count=1)


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new = process(text, path)
        if new != text:
            path.write_text(new, encoding="utf-8")
            n += 1
    print(f"Updated §0 선수 in {n} files")
    remaining = sum(
        1 for p in iter_corpus_md() if PLACEHOLDER in p.read_text(encoding="utf-8")
    )
    print(f"Remaining placeholder: {remaining}")
    return 1 if remaining else 0


if __name__ == "__main__":
    sys.exit(main())
