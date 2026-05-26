#!/usr/bin/env python3
"""Fix common markdown structure bugs: math inside tables, orphan mermaid, glued prose."""

from __future__ import annotations

import re
import sys

from _corpus import iter_corpus_md

# Table data row immediately followed by display-math opener (invalid in CommonMark).
MATH_AFTER_TABLE = re.compile(r"(\|[^\n]+\|)\n(\\\[)", re.M)

# Orphan mermaid lines between a closed fence and --- / ## (duplicate diagram tail).
ORPHAN_MERMAID_BLOCK = re.compile(
    r"(```\s*\n)\n---\n\n"
    r"((?:[ \t]*(?:Pay|ISA|flowchart|Gen|Pen)[^\n]*\n)+)"
    r"```\s*\n",
    re.M,
)

# **읽는 법** paragraph glued to next sentence (e.g. …맞춘다.상세는)
GLUED_AFTER_READING = re.compile(
    r"(\*\*읽는 법\*\*:[^\n]+?\.\s*)([가-힣\*#\[])",
)

# Template reading glue after DEPTH-STANDARD link (…맞춘다.세율)
GLUED_AFTER_TEMPLATE_READING = re.compile(
    r"(기호 예제를 맞춘다\.)([가-힣\*#\[])",
)

# enrich sometimes splits **읽는 법** and the template tail across blank lines
SPLIT_READING_TAIL = re.compile(
    r"(\*\*읽는 법\*\*:[^\n]+?쓴다\.)\s*\n+\s*(경제·재무 해석은[^\n]+맞춘다\.)",
)

# Stray ``` after orphan mermaid tail (leftover closer)
STRAY_FENCE_AFTER_HR = re.compile(
    r"(---\n\n(?:[ \t]*(?:Pay|ISA|Gen|Pen)-->[^\n]*\n)+)```\s*\n",
    re.M,
)

# §6 variable table: | \(PV\) | → | **PV** | (MkDocs tables often hide inline math)
VAR_TABLE_INLINE_SYM = re.compile(
    r"^\| \\\(([^\\)\n]{1,24})\\\) \|",
    re.M,
)

# Footnote clash when display math is misparsed as a table row: (1+r)^n
DISPLAY_EXPONENT = re.compile(
    r"(\(1\s*\+\s*r\))\^n\b",
)


def normalize_var_table_symbols(text: str) -> tuple[str, int]:
    changes = 0

    def repl(m: re.Match[str]) -> str:
        sym = m.group(1).strip()
        if "_" in sym or "{" in sym or "\\" in sym:
            return m.group(0)
        return f"| **{sym}** |"

    new = VAR_TABLE_INLINE_SYM.sub(repl, text)
    if new != text:
        changes += len(VAR_TABLE_INLINE_SYM.findall(text))
        text = new
    return text, changes


def brace_display_exponents(text: str) -> tuple[str, int]:
    n = len(DISPLAY_EXPONENT.findall(text))
    if not n:
        return text, 0
    return DISPLAY_EXPONENT.sub(r"\1^{n}", text), n


def fix_text(text: str) -> tuple[str, int]:
    changes = 0
    new = MATH_AFTER_TABLE.sub(r"\1\n\n\\[", text)
    if new != text:
        changes += len(MATH_AFTER_TABLE.findall(text))
        text = new

    new = ORPHAN_MERMAID_BLOCK.sub(r"\1\n---\n\n", text)
    if new != text:
        changes += 1
        text = new

    new = STRAY_FENCE_AFTER_HR.sub("", text)
    if new != text:
        changes += 1
        text = new

    new = GLUED_AFTER_READING.sub(r"\1\n\n\2", text)
    if new != text:
        changes += len(GLUED_AFTER_READING.findall(text))
        text = new

    new = GLUED_AFTER_TEMPLATE_READING.sub(r"\1\n\n\2", text)
    if new != text:
        changes += len(GLUED_AFTER_TEMPLATE_READING.findall(text))
        text = new

    new = SPLIT_READING_TAIL.sub(r"\1 \2", text)
    if new != text:
        changes += len(SPLIT_READING_TAIL.findall(text))
        text = new

    text, n_sym = normalize_var_table_symbols(text)
    changes += n_sym

    text, n_exp = brace_display_exponents(text)
    changes += n_exp

    return text, changes


def main() -> int:
    total = 0
    files = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, n = fix_text(text)
        if n:
            path.write_text(new_text, encoding="utf-8")
            print(f"{path.name}: {n}")
            total += n
            files += 1
    print(f"\nFixed structure in {files} files ({total} operations)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
