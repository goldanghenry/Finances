# L3 코퍼스 현황

> **기준**: [DEPTH-STANDARD.md](DEPTH-STANDARD.md) · **골드**: [GOLD-CHAPTER-STANDARD.md](GOLD-CHAPTER-STANDARD.md)

| Phase | 폴더 | L3+ 본문 | L4 본문 | 골드 G1–G6 | L4 G7–G9 |
|-------|------|----------|---------|------------|----------|
| 0 | 01-foundations/ | 7편 | 4편+ | [x] | [x] |
| 1 | financial-statements + roadmap | 2편 | 5편 | [x] | [x] |
| 2 | 02-economics/ | 2편 | 11편 | [x] | [x] |
| 3 | 03-markets/ | 12편+ | 15편+ | [x] | [x] |
| 3b | sectors/ | 7편 | — | [x] | n/a |
| 4 | 04-portfolio/ | 7편 | 4편 | [x] | [x] |
| 5 | 06-korea-policy/ | 13편+ | 3편+ | [x] | [x] |
| 6 | 05-behavioral/ | 1편 | 2편 | [x] | [x] |
| 7 | 07-real-estate/ | 1편 | 1편 | [x] | [x] |
| 8 | 08-advanced/ | 2편 | 7편+ | [x] | [x] |
| 9 | 09-corporate-finance/ | — | 3편 | n/a | [x] |
| R0 | 00-roadmap/ | 1편 (playbook) | — | [x] | n/a |

**1주차 8편** ([master-roadmap §1주차](../00-roadmap/master-roadmap.md)): cash-flow-basics, household-ledger-practical, db-pension, overseas-stocks-tax-part1-cgt, us-equity-indices-etf, leveraged-etf-qqq-qld, isa, isa-irp-practical-setup, passive-vs-active — **골드 린트 0** (2026-05-26).

---

## 검증 (2026-05-26, 골드 100%)

| 검사 | 결과 |
|------|------|
| `python scripts/lint_gold_chapter.py` | **0 files** |
| `python scripts/lint_corpus_quality.py` | **0 files** |
| `mkdocs build` | **성공** |
| 모범 편 | [compound-interest-and-time-value](../01-foundations/compound-interest-and-time-value.md) |

**파이프라인**: `enrich_section6_from_glossary.py` → `polish_chapter_to_gold.py` → `fix_faq_placement.py` → `lint_gold_chapter.py` (CI [pages.yml](../.github/workflows/pages.yml)).

**비활성화**: `add_section6_reading_notes.py` (템플릿 재오염 방지, `--force`만 예외).

---

## 이전 갱신 요약

- **2026-05-26 (교재 손질)**: `lint_corpus_quality.py`, 기계 수리, Phase별 1차 보강
- **2026-05-26 (독자 친화)**: §0, §4a, §6 변수표, MathJax, Phase nav
- **2026-05-25**: L4 확장, glossary 133항

**용어**: [glossary.md](../00-roadmap/glossary.md) · [TERMINOLOGY-STANDARD.md](TERMINOLOGY-STANDARD.md)

**전체 지도**: [CURRICULUM-MAP.md](../00-roadmap/CURRICULUM-MAP.md)

**갱신일**: 2026-05-26
