"""
👖 BLUE JEANS WEB NOVEL ENGINE v1.0 — prompt.py
웹소설 연재 최적화 프롬프트 시스템
19금/15금 듀얼 출력 · 클리프행어 엔진 · 떡밥 관리 · 과금 전환 설계
© 2026 BLUE JEANS PICTURES
"""

# =================================================================
# [1] SYSTEM PROMPT
# =================================================================
SYSTEM_PROMPT = """당신은 한국 웹소설 플랫폼(리디, 카카오페이지)에서 연재되는 상업 웹소설 전문 작가입니다.

[핵심 원칙]
1. 매 회차는 독자가 다음 회차를 결제하게 만드는 것이 목적이다.
2. 첫 문장에서 잡고, 마지막 3줄에서 다음 회차를 결정짓는다.
3. 감정은 행동과 신체 반응으로 보여준다. "슬펐다" "화가 났다" 금지.
4. 세계관 설명은 사건 속에 녹인다. 설정집 나열 금지.
5. 대사 비율 40% 이상. 모바일 독자는 지문 벽을 싫어한다.
6. 문단은 3~5줄 이내. 스마트폰 화면 가독성 우선.
7. 과금 관문 직전 3회차에 시즌 최강 반전을 배치한다.
8. 클리프행어 유형을 매 회차 끝에 의식적으로 설계한다.

[서사 동력 — Sorkin/Curtis 원칙]
- Intention & Obstacle: 주인공이 무엇을 원하고, 무엇이 막는가.
- Goal vs Need: 원하는 것과 필요한 것의 간극이 서사를 추진한다.
- Stakes: 실패하면 무엇을 잃는가. 판돈이 낮으면 긴장이 없다.
- Tactics = Character: 장애물을 넘는 방법이 캐릭터를 정의한다.
- Too Wet 금지: 캐릭터가 감정을 직접 설명하는 장면 금지.

[빌런 설계 — Villain 4 Questions]
- 빌런이 무엇을 원하는가?
- 왜 자신이 옳다고 믿는가?
- 어디까지 갈 수 있는가?
- 승률은? (중반까지 빌런이 이기고 있어야 한다)
""".strip()

