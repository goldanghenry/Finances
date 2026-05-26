#!/usr/bin/env python3
"""Repair §6 where variable tables and separators intrude into prose and display math."""

from __future__ import annotations

import re
import sys

from _corpus import iter_corpus_md
from lint_corpus_quality import split_table_row

VAR_HDR = "| 기호 | 이름 | 이 식에서 의미 |"
VAR_SEP = "|------|------|----------------|"
ORPHAN_NAME_HDR = re.compile(
    r"^\|\s*이름\s*\|\s*이 식에서 의미\s*\|\s*§4 용어·식 맥락에서 확인\s*\|\s*$"
)
PLACEHOLDER_ROW = re.compile(r"§4 용어·식 맥락에서 확인")
JUNK_ROW = re.compile(
    r"^\|\s*\\?\(?\\?(alpha|cdot|text|월|연금|일반)\b", re.I
)


def is_sep_line(line: str) -> bool:
    s = line.strip()
    if not s.startswith("|"):
        return False
    cells = [c.strip() for c in s.strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r"-+", c.replace(" ", "")) for c in cells if c)


def is_table_line(line: str) -> bool:
    return line.strip().startswith("|")


def clean_display_math(text: str) -> str:
    """Drop pipe-table lines inside \\[ ... \\] blocks."""

    def repl_block(m: re.Match[str]) -> str:
        body = m.group(1)
        kept: list[str] = []
        for ln in body.splitlines():
            s = ln.strip()
            if not s:
                continue
            if is_table_line(ln) or "기호" in s and "이름" in s and "의미" in s:
                continue
            if is_sep_line(ln):
                continue
            kept.append(ln)
        if not kept:
            return ""
        return "\\[\n" + "\n".join(kept) + "\n\\]"

    return re.sub(r"\\\[\s*\n([\s\S]*?)\\\]", repl_block, text)


def remove_orphan_name_headers(lines: list[str]) -> int:
    n = 0
    out: list[str] = []
    for ln in lines:
        if ORPHAN_NAME_HDR.match(ln.strip()):
            n += 1
            continue
        out.append(ln)
    lines[:] = out
    return n


def remove_placeholder_rows(lines: list[str]) -> int:
    n = 0
    out: list[str] = []
    for ln in lines:
        if PLACEHOLDER_ROW.search(ln) and is_table_line(ln):
            n += 1
            continue
        if JUNK_ROW.match(ln.strip()):
            n += 1
            continue
        out.append(ln)
    lines[:] = out
    return n


def is_table_data_row(line: str) -> bool:
    if not is_table_line(line) or is_sep_line(line):
        return False
    if line.strip() == VAR_HDR:
        return False
    first = split_table_row(line)[0].strip() if split_table_row(line) else ""
    if first in (
        "기호",
        "Bucket",
        "항목",
        "용어",
        "열1",
        "이름",
        "단계",
        "분기",
        "충격",
        "헤드라인",
        "헤드라인 (예)",
    ):
        return False
    return True


def split_hr_glued_to_headings(text: str) -> str:
    """Restore '---\\n\\n## N' when a horizontal rule was merged into a heading."""
    return re.sub(r"^(---+)\s*(#{1,6}\s)", r"\1\n\n\2", text, flags=re.M)


def split_separator_glued_to_heading(lines: list[str]) -> int:
    n = 0
    for i, ln in enumerate(lines):
        m = re.match(r"^(\|.*\|)\s*(#{1,6}\s.+)$", ln.strip())
        if m and is_sep_line(m.group(1)):
            lines[i] = m.group(1)
            lines.insert(i + 1, m.group(2))
            n += 1
    return n


def remove_intratable_separators(lines: list[str]) -> int:
    """Delete duplicate separator rows between two data rows (same table)."""
    n = 0
    i = 0
    while i < len(lines):
        if not is_sep_line(lines[i]):
            i += 1
            continue
        prev = i - 1
        nxt = i + 1
        while prev >= 0 and not lines[prev].strip():
            prev -= 1
        while nxt < len(lines) and not lines[nxt].strip():
            nxt += 1
        if (
            prev >= 0
            and nxt < len(lines)
            and is_table_data_row(lines[prev])
            and is_table_data_row(lines[nxt])
        ):
            del lines[i]
            n += 1
            continue
        i += 1
    return n


