# 부동산 투자 기초

> **면책**: 본 문서는 교육 목적이며, 특정 개인·법인에 대한 투자·세무·법률 자문이 아닙니다.

## 메타

| 항목 | 내용 |
|------|------|
| 최종 검증일 | 2026-05-24 |
| 난이도 | L3 (Deep) — [READER-GUIDE](../docs/READER-GUIDE.md) |
| 예상 읽기 시간 | 40~50분 |
| 관련 bucket | 주식·연금과 **별도** — 거주 vs 투자 구분 |

## 0. 이 편 읽기 전 (5분)

| 항목 | 내용 |
|------|------|
| **난이도** | L3 (Deep) — [READER-GUIDE §L등급](../docs/READER-GUIDE.md) |
| **선수** | 없음 |
| **이번 편에서 쓰는 기호** | 본문 §4·§4a 표 참고 |
| **복습 한 줄** | — |

## TL;DR

1. **부동산** = **거주(소비)** vs **투자**(임대·시세) — 목적이 다르면 회계·세금도 다름.
2. **레버리지**(대출)·**유동성 낮음**·거래비용·**양도세·종부세**.
3. **전세·월세** — 현금흐름·[debt](../01-foundations/debt-and-interest.md).
4. 주식 포트(**ISA·IRP·QQQ**)와 **상관·비중** 별도 설계.
5. 10년 자산 목표에 **부동산 필수 아님** — 청년 정책·주식과 **트레이드오프**.


## 1. 한 줄 정의 + 왜 중요한가

**정의**: **부동산 투자**는 임대수익·자본이득(시세 차익)을 목적으로 부동산·**REIT** 등에 자본을 배치하는 것입니다. **거주**는 소비에 가깝습니다.

**왜 중요한가**: “집 사야 성공” 서사와 **장기 주식·연금** 목표가 충돌할 수 있습니다. **금리·유동성**을 모르면 **레버리지**가 은퇴 설계를 무너뜨립니다.


## 2. 선수 / 이후

**선수**: [cash-flow-basics.md](../01-foundations/cash-flow-basics.md), [macroeconomics-basics.md](../02-economics/macroeconomics-basics.md), [debt-and-interest.md](../01-foundations/debt-and-interest.md)  
**이후**: REIT ETF 심화, 지역별 규제(별도 문서)


## 3. 직관·비유

부동산은 **무거운 가구** — 옮기기 어렵고(유동성), **할부(대출)** 로 크게 살 수 있습니다. 주식 ETF는 **바퀴 달린 서랍** — 내일 팔 수 있습니다(세금·규칙은 별도). **전세**는 “큰 보증금을 맡기고 사는 **임시 거주권**”입니다.


## 4. 정식 용어

| 용어 | English | 정의 |
|------|------|----------------|
| NOI | Net Operating Income | 임대수익−운영비 |
| 캡레이트 | Cap rate | NOI/가격 |
| LTV | Loan-to-Value | 대출/담보가치 |
| REIT | Real Estate Investment Trust | 상장 부동산 신탁 |
| 전세 | Jeonse | 보증금 거주 |
| 양도소득세 | CGT on property | 매도 차익 과세 |
| 종부세 | Comprehensive real estate tax | 보유 세금 |

### 4a. 핵심 용어 (본문 등장 순)

> 복습용. 정의는 §4 본표·[glossary](../00-roadmap/glossary.md)·본문 `!!! info` 박스.

