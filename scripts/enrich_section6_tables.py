#!/usr/bin/env python3
"""Replace generic §6 variable tables with symbols from math + §4 glossary."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"scripts", ".tmp_l3", "site", "webdocs", ".venv", "private", ".git", ".github", "docs", "references"}
SKIP_NAMES = {"README.md", "sources.md"}

GENERIC_ROW = re.compile(r"\| \(아래 식 참고\) \|[^\n]+\|\n")
GENERIC_TABLE = re.compile(
    r"\| 기호 \| 이름 \| 이 식에서 의미 \|\n\|[-| ]+\|\n\| \(아래 식 참고\) \|[^\n]+\|\n\n",
    re.M,
)
SYMBOL_IN_MATH = re.compile(
    r"\\(?:alpha|beta|gamma|delta|sigma|tau|pi|epsilon)_\{?\\?text\{([^}]+)\}|([A-Za-z]+)\}?|"
    r"\\?(?:alpha|beta|gamma|delta|sigma|tau|pi|epsilon)_\{?([A-Za-z_]+)\}?|"
    r"\b(NPV|IRR|PV|FV|PMT|WACC|CAPM|ERP|YTM|FCF|OCF|TER|ISA|IRP|DB|DC|GDP|CPI|MRR|ROE|ROIC|PER|P/E|EPS|DDM|APT|SMB|HML|RMW|CMA|MKT)\b|"
    r"\b([A-Z][a-z]?_\{?\\?text\{[^}]+\}\}?|[A-Z][a-z]?)_\{?\\?text\{([^}]+)\}\}?|"
    r"([CFS]_[0-9a-zA-Z_]+|R_f|E\[R_m\]|T_\{[^}]+\}|L_\{[^}]+\})",
    re.I,
)
SECTION4_TERMS = re.compile(
    r"^## 4\.[^\n]*\n+?(?:\|[^\n]+\|\n)+((?:\|[^\n]+\|\n)+)",
    re.M,
)


def is_corpus_md(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if rel.suffix != ".md" or rel.name in SKIP_NAMES:
        return False
    if any(p in SKIP_DIRS for p in rel.parts):
        return False
    return rel.parts[0] in {
        "00-roadmap",
        "01-foundations",
        "02-economics",
        "03-markets",
        "04-portfolio",
        "05-behavioral",
        "06-korea-policy",
        "07-real-estate",
        "08-advanced",
        "09-corporate-finance",
    }


def parse_section4_terms(text: str) -> dict[str, str]:
    terms: dict[str, str] = {}
    m = SECTION4_TERMS.search(text)
    if not m:
        return terms
    for line in m.group(1).splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in ("용어", "약어", "------"):
            continue
        key = re.sub(r"\\[a-zA-Z_{}\s\d^().]+", "", cells[0]).strip()
        key = key.split("(")[0].strip()
        if not key:
            key = cells[0].strip()
        desc = cells[-1] if cells else ""
        if len(desc) > 60:
            desc = desc[:57] + "…"
        terms[key.upper()] = desc
        terms[key] = desc
        if len(cells) >= 3:
            eng = cells[1].strip()
            if eng and len(eng) < 20:
                terms[eng.upper()] = desc
    return terms


def extract_symbols(section6: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    def add(sym: str) -> None:
        sym = sym.strip().replace(" ", "")
        if not sym or sym in seen or len(sym) > 24:
            return
        if sym in ("text", "frac", "sum", "min", "max", "cdot", "leq", "geq", "stackrel"):
            return
        seen.add(sym)
        found.append(sym)

    for m in SYMBOL_IN_MATH.finditer(section6):
        for g in m.groups():
            if g:
                add(g)
    for m in re.finditer(r"\\?([A-Za-z]+)_\{?\\?text\{([^}]+)\}\}?", section6):
        add(f"{m.group(1)}_{{{m.group(2)}}}")
    for m in re.finditer(r"\b([A-Z][a-z]?)_([A-Za-z0-9]+)\b", section6):
        add(f"{m.group(1)}_{m.group(2)}")
    return found[:8]


def build_table(symbols: list[str], terms4: dict[str, str]) -> str:
    lines = [
        "| 기호 | 이름 | 이 식에서 의미 |",
        "|------|------|----------------|",
    ]
    for sym in symbols:
        key = sym.upper().replace("{", "").replace("}", "")
        desc = terms4.get(sym, terms4.get(key, "§4·본문 정의 참고"))
        name = sym.replace("_", " ").replace("\\", "")
        lines.append(f"| {sym} | {name} | {desc} |")
    return "\n".join(lines) + "\n\n"


def has_quality_table(chunk: str) -> bool:
    if GENERIC_ROW.search(chunk):
        return False
    rows = [ln for ln in chunk.splitlines() if ln.startswith("|") and "---" not in ln]
    data_rows = [r for r in rows if "기호" not in r and "(아래 식 참고)" not in r]
    return len(data_rows) >= 3


def enrich_section6(text: str) -> tuple[str, bool]:
    m6 = re.search(r"^## 6[\.\s]", text, re.M)
    if not m6:
        return text, False
    tail = text[m6.start() :]
    m_end = re.search(r"^## [^6]", tail[10:], re.M)
    section6 = tail[: m_end.start() + 10] if m_end else tail
    if "해당 없음" in section6[:400] and "\\[" not in section6:
        return text, False

    terms4 = parse_section4_terms(text)
    symbols = extract_symbols(section6)
    if len(symbols) < 2:
        symbols = list(terms4.keys())[:6]
    if len(symbols) < 2:
        return text, False

    table = build_table(symbols, terms4)
    new_section6 = GENERIC_TABLE.sub(table, section6, count=1)
    if new_section6 == section6 and GENERIC_ROW.search(section6):
        new_section6 = GENERIC_ROW.sub("", section6)
        dm = re.search(r"\\\[\s*\n", new_section6)
        if dm:
            pos = dm.start()
            new_section6 = new_section6[:pos] + table + new_section6[pos:]
    if new_section6 == section6:
        if has_quality_table(section6[:1200]):
            return text, False
        dm = re.search(r"\\\[\s*\n", section6)
        if dm and not has_quality_table(section6[: dm.start()]):
            pos = dm.start()
            new_section6 = section6[:pos] + table + section6[pos:]
        else:
            return text, False

    return text[: m6.start()] + new_section6 + text[m6.start() + len(section6) :], True


def main() -> int:
    n = 0
    for path in sorted(ROOT.rglob("*.md")):
        if not is_corpus_md(path):
            continue
        text = path.read_text(encoding="utf-8")
        if "## 6" not in text:
            continue
        new_text, changed = enrich_section6(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
    print(f"Enriched §6 tables in {n} files")
    remaining = sum(
        1
        for p in ROOT.rglob("*.md")
        if is_corpus_md(p) and "(아래 식 참고)" in p.read_text(encoding="utf-8")
    )
    print(f"Remaining generic §6 rows: {remaining}")
    return 1 if remaining else 0


if __name__ == "__main__":
    sys.exit(main())
