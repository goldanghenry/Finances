"""Shared helpers for gold-standard corpus polish and lint."""

from __future__ import annotations

import re
from pathlib import Path

from repair_corpus_mechanical import (
    PLACEHOLDER as PLACEHOLDER_LEGACY,
    lookup_meaning,
    lookup_name,
    parse_section4_terms,
)

PLACEHOLDER_MEANINGS = (
    "§4·본문 정의 참고",
    "본문 §4·위 식 맥락 참고",
    "§4·본문 정의",
    "위 식 맥락 참고",
)
TEMPLATE_READING = "위 식의 기호는 바로 위 변수표와 같다"
TEMPLATE_READING_FULL = (
    "**읽는 법**: 위 식의 기호는 바로 위 변수표와 같다. "
    f"숫자는 [DEPTH-STANDARD](../docs/DEPTH-STANDARD.md) 교육용 기호(M·P·PV 등)로 대입한다."
)
DEPTH_LINK = "[DEPTH-STANDARD](../docs/DEPTH-STANDARD.md)"


def is_l4(text: str) -> bool:
    m = re.search(r"\| 난이도 \|[^\n]*L(\d)", text)
    return bool(m and m.group(1) == "4")


def section_slice(text: str, num: str) -> str:
    m = re.search(rf"^## {re.escape(num)}[\.\s]", text, re.M)
    if not m:
        return ""
    tail = text[m.start() :]
    if num == "10":
        m_end = re.search(
            r"^## (?:11|12|퀴즈|L3 보충|L4|부록)",
            tail[10:],
            re.M,
        )
    else:
        m_end = re.search(
            rf"^## (?!{re.escape(num)}[\.\s])",
            tail[10:],
            re.M,
        )
    return tail[: m_end.start() + 10] if m_end else tail


def section6_body(text: str) -> str:
    return section_slice(text, "6")


def section8_body(text: str) -> str:
    return section_slice(text, "8")


def section10_body(text: str) -> str:
    return section_slice(text, "10")


def bare_symbol(sym_cell: str) -> str:
    s = sym_cell.strip()
    s = re.sub(r"^\*\*|\*\*$", "", s)
    m = re.search(r"\\?\(?\\?([A-Za-z0-9_βπ]+)\\?\)?", s)
    if m:
        return m.group(1).replace("{", "").replace("}", "")
    return re.sub(r"\\[(){}]", "", s).strip()[:12]


def parse_var_table_before(text: str, pos: int) -> list[tuple[str, str, str]]:
    """Rows of (symbol, name, meaning) from last 3-col table before pos."""
    chunk = text[max(0, pos - 2500) : pos]
    if "이 식에서 의미" not in chunk:
        return []
    lines = chunk.splitlines()
    rows: list[tuple[str, str, str]] = []
    in_table = False
    for line in reversed(lines):
        if not line.strip().startswith("|"):
            if in_table:
                break
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[0] in ("기호", "------") or all(re.fullmatch(r"-+", c.replace(" ", "")) for c in cells):
            in_table = True
            continue
        if "이 식에서 의미" in line:
            in_table = True
            continue
        if in_table or "의미" in chunk:
            rows.append((cells[0], cells[1], cells[2]))
            in_table = True
    rows.reverse()
    return rows[-8:] if rows else []


def is_placeholder_meaning(s: str) -> bool:
    t = s.strip()
    if not t or t == "\\":
        return True
    if "[TODO:meaning]" in t:
        return True
    return any(p in t for p in PLACEHOLDER_MEANINGS)


def fix_variable_row(sym: str, name: str, mean: str, terms4: dict[str, str]) -> tuple[str, str, str]:
    bs = bare_symbol(sym)
    if is_placeholder_meaning(mean) or name.strip() in ("", bs, sym.strip()):
        mean = lookup_meaning(sym, terms4)
        if is_placeholder_meaning(mean):
            mean = f"{lookup_name(sym)}이(가) 이 식에서 맡는 역할(§4·본문 참고)"
        if name.strip() in ("", bs, sym.strip(), "\\"):
            name = lookup_name(sym)
    if len(mean) > 80:
        mean = mean[:77] + "…"
    return sym, name, mean


