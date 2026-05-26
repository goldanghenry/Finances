"""Shared corpus path helpers for maintenance scripts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"scripts", ".tmp_l3", "site", "webdocs", ".venv", "private", ".git", ".github", "docs", "references"}
SKIP_NAMES = {"README.md", "sources.md"}
CORPUS_TOP = {
    "01-foundations",
    "02-economics",
    "03-markets",
    "04-portfolio",
    "05-behavioral",
    "06-korea-policy",
    "07-real-estate",
    "08-advanced",
    "09-corporate-finance",
    "00-roadmap",
}


def is_corpus_md(path: Path) -> bool:
    if path.suffix != ".md" or path.name in SKIP_NAMES:
        return False
    if any(p in SKIP_DIRS for p in path.parts):
        return False
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return False
    if rel.parts[0] not in CORPUS_TOP:
        return False
    return "## 메타" in path.read_text(encoding="utf-8", errors="ignore")


def iter_corpus_md() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.md") if is_corpus_md(p))
