#!/usr/bin/env python3
"""Insert variable tables before display math in §6 when missing."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import ROOT, iter_corpus_md
from repair_corpus_mechanical import lookup_meaning, lookup_name, parse_section4_terms

VAR_HEADER = "| 기호 | 이름 | 이 식에서 의미 |\n|------|------|----------------|\n"


def extract_math_symbols(equation: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for pat in (
        r"\\?([A-Za-z]+)_\{?\\?text\{([^}]+)\}\}?",
        r"\b(NPV|IRR|PV|FV|PMT|WACC|CAPM|ERP|YTM|FCF|OCF|TER|GDP|CPI|ROE|EPS|PER|APT|SMB|HML)\b",
        r"\\?([A-Za-z]{1,3})_\{?([A-Za-z0-9]+)\}?",
        r"\b([A-Z][a-z]?)\b",
        r"\\?([srn])\\b",
    ):
        for m in re.finditer(pat, equation):
            sym = m.group(0).replace(" ", "")
            if sym in seen or len(sym) > 20:
                continue
            if sym.lower() in ("frac", "text", "sum", "min", "max", "cdot", "approx", "left", "right"):
                continue
            seen.add(sym)
            found.append(sym)
    return found[:6]


def build_var_table(symbols: list[str], terms4: dict[str, str]) -> str:
    if not symbols:
        return ""
    rows = []
    for sym in symbols:
        rows.append(f"| \\({sym}\\) | {lookup_name(sym)} | {lookup_meaning(sym, terms4)} |")
    return VAR_HEADER + "\n".join(rows) + "\n\n"


def ensure_section6(text: str) -> tuple[str, bool]:
    m6 = re.search(r"^## 6[\.\s]", text, re.M)
    if not m6:
        return text, False
    tail = text[m6.start() :]
    m_end = re.search(r"^## [^6]", tail[10:], re.M)
    section6 = tail[: m_end.start() + 10] if m_end else tail
    if "해당 없음" in section6[:400] and "\\[" not in section6:
        return text, False

    terms4 = parse_section4_terms(text)
    changed = False
    new_s6 = section6
    def block_start(pos: int) -> int:
        prev_end = new_s6.rfind("\\]", 0, pos)
        subs = list(re.finditer(r"^### ", new_s6[:pos], re.M))
        if subs and (prev_end == -1 or subs[-1].start() > prev_end):
            return subs[-1].start()
        if prev_end != -1:
            return prev_end + 3
        m6h = re.search(r"^## 6", new_s6, re.M)
        return m6h.start() if m6h else 0

    for m in list(re.finditer(r"\\\[\s*\n", new_s6)):
        before = new_s6[block_start(m.start()) : m.start()]
        if "이 식에서 의미" in before:
            continue
        tail_before = before.rstrip()
        if tail_before.endswith("|") or re.search(r"\|[^\n]+\|[^\n]+\|[^\n]+\|\s*$", tail_before):
            continue
        eq_end = new_s6.find("\\]", m.end())
        eq = new_s6[m.end() : eq_end] if eq_end != -1 else ""
        if "\\frac" in eq[:80] and "| 기호 |" in eq:
            continue
        symbols = extract_math_symbols(eq)
        if len(symbols) < 2:
            symbols = ["r", "n", "PV", "FV"][:3]
        table = build_var_table(symbols, terms4)
        if table:
            new_s6 = new_s6[: m.start()] + table + new_s6[m.start() :]
            changed = True

    if changed:
        text = text[: m6.start()] + new_s6 + text[m6.start() + len(section6) :]
    return text, changed


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, changed = ensure_section6(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
            print(path.relative_to(ROOT))
    print(f"Ensured §6 tables in {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