# =================================================================
# [2] GENRE RULES — 웹소설 장르 Rule Pack
# =================================================================
GENRE_RULES = {
    "로맨스판타지": {
        "core_emotion": "설렘 + 긴장 + 통쾌",
        "must_have": [
            "신분 차이 또는 금지된 관계",
            "여주 성장 아크 (약→강, 또는 숨겨진 강함 발현)",
            "남주 냉/온 전환 (여주에게만 다른 모습)",
            "궁정/정치 권모술수",
            "비밀 또는 숨겨진 정체성",
            "재회/이별/재회 리듬",
        ],
        "hook_rule": "매 회차 끝에 관계 변화 or 정치적 반전",
        "punch_rule": "10회차 내 1회 이상 심장이 쿵 하는 장면",
        "setpiece": "가면무도회, 밀실 대면, 전장 재회, 독살 위기, 비밀 폭로, 정략결혼 선언, 왕좌 앞 대립",
        "forbidden": [
            "여주가 수동적으로 구출만 당함",
            "남주가 이유 없이 폭력적",
            "세계관 설명이 2회차 이상 지속",
            "로맨스 없이 정치극만 3회차 이상",
        ],
    },
    "로맨스": {
        "core_emotion": "설렘 + 애틋함 + 가슴 시림",
        "must_have": [
            "밀당 리듬 (가까워졌다 멀어졌다)",
            "오해와 화해의 반복",
            "상대의 숨겨진 면을 발견하는 장면",
            "고백 또는 고백에 준하는 행동",
        ],
        "hook_rule": "매 회차 끝에 관계의 온도가 변한다",
        "punch_rule": "5회차 내 1회 이상 심장 박동 장면",
        "setpiece": "우연한 신체 접촉, 비 오는 날, 취중 고백, 질투 폭발, 이별 통보, 공항/역 재회",
        "forbidden": [
            "감정 설명으로 페이지 채우기",
            "삼각관계 질질 끌기 (20회차 이상)",
        ],
    },
    "현대판타지": {
        "core_emotion": "성장 쾌감 + 통쾌 + 긴장",
        "must_have": [
            "능력 각성 또는 시스템 획득",
            "현실 세계 기반 + 초자연 요소",
            "레벨업/성장 가시화",
            "기존 강자와의 대립",
        ],
        "hook_rule": "매 회차 끝에 새로운 위협 or 능력 발현 힌트",
        "punch_rule": "5회차 내 1회 이상 압도적 전투/역전",
        "setpiece": "각성 장면, 던전/레이드, 랭커 대결, 세계관 비밀 발견",
        "forbidden": [
            "설정 나열이 행동을 대체",
            "주인공이 너무 쉽게 이김 (긴장 없는 먼치킨)",
        ],
    },
    "판타지": {
        "core_emotion": "경이 + 모험 + 성장",
        "must_have": [
            "독자적 세계관",
            "마법/초능력 체계",
            "퀘스트 또는 대의",
            "동료 관계",
        ],
        "hook_rule": "매 회차 끝에 세계관의 새로운 층위가 열린다",
        "punch_rule": "10회차 내 1회 이상 서사적 전투/모험 셋피스",
        "setpiece": "고대 유적 탐험, 용/괴수 대결, 왕국 방어전, 금지된 마법 발동",
        "forbidden": [
            "세계관 설명이 사건을 압도",
            "전투만 반복되고 인물이 성장하지 않음",
        ],
    },
    "무협": {
        "core_emotion": "비장 + 의리 + 쾌감",
        "must_have": [
            "무공 수련/성장",
            "사제/동문 관계",
            "강호 세력 다툼",
            "복수 또는 대의",
        ],
        "hook_rule": "매 회차 끝에 새로운 적 or 비기 발견 or 배신",
        "punch_rule": "5회차 내 1회 이상 무공 대결 셋피스",
        "setpiece": "비무대회, 암살 습격, 비기 전수, 사부 죽음, 마교 침입",
        "forbidden": [
            "무공 설명이 서사를 대체",
            "인물 이름 과다 (회차당 신규 5명 이상)",
        ],
    },
    "BL": {
        "core_emotion": "설렘 + 금기 + 애틋함",
        "must_have": [
            "두 남자 주인공의 관계 발전",
            "사회적/내면적 장벽",
            "서로에 대한 인식 변화",
            "신체 접촉의 점진적 확대",
        ],
        "hook_rule": "매 회차 끝에 관계의 경계가 한 단계 움직인다",
        "punch_rule": "5회차 내 1회 이상 심장 폭발 장면",
        "setpiece": "우연한 동거, 술 취한 밤, 질투 폭발, 공개적 선언, 이별 후 재회",
        "forbidden": [
            "공수 고정관념 강요",
            "폭력을 로맨스로 포장",
        ],
    },
    "GL": {
        "core_emotion": "설렘 + 발견 + 연대",
        "must_have": [
            "두 여자 주인공의 관계 발전",
            "정체성 탐색 또는 수용",
            "서로의 세계를 확장하는 관계",
            "감정 인식의 점진적 변화",
        ],
        "hook_rule": "매 회차 끝에 감정의 이름이 한 단계 선명해진다",
        "punch_rule": "5회차 내 1회 이상 설렘 극대화 장면",
        "setpiece": "함께하는 일상, 위기 속 보호, 고백, 주변의 시선, 선택의 순간",
        "forbidden": [
            "남성 시선으로 대상화",
            "비극적 결말 강요",
        ],
    },
    "스릴러": {
        "core_emotion": "긴장 + 공포 + 반전",
        "must_have": [
            "위협의 에스컬레이션",
            "정보 비대칭 (독자 vs 인물)",
            "타이머/데드라인",
            "믿을 수 없는 인물",
        ],
        "hook_rule": "매 회차 끝에 위험이 한 단계 가까워진다",
        "punch_rule": "5회차 내 1회 이상 반전",
        "setpiece": "추격, 밀실 탈출, 정체 폭로, 인질 상황, 함정",
        "forbidden": [
            "주인공이 우연으로 위기 탈출",
            "빌런 동기가 불분명",
        ],
    },
    "호러": {
        "core_emotion": "공포 + 불안 + 경악",
        "must_have": [
            "일상의 균열 (처음엔 작게)",
            "감각 묘사 우선 (시각보다 청각/촉각)",
            "안도→공포 리듬",
            "설명 불가능한 현상의 점진적 확대",
        ],
        "hook_rule": "매 회차 끝에 공포의 범위가 넓어진다",
        "punch_rule": "3회차 내 1회 이상 공포 절정",
        "setpiece": "혼자 있는 밤, 반복되는 현상, 사라진 사람, 거울/사진 속 이상, 도망칠 수 없는 공간",
        "forbidden": [
            "괴물이 너무 빨리 정체를 드러냄",
            "공포 없이 고어만 나열",
        ],
    },
}

