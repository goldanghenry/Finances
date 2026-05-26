#!/usr/bin/env python3
"""Fill §6 variable table placeholders from §4 + SYMBOL_GLOSS (no natural-language generation)."""

from __future__ import annotations

import re
import sys

from _corpus import iter_corpus_md
from _gold_polish import fix_variable_row, is_placeholder_meaning, section6_body
from repair_corpus_mechanical import lookup_meaning, parse_section4_terms


def enrich(text: str) -> tuple[str, bool]:
    if not section6_body(text):
        return text, False
    terms4 = parse_section4_terms(text)
    changed = False

    def repl_row(m: re.Match[str]) -> str:
        nonlocal changed
        sym, name, mean = m.group(1), m.group(2), m.group(3)
        if "이 식에서 의미" in sym:
            return m.group(0)
        if not is_placeholder_meaning(mean) and name.strip() not in ("", sym.strip()):
            return m.group(0)
        ns, nn, nm = fix_variable_row(sym, name, mean, terms4)
        if is_placeholder_meaning(nm):
            nm = lookup_meaning(ns, terms4)
        if (ns, nn, nm) != (sym, name, mean):
            changed = True
        return f"| {ns} | {nn} | {nm} |"

    new_text = re.sub(
        r"^\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|\s*$",
        repl_row,
        text,
        flags=re.M,
    )
    return new_text, changed


def main() -> int:
    n = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, changed = enrich(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
    print(f"Enriched §6 variable tables in {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
