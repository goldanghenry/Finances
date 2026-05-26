#!/usr/bin/env python3
"""Warn on missing §0, meta difficulty, §6 variable table before equations."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"scripts", ".tmp_l3", "site", "webdocs", ".venv", "private", ".git", ".github", "docs", "references"}


def check(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    issues: list[str] = []
    if "## 메타" not in text:
        return issues
    if not re.search(r"^## 0\. 이 편 읽기 전", text, re.M):
        issues.append("missing §0")
    if not re.search(r"\| 난이도 \|", text):
        issues.append("missing meta 난이도")
    elif "READER-GUIDE" not in text and "reader-guide" not in text.lower():
        issues.append("난이도 without READER-GUIDE link")
    m6 = re.search(r"^## 6[\.\s]", text, re.M)
    if m6:
        s6 = text[m6.start() :]
        next_sec = re.search(r"^## [^6]", s6[10:], re.M)
        s6_body = s6[: next_sec.start() + 10] if next_sec else s6
        if "\\[" in s6_body or "$$" in s6_body:
            if "기호" not in s6_body[:800] and "변수" not in s6_body[:800]:
                if "해당 없음" not in s6_body[:200]:
                    issues.append("§6 may lack variable table")
    if ("L3" in text or "L4" in text) and not re.search(r"^### 4a\.|^## 4a\.", text, re.M):
        if "## 4." in text:
            issues.append("missing §4a (L3/L4)")
    return issues


def main() -> int:
    bad = 0
    for path in sorted(ROOT.rglob("*.md")):
        if any(p in SKIP for p in path.parts):
            continue
        if path.name == "README.md":
            continue
        issues = check(path)
        if issues:
            bad += 1
            print(f"{path.relative_to(ROOT)}: {', '.join(issues)}")
    print(f"\n{bad} files with warnings")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
