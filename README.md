# 👖 BLUE JEANS WEB NOVEL ENGINE v1.0

**웹소설 연재 최적화 AI 콘텐츠 엔진**
19금/15금 듀얼 출력 · 클리프행어 엔진 · 떡밥 관리 · 과금 전환 설계

> *Creator Engine이 기획을 만들고, Web Novel Engine이 연재를 만든다.*

---

## 소개

Web Novel Engine은 한국 웹소설 플랫폼(리디, 카카오페이지) 연재에 최적화된 AI 콘텐츠 생산 엔진입니다. Creator Engine의 코어 서사를 입력받아, 80~100회차 시즌 아크 설계부터 회차별 원고 집필, 19금/15금 듀얼 버전 출력까지 전체 연재 파이프라인을 지원합니다.

## 파이프라인

```
STEP 1  자료 입력         Creator Engine 연동 + 웹소설 고유 설정
STEP 2  시즌 아크 설계     25회차 × 4청크 순차 생성
STEP 3  떡밥 맵 설계       Plant / Payoff / Red Herring 배치
STEP 4  회차 플롯 설계     도입 / 전개 / 훅 3단 구조
STEP 5  회차 원고 집필     Opus 모델 · 19금 기준 원본
STEP 6  15금 변환          관능 씬 → 감정/상징 씬 대체
STEP 7  품질 체크          AI Anti-Pattern + 떡밥 + 캐릭터 일관성
STEP 8  내보내기           TXT / ZIP (19금·15금 분리)
```

## 핵심 시스템

| 시스템 | 설명 |
|--------|------|
| **듀얼 수위** | 19금 원본 → 15금 자동 변환 + 별도 대체 씬 생성 (B안) |
| **클리프행어 엔진** | 7유형(Slap/Reveal/Reversal/Arrival/Choice/Threat/Tears) + 연속 방지 |
| **떡밥 관리** | 핵심/중기/단기/미끼 분류 + 심기·힌트·회수 회차 배치 + 미회수 경고 |
| **과금 전환 설계** | 무료→유료 구간별 서사 밀도 차별화 |
| **프로듀서 노트** | 세션 전체 지시 주입 (Shortform Engine 계승) |
| **4청크 아크 생성** | 25회차 단위 순차 생성 + 캐릭터 바이블 주입 (Shortform Engine 계승) |
| **AI Anti-Pattern A1~A14** | 문체 품질 검증 (Novel Engine 계승) |
| **장르 Rule Pack** | 9장르 웹소설 특화 규칙 |
| **Style DNA** | 작가 고유 문체 분석 + 반영 (Novel Engine 계승) |

## 장르

로맨스판타지 · 로맨스 · 현대판타지 · 판타지 · 무협 · BL · GL · 스릴러 · 호러

## 기술 스택

| 항목 | 선택 |
|------|------|
| AI 모델 | Claude API (Opus=집필, Sonnet=구조) |
| 프레임워크 | Streamlit Cloud |
| 배포 | GitHub → Streamlit Cloud |
| API 키 | Streamlit Secrets |

## 설치 및 실행

```bash
streamlit run main.py
```

## 엔진 생태계

```
Creator Engine (기획)
    ├── Writer Engine      → 영화 시나리오
    ├── Series Engine      → OTT 시리즈
    ├── Novel Engine       → 상업 장편소설
    ├── Shortform Engine   → 숏폼 드라마 대본
    ├── ★ Web Novel Engine → 웹소설 연재물
    ├── Rewrite Engine     → 리라이트
    └── Translator Engines → 번역 (EN/JP)
```

## 디자인 시스템

| 요소 | 값 |
|------|-----|
| Primary | Midnight Navy `#191970` |
| Accent | Stitch Yellow `#FFCB05` |
| Display | Playfair Display 900 |
| Heading | Paperlogy 700 |
| Body | Pretendard |
| Mode | Light (강제) |

---

© 2026 BLUE JEANS PICTURES · Web Novel Engine v1.0
