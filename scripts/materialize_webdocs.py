#!/usr/bin/env python3
"""Replace webdocs symlinks with real copies so MkDocs / awesome-pages resolve nav paths."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBDOCS = ROOT / "webdocs"


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

    # MkDocs extra_javascript (not a content symlink)
    js_src = ROOT / "docs" / "javascripts"
    js_dst = WEBDOCS / "javascripts"
    if js_src.is_dir():
        if js_dst.exists():
            if js_dst.is_symlink():
                js_dst.unlink()
            elif js_dst.is_dir():
                shutil.rmtree(js_dst)
        shutil.copytree(js_src, js_dst)

    print(f"Materialized webdocs under {WEBDOCS}")


if __name__ == "__main__":
    main()
