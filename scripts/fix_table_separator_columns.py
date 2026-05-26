#!/usr/bin/env python3
"""Fix Markdown table separator rows whose column count mismatches the header."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import iter_corpus_md
from lint_corpus_quality import split_table_row

WRONG_3COL_SEP = "|------|------|----------------|"
ORPHAN_HEADER = re.compile(
    r"^\|\s*이름\s*\|\s*이 식에서 의미\s*\|\s*§4 용어·식 맥락에서 확인\s*\|\s*$"
)
VAR_HEADER_PREFIX = "| 기호 | 이름 | 이 식에서 의미 |"


def is_separator_line(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r"-+", c.replace(" ", "")) for c in cells)


def separator_for(ncol: int) -> str:
    if ncol == 3:
        return WRONG_3COL_SEP
    parts = ["------"] * ncol
    if ncol > 3:
        parts[-1] = "----------------"
    return "|" + "|".join(parts) + "|"


def remove_orphan_headers(lines: list[str]) -> int:
    """Drop duplicate §6 header row immediately before the real variable table."""
    changed = 0
    i = 0
    while i < len(lines):
        if ORPHAN_HEADER.match(lines[i].strip()):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].strip().startswith(VAR_HEADER_PREFIX):
                del lines[i]
                changed += 1
                if i > 0 and not lines[i - 1].strip():
                    del lines[i - 1]
                    changed += 1
                continue
        i += 1
    return changed


def prev_table_row_index(lines: list[str], i: int) -> int | None:
    j = i - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    if j >= 0 and lines[j].strip().startswith("|"):
        return j
    return None


def insert_missing_separators(lines: list[str]) -> int:
    """Insert a separator only when it is the first row of a pipe-table block."""
    changed = 0
    i = 0
    in_code = False
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code or not s.startswith("|") or is_separator_line(lines[i]):
            i += 1
            continue
        if prev_table_row_index(lines, i) is not None:
            i += 1
            continue
        if i + 1 >= len(lines):
            i += 1
            continue
        nxt = lines[i + 1].strip()
        if not nxt.startswith("|") or is_separator_line(lines[i + 1]):
            i += 1
            continue
        if ORPHAN_HEADER.match(s):
            i += 1
            continue
        ncol = len(split_table_row(lines[i]))
        if ncol < 2:
            i += 1
            continue
        lines.insert(i + 1, separator_for(ncol))
        changed += 1
        i += 2
    return changed


def fix_orphan_leading_separators(lines: list[str]) -> int:
    """Separator row with no header above — insert header from data column count."""
    changed = 0
    i = 0
    in_code = False
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code or not is_separator_line(lines[i]):
            i += 1
            continue
        prev = prev_table_row_index(lines, i)
        if prev is not None and not is_separator_line(lines[prev]):
            i += 1
            continue
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines) or not lines[j].strip().startswith("|"):
            i += 1
            continue
        ncol = len(split_table_row(lines[j]))
        if ncol < 2:
            i += 1
            continue
        first_cell = split_table_row(lines[j])[0]
        if re.search(r"\\?\(?\\?(PV|WACC|OCF|NPV|IRR|r|n|M|P)\b", first_cell):
            header = VAR_HEADER_PREFIX
        elif ncol == 2:
            header = "| 항목 | 내용 |"
        else:
            header = "| " + " | ".join([f"열{n + 1}" for n in range(ncol)]) + " |"
        lines[i] = header
        lines.insert(i + 1, separator_for(ncol))
        changed += 2
        i += 2
    return changed


def fix_merged_table_after_prose(lines: list[str]) -> int:
    """Unstick '| table' glued to end of a prose line (common enrich glitch)."""
    changed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.search(r"\.(\|)", line)
        if not m or line.strip().startswith("|"):
            i += 1
            continue
        split_at = m.start(1)
        head, tail = line[:split_at].rstrip(), line[split_at:].lstrip()
        if not tail.startswith("|"):
            i += 1
            continue
        lines[i] = head
        lines.insert(i + 1, "")
        lines.insert(i + 2, tail)
        changed += 1
        i += 3
    return changed


def fix_separator_widths(lines: list[str]) -> int:
    changed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip().startswith("|") or is_separator_line(line):
            i += 1
            continue
        ncol = len(split_table_row(line))
        if ncol < 1 or i + 1 >= len(lines):
            i += 1
            continue
        nxt = lines[i + 1]
        if not is_separator_line(nxt):
            i += 1
            continue
        sep_ncol = len(split_table_row(nxt))
        if sep_ncol == ncol:
            i += 1
            continue
        lines[i + 1] = separator_for(ncol)
        changed += 1
        i += 2
    return changed


def fix_file(text: str) -> tuple[str, int]:
    lines = text.splitlines()
    changed = fix_merged_table_after_prose(lines)
    changed += remove_orphan_headers(lines)
    changed += fix_orphan_leading_separators(lines)
    changed += insert_missing_separators(lines)
    changed += fix_separator_widths(lines)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), changed


def main() -> int:
    total = 0
    files = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, n = fix_file(text)
        if n:
            path.write_text(new_text, encoding="utf-8")
            print(f"{path.name}: {n} separator(s)")
            total += n
            files += 1
    print(f"\nFixed {total} separator(s) in {files} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