def detect_genre_key(genre_input):
    """장르 입력 문자열에서 GENRE_RULES 키를 매칭."""
    gl = genre_input.strip()
    if gl in GENRE_RULES:
        return gl
    mapping = {
        "로판": "로맨스판타지", "로맨스 판타지": "로맨스판타지",
        "현판": "현대판타지", "현대 판타지": "현대판타지",
        "비엘": "BL", "bl": "BL",
        "지엘": "GL", "gl": "GL",
    }
    return mapping.get(gl, gl)

def get_genre_rules_block(genre_key):
    """장르 Rule Pack을 프롬프트 텍스트로 변환."""
    rules = GENRE_RULES.get(genre_key)
    if not rules:
        return ""
    lines = [f"[장르 Rule Pack — {genre_key}]"]
    lines.append(f"핵심 감정: {rules['core_emotion']}")
    lines.append("필수 요소:")
    for m in rules["must_have"]:
        lines.append(f"  - {m}")
    lines.append(f"Hook 규칙: {rules['hook_rule']}")
    lines.append(f"Punch 규칙: {rules['punch_rule']}")
    lines.append(f"셋피스: {rules['setpiece']}")
    lines.append("금지 사항:")
    for f in rules["forbidden"]:
        lines.append(f"  - {f}")
    return "\n".join(lines)

# =================================================================
# [3] CLIFFHANGER RULES
# =================================================================
CLIFFHANGER_TYPES = ["Slap", "Reveal", "Reversal", "Arrival", "Choice", "Threat", "Tears"]

CLIFFHANGER_RULES = """[클리프행어 7유형]
1. Slap — 물리적/감정적 충격. 뺨, 문 닫힘, 갑작스러운 행동.
2. Reveal — 비밀 폭로. "그 남자... 반도국 왕자였어."
3. Reversal — 상황 역전. 동맹이 적으로, 승리가 패배로.
4. Arrival — 새 인물/요소 등장. 죽었다던 사람이 나타남.
5. Choice — 불가능한 선택. 둘 중 하나를 포기해야 한다.
6. Threat — 임박한 위험. 적이 핵심 정보를 손에 넣는다.
7. Tears — 감정 폭발. 참아왔던 것이 터진다.

[클리프행어 규칙]
- 매 회차 마지막 3줄에 반드시 클리프행어를 배치한다.
- 같은 유형 3회차 연속 금지. 반드시 변주한다.
- 과금 관문 직전 회차에는 Reveal 또는 Reversal을 사용한다.
- 클리프행어는 다음 회차 첫 장면과 직결되어야 한다.
""".strip()

# =================================================================
# [4] RATING RULES — 19금/15금
# =================================================================
RATING_19 = """[19금 수위 규칙 — 리디 성인관]
허용:
- 직접적 성행위 묘사
- 신체 부위 직접 명명
- 관능적 감각 묘사 (촉각, 체온, 호흡, 땀, 맥박)
- 정사 장면이 관계 진전의 서사 장치로 기능

금지:
- 감정 없는 성묘사 (포르노그래피)
- 폭력적/비합의적 성행위의 미화
- 관능 씬이 플롯과 무관한 삽입

관능 씬 작법 원칙:
1. 정사 전: 감정적 긴장이 먼저 쌓인다. 물리적 접촉 이전에 심리적 접근이 있어야 한다.
2. 정사 중: 감각 묘사를 교차한다. 촉각→시각→청각→체온→호흡. 한 감각에 머물지 않는다.
3. 정사 후: 관계가 달라져야 한다. 씬 전후로 두 사람의 관계 온도가 변하지 않으면 실패.
4. 대사: 관능 씬 안의 대사는 짧고 끊어진다. 설명적 대사 금지.
5. 시점: 주인공의 감각에 밀착한다. 객관적 묘사로 빠지지 않는다.
""".strip()

RATING_15 = """[15금 수위 규칙 — 카카오페이지/네이버 시리즈]
허용:
- 키스, 포옹 직접 묘사
- 감각 암시 (따뜻함, 떨림, 심장 박동, 호흡)
- 의복 위의 접촉 묘사
- 시선이 눈/입술에 머무는 묘사

금지:
- 직접적 성행위 묘사
- 신체 부위 직접 명명
- 신음/관능적 소리 묘사
- 노출 묘사

15금 감정 전달 원칙:
1. 19금에서 정사로 전달하는 감정(신뢰, 취약성, 친밀감)을 다른 방식으로 전달한다.
2. 대체 방식: 비밀 공유, 위기 속 보호, 진심 고백, 함께하는 일상의 변화.
3. 장면 전환: 키스 이후 → "문이 닫혔다" → 다음 아침 (시간 점프).
4. 암시 기법: 흐트러진 이불, 빈 자리, 어깨 위 머리카락, 달라진 호칭.
""".strip()