def generate_reading_note(equation: str, rows: list[tuple[str, str, str]]) -> str:
    eq = equation.replace("\n", " ").replace(" ", "")
    ids = [bare_symbol(s) for s, _, _ in rows]
    names = [n for _, n, _ in rows if n and n not in ids]

    def bold(x: str) -> str:
        b = bare_symbol(x) or x
        return f"**{b}**"

    if "FV" in eq and "PV" in eq and "(1+r)" in eq:
        return (
            "**읽는 법**: **PV**에 **r**를 **n**기간 복리하면 **FV**가 된다. "
            f"목표 **FV**가 정해지면 역산해 필요 **PV**·**PMT**를 구한다. 숫자는 {DEPTH_LINK} 기호로 대입한다."
        )
    if "FV" in eq and "PMT" in eq:
        return (
            "**읽는 법**: 매 기간 **PMT**가 **r**로 **n**번 복리·누적되면 **FV**가 된다. "
            f"월·연 단위는 **r**·**n** 정의와 맞춘다. {DEPTH_LINK} 참고."
        )
    if "NPV" in eq or "npv" in eq.lower():
        return (
            "**읽는 법**: **CF_t**를 **r**로 할인해 합한 뒤 **C_0**를 빼면 **NPV**다. "
            f"**NPV**>0이면 요구수익 **r** 하에서 투자 타당(가정 하). {DEPTH_LINK} 기호 예제 참고."
        )
    if "IRR" in eq:
        return (
            "**읽는 법**: **NPV**=0이 되도록 만드는 할인율이 **IRR**이다. "
            "다중 IRR·재투자 가정은 본문 함정 절을 확인한다."
        )
    if "WACC" in eq:
        return (
            "**읽는 법**: 부채·자본 비중으로 **r_d**·**r_e**를 가중 평균한 것이 **WACC**다. "
            "프로젝트·기업가치 할인율 근사로 쓴다."
        )
    if "beta" in eq.lower() or "β" in equation:
        return (
            "**읽는 법**: 시장 초과수익에 대한 민감도가 **β**다. "
            f"**R_f**·**ERP**와 함께 요구수익 **r**을 구성한다. {DEPTH_LINK} 참고."
        )
    if "실질" in equation or "명목" in equation or "pi" in eq or "π" in equation:
        return (
            "**읽는 법**: **명목** 수익에서 **인플레**를 반영하면 **실질** 체감 수익을 본다. "
            "정밀식은 본문 또는 §4 표를 따른다."
        )

    mentioned = [bold(s) for s, _, _ in rows[:4] if bare_symbol(s)]
    if len(mentioned) >= 2:
        return (
            f"**읽는 법**: {mentioned[0]}와 {mentioned[1]}의 관계를 위 식으로 쓴다. "
            f"경제·재무 해석은 변수표 「이 식에서 의미」와 {DEPTH_LINK} 기호 예제를 맞춘다."
        )
    if mentioned:
        return (
            f"**읽는 법**: {mentioned[0]}를 중심으로 위 식을 읽는다. "
            f"나머지 기호는 바로 위 표와 {DEPTH_LINK}를 따른다."
        )
    return (
        f"**읽는 법**: 위 식의 각 기호는 직전 변수표와 §4 정의에 대응한다. "
        f"구체 숫자는 {DEPTH_LINK} 교육용 기호(M·P·PV 등)로 대입한다."
    )


def l4_derivation_block(rows: list[tuple[str, str, str]]) -> str:
    syms = ", ".join(bold_symbol(s) for s, _, _ in rows[:3]) or "기호"
    return (
        "\n**유도 (L4)**:\n"
        f"1. **정의**: {syms}를 동일 시점·동일 통화로 맞춘다. — 단위 불일치면 식이 무의미해진다.\n"
        "2. **식 변형**: 양변을 정리해 목표 변수를 한쪽에 둔다. — 할인·복리는 **시점 이동**이 핵심이다.\n"
        "3. **해석**: 부호·크기가 경제 직관과 맞는지 확인한다. — 극단값에서 단조성·한계를 점검한다.\n"
    )


def bold_symbol(sym_cell: str) -> str:
    b = bare_symbol(sym_cell)
    return f"**{b}**" if b else sym_cell.strip()


def ensure_faq_practical(text: str) -> tuple[str, bool]:
    m = re.search(r"^## 10[\.\s]", text, re.M)
    if not m:
        return text, False
    tail = text[m.start() :]
    m_end = re.search(r"^## (?:11|L3 보충)", tail, re.M)
    s10 = tail[: m_end.start()] if m_end else tail
    if re.search(r"실무에서는|실무에선|실무에서는\?|실무 적용", s10):
        return text, False
    insert = (
        "\n**Q. 실무에서는?**  \n"
        "교과서 식·기호를 그대로 적용하기 전에 **수수료·세금·데이터 시점**을 분리한다. "
        f"숫자는 {DEPTH_LINK}처럼 기호만 먼저 맞추고, 법령·시장 수치는 §8 표·외부 출처로 갱신한다.\n\n"
    )
    if m_end:
        pos = m.start() + m_end.start()
        return text[:pos] + insert + text[pos:], True
    return text.rstrip() + insert + "\n", True


