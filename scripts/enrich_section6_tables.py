#!/usr/bin/env python3
"""Replace generic §6 variable tables with symbols from equations + §4 glossary."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _corpus import iter_corpus_md
from populate_section4a import TABLE4_PATTERNS, find_table4

GENERIC_ROW = re.compile(
    r"\| \(아래 식 참고\) \| — \| §4 본표·§0 기호 열 확인 \|\n?",
)
GENERIC_BLOCK = re.compile(
    r"\n\n\| 기호 \| 이름 \| 이 식에서 의미 \|\n"
    r"\|[-| ]+\|\n"
    r"\| \(아래 식 참고\) \| — \| §4 본표·§0 기호 열 확인 \|\n\n",
)
DISPLAY_MATH = re.compile(r"\\\[\s*\n([\s\S]*?)\\\]", re.M)
LATEX_SYM = re.compile(
    r"\\(?:text|mathrm)\{([^}]+)\}"
    r"|\\([a-zA-Z]+)"
    r"|(?<![a-zA-Z])([A-Z][A-Z0-9_]*(?:_\{[^}]+\}|_[0-9]+)?)"
    r"|([a-z][a-z0-9]*(?:_\{[^}]+\}|_[0-9]+)?)",
)
SKIP_SYMS = {
    "frac",
    "sum",
    "times",
    "quad",
    "qquad",
    "text",
    "mathrm",
    "left",
    "right",
    "approx",
    "Rightarrow",
    "uparrow",
    "downarrow",
    "perp",
    "annuity",
    "bond",
    "firm",
    "per",
    "the",
    "and",
    "or",
    "vs",
    "max",
    "min",
}


def parse_section4_symbols(text: str) -> dict[str, tuple[str, str]]:
    m4 = find_table4(text)
    if not m4:
        return {}
    block = m4.group(1) if hasattr(m4, "group") else ""
    out: dict[str, tuple[str, str]] = {}
    for line in block.strip().splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in ("용어", "------", "약어"):
            continue
        term = re.sub(r"\\[a-zA-Z_{}\s\d^().]+", "", cells[0]).strip()
        if not term or term.startswith("("):
            continue
        if len(cells) >= 4:
            ko, definition = cells[1], cells[3]
        elif len(cells) == 3:
            ko, definition = cells[1], cells[2]
        else:
            ko, definition = cells[0], cells[1]
        meaning = (definition or ko).split("—")[0].split("(")[0].strip()
        if len(meaning) > 64:
            meaning = meaning[:61] + "…"
        key = term.upper().replace(" ", "")
        out[key] = (ko or term, meaning)
        out[term] = (ko or term, meaning)
    return out


def symbols_in_latex(body: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for m in LATEX_SYM.finditer(body):
        raw = next(g for g in m.groups() if g)
        if raw in SKIP_SYMS or raw.isdigit():
            continue
        sym = raw.strip()
        if sym in seen:
            continue
        seen.add(sym)
        found.append(sym)
    return found[:8]


def build_table(symbols: list[str], lookup: dict[str, tuple[str, str]]) -> str:
    rows = [
        "",
        "| 기호 | 이름 | 이 식에서 의미 |",
        "|------|------|----------------|",
    ]
    for sym in symbols[:8]:
        key = sym.upper().replace(" ", "")
        ko, meaning = lookup.get(sym, lookup.get(key, (sym, "§4·본문 정의 참고")))
        rows.append(f"| \\({sym}\\) | {ko} | {meaning} |")
    return "\n".join(rows) + "\n\n"


def process(text: str) -> str:
    if "(아래 식 참고)" not in text:
        return text
    lookup = parse_section4_symbols(text)
    m6 = re.search(r"^## 6[\.\s]", text, re.M)
    if not m6:
        return text
    head, s6 = text[: m6.start()], text[m6.start() :]

    def repl_block(match: re.Match[str]) -> str:
        after = s6[match.end() :]
        dm = DISPLAY_MATH.search(after)
        if not dm:
            return match.group(0)
        syms = symbols_in_latex(dm.group(1))
        if not syms:
            return match.group(0)
        return build_table(syms, lookup)

    new_s6 = GENERIC_BLOCK.sub(repl_block, s6)
    if new_s6 == s6:
        # single-row generic without leading double newline
        pos = 0
        while True:
            gm = GENERIC_ROW.search(new_s6, pos)
            if not gm:
                break
            after = new_s6[gm.end() :]
            dm = DISPLAY_MATH.search(after)
            if dm:
                syms = symbols_in_latex(dm.group(1))
                if syms:
                    table = build_table(syms, lookup).rstrip() + "\n"
                    new_s6 = new_s6[: gm.start()] + table + new_s6[gm.end() :]
                    pos = gm.start() + len(table)
                    continue
            pos = gm.end()
    return head + new_s6


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new = process(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            n += 1
    print(f"Enhanced §6 tables in {n} files")
    remaining = sum(
        1 for p in iter_corpus_md() if "(아래 식 참고)" in p.read_text(encoding="utf-8")
    )
    print(f"Remaining generic rows: {remaining}")
    return 1 if remaining else 0


if __name__ == "__main__":
    sys.exit(main())