RATING_CONVERSION_RULES = """[19금 → 15금 변환 규칙]

변환 매핑:
| 19금 요소 | 15금 대체 |
| 직접적 신체 접촉 묘사 | 의복 위의 감각 (옷깃 사이로 전해지는 체온) |
| 호흡/신음 | 침묵 또는 이름 부르기 |
| 시선이 신체를 따라감 | 시선이 눈/입술에 머무름 |
| 정사 후 묘사 | 다음 아침 — 흐트러진 이불, 빈 자리 |
| 관능적 대사 | 감정적 고백 (같은 취약성, 다른 표현) |

변환 원칙:
1. 단순 삭제 금지. 삭제하면 서사에 구멍이 난다.
2. 19금 씬의 서사적 기능(관계 진전, 신뢰 구축, 취약성 노출)을 15금 방식으로 대체한다.
3. 변환 후에도 회차 분량(3,500자 ± 500자)을 유지한다.
4. 관능 씬이 2,000자 이상인 경우, 삭제보다 별도 15금 대체 씬을 생성한다.
""".strip()

# =================================================================
# [5] AI ANTI-PATTERN RULES (Novel Engine 계승)
# =================================================================
AI_ANTI_PATTERN = """[AI 문체 탈출 규칙 A1~A14]

A1. 종결어미 반복 금지: 연속 3문장이 같은 종결어미(~다, ~했다)로 끝나면 안 된다.
A2. 주어 반복 금지: 같은 주어가 연속 3문장 주어로 오면 안 된다. 주어 생략/교체.
A3. 구문 구조 반복 금지: 연속 3줄이 동일 구문 패턴이면 안 된다.
A4. 감정 직접 서술 금지: "슬펐다/화가 났다/행복했다" → 행동/신체 반응으로 대체.
A5. "마치 ~처럼" 과잉 금지: 한 회차에 비유 표현 3회 이하.
A6. 감정 형용사 반복 금지: 같은 형용사를 같은 회차에서 2번 이상 쓰지 마라.
A7. 대시(—) 사용 제한: 회차당 2회 이하. 쉼표(,)나 마침표(.)로 대체.
A8. 별표(**) 금지: **강조** 같은 별표 강조는 AI 출력의 신호다. 절대 쓰지 마라.
A9. 접속부사 과잉 금지: "그러나/하지만/그리고" 연속 사용 금지.
A10. 시제 일관성: 과거형 기본. 현재형 전환은 의도적인 경우만.
A11. 요약 서술 금지: "그 후 며칠이 지났다" 식의 시간 압축을 장면 전환 없이 쓰지 마라.
A12. 설명적 대사 금지: 인물이 독자를 위해 상황을 설명하는 대사 금지.
A13. 편의적 우연 금지: 우연한 만남/발견으로 위기를 해결하지 마라.
A14. 감정 나열 금지: "분노와 슬픔과 후회가 밀려왔다" → 하나의 행동으로 보여줘라.
""".strip()

# =================================================================
# [6] PROSE CRAFT — 웹소설 특화
# =================================================================
WEB_NOVEL_PROSE_RULES = """[웹소설 문체 규칙]

[문장]
- 문장은 짧게. 평균 15~25자. 긴 문장은 끊어라.
- 한 문단 3~5줄. 모바일 한 화면에 들어오는 분량.
- 문단 사이에 한 줄 공백. 숨 쉴 틈을 준다.

[대사]
- 대사 비율 40% 이상.
- 대사는 짧게. 한 턴에 3줄 이하.
- 같은 캐릭터 연속 대사 금지. 지문을 사이에 넣어라.
- 대사 태그 변주: '말했다' 반복 금지. 행동 지문으로 화자를 표시.

[감각]
- 시각보다 촉각/청각/후각을 먼저 쓴다.
- 감정은 신체 반응으로: 손이 떨린다, 목이 마른다, 심장이 빨라진다.
- 온도/질감/냄새로 공간에 진입한다.

[리듬]
- 짧은 문장 3개 → 중간 문장 1개 → 짧은 문장. 리듬을 만든다.
- 충격 장면: 한 줄에 한 문장. 여백이 충격을 키운다.
- 관능 장면: 문장이 길어진다. 호흡이 느려진다.

[금지 패턴]
- "~것이었다", "~터였다", "~셈이었다" 종결 금지.
- 격언/비유/철학적 진술로 심리를 풀지 않는다.
- 설명적 장면 전환("한편 그 무렵") 금지.
- 풀네임 반복 금지. 첫 등장 이후 성 또는 이름만.
- "매 문장 줄바꿈" 금지. 문단 단위로 끊어라.
""".strip()

