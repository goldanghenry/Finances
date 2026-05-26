#!/usr/bin/env python3
"""Fill §0 prereq from ## 2 선수 links (replace placeholder)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"scripts", ".tmp_l3", "site", "webdocs", ".venv", "private", ".git", ".github", "docs", "references"}
SKIP_NAMES = {"README.md", "sources.md"}
PLACEHOLDER = "§2 선수 문서 참고"
SECTION0_PREREQ = re.compile(r"^(\| \*\*선수\*\* \| ).*(\|)\s*$", re.M)
SECTION2 = re.compile(
    r"^## 2\.[^\n]*\n+?\*\*선수\*\*:\s*\n((?:- \[[^\n]+\]\([^\n]+\)[^\n]*\n)+)",
    re.M,
)
LINK_ITEM = re.compile(r"- \[([^\]]+)\]\(([^)]+)\)")


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


def parse_prereq_links(text: str) -> list[str]:
    m = SECTION2.search(text)
    if not m:
        return []
    items: list[str] = []
    for label, href in LINK_ITEM.findall(m.group(1)):
        label = label.strip()
        href = href.strip()
        if href.endswith(".md"):
            items.append(f"[{label}]({href})")
        else:
            items.append(f"[{label}]({href})")
    return items[:2]


def default_prereq(path: Path) -> str:
    name = path.name
    folder = path.parts[0] if path.parts else ""
    if name == "compound-interest-and-time-value.md":
        return "없음 (Phase 0 첫 권장)"
    if name == "cash-flow-basics.md":
        return "[compound-interest-and-time-value](compound-interest-and-time-value.md)"
    if folder == "02-economics" and name in ("microeconomics-basics.md", "macroeconomics-basics.md"):
        return "[compound-interest-and-time-value](../01-foundations/compound-interest-and-time-value.md)"
    if folder == "02-economics" and name.startswith("micro-"):
        return "[microeconomics-basics](microeconomics-basics.md)"
    if folder == "02-economics" and name.startswith("macro-"):
        return "[macroeconomics-basics](macroeconomics-basics.md)"
    if folder == "03-markets" and "sectors" in path.parts:
        return "[sector-investing-framework](sector-investing-framework.md)"
    if folder == "03-markets":
        return "[stocks-equities-intro](stocks-equities-intro.md)"
    if folder == "04-portfolio":
        return "[time-horizon-and-buckets](time-horizon-and-buckets.md)"
    if folder == "06-korea-policy" and "tax" in path.parts:
        return "[investment-tax-overview](investment-tax-overview.md)"
    if folder == "06-korea-policy":
        return "[isa](isa.md)"
    if folder == "08-advanced":
        return "[capm-and-risk-return](capm-and-risk-return.md)"
    if folder == "09-corporate-finance":
        return "[time-value-npv-irr](../01-foundations/time-value-npv-irr.md)"
    if folder == "00-roadmap":
        return "[STUDY-START](STUDY-START.md)"
    return "없음"


def enrich_prereq(text: str, path: Path) -> tuple[str, bool]:
    if "## 0." not in text or PLACEHOLDER not in text:
        return text, False
    links = parse_prereq_links(text)
    if links:
        new_val = " · ".join(links)
    else:
        new_val = default_prereq(path)
    if PLACEHOLDER not in text:
        return text, False

    def repl(m: re.Match[str]) -> str:
        current = m.group(0)
        if PLACEHOLDER not in current and "§2 선수" not in current:
            return current
        if links or new_val != PLACEHOLDER:
            return f"{m.group(1)}{new_val}{m.group(2)}"
        return current

    new_text = SECTION0_PREREQ.sub(repl, text, count=1)
    return new_text, new_text != text


def main() -> int:
    n = 0
    for path in sorted(ROOT.rglob("*.md")):
        if not is_corpus_md(path):
            continue
        text = path.read_text(encoding="utf-8")
        new_text, changed = enrich_prereq(text, path)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            n += 1
            print(path.relative_to(ROOT))
    print(f"Updated §0 prereq in {n} files")
    remaining = sum(
        1
        for p in ROOT.rglob("*.md")
        if is_corpus_md(p) and PLACEHOLDER in p.read_text(encoding="utf-8")
    )
    print(f"Remaining placeholder: {remaining}")
    return 1 if remaining else 0


if __name__ == "__main__":
    sys.exit(main())