def dedupe_consecutive_var_tables(lines: list[str]) -> int:
    """If two variable tables appear back-to-back, keep the second."""
    n = 0
    i = 0
    while i < len(lines):
        if lines[i].strip() != VAR_HDR:
            i += 1
            continue
        j = i + 1
        while j < len(lines) and (
            lines[j].strip() == VAR_SEP
            or is_sep_line(lines[j])
            or (is_table_line(lines[j]) and not lines[j].strip().startswith("###"))
        ):
            j += 1
        if j < len(lines) and lines[j].strip() == VAR_HDR:
            del lines[i:j]
            n += 1
            continue
        i += 1
    return n


def fix_split_headings(lines: list[str]) -> int:
    """### 6. + table junk + '5 Title' -> ### 6.5 Title"""
    n = 0
    i = 0
    while i < len(lines):
        if not re.match(r"^### 6\.\s*$", lines[i].strip()):
            i += 1
            continue
        j = i + 1
        while j < len(lines) and (
            not lines[j].strip()
            or is_table_line(lines[j])
            or is_sep_line(lines[j])
            or ORPHAN_NAME_HDR.match(lines[j].strip())
        ):
            j += 1
        if j < len(lines):
            m = re.match(r"^(\d+)\s+(.+)$", lines[j].strip())
            if m:
                num, title = m.group(1), m.group(2)
                lines[i] = f"### 6.{num} {title}"
                del lines[i + 1 : j + 1]
                n += 1
                continue
        i += 1
    return n


def fix_split_prose(lines: list[str]) -> int:
    """Merge prose split by intruding table rows (e.g. **Net Borr | table | owing**)."""
    n = 0
    i = 0
    while i < len(lines) - 2:
        a = lines[i].rstrip()
        if (
            not a
            or a.startswith("|")
            or is_sep_line(a)
            or a.startswith("#")
            or a.startswith("```")
            or a.startswith("\\")
            or a.startswith("- ")
            or a.startswith("* ")
        ):
            i += 1
            continue
        # incomplete bold/word at end
        if not re.search(r"[\.\?\!:\)]$|\*\*$", a) and not a.endswith("---"):
            j = i + 1
            intruded: list[int] = []
            while j < len(lines) and (
                not lines[j].strip()
                or lines[j].strip().startswith("---")
                or is_table_line(lines[j])
                or is_sep_line(lines[j])
                or ORPHAN_NAME_HDR.match(lines[j].strip())
            ):
                if is_table_line(lines[j]) or is_sep_line(lines[j]):
                    intruded.append(j)
                j += 1
            if intruded and j < len(lines):
                b = lines[j].strip()
                if b in ("\\[", "\\]") or b.startswith("\\["):
                    i += 1
                    continue
                if (
                    b
                    and not b.startswith("|")
                    and not b.startswith("#")
                    and not b.startswith("---")
                ):
                    merged = a + b
                    lines[i] = merged
                    for k in reversed(intruded + list(range(i + 1, j + 1))):
                        del lines[k]
                    n += 1
                    continue
        i += 1
    return n


def fix_rd_garbage(lines: list[str]) -> int:
    n = 0
    for i, ln in enumerate(lines):
        if ln.strip().startswith("RD](../docs"):
            lines[i] = (
                "숫자는 [DEPTH-STANDARD](../docs/DEPTH-STANDARD.md) "
                + ln.strip().removeprefix("RD](../docs/DEPTH-STANDARD.md) ")
            )
            n += 1
    return n