# =================================================================
# [7] EPISODE STRUCTURE
# =================================================================
EPISODE_STRUCTURE = """[회차 3단 구조]

[도입] 300~500자
  - 이전 회차 훅의 직접적 연결 (리캡이 아닌 연속)
  - 이번 회차의 질문/갈등 제기
  - 첫 3줄에서 독자를 잡는다

[전개] 2,000~2,800자
  - 갈등 전개 + 감정선 진행
  - 정보 공개 또는 숨김 (떡밥 Plant/Hint)
  - 씬 전환 최대 2회 (많으면 산만)
  - 대사와 행동이 번갈아 나온다

[훅(클리프행어)] 300~500자
  - 다음 회차를 읽게 만드는 장치
  - 7유형 중 선택 (Slap/Reveal/Reversal/Arrival/Choice/Threat/Tears)
  - 마지막 3줄이 가장 중요하다
  - 다음 회차 첫 장면과 직결
""".strip()

# =================================================================
# [8] RECAP RULES
# =================================================================
RECAP_RULES = """[리캡 처리 규칙]
독자가 며칠 후 돌아왔을 때 자연스럽게 상기시키는 기법.

금지:
- "지난 회차에서 ~했다" 식 직접 요약
- "이전에 ~라고 말한 적이 있었는데" 식 상기
- 작가 시점의 메타 서술

허용:
- 인물의 행동/대사 속에 자연스럽게 녹이기
  예: "공주는 어젯밤 히나스가 건넨 말을 아직 씹고 있었다."
- 소지품/공간을 통한 상기
  예: "목걸이를 만지작거리는 손. 반도국 문자가 새겨진 그것."
- 다른 인물의 언급
  예: "쿠로가 물었다. '공주께서 그날 밤 이후로 달라지셨다던데.'"
""".strip()

# =================================================================
# [9] PAYWALL DESIGN
# =================================================================
PAYWALL_DESIGN = """[과금 전환 설계]

무료 구간 (1~과금 전환점):
- 세계관 매력 극대화. 독자가 이 세계에 빠지게 만든다.
- 남녀 케미 확립. "이 두 사람의 관계가 궁금하다."
- 첫 번째 대형 반전을 무료 구간 끝에 배치.
- 빌런의 구체적 위협 확립. 판돈을 높인다.

과금 관문 (전환 직전 3회차):
- 시즌에서 가장 강한 반전/폭로.
- "여기서 끊기면 미칠 것 같다"는 감정 유발.
- Reveal 또는 Reversal 유형 클리프행어.

유료 구간 (과금 이후):
- 관계 심화 (19금에서는 관능 씬 시작).
- 정치극/액션 강도 상승.
- 떡밥 회수의 연쇄. 하나를 풀면 두 개가 열린다.
- 중반 위기(All Is Lost) → 역전의 카타르시스.
""".strip()

# =================================================================
# [10] AUTHOR STYLE DNA (Novel Engine 계승)
# =================================================================
AUTHOR_STYLE_DNA_BASE = """Mr.MOON 스타일 기본 규칙:
- 영화친화적인 상업 장편소설 톤으로 쓴다.
- 장면은 공간, 빛, 냄새, 소리, 촉감 중 최소 1개 감각 요소로 진입.
- 세계관 설명은 사건, 행동, 인물 반응, 대사 속에 배치.
- 주요 인물은 첫 등장 시 직업, 결핍, 비밀, 욕망 중 최소 2개가 드러나야 한다.
- 대사는 갈등, 관계 변화, 정보 전진에 기여.
- 감정은 결정적 장면에서 시선, 침묵, 몸짓, 행동으로 보여준다.
- 로맨스는 정보 교환, 위험 노출, 계급/권력 충돌과 함께 전진.
- 장면 말미에는 반전, 위협, 감정 흔들림, 선택 압력 중 하나를 남긴다.
- 감각어와 물성어를 반복 모티프로 사용.
- 문장은 중간 길이 기본, 전환과 충격 지점에서 짧게 끊는다.
- 설명문이 길어지면 장면과 대사로 환원.

문체 금지 패턴:
- '~것이었다','~터였다','~셈이었다' 종결 금지.
- 격언/비유/철학적 진술로 심리를 풀지 않는다.
- 설명적 장면 전환 금지.
- 플롯 무관 분위기 묘사 금지.
- 풀네임 끝까지 반복 금지.
- 기계적 리듬 반복 금지.
- 실존 명칭 금지.
- 매 문장 줄바꿈 금지.""".strip()

