#!/usr/bin/env python3
"""Batch polish corpus chapters toward gold standard (G1–G9)."""

from __future__ import annotations

import sys

from _corpus import iter_corpus_md
from _gold_polish import polish_file


def main() -> int:
    paths = iter_corpus_md()
    if len(sys.argv) > 1:
        from pathlib import Path
        from _corpus import ROOT

        paths = [ROOT / p if not Path(p).is_absolute() else Path(p) for p in sys.argv[1:]]
    n = 0
    for path in paths:
        text = path.read_text(encoding="utf-8")
        new_text, changed = polish_file(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
            print(path.relative_to(path.parents[2] if len(path.parents) > 2 else path.parent))
    print(f"Polished {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
