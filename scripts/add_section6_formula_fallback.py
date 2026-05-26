#!/usr/bin/env python3
"""Insert **식 (기호)** plain-text fallback after §6 display math blocks."""

from __future__ import annotations

import re
import sys

from _corpus import iter_corpus_md

DISPLAY_BLOCK = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)
SECTION6_START = re.compile(r"^## 6[\.\s]", re.M)
SECTION6_END = re.compile(r"^## [^6]", re.M)
FALLBACK_LINE = re.compile(r"\n\*\*식 \(기호\)\*\*:[^\n]*\n?")

GREEK_CMDS = (
    ("alpha", "α"),
    ("beta", "β"),
    ("gamma", "γ"),
    ("delta", "δ"),
    ("pi", "π"),
    ("sigma", "σ"),
    ("varepsilon", "ε"),
    ("Delta", "Δ"),
    ("Pi", "Π"),
)

SKIP_MACROS = re.compile(
    r"\\(?:begin|end|underbrace|overbrace|hat|bar|vec|sqrt|left|right)\b"
)


def section6_span(text: str) -> tuple[int, int] | None:
    m = SECTION6_START.search(text)
    if not m:
        return None
    start = m.start()
    tail = text[start + 10 :]
    m_end = SECTION6_END.search(tail)
    end = start + 10 + m_end.start() if m_end else len(text)
    if "해당 없음" in text[start : start + 300]:
        return None
    return start, end


def parse_brace_group(s: str, open_idx: int) -> tuple[str, int] | None:
    if open_idx >= len(s) or s[open_idx] != "{":
        return None
    depth = 0
    for i in range(open_idx, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[open_idx + 1 : i], i + 1
    return None


def replace_fracs(s: str) -> tuple[str, int]:
    changes = 0
    while True:
        m = re.search(r"\\frac\{", s)
        if not m:
            break
        brace_start = m.end() - 1
        parsed = parse_brace_group(s, brace_start)
        if not parsed:
            break
        num, after_num = parsed
        parsed_den = parse_brace_group(s, after_num)
        if not parsed_den:
            break
        den, after_den = parsed_den
        repl = f"({num.strip()}) / ({den.strip()})"
        s = s[: m.start()] + repl + s[after_den:]
        changes += 1
    return s, changes


def latex_to_fallback(body: str) -> str | None:
    s = " ".join(body.split())
    if not s or SKIP_MACROS.search(s):
        return None

    s = re.sub(r"\\text\{([^}]+)\}", r"\1", s)
    s = re.sub(r"\\mathrm\{([^}]+)\}", r"\1", s)
    s = re.sub(r"\\textbf\{([^}]+)\}", r"\1", s)
    s = re.sub(r"\\underbrace\{[^{}]+\}_\{[^{}]*\}", "", s)
    s = re.sub(r"\\(?:left|right)\b", "", s)
    s = re.sub(r"\\[,\;!\s]", " ", s)
    s = re.sub(r"\\quad\s*", " ", s)

    for cmd, ch in GREEK_CMDS:
        s = re.sub(
            rf"\\{cmd}(?:_\{{([^}}]+)\}}|_([A-Za-z0-9]))?",
            lambda m, c=ch: c + ("_" + (m.group(1) or m.group(2) or "")),
            s,
        )
        s = s.replace(f"\\{cmd}", ch)

    latex_ops = (
        (r"\times", "×"),
        (r"\cdot", "·"),
        (r"\approx", "≈"),
        (r"\leq", "≤"),
        (r"\geq", "≥"),
        (r"\neq", "≠"),
    )
    for pat, repl in latex_ops:
        s = s.replace(pat, repl)
    s = s.replace(r"\&", "&")
    s = re.sub(r"\\sum_\{?t\}?", "Σ_t", s)
    s = s.replace(r"\sum", "Σ")

    s, _ = replace_fracs(s)

    s = re.sub(r"\^\{([^}]+)\}", r"^\1", s)
    s = re.sub(r"_\{([^}]+)\}", r"_\1", s)
    s = re.sub(r"\\[a-zA-Z]{2,}", "", s)
    s = re.sub(r"\s+", " ", s).strip()

    if not s or "\\" in s:
        return None

    return bold_symbols(s)


def bold_symbols(s: str) -> str:
    s = re.sub(
        r"\(([^()]+)\)\^([A-Za-z0-9_]+)",
        lambda m: f"({bold_symbols(m.group(1))})^**{m.group(2)}**",
        s,
    )
    s = re.sub(
        r"(?<!\*)(α|β|γ|δ|π|σ|ε|Δ|Π)(_[A-Za-z0-9]+)?(?!\*)",
        lambda m: f"**{m.group(0)}**",
        s,
    )
    tokens = re.split(r"(\s+|×|·|≈|≤|≥|≠|=|\+|−|\-|/|\(|\)|,|\[|\])", s)
    out: list[str] = []
    for tok in tokens:
        if not tok:
            continue
        if re.fullmatch(r"[×·≈≤≥≠=+\-/(),\s]+", tok) or re.fullmatch(r"[\d.]+%?", tok):
            out.append(tok)
            continue
        if (
            re.fullmatch(r"[A-Za-z][A-Za-z0-9_&]*", tok)
            and tok not in {"min", "max", "mod", "times", "cdot", "approx"}
        ):
            out.append(f"**{tok}**")
        else:
            out.append(tok)
    result = "".join(out)
    result = re.sub(r"\*\*\*\*", "", result)
    result = re.sub(r"\s+", " ", result).strip()
    result = result.replace("· ", "·").replace("× ", "×")
    return result


def skip_existing_fallback(s6: str, pos: int) -> int:
    while True:
        m = FALLBACK_LINE.match(s6, pos)
        if not m:
            break
        pos = m.end()
    return pos


def dedupe_fallback_lines(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        out.append(lines[i])
        if lines[i].startswith("**식 (기호)**"):
            i += 1
            while i < len(lines) and lines[i].startswith("**식 (기호)**"):
                i += 1
            continue
        i += 1
    return "\n".join(out)


def process_section6(s6: str) -> tuple[str, int]:
    changes = 0
    out: list[str] = []
    pos = 0
    for m in DISPLAY_BLOCK.finditer(s6):
        out.append(s6[pos : m.end()])
        pos = skip_existing_fallback(s6, m.end())
        fallback = latex_to_fallback(m.group(1))
        if fallback and len(fallback) >= 3:
            out.append(f"\n\n**식 (기호)**: {fallback}\n")
            changes += 1
    out.append(s6[pos:])
    return dedupe_fallback_lines("".join(out)), changes


def fix_text(text: str) -> tuple[str, int]:
    span = section6_span(text)
    if not span:
        return text, 0
    start, end = span
    s6, n = process_section6(text[start:end])
    if not n:
        return text, 0
    return text[:start] + s6 + text[end:], n


def main() -> int:
    total = 0
    files = 0
    for path in iter_corpus_md():
        text = path.read_text(encoding="utf-8")
        new_text, n = fix_text(text)
        if n:
            path.write_text(new_text, encoding="utf-8")
            print(f"{path.name}: {n}")
            total += n
            files += 1
    print(f"\nAdded formula fallback in {files} files ({total} blocks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