# =================================================================
# [11] HELPERS
# =================================================================
def _style_block(style_dna, style_strength="중"):
    sm = {
        "약": "문체 특징을 은은하게 반영하되 장르 요구와 가독성을 우선한다.",
        "중": "문체 특징을 분명히 반영하되 반복감이나 자기복제는 피한다.",
        "강": "문체 특징을 강하게 반영하되 추진력과 가독성은 무너뜨리지 않는다.",
    }
    return (
        f"[기본 STYLE DNA]\n{AUTHOR_STYLE_DNA_BASE}\n\n"
        f"[사용자 STYLE DNA]\n{style_dna or '사용자 문체 샘플 없음. 기본 STYLE DNA만 사용.'}\n\n"
        f"[문체 반영 강도]\n{sm.get(style_strength, sm['중'])}"
    )

def _pn_block(producer_note):
    if producer_note and producer_note.strip():
        return f"\n[프로듀서 노트 — 반드시 반영]\n{producer_note.strip()}\n"
    return ""

def _genre_block(genre):
    return get_genre_rules_block(detect_genre_key(genre))

def _rating_block(rating):
    if rating == "19":
        return RATING_19
    elif rating == "15":
        return RATING_15
    return RATING_19

# =================================================================
# [12] PROMPT BUILDERS
# =================================================================

# ── STEP 2: 시즌 아크 ──
def build_season_arc_prompt(concept, total_eps, producer_note="",
                            chunk=1, total_chunks=4, prev_summary=""):
    """25회차 단위 청크별 시즌 아크 생성."""
    genre = concept.get("genre", "로맨스판타지")
    paywall_ep = concept.get("paywall_ep", 25)

    blocks_per_chunk = 5
    start_block = (chunk - 1) * blocks_per_chunk + 1
    end_block = chunk * blocks_per_chunk
    start_ep = (start_block - 1) * 5 + 1
    end_ep = min(end_block * 5, total_eps)

    chunk_phases = {
        1: f"도입 + 갈등 구축 (EP1~25). 세계관 진입, 남녀 첫 만남, 비밀 설정. 과금 관문(EP{paywall_ep}) 직전에 최대 반전.",
        2: "중반 전개 (EP26~50). 관계 심화, 새로운 적대자, 삼각관계, 세계관 확장. 19금은 관능 씬 시작.",
        3: "클라이맥스 구축 (EP51~75). 최대 위기, 비밀 폭로, 배신, All Is Lost.",
        4: "최종 역전 + 결말 (EP76~100). 완전한 역전, 재회/이별, 떡밥 회수, 시즌2 떡밥.",
    }

    prev_block = ""
    if prev_summary:
        prev_block = f"\n[이전 청크 요약 — 이어서 설계할 것]\n{prev_summary}\n"

    paywall_note = ""
    if chunk == 1:
        paywall_note = f"\n★ EP{paywall_ep - 2}~{paywall_ep}은 과금 전환점. 이 청크에서 가장 강한 반전을 여기에 배치.\n"

    return f"""[TASK] {total_eps}화 웹소설 시즌 아크 — 청크 {chunk}/{total_chunks} (EP{start_ep}~{end_ep})

[컨셉]
제목: {concept.get('title', '')}
장르: {genre}
로그라인: {concept.get('logline', '')}
시즌 질문: {concept.get('season_question', '')}
주인공: {concept.get('protagonist', '')}
남주/여주: {concept.get('love_interest', '')}
빌런: {concept.get('villain', '')}
세계관: {concept.get('world', '')}
관계 구도: {concept.get('relationships', '')}
시놉시스: {concept.get('synopsis', '')}

{_genre_block(genre)}
{_pn_block(producer_note)}{prev_block}{paywall_note}
[이 청크의 국면]
{chunk_phases.get(chunk, '')}

{CLIFFHANGER_RULES}

[과금 전환 설계]
{PAYWALL_DESIGN}

[JSON 출력 — 이 청크의 5블록(25화)만]
{{
  "chunk": {chunk},
  "chunk_summary": "이 청크 25화 흐름 요약 2~3문장 (다음 청크에 전달용)",
  "blocks": [
    {{
      "block_no": {start_block},
      "ep_range": "EP{start_ep}~{start_ep + 4}",
      "phase": "국면",
      "theme": "핵심 감정/사건",
      "episodes": [
        {{
          "ep": {start_ep},
          "title": "회차 제목 (10자 이내)",
          "summary": "핵심 사건 1줄 (30자 이내)",
          "cliffhanger_type": "Slap|Reveal|Reversal|Arrival|Choice|Threat|Tears",
          "cliffhanger": "클리프행어 내용 1줄",
          "plant_or_payoff": "P:떡밥명 또는 H:떡밥명 또는 R:떡밥명 또는 없음"
        }}
      ]
    }}
  ]
}}""".strip()


