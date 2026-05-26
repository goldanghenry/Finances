#!/usr/bin/env python3
"""Gold-standard lint for L3/L4 corpus chapters (G1–G9)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import ROOT, iter_corpus_md
from _gold_polish import (
    PLACEHOLDER_MEANINGS,
    TEMPLATE_READING,
    is_l4,
    section6_body,
    section8_body,
    section10_body,
)

FORBIDDEN = (
    "§4·본문 정의 참고",
    "본문 §4·위 식 맥락 참고",
    "본문 §4·식 맥락 참고",
    TEMPLATE_READING,
    "[TODO:meaning]",
)

S8_MONEY = re.compile(r"\d+,?\d*만\s*원?|\d+\.?\d*억\s*원?")
S8_SALARY = re.compile(r"연봉\s*\d")
S8_INSTITUTIONAL = re.compile(
    r"한도|제도|L_ISA|법령|상한|ISA|IRP|연금|세액공제|예금자보호|1천~|보도상|DC \+|공제|비과세\s*\d|W-8BEN"
)
PRACTICAL_FAQ = re.compile(r"실무에서는|실무에선|실무에서는\?|실무 적용")
PRACTICE = re.compile(r"##\s*연습문제|연습문제\s*\(|###\s*연습|## 부록.*연습")
LIMIT = re.compile(r"가정이 깨지면|한계 사례|### 가정이 깨지면")
DERIVATION = re.compile(r"\*\*유도 \(L4\)\*\*|###\s*유도|유도 \(L4\)")


def check_forbidden(text: str) -> list[str]:
    issues = []
    for phrase in FORBIDDEN:
        if phrase in text:
            issues.append(f"forbidden phrase: {phrase!r}")
    return issues


def check_section6_gold(text: str) -> list[str]:
    issues: list[str] = []
    s6 = section6_body(text)
    if not s6 or "해당 없음" in s6[:300]:
        return issues
    s6_nc = re.sub(r"```[\s\S]*?```", "", s6)
    n_math = len(re.findall(r"\\\[\s*\n", s6_nc))
    n_tables = s6_nc.count("이 식에서 의미")
    if n_math > 0 and n_tables < n_math:
        issues.append(
            f"§6: {n_math} display equation(s) but {n_tables} variable table(s) (G1)"
        )
    for phrase in PLACEHOLDER_MEANINGS:
        if phrase in s6:
            issues.append(f"§6 placeholder (G1): {phrase!r}")
    if TEMPLATE_READING in s6:
        issues.append("§6 template reading note (G2)")

    # Each display math should have 읽는 법 within 250 chars
    for m in re.finditer(r"\\\]\s*\n", s6_nc):
        after = s6_nc[m.end() : m.end() + 250]
        if "읽는 법" not in after:
            issues.append("§6 equation missing **읽는 법** within 250 chars (G2)")
            break
    return issues


def check_section8_gold(text: str) -> list[str]:
    issues: list[str] = []
    s8 = section8_body(text)
    if not s8:
        return issues
    for line in s8.splitlines():
        if S8_INSTITUTIONAL.search(line):
            continue
        if S8_MONEY.search(line):
            issues.append("§8 contains concrete amount (G3)")
            break
        if S8_SALARY.search(line):
            issues.append("§8 contains concrete 연봉 number (G3)")
            break
    return issues


def check_faq(text: str) -> list[str]:
    s10 = section10_body(text)
    if not s10:
        return []
    if not PRACTICAL_FAQ.search(s10):
        return ["§10 missing practical FAQ (G4)"]
    return []


def check_l4(text: str) -> list[str]:
    if not is_l4(text):
        return []
    issues: list[str] = []
    if not PRACTICE.search(text):
        issues.append("L4 missing 연습문제 section (G8)")
    if not LIMIT.search(text):
        issues.append("L4 missing limitation / 가정이 깨지면 (G9)")
    s6 = section6_body(text)
    if s6 and re.search(r"\\\[\s*\n", s6) and not DERIVATION.search(s6):
        issues.append("L4 §6 missing 유도 block (G7)")
    return issues


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    issues.extend(check_forbidden(text))
    issues.extend(check_section6_gold(text))
    issues.extend(check_section8_gold(text))
    issues.extend(check_faq(text))
    issues.extend(check_l4(text))
    return issues


def main() -> int:
    paths = iter_corpus_md()
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1:]]
    bad = 0
    for path in paths:
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            print(f"missing: {path}")
            bad += 1
            continue
        issues = check_file(path)
        if issues:
            bad += 1
            print(f"{path.relative_to(ROOT)}:")
            for issue in issues:
                print(f"  - {issue}")
    print(f"\n{bad} files with gold issues")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
