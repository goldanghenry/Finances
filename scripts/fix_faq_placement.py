#!/usr/bin/env python3
"""Move **Q. 실무에서는?** into §10 (before ## 11)."""

from __future__ import annotations

import re
import sys

from _corpus import iter_corpus_md

FAQ = re.compile(
    r"\n\*\*Q\. 실무에서는\?\*\*\s+\n[^\n]+\n+",
    re.M,
)
INSERT = (
    "\n**Q. 실무에서는?**  \n"
    "교과서 식·기호를 그대로 적용하기 전에 **수수료·세금·데이터 시점**을 분리한다. "
    "숫자는 [DEPTH-STANDARD](../docs/DEPTH-STANDARD.md)처럼 기호만 먼저 맞추고, "
    "법령·시장 수치는 §8 표·외부 출처로 갱신한다.\n\n"
)


def fix(text: str) -> tuple[str, bool]:
    if not re.search(r"^## 10[\.\s]", text, re.M):
        return text, False
    text = FAQ.sub("\n", text)
    m = re.search(r"^## 10[\.\s]", text, re.M)
    tail = text[m.start() :]
    m_end = re.search(r"^## (?:11|L3 보충)", tail, re.M)
    chunk = tail[: m_end.start()] if m_end else tail
    if re.search(r"실무에서는|실무에선|실무 적용", chunk):
        return text, FAQ.search(text) is None
    if not m_end:
        return text.rstrip() + INSERT, True
    pos = m.start() + m_end.start()
    return text[:pos] + INSERT + text[pos:], True


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, changed = fix(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
    print(f"Fixed FAQ placement in {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
