#!/usr/bin/env python3
"""Add short '읽는 법' after display math in §6 when missing."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import ROOT, iter_corpus_md

NOTE = "\n**읽는 법**: 위 식의 기호는 바로 위 변수표와 같다. 숫자는 [DEPTH-STANDARD](../docs/DEPTH-STANDARD.md) 교육용 기호(M·P·PV 등)로 대입한다.\n"


def enrich(text: str) -> tuple[str, bool]:
    m6 = re.search(r"^## 6[\.\s]", text, re.M)
    if not m6:
        return text, False
    tail = text[m6.start() :]
    m_end = re.search(r"^## [^6]", tail[10:], re.M)
    section6 = tail[: m_end.start() + 10] if m_end else tail
    if "해당 없음" in section6[:300]:
        return text, False

    changed = False
    new_s6 = section6
    pos = 0
    while True:
        m = re.search(r"\\\]\s*\n", new_s6[pos:])
        if not m:
            break
        end = pos + m.end()
        after = new_s6[end : end + 120]
        if "읽는 법" in after or after.strip().startswith("|"):
            pos = end
            continue
        if after.strip().startswith("```"):
            pos = end
            continue
        new_s6 = new_s6[:end] + NOTE + new_s6[end:]
        changed = True
        pos = end + len(NOTE)

    if changed:
        text = text[: m6.start()] + new_s6 + text[m6.start() + len(section6) :]
    return text, changed


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, changed = enrich(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
    print(f"Added §6 reading notes in {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
