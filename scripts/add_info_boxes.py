#!/usr/bin/env python3
"""Insert !!! info boxes at first acronym occurrence across all corpus docs."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"scripts", ".tmp_l3", "site", "webdocs", ".venv", "private", ".git", ".github", "docs", "references"}
SKIP_NAMES = {
    "README.md",
    "sources.md",
    "TEMPLATE.md",
    "required-reading-guide.md",
    "ai-engineer-investing-playbook.md",
    "office-worker-investing-playbook.md",
}

# term -> (English, one-line Korean)
TERM_DEFS: dict[str, tuple[str, str]] = {
    "PV": ("Present Value", "미래·과거 현금흐름을 오늘 가치로 환산한 금액"),
    "FV": ("Future Value", "오늘 PV를 이자·수익률로 굴린 미래 금액"),
    "PMT": ("Payment", "매 기간 동일한 금액의 납입·수령"),
    "NPV": ("Net Present Value", "할인된 현금흐름 합 − 초기 투자액"),
    "IRR": ("Internal Rate of Return", "NPV=0이 되는 내부수익률"),
    "TVM": ("Time Value of Money", "시점이 다르면 돈의 가치가 다름"),
    "M": ("Monthly take-home", "월 실수령·가계 기준 금액(기호 M)"),
    "Bucket": ("Time bucket", "목적·기간별 자금 슬롯"),
    "OCF": ("Operating Cash Flow", "영업활동 현금흐름"),
    "FCF": ("Free Cash Flow", "투자자에게 가용한 잉여현금흐름(영업CF − CAPEX)"),
    "PER": ("Price-Earnings Ratio", "주가 ÷ 주당순이익. 주가 수익 배수"),
    "PBR": ("Price-to-Book Ratio", "주가 ÷ 주당순자산. 장부가 대비 주가 배수"),
    "EPS": ("Earnings Per Share", "주당순이익. 순이익 ÷ 발행주식수"),
    "DPS": ("Dividend Per Share", "주당 배당금. 배당 총액 ÷ 발행주식수"),
    "ROE": ("Return on Equity", "순이익 ÷ 자기자본. 자기자본이익률"),
    "ROA": ("Return on Assets", "순이익 ÷ 총자산. 총자산이익률"),
    "ROIC": ("Return on Invested Capital", "세후영업이익 ÷ 투하자본"),
    "EBITDA": ("Earnings Before Interest, Taxes, Depreciation & Amortization", "이자·세금·감가상각 차감 전 영업이익"),
    "GDP": ("Gross Domestic Product", "일정 기간 국내 총생산"),
    "CPI": ("Consumer Price Index", "소비자물가지수·인플레 근사 지표"),
    "ETF": ("Exchange-Traded Fund", "거래소에 상장된 인덱스·자산 묶음 펀드"),
    "TER": ("Total Expense Ratio", "펀드·ETF 연간 총보수율"),
    "ISA": ("Individual Savings Account", "개인종합자산관리계좌"),
    "IRP": ("Individual Retirement Pension", "개인형 퇴직연금"),
    "DB": ("Defined Benefit", "확정급여형 퇴직연금"),
    "DC": ("Defined Contribution", "확정기여형 퇴직연금"),
    "CGT": ("Capital Gains Tax", "자산 매각 차익에 부과하는 세금"),
    "YTM": ("Yield to Maturity", "채권 만기수익률(IRR 근사)"),
    "CAPM": ("Capital Asset Pricing Model", "β로 기대수익을 설명하는 단일요인 모형"),
    "WACC": ("Weighted Average Cost of Capital", "부채·자기자본 가중 평균 자본비용"),
    "ERP": ("Equity Risk Premium", "주식위험프리미엄 E[Rm] − Rf"),
    "β": ("Beta", "시장 수익률 1% 변화에 대한 자산 수익률 민감도"),
    "IS-LM": ("IS-LM model", "총수요·통화시장 균형 거시 모형"),
    "QE": ("Quantitative Easing", "중앙은행의 양적완화"),
    "MPT": ("Modern Portfolio Theory", "분산·효율 프론티어 포트폴리오 이론"),
    "DCA": ("Dollar-Cost Averaging", "정기·정액 분할 매입"),
    "EMH": ("Efficient Market Hypothesis", "가격이 이용 가능한 정보를 반영한다는 가설"),
    "APT": ("Arbitrage Pricing Theory", "다요인 자산가격 모형"),
    "SMB": ("Small Minus Big", "소형−대형 규모 팩터"),
    "HML": ("High Minus Low", "가치−성장 장부가/시가 팩터"),
    "REIT": ("Real Estate Investment Trust", "부동산투자신탁. 부동산 수익을 배분하는 증권"),
    "FOMO": ("Fear Of Missing Out", "소외 불안·충동 매매 심리"),
    "GPU": ("Graphics Processing Unit", "AI 학습·추론 가속 칩"),
    "HBM": ("High Bandwidth Memory", "GPU 옆 고대역폭 메모리"),
    "CAPEX": ("Capital Expenditure", "설비·데이터센터 등 자본 지출"),
    "DCF": ("Discounted Cash Flow", "미래 현금흐름을 할인해 기업가치를 추정하는 방법"),
    "DRIP": ("Dividend Reinvestment Plan", "배당금을 자동으로 동일 종목에 재투자하는 제도"),
    "M&A": ("Mergers & Acquisitions", "기업 합병·인수"),
    "VC": ("Venture Capital", "스타트업·초기 기업에 투자하는 벤처 자본"),
}

# Terms relevant to every corpus phase folder (used when no specific extra terms apply)
PHASE_TERMS: dict[str, list[str]] = {
    "01-foundations": ["PV", "FV", "PMT", "M", "Bucket", "NPV", "IRR", "TVM", "OCF", "FCF", "ROE", "EPS", "EBITDA"],
    "02-economics": ["GDP", "CPI", "β", "IS-LM", "QE", "CAPM", "ERP"],
    "03-markets": ["ETF", "TER", "PER", "PBR", "YTM", "PV", "FV", "REIT", "DCA", "ISA", "IRP"],
    "04-portfolio": ["Bucket", "DCA", "MPT", "β", "ERP", "ETF", "ISA", "IRP", "CAPM", "WACC"],
    "05-behavioral": ["FOMO", "Bucket", "DCA", "ETF"],
    "06-korea-policy": ["ISA", "IRP", "DB", "DC", "CGT", "ETF", "FCF"],
    "07-real-estate": ["REIT", "PV", "IRR", "CAPM", "DCF"],
    "08-advanced": ["CAPM", "WACC", "NPV", "IRR", "APT", "EMH", "SMB", "HML", "β", "ERP", "DCF"],
    "09-corporate-finance": ["WACC", "NPV", "IRR", "FCF", "ROIC", "EBITDA", "DCF", "M&A", "VC"],
    "00-roadmap": ["M", "ISA", "Bucket", "NPV", "ETF", "IRP"],
}


def is_corpus_md(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if rel.suffix != ".md" or rel.name in SKIP_NAMES:
        return False
    if any(p in SKIP_DIRS for p in rel.parts):
        return False
    return rel.parts[0] in PHASE_TERMS


def terms_for_path(path: Path) -> list[str]:
    # Use relative path to get the phase folder correctly
    rel = path.relative_to(ROOT) if path.is_absolute() else path
    folder = rel.parts[0]
    base = PHASE_TERMS.get(folder, list(TERM_DEFS.keys()))
    name = rel.name.lower()
    parts_str = "/".join(rel.parts)
    extra: list[str] = []
    if "tax" in name or "tax" in parts_str:
        extra += ["CGT", "ISA", "IRP", "FCF"]
    if "bond" in name:
        extra += ["YTM", "PV", "WACC"]
    if "pension" in name or "irp" in name or "db" in name or "dc" in name:
        extra += ["DB", "DC", "IRP", "ISA"]
    if "factor" in name:
        extra += ["SMB", "HML", "APT", "β"]
    if "sectors" in parts_str:
        extra += ["GPU", "HBM", "CAPEX", "ETF", "TER"]
    if "reits" in name or "alternatives" in name:
        extra += ["REIT", "ETF", "DCF"]
    if "valuation" in name:
        extra += ["PER", "PBR", "DCF", "FCF", "EBITDA", "WACC"]
    if "monetary" in name or "qe" in name:
        extra += ["QE", "GDP", "CPI"]
    if "asset-prices" in name or "macro-06" in name:
        extra += ["ERP", "β", "CAPM"]
    if "dividend" in name or "buyback" in name:
        extra += ["FCF", "EPS", "DPS", "DRIP", "ISA", "IRP"]
    if "financial-statement" in name or "statements" in name:
        extra += ["EBITDA", "FCF", "ROE", "ROA", "EPS", "PER", "PBR"]
    if "wacc" in name or "capital-structure" in name:
        extra += ["WACC", "CAPM", "DCF", "EBITDA"]
    if "startup" in name or "ma-basics" in name or "vc" in name:
        extra += ["DCF", "IRR", "WACC", "M&A", "VC"]
    out: list[str] = []
    for t in base + extra:
        if t not in out and t in TERM_DEFS:
            out.append(t)
    return out[:8]


def already_has_box(text: str, term: str) -> bool:
    if f'!!! info "{term}' in text:
        return True
    if f'!!! info "{term} (' in text:
        return True
    pat = re.compile(rf'!!! info[^\n]*{re.escape(term)}', re.I)
    return bool(pat.search(text))


def inside_admonition(text: str, pos: int) -> bool:
    """True if pos falls inside an existing !!! info block body."""
    before = text[:pos]
    headers = list(re.finditer(r"^!!! .+$", before, re.M))
    if not headers:
        return False
    last = headers[-1]
    after_header = text[last.end() : pos]
    return "\n" in after_header and not re.search(r"^##+ ", after_header, re.M)


_TABLE_BLOCK = re.compile(
    r"(?:^|\n)(\|[^\n]+\n\|[-: |]+\|\n(?:\|[^\n]+\n)+)",
    re.M,
)


def table_row_spans(body: str) -> list[tuple[int, int]]:
    """Character spans of markdown table blocks in body."""
    spans: list[tuple[int, int]] = []
    for m in _TABLE_BLOCK.finditer(body):
        start = m.start(1)
        spans.append((start, m.end(1)))
    return spans


def inside_table_block(body: str, pos: int, spans: list[tuple[int, int]] | None = None) -> bool:
    if spans is None:
        spans = table_row_spans(body)
    return any(start <= pos < end for start, end in spans)


def section1_body(text: str) -> tuple[int, int, str]:
    m = re.search(r"^## 1\.[^\n]*\n", text, re.M)
    if not m:
        m = re.search(r"^## TL;DR[^\n]*\n", text, re.M)
    if not m:
        return 0, 0, ""
    start = m.end()
    m2 = re.search(r"^## [^1T]", text[start:], re.M)
    if not m2:
        m2 = re.search(r"^## 2[\.\s]", text[start:], re.M)
    end = start + m2.start() if m2 else len(text)
    return start, end, text[start:end]


def make_box(term: str) -> str:
    eng, ko = TERM_DEFS[term]
    return f'!!! info "{term} ({eng})"\n    {ko}.\n\n'


def insert_boxes(text: str, path: Path) -> tuple[str, bool]:
    start, end, body = section1_body(text)
    if not body:
        return text, False
    terms = terms_for_path(path)
    new_body = body
    table_spans = table_row_spans(new_body)
    inserted = 0
    for term in terms:
        if inserted >= 5:
            break
        if already_has_box(text, term):
            continue
        escaped = re.escape(term)
        pattern = re.compile(rf"(?<![A-Za-z0-9_])({escaped})(?![A-Za-z0-9_])", re.I)
        m = pattern.search(new_body)
        if not m and "/" in term:
            continue
        if not m:
            m = re.search(escaped, new_body, re.I)
        if not m:
            continue
        pos = m.start()
        line_start = new_body.rfind("\n", 0, pos) + 1
        line_end = new_body.find("\n", pos)
        if line_end == -1:
            line_end = len(new_body)
        current_line = new_body[line_start:line_end]
        prefix = new_body[line_start:pos]
        abs_pos = start + pos
        if inside_admonition(text, abs_pos):
            continue
        if prefix.strip().startswith("!") or prefix.strip().startswith("|"):
            continue
        if current_line.startswith("    ") or current_line.startswith("\t"):
            continue
        if current_line.strip().startswith("|"):
            continue
        if inside_table_block(new_body, pos, table_spans):
            continue
        if re.match(r"^\s*[-*0-9]+\.", current_line):
            continue
        box = make_box(term)
        new_body = new_body[:line_start] + box + new_body[line_start:]
        table_spans = table_row_spans(new_body)
        inserted += 1
    if inserted == 0 and terms:
        first = terms[0]
        if not already_has_box(text, first):
            anchor = re.search(
                r"(\*\*왜 중요한가[^*]*\*\*:\s*\n)(\s*\|)",
                new_body,
            )
            if anchor and not inside_table_block(new_body, anchor.start(2), table_spans):
                pos = anchor.start(2)
            else:
                m_def = re.search(r"(\*\*정의\*\*:[^\n]+\n\n)", new_body)
                pos = m_def.end() if m_def else 0
            if pos > 0 and not inside_table_block(new_body, pos, table_spans):
                new_body = new_body[:pos] + make_box(first) + new_body[pos:]
                inserted = 1
    if inserted == 0:
        return text, False
    return text[:start] + new_body + text[end:], True


def main() -> int:
    n = 0
    no_info = 0
    for path in sorted(ROOT.rglob("*.md")):
        if not is_corpus_md(path):
            continue
        text = path.read_text(encoding="utf-8")
        if "## 메타" not in text:
            continue
        new_text, changed = insert_boxes(text, path)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
        if "!!! info" not in new_text:
            no_info += 1
    print(f"Added info boxes in {n} files; {no_info} corpus files still without info")
    return 0


if __name__ == "__main__":
    sys.exit(main())