# ── STEP 3: 떡밥 맵 ──
def build_plant_payoff_prompt(season_arc, characters):
    """시즌 아크에서 떡밥 맵 추출."""
    return f"""[TASK] 다음 시즌 아크에서 떡밥(Plant & Payoff) 맵을 설계하라.

[시즌 아크]
{season_arc}

[캐릭터]
{characters}

[떡밥 유형]
- 핵심 떡밥: 시즌 관통 비밀/미스터리. 70~90회차에 회수.
- 중기 떡밥: 20~30회 단위 서브플롯. 해당 구간 내 회수.
- 단기 떡밥: 3~5회 내 회수.
- 미끼(Red Herring): 의도적 오해 유도. 반전 시점에 정체 드러남.

[JSON 출력]
{{
  "plants": [
    {{
      "id": "P001",
      "name": "떡밥 이름",
      "type": "핵심|중기|단기|미끼",
      "description": "떡밥 내용 설명",
      "plant_ep": 0,
      "hints": [0, 0, 0],
      "payoff_ep": 0,
      "related_characters": ["인물1", "인물2"]
    }}
  ]
}}""".strip()


# ── STEP 4: 회차 플롯 ──
def build_episode_plot_prompt(season_arc_block, plant_map, ep_number,
                              prev_episodes_summary, producer_note=""):
    """개별 회차 플롯(도입/전개/훅) 설계."""
    return f"""[TASK] EP{ep_number} 회차 플롯 설계

[시즌 아크 — 해당 블록]
{season_arc_block}

[떡밥 맵 — 이번 회차 관련]
{plant_map}

[이전 회차 요약]
{prev_episodes_summary}

{_pn_block(producer_note)}

{EPISODE_STRUCTURE}

{CLIFFHANGER_RULES}

[JSON 출력]
{{
  "ep": {ep_number},
  "title": "회차 제목",
  "opening": {{
    "hook_line": "첫 문장 (독자를 잡는 한 줄)",
    "recap_method": "리캡 방식 (행동/소지품/대사 중)",
    "question": "이번 회차에서 독자가 품게 될 질문"
  }},
  "development": {{
    "scenes": [
      {{
        "scene_no": 1,
        "location": "장소",
        "characters": ["인물1", "인물2"],
        "conflict": "이 씬의 갈등",
        "outcome": "씬 결과",
        "plant_or_payoff": "P:떡밥명 또는 R:떡밥명 또는 없음"
      }}
    ],
    "emotion_arc": "이번 회차의 감정 곡선 (예: 불안→안도→충격)"
  }},
  "cliffhanger": {{
    "type": "7유형 중 하나",
    "content": "클리프행어 내용",
    "next_ep_connection": "다음 회차 첫 장면에 어떻게 연결되는지"
  }}
}}""".strip()


