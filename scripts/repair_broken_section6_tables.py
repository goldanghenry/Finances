#!/usr/bin/env python3
"""Repair common §6 table corruption (broken separators, placeholder rows)."""

from __future__ import annotations

import re
import sys

from _corpus import iter_corpus_md
from _gold_polish import TEMPLATE_READING_FULL, strip_template_reading_global
from repair_corpus_mechanical import SYMBOL_GLOSS, lookup_meaning, lookup_name, parse_section4_terms

VAR_HEADER = "| 기호 | 이름 | 이 식에서 의미 |"
GOOD_SEP = "|------|------|----------------|"
PLACEHOLDER_MEANING = re.compile(
    r"이\(가\) 이 식에서 맡는 역할|§4·본문 정의 참고|본문 §4·식 맥락 참고|\[TODO:meaning\]"
)
# Separator row with placeholder text in any column
BAD_SEP = re.compile(
    r"^\|(?:[^|\n]*\|){2}[^|\n]*이\(가\) 이 식에서 맡는 역할[^|\n]*\|\s*$",
    re.M,
)
BAD_SEP_GLOSS = re.compile(
    r"^\|\s*[-:\s|]+\|\s*[-:\s|]+\|\s*(?:위\s*식의\s*)?[-:\s|]+\|\s*$",
    re.M,
)
JUNK_SYMBOL = re.compile(
    r"^\\?\(?\\?(alpha|cdot|월|연금|일반|text)\b",
    re.I,
)


def latex_display(latex: str) -> str:
    """Wrap raw LaTeX (e.g. \\alpha_\\text{ISA}) for markdown table cell."""
    s = latex.strip()
    if s.startswith("\\(") and s.endswith("\\)"):
        return s
    if not s.startswith("\\"):
        s = "\\" + s if s[0].isalpha() else s
    return f"\\({s}\\)"


def bare_key(latex: str) -> str:
    s = latex.strip().strip("$")
    s = re.sub(r"^\\?\(?\\?", "", s)
    s = re.sub(r"\\\)?$", "", s)
    s = s.replace("\\text{", "_").replace("}", "").replace("{", "")
    s = s.replace("\\", "").replace("(", "").replace(")", "")
    return s.replace(" ", "")


def extract_equation_symbols(equation: str) -> list[str]:
    """Pull symbols from display math in document order (deduped)."""
    found: list[str] = []
    seen: set[str] = set()
    skip_labels = {"월", "연금", "일반", "text", "quad"}

    def add(latex: str) -> None:
        key = bare_key(latex)
        if not key or key in seen or key in skip_labels:
            return
        if JUNK_SYMBOL.search(latex) and "_" not in latex and key not in SYMBOL_GLOSS:
            return
        if key in ("cdot", "leq", "stackrel"):
            return
        seen.add(key)
        found.append(latex)

    for m in re.finditer(r"\\alpha_\\text\{([^}]+)\}", equation):
        add(f"\\alpha_\\text{{{m.group(1)}}}")
    for m in re.finditer(r"L_\\text\{([^}]+)\}", equation):
        add(f"L_\\text{{{m.group(1)}}}")
    for m in re.finditer(
        r"\b(NPV|IRR|PV|FV|PMT|WACC|CAPM|ERP|YTM|FCF|OCF|TER|ISA|IRP|DB|DC|GDP|CPI|M)\b",
        equation,
    ):
        add(m.group(1))
    for m in re.finditer(r"\\?([A-Za-z])_\{?\\?text\{([^}]+)\}\}?", equation):
        if m.group(2) in skip_labels:
            continue
        add(f"\\{m.group(1)}_\\text{{{m.group(2)}}}")
    for m in re.finditer(r"\b([A-Z][a-z]?)_([A-Za-z0-9]+)\b", equation):
        add(f"{m.group(1)}_{m.group(2)}")
    for m in re.finditer(r"\\beta\b|\\sigma\b|\\pi\b", equation):
        add(m.group(0))
    return found[:8]