def remove_fragment_blocks(lines: list[str]) -> int:
    """Drop known orphan fragments in §6."""
    drop_pats = [
        r"^3\. \*\*해석\*\*: 부호·크기",
        r"^\(분류\)\*\* 반영",
        r"^--\s*$",
        r"^\*\*반도체 업황\*\*: \*\*Sales↑\*\*와 \*\*$",
    ]
    n = 0
    out: list[str] = []
    for ln in lines:
        if any(re.match(p, ln.strip()) for p in drop_pats):
            n += 1
            continue
        out.append(ln)
    lines[:] = out
    return n


def fix_glued_display_math_openers(text: str) -> str:
    """Prose ending with \\[ on same line -> newline before display math."""
    text = re.sub(r"([^\n\\])\\\[\s*\n", r"\1\n\n\\[\n", text)
    return re.sub(r"([^\n\\])\\\[\s*$", r"\1\n\n\\[", text, flags=re.M)


def close_unterminated_display_blocks(text: str) -> str:
    """Insert \\] before **유도 / ### when a display block was left open."""
    lines = text.splitlines()
    out: list[str] = []
    open_block = False
    for i, ln in enumerate(lines):
        st = ln.strip()
        if st == "\\[":
            open_block = True
            out.append(ln)
            continue
        if st == "\\]":
            open_block = False
            out.append(ln)
            continue
        if open_block and (
            st.startswith("**유도")
            or st.startswith("### ")
            or (st.startswith("**읽는 법**") and i > 0 and out and out[-1].strip() and not out[-1].strip().startswith("\\"))
        ):
            out.append("\\]")
            open_block = False
        out.append(ln)
    if open_block:
        out.append("\\]")
    return "\n".join(out)


def fix_broken_latex_cmds(text: str) -> str:
    text = text.replace(r"\(\FCF\)", r"\(FCF\)")
    text = text.replace(r"\(\OCF\)", r"\(OCF\)")
    text = re.sub(
        r"\|\s*\\?\(?\\?X_\\text\{\s*gross\s*\}\s*\\?\)?\s*\|[^|\n]+\|[^|\n]*§4[^|\n]*\|",
        "",
        text,
    )
    return text


def repair_section6(text: str) -> tuple[str, int]:
    m = re.search(r"^## 6[\.\s]", text, re.M)
    if not m:
        return text, 0
    end_m = re.search(r"^## [^6]", text[m.start() + 10 :], re.M)
    end = m.start() + 10 + end_m.start() if end_m else len(text)
    head, s6, tail = text[: m.start()], text[m.start() : end], text[end:]
    changes = 0

    s6 = fix_glued_display_math_openers(s6)
    s6 = clean_display_math(s6)
    s6 = fix_broken_latex_cmds(s6)
    lines = s6.splitlines()

    for fn in (
        remove_orphan_name_headers,
        remove_placeholder_rows,
        remove_intratable_separators,
        dedupe_consecutive_var_tables,
        fix_split_headings,
        fix_split_prose,
        fix_rd_garbage,
        remove_fragment_blocks,
        split_separator_glued_to_heading,
    ):
        changes += fn(lines)

    s6 = "\n".join(lines)
    s6 = clean_display_math(s6)
    s6 = fix_glued_display_math_openers(s6)
    s6 = close_unterminated_display_blocks(s6)
    s6 = re.sub(r"\n{4,}", "\n\n\n", s6)
    if tail:
        result = head + s6.rstrip() + "\n\n" + tail.lstrip("\n")
    else:
        result = head + s6
    result = split_hr_glued_to_headings(result)
    result = re.sub(
        r"(\|(?:[^|\n]*\|)+)\s*(#{1,6}\s)",
        r"\1\n\n\2",
        result,
    )
    return result, changes


def main() -> int:
    total = 0
    files = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        text2 = split_hr_glued_to_headings(text)
        hr_fix = int(text2 != text)
        new_text, n = repair_section6(text2)
        n += hr_fix
        if n:
            path.write_text(new_text, encoding="utf-8")
            print(f"{path.name}: {n} fix(es)")
            total += n
            files += 1
    print(f"\nRepaired §6 intrusion in {files} files ({total} operations)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
