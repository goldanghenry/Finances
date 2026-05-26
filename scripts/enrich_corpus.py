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
        "repair_corpus_mechanical.py",
        "repair_broken_section6_tables.py",
        "repair_mangled_tables.py",
        "repair_section6_intrusion.py",
        "ensure_section6_variable_tables.py",
        "repair_split_tables.py",
        "add_info_boxes.py",
        "repair_tables_split_by_info.py",
        "repair_section4a.py",
        "enrich_section6_from_glossary.py",
        "fix_table_separator_columns.py",
        "fix_unbalanced_display_math.py",
    ]
    for step in steps:
        run(step)
    print("\n=== lint_reader_friendly.py ===")
    subprocess.run([sys.executable, str(SCRIPTS / "lint_reader_friendly.py")], cwd=ROOT, check=True)
    print("\nEnrich corpus complete.")


if __name__ == "__main__":
    main()
