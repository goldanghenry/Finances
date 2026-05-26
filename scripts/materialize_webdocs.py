#!/usr/bin/env python3
"""Replace webdocs symlinks with real copies so MkDocs / awesome-pages resolve nav paths."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBDOCS = ROOT / "webdocs"
SYNC_DIRS = (
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
    "references",
)


def materialize_entry(entry: Path) -> None:
    if not entry.is_symlink():
        return
    target = entry.resolve()
    entry.unlink()
    if target.is_dir():
        shutil.copytree(target, entry, symlinks=False)
    else:
        shutil.copy2(target, entry)


def main() -> None:
    if not WEBDOCS.is_dir():
        print(f"Missing {WEBDOCS}", file=sys.stderr)
        sys.exit(1)

    for child in sorted(WEBDOCS.iterdir()):
        if child.name.startswith("."):
            continue
        materialize_entry(child)

    # MkDocs assets under docs/ (not content symlinks)
    for asset_dir in ("javascripts", "stylesheets"):
        src = ROOT / "docs" / asset_dir
        dst = WEBDOCS / asset_dir
        if not src.is_dir():
            continue
        if dst.exists():
            if dst.is_symlink():
                dst.unlink()
            elif dst.is_dir():
                shutil.rmtree(dst)
        shutil.copytree(src, dst)

    synced = 0
    for dirname in SYNC_DIRS:
        src_dir = ROOT / dirname
        dst_dir = WEBDOCS / dirname
        if not src_dir.is_dir() or not dst_dir.is_dir():
            continue
        for src in src_dir.rglob("*.md"):
            rel = src.relative_to(src_dir)
            dst = dst_dir / rel
            if dst.is_symlink():
                dst.unlink()
            if not dst.exists() or dst.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                synced += 1
    print(f"Materialized webdocs under {WEBDOCS}; synced {synced} markdown files")


if __name__ == "__main__":
    main()
