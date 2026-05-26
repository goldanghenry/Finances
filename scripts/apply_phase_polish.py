#!/usr/bin/env python3
"""Apply phase-specific reader-friendly polish blocks."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PHASE_DIRS: dict[str, list[str]] = {
    "0": ["01-foundations"],
    "1": ["01-foundations"],
    "2": ["02-economics"],
    "3": ["03-markets"],
    "3b": ["03-markets/sectors"],
    "4": ["04-portfolio"],
    "5": ["06-korea-policy"],
    "6": ["05-behavioral"],
    "7": ["07-real-estate"],
    "8": ["08-advanced"],
    "9": ["09-corporate-finance"],
}

PHASE1_FILES = {
    "financial-statements-intro.md",
    "financial-statements-analysis.md",
    "cash-flow-statement-fcf.md",
    "reading-annual-reports-dart.md",
    "dividends-buybacks.md",
    "financial-statements-study-roadmap.md",
}

PHASE0_FILES = {
    "compound-interest-and-time-value.md",
    "emergency-fund.md",
    "cash-flow-basics.md",
    "household-ledger-practical.md",
    "debt-and-interest.md",
    "insurance-risk-transfer.md",
    "financial-products-short-term.md",
    "time-value-npv-irr.md",
}

COMPANY_NOTE = (
    "\n> **가상 사례 회사**: 본 Phase 재무제표 심화 편은 **「가상 주식회사 한빛전자」** "
    "(가상의 코스피 제조·전자 부품) 숫자로 3표·DART·FCF를 **같은 스레드**로 읽는다. "
    "실제 종목·실적이 아니다.\n"
)

PAIR_NOTES: dict[str, str] = {
    "bonds-fixed-income.md": (
        "\n> **심화 편**: 본문 입문 후 [채권 심화](bonds-fixed-income-deep.md)에서 "
        "듀레이션·컨벡시티·신용 스프레드를 이어서 읽는다.\n"
    ),
    "etf-index-funds.md": (
        "\n> **심화 편**: [ETF 심화](etf-index-funds-deep.md)에서 추적오차·괴리·"
        "인덱스 구성을 본다.\n"
    ),
    "stocks-equities-intro.md": (
        "\n> **심화 편**: [주식 밸류에이션](equity-valuation-fundamentals.md)에서 "
        "DCF·멀티플·DDM을 연결한다.\n"
    ),
}

TAX_NOTE = (
    "\n> **세금 시리즈 읽기 순서**: [해외주식 part1](tax/overseas-stocks-tax-part1-cgt.md) "
    "→ part2(배당) → part3(시나리오)는 **동일 가상 거래**(교육용 기호 P·M)로 "
    "표를 맞춰 읽는다.\n"
)

MODEL_NOTE = (
    "\n\n**이 모형이 말하는 것**: 수식은 계산 절차이고, 경제 직관은 "
    "「누가 이득·손해를 보는가」「어떤 가정이 깨지면 결론이 뒤집히는가」다. "
    "유도 각 단계마다 **가정**을 한 줄로 적어 본다.\n"
)


def iter_phase_files(phase: str) -> list[Path]:
    paths: list[Path] = []
    for rel in PHASE_DIRS.get(phase, []):
        base = ROOT / rel
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            if p.name == "README.md":
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            if "## 메타" not in text:
                continue
            if phase == "0" and p.name not in PHASE0_FILES:
                continue
            if phase == "1" and p.name not in PHASE1_FILES:
                continue
            paths.append(p)
    return paths


def insert_after_section3(text: str, block: str, marker: str) -> tuple[str, bool]:
    if marker in text:
        return text, False
    m = re.search(r"^## 3\.[^\n]*\n", text, re.M)
    if not m:
        return text, False
    start = m.end()
    m2 = re.search(r"^## 4[\.\s]", text[start:], re.M)
    if not m2:
        return text, False
    insert_at = start + m2.start()
    return text[:insert_at] + block + text[insert_at:], True


def polish_file(path: Path, phase: str) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    if phase == "1" and path.name in PHASE1_FILES and "한빛전자" not in text:
        m = re.search(r"^## 0\.[^\n]*\n(?:.*?\n)*?(?=## TL;DR)", text, re.M | re.S)
        if m:
            text = text[: m.end()] + COMPANY_NOTE + text[m.end() :]
    if phase == "2" and path.parent.name == "02-economics":
        text, _ = insert_after_section3(text, MODEL_NOTE, "이 모형이 말하는 것")
    if phase == "3" and path.name in PAIR_NOTES and PAIR_NOTES[path.name].strip() not in text:
        m = re.search(r"^## TL;DR", text, re.M)
        if m:
            text = text[: m.start()] + PAIR_NOTES[path.name] + text[m.start() :]
    if phase == "5" and "overseas-stocks-tax-part1" in path.name and "동일 가상 거래" not in text:
        m = re.search(r"^## TL;DR", text, re.M)
        if m:
            text = text[: m.start()] + TAX_NOTE + text[m.start() :]
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    phases = list(PHASE_DIRS) if phase == "all" else [phase]
    n = 0
    for ph in phases:
        for path in iter_phase_files(ph):
            if polish_file(path, ph):
                n += 1
                print(f"[{ph}] {path.relative_to(ROOT)}")
    print(f"Polished {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
