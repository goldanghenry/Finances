#!/usr/bin/env python3
"""Repair broken admonitions, orphaned table rows, and §6 placeholder variable tables."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import iter_corpus_md

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = "§4·본문 정의 참고"

# symbol -> (Korean name, meaning in formulas)
SYMBOL_GLOSS: dict[str, tuple[str, str]] = {
    "PV": ("현재가치", "오늘 시점으로 환산한 금액"),
    "FV": ("미래가치", "미래 시점의 목표·결과 금액"),
    "PMT": ("정기 납입", "매 기간 동일하게 넣거나 받는 금액"),
    "NPV": ("순현재가치", "할인 CF 합에서 초기 투자를 뺀 값"),
    "IRR": ("내부수익률", "NPV를 0으로 만드는 할인율"),
    "r": ("할인율·수익률", "기간당 이자·요구수익률"),
    "n": ("기간", "연·월 등 복리·할인에 쓰는 횟수"),
    "s": ("저축률", "소득 대비 남는 비율"),
    "Y": ("소득", "기간 총 실수령·매출 등"),
    "C": ("지출", "기간 총 현금 유출"),
    "M": ("월 실수령", "가계 교육용 월 세후 소득 기호"),
    "R_f": ("무위험금리", "국채·예금 등 기준 금리"),
    "Rf": ("무위험금리", "국채·예금 등 기준 금리"),
    "beta": ("베타", "시장 대비 민감도"),
    "β": ("베타", "시장 대비 민감도"),
    "C_0": ("초기 투자", "시점 0 유출(투자금)"),
    "CF_t": ("t기 현금흐름", "유입 +, 유출 − (관례 확인)"),
    "T": ("기간", "마지막 CF 시점"),
    "F_0": ("비상금 합계", "runway 분자(유동성)"),
    "NMB": ("순소비", "runway 분모(월 필수 지출)"),
    "L_ISA": ("ISA 연 한도", "제도상 연 납입 상한(만 원)"),
    "alpha_textISA": ("ISA 적립 비율", "월 실수령 M 중 ISA 슬롯 비율"),
    "alpha_textP": ("연금 적립 비율", "IRP·연금저축 등 연금 슬롯 비율"),
    "alpha_textG": ("일반 계좌 비율", "한도 초과·위성·환전 여유 비율"),
    "alpha_ISA": ("ISA 배분 비율", "월 소득 중 ISA로 보내는 비율"),
    "alpha_P": ("연금 배분 비율", "IRP·DC 등 연금 슬롯 비율"),
    "alpha_G": ("일반 배분 비율", "과세 일반계좌·위성·환전 여유 비율"),
    "alpha": ("그리스 문자 α", "배분·민감도 등 맥락별 계수(아래 첨자와 함께 읽기)"),
    "ISA": ("ISA", "개인종합자산관리계좌 슬롯"),
    "P": ("포트 규모", "가상 포트폴리오 규모(만 원)"),
    "ERP": ("주식위험프리미엄", "E[Rm] − Rf"),
    "WACC": ("가중평균자본비용", "기업·프로젝트 할인율 근사"),
    "YTM": ("만기수익률", "채권 가격에 내재된 IRR 근사"),
    "FCF": ("잉여현금흐름", "투자자에게 가용한 현금"),
    "OCF": ("영업현금흐름", "영업활동에서 발생한 현금"),
    "PER": ("주가수익비율", "주가 ÷ EPS"),
    "EPS": ("주당순이익", "순이익 ÷ 발행주식수"),
    "GDP": ("국내총생산", "일정 기간 총생산"),
    "CPI": ("소비자물가", "인플레이션 근사 지표"),
    "pi": ("인플레이션율", "물가 상승률"),
    "π": ("인플레이션율", "물가 상승률"),
}


def parse_section4_terms(text: str) -> dict[str, str]:
    terms: dict[str, str] = {}
    m = re.search(r"^## 4\.[^\n]*\n+?(?:\|[^\n]+\|\n)+((?:\|[^\n]+\|\n)+)", text, re.M)
    if not m:
        return terms
    for line in m.group(1).splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in ("용어", "------", "약어"):
            continue
        key = re.sub(r"\\[a-zA-Z_{}\s\d^().]+", "", cells[0]).strip()
        key = key.split("(")[0].strip()
        desc = cells[-1] if cells else ""
        if len(desc) > 80:
            desc = desc[:77] + "…"
        if key:
            terms[key] = desc
            terms[key.upper()] = desc
        if len(cells) >= 3 and cells[1]:
            eng = cells[1].strip()
            if eng and len(eng) < 30:
                terms[eng.upper()] = desc
    return terms


def lookup_meaning(sym: str, terms4: dict[str, str]) -> str:
    raw = sym.strip()
    for key in (raw, raw.upper(), raw.replace("\\", "")):
        if key in terms4 and terms4[key] and terms4[key] != PLACEHOLDER:
            return terms4[key]
    bare = re.sub(r"^\\?\(?\\?([A-Za-z0-9_]+)\\?\)?$", r"\1", raw)
    bare = bare.replace("{", "").replace("}", "")
    if bare in SYMBOL_GLOSS:
        return SYMBOL_GLOSS[bare][1]
    if bare.upper() in SYMBOL_GLOSS:
        return SYMBOL_GLOSS[bare.upper()][1]
    for k, (_, meaning) in SYMBOL_GLOSS.items():
        if k.upper() == bare.upper():
            return meaning
    name = lookup_name(sym)
    if name and name.replace("_", " ") != bare.replace("_", " "):
        return f"위 식의 {name}"
    return terms4.get(bare, terms4.get(bare.upper(), f"위 식의 {bare}"))


def lookup_name(sym: str) -> str:
    bare = re.sub(r"^\\?\(?\\?([A-Za-z0-9_βπ]+)\\?\)?$", r"\1", sym.strip())
    bare = bare.replace("{", "").replace("}", "")
    if bare in SYMBOL_GLOSS:
        return SYMBOL_GLOSS[bare][0]
    if bare.upper() in SYMBOL_GLOSS:
        return SYMBOL_GLOSS[bare.upper()][0]
    return bare.replace("_", " ")


def fix_section6_placeholders(text: str) -> tuple[str, bool]:
    if PLACEHOLDER not in text and not re.search(r"\|\s*\\\s*\|", text):
        return text, False
    terms4 = parse_section4_terms(text)
    changed = False

    def repl_row(m: re.Match[str]) -> str:
        nonlocal changed
        sym_cell, name_cell, mean_cell = m.group(1), m.group(2), m.group(3)
        sym = sym_cell.strip()
        if PLACEHOLDER not in mean_cell and not re.fullmatch(r"\\?", mean_cell.strip()):
            if re.fullmatch(r"\\?", mean_cell.strip()):
                changed = True
                mean_cell = lookup_meaning(sym, terms4)
            else:
                return m.group(0)
        else:
            changed = True
        if PLACEHOLDER in mean_cell or mean_cell.strip() in ("\\", ""):
            mean_cell = lookup_meaning(sym, terms4)
        if name_cell.strip() in ("", sym, sym.replace("\\", "")):
            name_cell = lookup_name(sym)
        if re.fullmatch(r"\\?", sym_cell.strip()):
            return m.group(0)
        return f"| {sym_cell} | {name_cell} | {mean_cell} |"

    new_text = re.sub(
        r"^\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|\s*$",
        repl_row,
        text,
        flags=re.M,
    )
    return new_text, changed


def fix_orphan_table_rows_after_admonition(text: str) -> tuple[str, bool]:
    """Move | rows after empty/broken admonition back into preceding table block."""
    lines = text.splitlines()
    changed = False
    i = 0
    while i < len(lines):
        if not lines[i].startswith("!!! "):
            i += 1
            continue
        title = lines[i]
        j = i + 1
        body: list[str] = []
        while j < len(lines) and not lines[j].startswith("!!! ") and not lines[j].startswith("## "):
            if lines[j].strip() == "" and j + 1 < len(lines) and lines[j + 1].startswith("|"):
                break
            if lines[j].startswith("|") and not body:
                break
            body.append(lines[j])
            j += 1
        if body and all(b.strip() == "" for b in body):
            # empty admonition — drop and keep following content
            changed = True
            lines = lines[:i] + lines[j:]
            continue
        i = j if j > i else i + 1
    return "\n".join(lines), changed


def fix_cash_flow_section1(text: str) -> tuple[str, bool]:
    if "cash-flow-basics" not in text and "PMT (Payment, 정기 납입)" not in text:
        return text, False
    old = (
        '!!! info "PMT (Payment, 정기 납입)"\n\n'
        '!!! info "ETF"\n'
        "    지수·자산 **바구니**를 한 종목처럼 거래\n\n"
        "    복리 공식에서 **매월·매년 같은 금액**으로 넣는 돈. 가계에서는 **비상금·ISA·ETF로 자동이체하는 금액 합**이 PMT에 해당한다. **실제로 통장에서 빠져나간 돈**이어야 한다.\n\n"
        "| 이유 | 설명 |\n"
        "|------|------|\n"
        "| **미래가치(FV)에 들어가는 돈** | 위 **PMT**가 [복리 공식](compound-interest-and-time-value.md#62-정기-납입기말-납입-연금-교육용)의 입력 — **수익률만큼** 중요 |\n\n"
        '!!! info "Bucket"\n'
        "    시간·목적별 **자금 슬롯**(0 비상금 → 3 코어 등)\n\n"
        "| **Bucket 실행** | 이론적 자산배분 없이 **매달 남는 돈**이 없으면 설계 불가 |\n"
        "| **행동** | 카드·구독·고정비가 **저축률을 잠식** — [fomo-and-trading-hours](../05-behavioral/fomo-and-trading-hours.md) |\n"
    )
    new = (
        '!!! info "PMT (Payment, 정기 납입)"\n'
        "    복리 공식에서 **매월·매년 같은 금액**으로 넣는 돈. 가계에서는 **비상금·ISA·ETF 자동이체 합**이 PMT에 해당한다. **실제로 통장에서 빠져나간 돈**이어야 한다.\n\n"
        '!!! info "ETF (Exchange-Traded Fund)"\n'
        "    지수·자산 **바구니**를 한 종목처럼 거래하는 상품. PMT로 넣는 대상 중 하나.\n\n"
        '!!! info "Bucket (자금 슬롯)"\n'
        "    시간·목적별 **자금 통**(0 비상금 → 3 코어 등). **채우는 순서**가 비중 %보다 먼저다.\n\n"
        "| 이유 | 설명 |\n"
        "|------|------|\n"
        "| **미래가치(FV)에 들어가는 돈** | **PMT**가 [복리 공식](compound-interest-and-time-value.md#62-정기-납입기말-납입-연금-교육용)의 입력 — **수익률만큼** 중요 |\n"
        "| **Bucket 실행** | 이론적 자산배분 없이 **매달 남는 돈**이 없으면 설계 불가 |\n"
        "| **행동** | 카드·구독·고정비가 **저축률을 잠식** — [fomo-and-trading-hours](../05-behavioral/fomo-and-trading-hours.md) |\n"
    )
    if old in text:
        return text.replace(old, new), True
    return text, False


def repair_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    text, c1 = fix_section6_placeholders(text)
    text, c2 = fix_orphan_table_rows_after_admonition(text)
    if path.name == "cash-flow-basics.md":
        text, c3 = fix_cash_flow_section1(text)
    else:
        c3 = False
    if text != orig:
        path.write_text(text, encoding="utf-8")
    return c1 or c2 or c3


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        if repair_file(path):
            n += 1
            print(f"repaired {path.relative_to(ROOT)}")
    print(f"Repaired {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
