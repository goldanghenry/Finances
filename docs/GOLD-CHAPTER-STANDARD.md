# 골드 편 기준 (GOLD-CHAPTER-STANDARD)

> 저자·편집용. 독자는 [READER-GUIDE](READER-GUIDE.md)만 보면 된다.  
> **모범 편**: [compound-interest-and-time-value.md](../01-foundations/compound-interest-and-time-value.md)

---

## L3 편 — 편당 통과 조건 (G1~G6)

| ID | 항목 | 통과 조건 |
|----|------|-----------|
| G1 | §6 변수표 | 각 `\[...\]` **직전**에 3열 표(기호·이름·**이 식에서 의미**); placeholder·`TODO:meaning` **0** |
| G2 | §6 읽는 법 | 식 **직후** 2~4문장; **기호 이름**을 본문에 언급; 템플릿 문장 금지 |
| G3 | §8 예제 | [DEPTH-STANDARD](DEPTH-STANDARD.md) 교육용 기호(M·P·PV·F₀…); 구체 연봉·만 원 금액 금지 |
| G4 | FAQ | §10에 「실무에서는?」 또는 동등 질문 **1개 이상** |
| G5 | 자급자족 | §0·§4·첫 등장 `!!! info`로 선수 없이 기호 이해 가능 |
| G6 | 무결성 | `lint_corpus_quality.py` + `lint_gold_chapter.py` **0 error** |

### G1 — 변수표 (Good vs Bad)

**Good** (식마다 구체적 의미):

```markdown
| 기호 | 이름 | 이 식에서 의미 |
|------|------|----------------|
| **FV** | 미래가치 | **n**기간 끝에 모인 총액 |
| **PMT** | 정기 납입 | 매 기간 **같은** 납입액 |

\[
FV = PMT \times \frac{(1+r)^n - 1}{r}
\]

**읽는 법**: 매 기간 **PMT**가 **r**로 **n**번 복리되면 **FV**가 된다.
```

**Bad**:

```markdown
| \(r\) | r | 본문 §4·위 식 맥락 참고 |

**읽는 법**: 위 식의 기호는 바로 위 변수표와 같다. 숫자는 DEPTH-STANDARD…
```

### G2 — 읽는 법

- **Good**: 식에 등장하는 기호 2개 이상을 **이름으로** 쓰고, 경제·재무 해석 1문장.
- **Bad**: 모든 식에 동일한 2문장 템플릿만 반복.

### G3 — §8 예제

- **Good**: 「월 실수령 **M**, 비상금 **B**, ISA **T**…」
- **Bad**: 「실수령 320만 원, ISA 50만…」

---

## L4 편 — L3 전부 + G7~G9

| ID | 항목 | 통과 조건 |
|----|------|-----------|
| G7 | 유도 | 주요 §6 식 **앞뒤**에 번호 유도 단계 + 단계마다 해석 1문장 |
| G8 | 연습 | `## 연습문제` 또는 §12에 문제 **3+**, 해설 키(기호·부등식) |
| G9 | 한계 | §11 또는 §6에 「가정이 깨지면」 한계 **1+** |

---

## 편집 워크플로 (2-pass)

1. `python scripts/lint_gold_chapter.py path/to/file.md`
2. Pass 1: §6 변수표·읽는 법·§8 기호화
3. Pass 2: FAQ·L4 유도·연습·§3↔§6 스레드
4. `python scripts/lint_gold_chapter.py` (전체) → 0
5. `mkdocs build`

---

## 금지 문자열 (린트가 잡음)

- `§4·본문 정의 참고`
- `본문 §4·위 식 맥락 참고`
- `위 식의 기호는 바로 위 변수표와 같다`

---

## 검증 명령

```bash
python scripts/lint_gold_chapter.py
python scripts/lint_corpus_quality.py
mkdocs build
```
