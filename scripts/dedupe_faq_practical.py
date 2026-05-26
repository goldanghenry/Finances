#!/usr/bin/env python3
"""Remove duplicate **Q. 실무에서는?** blocks; keep first in §10."""

from __future__ import annotations

import re
import sys

from _corpus import iter_corpus_md

BLOCK = re.compile(
    r"\n\*\*Q\. 실무에서는\?\*\*\s+\n[^\n]+\n",
    re.M,
)


def dedupe(text: str) -> tuple[str, bool]:
    matches = list(BLOCK.finditer(text))
    if len(matches) <= 1:
        return text, False
    # keep first only
    new = text
    for m in reversed(matches[1:]):
        new = new[: m.start()] + new[m.end() :]
    return new, True


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, changed = dedupe(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
    print(f"Deduped FAQ in {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
