#!/usr/bin/env python3
"""Repair LaTeX/table merge corruption that breaks lint_corpus_quality."""

from __future__ import annotations

import re
import sys

from _corpus import iter_corpus_md

VAR_HDR = "| 기호 | 이름 | 이 식에서 의미 |"
VAR_SEP = "|------|------|----------------|"
MERGED_HDR = re.compile(r"(?P<before>[^\n|]*?)\|\s*기호\s*\|\s*이름\s*\|\s*이 식에서 의미\s*\|")
BROKEN_ROW = re.compile(
    r"^\s*\|[^|\n]*\|[^|\n]*\|[^|\n]*\|\s*기호\s*\|\s*이름\s*\|\s*이 식에서 의미\s*\|\s*$"
)
DOUBLE_PIPE_ROW = re.compile(r"(\|[^|\n]+\|[^|\n]+\|)\s*\|\s*기호\s*\|")
LONE_BACKSLASH_CELL = re.compile(r"^\|\s*\\\s*\|")


def dedupe_var_tables(lines: list[str]) -> list[str]:
    """Drop consecutive duplicate variable-table headers/separators."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.strip() == VAR_HDR:
            # collect this table block
            block = [ln]
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                block.append(lines[j])
                j += 1
            # if next block is also VAR_HDR immediately, skip this one if it's junk
            if j < len(lines) and lines[j].strip() == VAR_HDR:
                # keep the later block only — skip current if it has <3 data rows
                data = [b for b in block if VAR_HDR not in b and VAR_SEP not in b and "---" not in b]
                if len(data) < 2:
                    i = j
                    continue
            out.extend(block)
            i = j
            continue
        out.append(ln)
        i += 1
    return out


def split_merged_lines(text: str) -> str:
    lines = text.splitlines()
    new_lines: list[str] = []
    for ln in lines:
        if VAR_HDR in ln and not ln.strip().startswith("|"):
            m = MERGED_HDR.search(ln)
            if m:
                before = m.group("before").rstrip()
                rest = ln[m.end() - len(VAR_HDR) :].lstrip()
                if before:
                    # truncate broken LaTeX openers
                    if before.rstrip().endswith("\\["):
                        new_lines.append(before.rstrip())
                    elif "\\[" in before and "\\]" not in before:
                        # drop incomplete display-math opener line
                        before = re.sub(r"\\\[\s*$", "", before).rstrip()
                        if before:
                            new_lines.append(before)
                    else:
                        new_lines.append(before)
                new_lines.append(VAR_HDR + rest[rest.startswith("|") and 0 :])
                if rest and not rest.startswith("|"):
                    new_lines.append("|" + rest if rest.startswith(" ") else rest)
                continue
        m2 = DOUBLE_PIPE_ROW.search(ln)
        if m2 and VAR_HDR in ln:
            prefix = m2.group(1) + " |"
            new_lines.append(prefix)
            idx = ln.index(VAR_HDR)
            new_lines.append(ln[idx:])
            continue
        if BROKEN_ROW.match(ln):
            continue
        if LONE_BACKSLASH_CELL.match(ln.strip()):
            new_lines.append(VAR_HDR)
            continue
        new_lines.append(ln)
    return "\n".join(dedupe_var_tables(new_lines))


def remove_orphan_display_math(text: str) -> str:
    """Remove \\[ blocks that never close and contain table markers."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == "\\[":
            j = i + 1
            found_close = False
            while j < len(lines):
                if lines[j].strip() == "\\]":
                    found_close = True
                    break
                if lines[j].strip() == "\\[":
                    break
                j += 1
            if not found_close:
                chunk = "\n".join(lines[i:j])
                if "|" in chunk or "기호" in chunk or "\\lamb" in chunk:
                    i = j
                    continue
        # single-line \[ ... without \] on same or following lines
        if lines[i].strip().startswith("\\[") and "\\]" not in lines[i]:
            if "|" in lines[i] or "기호" in lines[i]:
                i += 1
                continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def remove_junk_separator_runs(lines: list[str]) -> list[str]:
    out: list[str] = []
    sep_run = 0
    for ln in lines:
        if ln.strip() == VAR_SEP:
            sep_run += 1
            if sep_run > 1:
                continue
        else:
            sep_run = 0
        out.append(ln)
    return out


def remove_fragment_lines(text: str) -> str:
    """Drop orphan prose/table fragments."""
    drop_pats = [
        r"^·PV 등\)로 대입한다\.\s*$",
        r"^/DEPTH-STANDARD\.md\)",
        r"^\|\s*--\|\s*기호",
        r"^\|\s*\\\(\s*\|\s*기호",
    ]
    lines = []
    for ln in text.splitlines():
        if any(re.search(p, ln) for p in drop_pats):
            continue
        if re.match(r"^\|\s*PV\)\s*\|", ln):
            continue
        lines.append(ln)
    return "\n".join(remove_junk_separator_runs(lines))


def clean_table_artifacts(text: str) -> str:
    text = re.sub(
        r"(\| 기호 \| 이름 \| 이 식에서 의미 \|)\s*\|\s*기호 \| 이름 \| 이 식에서 의미 \|",
        r"\1",
        text,
    )
    text = re.sub(
        r"^\|\s*------\s*\|\s*------\s*\|[^\n]*이\(가\)[^\n]*\|\s*$",
        VAR_SEP,
        text,
        flags=re.M,
    )
    # prose + orphan var table before "정의 확인)"
    text = re.sub(
        r"(\(교육용; 실무는 \*\*처분·M&A\*\* 제외·순액)\n\| 기호[^\n]*\n(?:\|[^\n]+\n)+?\n+( 정의 확인\)\.)",
        r"\1\2",
        text,
    )
    text = re.sub(r"순액\n+\s*정의 확인\)\.", "순액 정의 확인).", text)
    lines: list[str] = []
    for ln in text.splitlines():
        s = ln.strip()
        if re.match(r"^\|[^|\n]+\|[^|\n]+\|\s*현\s*$", ln):
            continue
        if s in ("핵심이다.",) or s.startswith("핵심이다."):
            continue
        if re.match(r"^CAPEX/Sales", s):
            continue
        if re.match(r"^\|\s*------\s*\|\s*------\s*\|\s*------\s*\|", ln):
            continue
        if re.match(r"^/DEPTH-STANDARD", s):
            continue
        if re.match(r"^\d+\.\s+\*\*해석\*\*", s) and lines and lines[-1].strip() == "---":
            continue
        lines.append(ln)
    text = "\n".join(lines)
    # merge broken prose lines
    text = re.sub(
        r"(\*\*CAPEX\*\*는[^\n]+순액)\n\n+( 정의 확인\)\.)",
        r"\1\2",
        text,
    )
    text = re.sub(r"(\*\*CAPEX\*\*는[^\n]+순액)\s+(정의 확인\)\.)", r"\1 \2", text)
    return text


def fix_unbalanced_display_math(text: str) -> str:
    """Remove stray \\] or orphan \\[ lines."""
    opens = [m.start() for m in re.finditer(r"\\\[\s*\n", text)]
    closes = [m.start() for m in re.finditer(r"\\\]\s*\n", text)]
    if len(opens) == len(closes):
        return text
    lines = text.splitlines()
    if len(opens) < len(closes):
        # drop lone \\] lines not preceded by content block
        out: list[str] = []
        in_block = False
        for ln in lines:
            if ln.strip() == "\\[":
                in_block = True
                out.append(ln)
                continue
            if ln.strip() == "\\]":
                if in_block:
                    in_block = False
                    out.append(ln)
                continue
            out.append(ln)
        return "\n".join(out)
    # extra \\[ — remove orphan openers (handled in remove_orphan_display_math)
    return text


def repair(text: str) -> tuple[str, bool]:
    orig = text
    text = split_merged_lines(text)
    text = remove_orphan_display_math(text)
    text = remove_fragment_lines(text)
    text = clean_table_artifacts(text)
    text = fix_unbalanced_display_math(text)
    text = re.sub(
        r"(\*\*유도 \(L4\)\*\*:)\| 기호 \|",
        r"\1\n\n| 기호 |",
        text,
    )
    text = re.sub(
        r"(\*\*읽는 법\*\*:[^\n]+)\| 기호 \|",
        r"\1\n\n| 기호 |",
        text,
    )
    text = MERGED_HDR.sub(
        lambda m: (m.group("before").rstrip() + "\n\n" + VAR_HDR) if m.group("before").strip() else VAR_HDR,
        text,
    )
    return text, text != orig


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, changed = repair(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
    print(f"Repaired mangled tables in {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
