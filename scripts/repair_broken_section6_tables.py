#!/usr/bin/env python3
"""Repair common §6 table corruption (broken separators, split reading notes)."""

from __future__ import annotations

import re
import sys

from _corpus import iter_corpus_md
from _gold_polish import TEMPLATE_READING_FULL, strip_template_reading_global

BAD_SEP = re.compile(
    r"^\|\s*------\s*\|\s*------\s*\|\s*------이\(가\) 이 식에서 맡는 역할.*\|\s*$",
    re.M,
)
GOOD_SEP = "|------|------|----------------|"


def repair(text: str) -> tuple[str, bool]:
    changed = False
    t, c = strip_template_reading_global(text)
    if c:
        text, changed = t, True
    if BAD_SEP.search(text):
        text = BAD_SEP.sub(GOOD_SEP, text)
        changed = True
    # Remove orphan fragments from mangled reading notes
    frag = re.sub(
        r"\n\.\s*숫자는 \[DEPTH-STANDARD\][^\n]+\n",
        "\n",
        text,
    )
    if frag != text:
        text = frag
        changed = True
    text2 = re.sub(
        r"\*\*읽는 법\*\*:[^\n]*\| 기호 \| 이름 \| 이 식에서 의미 \|[\s\S]*?로 위 변수표와 같다\.[^\n]*\n",
        "\n",
        text,
    )
    if text2 != text:
        text = text2
        changed = True
    return text, changed


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, changed = repair(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
    print(f"Repaired §6 table corruption in {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