def is_corrupt_table(block: str) -> bool:
    if BAD_SEP.search(block):
        return True
    rows = [ln for ln in block.splitlines() if ln.strip().startswith("|") and "---" not in ln]
    data = [r for r in rows if "기호" not in r]
    if not data:
        return False
    bad = sum(1 for r in data if PLACEHOLDER_MEANING.search(r))
    junk = sum(1 for r in data if JUNK_SYMBOL.search(r.split("|")[1] if "|" in r else ""))
    return bad >= max(1, len(data) // 2) or junk >= 2


def rebuild_var_table(equation: str, terms4: dict[str, str]) -> str:
    symbols = extract_equation_symbols(equation)
    if len(symbols) < 2:
        symbols = ["\\alpha_\\text{ISA}", "M"]
    lines = [VAR_HEADER, GOOD_SEP]
    for sym in symbols:
        disp = latex_display(sym)
        key = bare_key(sym)
        name = lookup_name(key)
        mean = lookup_meaning(key, terms4)
        if PLACEHOLDER_MEANING.search(mean) or mean == "본문 §4·식 맥락 참고":
            gloss = SYMBOL_GLOSS.get(key) or SYMBOL_GLOSS.get(key.upper())
            if gloss:
                name, mean = gloss
        lines.append(f"| {disp} | {name} | {mean} |")
    return "\n".join(lines) + "\n\n"


def repair_section6_tables(text: str) -> tuple[str, bool]:
    changed = False
    m6 = re.search(r"^## 6[\.\s]", text, re.M)
    if not m6:
        return text, False
    terms4 = parse_section4_terms(text)
    tail = text[m6.start() :]
    m_end = re.search(r"^## [^6]", tail[10:], re.M)
    section6 = tail[: m_end.start() + 10] if m_end else tail

    pos = 0
    while True:
        dm = re.search(r"\\\[\s*\n", section6[pos:])
        if not dm:
            break
        eq_start = pos + dm.start()
        eq_end = section6.find("\\]", eq_start)
        if eq_end == -1:
            break
        equation = section6[eq_start:eq_end]
        before = section6[max(0, eq_start - 2500) : eq_start]
        if "이 식에서 의미" not in before:
            pos = eq_start + 1
            continue
        hdr = list(re.finditer(r"\| 기호 \| 이름 \| 이 식에서 의미 \|", before))
        if not hdr:
            pos = eq_start + 1
            continue
        hpos = hdr[-1].start()
        table_chunk = before[hpos:]
        if not is_corrupt_table(table_chunk):
            pos = eq_start + 1
            continue
        new_table = rebuild_var_table(equation, terms4)
        section6 = section6[:hpos] + new_table + section6[eq_start:]
        changed = True
        pos = hpos + len(new_table)

    if changed:
        text = text[: m6.start()] + section6 + text[m6.start() + len(section6) :]
    return text, changed


def scrub_orphan_lines(text: str) -> tuple[str, bool]:
    """Drop mangled single-line table fragments and DEPTH-STANDARD orphans."""
    if "이(가) 이 식에서 맡는 역할" not in text and "/DEPTH-STANDARD" not in text:
        return text, False
    out: list[str] = []
    changed = False
    for ln in text.splitlines():
        if re.match(r"^/DEPTH-STANDARD\.md\)", ln.strip()):
            changed = True
            continue
        if "이(가) 이 식에서 맡는 역할" in ln and ln.count("|") < 3:
            changed = True
            continue
        if re.search(r"\\\)\s*\|", ln) and "이(가) 이 식에서" in ln:
            changed = True
            continue
        if re.match(r"^\s*\\?[^|\n]*\\\)\s*\|", ln) and "이(가)" in ln:
            changed = True
            continue
        out.append(ln)
    return "\n".join(out), changed


def fix_placeholder_rows(text: str) -> tuple[str, bool]:
    """Fix individual §6 rows that still use the old placeholder meaning."""
    if "이(가) 이 식에서 맡는 역할" not in text:
        return text, False
    terms4 = parse_section4_terms(text)
    changed = False

    def repl(m: re.Match[str]) -> str:
        nonlocal changed
        sym, name, mean = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        if "기호" in sym or re.fullmatch(r"[\s\-]+", sym):
            if "이(가) 이 식에서" in mean:
                changed = True
                return GOOD_SEP
            return m.group(0)
        if "이(가) 이 식에서 맡는 역할" not in mean:
            return m.group(0)
        key = bare_key(sym)
        new_name = lookup_name(key) if name in ("", key, sym) or "text" in name else name
        new_mean = lookup_meaning(key, terms4)
        gloss = SYMBOL_GLOSS.get(key) or SYMBOL_GLOSS.get(key.upper())
        if gloss and (new_mean == "본문 §4·식 맥락 참고" or "이(가)" in new_mean):
            new_name, new_mean = gloss
        if new_mean == mean and new_name == name:
            new_mean = "본문 §4·식 맥락 참고"
        changed = True
        return f"| {sym} | {new_name} | {new_mean} |"

    new_text = re.sub(
        r"^\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|\s*$",
        repl,
        text,
        flags=re.M,
    )
    return new_text, changed


def repair(text: str) -> tuple[str, bool]:
    changed = False
    t, c = strip_template_reading_global(text)
    if c:
        text, changed = t, True
    if BAD_SEP.search(text):
        text = BAD_SEP.sub(GOOD_SEP, text)
        changed = True
    if BAD_SEP_GLOSS.search(text) or "위 식의 ------" in text:
        text2 = BAD_SEP_GLOSS.sub(GOOD_SEP, text)
        text2 = re.sub(
            r"^\|\s*------\s*\|\s*------\s*\|\s*위\s*식의\s*------\s*\|\s*$",
            GOOD_SEP,
            text2,
            flags=re.M,
        )
        if text2 != text:
            text = text2
            changed = True
    t2, c2 = repair_section6_tables(text)
    if c2:
        text, changed = t2, True
    t3, c3 = fix_placeholder_rows(text)
    if c3:
        text, changed = t3, True
    t4, c4 = scrub_orphan_lines(text)
    if c4:
        text, changed = t4, True
    frag = re.sub(
        r"\n\.\s*숫자는 \[DEPTH-STANDARD\][^\n]+\n",
        "\n",
        text,
    )
    if frag != text:
        text = frag
        changed = True
    text2 = re.sub(
        r"\*\*읽는 법\*\*:[^\n]*\| 기호 \| 이름 \| 이 식에서 의미 \|[\s\S]*?로 위 변수표와 같다\.[^\n]*\n",
        "\n",
        text,
    )
    if text2 != text:
        text = text2
        changed = True
    return text, changed


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, changed = repair(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
    print(f"Repaired §6 table corruption in {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