def ensure_l4_practice(text: str) -> tuple[str, bool]:
    if not is_l4(text):
        return text, False
    if re.search(r"##\s*연습문제|연습문제\s*\(|###\s*연습", text):
        return text, False
    block = (
        "\n## 연습문제 (L4, 기호)\n\n"
        "1. 위 §6 주요 식에서 변수 하나를 미지로 두고, 나머지를 기호로 둔 **관계식**을 쓰시오.\n"
        "2. 가정이 깨질 때(유동성·세금·다중 IRR 등) 위 식의 **한계**를 기호·부등식으로 서술하시오.\n"
        "3. §8 예제와 동일 기호(M·P·PV 등)로 **부호·단조성**만 검증하는 짧은 논증을 하시오.\n\n"
        "### 해설 키\n\n"
        "1. 직전 변수표의 「이 식에서 의미」를 이용해 동일 차원으로 정리한다.\n"
        "2. 「가정이 깨지면」 절의 한계 사례와 연결한다.\n"
        "3. 숫자 대입 없이 **부호**·**단위** 일치만 확인한다.\n"
    )
    for pat in (r"^## 12[\.\s]", r"^## 퀴즈", r"^## 부록"):
        m = re.search(pat, text, re.M)
        if m:
            prefix = text[: m.start()]
            if not prefix.endswith("\n\n"):
                prefix = prefix.rstrip() + "\n\n"
            return prefix + block + text[m.start() :], True
    return text.rstrip() + "\n\n" + block + "\n", True


def ensure_l4_limit(text: str) -> tuple[str, bool]:
    if not is_l4(text):
        return text, False
    if re.search(r"가정이 깨지면|한계 사례|한계:", text):
        return text, False
    block = (
        "\n### 가정이 깨지면 (L4)\n\n"
        "- **한계**: 유동성·정보·세금·거래비용이 무시된 가정에서 유도된 식은 "
        "스트레스 구간에서 기호 관계가 역전되거나 추정이 불안정해질 수 있다.\n"
    )
    m11 = re.search(r"^## 11[\.\s]", text, re.M)
    if m11:
        tail = text[m11.start() :]
        m12 = re.search(r"^## 12[\.\s]", tail[10:], re.M)
        pos = m11.start() + 10 + m12.start() if m12 else len(text)
        return text[:pos] + block + text[pos:], True
    return text, False


def strip_template_reading_global(text: str) -> tuple[str, bool]:
    if TEMPLATE_READING not in text:
        return text, False
    new = text.replace(TEMPLATE_READING_FULL, "")
    new = re.sub(
        r"\*\*읽는 법\*\*:\s*위 식의 기호는 바로 위 변수표와 같다\.[^\n]*",
        "",
        new,
    )
    return new, new != text


def polish_section8_amounts(text: str) -> tuple[str, bool]:
    s8 = section8_body(text)
    if not s8:
        return text, False
    m8 = re.search(r"^## 8[\.\s]", text, re.M)
    assert m8
    start = m8.start()
    tail = text[start:]
    m_end = re.search(r"^## [^8]", tail[10:], re.M)
    end = start + (m_end.start() + 10 if m_end else len(tail))
    section = text[start:end]
    changed = False
    inst = re.compile(
        r"한도|제도|L_ISA|법령|상한|ISA|IRP|연금|세액공제|DC \+|예금자보호|1천~|보도상|비과세\s*\d"
    )
    new_lines: list[str] = []
    for line in section.splitlines():
        if inst.search(line):
            new_lines.append(line)
            continue
        nl = line
        old = nl
        nl = re.sub(r"\d+~\d+만\s*원", "**M** (만 원, 교육용)", nl)
        nl = re.sub(r"\d+,?\d*만\s*원", "**M** (만 원, 교육용)", nl)
        nl = re.sub(r"[−-]?\d{1,3}(?:,\d{3})*만(?![\w*])", "**M**", nl)
        nl = re.sub(r"[−-]?\d+,?\d*만(?![\w*])", "**M**", nl)
        nl = re.sub(r"\d+\.\d+억", "**F**", nl)
        nl = re.sub(r"\*\*1,\*\*M\*\*", "**M**", nl)
        nl = re.sub(r"\d+\.?\d*억\s*원?", "**F**", nl)
        nl = re.sub(r"(?<![\w])(\d+)억", r"**F**", nl)
        nl = re.sub(r"수천만\s*원", "**M** 규모", nl)
        nl = re.sub(r"연봉\s*\d+[^\s]*", "연봉 **Y**", nl)
        nl = re.sub(r"\*{3,}M\*{2,}", "**M**", nl)
        nl = re.sub(r"2,\*\*M\*\*", "**M**", nl)
        if nl != old:
            changed = True
        new_lines.append(nl)
    new_section = "\n".join(new_lines)
    if changed:
        text = text[:start] + new_section + text[end:]
    return text, changed