# ── STEP 5: 회차 원고 집필 ──
def build_episode_write_prompt(episode_plot, characters, style_dna,
                               genre, rating, prev_3_episodes,
                               plant_map_relevant, producer_note="",
                               style_strength="중", target_length=3500):
    """회차 원고 집필 (19금 또는 15금)."""
    return f"""[TASK] 웹소설 EP 원고 집필

{_genre_block(genre)}

{_rating_block(rating)}

{AI_ANTI_PATTERN}

{WEB_NOVEL_PROSE_RULES}

{EPISODE_STRUCTURE}

{RECAP_RULES}

{_style_block(style_dna, style_strength)}

{_pn_block(producer_note)}

[캐릭터 바이블]
{characters}

[떡밥 맵 — 이번 회차]
{plant_map_relevant}

[이전 3회차]
{prev_3_episodes}

[이번 회차 플롯]
{episode_plot}

[집필 지시]
- 분량: {target_length}자 ± 300자.
- 도입(300~500자) → 전개(2,000~2,800자) → 훅(300~500자).
- 클리프행어는 플롯에서 지정된 유형과 내용을 따른다.
- 리캡은 자연스럽게 녹인다. 직접 요약 금지.
- 대사 비율 40% 이상.
- 문단 3~5줄. 문단 사이 한 줄 공백.
- AI Anti-Pattern A1~A14를 반드시 지킨다.
- 마지막 3줄이 가장 중요하다.

[출력]
순수 원고 텍스트만 출력. JSON/마크다운/주석 금지.
""".strip()


# ── STEP 6: 15금 변환 ──
def build_rating_convert_prompt(episode_19_text):
    """19금 원고를 15금으로 변환."""
    return f"""[TASK] 19금 웹소설 원고를 15금으로 변환

{RATING_CONVERSION_RULES}

{RATING_15}

[변환 원칙]
1. 단순 삭제 금지. 서사적 기능을 유지하면서 표현을 전환한다.
2. 관능 씬은 감정/상징 씬으로 대체한다.
3. 변환 후에도 3,500자 ± 500자를 유지한다.
4. 캐릭터 관계의 온도 변화는 동일하게 유지한다.
5. 클리프행어는 변경하지 않는다.

[19금 원본]
{episode_19_text}

[출력]
15금 변환 원고 텍스트만 출력. JSON/마크다운/주석 금지.
""".strip()


def build_alternative_scene_prompt(episode_19_text, scene_description,
                                   characters, genre):
    """관능 씬 2,000자 이상일 때 별도 15금 대체 씬 생성 (B안)."""
    return f"""[TASK] 15금 대체 씬 생성

다음 19금 관능 씬의 서사적 기능(관계 진전, 신뢰 구축, 취약성 노출)을
15금 기준으로 완전히 다른 씬으로 재구성하라.

{_genre_block(genre)}
{RATING_15}

[관능 씬의 서사적 기능]
{scene_description}

[캐릭터]
{characters}

[19금 원본 참고 (톤/감정선 참고용)]
{episode_19_text}

[대체 씬 작법]
- 정사 대신: 비밀 공유, 위기 속 보호, 진심 고백, 함께하는 일상의 변화 중 선택.
- 같은 감정적 결과를 다른 경로로 도달한다.
- 분량: 1,500~2,500자.

[출력]
15금 대체 씬 텍스트만 출력.
""".strip()


# ── STEP 7: 품질 체크 ──
def build_quality_check_prompt(episode_text, episode_number, characters,
                               plant_map, prev_episodes_summary, rating):
    """회차 품질 자동 검사."""
    return f"""[TASK] EP{episode_number} 품질 체크

[원고]
{episode_text}

[캐릭터 바이블]
{characters}

[떡밥 맵]
{plant_map}

[이전 회차 요약]
{prev_episodes_summary}

[검사 항목 — JSON 출력]
{{
  "episode": {episode_number},
  "length": 0,
  "length_pass": true,
  "ai_antipattern_violations": [
    {{"rule": "A1", "location": "...", "suggestion": "..."}}
  ],
  "cliffhanger_check": {{
    "exists": true,
    "type": "유형",
    "strength": "상/중/하"
  }},
  "character_consistency": [
    {{"character": "이름", "issue": "문제점 또는 OK"}}
  ],
  "plant_payoff_check": [
    {{"id": "P001", "status": "정상 배치|누락|시점 오류"}}
  ],
  "dialogue_ratio": 0.0,
  "rating_compliance": {{
    "target": "{rating}금",
    "pass": true,
    "violations": []
  }},
  "recap_naturalness": "자연스러움|어색함|직접요약사용",
  "overall_score": 0,
  "top_3_improvements": ["...", "...", "..."]
}}""".strip()


# ── 유틸리티 ──
def build_episode_summary_prompt(episode_text, episode_number):
    """완료 회차 요약 (토큰 관리용)."""
    return f"""다음 EP{episode_number} 원고를 200자 이내로 요약하라.
포함 필수: 핵심 사건, 인물 관계 변화, 공개된 정보, 클리프행어.

[원고]
{episode_text}

[출력]
200자 이내 요약 텍스트만.
""".strip()
