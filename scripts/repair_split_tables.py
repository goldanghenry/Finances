#!/usr/bin/env python3
"""Merge table rows orphaned after admonitions into the preceding table."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import ROOT, iter_corpus_md


def repair_split_tables(text: str) -> tuple[str, bool]:
    lines = text.splitlines()
    changed = False
    i = 0
    while i < len(lines):
        if not lines[i].strip().startswith("|") or "---" in lines[i]:
            i += 1
            continue
        # Found table header row
        header_cols = len(lines[i].strip().strip("|").split("|"))
        j = i + 1
        if j < len(lines) and re.match(r"^\|[\s\-:|]+\|$", lines[j].strip()):
            j += 1
        # Collect data rows until break
        data_end = j
        while data_end < len(lines) and lines[data_end].strip().startswith("|"):
            if "---" in lines[data_end]:
                break
            data_end += 1
        # Look for admonition then orphan rows with same col count
        k = data_end
        while k < len(lines):
            if lines[k].strip() == "":
                k += 1
                continue
            if lines[k].startswith("!!! "):
                ad_end = k + 1
                while ad_end < len(lines) and not lines[ad_end].startswith("!!! ") and not lines[ad_end].startswith("##"):
                    if lines[ad_end].strip().startswith("|"):
                        break
                    ad_end += 1
                orphans: list[str] = []
                while ad_end < len(lines) and lines[ad_end].strip().startswith("|"):
                    if "---" in lines[ad_end]:
                        break
                    cols = len(lines[ad_end].strip().strip("|").split("|"))
                    if cols == header_cols:
                        orphans.append(lines[ad_end])
                        ad_end += 1
                    else:
                        break
                if orphans:
                    changed = True
                    lines = lines[:data_end] + orphans + lines[ad_end:]
                    data_end = data_end + len(orphans)
                    k = data_end
                    continue
                k = ad_end
                continue
            break
        i = data_end if data_end > i else i + 1
    return "\n".join(lines), changed


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, changed = repair_split_tables(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
            print(path.relative_to(ROOT))
    print(f"Fixed split tables in {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
