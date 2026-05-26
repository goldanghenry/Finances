#!/usr/bin/env python3
"""Inject Phase reading-order nav into mkdocs.yml from docs/phase-reading-order.yaml."""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "docs" / "phase-reading-order.yaml"
MKDOCS_PATH = ROOT / "mkdocs.yml"
MARKER_START = "# AUTO-NAV-START"
MARKER_END = "# AUTO-NAV-END"


def build_nav_block(nav: list[dict]) -> str:
    lines = [MARKER_START, "nav:"]
    for section in nav:
        title = section["title"]
        items = section.get("items", [])
        lines.append(f'  - "{title}":')
        for item in items:
            if isinstance(item, str):
                lines.append(f"    - {item}")
            elif isinstance(item, dict):
                for label, path in item.items():
                    lines.append(f'    - "{label}": {path}')
            else:
                raise TypeError(f"nav item must be str or dict, got {type(item)}")
    lines.append(MARKER_END)
    return "\n".join(lines) + "\n"


def inject_nav(mkdocs_text: str, nav_block: str) -> str:
    pattern = re.compile(
        rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}\n?",
        re.DOTALL,
    )
    if pattern.search(mkdocs_text):
        return pattern.sub(nav_block, mkdocs_text)
    # Insert after site_dir line
    anchor = "site_dir: site\n"
    if anchor not in mkdocs_text:
        raise RuntimeError("mkdocs.yml: expected 'site_dir: site' anchor")
    return mkdocs_text.replace(anchor, anchor + "\n" + nav_block)


def main() -> None:
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    nav = data.get("nav", [])
    nav_block = build_nav_block(nav)
    mkdocs_text = MKDOCS_PATH.read_text(encoding="utf-8")
    MKDOCS_PATH.write_text(inject_nav(mkdocs_text, nav_block), encoding="utf-8")
    print(f"Updated {MKDOCS_PATH} ({len(nav)} sections)")


if __name__ == "__main__":
    main()
