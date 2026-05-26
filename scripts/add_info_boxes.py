#!/usr/bin/env python3
"""Insert !!! info boxes at first abbreviation occurrence in §1."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import iter_corpus_md

PHASE_ABBREVS: dict[str, list[tuple[str, str, str]]] = {
    "0": [
        ("PV", "PV (Present Value)", "오늘 시점 가치 — 미래 현금을 **할인**할 때 씀"),
        ("FV", "FV (Future Value)", "미래 시점 가치 — 저축·투자 **목표액** 설계에 씀"),
        ("PMT", "PMT (Payment)", "매기간 **같은 금액** 납입(연금·DCA)"),
        ("M", "M (월지출)", "월 **세후 실수령**·지출 기준액(교육용 기호)"),
        ("Bucket", "Bucket", "시간·목적별 **자금 슬롯**(0 비상금 → 3 코어 등)"),
    ],
    "1": [
        ("OCF", "OCF (Operating Cash Flow)", "영업활동 **현금유입−유출**"),
        ("FCF", "FCF (Free Cash Flow)", "기업·가치평가의 **잉여 현금**"),
        ("PER", "PER (P/E)", "주가 ÷ **주당순이익(EPS)**"),
        ("ROE", "ROE", "순이익 ÷ **자기자본** — 수익성 지표"),
    ],
    "2": [
        ("GDP", "GDP", "국내총생산 — **경기 규모**"),
        ("CPI", "CPI", "소비자물가지수 — **인플레** 척도"),
        ("β", "베타 (β)", "시장 대비 **민감도**"),
        ("IS-LM", "IS-LM", "거시 **수요·금리** 균형 모형"),
    ],
    "3": [
        ("ETF", "ETF", "지수·자산 **바구니**를 한 종목처럼 거래"),
        ("TER", "TER", "연간 **총보수율** — 장기 복리에 영향"),
        ("YTM", "YTM", "채권 **만기수익률**(시장 할인율)"),
    ],
    "5": [
        ("ISA", "ISA", "개인종합자산관리계좌 — **비과세·한도**"),
        ("IRP", "IRP", "개인형 퇴직연금 — **세액공제·이연**"),
        ("CGT", "CGT", "양도소득세 — **매매차익** 과세"),
    ],
    "8": [
        ("CAPM", "CAPM", "위험 대비 **기대수익** 모형"),
        ("WACC", "WACC", "부채·자본 **가중 평균** 자본비용"),
        ("NPV", "NPV", "할인 현금흐름 **순현재가치**"),
        ("IRR", "IRR", "NPV=0이 되는 **내부수익률**"),
    ],
}


def phase_key(path: Path) -> str:
    top = path.parts[0] if path.parts else ""
    name = path.name
    if top == "02-economics":
        return "2"
    if top == "03-markets":
        return "3"
    if top == "04-portfolio":
        return "3"
    if top == "06-korea-policy":
        return "5"
    if top in ("08-advanced", "09-corporate-finance"):
        return "8"
    if top == "01-foundations" and "financial-statement" in name:
        return "1"
    return "0"


def section1_bounds(text: str) -> tuple[int, int] | None:
    m1 = re.search(r"^## 1\.[^\n]*\n", text, re.M)
    if not m1:
        return None
    start = m1.end()
    m2 = re.search(r"^## 2\.[^\n]*\n", text[start:], re.M)
    end = start + m2.start() if m2 else len(text)
    return start, end


def already_defined(text: str, sym: str) -> bool:
    pat = re.compile(
        rf"!!! info[^\n]*{re.escape(sym)}|§0[^\n]*{re.escape(sym)}|\*\*{re.escape(sym)}\*\*",
        re.I,
    )
    return bool(pat.search(text[:2500]))


def insert_boxes(text: str, path: Path, max_boxes: int = 5) -> str:
    bounds = section1_bounds(text)
    if not bounds:
        return text
    s1_start, s1_end = bounds
    s1 = text[s1_start:s1_end]
    pk = phase_key(path)
    candidates = PHASE_ABBREVS.get(pk, []) + PHASE_ABBREVS.get("3", [])
    inserted = 0
    offset = 0
    for sym, title, body in candidates:
        if inserted >= max_boxes:
            break
        if already_defined(text, sym):
            continue
        # word boundary for Latin; literal for symbols like β
        if sym == "β":
            m = re.search(r"(?<![A-Za-z])β(?![A-Za-z])", s1)
        elif sym == "IS-LM":
            m = re.search(r"IS-LM", s1)
        else:
            m = re.search(rf"(?<![A-Za-z0-9_]){re.escape(sym)}(?![A-Za-z0-9_])", s1)
        if not m:
            continue
        pos = s1_start + m.start() + offset
        line_start = text.rfind("\n", 0, pos) + 1
        if text[line_start:pos].strip().startswith("!!!"):
            continue
        box = f'\n!!! info "{title}"\n    {body}\n\n'
        text = text[:line_start] + box + text[line_start:]
        offset += len(box)
        inserted += 1
    return text


def main() -> None:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        if "!!! info" in text and path.name not in ("compound-interest-and-time-value.md",):
            # still add if missing for this phase
            pass
        new = insert_boxes(text, path)
        if new != text:
            path.write_text(new, encoding="utf-8")
            n += 1
    with_info = sum(
        1 for p in iter_corpus_md() if "!!! info" in p.read_text(encoding="utf-8")
    )
    total = len(iter_corpus_md())
    print(f"Added/updated info boxes in {n} files")
    print(f"Files with !!! info: {with_info}/{total} ({100*with_info//max(total,1)}%)")


if __name__ == "__main__":
    main()
