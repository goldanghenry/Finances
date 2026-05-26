#!/usr/bin/env python3
"""Run all corpus enrichment steps in order."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(name: str) -> None:
    path = SCRIPTS / name
    print(f"\n=== {name} ===")
    subprocess.run([sys.executable, str(path)], cwd=ROOT, check=True)


def main() -> None:
    steps = [
        "enrich_section0_prereq.py",
        "enrich_section6_tables.py",
        "add_info_boxes.py",
        "repair_section4a.py",
    ]
    for step in steps:
        run(step)
    print("\n=== lint_reader_friendly.py ===")
    subprocess.run([sys.executable, str(SCRIPTS / "lint_reader_friendly.py")], cwd=ROOT, check=True)
    print("\nEnrich corpus complete.")


if __name__ == "__main__":
    main()
