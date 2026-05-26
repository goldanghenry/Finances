#!/usr/bin/env python3
"""Remove orphan display-math closers and glued \\\\[ openers."""

from __future__ import annotations

import re
import sys

from _corpus import iter_corpus_md


def close_unterminated_display_blocks(text: str) -> tuple[str, int]:
    """Insert \\] before **읽는 법** / ### when a display block was left open."""
    lines = text.splitlines()
    out: list[str] = []
    open_block = False
    changes = 0
    for ln in lines:
        st = ln.strip()
        if st == "\\[":
            open_block = True
            out.append(ln)
            continue
        if st == "\\]":
            open_block = False
            out.append(ln)
            continue
        if open_block and (
            st.startswith("**읽는 법**")
            or st.startswith("### ")
        ):
            out.append("\\]")
            open_block = False
            changes += 1
        out.append(ln)
    if open_block:
        out.append("\\]")
        changes += 1
    return "\n".join(out), changes


def fix_text(text: str) -> tuple[str, int]:
    changes = 0
    new_text = re.sub(r"([^\n\\])\\\[\s*\n", r"\1\n\n\\[\n", text)
    new_text = re.sub(r"([^\n\\])\\\[\s*$", r"\1\n\n\\[", new_text, flags=re.M)
    if new_text != text:
        changes += 1
    text = new_text

    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        st = ln.strip()

        # orphan latex fragment until lone \]
        if st.startswith("\\quad") or (
            st.startswith("\\frac") and i > 0 and out and out[-1].strip().startswith("**")
        ):
            while i < len(lines) and lines[i].strip() != "\\]":
                i += 1
                changes += 1
            if i < len(lines) and lines[i].strip() == "\\]":
                i += 1
                changes += 1
            continue

        # duplicate \] or \] after 읽는 법 without opening
        if st == "\\]":
            prev_nonempty = next((out[j] for j in range(len(out) - 1, -1, -1) if out[j].strip()), "")
            if prev_nonempty.strip() == "\\]" or prev_nonempty.strip().startswith("**읽는 법**"):
                i += 1
                changes += 1
                continue

        out.append(ln)
        i += 1

    text = "\n".join(out)
    text = re.sub(
        r"(\*\*읽는 법\*\*:[^\n]+\n)(\*\*유도 \(L4\)\*\*:[\s\S]*?)(\n\*\*읽는 법\*\*:[^\n]+\n\*\*유도 \(L4\)\*\*)",
        r"\1\2",
        text,
        count=0,
    )
    text, n_close = close_unterminated_display_blocks(text)
    changes += n_close
    text = re.sub(r"\\\[\s*\n\s*\\\]", "", text)
    # Drop orphan closers when enrich left more \\] than \\[.
    while text.count("\\[") < text.count("\\]"):
        text2 = re.sub(r"(?m)^\s*\\\]\s*$\n?", "", text, count=1)
        if text2 == text:
            break
        text = text2
        changes += 1
    return text, changes


def main() -> int:
    total = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, n = fix_text(text)
        if n:
            path.write_text(new_text, encoding="utf-8")
            o = sum(1 for ln in new_text.splitlines() if ln.strip() == "\\[")
            c = sum(1 for ln in new_text.splitlines() if ln.strip() == "\\]")
            flag = "" if o == c else f" (still {o}/{c})"
            print(f"{path.name}: {n}{flag}")
            total += n
    print(f"\n{total} fixes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
