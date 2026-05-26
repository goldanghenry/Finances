# 독자 가이드 — 이 코퍼스 읽는 법

> **면책**: 교육 목적이며 투자·세무·법률 자문이 아닙니다.

처음 오셨다면 **이 페이지 → [STUDY-START](../00-roadmap/STUDY-START.md) → Phase 0** 순으로 가세요. 사이트 **왼쪽 메뉴**도 아래 Phase 순서와 같습니다.

### GitHub 원문(.md) vs 사이트(GitHub Pages)

| 보는 곳 | 수식·메뉴 | 권장 |
|---------|-----------|------|
| **GitHub** 저장소에서 `.md` 파일 직접 열기 | LaTeX가 `\[ PV = ... \]` **원문**으로 보임. Phase 메뉴 없음 | 빠른 diff·편집용 |
| **[GitHub Pages](https://goldanghenry.github.io/Finances/)** (MkDocs Material) | **MathJax**로 수식 렌더, Phase 순 **사이드바**, `!!! info` 박스 | **일반 독자 읽기** |

로컬에서 사이트와 동일하게 보려면 [github-pages-deploy.md](github-pages-deploy.md)의 `mkdocs serve` 절차를 따르세요.

---

## 1. L1 ~ L4 난이도란?

각 본문 맨 위 **메타** 표의 `난이도`와 사이드바 제목 옆 표기를 뜻합니다. **폴더 번호(01, 02…)와 Phase 번호는 다릅니다.**

| 등급 | 한 줄 | 누가 | 편당 읽기(가이드) | 건너뛰기 |
|------|------|------|-------------------|----------|
| **L1** | 입문·지도·짧은 요약 | 막 시작, 방향만 잡을 때 | 20~40분 | `README`·`*-primer` — 본문 대신 훑기 |
| **L2** | 표준 학습문 | (본 코퍼스에는 거의 없음) | 약 1~1.5시간 | — |
| **L3** | **교재 본문** — 예제·FAQ·한국 적용 | **일반 독자 주력** | 약 1.5~2시간 | 비전공도 가능. **§0·용어 박스** 활용 |
| **L4** | 전공자 심화 — 유도·비교정태·연습문제 | 경제·금융 기초 있는 독자 | 약 2.5~4시간+ | L3·선수 문서 없으면 **나중에** |

**이 저장소 현황**: 대부분 **L3**, 일부 **L4**(경제학 11편, 재무제표 심화, NPV·IRR 등). 저자용 상세 규칙은 [DEPTH-STANDARD](DEPTH-STANDARD.md) — 독자는 **이 가이드만** 보면 됩니다.

### L3 vs L4 읽기 팁

| | L3 | L4 |
|--|----|----|
| 목표 | 개념·실무·한국 제도 이해 | 모형·수식 **유도**·한계 사례 |
| 수식 | 변수 표 → 식 → **기호 예시** | 위 + 비교정태·연습문제 |
| 막히면 | §0·§4a·[glossary](../00-roadmap/glossary.md) | 선수 L3 편으로 되돌아가기 |

---

## 2. Phase 읽기 순서 (메뉴와 동일)

| Phase | 무엇을 배우나 | 대표 경로 | 기간(가이드) |
|-------|----------------|-----------|--------------|
| **0** | 복리·비상금·가계·부채 | [01-foundations](../01-foundations/) | 2주 |
| **1** | 재무제표 | [financial-statements-study-roadmap](../01-foundations/financial-statements-study-roadmap.md) | 2~12주 |
| **2** | 미시·거시 경제 **L4** | [02-economics](../02-economics/) | 10~12주 |
| **3** | 주식·채권·ETF·시장 | [03-markets](../03-markets/) | 7주 |
| **3b** | 섹터·테마 | [sectors](../03-markets/sectors/) | 9주 병행 |
| **4** | 포트폴리오·bucket | [04-portfolio](../04-portfolio/) | 4주 |
| **5** | 한국 세금·ISA·DB·IRP | [06-korea-policy](../06-korea-policy/) | **병행** |
| **6** | 행동금융 | [05-behavioral](../05-behavioral/) | 선택 |
| **7** | 부동산·REIT | [07-real-estate](../07-real-estate/) | 선택 |
| **8** | CAPM·팩터·퀀트 | [08-advanced](../08-advanced/) | 선택 |
| **9** | M&A·VC | [09-corporate-finance](../09-corporate-finance/) | 선택 |

**병행**: Phase **5(세금·계좌)** 는 Phase 3~4와 같이 진행해도 됩니다.  
**실행 로드맵**: [master-roadmap](../00-roadmap/master-roadmap.md) · [ai-engineer-investing-playbook](../00-roadmap/ai-engineer-investing-playbook.md)

---

## 3. 한 편 읽는 순서 (5~10분 + 본문)

```mermaid
flowchart LR
  meta[메타_난이도] --> s0["§0_선행_5분"]
  s0 --> tldr[TL;DR]
  tldr --> body[본문_첫등장_박스]
  body --> s6["§6_변수표_후_수식"]
  s6 --> quiz[퀴즈]
```

1. **메타** — 난이도(L3/L4), 읽기 시간  
2. **§0 이 편 읽기 전** — 선수 링크, 이번 편 **기호·약어**  
3. **TL;DR** — 핵심 5줄  
4. **§4a 핵심 용어** — 복습용 표  
5. 본문 — `!!! info` **첫 등장 박스** (약어 풀이)  
6. **§6** — **변수 설명표 → 수식** (아래 §4 참고)  
7. **퀴즈** — 닫고 풀기  

---

## 4. 약어·수식 읽는 법

### 4.1 돈의 시간가치(TVM) — 가장 자주 나옴

| 기호 | 영문 | 뜻 |
|------|------|-----|
| **PV** | Present Value | **현재가치** — 오늘 기준 가치 |
| **FV** | Future Value | **미래가치** — 미래 시점 가치 |
| **PMT** | Payment | **정기 납입** — 매월·매년 같은 금액 |
| **r** | rate | **이자율·수익률**(연 또는 월) |
| **n** | periods | **기간**(년 또는 월) |

**복리(compound interest)**: 이전에 붙은 이자·수익이 다음 기간 **원금에 포함**되어 다시 불어나는 구조.  
**단리(simple interest)**: 이자가 원금에 다시 붙지 않음.

→ 처음부터: [복리와 시간가치](../01-foundations/compound-interest-and-time-value.md)  
→ 심화: [NPV·IRR](../01-foundations/time-value-npv-irr.md) (L4)

### 4.2 가계·투자 기호 (교육용)

| 기호 | 뜻 |
|------|-----|
| **M** | 월 **세후 실수령**(만 원) — 독자 본인 숫자로 치환 |
| **L_ISA** | ISA **연 납입 한도**(제도 상수) |

→ [DEPTH-STANDARD §교육용 금액 기호](DEPTH-STANDARD.md)

### 4.3 §6 수식이 나올 때

1. **변수 표** — 각 기호가 무엇인지  
2. **수식** — LaTeX 블록  
3. **기호 예시** — 구체 금액 대신 M·α 등  

---

## 5. 어디서 시작?

| 상황 | 시작 문서 |
|------|-----------|
| 오늘 첫날 | [STUDY-START](../00-roadmap/STUDY-START.md) |
| 돈·복리부터 | [compound-interest-and-time-value](../01-foundations/compound-interest-and-time-value.md) |
| 월급·저축부터 | [cash-flow-basics](../01-foundations/cash-flow-basics.md) |
| DB·ISA 실무 | [db-pension](../06-korea-policy/db-pension.md), [isa](../06-korea-policy/isa.md) |
| 전체 지도 | [CURRICULUM-MAP](../00-roadmap/CURRICULUM-MAP.md) |

**용어 사전**: [glossary](../00-roadmap/glossary.md)

---

## 6. 비공개 메모

본인 **실제 M·bucket 체크리스트**는 Git에 올라가지 않는 `private/` 폴더에만 둡니다. → [private-notes](private-notes.md)