def polish_section6(text: str) -> tuple[str, bool]:
    s6 = section6_body(text)
    if not s6 or "해당 없음" in s6[:300]:
        return text, False
    terms4 = parse_section4_terms(text)
    changed = False
    m6 = re.search(r"^## 6[\.\s]", text, re.M)
    assert m6
    start = m6.start()
    tail = text[start:]
    m_end = re.search(r"^## [^6]", tail[10:], re.M)
    end = start + (m_end.start() + 10 if m_end else len(tail))
    section = text[start:end]

    # Fix placeholder variable rows
    def repl_row(m: re.Match[str]) -> str:
        nonlocal changed
        sym, name, mean = m.group(1), m.group(2), m.group(3)
        if "이 식에서 의미" in sym:
            return m.group(0)
        if not is_placeholder_meaning(mean) and name.strip() not in ("", bare_symbol(sym)):
            return m.group(0)
        ns, nn, nm = fix_variable_row(sym, name, mean, terms4)
        if (ns, nn, nm) != (sym, name, mean):
            changed = True
        return f"| {ns} | {nn} | {nm} |"

    section = re.sub(
        r"^\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|\s*$",
        repl_row,
        section,
        flags=re.M,
    )

    # Replace template / missing reading notes after display math
    l4 = is_l4(text)
    pos = 0
    while True:
        m = re.search(r"\\\[", section[pos:])
        if not m:
            break
        eq_start = pos + m.start()
        m_close = re.search(r"\\\]", section[eq_start:])
        if not m_close:
            break
        eq_end = eq_start + m_close.end()
        if not section[eq_end : eq_end + 1] == "\n":
            eq_end += 0
        else:
            eq_end += 1
        equation = section[eq_start:eq_end]
        after = section[eq_end : eq_end + 200]
        rows = parse_var_table_before(section, eq_start)
        note = generate_reading_note(equation, rows)

        after_full = section[eq_end:]
        needs_note = TEMPLATE_READING in after_full[:200] or "읽는 법" not in after_full[:120]
        if needs_note:
            after_full = after_full.replace(TEMPLATE_READING_FULL, "")
            after_full = re.sub(
                r"\*\*읽는 법\*\*:\s*위 식의 기호는 바로 위 변수표와 같다\.[^\n]*",
                "",
                after_full,
            )
            if TEMPLATE_READING in after_full[:200] or (
                "읽는 법" not in after_full[:120]
            ):
                deriv = (
                    l4_derivation_block(rows)
                    if l4 and "**유도 (L4)**" not in after_full[:400]
                    else ""
                )
                section = section[:eq_end] + "\n" + note + deriv + after_full
                changed = True
                pos = eq_end + len(note) + len(deriv)
            else:
                section = section[:eq_end] + after_full
                changed = True
                pos = eq_end + len(after_full)
        else:
            pos = eq_end

    if changed:
        text = text[:start] + section + text[end:]
    return text, changed


def polish_file(text: str) -> tuple[str, bool]:
    from repair_corpus_mechanical import fix_section6_placeholders

    changed = False
    t0, c0 = strip_template_reading_global(text)
    if c0:
        text, changed = t0, True
    t2, c2 = fix_section6_placeholders(text)
    if c2:
        text, changed = t2, True
    t3, c3 = polish_section6(text)
    if c3:
        text, changed = t3, True
    t4, c4 = ensure_faq_practical(text)
    if c4:
        text, changed = t4, True
    t5, c5 = ensure_l4_practice(text)
    if c5:
        text, changed = t5, True
    t6, c6 = ensure_l4_limit(text)
    if c6:
        text, changed = t6, True
    t7, c7 = polish_section8_amounts(text)
    if c7:
        text, changed = t7, True
    t0b, c0b = strip_template_reading_global(text)
    if c0b:
        text, changed = t0b, True
    return text, changed
