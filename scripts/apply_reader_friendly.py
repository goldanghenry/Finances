#!/usr/bin/env python3
"""
Insert §0, normalize meta difficulty, ensure §4a stub for L3/L4 corpus files.
Skips: README, docs/*, references, scripts, plan files, already-has-§0.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"scripts", ".tmp_l3", "site", "webdocs", ".venv", "private", ".git", ".github"}
SKIP_NAMES = {"README.md", "sources.md"}

SECTION0 = """## 0. 이 편 읽기 전 (5분)

| 항목 | 내용 |
|------|------|
| **난이도** | {level} — [READER-GUIDE §L등급]({reader_link}) |
| **선수** | {prereq} |
| **이번 편에서 쓰는 기호** | {symbols} |
| **복습 한 줄** | {review} |

"""

SECTION4A_STUB = """
### 4a. 핵심 용어 (본문 등장 순)

> 복습용. 정의는 §4 본표·[glossary]({glossary})·본문 `!!! info` 박스.

| 용어 | 한 줄 | 관련 이론 | glossary |
|------|-------|-----------|----------|
| (본문 표 참고) | — | — | [glossary]({glossary}) |

"""

META_LEVEL_RE = re.compile(r"^\| 난이도 \|.*\|$", re.M)
HAS_SECTION0 = re.compile(r"^## 0\. 이 편 읽기 전", re.M)
HAS_SECTION4A = re.compile(r"^### 4a\.|^## 4a\.", re.M)
META_BLOCK = re.compile(r"(## 메타\n\n\|[^\n]+\|\n(?:\|[^\n]+\|\n)+)", re.M)


def reader_link(path: Path) -> str:
    rel = path.relative_to(ROOT)
    depth = len(rel.parents) - 1
    return "../" * depth + "docs/READER-GUIDE.md"


def glossary_link(path: Path) -> str:
    rel = path.relative_to(ROOT)
    depth = len(rel.parents) - 1
    return "../" * depth + "00-roadmap/glossary.md"


def detect_level(text: str) -> str:
    m = re.search(r"\| 난이도 \| ([^|]+) \|", text)
    if m:
        raw = m.group(1).strip()
        if "L4" in raw:
            return "L4 (Graduate)"
        if "L3" in raw:
            return "L3 (Deep)"
        if "L2" in raw:
            return "L2 (Standard)"
        if "L1" in raw:
            return "L1 (Primer)"
    if "**L4" in text or "L4 (" in text:
        return "L4 (Graduate)"
    return "L3 (Deep)"


def default_symbols(path: Path) -> str:
    name = path.name
    if "compound" in name or "time-value" in name or "npv" in name:
        return "PV, FV, PMT, r, n, 복리"
    if "cash-flow" in name or "household" in name or "emergency" in name:
        return "M, FV, PMT, 저축률, Bucket"
    if "isa" in name or "irp" in name or "pension" in name or "tax" in name:
        return "L_ISA, ISA, IRP, DB, DC (해당 시)"
    if "portfolio" in name or "bucket" in name:
        return "Bucket, 코어, 위성, DCA"
    if path.parts[0] == "02-economics":
        return "GDP, CPI, IS-LM, QE (해당 시)"
    return "본문 §4·§4a 표 참고"


def default_prereq(path: Path) -> str:
    if path.name == "compound-interest-and-time-value.md":
        return "없음 (Phase 0 첫 권장)"
    if path.name == "cash-flow-basics.md":
        return "[compound-interest-and-time-value](compound-interest-and-time-value.md)"
    return "§2 선수 문서 참고"


def default_review(path: Path, level: str) -> str:
    if "compound" in path.name:
        return "복리 = 이자가 원금에 다시 붙는 구조"
    if level.startswith("L4"):
        return "L3 선수 편을 먼저 읽으면 수식이 수월함"
    return "—"


def insert_section0(text: str, path: Path) -> str:
    if HAS_SECTION0.search(text):
        return text
    level = detect_level(text)
    rl = reader_link(path)
    block = SECTION0.format(
        level=level,
        reader_link=rl,
        prereq=default_prereq(path),
        symbols=default_symbols(path),
        review=default_review(path, level),
    )
    # After meta table, before TL;DR or ---
    m = META_BLOCK.search(text)
    if not m:
        return text
    end = m.end()
    rest = text[end:]
    if rest.lstrip().startswith("## 0."):
        return text
    return text[:end] + "\n" + block + rest


def fix_meta_level(text: str, path: Path) -> str:
    level = detect_level(text)
    rl = reader_link(path)
    new_line = f"| 난이도 | {level} — [{rl.split('/')[-1].replace('.md','')}]({rl}) |"
    if META_LEVEL_RE.search(text):
        return META_LEVEL_RE.sub(new_line, text, count=1)
    return text


def insert_section4a(text: str, path: Path) -> str:
    if HAS_SECTION4A.search(text):
        return text
    if "## 4." not in text and "## 4 " not in text:
        return text
    gl = glossary_link(path)
    stub = SECTION4A_STUB.format(glossary=gl)
    # After first ## 4. 정식 block table ends (before ### 4a or ## 5)
    m = re.search(r"(## 4\.[^\n]*\n(?:.*?\n)*?\|[^\n]+\|\n(?:\|[^\n]+\|\n)+)", text)
    if not m:
        return text
    insert_at = m.end()
    return text[:insert_at] + stub + text[insert_at:]


def is_corpus_md(path: Path) -> bool:
    path = path if path.is_absolute() else ROOT / path
    if path.suffix != ".md":
        return False
    if path.name in SKIP_NAMES:
        return False
    if any(p in SKIP_DIRS for p in path.parts):
        return False
    if path.parts[0] == "docs" and path.name not in ("READER-GUIDE.md",):
        return False
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return False
    if rel.parts[0] in {
        "01-foundations",
        "02-economics",
        "03-markets",
        "04-portfolio",
        "05-behavioral",
        "06-korea-policy",
        "07-real-estate",
        "08-advanced",
        "09-corporate-finance",
        "00-roadmap",
    }:
        return "## 메타" in path.read_text(encoding="utf-8", errors="ignore")
    return False


def process(path: Path, dry_run: bool = False) -> bool:
    path = path if path.is_absolute() else ROOT / path
    text = path.read_text(encoding="utf-8")
    orig = text
    text = fix_meta_level(text, path)
    text = insert_section0(text, path)
    text = insert_section4a(text, path)
    if text != orig:
        if not dry_run:
            path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    dry = "--dry-run" in sys.argv
    changed = 0
    for path in sorted(ROOT.rglob("*.md")):
        if not is_corpus_md(path):
            continue
        if process(path, dry_run=dry):
            changed += 1
            print(path.relative_to(ROOT))
    print(f"{'Would update' if dry else 'Updated'} {changed} files")


if __name__ == "__main__":
    main()
