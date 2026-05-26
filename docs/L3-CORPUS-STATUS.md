# L3 코퍼스 현황

> **기준**: [DEPTH-STANDARD.md](DEPTH-STANDARD.md) — L3 본문 **≥10,000자**, L4 **≥18,000자**, 12블록, 예제 3+, mermaid 2+, FAQ 5+ (L4: 8+)

| Phase | 폴더 | L3+ 본문 | L4 본문 | 인덱스·Primer |
|-------|------|----------|---------|----------------|
| 0 | 01-foundations/ | 7편 ✅ | 4편+ ✅ | README |
| 1 | financial-statements + roadmap | 2편 ✅ | 5편 ✅ | — |
| 2 | 02-economics/ | 2편 ✅ | 11편 ✅ | README |
| 3 | 03-markets/ | 12편+ ✅ | 15편+ ✅ | primer L1 |
| 3b | sectors/ | 7편 ✅ | — | README |
| 4 | 04-portfolio/ | 7편 ✅ | 4편 ✅ | README |
| 5 | 06-korea-policy/ | 13편+ ✅ | 3편+ ✅ | README |
| 6 | 05-behavioral/ | 1편 ✅ | 2편 ✅ | README |
| 7 | 07-real-estate/ | 1편 ✅ | 1편 ✅ | README |
| 8 | 08-advanced/ | 2편 ✅ | 7편+ ✅ | README |
| 9 | 09-corporate-finance/ | — | 3편 ✅ | README |
| R0 | 00-roadmap/ | 1편 (playbook) | — | STUDY-START |

**이번 갱신 (2026-05-26, 교재 손질)**:

- **품질 게이트**: `scripts/lint_corpus_quality.py` (표·admonition·§6 변수표·수식) — CI [pages.yml](../.github/workflows/pages.yml) 연동
- **수리 파이프라인**: `repair_corpus_mechanical.py`, `ensure_section6_variable_tables.py`, `repair_split_tables.py`, `add_section6_reading_notes.py`, `apply_phase_polish.py`
- **편집 완료(기계+1차 서술)**: Phase 0~9 — §6 변수표·읽는 법, Phase 1 **한빛전자** 스레드, Phase 2 모형 해석, Phase 3 입문↔심화, Phase 5 세금 part 연속, [playbook](../00-roadmap/ai-engineer-investing-playbook.md) 월별 §번호
- **골드 참고**: [compound-interest-and-time-value](../01-foundations/compound-interest-and-time-value.md), [time-value-npv-irr](../01-foundations/time-value-npv-irr.md) §6, [cash-flow-basics](../01-foundations/cash-flow-basics.md) §8(기호 M·R·C)

**이전 (2026-05-26)**: 독자 친화 일괄 보강 — **§0**, **§4a**, **§6 변수표**, **`!!! info`**, MathJax, Phase nav, [READER-GUIDE](READER-GUIDE.md). 유지보수: `scripts/enrich_corpus.py` → `lint_reader_friendly.py` + `lint_corpus_quality.py`.

**이전 (2026-05-25)**: B 7편 L4, C 4편 L4, 신규 L3 7편, glossary 133항, [TERMINOLOGY-STANDARD](TERMINOLOGY-STANDARD.md), 15편 §4a/4b retrofit.

**용어**: [glossary.md](../00-roadmap/glossary.md) · §4a/4b — [TERMINOLOGY-STANDARD.md](TERMINOLOGY-STANDARD.md)

**인덱스·Primer** (`*-primer.md`, `README.md`)는 L1~L2 — 본문으로 연결.

**검증**: `python scripts/lint_reader_friendly.py` · `mkdocs build` · `wc -c` — L3 본문 10KB+, L4 18KB+

**갱신일**: 2026-05-26

**전체 지도**: [CURRICULUM-MAP.md](../00-roadmap/CURRICULUM-MAP.md) — **~89과목 ✅**, 확장 X 8과목 ❌