| 용어 | 한 줄 | 관련 이론 | glossary |
|------|------|------|----------------|
| NOI | 임대수익−운영비 | §4 | [glossary](../00-roadmap/glossary.md#noi) |
| 캡레이트 | NOI/가격 | §4 | [glossary](../00-roadmap/glossary.md#캡레이트) |
| LTV | 대출/담보가치 | §4 | [glossary](../00-roadmap/glossary.md#ltv) |
| REIT | 상장 부동산 신탁 | §4 | [glossary](../00-roadmap/glossary.md#reit) |
| 전세 | 보증금 거주 | §4 | [glossary](../00-roadmap/glossary.md#전세) |
| 양도소득세 | 매도 차익 과세 | §4 | [glossary](../00-roadmap/glossary.md#양도소득세) |
| 종부세 | 보유 세금 | §4 | [glossary](../00-roadmap/glossary.md#종부세) |


## 5. 메커니즘

```mermaid
flowchart TD
  Buy[매입_대출_LTV] --> CF[임대_현금흐름_NOI]
  CF --> Service[이자_상환]
  CF --> Opex[운영비_관리]
  Price[시세_변동] --> Equity[순자산]
  Service --> Risk[금리_상승_리스크]
```

```mermaid
flowchart LR
  Live[거주_전세_월세] --> Cons[소비_성격]
  Inv[투자_임대_REIT] --> Ret[수익_성격]
```


## 6. 수식·모델

| 기호 | 이름 | 이 식에서 의미 |
|------|------|----------------|
| **r** | 할인율·수익률 | 기간당 이자·요구수익률 |
| **n** | 기간 | 연·월 등 복리·할인에 쓰는 횟수 |
| **PV** | 현재가치 | 오늘 시점으로 환산한 금액 |
| **FV** | 미래가치 | 미래 시점의 목표·결과 금액 |

\[
\text{Cap rate} = \frac{\text{NOI}}{\text{가격}}
\]

**식 (기호)**: **Cap** **rate** = (**NOI**) / (가격)


**식 (기호)**: **Cap** **rate** = (**NOI**) / (가격)



**읽는 법**: **Cap**와 **NOI**의 관계를 위 식으로 쓴다. 경제·재무 해석은 변수표 「이 식에서 의미」와 [DEPTH-STANDARD](../docs/DEPTH-STANDARD.md) 기호 예제를 맞춘다.
| 기호 | 이름 | 이 식에서 의미 |
|------|------|----------------|
| **r** | 할인율·수익률 | 기간당 이자·요구수익률 |
| **n** | 기간 | 연·월 등 복리·할인에 쓰는 횟수 |
| **PV** | 현재가치 | 오늘 시점으로 환산한 금액 |

\[
\text{LTV} = \frac{\text{대출잔액}}{\text{담보가치}}
\]

**식 (기호)**: **LTV** = (대출잔액) / (담보가치)


**식 (기호)**: **LTV** = (대출잔액) / (담보가치)



**읽는 법**: **r**와 **n**의 관계를 위 식으로 쓴다. 경제·재무 해석은 변수표 「이 식에서 의미」와 [DEPTH-STANDARD](../docs/DEPTH-STANDARD.md) 기호 예제를 맞춘다.
**현금흐름**(단순):

| 기호 | 이름 | 이 식에서 의미 |
|------|------|----------------|
| **r** | 할인율·수익률 | 기간당 이자·요구수익률 |
| **n** | 기간 | 연·월 등 복리·할인에 쓰는 횟수 |
| **PV** | 현재가치 | 오늘 시점으로 환산한 금액 |

\[
CF = \text{임대료} - \text{이자} - \text{운영비} - \text{원금상환}
\]

**식 (기호)**: **CF** = 임대료 - 이자 - 운영비 - 원금상환


**식 (기호)**: **CF** = 임대료 - 이자 - 운영비 - 원금상환



**읽는 법**: **r**와 **n**의 관계를 위 식으로 쓴다. 경제·재무 해석은 변수표 「이 식에서 의미」와 [DEPTH-STANDARD](../docs/DEPTH-STANDARD.md) 기호 예제를 맞춘다.---

ocs/DEPTH-STANDARD.md) 기호 예제를 맞춘다.---

## 7. 한국 적용

### 7.1 2025~2026

| 항목 | 내용 |
|------|------|
| 양도소득세 | **거주·보유 기간**·주택 수 |
| 취득세 | 매입 시 |
| 종부세 | 고액 **보유** |
| 전세 | 보증금 **채권**·[debt](../01-foundations/debt-and-interest.md) |
| REIT ETF | **주식 계좌·ISA** — 상품별 |

### 7.2 주식·정책과 관계

| | 부동산 | 주식·ISA·IRP |
|------|------|----------------|
| 유동성 | 낮음 | 상대적 높음 |
| 청년도약 | **무관** | 별도 |
| DB QQQ | 무관 | IRP·ISA |

### 7.3 2025 vs 2026 (거시)

| 요인 | 부동산 | 주식 포트 |
|------|------|----------------|
| 금리↑ | **대출 부담** | 채권·성장주 변동 |
| 전세가 | 보증금 **규모** | 현금흐름 |
| REIT | **금리 민감** | ISA 편입 검토 |

### 7.4 의사결정 (교육)

```mermaid
flowchart TD
  Q{10년_목표}
  Q -->|유동성_우선| Stock[ISA_IRP_QQQ]
  Q -->|거주_안정| Jeon[전세_또는_월세]
  Q -->|투자_임대| RE[REIT_또는_직접_신중]
```

### 7.5 전세·월세·대출 — 현금흐름 연결

| 선택 | 현금흐름 | 주식 포트와 충돌 |
|------|------|----------------|
| 전세 | 보증금 **일시 유출** | DCA **축소** 위험 |
| 월세 | 매월 **고정 지출** | 비상금 Bucket 0 우선 |
| 매수+LTV | 이자·원금 | **레버리지** — 금리 shock |
| REIT ETF | **소액**·유동 | ISA·IRP 편입 검토 |

### 7.6 10년 목표 — 부동산 vs 주식·연금 (교육)

```mermaid
flowchart TD
  Goal[10년_순자산] --> Q{유동성_우선?}
  Q -->|예| Fin[ISA_IRP_QQQ_코어]
  Q -->|거주_안정| Home[전세_월세]
  Q -->|임대_전문| RE[REIT_또는_직접_신중]
  Fin --> Leap[청년도약_만기_후_재배분]
```

| | 주식·ISA·IRP | 직접 부동산 |
|------|------|----------------|
| 최소 금액 | 낮음 | 높음 |
| 유동성 | 상대 높음 | **낮음** |
| 레버리지 | QLD 등 **비권장** | **LTV** |
| 세금 문서 | tax 시리즈 | 본 문서·전문가 |

**법·정책 근거**: 소득세법(양도·보유), 지방세(취득·종부), 주택법·전세 관련 규정 — **개요만**.


### 7.7 REIT·부동산 ETF — 주식 포트 연동

| 상품 | 특징 | 세금·계좌 |
|------|------|----------------|
| 상장 REIT ETF | 유동성·소액 | 국내주식·ISA 규칙 |
| 미국 REIT ETF | 배당·양도 | Part1·2 |
| 직접 임대 | LTV·관리 | 양도·보유세 |

**10억 목표**를 부동산 **직접**만으로 맞추려면 LTV·금리·공실 리스크가 큽니다. [asset-allocation.md](../04-portfolio/asset-allocation.md)에서 **주식·연금·REIT** 비중을 함께 설계하세요.


## 8. 숫자 예제 (가상)

> 가상 인물·금액.

> 가상 인물·금액.

### 예제 1: 전세 vs 매수 (가상)

| | 가상 AH (전세) |
|--|----------------|
| 보증금 | **F**(가상) |
| 주식 ISA | 월 80만 DCA |
| **유동성** | 높음 |

| | 가상 AI (매수) |
|--|----------------|
| 대출 LTV 70% | 금리 4% |
| 월 이자(가상) | **M** |
| **주식 DCA** | 축소 |

### 예제 2: REIT vs 직접 (가상)

| | REIT ETF | 직접 임대 |
|------|------|----------------|
| 최소 금액 | 낮음 | 높음 |
| 레버리지 | 펀드 구조 | **본인 LTV** |
| 유동성 | **장중 매도** | 매도 어려움 |

### 예제 3: 금리 shock (가상)

| | 가상 AJ |
|--|---------|
| 금리 +2%p | 월 상환 +**M** |
| 임대료 고정 | CF **악화** |


## 9. FAQ

**Q1.** 20대에 집 필수? — **아니오**.  
**Q2.** REIT vs 직접? — **유동성·레버리지**.  
**Q3.** 주식과? — **별도** bucket·비중.  
**Q4.** 청년도약? — **무관**.  
**Q5.** ISA에 REIT? — **상품별** 가능.  
**Q6.** 전세=투자? — **거주** 소비.  
**Q7.** AI·전력 섹터? — [power-grid](../03-markets/sectors/power-grid-electrification.md) — 주식 노출.  
**Q8.** 10억 목표? — 부동산 **선택**.


### 실행 워크숍 체크리스트 (교육)

| # | 질문 | Yes 시 다음 문서 |
|------|------|----------------|
| 1 | 해외 ETF·주식을 보유 중인가? | [overseas-stocks-tax-part1-cgt.md](overseas-stocks-tax-part1-cgt.md) |
| 2 | 해외 배당이 연 500만 이상인가? | [part2-dividend](overseas-stocks-tax-part2-dividend.md) |
| 3 | DB 재직인가? | [db-pension.md](../db-pension.md) + IRP·ISA |
| 4 | 국내주식을 NXT에서 거래하는가? | [korea-ats-nextrade.md](../03-markets/korea-ats-nextrade.md) |
| 5 | 10년 코어가 QQQ인가? | [isa.md](../isa.md) 또는 [isa-irp-pension-tax.md](isa-irp-pension-tax.md) |

위 표는 **의사결정 보조**이며, 개인 소득·가구·회사 제도에 따라 답이 달라집니다. 불확실하면 [investment-tax-overview.md](investment-tax-overview.md) → [account-product-tax-map.md](account-product-tax-map.md) 순으로 읽으세요.


## 10. 함정·리스크·한계

- **거주=투자** 착각  
- **금리·LTV** 무시  
- **전세·보증금** 리스크  
- **유동성** 과소평가  
- **세법** 개정

---


**Q. 실무에서는?**  
교과서 식·기호를 그대로 적용하기 전에 **수수료·세금·데이터 시점**을 분리한다. 숫자는 [DEPTH-STANDARD](../docs/DEPTH-STANDARD.md)처럼 기호만 먼저 맞추고, 법령·시장 수치는 §8 표·외부 출처로 갱신한다.

## L3 보충 — 장기 자산 형성 연결

본 절은 [DEPTH-STANDARD.md](../../docs/DEPTH-STANDARD.md) L3 게이트를 충족하기 위한 **실행·교차 링크** 보충입니다.

### Bucket·현금흐름 연결

| Bucket | 대표 제도·자산 | 본 문서와의 관계 |
|------|------|----------------|
| 0 | 비상금 MMDA | 세금·투자 **전** 우선 |
| 1 | [청년도약](../06-korea-policy/youth-leap-account.md)·[미래적금](../06-korea-policy/youth-future-savings.md) | 정책 적금 — 주식 **대체 아님** |
| 2a | DB·DC | [db-vs-dc-pension.md](../06-korea-policy/db-vs-dc-pension.md) |
| 2b | ISA·IRP | [isa.md](../06-korea-policy/isa.md)·[isa-irp-pension-tax.md](../06-korea-policy/tax/isa-irp-pension-tax.md) |
| 3 | QQQ·채권 코어 | [capm-and-risk-return.md](../08-advanced/capm-and-risk-return.md) |
| 4 | NXT·코스닥·QLD | [fomo-and-trading-hours.md](../05-behavioral/fomo-and-trading-hours.md) |

### 연간 점검 루틴 (교육)

| 분기 | 할 일 |
|------|--------|
| Q1 | [investment-tax-overview.md](../06-korea-policy/tax/investment-tax-overview.md) 캘린더 확인 |
| Q2 | [rebalancing-and-dca.md](../04-portfolio/rebalancing-and-dca.md) 코어 비중 |
| Q3 | 해외 배당·금융소득 **누적** — Part2 |
| Q4 | 익년 **5월** 양도세 자료 정리 — Part1 |
| ISA | 개설일 +36개월 **만기** 알림 |

### 2025 vs 2026 정책 추적

| 항목 | 확인 출처 |
|------|-----------|
| ISA 한도·비과세 | 금융위·조세특례 시행일 |
| DC +300만 공제 | 국세청·통합연금포털 |
| 청년도약 일몰·미래적금 | [kinfa](https://ylaccount.kinfa.or.kr) |
| 금융투자소득세 | 금융위 보도·[sources.md](../../references/sources.md) |
| NXT 종목·거래중단 | [nextrade.co.kr](https://www.nextrade.co.kr) |

**면책 재확인**: 가상 예제·보도 수치는 **시점별 개정**됩니다. 실행·신고 전 공식 출처를 확인하세요.


## 11. 심화 읽기

- [asset-allocation.md](../04-portfolio/asset-allocation.md)  
- [time-horizon-and-buckets.md](../04-portfolio/time-horizon-and-buckets.md)


## 12. 퀴즈

1. REIT 장점 한 가지?  
2. 전세 vs 투자 매입?  
3. 금리↑ LTV 보유자?  
4. 청년도약과?  
5. Cap rate 식?

<details><summary>힌트</summary>1. 유동성 2. 거주 vs 수익 3. 이자 부담 4. 무관 5. NOI/가격</details>