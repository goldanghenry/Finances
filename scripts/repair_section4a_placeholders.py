#!/usr/bin/env python3
"""Fix §4a rows with lone backslash in '한 줄' column."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import ROOT, iter_corpus_md

FALLBACK: dict[str, str] = {
    "Sharpe": "(Rp−Rf)/σp",
    "Sortino": "(Rp−Rf)/하방σ",
    "Treynor": "(Rp−Rf)/β",
    "TE": "추적오차 σ",
    "IR": "초과/TE",
    "초과수익": "벤치마크 대비 초과",
    "β": "시장 민감도",
}


def repair(text: str) -> tuple[str, bool]:
    changed = False

    def repl(m: re.Match[str]) -> str:
        nonlocal changed
        term, val = m.group(1), m.group(2).strip()
        if val != "\\":
            return m.group(0)
        changed = True
        fix = FALLBACK.get(term, FALLBACK.get(term.strip(), "§4 본표 참고"))
        return f"| {term} | {fix} |"

    new = re.sub(
        r"^\| ([^|]+) \| \\ \|",
        repl,
        text,
        flags=re.M,
    )
    return new, changed


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new, c = repair(text)
        if c:
            path.write_text(new, encoding="utf-8")
            n += 1
            print(path.relative_to(ROOT))
    print(f"Fixed §4a placeholders in {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
