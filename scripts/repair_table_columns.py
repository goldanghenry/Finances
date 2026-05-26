#!/usr/bin/env python3
"""Fix obvious 2-column rows in 3-column markdown tables."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import ROOT, iter_corpus_md


def repair_tables(text: str) -> tuple[str, bool]:
    lines = text.splitlines()
    changed = False
    i = 0
    while i < len(lines):
        if not lines[i].strip().startswith("|") or "---" in lines[i]:
            i += 1
            continue
        header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        ncol = len(header)
        if ncol < 3:
            i += 1
            continue
        j = i + 1
        if j < len(lines) and re.match(r"^\|[\s\-:|]+\|$", lines[j].strip()):
            j += 1
        while j < len(lines) and lines[j].strip().startswith("|") and "---" not in lines[j]:
            cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
            if len(cells) == 2 and ncol >= 3:
                # split long second cell at last " | " pattern or append empty third
                second = cells[1]
                if "**적정 대조 필요**" in second and "개별 차이)" in second:
                    idx = second.rfind("개별 차이)")
                    if idx != -1:
                        cells = [cells[0], second[: idx + len("개별 차이)")].strip(), second[idx + len("개별 차이)") :].strip() or "**적정 대조 필요**"]
                        lines[j] = "| " + " | ".join(cells) + " |"
                        changed = True
                else:
                    cells.append("—")
                    lines[j] = "| " + " | ".join(cells) + " |"
                    changed = True
            j += 1
        i = j
    return "\n".join(lines), changed


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new, c = repair_tables(text)
        if c:
            path.write_text(new, encoding="utf-8")
            n += 1
            print(path.relative_to(ROOT))
    print(f"Fixed tables in {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
