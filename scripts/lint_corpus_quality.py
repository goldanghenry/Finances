#!/usr/bin/env python3
"""Fail on broken tables, admonitions, §6 placeholders, and display math in corpus."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import ROOT, iter_corpus_md

PLACEHOLDER = "§4·본문 정의 참고"
L3_MIN = 10_000
L4_MIN = 18_000


def split_table_row(line: str) -> list[str]:
    body = line.strip().strip("|")
    cells: list[str] = []
    current: list[str] = []
    i = 0
    in_math = False
    while i < len(body):
        if body[i : i + 2] == "\\(":
            in_math = True
            current.append(body[i])
            current.append(body[i + 1])
            i += 2
            continue
        if body[i : i + 2] == "\\)" and in_math:
            in_math = False
            current.append(body[i])
            current.append(body[i + 1])
            i += 2
            continue
        if body[i] == "|" and not in_math:
            if i > 0 and body[i - 1] == "\\":
                current.append(body[i])
                i += 1
                continue
            cells.append("".join(current).strip())
            current = []
            i += 1
            continue
        current.append(body[i])
        i += 1
    cells.append("".join(current).strip())
    return cells


def split_table_blocks(text: str) -> list[list[tuple[int, list[str]]]]:
    """Contiguous pipe-table blocks; break on blank line, heading, or admonition."""
    blocks: list[list[tuple[int, list[str]]]] = []
    current: list[tuple[int, list[str]]] = []
    in_code = False
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            if current:
                blocks.append(current)
                current = []
            continue
        if in_code:
            continue
        if stripped.startswith("!!! ") or stripped.startswith("## ") or stripped.startswith("# "):
            if current:
                blocks.append(current)
                current = []
            continue
        if not stripped.startswith("|"):
            if current:
                blocks.append(current)
                current = []
            continue
        cells = split_table_row(line)
        if all(re.fullmatch(r"-+", c.replace(" ", "")) for c in cells if c):
            continue
        current.append((i, cells))
    if current:
        blocks.append(current)
    return blocks


def is_separator_line(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r"-+", c.replace(" ", "")) for c in cells)


def check_tables(text: str) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        if not line.strip().startswith("|") or is_separator_line(line):
            continue
        ncol = len(split_table_row(line))
        if ncol < 1 or i >= len(lines):
            continue
        nxt = lines[i]
        if not nxt.strip().startswith("|") or not is_separator_line(nxt):
            continue
        sep_ncol = len(split_table_row(nxt))
        if sep_ncol != ncol:
            issues.append(
                f"line {i + 1}: separator has {sep_ncol} columns, header has {ncol}"
            )
    for block in split_table_blocks(text):
        if len(block) < 2:
            continue
        widths = {len(cells) for _, cells in block}
        if len(widths) > 1:
            issues.append(f"line {block[0][0]}: table column count mismatch ({widths})")
        for lineno, cells in block:
            for j, cell in enumerate(cells):
                if cell in ("\\",):
                    issues.append(f"line {lineno}: broken table cell in column {j + 1}")
    return issues


def check_admonitions(text: str) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.startswith("!!! "):
            i += 1
            continue
        body_lines: list[str] = []
        j = i + 1
        while j < len(lines):
            nxt = lines[j]
            if nxt.startswith("!!! "):
                break
            if re.match(r"^##+ ", nxt):
                break
            if nxt.strip() and not nxt.startswith("    ") and not nxt.startswith("\t"):
                break
            body_lines.append(nxt)
            j += 1
        content = "\n".join(body_lines).strip()
        if not content:
            issues.append(f"line {i + 1}: empty admonition body")
        elif any(bl.strip().startswith("|") for bl in body_lines):
            issues.append(f"line {i + 1}: table row inside admonition")
        i = j if j > i else i + 1
    return issues


def section6_body(text: str) -> str:
    m = re.search(r"^## 6[\.\s]", text, re.M)
    if not m:
        return ""
    tail = text[m.start() :]
    m_end = re.search(r"^## [^6]", tail[10:], re.M)
    return tail[: m_end.start() + 10] if m_end else tail


def check_section6(text: str) -> list[str]:
    issues: list[str] = []
    s6 = section6_body(text)
    if not s6 or "해당 없음" in s6[:300]:
        return issues
    if PLACEHOLDER in s6:
        issues.append("§6 contains placeholder '§4·본문 정의 참고'")
    s6_no_code = re.sub(r"```[\s\S]*?```", "", s6)
    if re.search(r"\|\s*\\\s*\|", s6_no_code):
        issues.append("§6 has broken table cell (lone backslash)")
    n_math = len(re.findall(r"\\\[\s*\n", s6_no_code))
    n_tables = s6_no_code.count("이 식에서 의미")
    if n_math > 0 and n_tables < n_math:
        issues.append(
            f"§6 has {n_math} display equation(s) but {n_tables} variable table(s)"
        )
    if re.search(r"\|[^\n]+\|\n\\\[", s6_no_code):
        issues.append("§6 display math glued to table row (need blank line before \\[)")
    return issues


def check_math(text: str) -> list[str]:
    issues: list[str] = []
    if text.count("\\[") != text.count("\\]"):
        issues.append("unbalanced \\[ ... \\]")
    return issues


def difficulty(text: str) -> str | None:
    m = re.search(r"\| 난이도 \|[^\n]*L(\d)", text)
    return m.group(1) if m else None


def check_length(path: Path, text: str) -> list[str]:
    issues: list[str] = []
    d = difficulty(text)
    size = len(text.encode("utf-8"))
    if d == "3" and size < L3_MIN:
        issues.append(f"size {size} < L3 minimum {L3_MIN}")
    if d == "4" and size < L4_MIN:
        issues.append(f"size {size} < L4 minimum {L4_MIN}")
    return issues


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    issues.extend(check_tables(text))
    issues.extend(check_admonitions(text))
    issues.extend(check_section6(text))
    issues.extend(check_math(text))
    issues.extend(check_length(path, text))
    return issues


def main() -> int:
    bad = 0
    for path in iter_corpus_md():
        issues = check_file(path)
        if issues:
            bad += 1
            print(f"{path.relative_to(ROOT)}:")
            for issue in issues:
                print(f"  - {issue}")
    print(f"\n{bad} files with quality issues")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
