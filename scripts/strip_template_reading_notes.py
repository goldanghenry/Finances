#!/usr/bin/env python3
"""Remove template §6 reading notes; leave GOLD_READING markers for manual fill."""

from __future__ import annotations

import hashlib
import re
import sys

from _corpus import ROOT, iter_corpus_md
from _gold_polish import TEMPLATE_READING, section6_body

MARKER = "<!-- GOLD_READING: {hash} -->"


def strip(text: str) -> tuple[str, bool]:
    if TEMPLATE_READING not in text:
        return text, False
    changed = False

    def repl(m: re.Match[str]) -> str:
        nonlocal changed
        line = m.group(0)
        if TEMPLATE_READING not in line:
            return line
        changed = True
        # find nearest equation above
        before = text[: m.start()]
        eq_m = list(re.finditer(r"\\\[\s*\n[\s\S]*?\\\]\s*\n", before))
        h = "none"
        if eq_m:
            eq = eq_m[-1].group(0)
            h = hashlib.sha256(eq.encode()).hexdigest()[:10]
        return MARKER.format(hash=h) + "\n"

    new_text = re.sub(
        r"\n\*\*읽는 법\*\*:[^\n]*" + re.escape(TEMPLATE_READING) + r"[^\n]*\n",
        repl,
        text,
    )
    if not changed:
        new_text = text.replace(
            "**읽는 법**: 위 식의 기호는 바로 위 변수표와 같다. "
            "숫자는 [DEPTH-STANDARD](../docs/DEPTH-STANDARD.md) 교육용 기호(M·P·PV 등)로 대입한다.\n",
            "",
        )
        changed = new_text != text
    return new_text, changed


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, changed = strip(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
    print(f"Stripped template reading notes in {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
