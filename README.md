# 👖 BLUE JEANS WEB NOVEL ENGINE v2.0

**웹소설 연재 최적화 AI 콘텐츠 엔진**
3단계 파이프라인 · Core Arc 완결형 설계 · 인기 대응 Extension 모드
19금/15금 듀얼 출력 · 클리프행어 엔진 · 떡밥 관리

> *Core 50화로 시작해서 반응에 따라 100화, 시즌 2까지 확장하는 실전 연재 엔진*

---

## 소개

Web Novel Engine v2.0은 한국 웹소설 플랫폼(리디, 카카오페이지) 연재에 최적화된 AI 콘텐츠 생산 엔진입니다. 사전제작의 안정성과 연재 반응 대응의 유연성을 결합한 **Core Arc + Extension** 구조로 설계되었습니다.

---

## 3단계 파이프라인

```
STEP 1. CONCEPT (아이디어 / 기획서 / 직접입력)
   ├── 기획서 업로드 (DOCX/HWP/PDF/TXT 자동 파싱)
   ├── 한 줄 아이디어 → 컨셉 카드 자동 생성
   ├── 9칸 직접 입력
   └── 자동 보강 (빌런 / Fatal Flaw / 미스터리 축)
          ↓
STEP 2. BUILD-UP
   ├── 2-1. Core Arc (25화 × 2청크, 50화 완결형)
   ├── 2-2. 떡밥 맵 (Plant & Payoff + Extension 예비)
   ├── 2-3. 캐릭터 바이블
   ├── 2-4. 회차 플롯 (도입/전개/훅)
   └── 2-5. 🆙 Extension Arc (인기 대응 확장)
          ↓
STEP 3. WRITING
   ├── 3-1. 19금 원고 집필 (Opus)
   ├── 3-2. 15금 변환 (Sonnet)
   ├── 3-3. 품질 체크
   └── 3-4. 내보내기 (ZIP)
```

---

## 핵심 시스템

### 🎯 Core Arc + Extension 구조

Core 50화로 작게 시작해서 시장 반응에 따라 확장하는 실전 연재 패턴:

```
[Core Arc 50화]        독립 완결 가능
  ↓ 반응 지표 확인
[Extension +25~50화]   인기 대응 확장
  ↓
[Season 2]             장기 IP화
```

### 📊 Extension 3가지 모드

| 모드 | 타이밍 | 특징 |
|------|--------|------|
| **Bridge Extension** | 중반 30~35화 | 기존 회차 유지, 브릿지 3~5화만 재설계 |
| **Late Extension** | 후반 45화 전후 | 결말을 시즌1 클리프행어로 전환 |
| **Season Break** | 완결 후 | 독립 시즌 2로 개시 |

### 🏷️ 웹소설 공식 태그

환생 · 회귀 · 빙의 · 역하렘 · 치정 · 계약결혼 · 먼치킨 · 복수 · 사이다 — 9개 공식 태그 선택 시 해당 공식의 필수 요소와 훅 패턴이 프롬프트에 자동 주입됩니다.

### 🔥 클리프행어 엔진

7유형(Slap/Reveal/Reversal/Arrival/Choice/Threat/Tears) 자동 분류 + 연속 방지 + 과금 관문 Reveal/Reversal 강제.

### 🌱 떡밥 관리

- **핵심/중기/단기/미끼/Extension예비** 5종 분류
- 심기(Plant) → 힌트 → 회수(Payoff) 회차 자동 매핑
- Extension 시 기존 미회수 떡밥 자동 재활용

### 🔞 듀얼 수위

19금 원본(Opus) → 15금 변환(Sonnet). 단순 삭제가 아닌 서사적 기능 유지 변환.

---

## 장르

로맨스판타지 · 로맨스 · **치정 로맨스** · 현대판타지 · 판타지 · 무협 · BL · GL · 스릴러 · 호러

---

## 기술 스택

| 항목 | 선택 |
|------|------|
| AI 모델 | Claude API (Opus=집필, Sonnet=구조) |
| 프레임워크 | Streamlit Cloud |
| 기획서 파서 | python-docx, olefile(HWP), pypdf |
| 배포 | GitHub → Streamlit Cloud |

---

## 파일 구조

```
webnovel-engine/
├── main.py              # 3탭 UI + 파이프라인 (1,111줄)
├── prompt.py            # 프롬프트 시스템 (1,110줄)
├── parser.py            # 기획서 파일 파서 (164줄)
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```

---

## 설치 및 실행

```bash
streamlit run main.py
```

---

## 실전 사용 시나리오

### 시나리오 A. 기획서 → 즉시 연재
```
1. STEP 1 → 기획서 업로드 (DOCX)
2. STEP 1 → 자동 보강 실행
3. STEP 2 → Core Arc 50화 생성 → 떡밥 맵 → 캐릭터 바이블
4. STEP 3 → 회차별 집필 (19금 + 15금)
```

### 시나리오 B. 아이디어 → 기획 → 연재
```
1. STEP 1 → 아이디어 생성 모드
2. STEP 1 → 컨셉 카드 확인 및 수정
3. STEP 2 → Core Arc → 떡밥 → 플롯
4. STEP 3 → 집필
```

### 시나리오 C. 연재 중 Extension (50화 → 100화)
```
1. Core 50화 집필 완료 또는 30화 연재 진행 중
2. 독자 반응 확인 (유료 전환율, 댓글)
3. STEP 2 → Extension 탭 → 모드 선택 → 독자 피드백 입력
4. Extension +50화 생성
5. 추가 회차 집필
```

---

## 엔진 생태계

```
Creator Engine (영화/시리즈 기획)
    ├── Writer Engine      → 영화 시나리오
    ├── Series Engine      → OTT 시리즈
    ├── Novel Engine       → 상업 장편소설
    ├── Shortform Engine   → 숏폼 드라마 대본
    ├── ★ Web Novel Engine → 웹소설 연재물
    ├── Rewrite Engine     → 리라이트
    └── Translator Engines → 번역 (EN/JP)
```

---

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

## 버전 히스토리

| 버전 | 변경 |
|------|------|
| v1.0 | 초기 빌드. 8단계 파이프라인 |
| **v2.0** | **3단계 파이프라인 + Extension 모드. 기획서 파서. 컨셉 카드. 9공식 태그. 치정 로맨스 장르.** |

---

© 2026 BLUE JEANS PICTURES · Web Novel Engine v2.0
