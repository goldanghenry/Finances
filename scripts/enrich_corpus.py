#!/usr/bin/env python3
"""Run corpus enrichment pipeline in fixed order."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(name: str, *extra: str) -> None:
    cmd = [sys.executable, str(SCRIPTS / name), *extra]
    print(f"\n>>> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    run("enrich_section0_prereq.py")
    run("enrich_section6_tables.py")
    run("add_info_boxes.py")
    run("repair_section4a.py")
    run("lint_reader_friendly.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
