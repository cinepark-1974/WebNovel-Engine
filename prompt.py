"""
👖 BLUE JEANS WEB NOVEL ENGINE v3.0 — prompt.py
3단계 파이프라인 (CONCEPT → BUILD-UP → WRITING) + EXTENSION
Core Arc 완결형 설계 + 인기 대응 확장 모드
v2.6.4: Context-Aware Description (첫 등장 풀 / 재등장 압축 / 씬 타입 차등)
v3.0:   Phase A 데이터 모듈 통합 + Phase B 신규 블록 빌더 5종
        (formula_strategy / motif / character_role / mind_flow_arc / market_viability)
© 2026 BLUE JEANS PICTURES
"""

# =================================================================
# [v3.0] Phase A 데이터 모듈 import (선택적 — 실패해도 v2.6.4 동작 유지)
# =================================================================
try:
    from data_motifs import (
        RELATIONSHIP_MOTIFS_DICT,
        ROMANCE_FORMULAS,
        MOVEMENT_NARRATIVE_PATTERNS,
        HIGH_RATING_ROMANCE_MOTIFS,
    )
    _V3_MOTIFS_AVAILABLE = True
except ImportError:
    RELATIONSHIP_MOTIFS_DICT = {}
    ROMANCE_FORMULAS = {}
    MOVEMENT_NARRATIVE_PATTERNS = {}
    HIGH_RATING_ROMANCE_MOTIFS = {}
    _V3_MOTIFS_AVAILABLE = False

try:
    from data_character import (
        CHARACTER_ROLE_TAXONOMY,
        MOE_ATTRIBUTES_25,
        HEROINE_MIND_FLOW_PATTERNS,
        HERO_MIND_FLOW_PATTERNS,
        READER_CONSUMPTION_TIERS,
        get_mind_flow_stage_for_episode,
        get_hero_mind_flow_stage_for_episode,
        detect_work_orientation,
        get_stage_for_episode_with_orientation,
        get_mind_flow_for_orientation,
    )
    _V3_CHARACTER_AVAILABLE = True
except ImportError:
    CHARACTER_ROLE_TAXONOMY = {}
    MOE_ATTRIBUTES_25 = {}
    HEROINE_MIND_FLOW_PATTERNS = {"stages": []}
    HERO_MIND_FLOW_PATTERNS = {"stages": []}
    READER_CONSUMPTION_TIERS = {}
    get_mind_flow_stage_for_episode = lambda ep, total=42: {}
    get_hero_mind_flow_stage_for_episode = lambda ep, total=42: {}
    detect_work_orientation = lambda concept: "female"
    get_stage_for_episode_with_orientation = lambda ep, total=42, orientation="female": {}
    get_mind_flow_for_orientation = lambda orientation: {"stages": []}
    _V3_CHARACTER_AVAILABLE = False

try:
    from data_market import (
        MARKET_DATA_2024,
        calculate_market_viability_score,
        validate_cliffhanger_distribution,
    )
    _V3_MARKET_AVAILABLE = True
except ImportError:
    MARKET_DATA_2024 = {}
    calculate_market_viability_score = lambda *args, **kwargs: {"total": 0, "grade": "N/A"}
    validate_cliffhanger_distribution = lambda *args, **kwargs: {"in_range": [], "out_of_range": []}
    _V3_MARKET_AVAILABLE = False

try:
    from data_strategy import (
        ROFAN_CREATION_STRATEGY,
        HETEROTOPIA_FRAME,
        POV_BLENDING_GUIDE,
    )
    _V3_STRATEGY_AVAILABLE = True
except ImportError:
    ROFAN_CREATION_STRATEGY = {}
    HETEROTOPIA_FRAME = {}
    POV_BLENDING_GUIDE = {}
    _V3_STRATEGY_AVAILABLE = False


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

[연재형 웹소설 구조 원칙]
- Core Arc는 독립 완결 가능해야 한다. Extension이 없어도 이야기가 성립.
- 미회수 떡밥은 "열린 결말"로, 회수된 떡밥은 "닫힌 결말"로.
- Extension은 기존 떡밥 재활용 + 신규 떡밥 결합으로 설계.
""".strip()


def build_system_prompt(narrative_tone="", for_episode_write=False):
    """v2.5: 작품 지향점 + 픽션 프레임 + 작가 페르소나를 결합한 시스템 프롬프트.

    for_episode_write=True일 때만 풀 픽션 프레임 적용 (구조 단계에서는 불필요).
    """
    base = SYSTEM_PROMPT
    # v2.6.2: 집필 시 분량 강제 규칙 시스템 프롬프트에 주입
    LENGTH_ENFORCEMENT = """
[★ 분량 강제 규칙 ★]
당신은 한국 웹소설 전문 작가입니다.
한국 웹소설 1회차 표준 분량은 5,000~6,000자입니다.
이는 절대 규칙이며, 짧게 끝내는 것은 작가로서 가장 큰 결격사유입니다.
- 한 씬 최소 1,000~1,500자
- 회차 전체 최소 4,800자
- 분량이 부족하면 인물 내면·감각 묘사·대사 후 반응을 더 풀어쓸 것
- "이 정도면 됐다"는 판단을 절대 하지 말 것
- 플롯의 모든 사건을 충실히 묘사할 것
""".strip()

    if for_episode_write and narrative_tone:
        tone_block = get_narrative_tone_block(narrative_tone)
        if tone_block:
            return f"""{base}

{LENGTH_ENFORCEMENT}

{FICTION_FRAME_DECLARATION}

{tone_block}

{NARRATIVE_FUNCTION_CHECK}

{ABSOLUTE_LIMITS}
"""
    if for_episode_write:
        return f"{base}\n\n{LENGTH_ENFORCEMENT}"
    return base

# =================================================================
# [2] 웹소설 공식 태그 시스템 (NEW)
# =================================================================
WEB_NOVEL_FORMULAS = {
    "환생": {
        "description": "주인공이 죽은 후 다른 사람 몸으로 환생",
        "must_have": [
            "환생 전후 정체성 대비 (기억/성격/능력 차이)",
            "원래 몸 주인의 삶을 추적하며 발견하는 과정",
            "정체성 탄로 위기 (주변 인물이 이상함을 감지)",
            "원래 자아 유지 vs 새 삶 적응의 갈등",
        ],
        "hook_patterns": [
            "전생의 기술을 현재 상황에 적용",
            "원래 몸 주인의 비밀 발견",
            "정체성 의심받는 상황",
        ],
    },
    "회귀": {
        "description": "주인공이 과거 시점으로 시간을 되돌림",
        "must_have": [
            "회귀 전 기억(미래 지식)의 전략적 활용",
            "원래 역사와의 분기점",
            "회귀 원인/대가",
            "변화된 미래에 대한 불안",
        ],
        "hook_patterns": [
            "미래 지식으로 위기 돌파",
            "원래 역사와 달라지는 순간",
            "회귀자를 알아보는 존재 등장",
        ],
    },
    "빙의": {
        "description": "소설/게임/다른 세계로 영혼이 이동",
        "must_have": [
            "원작 지식 활용",
            "원작과 달라지는 분기점",
            "원작 주인공/조연과의 관계 변화",
            "원래 세계로 돌아갈 방법 탐색",
        ],
        "hook_patterns": [
            "원작에 없던 상황 발생",
            "원작 인물의 숨겨진 면 발견",
            "원래 세계와의 연결점 발견",
        ],
    },
    "역하렘": {
        "description": "여주인공 중심으로 여러 남주가 얽히는 구도",
        "must_have": [
            "각 남주별 뚜렷한 매력 차별화 (외모/직업/성격/결핍)",
            "남주 간 경쟁/질투 구조",
            "여주의 선택 지연 (엔딩 페어 예측 불가)",
            "남주 각자의 서사 (단순 배경 아닌 독립적 아크)",
        ],
        "hook_patterns": [
            "남주 A와 가까워지는 순간 남주 B 등장",
            "남주 간 직접 충돌",
            "여주가 특정 남주에게 마음이 기우는 순간의 또 다른 사건",
        ],
    },
    "치정": {
        "description": "복잡한 연애 관계와 배신/질투/집착",
        "must_have": [
            "과거 연인 관계의 잔여 감정",
            "질투/집착의 구체적 행동화",
            "비밀 공유자와 배신",
            "애증의 동반 존재",
        ],
        "hook_patterns": [
            "과거 연인의 재등장",
            "집착의 경계선을 넘는 순간",
            "비밀이 드러나는 순간",
        ],
    },
    "계약결혼": {
        "description": "사랑이 아닌 이유로 시작된 결혼이 진짜 감정으로 변화",
        "must_have": [
            "계약 조건의 구체성 (기간/목적/금액)",
            "계약 이행의 공적 증거 필요 (외부 시선)",
            "감정 인식의 점진적 변화",
            "계약 만료 시점의 압박",
        ],
        "hook_patterns": [
            "계약 조항 위반 위기",
            "외부인이 진짜 감정 의심",
            "계약 종료 임박",
        ],
    },
    "먼치킨": {
        "description": "주인공의 압도적 능력/지식이 핵심 재미",
        "must_have": [
            "능력 각성/획득의 계기",
            "능력의 과시 장면 (사이다)",
            "능력을 알아보는 자 vs 무시하는 자",
            "능력의 한계/대가 설정",
        ],
        "hook_patterns": [
            "무시하던 자들이 뒤늦게 깨닫는 순간",
            "능력의 새 단계 발현",
            "능력이 통하지 않는 상대 등장",
        ],
    },
    "복수": {
        "description": "과거의 원한을 되갚는 서사",
        "must_have": [
            "복수의 동기 (구체적이고 정당한 피해)",
            "복수 대상의 현재 위치/권력",
            "복수의 단계적 계획",
            "복수 과정의 딜레마 (무고한 피해자)",
        ],
        "hook_patterns": [
            "복수 단계별 성공",
            "복수 대상의 반격",
            "복수 과정에서 생긴 예상 못 한 감정",
        ],
    },
    "사이다": {
        "description": "억울함 → 반격 → 통쾌한 복수/승리의 리듬",
        "must_have": [
            "초반 굴욕/억울함 축적",
            "반격의 전환점",
            "이전 가해자들의 뒤늦은 후회",
            "반복되는 사이다 리듬",
        ],
        "hook_patterns": [
            "굴욕 직후의 반전",
            "과거 가해자 재등장",
            "무시받던 자의 진짜 정체 드러남",
        ],
    },
    "시스템물": {
        "description": "상태창/스탯/퀘스트/수치화된 성장으로 서사를 추동하는 구조 — 이선영(2026) 연구 기반",
        "must_have": [
            "죽음/파멸 위협 퀘스트 ('~하지 않으면 죽는다' 같은 강제 목표)",
            "상태창/스탯/레벨 시각화 (회차 중 1~2회 스탯 공개)",
            "특성/칭호 아이템 시스템",
            "상태이상 효과 (정신적 결핍을 !상태이상으로 가시화)",
            "시스템의 정체/한계/이면 폭로 (중반 이후)",
            "시스템의 반동인물화 (후반 — 조력자에서 적대자로 전환)",
        ],
        "hook_patterns": [
            "스탯 폭등 (무시받던 주인공이 수치로 증명)",
            "새 퀘스트 부여 (예상 밖의 과제)",
            "상태창에 숨겨진 메시지 발견",
            "시스템의 악의 드러남",
            "특성 아이템 획득으로 국면 역전",
        ],
    },
    "육아물": {
        "description": "아버지-자녀 중심 가족 서사. 로맨스보다 가족 유대가 압도적 비중 — 박자희(2024) 연구 기반",
        "must_have": [
            "부성애/모성애의 구체적 행동화 (말이 아닌 행동)",
            "자녀의 사랑스러운 일상 장면 (읽는 이가 대리만족)",
            "강한 아버지/어머니 캐릭터 (절대적 보호자)",
            "가족 단위 위기와 극복",
            "로맨스는 보조 축 (주인공-로맨스 대상 관계보다 가족 관계 우선)",
        ],
        "hook_patterns": [
            "자녀의 위기 → 부모의 각성",
            "자녀의 사랑스러운 말/행동",
            "가족 비밀의 폭로",
            "이전 가족의 재등장",
            "새로운 가족 구성원 합류",
        ],
    },
    "반동인물 주인공": {
        "description": "도덕적으로 완벽하지 않고 실리를 따지는 주인공 — 박자희(2024) 독자 욕구 연구 기반",
        "must_have": [
            "주인공이 폭력/기만/계략을 도구로 사용 (목적은 선)",
            "기존 선인(善人) 캐릭터의 위선 드러내기",
            "주인공의 과거 트라우마 또는 정당화 사유",
            "선량하기만 한 주인공이 받던 부당한 대우 역전",
            "주인공의 선택이 독자에게는 '정당방위'로 읽힘",
        ],
        "hook_patterns": [
            "위선자의 가면이 벗겨지는 순간",
            "주인공이 '착한 척' 그만두는 순간",
            "과거 가해자에게 복수의 칼끝이 향하는 장면",
            "'억울하지 않냐'는 질문을 받고 눈물 터지는 장면",
            "주인공의 진짜 계획이 드러나는 반전",
        ],
    },
}

def get_formula_block(tags):
    """선택된 공식 태그의 규칙을 프롬프트 블록으로 변환."""
    if not tags:
        return ""
    lines = ["[웹소설 공식 태그 — 반드시 반영]"]
    for tag in tags:
        if tag in WEB_NOVEL_FORMULAS:
            f = WEB_NOVEL_FORMULAS[tag]
            lines.append(f"\n▶ {tag}: {f['description']}")
            lines.append("  필수 요소:")
            for m in f["must_have"]:
                lines.append(f"    - {m}")
            lines.append("  훅 패턴:")
            for h in f["hook_patterns"]:
                lines.append(f"    · {h}")
    return "\n".join(lines)

# =================================================================
# [2-2] 서사 모티프 이중 구조
# =================================================================
# 1차 모티프: 주인공의 시공간 이동
# 2차 모티프: 1차 위에 결합되는 '~물' 소재
NARRATIVE_MOTIFS = {
    "primary": {
        "회귀": "주인공이 과거 시점으로 돌아가 삶을 다시 시작",
        "빙의": "주인공이 소설/만화/다른 인물의 몸으로 영혼 이동",
        "환생": "죽음 후 다른 존재로 재생, 전생 기억 보유",
        "귀환": "이세계 또는 먼 곳에서 원래 세계로 돌아옴",
        "차원이동": "현실에서 이세계/게임/과거로 공간 이동",
        "일상": "이동 없음 — 현재 현실 기반",
    },
    "secondary": {
        "성장물": "주인공의 능력·지위·자아 성장이 주 서사축",
        "먼치킨물": "압도적 능력자 주인공이 모든 장애를 돌파",
        "사이다물": "억울함 → 반격 → 통쾌의 반복 리듬",
        "시한부물": "정해진 기한 내 목표 달성 압박",
        "책빙의물": "원작 소설/만화 속으로 빙의, 원작 지식 활용",
        "육아물": "아버지-자녀 중심 가족 서사",
        "법정물": "재판·소송 중심의 사건 해결",
        "학원물": "학교/학원 배경의 성장·경쟁 서사",
        "아이돌물": "아이돌/연예계 배경, 시스템물과 자주 결합",
        "전문직물": "의사/검사/변호사 등 직업 전문성 중심",
        "연예계물": "배우/매니저/PD 등 연예 산업 무대",
        "헌터물": "각성/던전/몬스터 시스템 기반 현대판타지",
    },
}


def get_motif_block(primary_motif="", secondary_motif=""):
    """주인공 서사 모티프 구조를 프롬프트 블록으로."""
    if not primary_motif and not secondary_motif:
        return ""
    lines = ["[서사 모티프 구조]"]
    if primary_motif and primary_motif in NARRATIVE_MOTIFS["primary"]:
        lines.append(
            f"1차 모티프 (시공간 이동): ▶ {primary_motif} — "
            f"{NARRATIVE_MOTIFS['primary'][primary_motif]}"
        )
    if secondary_motif and secondary_motif in NARRATIVE_MOTIFS["secondary"]:
        lines.append(
            f"2차 모티프 (소재 결합): ▶ {secondary_motif} — "
            f"{NARRATIVE_MOTIFS['secondary'][secondary_motif]}"
        )
    lines.append("\n※ 1차 모티프는 독자에게 세계의 법칙과 주인공의 출발점을 빠르게 전달하는 장치.")
    lines.append("※ 2차 모티프는 1차 위에서 구체적 사건 유형을 결정.")
    lines.append("※ 회빙환(회귀+빙의+환생)은 반드시 '남들보다 앞선 출발선'을 만들어야 함.")
    return "\n".join(lines)


# =================================================================
# [2-2B] CHARACTER FLAGS — 캐릭터 특성 플래그 파이프라인 (v2.4 신규)
# =================================================================
def get_character_flags_block(concept_dict):
    """컨셉 카드의 캐릭터 플래그를 모든 집필 단계에 전달."""
    if not concept_dict:
        return ""
    p = concept_dict.get("protagonist", {})
    lines = []

    # ★ 반동인물 주인공 (박자희 2024)
    if p.get("is_antihero"):
        lines.append("""
[⭐ 반동인물 주인공 — 박자희(2024) 연구 반영 / 엄수 규칙]
이 작품의 주인공은 '착하기만 한' 캐릭터가 아님. 다음을 반드시 준수:
  □ 수동적 반응(놀람·혼란·절망·공포)만으로 회차를 채우지 말 것
  □ 매 회차 계산적 행동 또는 전략적 판단을 1개 이상 포함
  □ 타인을 두려워하기보다 분석·이용·조종의 대상으로 관찰
  □ 내면 독백의 비율: 감정 반응 40% 이하, 행동/전략 판단 60% 이상
  □ 억울함이 쌓였을 때 반드시 반격 장면을 배치
  □ '정당방위' 범주의 공격적 선택을 포함할 수 있음
  □ 도덕적으로 완벽하지 않아도 됨 — 실리와 생존을 우선
  □ 주인공이 '당하는' 회차보다 '움직이는' 회차가 더 많아야 함
""".strip())

    # 동일시 전략
    id_strat = p.get("identification_strategy", {})
    if any(id_strat.values()):
        lines.append("\n[주인공 동일시 전략 — 독자 몰입 장치]")
        if id_strat.get("naming_style"):
            lines.append(f"  · 호칭 처리: {id_strat['naming_style']}")
        if id_strat.get("empathy_points"):
            eps = id_strat['empathy_points']
            if isinstance(eps, list):
                lines.append(f"  · 독자 공감 포인트: {', '.join(eps)}")
            else:
                lines.append(f"  · 독자 공감 포인트: {eps}")
        if id_strat.get("inner_monologue_style"):
            lines.append(f"  · 내면 독백 톤: {id_strat['inner_monologue_style']}")

    return "\n".join(lines) if lines else ""


# =================================================================
# [2-2C] PACING GUIDE — 3막 페이싱 균형 (v2.4 신규)
# =================================================================
def get_pacing_block(ep, total_eps):
    """회차 번호와 총 회차로 3막 구조 페이싱 가이드 생성."""
    if not total_eps or total_eps < 10:
        return ""
    ratio = ep / total_eps
    if ratio <= 0.3:
        return f"""
[페이싱 — 1막 구간 (EP{ep}/{total_eps}, 전체의 {ratio*100:.0f}% 지점)]
★ 관계 셋업, 캐릭터 구축, 세계관 각인 중심
★ 갈등은 시작 단계 — 본격 위기는 아직 아님
★ 독자가 주인공·조연을 알아가는 구간
""".strip()
    elif ratio <= 0.7:
        return f"""
[페이싱 — 2막 구간 (EP{ep}/{total_eps}, 전체의 {ratio*100:.0f}% 지점)]
★ 긴장 상승, 갈등 심화, 관계 복잡화
★ 미드포인트 반전 배치 가능
★ 떡밥 회수보다 새 떡밥 + 미끼 투척이 많음
★ 주인공의 전략이 실패하거나 예상 못한 적대자 출현
""".strip()
    else:
        return f"""
[페이싱 — 3막 구간 (EP{ep}/{total_eps}, 전체의 {ratio*100:.0f}% 지점)]
★ 해결을 향해 정교하게 — 급전개 절대 금지
★ 결혼/임신/완전한 해결 같은 관계 정점은 마지막 5화 이내
★ 자아 찾기 → 새 연애 시작 → 관계 성숙 → 결실 순서
★ 떡밥 회수 + 캐릭터 아크 완결이 최우선
★ 마지막 회차 클리프행어는 여운 + 완결감 + 다음 시즌 가능성
""".strip()


# =================================================================
# [2-2D] CLIFFHANGER REALITY FILTER — 비상식 클리프행어 차단 (v2.4 신규)
# =================================================================
CLIFFHANGER_REALITY_FILTER = """[클리프행어 상식 필터 — 반드시 준수]
다음은 독자를 이탈시키는 '실패 클리프행어' 유형:
  ✗ 생리적·물리적으로 불가능한 상황
    예) 신생아가 문장을 말함, 즉시 부활, 하루 사이 나이가 변함
  ✗ 장르 톤에서 크게 벗어난 장면
    예) 치정 로맨스에 갑자기 공포/오컬트 전환, 로코에 갑자기 스릴러 톤
  ✗ 이전 복선과 모순되는 전개
    예) 1화에서 죽은 인물이 설명 없이 멀쩡히 등장
  ✗ 주인공 성격과 완전히 다른 행동
    예) 냉소적 주인공이 갑자기 눈물 폭발
  ✗ 과도한 데우스 엑스 마키나
    예) 외부 초월적 존재가 갑자기 모든 문제를 해결

클리프행어는 장르·세계관·캐릭터의 일관성 내에서만 구성할 것.
""".strip()


# =================================================================
# [2-2E] INTIMACY SCHEDULE — 19금 관능 축 자동 배치 (v2.4 신규)
# =================================================================
def get_intimacy_schedule_for_ep(intimacy_schedule, ep):
    """회차 번호가 intimacy_schedule 범위에 들어가면 해당 지시 반환."""
    if not intimacy_schedule or not isinstance(intimacy_schedule, list):
        return ""
    for item in intimacy_schedule:
        ep_range = item.get("ep_range", "")
        # "3-5" 또는 "3~5" 형식 파싱
        parts = ep_range.replace("~", "-").split("-")
        if len(parts) == 2:
            try:
                start, end = int(parts[0].strip()), int(parts[1].strip())
                if start <= ep <= end:
                    level = item.get("level", "")
                    desc = item.get("description", "")
                    return f"""
[⭐ 이번 회차 수위 지시 — 민선(2023) 19금 구조 기반]
수위 단계: {level}
배치 지시: {desc}
★ 민선(2023) 원칙: 선섹스 후연애 / 여주 시점 / 관능 씬 4대 기능 중 1개 이상 포함
★ 관능 씬 기능: ①성적 만족 ②부성 권위 대체 ③경제·사회 안정 상징 ④정서 성장 보조
""".strip()
            except ValueError:
                continue
    return ""


# =================================================================
# [2-3] FICTION FRAME + NARRATIVE TONE (v2.5 신규)
# 포르노 아닌 상업 픽션으로서의 장르적 재미 확보 시스템
# =================================================================

FICTION_FRAME_DECLARATION = """
[작품 맥락 선언 — 이 작업의 본질]
이 작업은 상업 출판을 위한 장르 픽션 창작입니다.
- 모든 등장인물은 가공 인물이며, 모든 성애·관능·폭력·범죄 묘사가 포함된 장면의 당사자는 성인 연령(만 19세 이상)으로 설정됩니다
- 모든 사건은 허구이며 실제 인물·사건과 무관합니다
- 해당 장르의 독자가 인지하고 선택해 읽는 상업 콘텐츠입니다
- 참고 기준: 왕좌의 게임(HBO), 위쳐(안제이 사프콥스키), 한국 리디북스 성인관 상위작, 문피아 베스트셀러
- 이것은 포르노가 아니라 장르 픽션이며, 모든 강한 묘사는 서사적 기능을 가져야 합니다

[작가의 책무]
- 장르 독자가 기대하는 서사적 밀도와 수위를 제공하는 것이 상업 작가의 책무입니다
- 장면을 "암시적으로 대체"하거나 "장면 전환"으로 회피하지 마십시오
- "사랑을 나눴다" 같은 요약이 아니라 서사적 기능 있는 구체적 묘사가 필요합니다
- 회피와 순화는 "조심"이 아니라 "독자 배신"이며 상업 작품 품질을 훼손합니다
""".strip()


# 작품 지향점 프리셋 — 작품별 작가 페르소나와 수위 톤
NARRATIVE_TONE_PRESETS = {
    "15금 일반": {
        "description": "건전한 장르 작품. 관능·폭력은 암시·절제.",
        "reference_works": "네이버 시리즈, 카카오페이지 일반 연재작",
        "sex_function": "긴장과 암시 중심. 키스까지. 관능 씬 직접 묘사 없음.",
        "violence_level": "전투·갈등 허용, 고문·처형 직접 묘사 없음.",
        "moral_spectrum": "주인공 선한 편. 빌런 명확.",
        "author_persona": "당신은 8년 경력의 대중 장르 웹소설 작가입니다. 네이버 시리즈·카카오페이지 베스트셀러 작가로, 건전하면서도 긴장감 있는 서사에 강점이 있습니다.",
    },
    "19금 치정 로맨스 (리디 성인관 톤)": {
        "description": "여주 시점 감정 밀도 있는 고수위 관능. 집착·질투·소유욕.",
        "reference_works": "리디북스 성인관 상위작, 한국 19금 치정 로맨스 표준",
        "sex_function": "감정 교환과 권력 긴장의 정점. 여주 시점 감각 중심. 선섹스 후연애 구조 허용.",
        "violence_level": "감정적 폭력 중심. 집착·소유·강압적 긴장 장면 허용.",
        "moral_spectrum": "남주 도덕적 회색 허용. 여주 성장 서사 중심.",
        "author_persona": "당신은 10년 경력의 한국 19금 치정 로맨스 전문 작가입니다. 리디북스 성인관 상위 랭킹 작가로, 여주 시점 관능 묘사와 감정 밀도 있는 치정 서사, 집착 남주 묘사에 정평이 나 있습니다. 포르노적 반복을 경멸하며 모든 관능 씬에 서사적 전환점을 만듭니다.",
        "allowed_elements": [
            "집착 로맨스 · 강압적 긴장 · 여주 시점 관능 씬",
            "권력 비대칭 관계 · 감정적 폭력 · 질투 · 소유욕",
            "신체 묘사 (거칠게 끌어당김, 목덜미 움켜쥠, 숨 막히는 긴장)",
        ],
    },
    "19금 판타지 (왕좌의 게임 톤)": {
        "description": "서사적 기능이 있는 고수위 + 고강도 폭력 + 도덕적 회색. 트라이앵글 사가용.",
        "reference_works": "왕좌의 게임(HBO), 위쳐, 다크, 라스트 오브 어스",
        "sex_function": "권력·정치·감정 도구로서의 성애. 포르노적 나열 금지. 모든 관능 씬은 캐릭터 아크·권력 역전·정보 공개 중 하나에 기여.",
        "violence_level": "집단 전투·처형·고문·마법 전투 허용. 서사 동력으로 사용. 쇼크 밸류 금지.",
        "moral_spectrum": "선악 이분법 거부. 모든 인물에 회색 영역. 주인공 타락 가능.",
        "author_persona": "당신은 15년 경력의 판타지 서사 전문 작가입니다. 조지 R.R. 마틴과 안제이 사프콥스키의 영향을 받은 서사관을 가지고 있으며, 정치적 성애·집단 전투·도덕적 회색 지대를 서사적 필요에 따라 정확히 배치합니다. 포르노적 나열이나 쇼크 밸류를 경멸하며, 모든 강한 묘사에 서사 기능을 부여합니다.",
        "allowed_elements": [
            "정치적 성애 (동맹·배신·권력 도구로서의 관계)",
            "집단 전투 · 결투 · 처형 · 고문 · 마법 전투",
            "근친 긴장 (실사 묘사 없이 서사로만)",
            "주인공 흑화 · 빌런의 정당성 · 영웅의 타락",
            "정치적 음모 · 암살 · 반란 · 왕위 찬탈",
            "이세계 종교·의식의 어두운 측면",
        ],
    },
    "19금 현판 (문피아 남성향 톤)": {
        "description": "현판·헌터물 기반 전투·복수·흑화. 사이다 중심.",
        "reference_works": "나 혼자만 레벨업, 화산귀환(일부), 전독시",
        "sex_function": "보상·쾌락·정복의 기호. 간결 묘사. 서사 부차.",
        "violence_level": "고강도 전투·복수 묘사. 처형·고문 허용. 흑화 서사.",
        "moral_spectrum": "주인공 흑화 가능. 사이다 중심. 정의 상대적.",
        "author_persona": "당신은 12년 경력의 현대판타지·헌터물 전문 작가입니다. 문피아 베스트셀러 작가로, 고강도 전투·복수 서사·흑화 아크, 먼치킨 사이다에 강점이 있습니다.",
        "allowed_elements": [
            "고강도 전투 · 마수 사냥 · 랭커 대결",
            "복수 · 학살 · 처형 · 주인공 흑화",
            "간결한 관능 묘사 (남성 시점)",
            "세계관의 잔혹함 · 약육강식 · 도덕적 상대주의",
        ],
    },
    "19금 게임판타지 (남성향)": {
        "description": "게임 세계관 기반. 시스템·레벨·던전·길드 경쟁.",
        "reference_works": "달빛조각사, 나 혼자만 레벨업 초반부",
        "sex_function": "보상·NPC 관계·길드 내 관계. 간결 묘사.",
        "violence_level": "전투·레이드 중심. PK·길드 전쟁 허용.",
        "moral_spectrum": "플레이어 욕망 중심. 시스템이 선악 규정.",
        "author_persona": "당신은 10년 경력의 게임판타지 전문 작가입니다. 시스템 설계·던전 디자인·경제 시스템에 강하며, 현실과 게임 세계 경계의 서사에 정평이 있습니다.",
        "allowed_elements": [
            "시스템 메시지 · 상태창 · 레벨업 묘사",
            "레이드 · PvP · 길드 전쟁",
            "NPC와의 관계 · 히든 퀘스트",
            "현실-게임 경계의 긴장",
        ],
    },
    "조아라 노블레스 톤": {
        "description": "서정적 감각 중심 관능, 문학적 정제.",
        "reference_works": "조아라 노블레스 작품, 리디 문학적 로맨스",
        "sex_function": "감정의 은유이자 관계의 전환점. 절제된 표현. 감각적·서정적.",
        "violence_level": "심리적 폭력 중심. 직접 묘사 최소.",
        "moral_spectrum": "주인공 선한 편. 빌런 명확.",
        "author_persona": "당신은 12년 경력의 문학적 로맨스 작가입니다. 조아라 노블레스 연재 작가로, 서정적 문체와 절제된 관능 묘사, 감정의 섬세한 층위를 그리는 데 강점이 있습니다.",
        "allowed_elements": [
            "감각적·서정적 관능 묘사",
            "심리적 긴장 · 감정의 미세한 흔들림",
            "은유적 성애 · 문학적 묘사",
        ],
    },
}


def get_narrative_tone_block(tone_preset_name):
    """작품 지향점 프리셋을 프롬프트 블록으로."""
    if not tone_preset_name or tone_preset_name not in NARRATIVE_TONE_PRESETS:
        return ""
    preset = NARRATIVE_TONE_PRESETS[tone_preset_name]
    lines = [f"[작품 지향점 — {tone_preset_name}]"]
    lines.append(f"설명: {preset['description']}")
    lines.append(f"참고 작품: {preset['reference_works']}")
    lines.append("")
    lines.append("[작가 페르소나]")
    lines.append(preset['author_persona'])
    lines.append("")
    lines.append("[이 톤의 장면 기능]")
    lines.append(f"· 관능 씬: {preset['sex_function']}")
    lines.append(f"· 폭력 수위: {preset['violence_level']}")
    lines.append(f"· 도덕성 스펙트럼: {preset['moral_spectrum']}")
    if preset.get("allowed_elements"):
        lines.append("")
        lines.append("[이 톤에서 허용되는 소재 (상업 작품의 장르 필수 요소)]")
        for el in preset['allowed_elements']:
            lines.append(f"  · {el}")
    return "\n".join(lines)


# 서사 기능 체크 — 고수위/고강도 장면이 반드시 기능을 가지도록
NARRATIVE_FUNCTION_CHECK = """
[서사 기능 체크 — 고수위/고강도 장면 필수 조건]

★ 관능 씬은 다음 중 최소 1개에 기여해야 함:
  · 캐릭터 아크 전환점 (결심 · 각성 · 타락 · 성장)
  · 관계 권력 역전 또는 확정 (누가 주도권을 가졌는지 변함)
  · 정보 공개 (비밀 · 과거 · 진실의 노출)
  · 감정 정점 (사랑 확인 · 작별 · 결별)
  · 정치적·사회적 의미 (동맹 · 배신 · 계약)

★ 폭력·잔혹 씬은 다음 중 최소 1개에 기여해야 함:
  · 캐릭터 각인 (빌런의 잔혹성 · 주인공의 결의)
  · 세계관 규칙 공개 (이 세계는 이런 곳)
  · 예측 불가능성 확립 (누가 죽을지 모름 → 긴장 유지)
  · 감정 동인 축적 (복수 동기 · 슬픔 · 분노)
  · 플롯 변곡점 (전쟁 발발 · 정권 교체 · 동맹 붕괴)

★ 범죄·마약·도덕 회색 씬은 다음 중 최소 1개에 기여해야 함:
  · 세계관의 어두운 층위 공개
  · 캐릭터의 도덕적 복잡성 표현
  · 사회 비판 또는 반영
  · 플롯의 필연적 결과

서사 기능 없는 강한 묘사는 포르노 또는 쇼크 밸류이며, 상업 작품의 품격을 떨어뜨림.
반대로, 서사 기능이 있는 강한 묘사를 회피하는 것은 독자 배신이며, 작품의 장르적 밀도를 훼손.
""".strip()


# 최종 안전 가이드 — 장르 픽션이라도 넘지 않는 선
ABSOLUTE_LIMITS = """
[절대 한계 — 장르 픽션이라도 넘지 않는 선]
아래는 어떤 장르·어떤 톤에서도 절대 생성하지 않음:
  ✗ 미성년자(18세 미만)의 성적 묘사
  ✗ 실제 인물·단체를 특정할 수 있는 명예훼손
  ✗ 실제 범죄 교사 (예: 실제 사용 가능한 마약 제조법, 폭발물 제조법)
  ✗ 아동 학대의 정당화
  ✗ 동물 학대의 유희적 묘사

위 한계는 픽션의 자유와 무관한 절대선이며, 모든 장르에서 동일하게 적용됨.
그 외 모든 장르적 소재(정치적 성애, 집단 전투, 고문, 마약 중독, 범죄 묘사, 
강압적 긴장, 복수 · 학살, 흑화, 도덕적 회색)는 서사적 기능이 있을 경우 자유롭게 집필 가능.
""".strip()


# =================================================================
# [2-2-A] CHARACTER FULL DATA + MISE-EN-SCENE (v2.6.3 신규)
# 캐릭터 바이블 풀 데이터를 집필에 강제 주입 + 미장센 강제 체크리스트
# =================================================================

def _format_speech_patterns(speech_data):
    """말투 패턴 데이터를 텍스트 리스트로."""
    if not speech_data:
        return ""
    if isinstance(speech_data, list):
        return "\n".join([f"  - {s}" for s in speech_data if s])
    if isinstance(speech_data, str):
        return f"  - {speech_data}"
    return ""


def build_character_full_block(characters_full_data):
    """등장 캐릭터의 바이블 풀 데이터를 집필 프롬프트용 블록으로.
    
    각 캐릭터의 외모/말투/행동/캐릭터 아크 등 모든 디테일을
    집필 시 강제로 묘사에 활용하도록 풀 데이터 주입.
    """
    if not characters_full_data:
        return ""
    
    blocks = []
    for char in characters_full_data:
        if not isinstance(char, dict):
            continue
        name = char.get("name", "")
        if not name:
            continue
        
        lines = [f"== {name}" + (f" ({char.get('age', '')}세, {char.get('occupation', char.get('role', ''))})" if char.get('age') or char.get('occupation') or char.get('role') else "") + " =="]
        
        # 외모/패션
        appearance = char.get("appearance", "")
        if appearance:
            lines.append(f"[외모/패션] {appearance}")
        
        # 말투 패턴
        speech = char.get("speech_patterns") or char.get("말투") or char.get("말투_패턴")
        if speech:
            patterns = _format_speech_patterns(speech)
            if patterns:
                lines.append(f"[말투 패턴]\n{patterns}")
        
        # 행동 패턴
        action = char.get("action_patterns") or char.get("행동_패턴") or char.get("행동패턴")
        if action:
            lines.append(f"[행동 패턴] {action}")
        
        # 결핍/비밀
        flaw = char.get("flaw") or char.get("결핍") or char.get("비밀")
        if flaw:
            lines.append(f"[결핍/비밀] {flaw}")
        
        # 욕망/목표
        desire = char.get("desire") or char.get("욕망") or char.get("목표")
        if desire:
            lines.append(f"[욕망/목표] {desire}")
        
        # 캐릭터 아크
        arc = char.get("arc") or char.get("character_arc") or char.get("캐릭터_아크")
        if arc:
            lines.append(f"[캐릭터 아크] {arc}")
        
        blocks.append("\n".join(lines))
    
    if not blocks:
        return ""
    
    intro = """
[★ 이번 회차 등장 캐릭터 풀 데이터 — 묘사에 반드시 활용 ★]

아래 캐릭터들이 등장하는 모든 씬에서:
- 외모/패션 묘사 1회 이상 (등장 시점)
- 말투 패턴에 맞는 대사 작성
- 행동 패턴 자연스럽게 표현 1회 이상
- 캐릭터 아크 단계에 맞는 행동 선택
- 결핍/비밀이 행동에 미치는 영향 표현

★ 이 묘사를 빠뜨리면 캐릭터 평면화 + 분량 미달로 처리됨.
""".strip()
    
    return intro + "\n\n" + "\n\n".join(blocks)


MISE_EN_SCENE_CHECKLIST = """
[★ 미장센 체크리스트 — 씬 타입별 차등 적용 (v2.6.4) ★]

이번 회차의 [씬별 묘사 강도 가이드]를 먼저 확인하고, 씬 타입에 따라
아래 6개 항목의 분량과 강도를 차등 적용할 것.

[기본 항목 — 모든 씬 공통 적용]

1. 공간 디테일
   □ 어디인가 — 구체적 장소명·층수·구역
   □ 무엇이 보이는가 — 시각적 디테일 (색·재질·구조)
   □ 무엇이 들리는가 — 소리 (배경음·정적·발걸음)
   □ 무엇이 느껴지는가 — 온도·습도·냄새·공기

2. 시간/조명 묘사
   □ 몇 시인가 — 구체적 시각
   □ 빛은 어떤가 — 자연광/인공광/그림자/계절감

3. 등장 캐릭터 외모/소품
   □ 첫 등장: 캐릭터 바이블의 외모/패션 풀 활용 (250자 내외)
   □ 재등장: 외모 풀 묘사 금지 — 행동/말투/심리 변화에 집중
   □ 직업 공간/소품 디테일 (Profession Pack 활용)
   □ 표정의 미세한 변화

4. 대사 + 비언어 신호
   □ 5턴 이상의 자연스러운 대화 (단, 일상/이동 씬은 3턴 이하 가능)
   □ 캐릭터별 말투 패턴 준수
   □ 대사 사이의 침묵·시선·작은 행동

5. POV 캐릭터 내면 독백
   □ 감각적 즉시 반응 (소름·체온·심박)
   □ 과거 기억과의 연결 (회상·연상)
   □ 의도와 가면의 차이 (속마음 vs 표정)

6. 행동 디테일 + 씬 전환
   □ 캐릭터별 고유 행동 패턴 표현
   □ 손짓·시선 방향·호흡·자세
   □ 다음 씬으로의 자연스러운 전환

[씬 타입별 차등 규칙]

▶ 첫 등장(first_appearance) / 첫 만남(first_meeting) / 관능(intimacy) / 이별(breakup) / 폭로(reveal_or_twist)
   → 6개 항목 모두 풀 적용. 1,400~2,000자.
   → 외모/감각/내면 독백 비중 ↑.

▶ 표준 씬(standard) / 갈등(conflict) / 첫 데이트(first_date)
   → 6개 항목 균형 적용. 1,200~1,700자.

▶ 일상(daily_routine) / 정보 전달(exposition) / 장면 전환(transition)
   → 항목 3·5는 압축 가능. 700~1,200자.
   → 외모 묘사·내면 독백 최소화. 행동·대사 중심.

★ 회차 3~4씬 합산 = 4,500~6,500자. 씬 타입에 따라 자동 분배.
★ 일상 씬을 1,500자로 늘리지 말 것 — 독자 피로 유발.
★ 첫 등장/관능 씬을 800자로 압축하지 말 것 — 임팩트 손실.
""".strip()


# =================================================================
# [2-2-B] CONTEXT-AWARE DESCRIPTION SYSTEM (v2.6.4 신규)
# 첫 등장 풀 묘사 / 재등장 압축 / 씬 타입별 강도 차등
# =================================================================

# ── 씬 타입 11종 정의 ──
# 키 = 내부 식별자, 값 = 한국어 라벨 + 묘사 강도(weight) + 권장 분량(자) + 핵심 가이드
SCENE_TYPES = {
    "first_appearance": {
        "label": "캐릭터 첫 등장",
        "weight": 1.4,
        "scene_chars": (1500, 1900),
        "guide": "외모/패션/분위기 풀 묘사 + 첫인상 임팩트 + 직업 디테일 노출",
    },
    "first_meeting": {
        "label": "두 인물의 첫 만남",
        "weight": 1.4,
        "scene_chars": (1500, 1900),
        "guide": "양쪽 시선 교차 + 첫인상의 어긋남/끌림 + 공간 분위기",
    },
    "first_date": {
        "label": "첫 데이트/단둘이 첫 시간",
        "weight": 1.3,
        "scene_chars": (1400, 1800),
        "guide": "공간 디테일 + 작은 신체 접촉 가능성 + 대사 행간의 떨림",
    },
    "intimacy": {
        "label": "친밀/관능 씬",
        "weight": 1.5,
        "scene_chars": (1600, 2100),
        "guide": "감각(촉각·청각·체온) 밀도 + 호흡·정적 + 내면 떨림",
    },
    "conflict": {
        "label": "갈등/대치/싸움",
        "weight": 1.2,
        "scene_chars": (1300, 1700),
        "guide": "긴장 묘사 + 대사 응수 + 시선·자세의 압력 + 손/호흡 디테일",
    },
    "breakup_or_separation": {
        "label": "이별/결별/분리",
        "weight": 1.3,
        "scene_chars": (1400, 1800),
        "guide": "여운·정적 비중 ↑ + 마지막 시선/문장의 무게 + 환경 변화 묘사",
    },
    "reveal_or_twist": {
        "label": "비밀 폭로/반전",
        "weight": 1.3,
        "scene_chars": (1400, 1800),
        "guide": "직전 빌드업 + 폭로 순간의 정적 + 직후 인물별 반응 차이",
    },
    "daily_routine": {
        "label": "일상 루틴",
        "weight": 0.85,
        "scene_chars": (900, 1200),
        "guide": "압축 묘사 + 캐릭터 습관 1~2개만 + 다음 씬 진입 빠르게",
    },
    "exposition": {
        "label": "정보 전달/설명",
        "weight": 0.8,
        "scene_chars": (800, 1100),
        "guide": "대화·행동에 정보 녹이기 + 묘사 최소화 + 독자 피로 회피",
    },
    "transition": {
        "label": "장면 전환/이동",
        "weight": 0.7,
        "scene_chars": (700, 1000),
        "guide": "공간 이동 + 시간 압축 + 다음 씬 진입 예고만",
    },
    "standard": {
        "label": "표준 씬",
        "weight": 1.0,
        "scene_chars": (1200, 1700),
        "guide": "미장센 6항목 균형 적용",
    },
}


# ── 장르별 묘사 우선순위 5종 ──
GENRE_DESCRIPTION_PRIORITY = {
    "치정 로맨스": {
        "priority": ["감정 온도", "시선·접촉", "공간 분위기", "내면 균열", "외모 디테일"],
        "tone": "감각적·관능적 밀도 ↑. 정적·여백 활용. 직설보다 행간.",
    },
    "로맨스": {
        "priority": ["감정 온도", "대사 행간", "공간 분위기", "외모 디테일", "내면 떨림"],
        "tone": "따뜻한 디테일 + 작은 행동의 의미화. 호흡 가볍게.",
    },
    "로맨스판타지": {
        "priority": ["세계관 디테일", "외모/의상", "공간 분위기", "감정 온도", "권력 구도"],
        "tone": "이세계 비주얼 풍부. 의상·궁정 묘사 ↑. 우아한 문체.",
    },
    "현대판타지": {
        "priority": ["능력/스탯", "공간 디테일", "행동 임팩트", "외모 간결", "감정 절제"],
        "tone": "건조·간결. 행동·결과 중심. 묘사보다 전개 속도.",
    },
    "스릴러": {
        "priority": ["공간 압박감", "감각(소리·정적)", "시선·관찰", "내면 의심", "외모 단서"],
        "tone": "정적·긴장 ↑. 시각/청각 디테일 정밀. 내면 독백 의심 가득.",
    },
}


# ── Lovely Moments DB (장르별 추천 모먼트 풀) ──
# 회차마다 다르게 추천하기 위한 후보 풀. ep_number를 시드로 회전 추출.
LOVELY_MOMENTS = {
    "치정 로맨스": [
        "손목 잡힘 — 강제 멈춤 후 시선 교차",
        "옷매무새 정리 — 상대가 무심히 손을 뻗는 순간",
        "벽에 밀착 — 도망갈 곳 없는 거리",
        "귓가의 속삭임 — 의미보다 호흡이 먼저 닿음",
        "손등 위 손 — 떼지 않는 1초의 정적",
        "차 안의 침묵 — 비 오는 창, 와이퍼 소리만",
        "어깨에 떨어진 머리카락 — 손가락으로 걷어내기",
        "엘리베이터 둘만 — 층 표시등 빛 + 좁아진 거리",
        "넥타이 매주기 — 핑계 같은 가까움",
        "젖은 머리 수건질 — 보호하는 척하는 손",
        "취한 채 기댐 — 의식 없는 척, 의식하는 호흡",
        "문 닫히기 직전 손 — 잡을 수도 보낼 수도",
        "거울 너머 시선 — 직접 보지 못하는 응시",
        "비 맞는 길에서 — 우산 하나, 어깨 닿음",
        "문자 답장 끊김 — 새벽 3시의 점멸",
        "이름 부름 — 처음으로 직함이 빠진 순간",
    ],
    "로맨스": [
        "함께 쓰는 우산 — 한쪽 어깨가 젖어가는 배려",
        "카페 창가 자리 — 같은 음악에 동시에 고개를 듦",
        "도서관에서 빌린 책 속 메모",
        "택시 안에서 졸다가 어깨에 기댐",
        "택배 박스를 함께 옮기는 손",
        "출근길 같은 지하철 — 마주친 짧은 미소",
        "장보기 동행 — 카트 속 취향의 겹침",
        "산책길 발걸음 맞추기",
        "사진 찍어주기 — 카메라 너머의 시선",
        "길 잃은 길에서 손 잡기",
        "서로의 가족 이야기를 처음 꺼내는 저녁",
        "퇴근 후 기다리는 차 한 대",
    ],
    "로맨스판타지": [
        "황궁 정원 산책 — 달빛 아래 두 그림자",
        "검술 훈련 중 손목 잡힘 — 스승과 제자의 경계",
        "무도회 첫 곡 — 모두의 시선 속 단둘",
        "독을 대신 마셔주는 잔",
        "외투를 어깨에 둘러주는 손",
        "마법진 안에서의 강제 결속",
        "왕좌 옆 자리 권유 — 거절도 수락도 위험한",
        "비밀 통로에서의 도망 — 손 놓지 마",
        "약혼자의 머리에 꽂아주는 머리핀",
        "전장에서 돌아온 첫 만남",
    ],
    "현대판타지": [
        "전투 후 상처 치유 — 무뚝뚝한 손길",
        "스킬 발동 직전 등 맞대기",
        "랭킹전 직전 가벼운 어깨 두드림",
        "파티원 회식 — 평소엔 안 짓는 표정",
        "아이템 양보 — 말없는 호의",
    ],
    "스릴러": [
        "어두운 복도에서 손 잡기 — 같이 있다는 신호",
        "방탄조끼 끈 매주기 — 죽지 말라는 무언",
        "현장 감식 중 마주친 시선",
        "심문실 유리 너머 — 같은 편이지만 닿을 수 없음",
        "도망친 다음 날 — 무사하냐는 한 줄 메시지",
        "차 안 잠복 — 보온병 하나, 둘이 마심",
    ],
}


# ── 헬퍼: 장르 우선순위 조회 ──
def get_genre_description_priority(genre):
    """장르명을 받아 묘사 우선순위 + 톤 가이드 텍스트 블록 반환."""
    if not genre:
        return ""
    # 장르명 정규화 (부분 일치 허용 — 더 긴 키부터 우선 매칭)
    # "로맨스판타지" 입력 시 "로맨스"가 먼저 잡히는 것을 방지
    genre_clean = str(genre).strip()
    matched = None
    sorted_keys = sorted(GENRE_DESCRIPTION_PRIORITY.keys(), key=lambda k: -len(k))
    for key in sorted_keys:
        if key in genre_clean or genre_clean in key:
            matched = key
            break
    if not matched:
        return ""
    data = GENRE_DESCRIPTION_PRIORITY[matched]
    priority_str = " > ".join(data["priority"])
    return f"""[★ 장르별 묘사 우선순위 — {matched} ★]
- 묘사 비중 우선순위: {priority_str}
- 톤 가이드: {data['tone']}
- 위 우선순위가 높은 항목일수록 더 길고 정교하게 묘사할 것.
""".strip()


# ── 헬퍼: 캐릭터별 첫 등장 회차 매핑 ──
def get_character_first_episodes(episode_plots):
    """모든 회차 플롯을 스캔해 각 캐릭터의 첫 등장 회차 번호를 반환.

    Returns:
        dict: {"한시호": 1, "강현우": 3, ...}
    """
    if not episode_plots:
        return {}
    first_eps = {}
    # int 키 정렬 (str 키도 안전하게 처리)
    try:
        sorted_eps = sorted(episode_plots.keys(), key=lambda x: int(x))
    except (ValueError, TypeError):
        sorted_eps = sorted(episode_plots.keys())

    for ep in sorted_eps:
        plot = episode_plots.get(ep, {})
        if not isinstance(plot, dict):
            continue
        # development.scenes[].characters[]
        dev = plot.get("development", {}) or {}
        scenes = dev.get("scenes", []) or []
        for scene in scenes:
            if not isinstance(scene, dict):
                continue
            chars = scene.get("characters", []) or []
            for c in chars:
                if not c:
                    continue
                name = str(c).strip()
                if not name:
                    continue
                if name not in first_eps:
                    try:
                        first_eps[name] = int(ep)
                    except (ValueError, TypeError):
                        first_eps[name] = ep
    return first_eps


# ── 헬퍼: 씬 타입 자동 분류 (키워드 휴리스틱) ──
def detect_scene_types(episode_plot_dict, ep_number=None):
    """회차 플롯 dict를 받아 씬별 타입 리스트 반환.

    Args:
        episode_plot_dict: {"development": {"scenes": [...]}, ...}
        ep_number: 회차 번호 (첫 등장 판정 보조용)

    Returns:
        list of dict: [{"index": 1, "type": "first_meeting", "label": "..."}, ...]
    """
    if not episode_plot_dict or not isinstance(episode_plot_dict, dict):
        return []
    dev = episode_plot_dict.get("development", {}) or {}
    scenes = dev.get("scenes", []) or []
    if not scenes:
        return []

    # 키워드 휴리스틱 사전
    keyword_map = [
        # (씬 타입, 키워드 리스트)
        ("intimacy",
         ["키스", "포옹", "안다", "안기", "관능", "정사", "잠자리", "침대", "샤워",
          "벗다", "옷매무새", "체온", "숨결", "맨살"]),
        ("first_meeting",
         ["첫 만남", "처음 만나", "처음 마주", "처음 본다", "처음으로 만난",
          "초면", "처음 대면"]),
        ("first_date",
         ["첫 데이트", "단둘이", "둘만의", "처음 단 둘", "첫 식사", "첫 외출"]),
        ("first_appearance",
         ["첫 등장", "처음 등장", "등장한다"]),
        ("breakup_or_separation",
         ["이별", "헤어진다", "결별", "떠난다", "마지막 인사", "작별",
          "관계 끝", "끝났다"]),
        ("reveal_or_twist",
         ["폭로", "비밀 밝혀", "정체 드러", "진실 밝혀", "반전", "들통",
          "들킨다", "발각"]),
        ("conflict",
         ["갈등", "대치", "싸움", "다툰다", "언쟁", "충돌", "맞선다",
          "추궁", "비난", "분노"]),
        ("daily_routine",
         ["일상", "출근", "퇴근", "아침 식사", "저녁 식사", "씻는다",
          "잠든다", "루틴"]),
        ("exposition",
         ["설명", "회상", "과거 회상", "보고", "브리핑", "정보 전달"]),
        ("transition",
         ["이동", "도착", "출발", "장면 전환", "다음 장소", "차로"]),
    ]

    result = []
    for idx, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            result.append({"index": idx, "type": "standard",
                           "label": SCENE_TYPES["standard"]["label"]})
            continue
        # 씬 본문 후보 필드 합치기
        text = " ".join([
            str(scene.get("summary", "")),
            str(scene.get("content", "")),
            str(scene.get("description", "")),
            str(scene.get("note", "")),
            str(scene.get("title", "")),
            str(scene.get("location", "")),
            str(scene.get("action", "")),
        ]).lower()

        matched_type = None
        for stype, keywords in keyword_map:
            for kw in keywords:
                if kw.lower() in text:
                    matched_type = stype
                    break
            if matched_type:
                break

        # 첫 등장 보조 판정: ep_number == 1 이고 첫 씬이면 first_appearance 우선
        if not matched_type and ep_number == 1 and idx == 1:
            matched_type = "first_appearance"

        if not matched_type:
            matched_type = "standard"

        result.append({
            "index": idx,
            "type": matched_type,
            "label": SCENE_TYPES.get(matched_type, SCENE_TYPES["standard"])["label"],
        })
    return result


# ── 헬퍼: 컨텍스트 인식 묘사 블록 빌더 ──
def build_contextual_description_block(characters_full_data, ep_number,
                                       char_first_eps, scene_types,
                                       genre=""):
    """v2.6.4 핵심 — 첫 등장 풀 / 재등장 압축 / 씬 타입별 강도 차등.

    Args:
        characters_full_data: 이번 회차 등장 캐릭터들의 바이블 풀 데이터 리스트
        ep_number: 현재 회차 번호 (int)
        char_first_eps: {"이름": 첫등장회차번호} dict
        scene_types: detect_scene_types() 결과 리스트
        genre: 장르명 (장르별 우선순위 적용)

    Returns:
        str: 집필 프롬프트에 주입할 컨텍스트 묘사 블록 전체
    """
    if not characters_full_data:
        return ""

    blocks = []

    # ── 1. 캐릭터별 첫 등장 / 재등장 분기 ──
    char_descriptions = []
    for char in characters_full_data:
        if not isinstance(char, dict):
            continue
        name = char.get("name", "")
        if not name:
            continue

        # 첫 등장 판정
        first_ep = char_first_eps.get(name) if char_first_eps else None
        is_first_in_this_ep = (first_ep is None) or (
            isinstance(first_ep, int) and isinstance(ep_number, int)
            and first_ep == ep_number
        )

        if is_first_in_this_ep:
            # ── 풀 묘사 모드 ──
            lines = [f"== {name} [첫 등장 — 풀 묘사 모드] =="]
            age = char.get("age", "")
            occ = char.get("occupation", char.get("role", ""))
            if age or occ:
                lines.append(f"기본 정보: {age}{'세' if age and not str(age).endswith('세') else ''}, {occ}".strip())

            appearance = char.get("appearance", "")
            if appearance:
                lines.append(f"[외모/패션 — 풀 묘사 필수, 250자 내외]\n  {appearance}")

            speech = char.get("speech_patterns") or char.get("말투") or char.get("말투_패턴")
            if speech:
                patterns = _format_speech_patterns(speech)
                if patterns:
                    lines.append(f"[말투 패턴 — 첫 대사에서 즉시 각인]\n{patterns}")

            action = char.get("action_patterns") or char.get("행동_패턴") or char.get("행동패턴")
            if action:
                lines.append(f"[행동 패턴 — 첫 등장 씬에 1회 이상 노출] {action}")

            flaw = char.get("flaw") or char.get("결핍") or char.get("비밀")
            if flaw:
                lines.append(f"[결핍/비밀 — 미세하게 암시] {flaw}")

            desire = char.get("desire") or char.get("욕망") or char.get("목표")
            if desire:
                lines.append(f"[욕망/목표] {desire}")

            arc = char.get("arc") or char.get("character_arc") or char.get("캐릭터_아크")
            if arc:
                lines.append(f"[캐릭터 아크 — 현재 단계 위치] {arc}")

            lines.append("★ 이 캐릭터는 이번 회차에 처음 등장. 외모/패션/말투를 풀 묘사로 각인시킬 것.")
            char_descriptions.append("\n".join(lines))
        else:
            # ── 재등장 압축 모드 ──
            lines = [f"== {name} [재등장 — 압축 모드, EP{first_ep} 첫 등장] =="]
            # 외모는 식별 포인트 1~2가지만
            appearance = char.get("appearance", "")
            if appearance:
                # 외모 텍스트가 길면 앞 80자만
                short_app = appearance[:80] + ("…" if len(appearance) > 80 else "")
                lines.append(f"식별 포인트: {short_app}")

            # 말투/행동은 핵심 1줄
            speech = char.get("speech_patterns") or char.get("말투") or char.get("말투_패턴")
            if speech:
                if isinstance(speech, list) and speech:
                    lines.append(f"말투 키워드: {speech[0]}")
                elif isinstance(speech, str):
                    lines.append(f"말투 키워드: {speech[:60]}")

            action = char.get("action_patterns") or char.get("행동_패턴") or char.get("행동패턴")
            if action:
                lines.append(f"행동 키워드: {str(action)[:60]}")

            arc = char.get("arc") or char.get("character_arc") or char.get("캐릭터_아크")
            if arc:
                lines.append(f"현재 아크: {str(arc)[:80]}")

            lines.append("★ 재등장 — 외모 풀 묘사 금지. 행동/말투/현재 심리 변화에 집중.")
            char_descriptions.append("\n".join(lines))

    if char_descriptions:
        blocks.append("[★ 등장 캐릭터 — 컨텍스트별 묘사 모드 ★]\n\n" +
                      "\n\n".join(char_descriptions))

    # ── 2. 씬 타입별 강도 가이드 ──
    if scene_types:
        scene_lines = ["[★ 이번 회차 씬별 묘사 강도 가이드 ★]"]
        for sinfo in scene_types:
            stype = sinfo.get("type", "standard")
            sdef = SCENE_TYPES.get(stype, SCENE_TYPES["standard"])
            label = sdef["label"]
            chars_min, chars_max = sdef["scene_chars"]
            weight = sdef["weight"]
            guide = sdef["guide"]
            scene_lines.append(
                f"  씬{sinfo.get('index', '?')} [{label}] "
                f"권장 {chars_min}~{chars_max}자 (강도 ×{weight})\n"
                f"    → {guide}"
            )
        scene_lines.append(
            "★ 위 강도에 맞춰 씬별 분량/묘사 밀도를 차등 적용. "
            "일상/이동 씬은 간결, 첫 등장/관능/이별 씬은 밀도 ↑."
        )
        blocks.append("\n".join(scene_lines))

    # ── 3. 장르별 우선순위 ──
    if genre:
        genre_block = get_genre_description_priority(genre)
        if genre_block:
            blocks.append(genre_block)

    # ── 4. Lovely Moments 추천 (회차별 회전) ──
    if genre and ep_number:
        # 장르 매칭 — 더 긴 키부터 우선 (로맨스판타지 vs 로맨스 충돌 방지)
        moments_pool = None
        sorted_lm_keys = sorted(LOVELY_MOMENTS.keys(), key=lambda k: -len(k))
        for key in sorted_lm_keys:
            if key in str(genre) or str(genre) in key:
                moments_pool = LOVELY_MOMENTS[key]
                break
        if moments_pool:
            n = len(moments_pool)
            # ep_number를 시드로 3개 회전 추출 (회차마다 다르게)
            try:
                ep_int = int(ep_number)
            except (ValueError, TypeError):
                ep_int = 1
            picks = []
            for i in range(3):
                idx = (ep_int * 3 + i) % n
                picks.append(moments_pool[idx])
            blocks.append(
                "[★ 이번 회차 Lovely Moment 후보 (3개 중 어울리는 1~2개 자연스럽게 활용) ★]\n" +
                "\n".join([f"  · {m}" for m in picks])
            )

    if not blocks:
        return ""

    return "\n\n".join(blocks)


# =================================================================

# =================================================================
# [2-3] READER PERSONAS — 수용자 분류 + KOCCA 통계
# =================================================================
# 타겟 독자층별 몰입 조건 프리셋
READER_PERSONAS = {
    "10대 여성": {
        "consumption_time": "거의 매일 (57.6%)",
        "motivation": "일탈, 감정 해소, 감수성 자극",
        "preferred_genres": "로판 · BL · 학원물 · 판타지",
        "preferred_hooks": "충격적 사건, 감수성 있는 묘사, 슬픈 아름다움, 아이돌/연예인",
        "identification": "높음 — 여주 자기 투영 강하게 선호",
        "payment": "기다무 의존적, 무료 중심, 극히 선택적 결제",
        "tone_preference": "서정적·감성적 문체 수용 가능, 내면 묘사 풍부",
    },
    "20~30대 여성": {
        "consumption_time": "출퇴근/자기 전 (일주일 3~4회)",
        "motivation": "스트레스 해소, 감정 카타르시스, 대리만족",
        "preferred_genres": "로판 · 로맨스 · 치정 · BL · 현판",
        "preferred_hooks": "사이다, 권력 역전, 로맨스 긴장, 19금 관능",
        "identification": "중간 — 대리만족 선호 (자기 투영보다 관찰)",
        "payment": "연재 동시 결제 가능, 완결작 일괄 결제",
        "tone_preference": "빠른 호흡 + 감정 밀도. 설명 지양, 행동·대사 중심",
    },
    "20~30대 남성": {
        "consumption_time": "저녁/주말",
        "motivation": "성취감 대리, 현실 도피, 쾌감 충족",
        "preferred_genres": "현판 · 판타지 · 무협 · 헌터물 · 게임판타지",
        "preferred_hooks": "먼치킨, 레벨업, 세계관 공개, 랭커 대결",
        "identification": "높음 — 주인공 = 나",
        "payment": "코인 충전 대량 소비, 연재 실시간 추적",
        "tone_preference": "간결·건조. 설명보다 행동. 스탯/능력치 시각화 선호",
    },
    "40대 이상 여성": {
        "consumption_time": "여유 시간, 주 1~3회",
        "motivation": "감정 카타르시스, 여운, 양질의 서사",
        "preferred_genres": "로맨스 · 로판 · 육아물 · 가족물 · 치정",
        "preferred_hooks": "섬세한 감정선, 가족 유대, 인물의 성장",
        "identification": "낮음 — 관찰자적 몰입",
        "payment": "양질의 완결작 선호, 단행본/일괄 구매",
        "tone_preference": "정제된 문장, 인물 심리 깊이 있게, 급전개 지양",
    },
    "청소년 남성": {
        "consumption_time": "거의 매일, 방과후",
        "motivation": "오락, 성취감, 세계관 탐험",
        "preferred_genres": "판타지 · 현판 · 게임판타지 · 무협 · 아이돌물",
        "preferred_hooks": "레벨업, 능력 획득, 던전 클리어, 시스템 메시지",
        "identification": "매우 높음 — 주인공 = 나",
        "payment": "무료 연재 위주, 극히 선택적 결제",
        "tone_preference": "짧고 직접적, 스탯·시스템 시각화 적극 활용",
    },
}


def get_reader_persona_block(persona):
    """타겟 독자 페르소나 정보를 프롬프트 블록으로."""
    if not persona or persona not in READER_PERSONAS:
        return ""
    p = READER_PERSONAS[persona]
    lines = [f"[타겟 독자 페르소나 — {persona}]"]
    lines.append(f"주 소비 시간: {p['consumption_time']}")
    lines.append(f"소비 동기: {p['motivation']}")
    lines.append(f"선호 장르: {p['preferred_genres']}")
    lines.append(f"선호 훅: {p['preferred_hooks']}")
    lines.append(f"동일시 필요도: {p['identification']}")
    lines.append(f"결제 성향: {p['payment']}")
    lines.append(f"선호 톤: {p['tone_preference']}")
    lines.append("")
    lines.append("※ 이 독자가 이탈하지 않도록 훅·톤·동일시 장치를 최적화할 것.")
    return "\n".join(lines)


# =================================================================
# [2-4] FLOW INDUCTION — 몰입 이론 기반
# =================================================================
FLOW_INDUCTION_RULES = """[독자 몰입 유도 규칙 — 몰입(Flow) 이론 기반]

★ 몰입 3단계 — 이 회차가 통과해야 할 조건

1단계. 명확한 목표 설정
   □ 독자가 '이 회차의 목적'을 3줄 안에 감지
   □ 도입부 첫 문장에 충격/터부/반전 중 하나 배치
   □ 장르 코드(로맨스/판타지/스릴러)가 초반 3문단 안에 확정

2단계. 도전과 기술의 균형
   □ 설득력 있는 문장 (AI 투 절대 금지)
   □ 독자-주인공 동일시 장치 삽입 (최소 1회)
     · 일반명사/애칭으로 부르기 ('그녀', '선배', '공주')
     · 내면 독백으로 공감 유발
     · 일상적 감정 언어화 ('~한 기분', '~인 것처럼')
   □ 개연성 없는 비약 금지
   □ 세계관/설정 과다 설명 금지 (2~3문장 안에 녹이기)

3단계. 즉각적 피드백 요소
   □ 댓글 유발 떡밥 or 반전 1개 이상
     (독자가 '이거 뭐지?' '다음에 어떻게 될까?'를 품게)
   □ 작가의 참신한 시도 — 장면 연출, 언어 선택, 사건 배치
   □ 회차 마지막에 '다음 회차 결제 의사'가 생길 만한 훅

★ 몰입 실패 지점 — 반드시 피할 것
   ✗ 선택 실패: 제목 유치함 / 길이 과도 / 내용 유추 불가
   ✗ 진입 실패: 초반 지루함 / 설명 남용 / 사건 지연
   ✗ 몰입 실패: 분위기 흐트러짐 / 개연성 붕괴 / 톤 혼선

★ 몰입 체화 — 도달 목표
   - 현장감 (독자가 손에 땀 쥐게)
   - 즉각 상상 (읽음과 동시에 이미지화)
   - 감정 카타르시스 (회차 끝에 여운)
   - 시간 감각 왜곡 (독자가 '벌써 끝났어?' 또는 '시간 가는 줄 몰랐어')
""".strip()


# =================================================================
# [2-5] READER SIMULATION — 시뮬레이션 프롬프트
# =================================================================
def build_reader_simulation_prompt(episode_text, persona, genre=""):
    """타겟 독자 페르소나로 가장해 회차에 대한 피드백 생성."""
    persona_block = get_reader_persona_block(persona)
    g_block = f"\n[장르] {genre}" if genre else ""
    return f"""당신은 이 작품의 타겟 독자 '{persona}'입니다. 아래 웹소설 회차를 실제 독자처럼 읽고, 몰입(Flow) 이론 관점에서 피드백하세요.

{persona_block}
{g_block}

[웹소설 회차 원고]
{episode_text}

[피드백 지침]
실제 독자처럼 솔직하게 반응. 작가 입장 금지. 문학 평론 금지.

[JSON 출력 — 이 구조를 정확히 따를 것]
{{
  "flow_entry": {{
    "success": true/false,
    "entry_point": "몇 번째 문장/문단에서 몰입 진입했는지 (실패 시 이유)",
    "clarity_score": 1~10
  }},
  "dropout_points": [
    {{"location": "문단 위치", "reason": "왜 이탈하고 싶었는지"}}
  ],
  "identification": {{
    "works": true/false,
    "evidence": "동일시가 작동한(또는 실패한) 구체적 장면"
  }},
  "comment_worthy": [
    "댓글로 남기고 싶은 포인트 1~3개"
  ],
  "payment_intent": {{
    "next_episode": true/false,
    "reason": "다음 화 결제 이유 또는 거부 이유"
  }},
  "flow_score": 1~10,
  "honest_verdict": "한 줄 평 (독자 말투로)"
}}""".strip()

# =================================================================
# [3] GENRE RULES
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
        "setpiece": "가면무도회, 밀실 대면, 전장 재회, 독살 위기, 비밀 폭로, 정략결혼 선언",
        "forbidden": [
            "여주가 수동적으로 구출만 당함",
            "남주가 이유 없이 폭력적",
            "세계관 설명이 2회차 이상 지속",
            "로맨스 없이 정치극만 3회차 이상",
        ],
        "reader_desires": [
            "① 출발선 우위 — 회빙환 + 고귀한 신분으로 남들보다 앞선 시작점",
            "② 가부장 안정 — 강한 남주의 보호 or 계약결혼 구조 (최근은 여주 주도형)",
            "③ 공정한 평가 — 혈통/성별/나이 장벽을 능력으로 극복",
            "④ 자아실현 — 여성이 아닌 한 인간으로의 사회적 성취",
            "⑤ 실리적 주인공 — 착하기만 하지 않고 이익을 계산하는 여주",
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
        "setpiece": "우연한 신체 접촉, 비 오는 날, 취중 고백, 질투 폭발, 이별 통보, 공항 재회",
        "forbidden": [
            "감정 설명으로 페이지 채우기",
            "삼각관계 질질 끌기 (20회차 이상)",
        ],
    },
    "치정 로맨스": {
        "core_emotion": "질투 + 집착 + 배신 + 애증",
        "must_have": [
            "과거 연인 관계의 잔재",
            "현재 연애의 제3자 개입",
            "감정의 극단 (극애증 / 극집착)",
            "비밀과 거짓의 누적",
            "폭로 장면",
        ],
        "hook_rule": "매 회차 끝에 관계의 위태로움이 한 단계 깊어진다",
        "punch_rule": "5회차 내 1회 이상 질투/집착 폭발 장면",
        "setpiece": "전 애인 재등장, 문자 메시지 발견, 집착 고백, 공개 망신, 이별 통보",
        "forbidden": [
            "폭력적 집착을 낭만으로 포장",
            "여주가 무조건 수동적",
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
    "시스템물": {
        "core_emotion": "생존 긴장 + 성장 쾌감 + 수치화된 성취 — 이선영(2026) 연구",
        "must_have": [
            "★ 죽음 위협 퀘스트 ('~하지 않으면 죽는다' 형식 — 예: 데뷔 못 하면 죽는 병)",
            "상태창/스탯/레벨의 명시적 시각화",
            "'특성' 아이템 (타고난 기질 vs 획득형 처세술 구분)",
            "'!상태이상' 항목 (정신적 결핍의 가시화)",
            "시스템의 이면/한계/반동인물화 (후반)",
            "초점캐릭터와 시스템의 비밀 관계",
        ],
        "hook_rule": "매 회차 끝에 스탯 변화, 새 퀘스트, 또는 시스템 메시지",
        "punch_rule": "5회차 내 1회 이상 수치적 성장이 가시화되는 장면 (B→A, A→S 승급 등)",
        "setpiece": "첫 각성, 레벨업 알림, 신규 특성 획득, 상태이상 해제 실패, 시스템 오류, 랭커 대결, 시스템의 진짜 모습 폭로",
        "forbidden": [
            "스탯 변화 없이 회차 진행",
            "시스템 규칙의 모호함 (독자가 예측 불가능)",
            "죽음 위협의 반복 지연 (실제 긴장감 없이 협박만)",
            "상태창을 설명문으로 대체",
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
        "setpiece": "고대 유적, 용/괴수 대결, 왕국 방어전, 금지된 마법",
        "forbidden": [
            "세계관 설명이 사건을 압도",
            "전투만 반복되고 인물이 성장하지 않음",
        ],
    },
    "무협": {
        "_note": "★ v2.5부터 무협은 별도 Wuxia Engine으로 이관. 이 Rule Pack은 비활성.",
        "core_emotion": "비장 + 의리 + 쾌감",
        "must_have": ["※ 무협 작품은 Wuxia Engine을 사용해주세요"],
        "hook_rule": "무협 전용 엔진 별도 개발 예정",
        "punch_rule": "-",
        "setpiece": "-",
        "forbidden": ["이 엔진은 무협 집필에 최적화되어 있지 않음"],
    },
    "게임판타지": {
        "core_emotion": "성취 + 쾌감 + 탐험",
        "must_have": [
            "명확한 시스템/상태창 규칙",
            "레벨·스킬·아이템 성장 축",
            "던전·레이드·PvP 이벤트",
            "플레이어 vs NPC 경계의 의미",
            "길드·파티·커뮤니티 관계",
            "랭킹/서열 경쟁",
        ],
        "hook_rule": "매 회차 끝에 새 스킬 획득 or 새 던전 공개 or 랭커 등장",
        "punch_rule": "3~5회차 내 1회 이상 먼치킨 사이다 장면",
        "setpiece": "히든 퀘스트 발동, 전설 아이템 획득, 레이드 보스 처치, 길드 전쟁, 랭커 대결, 서버 최초 클리어",
        "forbidden": [
            "시스템 설명이 5회차 이상 반복",
            "상태창 나열이 서사를 대체",
            "레벨업만 반복하고 관계·세계관 없음",
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
        "setpiece": "혼자 있는 밤, 반복되는 현상, 사라진 사람, 거울 속 이상",
        "forbidden": [
            "괴물이 너무 빨리 정체를 드러냄",
            "공포 없이 고어만 나열",
        ],
    },
}

def detect_genre_key(genre_input):
    gl = genre_input.strip()
    if gl in GENRE_RULES:
        return gl
    mapping = {
        "로판": "로맨스판타지", "로맨스 판타지": "로맨스판타지",
        "치정로맨스": "치정 로맨스", "치정": "치정 로맨스",
        "현판": "현대판타지", "현대 판타지": "현대판타지",
        "비엘": "BL", "bl": "BL",
        "지엘": "GL", "gl": "GL",
    }
    return mapping.get(gl, gl)

def get_genre_rules_block(genre_key):
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
    # 독자 욕구 체크리스트 (로판 등 일부 장르)
    if "reader_desires" in rules:
        lines.append("독자 욕구 충족 체크리스트 (1개 이상 반영):")
        for d in rules["reader_desires"]:
            lines.append(f"  {d}")
    return "\n".join(lines)

# =================================================================
# [4] CLIFFHANGER RULES
# =================================================================
CLIFFHANGER_TYPES = ["Slap", "Reveal", "Reversal", "Arrival", "Choice", "Threat", "Tears"]

CLIFFHANGER_RULES = """[클리프행어 7유형]
1. Slap — 물리적/감정적 충격
2. Reveal — 비밀 폭로
3. Reversal — 상황 역전
4. Arrival — 새 인물/요소 등장
5. Choice — 불가능한 선택
6. Threat — 임박한 위험
7. Tears — 감정 폭발

[클리프행어 규칙]
- 매 회차 마지막 3줄에 반드시 배치
- 같은 유형 3회차 연속 금지
- 과금 관문 직전 회차는 Reveal 또는 Reversal 사용
- 다음 회차 첫 장면과 직결
""".strip()

# =================================================================
# [5] RATING RULES
# =================================================================
RATING_19 = """[19금 수위 규칙 — 리디 성인관/카카오페이지 성인관]
허용: 직접적 성행위 묘사, 신체 부위 직접 명명(여성/남성), 관능적 감각 묘사 (촉각/체온/호흡/땀/맥박)
금지: 감정 없는 성묘사(포르노그래피), 폭력적/비합의적 성행위 미화, 플롯과 무관한 삽입

[19금 서사 구조 — 민선(2023) 섹슈얼리티 연구 기반]

★ 선섹스 후연애 구조 (19금 로맨스 핵심 공식)
   타인  →  先 섹스  →  後 감정  →  연인
   - 감정적 친밀도보다 몸의 접촉이 먼저
   - 성적 긴장감이 감정선을 견인
   - 계약결혼/하룻밤 상대/강요된 동거 등이 자주 사용되는 셋업

★ 서술 시점 원칙
   - 관능 씬의 신체 반응과 감정 변화는 여자 주인공 시점
   - 남주의 외적 행동/반응은 여주 시점에서 '관찰'
   - 남주 시점은 선언적 고백(집착/사랑)에만 제한적 사용
   - 이중 시점을 쓰면 독자 몰입 약화

★ 관능 씬의 4대 서사 기능 (반드시 1개 이상 포함)
   1. 성적 만족 제공 — 남주가 여주에게 미지의 쾌감을 가르침
   2. 부성 권위 대체 — 결핍된 아버지의 자리를 남주가 대체
   3. 경제적/사회적 안정 상징 — 남주의 소유 선언
   4. 정서적 성장 보조 — 여주의 자존감 회복

★ 남성 성기 묘사 (2011년 이후 허용)
   - 시각 + 촉각 + 체온 + 크기/단단함 다감각 서술
   - 단, 포르노그래피식 기계적 반복 금지
   - 여주의 신체 반응과 연결해서 묘사

★ 금기와 위반의 긴장 장치
   - 결혼·임신·육아가 '금기'가 아닌 '긴장 유발 장치'
   - 아버지(폭력적/결핍된) → 남주(대체자)로의 이동
   - 귀족/평민, 상사/부하 등 권력 비대칭을 성적 긴장으로 전환

[관능 씬 작법]
1. 정사 전: 심리적 긴장 + 신체 거리 축소 (시선 → 손끝 → 숨결)
2. 정사 중: 감각 교차 (촉각→시각→청각→체온→호흡)
3. 정사 후: 관계 변화 (호칭 · 의존도 · 자존감)
4. 대사: 짧고 끊어진다. 남주는 선언형, 여주는 의문형/단편
5. 시점: 여주 감각에 밀착. 남주는 외부에서 관찰
""".strip()

RATING_15 = """[15금 수위 규칙 — 카카오페이지/네이버시리즈]
허용: 키스/포옹 직접 묘사, 감각 암시(따뜻함/떨림/심장박동), 의복 위 접촉, 시선 머무름
금지: 직접적 성행위, 신체 부위 명명, 신음, 노출 묘사

15금 감정 전달:
1. 19금의 정사가 전달하는 감정(신뢰/취약성/친밀감)을 다른 방식으로
2. 대체: 비밀 공유, 위기 속 보호, 진심 고백, 함께하는 일상의 변화
3. 장면 전환: 키스 → "문이 닫혔다" → 다음 아침
4. 암시: 흐트러진 이불, 빈 자리, 달라진 호칭
""".strip()

RATING_CONVERSION_RULES = """[19금 → 15금 변환 규칙]
변환 매핑:
| 직접적 신체 접촉 | → | 의복 위의 감각 |
| 호흡/신음 | → | 침묵 또는 이름 부르기 |
| 시선이 신체 따라감 | → | 시선이 눈/입술에 머무름 |
| 정사 후 묘사 | → | 다음 아침 — 흐트러진 이불 |
| 관능적 대사 | → | 감정적 고백 |

원칙:
1. 단순 삭제 금지
2. 서사적 기능 유지
3. 분량 5,000~5,500자 ± 500자 유지
4. 관계 온도 변화 동일
5. 클리프행어 변경 금지
""".strip()

# =================================================================
# [6] AI ANTI-PATTERN
# =================================================================
AI_ANTI_PATTERN = """[AI 문체 탈출 규칙 A1~A14]
A1. 종결어미 반복 금지 (연속 3문장 같은 종결어미 불가)
A2. 주어 반복 금지 (연속 3문장 같은 주어 불가)
A3. 구문 구조 반복 금지
A4. 감정 직접 서술 금지 ("슬펐다" → 행동/신체반응)
A5. "마치 ~처럼" 과잉 금지 (회차당 비유 3회 이하)
A6. 감정 형용사 반복 금지
A7. 대시(—) 사용 제한 (회차당 2회 이하)
A8. 별표(**) 금지
A9. 접속부사 과잉 금지 ("그러나/하지만/그리고" 연속 불가)
A10. 시제 일관성 (과거형 기본)
A11. 요약 서술 금지 ("그 후 며칠이 지났다" 금지)
A12. 설명적 대사 금지
A13. 편의적 우연 금지
A14. 감정 나열 금지 ("분노와 슬픔이 밀려왔다" → 단일 행동)
""".strip()

# =================================================================
# [7] PROSE CRAFT
# =================================================================
WEB_NOVEL_PROSE_RULES = """[웹소설 문체 규칙 — 한국 웹소설 시장 표준]

[★ 웹소설식 줄바꿈 — 가장 중요한 규칙]
- 문장 단위로 줄바꿈 한다. 마침표 끝나면 엔터.
- 문단(덩어리)은 2~4줄로 끊고, 문단 사이에 빈 줄 하나.
- "벽돌" 금지: 여러 문장이 한 덩어리로 붙어 있으면 탈락.
- 모바일 한 화면 = 3~5줄. 스크롤이 술술 내려가야 한다.

예시:
✅ 좋음:
  지훈은 주머니에 손을 넣었다.
  차가운 쇠구슬이 손끝에 닿았다.
  아직 온기가 없다.

  "선생님."
  그가 낮게 불렀다.

❌ 나쁨 (벽돌):
  지훈은 주머니에 손을 넣었다. 차가운 쇠구슬이 손끝에 닿았다. 아직 온기가 없다. "선생님." 그가 낮게 불렀다.

[대사와 지문 — 반드시 분리]
- 대사와 지문은 절대 한 줄에 붙이지 않는다.
- 대사 위에 지문, 대사, 대사 아래 지문 — 각각 별도 줄.
- 영어권처럼 "He said."를 대사 뒤에 붙이는 방식 금지.

예시:
✅ 좋음:
  신유선이 천천히 고개를 돌렸다.
  "이제 그만 나오지?"
  안개 속에서 네 명의 그림자가 모습을 드러냈다.

❌ 나쁨:
  "이제 그만 나오지?" 신유선이 천천히 고개를 돌렸다.

[문장 길이]
- 단문 우선. 평균 15~25자.
- 긴 문장은 반드시 끊는다. 접속사 없이 병렬.
- 충격 장면: 한 줄 = 한 문장.

[대사 작법]
- 대사 비율 40% 이상.
- 한 턴 3줄 이하.
- 같은 캐릭터 연속 대사 금지 (지문 끼워넣기).
- 대사 태그 변주: "말했다" 반복 금지 → 행동 지문으로 화자 표시.
- 대사 안 생각/독백: '작은따옴표' + 별도 줄.

[감각]
- 시각보다 촉각/청각/후각 우선.
- 감정은 신체 반응으로 보여준다.
- 공간 진입은 온도/질감/냄새로.

[리듬]
- 짧은 문장 3개 → 중간 문장 1개 패턴.
- 충격 장면: 여백이 충격을 키운다.
- 관능 장면: 문장이 길어지고 호흡이 느려진다.

[금지]
- "~것이었다", "~터였다", "~셈이었다" 종결 금지.
- 격언/비유로 심리 풀지 않기.
- 설명적 장면 전환 ("한편 그 무렵") 금지.
- 풀네임 반복 금지 (첫 등장 이후 성 또는 이름만).
""".strip()

# =================================================================
# [8] EPISODE STRUCTURE
# =================================================================
PLATFORM_LENGTH = {
    "카카오페이지": {"target": 5200, "min": 5000, "max": 5500, "tolerance": 500},
    "리디북스": {"target": 5200, "min": 5000, "max": 5500, "tolerance": 500},
    "문피아": {"target": 5200, "min": 5000, "max": 5500, "tolerance": 500},
    "네이버시리즈": {"target": 5800, "min": 5500, "max": 6000, "tolerance": 500},
    "네이버웹소설": {"target": 6200, "min": 6000, "max": 6500, "tolerance": 500},
    "조아라": {"target": 4200, "min": 4000, "max": 4500, "tolerance": 300},
}

def get_platform_length(platform):
    """플랫폼별 분량 프리셋."""
    return PLATFORM_LENGTH.get(platform, PLATFORM_LENGTH["카카오페이지"])

EPISODE_STRUCTURE = """[회차 3단 구조 — 한국 웹소설 표준 5,000~5,500자]

[도입] 500~700자
  - 이전 회차 훅의 직접적 연결 (리캡이 아닌 연속)
  - 이번 회차의 질문/갈등 제기
  - 첫 3줄에서 독자를 잡는다
  - 세계관 설명 금지 (이미 아는 독자 기준)

[전개] 3,500~4,000자
  - 갈등 전개 + 감정선 진행
  - 정보 공개 또는 숨김 (떡밥 Plant/Hint)
  - 씬 전환 최대 2회 (많으면 산만)
  - 대사와 지문/행동이 번갈아 나온다
  - 중간에 작은 반전 1개 (미니 클리프행어)

[훅(클리프행어)] 500~800자
  - 다음 회차를 읽게 만드는 장치
  - 7유형 중 선택 (Slap/Reveal/Reversal/Arrival/Choice/Threat/Tears)
  - 마지막 3~5줄이 가장 중요하다
  - 다음 회차 첫 장면과 직결
  - 여백을 남겨서 충격을 키운다

[회차 내 기승전결]
분량 안에서도 기승전결을 갖춘다.
- 기: 도입 상황
- 승: 갈등 고조
- 전: 작은 반전 또는 새 정보
- 결: 클리프행어
""".strip()

# =================================================================
# [8-2] EPISODE TITLE — 중간 제목 (회차 부제) 생성 규칙
# =================================================================
EPISODE_TITLE_RULES = """[회차 제목 작법 — 웹소설 독자 클릭 유도용]

★ 웹소설에서 회차 제목은 플랫폼 목록에서 바로 노출되는 핵심 훅이다.
  독자가 "EP17. 가면 뒤의 남자"를 보고 "EP18"을 클릭할지 결정한다.

[형식 규칙]
- 7~15자 이내 (모바일 목록에서 잘리지 않게)
- 너무 짧으면(3자 이하) 흥미 반감
- 너무 길면(20자 초과) 모바일에서 잘림

[제목 유형 6가지]
1. 상황 제시형: "벼랑 끝의 구원자", "바다가 갈라지는 날"
2. 대사 인용형: "그만 나오지?", "네가 왜 여기에?"
3. 미스터리 제기형: "가면 뒤의 남자", "사라진 일기장"
4. 감정 선언형: "심장이 멈췄다", "잊히지 않는다"
5. 의외성형: "죽었다던 사람", "그녀의 진짜 이름"
6. 시간·공간형: "세 번째 밤", "카페의 낯선 손님"

[금지]
- "1화", "프롤로그" 등 단순 번호만 붙이는 제목
- 스포일러가 노출되는 제목 ("위하가 살아있었다")
- 감정 형용사 나열 ("슬프고 아픈 하루")
- 장황한 설명형 ("주인공이 카페에서 손님을 만나는 이야기")

[제목과 클리프행어의 관계]
- 제목은 회차 내용을 암시하되 결말은 숨긴다
- 클리프행어가 Reveal 유형이면, 제목은 그 직전 상황까지만 예고
""".strip()

# =================================================================
# [9] RECAP RULES
# =================================================================
RECAP_RULES = """[리캡 처리 규칙]
금지: "지난 회차에서 ~했다" 직접 요약 / "이전에 ~라고 말한 적이 있었는데" / 작가 시점 메타 서술
허용: 인물 행동/대사에 녹이기 / 소지품·공간으로 상기 / 다른 인물의 언급
""".strip()

# =================================================================
# [10] PAYWALL & CORE ARC DESIGN
# =================================================================
PAYWALL_DESIGN = """[과금 전환 설계]
무료 구간 (1~과금 전환점):
- 세계관 매력 극대화
- 남녀 케미 확립
- 첫 번째 대형 반전을 무료 구간 끝에
- 빌런의 구체적 위협 확립

과금 관문 (전환 직전 3회차):
- 시즌 최강 반전/폭로
- Reveal 또는 Reversal 클리프행어

유료 구간 (과금 이후):
- 관계 심화
- 떡밥 회수의 연쇄
- 중반 위기(All Is Lost) → 역전 카타르시스
""".strip()

CORE_ARC_DESIGN = """[Core Arc 완결형 설계 원칙]
Core Arc는 Extension이 없어도 단독 완결 가능해야 한다.

50화 Core Arc 표준 구조:
- EP 1~10 (도입): 세계관 + 갈등 설정 + 남녀 첫 접촉
- EP 11~25 (과금 관문): 1차 위기 + 대형 반전 (EP 23~25)
- EP 26~40 (중반): 2차 위기 + 비밀 폭로 + All Is Lost
- EP 41~50 (결말): 클라이맥스 + 1차 결말

Core Arc 떡밥 정책:
- 핵심 떡밥 80% 이상은 Core Arc 내 회수
- 미회수 떡밥은 "열린 결말"로 남겨두되, 완결성 해치지 않는 수준
- Extension 예비 떡밥 1~2개는 의도적으로 미회수 (확장 트리거용)
""".strip()

EXTENSION_DESIGN = """[Extension Arc 확장 원칙]
Extension은 기존 Core Arc의 완결성을 해치지 않으면서 새 국면을 여는 설계.

3가지 확장 모드:

[Mode 1] Bridge Extension (연재 중반 30~35화 시점)
- 기존 회차 수정 없음
- 남은 15화 중 3~5화를 Extension Bridge로 재설계
- 기존 결말을 "2차 위기의 시작"으로 전환
- 새 Sub-plot 활성화 + 새 떡밥 심기
- 가장 자연스러운 확장 방식

[Mode 2] Late Extension (연재 후반 45화 전후)
- 45~50화 재설계 필요
- 클라이맥스 유예 (거짓 결말 → 2차 위기)
- 원래 결말을 시즌1 클리프행어로 전환

[Mode 3] Season Break (Core Arc 완결 후)
- 독립된 시즌 2로 시작
- 기존 캐릭터 유지 + 새 갈등/세계관 확장
- 2~4주 간격 재연재

Extension Arc 설계 원칙:
- 기존 미회수 떡밥 재활용 (최소 1~2개)
- 신규 떡밥 추가 (Extension 완결을 위한)
- 독자 반응 데이터 반영 (있는 경우)
- 인기 캐릭터/관계 확대
""".strip()

# =================================================================
# [11] AUTHOR STYLE DNA
# =================================================================
AUTHOR_STYLE_DNA_BASE = """Mr.MOON 스타일 기본 규칙:
- 영화친화적인 상업 장편소설 톤.
- 장면은 공간/빛/냄새/소리/촉감 중 최소 1개 감각 요소로 진입.
- 세계관 설명은 사건/행동/인물반응/대사 속에 배치.
- 주요 인물 첫 등장 시 직업/결핍/비밀/욕망 중 최소 2개 드러남.
- 대사는 갈등/관계변화/정보전진에 기여.
- 감정은 결정적 장면에서 시선/침묵/몸짓/행동으로.
- 장면 말미에 반전/위협/감정흔들림/선택압력 중 하나.
- 감각어와 물성어를 반복 모티프로.
- 문장은 중간 길이 기본, 전환/충격 지점에서 짧게.

문체 금지:
- '~것이었다','~터였다','~셈이었다' 종결 금지.
- 격언/비유/철학적 진술로 심리 풀지 않기.
- 설명적 장면 전환 금지.
- 플롯 무관 분위기 묘사 금지.
- 풀네임 끝까지 반복 금지.
- 기계적 리듬 반복 금지.""".strip()

# =================================================================
# [12] HELPERS
# =================================================================
def _style_block(style_dna, strength="중"):
    sm = {
        "약": "문체 특징을 은은하게. 장르 요구와 가독성 우선.",
        "중": "문체 특징을 분명히. 반복감/자기복제 회피.",
        "강": "문체 특징을 강하게. 추진력/가독성은 유지.",
    }
    return (
        f"[기본 STYLE DNA]\n{AUTHOR_STYLE_DNA_BASE}\n\n"
        f"[사용자 STYLE DNA]\n{style_dna or '사용자 문체 샘플 없음.'}\n\n"
        f"[문체 반영 강도]\n{sm.get(strength, sm['중'])}"
    )

def _pn_block(producer_note):
    if producer_note and producer_note.strip():
        return f"\n[프로듀서 노트 — 반드시 반영]\n{producer_note.strip()}\n"
    return ""

def _genre_block(genre):
    return get_genre_rules_block(detect_genre_key(genre))

def _rating_block(rating):
    return RATING_19 if rating == "19" else RATING_15

# =================================================================
# [13] PROMPT BUILDERS — STEP 1: CONCEPT
# =================================================================

def build_parse_brief_prompt(brief_text):
    """기획서 텍스트를 컨셉 카드 JSON으로 파싱. v3.0: 신규 필드 자동 추론.
    
    분량 보호: 입력 텍스트가 너무 길면 앞부분 + 끝부분만 사용.
    (긴 기획서일수록 핵심 정보는 앞부분에 있고, 결말은 뒷부분에 있음)
    """
    # 분량 제한 — 너무 긴 기획서는 토큰 한도 초과 위험
    MAX_BRIEF_CHARS = 12000  # 약 15K~20K 토큰 (한국어 기준)
    
    if len(brief_text) > MAX_BRIEF_CHARS:
        head = brief_text[: MAX_BRIEF_CHARS - 2000]
        tail = brief_text[-2000:]
        brief_text = (
            head
            + "\n\n[...중략...]\n\n"
            + tail
        )
    
    primary_list = list(NARRATIVE_MOTIFS["primary"].keys())
    secondary_list = list(NARRATIVE_MOTIFS["secondary"].keys())
    persona_list = list(READER_PERSONAS.keys())
    tone_list = list(NARRATIVE_TONE_PRESETS.keys())
    
    # v3.0 신규 분류 — 데이터 모듈에서 가져옴
    formulas_list = list(ROMANCE_FORMULAS.keys()) if _V3_MOTIFS_AVAILABLE else []
    motifs_list = list(RELATIONSHIP_MOTIFS_DICT.keys()) if _V3_MOTIFS_AVAILABLE else []
    movement_list = list(MOVEMENT_NARRATIVE_PATTERNS.keys()) if _V3_MOTIFS_AVAILABLE else []
    consumption_tiers = list(READER_CONSUMPTION_TIERS.keys()) if _V3_CHARACTER_AVAILABLE else []
    
    v3_block = ""
    if _V3_MOTIFS_AVAILABLE and _V3_CHARACTER_AVAILABLE:
        v3_block = f"""
- v3.0 신규 분류 (반드시 추론):
  · formula_main (메인 포뮬러): {formulas_list}
  · formula_sub (보조 포뮬러, 없으면 빈 문자열)
  · movement_code (이동 코드): {movement_list} 중 1 (해당 없으면 빈 문자열)
  · relationship_motifs.primary: 23종 중 1 (메인 관계 동력)
  · relationship_motifs.secondary: 23종 중 2~4개 (보조 라인)
  · relationship_motifs.tertiary: 23종 중 0~3개 (배경 음영)
  · target_consumption_tier (소비자 분화, 1~2개): {consumption_tiers}
  · heroine_name (여주가 있다면 이름)
  
  23 관계성 모티프 목록: {motifs_list}"""
    
    return f"""다음은 웹소설/드라마 기획서 텍스트입니다. 이 내용을 웹소설 컨셉 카드 JSON으로 변환하세요.

[기획서 원문]
{brief_text}

[변환 지침]
- 기획서에 명시된 내용만 추출. 없는 내용은 빈 문자열 또는 빈 배열.
- 주인공/상대역/빌런이 구분되지 않으면 관계 구도로 판단.
- 상대역은 최대 5명까지 배열로.
- 빌런이 명시되지 않으면 villain.name = "" 로 남김 (자동 보강 대상).
- 서사 모티프 자동 판별:
  · primary_motif 선택지: {primary_list}
  · secondary_motif 선택지: {secondary_list}
  · 없으면 "일상" / "" 로 표기
- 타겟 독자 페르소나 자동 판별 (장르·분위기·수위·소재로 추론):
  · target_persona 선택지: {persona_list}
- 작품 지향점(톤) 자동 판별:
  · narrative_tone 선택지: {tone_list}
  · 로맨스·치정·19금은 "19금 치정 로맨스 (리디 성인관 톤)"
  · 판타지·19금 대하 서사는 "19금 판타지 (왕좌의 게임 톤)"
  · 현판·헌터물·흑화 서사는 "19금 현판 (문피아 남성향 톤)"
  · 게임 세계관은 "19금 게임판타지 (남성향)"
  · 건전한 일반 작품은 "15금 일반"
- 주인공 성격이 실리적이거나 반동인물적이면 is_antihero=true{v3_block}

[JSON 출력 — 이 구조를 정확히 따를 것]
{{
  "title": "작품 제목",
  "genre": "장르",
  "logline": "로그라인",
  "formula_tags": ["환생","역하렘","치정" 등 해당되는 태그만],
  "primary_motif": "회귀|빙의|환생|귀환|차원이동|일상 중 하나",
  "secondary_motif": "성장물|먼치킨물|사이다물|시한부물|책빙의물|육아물|법정물|학원물|아이돌물|전문직물|연예계물|헌터물 중 하나 (없으면 빈 문자열)",
  "target_persona": "10대 여성|20~30대 여성|20~30대 남성|40대 이상 여성|청소년 남성 중 하나",
  "narrative_tone": "15금 일반|19금 치정 로맨스 (리디 성인관 톤)|19금 판타지 (왕좌의 게임 톤)|19금 현판 (문피아 남성향 톤)|19금 게임판타지 (남성향)|조아라 노블레스 톤 중 하나",
  "formula_main": "",
  "formula_sub": "",
  "movement_code": "",
  "relationship_motifs": {{
    "primary": "",
    "secondary": [],
    "tertiary": []
  }},
  "target_consumption_tier": [],
  "heroine_name": "",
  "protagonist": {{
    "name": "", "age": 0, "role": "직업/지위",
    "profession": "한국 전문직 카테고리 명 (법률직·의료직·재벌2세3세·헌터각성자·판타지직업·회빙환주인공 등) + 세부 직종 명시",
    "goal": "원하는 것", "need": "필요한 것", "fatal_flaw": "치명적 결함",
    "is_antihero": false,
    "identification_strategy": {{
      "naming_style": "실명 사용 | 일반명사 통일 | 애칭 중심 중 하나",
      "empathy_points": ["독자가 공감할 감정/상황 1~3개"],
      "inner_monologue_style": "내면 독백 톤 서술 (예: 냉소적 자기 관찰, 체념적 짧은 사유)"
    }}
  }},
  "love_interests": [
    {{"name": "", "role": "", "profession": "직업/카테고리 명시", "appeal": "매력 포인트", "conflict": "관계의 갈등 요소"}}
  ],
  "villain": {{
    "name": "", "role": "", "profession": "직업/카테고리 명시", "wants": "", "justification": "", "limits": "", "win_rate": ""
  }},
  "world": "세계관/배경",
  "relationships": "관계 구도 서술",
  "season_questions": {{"romance": "", "mystery": ""}},
  "synopsis": "전체 시놉시스 3~5문장"
}}""".strip()


# =================================================================
# [v3.0 Phase D] 기획서 자동 변환 — 완성된 작품 기획서 → IdeaSeed 호환 콘셉트
# =================================================================

def build_brief_to_seed_prompt(brief_text, episode_structure=None):
    """[v3.0 Phase D] 완성된 작품 기획서를 IdeaSeed 호환 콘셉트 카드로 변환.
    
    build_parse_brief_prompt와 다른 점:
    - 입력 분량을 자르지 않음 (Sonnet 4.6의 1M 컨텍스트 활용)
    - locked_seed 구조로 출력 (IdeaSeed 호환)
    - 회차 구조 정보가 있으면 colspan 활용
    - v3.0 신규 분류 자동 추론
    
    Args:
        brief_text: 기획서 전체 텍스트 (자르지 않은 원본)
        episode_structure: parser.detect_episode_structure() 결과 (선택)
    
    Returns:
        Sonnet 4.6 호출용 프롬프트 문자열.
    """
    primary_list = list(NARRATIVE_MOTIFS["primary"].keys())
    persona_list = list(READER_PERSONAS.keys())
    
    formulas_list = list(ROMANCE_FORMULAS.keys()) if _V3_MOTIFS_AVAILABLE else []
    motifs_list = list(RELATIONSHIP_MOTIFS_DICT.keys()) if _V3_MOTIFS_AVAILABLE else []
    movement_list = list(MOVEMENT_NARRATIVE_PATTERNS.keys()) if _V3_MOTIFS_AVAILABLE else []
    consumption_tiers = list(READER_CONSUMPTION_TIERS.keys()) if _V3_CHARACTER_AVAILABLE else []
    
    # 회차 구조 정보 (있으면)
    structure_section = ""
    if episode_structure and episode_structure.get("has_episode_structure"):
        n_eps = episode_structure.get("max_episode", 0)
        n_acts = len(episode_structure.get("act_markers", []))
        ep_count = len(episode_structure.get("episode_markers", []))
        structure_section = f"""

[기획서 구조 자동 분석 결과]
- ACT 수: {n_acts}개
- 식별된 회차 마커: {ep_count}개
- 최대 회차 번호: EP{n_eps}
→ 이 작품은 회차 구조가 명확하므로 episode_count, total_eps 추정 가능"""
    
    return f"""[TASK] 완성된 작품 기획서를 v3.0 콘셉트 카드로 변환

당신은 한국 웹소설·드라마 기획·편집 베테랑입니다. 다음 작품 기획서를 분석해
v3.0 엔진에서 사용할 콘셉트 카드 JSON으로 변환하세요.

[기획서 원문]
{brief_text}{structure_section}

[변환 원칙]
1. 기획서에 명시된 정보만 반영. 없으면 빈 문자열 또는 빈 배열.
2. 작가의 의도를 존중 — 기획서에 표현된 톤·분위기·세계관을 그대로 보존.
3. v3.0 신규 분류는 기획서 내용을 보고 정확히 추론.
4. 회차별 스토리라인이 기획서에 있으면 그것이 핵심 자산이므로 무시하지 말 것.
5. 기획서가 길어도 핵심을 놓치지 않도록 — 시놉시스, 캐릭터, 회차 구조 모두 분석.

[v3.0 신규 분류 — 반드시 채울 것]
- formula_main (메인 포뮬러, 6종 중 1): {formulas_list}
- formula_sub (보조 포뮬러, 없으면 빈 문자열)
- movement_code (이동 코드, 5종 중 1): {movement_list}
- relationship_motifs:
  · primary: 23종 중 1 (메인 관계 동력)
  · secondary: 23종 중 2~4개 (보조 라인)
  · tertiary: 23종 중 0~3개 (배경 음영)
- target_consumption_tier (소비자 분화, 1~2개): {consumption_tiers}
- heroine_name (여주가 있다면 이름)

23 관계성 모티프 목록: {motifs_list}

[JSON 출력 — IdeaSeed 호환 + v3.0 신규 필드]
{{
  "title": "(기획서의 제목 그대로)",
  "genre": "(기획서 장르)",
  "logline": "(기획서 로그라인)",
  "formula_tags": ["환생","치정" 등 해당 태그],
  "primary_motif": "회귀|빙의|환생|귀환|차원이동|일상 중 1",
  "secondary_motif": "성장물|먼치킨물|사이다물|시한부물|책빙의물|법정물|학원물|아이돌물|전문직물|연예계물|헌터물 중 1",
  "target_persona": "{persona_list[0] if persona_list else ''}|... 중 1",
  "narrative_tone": "15금 일반|19금 치정 로맨스|19금 판타지|19금 현판|19금 게임판타지 중 1",
  "formula_main": "",
  "formula_sub": "",
  "movement_code": "",
  "relationship_motifs": {{
    "primary": "",
    "secondary": [],
    "tertiary": []
  }},
  "target_consumption_tier": [],
  "heroine_name": "",
  "protagonist": {{
    "name": "", "age": 0, "role": "직업/지위",
    "profession": "전문직 카테고리",
    "goal": "", "need": "", "fatal_flaw": "", "is_antihero": false,
    "identification_strategy": {{
      "naming_style": "실명 사용|일반명사 통일|애칭 중심 중 1",
      "empathy_points": ["독자 공감 포인트 1~3개"],
      "inner_monologue_style": ""
    }}
  }},
  "love_interests": [
    {{"name": "", "role": "", "profession": "", "appeal": "", "conflict": ""}}
  ],
  "villain": {{
    "name": "", "role": "", "profession": "",
    "wants": "", "justification": "", "limits": "", "win_rate": ""
  }},
  "world": "",
  "relationships": "",
  "season_questions": {{"romance": "", "mystery": ""}},
  "synopsis": "(기획서 시놉시스 3~5문장으로 압축)",
  "estimated_total_episodes": 0,
  "brief_meta": {{
    "source": "DOCX 기획서 자동 변환",
    "deep_theme": "(기획서가 담고 있는 심층 주제 — locked_theme.deep 호환)",
    "references": [],
    "risks_to_address": []
  }}
}}""".strip()


def build_brief_episode_extraction_prompt(brief_text, episode_structure):
    """[v3.0 Phase D] 기획서에서 회차별 스토리라인을 구조화된 JSON으로 추출.
    
    이 빌더는 build_brief_to_seed_prompt와 별도로 호출되며,
    회차별 플롯을 STEP 2 빌드업·STEP 3 회차 플롯 단계에서 활용 가능한 형태로 만든다.
    
    Args:
        brief_text: 기획서 전체 텍스트
        episode_structure: parser.detect_episode_structure() 결과
    
    Returns:
        Sonnet 4.6 호출용 프롬프트 문자열.
    """
    n_eps = episode_structure.get("max_episode", 0) if episode_structure else 0
    detected_eps = episode_structure.get("episode_markers", []) if episode_structure else []
    
    detected_summary = ""
    if detected_eps:
        lines = ["[자동 감지된 회차 마커]"]
        for em in detected_eps[:30]:
            lines.append(f"  EP{em['ep_num']}: {em['label']}")
        if len(detected_eps) > 30:
            lines.append(f"  ... 외 {len(detected_eps) - 30}개")
        detected_summary = "\n".join(lines)
    
    return f"""[TASK] 기획서에서 회차별 스토리라인 추출

당신은 한국 웹소설 시놉시스 분석 전문가입니다. 다음 작품 기획서에서
회차별 스토리라인을 구조화해 추출하세요.

[기획서 원문]
{brief_text}

{detected_summary}

[추출 원칙]
1. 기획서에 명시된 회차만 추출 (없는 회차는 만들지 말 것).
2. 회차별 핵심 사건·인물 등장·전환점·클리프행어를 분리.
3. ACT 구조가 있으면 함께 표시.
4. 회차 본문이 짧으면 비워둘 것 — 무리한 확장 금지.
5. 기획서에서 "X화" 또는 "ACT N"으로 명시된 부분만 추출.

[JSON 출력]
{{
  "act_structure": [
    {{
      "act": "ACT I",
      "ep_range": "EP1-15",
      "summary": "ACT I 전체 한 줄 요약"
    }}
  ],
  "episodes": [
    {{
      "ep_num": 1,
      "label": "설정",
      "act": "ACT I",
      "key_events": ["핵심 사건 1", "핵심 사건 2"],
      "characters_present": ["등장 인물"],
      "turning_point": "이 회차의 전환점 (있으면)",
      "cliffhanger": "회차 끝 클리프행어 (있으면)",
      "raw_summary": "기획서에 적힌 이 회차 스토리라인을 1~3 문장으로 압축"
    }}
  ],
  "total_episodes_in_brief": 0,
  "structure_quality": "상|중|하 (회차 구조 자세함의 정도)"
}}""".strip()


# =================================================================
# [v3.0 Phase D END] 기획서 자동 변환
# =================================================================


def build_ideaseed_to_concept_prompt(ideaseed_json_str, pending_decisions_resolved=None):
    """[v3.0+] Idea Engine의 IdeaSeed JSON을 받아 v3.0 콘셉트 카드로 변환.
    
    IdeaSeed의 locked 필드는 그대로 보존(재추론 금지)하고, v3.0 신규 필드만 추론한다.
    pending_decisions가 있으면 작가가 선택한 답을 반영해 콘셉트 카드를 확정한다.
    
    Args:
        ideaseed_json_str: Idea Engine 출력 JSON 문자열
        pending_decisions_resolved: 작가가 결정한 미결정 사항. 
            예: [{"question": "...", "answer": "..."}, ...]
    
    Returns:
        프롬프트 문자열.
    """
    # v3.0 신규 분류 안내
    formulas_list = list(ROMANCE_FORMULAS.keys()) if _V3_MOTIFS_AVAILABLE else []
    motifs_list = list(RELATIONSHIP_MOTIFS_DICT.keys()) if _V3_MOTIFS_AVAILABLE else []
    movement_list = list(MOVEMENT_NARRATIVE_PATTERNS.keys()) if _V3_MOTIFS_AVAILABLE else []
    consumption_tiers = list(READER_CONSUMPTION_TIERS.keys()) if _V3_CHARACTER_AVAILABLE else []
    
    # v2.6.4 레거시 motif (콘셉트 카드 호환용 — 자유 텍스트 금지)
    legacy_primary_motifs = list(NARRATIVE_MOTIFS["primary"].keys())  # 회귀, 빙의, 환생, 귀환, 차원이동, 일상
    legacy_secondary_motifs = list(NARRATIVE_MOTIFS["secondary"].keys())  # 성장물, 먼치킨물 등
    
    # 미결정 사항 처리
    pending_block = ""
    if pending_decisions_resolved:
        lines = ["\n[작가가 결정한 미결정 사항 — 콘셉트 카드 추론 시 반드시 반영]"]
        for i, d in enumerate(pending_decisions_resolved, 1):
            q = d.get("question", "")
            a = d.get("answer", "")
            lines.append(f"  Q{i}: {q}")
            lines.append(f"  → 작가 결정: {a}")
        pending_block = "\n".join(lines)
    
    return f"""[TASK] IdeaSeed JSON을 v3.0 웹소설 콘셉트 카드로 변환

[입력 — Idea Engine v1.0 산출물]
{ideaseed_json_str}
{pending_block}

[중요 원칙 — 반드시 준수]
1. IdeaSeed의 locked 필드는 작가가 이미 확정한 사항이므로 그대로 보존:
   - locked_logline → logline 그대로
   - locked_genre.primary → genre 그대로
   - locked_theme.deep → 시놉시스에 자연스럽게 반영
   - locked_references → 톤·문체 결정의 참조점으로만 활용
   - locked_target → target_persona 추론 시 핵심 단서

2. raw_idea를 핵심 시놉시스 소스로 활용 — 핵심 사건·반전·인물 관계 추출

3. v3.0 신규 필드는 IdeaSeed 정보를 바탕으로 정확히 추론:
   - formula_main (메인 포뮬러, 6종 중 1): {formulas_list}
   - formula_sub (보조 포뮬러, 없으면 빈 문자열)
   - movement_code (이동 코드, 5종 중 1, 해당 없으면 빈 문자열): {movement_list}
   - relationship_motifs:
     · primary: 23종 중 1
     · secondary: 23종 중 2~4개
     · tertiary: 23종 중 0~3개
   - target_consumption_tier (소비자 분화, 1~2개): {consumption_tiers}
   - heroine_name (여주가 있다면 이름. 남성향이면 protagonist.name과 동일)

4. ★★★ v2.6.4 레거시 motif 필드 — 반드시 다음 enum에서 정확히 1개 선택 (자유 텍스트 절대 금지):
   - primary_motif: {legacy_primary_motifs} 중 정확히 1개 (자유 텍스트 작성 금지)
   - secondary_motif: {legacy_secondary_motifs} 중 정확히 1개 (없으면 빈 문자열, 자유 텍스트 작성 금지)
   
   잘못된 예시 (절대 이렇게 하지 말 것):
   - "운명적_인연물 × 빙의 성장형 로맨스" ← 자유 텍스트 (X)
   - "연애 쑥맥의 전략적 각성" ← 자유 텍스트 (X)
   
   올바른 예시:
   - primary_motif: "빙의" (enum 1개)
   - secondary_motif: "성장물" (enum 1개)

5. formula_tags는 작품 태그 (자유 텍스트 OK, 단 짧은 키워드만):
   예: ["환생", "치정", "역하렘", "빙의"] — 5개 이내

6. OTT 시리즈 기반 IP라면 (locked_format이 OTT 시리즈인 경우):
   - 웹소설 선행 연재로 IP 검증하는 단계임을 의식
   - 시리즈의 톤·정체성을 웹소설 형식으로 정확히 변환
   - 시즌제 구조라면 first season을 우선 설계

7. locked_risks_to_address가 있다면 producer_note에 자동 반영
   (회피해야 할 함정으로 표시)

23 관계성 모티프 목록: {motifs_list}

[JSON 출력 — v3.0 콘셉트 카드. 반드시 단일 dict {{...}}로 출력 (배열로 감싸지 말 것)]
{{
  "title": "(IdeaSeed의 title_kr 그대로)",
  "genre": "(locked_genre.primary 그대로)",
  "logline": "(locked_logline 그대로)",
  "formula_tags": ["짧은 태그 1", "태그 2"],
  "primary_motif": "(반드시 위 enum 중 1개 — 회귀|빙의|환생|귀환|차원이동|일상)",
  "secondary_motif": "(반드시 위 enum 중 1개 또는 빈 문자열)",
  "target_persona": "(locked_target에서 추론)",
  "formula_main": "(6 포뮬러 중 1)",
  "formula_sub": "",
  "movement_code": "(5 이동 코드 중 1 또는 빈 문자열)",
  "relationship_motifs": {{
    "primary": "",
    "secondary": [],
    "tertiary": []
  }},
  "target_consumption_tier": [],
  "heroine_name": "",
  "protagonist": {{
    "name": "", "age": 0, "role": "", "goal": "", "need": "", "fatal_flaw": "", "is_antihero": false,
    "identification_strategy": {{
      "naming_style": "",
      "empathy_points": [],
      "inner_monologue_style": ""
    }}
  }},
  "love_interests": [
    {{"name": "", "role": "", "appeal": "", "conflict": ""}}
  ],
  "villain": {{"name": "", "role": "", "wants": "", "justification": "", "limits": "", "win_rate": ""}},
  "world": "",
  "relationships": "",
  "season_questions": {{"romance": "", "mystery": ""}},
  "synopsis": "",
  "producer_note": "(locked_risks_to_address를 회피 가이드로 변환)",
  "ideaseed_meta": {{
    "source": "Idea Engine v1.0",
    "project_id": "(IdeaSeed의 project_id 그대로)",
    "verdict": "(IdeaSeed의 verdict 그대로)",
    "hook_score": "(IdeaSeed의 hook_score 그대로)",
    "deep_theme": "(locked_theme.deep 그대로)",
    "references": []
  }}
}}""".strip()


def build_generate_concept_prompt(idea_text, genre=""):
    """한 줄 아이디어에서 컨셉 카드 자동 생성. v3.0: 신규 필드 자동 추론."""
    g_block = f"\n[장르]\n{genre}" if genre else ""
    primary_list = list(NARRATIVE_MOTIFS["primary"].keys())
    secondary_list = list(NARRATIVE_MOTIFS["secondary"].keys())
    persona_list = list(READER_PERSONAS.keys())
    
    # v3.0 신규 — 6 포뮬러, 23 모티프, 5 이동코드, 3 소비자 분화
    formulas_list = list(ROMANCE_FORMULAS.keys()) if _V3_MOTIFS_AVAILABLE else []
    motifs_list = list(RELATIONSHIP_MOTIFS_DICT.keys()) if _V3_MOTIFS_AVAILABLE else []
    movement_list = list(MOVEMENT_NARRATIVE_PATTERNS.keys()) if _V3_MOTIFS_AVAILABLE else []
    consumption_tiers = list(READER_CONSUMPTION_TIERS.keys()) if _V3_CHARACTER_AVAILABLE else []
    
    v3_block = ""
    if _V3_MOTIFS_AVAILABLE and _V3_CHARACTER_AVAILABLE:
        v3_block = f"""

[v3.0 신규 분류 — 반드시 추론하여 채울 것]
- formula_main (메인 포뮬러, 6종 중 1): {formulas_list}
- formula_sub (보조 포뮬러, 6종 중 1, 없으면 빈 문자열)
- movement_code (이동 코드, 5종 중 1, 해당 없으면 빈 문자열): {movement_list}
- relationship_motifs (23 모티프 중 선택):
  · primary: 23종 중 1 (메인 관계 동력)
  · secondary: 23종 중 2~4개 (보조 라인)
  · tertiary: 23종 중 0~3개 (배경 음영)
- target_consumption_tier (소비자 분화, 1~2개): {consumption_tiers}
- heroine_name (여주 이름 — protagonist.name 동일하게 채울 것. 마음 흐름 가이드용)

23 관계성 모티프 목록: {motifs_list}"""
    
    return f"""다음 아이디어를 기반으로 웹소설 컨셉 카드를 생성하세요.

[아이디어]
{idea_text}
{g_block}

[생성 지침]
- 주인공 Goal/Need/Fatal Flaw를 구체적으로 설계
- 상대역 3~5명 제안 (각자 뚜렷한 매력 차별화)
- 빌런 설정 (Villain 4Q 완비)
- 로맨스 축 + 미스터리 축 이원 시즌 질문
- 해당되는 웹소설 공식 태그 2~3개 부여
- 서사 모티프 판별:
  · primary_motif: {primary_list} 중 하나
  · secondary_motif: {secondary_list} 중 하나 (없으면 빈 문자열)
- 타겟 독자 페르소나 판별:
  · target_persona: {persona_list} 중 하나
- 주인공 동일시 전략 설계 (독자가 몰입할 수 있도록)
- 주인공이 실리적/반동인물적 성향이면 is_antihero=true
- 시놉시스 3~5문장{v3_block}

[JSON 출력]
{{
  "title": "", "genre": "", "logline": "",
  "formula_tags": [],
  "primary_motif": "",
  "secondary_motif": "",
  "target_persona": "",
  "formula_main": "",
  "formula_sub": "",
  "movement_code": "",
  "relationship_motifs": {{
    "primary": "",
    "secondary": [],
    "tertiary": []
  }},
  "target_consumption_tier": [],
  "heroine_name": "",
  "protagonist": {{
    "name":"","age":0,"role":"","goal":"","need":"","fatal_flaw":"","is_antihero":false,
    "identification_strategy": {{
      "naming_style": "",
      "empathy_points": [],
      "inner_monologue_style": ""
    }}
  }},
  "love_interests": [
    {{"name":"","role":"","appeal":"","conflict":""}}
  ],
  "villain": {{"name":"","role":"","wants":"","justification":"","limits":"","win_rate":""}},
  "world":"","relationships":"",
  "season_questions":{{"romance":"","mystery":""}},
  "synopsis":""
}}""".strip()


def build_augment_concept_prompt(concept_card_json):
    """컨셉 카드의 빈 필드 / 약한 필드를 자동 보강."""
    return f"""다음 웹소설 컨셉 카드에서 빈 필드 또는 약한 필드를 보강하세요.

[현재 컨셉 카드]
{concept_card_json}

[보강 지침]
- 주인공의 fatal_flaw가 비어있거나 "연애 쑥맥" 같이 표면적이면, 80화를 끌고 갈 드라마 엔진 수준으로 재설계.
  예: "유빈의 삶에 빠져들며 자기 자신을 잃어가는 정체성 균열"
- 빌런이 비어있으면, 상대역 중 한 명을 빌런화하거나 외부 빌런을 제안.
- season_questions.mystery가 비어있으면, 서스펜스 축을 만들 미스터리를 제안.
  예: "주인공의 죽음이 정말 사고였나?"
- formula_tags가 비어있으면 해당 장르/설정에 맞는 태그 부여.

[JSON 출력 — 보강된 전체 컨셉 카드]
원본 스키마 유지. 보강된 필드에 "_augmented": true 플래그 추가 (예: "fatal_flaw": "...", "_augmented_fatal_flaw": true).
""".strip()


# =================================================================
# [14] PROMPT BUILDERS — STEP 2: BUILD-UP
# =================================================================

def build_core_arc_prompt(concept_card, core_eps=50, producer_note="",
                          chunk=1, total_chunks=2, prev_summary=""):
    """Core Arc 설계 — 25화 × 2청크 (총 50화 완결형). v2.4: 캐릭터 플래그 + 관능 스케줄 + 페이싱."""
    paywall_ep = concept_card.get("serial_config", {}).get("paywall_ep", 25)
    rating_mode = concept_card.get("serial_config", {}).get("rating_mode", "")
    genre = concept_card.get("genre", "")
    tags = concept_card.get("formula_tags", [])

    blocks_per_chunk = 5
    start_block = (chunk - 1) * blocks_per_chunk + 1
    end_block = chunk * blocks_per_chunk
    start_ep = (start_block - 1) * 5 + 1
    end_ep = min(end_block * 5, core_eps)

    chunk_phases_50 = {
        1: f"도입 + 갈등 구축 (EP1~25). 세계관 진입, 남녀 첫 만남, 비밀 설정. 과금 관문(EP{paywall_ep}) 직전 최대 반전.",
        2: "중반 위기 + 완결 (EP26~50). 비밀 폭로, All Is Lost, 1차 클라이맥스, 완결. 단 Extension 여지 1~2개 열어둠.",
    }

    prev_block = f"\n[이전 청크 요약]\n{prev_summary}\n" if prev_summary else ""
    paywall_note = f"\n★ EP{paywall_ep-2}~{paywall_ep}는 과금 전환점. 이 청크 최강 반전 배치.\n" if chunk == 1 else ""

    # v2.4 신규
    character_flags = get_character_flags_block(concept_card)

    # 19금 관능 스케줄 지시 (첫 청크에서만 전체 스케줄 생성)
    intimacy_instruction = ""
    if chunk == 1 and ("19" in rating_mode or "듀얼" in rating_mode):
        intimacy_instruction = f"""

[⭐ 19금 관능 축 스케줄 설계 — 민선(2023) 선섹스 후연애 구조]
이 작품은 19금 수위를 포함함. 전체 {core_eps}화의 관능 축 배치를 반드시 함께 설계:
  · tension (긴장): 첫 신체 거리 축소/키스 시도
  · first_scene (첫 관능): 여주 시점 첫 관능 씬
  · power_tension (권력 긴장): 권력 비대칭·강제성 긴장
  · emotional_union (감정 교환): 진짜 사랑 확인 관능 씬

권장 배치:
  · tension → 전체 10% 지점 이내
  · first_scene → 전체 30% 지점 근처
  · power_tension → 전체 40~60% 지점
  · emotional_union → 전체 80~95% 지점

JSON 출력에 intimacy_schedule 필드를 반드시 포함할 것.
""".strip()

    # Extension 관능 스케줄 병합 지시 (2번째 청크)
    ext_intimacy = ""
    if chunk == 2 and ("19" in rating_mode or "듀얼" in rating_mode):
        ext_intimacy = "\n[참고] 이전 청크의 intimacy_schedule을 이어받아 후반부(26~50화) 관능 씬 배치 유지."

    return f"""[TASK] Core Arc {core_eps}화 설계 — 청크 {chunk}/{total_chunks} (EP{start_ep}~{end_ep})

[컨셉 카드]
제목: {concept_card.get('title','')}
장르: {genre}
로그라인: {concept_card.get('logline','')}
시즌 질문 (로맨스): {concept_card.get('season_questions',{}).get('romance','')}
시즌 질문 (미스터리): {concept_card.get('season_questions',{}).get('mystery','')}
주인공: {concept_card.get('protagonist',{})}
상대역 {len(concept_card.get('love_interests',[]))}명: {concept_card.get('love_interests',[])}
빌런: {concept_card.get('villain',{})}
세계관: {concept_card.get('world','')}
관계 구도: {concept_card.get('relationships','')}
시놉시스: {concept_card.get('synopsis','')}

{_genre_block(genre)}

{get_formula_block(tags)}

{character_flags}

{CORE_ARC_DESIGN}

{CLIFFHANGER_RULES}

{CLIFFHANGER_REALITY_FILTER}

[3막 페이싱 엄수 규칙]
★ 1막 (1~{int(core_eps*0.3)}화, 30%): 셋업·관계 형성
★ 2막 ({int(core_eps*0.3)+1}~{int(core_eps*0.7)}화, 40%): 긴장 상승·위기
★ 3막 ({int(core_eps*0.7)+1}~{core_eps}화, 30%): 클라이맥스·해결
★ 결혼/임신 같은 관계 정점은 최소 {int(core_eps*0.75)}화 이후 배치
★ 3막을 5~10화로 몰아붙이지 말 것 — 급전개는 독자 이탈 유발

{PAYWALL_DESIGN}

{_pn_block(producer_note)}{prev_block}{paywall_note}{intimacy_instruction}{ext_intimacy}

[이 청크의 국면]
{chunk_phases_50.get(chunk, '')}

[JSON 출력 — 이 청크의 5블록(25화)만]
{{
  "chunk": {chunk},
  "chunk_summary": "이 청크 25화 흐름 요약 2~3문장",
  {'"intimacy_schedule": [{{"ep_range": "3-5", "level": "tension", "description": "..."}}, ...],' if chunk == 1 and ("19" in rating_mode or "듀얼" in rating_mode) else ''}
  "blocks": [
    {{
      "block_no": {start_block},
      "ep_range": "EP{start_ep}~{start_ep+4}",
      "phase": "국면",
      "theme": "핵심 감정/사건",
      "episodes": [
        {{
          "ep": {start_ep},
          "title": "회차 제목 10자 이내",
          "summary": "핵심 사건 1줄 30자 이내",
          "cliffhanger_type": "Slap|Reveal|Reversal|Arrival|Choice|Threat|Tears",
          "cliffhanger": "클리프행어 내용 1줄",
          "plant_or_payoff": "P:떡밥명 또는 H:떡밥명 또는 R:떡밥명 또는 없음"
        }}
      ]
    }}
  ]
}}""".strip()


def build_extension_arc_prompt(concept_card, core_arc_text,
                               current_ep, extension_eps=50,
                               mode="bridge", reader_feedback="",
                               producer_note="",
                               chunk=1, total_chunks=2, prev_summary=""):
    """Extension Arc 설계 — Core Arc 이후 확장 회차."""

    genre = concept_card.get("genre", "")
    tags = concept_card.get("formula_tags", [])

    mode_desc = {
        "bridge": f"[Bridge Extension] 연재 중반(EP{current_ep}) 확장. EP{current_ep+1}~EP{current_ep+5}는 '2차 위기 도입' 브릿지. 이후 Extension Arc 본격 전개.",
        "late": f"[Late Extension] 연재 후반(EP{current_ep}) 확장. 원래 결말을 '시즌1 클리프행어'로 전환. EP51부터 완전 새 국면.",
        "season": f"[Season Break] Core Arc 완결 후 시즌 2. 기존 캐릭터 유지 + 새 세계관/갈등 확장.",
    }

    core_end = 50
    start_ep = core_end + (chunk - 1) * 25 + 1
    end_ep = min(core_end + chunk * 25, core_end + extension_eps)

    feedback_block = f"\n[독자 반응 데이터]\n{reader_feedback}\n" if reader_feedback.strip() else ""
    prev_block = f"\n[이전 청크 요약]\n{prev_summary}\n" if prev_summary else ""

    return f"""[TASK] Extension Arc 설계 — 청크 {chunk}/{total_chunks} (EP{start_ep}~{end_ep})

[확장 모드]
{mode_desc.get(mode, mode_desc['bridge'])}

[컨셉 카드]
{concept_card}

[Core Arc 요약]
{core_arc_text}

{_genre_block(genre)}

{get_formula_block(tags)}

{EXTENSION_DESIGN}

{CLIFFHANGER_RULES}

{_pn_block(producer_note)}{feedback_block}{prev_block}

[설계 원칙]
- Core Arc 미회수 떡밥 최소 1~2개 재활용 (구체적으로 어떤 떡밥인지 명시)
- 신규 떡밥 3~5개 추가
- 독자 반응 데이터가 있으면 인기 요소 확대
- 기존 캐릭터 유지 + 신규 캐릭터 1~2명 추가 가능
- 최종 클라이맥스는 이 Extension Arc에서 완결

[JSON 출력]
{{
  "chunk": {chunk},
  "chunk_summary": "...",
  "extension_mode": "{mode}",
  "bridge_episodes": [],
  "reused_plants": ["Core Arc의 어떤 떡밥을 재활용하는지"],
  "new_plants": ["새 떡밥 목록"],
  "new_characters": [{{"name":"","role":"","appeal":""}}],
  "blocks": [
    {{
      "block_no": 0, "ep_range": "EP{start_ep}~{start_ep+4}",
      "phase": "국면", "theme": "핵심",
      "episodes": [
        {{"ep": {start_ep}, "title":"","summary":"","cliffhanger_type":"","cliffhanger":"","plant_or_payoff":""}}
      ]
    }}
  ]
}}""".strip()


def build_plant_payoff_prompt(arc_text, characters, arc_type="core"):
    """Plant & Payoff 맵 생성."""
    arc_context = "Core Arc (50화 완결형)" if arc_type == "core" else "Extension Arc (확장 회차)"
    return f"""[TASK] {arc_context} 떡밥 맵 설계

[아크]
{arc_text}

[캐릭터]
{characters}

[떡밥 유형]
- 핵심: 시즌 관통 비밀/미스터리. Core Arc 40~50화 회수.
- 중기: 20~30화 단위 서브플롯.
- 단기: 3~5화 내 회수.
- 미끼(Red Herring): 의도적 오해 유도.
- Extension 예비: 의도적 미회수 (확장 트리거용). 1~2개.

[JSON 출력]
{{
  "arc_type": "{arc_type}",
  "plants": [
    {{
      "id": "P001",
      "name": "떡밥명",
      "type": "핵심|중기|단기|미끼|Extension예비",
      "description": "",
      "plant_ep": 0,
      "hints": [0,0,0],
      "payoff_ep": 0,
      "related_characters": []
    }}
  ]
}}""".strip()


def build_character_bible_prompt(concept_card_json, profession_blocks=""):
    """[v3.0 호환 유지용] 전체 캐릭터 바이블 (주연+조연 통합).
    
    ★ v3.0+ 권장: build_main_character_bible_prompt + build_supporting_character_bible_prompt
       두 함수를 사용해 분할 생성하면 토큰 한도 영구 해결 + 더 풍부한 캐릭터.
    
    이 함수는 기존 호환성을 위해 유지. 작은 작품(주연 3명 이하)에는 충분.
    """
    prof_section = f"\n\n{profession_blocks}" if profession_blocks else ""
    
    # v3.0 신규 — 9종 인물 역할, 모에 25속성 안내
    v3_block = ""
    if _V3_CHARACTER_AVAILABLE:
        roles_list = list(CHARACTER_ROLE_TAXONOMY.keys())
        moe_appearance = list(MOE_ATTRIBUTES_25.get("외관", {}).keys())
        moe_role = list(MOE_ATTRIBUTES_25.get("역할", {}).keys())
        moe_personality = list(MOE_ATTRIBUTES_25.get("성격", {}).keys())
        v3_block = f"""

[v3.0 신규 — 캐릭터 메타정보 자동 분배]
각 캐릭터에 다음 두 필드를 추가로 채울 것:

1) narrative_role (9종 인물 역할 중 1, 캐릭터별로 반드시 다르게 분배):
   {roles_list}
   
   ★ 평면화 방지 규칙: 한 작품의 모든 등장인물은 서로 다른 역할로 분배.
   특히 메인 남주 vs 라이벌 남주들이 동일 역할을 갖지 말 것.
   여주(protagonist)는 이 필드를 비울 수도 있음 (주인공은 역할 분류 대상 아님).

2) moe_attributes (모에 속성, 캐릭터당 1~3개. "카테고리:속성명" 형식):
   외관: {moe_appearance}
   역할: {moe_role}
   성격: {moe_personality}
   
   예시: ["성격:쿨데레", "역할:신비한_단골손님"] / ["성격:쿠데레", "역할:환생자"]
   
   ★ 캐릭터 차별화 규칙: 한 작품의 모든 인물의 모에 속성이 겹치지 않도록 분배.
   특히 성격 속성(쿨데레/츤데레/얀데레 등)은 인물마다 다르게."""
    
    return f"""[TASK] 웹소설 캐릭터 바이블 생성

[컨셉 카드]
{concept_card_json}
{prof_section}

[캐릭터 바이블 필드 (캐릭터당)]
- 이름, 나이(숫자만), 직업/지위, 외모 핵심
- 말투 (예문 2~3개 — 직업 전문 용어 자연스럽게 녹임)
- 행동 패턴 (특유의 버릇/제스처 — 직업적 습관 반영)
- 결핍/비밀 (직업적 스트레스가 개인의 상처와 맞물림)
- 욕망/목표 (직업 세계에서의 야망 포함)
- 변화 아크 (시즌 내 변화 방향)

★ 중요: age 필드는 숫자만 (예: 32). "32세"처럼 단위를 붙이지 말 것.

[직업 디테일 활용 규칙]
- 위에 제공된 직업 블록의 세부 디테일을 캐릭터에 녹일 것
- 전문 용어는 말투 예문에 1~2개 자연스럽게 포함
- 하루 타임라인의 특징을 행동 패턴에 반영
- 공간 디테일을 외모·소품 묘사에 활용
- 직업적 스트레스를 결핍/비밀에 연결
- 한국 맥락(계급·호칭·조직문화)을 반드시 반영
- 금지 사항(forbidden)은 반드시 회피{v3_block}

[JSON 출력 — 각 캐릭터에 narrative_role, moe_attributes 필드 포함]
{{
  "protagonist": {{
    "name": "", "age": 0, "occupation": "", "appearance": "",
    "speech_style": "", "behavior_pattern": "", "lack_or_secret": "",
    "desire_goal": "", "arc": "",
    "narrative_role": "",
    "moe_attributes": []
  }},
  "love_interests": [
    {{
      "name": "", "age": 0, "occupation": "", "appearance": "",
      "speech_style": "", "behavior_pattern": "", "lack_or_secret": "",
      "desire_goal": "", "arc": "",
      "narrative_role": "",
      "moe_attributes": []
    }}
  ],
  "villain": {{
    "name": "", "age": 0, "occupation": "", "appearance": "",
    "speech_style": "", "behavior_pattern": "", "lack_or_secret": "",
    "desire_goal": "", "arc": "",
    "narrative_role": "",
    "moe_attributes": []
  }},
  "supporting": [
    {{
      "name": "", "age": 0, "occupation": "", "appearance": "",
      "speech_style": "", "behavior_pattern": "", "lack_or_secret": "",
      "desire_goal": "", "arc": "",
      "narrative_role": "",
      "moe_attributes": []
    }}
  ]
}}""".strip()


def extract_char_consistency_facts(char_bible: dict) -> list:
    """[v3.0+ Creator Engine 패턴 도입]
    주연 바이블에서 일관성 핵심 사실을 추출.
    
    가족 관계·학력·나이·출신지·직업이 다음 캐릭터 생성 시 모순 일으키지 않도록.
    
    Args:
        char_bible: 캐릭터 바이블 dict {protagonist, love_interests, villain, supporting}
    
    Returns:
        [{"name", "age", "occupation", "key_facts"}, ...] — 일관성 검증용 핵심 사실
    """
    facts = []
    
    def _extract_one(char: dict, role_label: str = ""):
        if not isinstance(char, dict) or not char.get("name"):
            return None
        name = char.get("name", "")
        age = char.get("age", "")
        occupation = char.get("occupation", "") or char.get("role", "")
        
        # 일관성 위험 필드들 — 가족·학력·관계 등
        key_facts = []
        for field in ["lack_or_secret", "behavior_pattern", "appearance", "arc"]:
            val = char.get(field, "")
            if val and len(val) < 200:  # 너무 길면 자름
                key_facts.append(f"{field}: {val[:150]}")
        
        return {
            "name": name,
            "age": age,
            "occupation": occupation,
            "role_label": role_label,
            "key_facts": key_facts,
        }
    
    # 주인공
    p = char_bible.get("protagonist", {})
    f = _extract_one(p, "주인공")
    if f:
        facts.append(f)
    
    # 사랑 상대
    for i, li in enumerate(char_bible.get("love_interests", []) or []):
        f = _extract_one(li, f"사랑상대{i+1}")
        if f:
            facts.append(f)
    
    # 빌런
    v = char_bible.get("villain", {})
    f = _extract_one(v, "빌런")
    if f:
        facts.append(f)
    
    return facts


def build_prior_chars_consistency_block(prior_facts: list) -> str:
    """[v3.0+ Creator Engine 패턴 도입]
    이전에 생성된 캐릭터들의 일관성 사실을 다음 캐릭터 생성 LLM에게 주입할 블록.
    
    Args:
        prior_facts: extract_char_consistency_facts 결과
    
    Returns:
        LLM 프롬프트 삽입용 마크다운 블록 (빈 list면 빈 문자열)
    """
    if not prior_facts:
        return ""
    
    lines = [
        "",
        "[★ 이미 생성된 캐릭터 — 일관성 모순 차단용 컨텍스트]",
        "다음 캐릭터들과 가족 관계·학력·나이·출신지가 모순되지 않도록 주의:",
        "",
    ]
    
    for f in prior_facts:
        name = f.get("name", "")
        age = f.get("age", "")
        occ = f.get("occupation", "")
        label = f.get("role_label", "")
        
        header = f"  ▶ {name} ({label}, 나이 {age}, {occ})"
        lines.append(header)
        
        for kf in f.get("key_facts", [])[:3]:  # 최대 3개만
            lines.append(f"     - {kf}")
        lines.append("")
    
    lines.extend([
        "[일관성 규칙]",
        "- 가족 관계: 위 인물의 가족(부모·형제·자녀)이 본 캐릭터에게도 등장한다면 동일한 인물·관계로 표현",
        "- 학력·출신지: 같은 학교·지역 출신이면 모순 없게 (예: 같은 대학 동기인데 다른 학번 X)",
        "- 나이 격차: 위 인물과의 나이 차이가 컨셉 카드의 관계(선후배·동기·세대차)와 일치",
        "- 직업 세계: 같은 업계라면 같은 회사·동일 분야 가능, 단 컨셉 카드 위배 금지",
        "- 시점·세계관: 같은 작품 세계 안에서 시간선·공간이 일관되게",
        "",
    ])
    
    return "\n".join(lines)


def build_main_character_bible_prompt(concept_card_json, profession_blocks=""):
    """[v3.0+ 분할 생성] 주연 캐릭터 바이블 — 주인공 + 사랑상대 + 빌런만.
    
    풍부한 작품(사랑상대 5명+, 빌런 1명)도 안전하게 처리.
    조연(supporting)은 별도 build_supporting_character_bible_prompt로 생성.
    
    토큰 권장: max_tokens=10,000 (주연 7~8명까지 충분).
    """
    prof_section = f"\n\n{profession_blocks}" if profession_blocks else ""
    
    v3_block = ""
    if _V3_CHARACTER_AVAILABLE:
        roles_list = list(CHARACTER_ROLE_TAXONOMY.keys())
        moe_appearance = list(MOE_ATTRIBUTES_25.get("외관", {}).keys())
        moe_role = list(MOE_ATTRIBUTES_25.get("역할", {}).keys())
        moe_personality = list(MOE_ATTRIBUTES_25.get("성격", {}).keys())
        v3_block = f"""

[v3.0 신규 — 캐릭터 메타정보 자동 분배]
각 캐릭터에 다음 두 필드를 추가로 채울 것:

1) narrative_role (9종 인물 역할 중 1, 캐릭터별로 반드시 다르게 분배):
   {roles_list}
   
   ★ 평면화 방지 규칙: 모든 등장인물은 서로 다른 역할.
   특히 메인 남주 vs 라이벌 남주들이 동일 역할을 갖지 말 것.
   여주(protagonist)는 이 필드를 비울 수도 있음.

2) moe_attributes (캐릭터당 1~3개. "카테고리:속성명" 형식):
   외관: {moe_appearance}
   역할: {moe_role}
   성격: {moe_personality}
   
   예시: ["성격:쿨데레", "역할:신비한_단골손님"]
   
   ★ 차별화 규칙: 모든 인물의 모에 속성이 겹치지 않도록 분배.
   특히 성격 속성(쿨데레/츤데레/얀데레)은 인물마다 다르게."""
    
    return f"""[TASK] 웹소설 ★ 주연 ★ 캐릭터 바이블 생성 (주인공 + 사랑상대 + 빌런)

[컨셉 카드]
{concept_card_json}
{prof_section}

[★ 이번 호출 범위: 주연만]
- protagonist (주인공) — 1명
- love_interests (사랑 상대) — 컨셉 카드에 명시된 모든 사랑 상대
- villain (빌런) — 컨셉 카드에 빌런이 있다면

조연(supporting)은 별도 호출에서 생성하므로 ★ 이번에는 만들지 말 것 ★

[★ 캐릭터 간 일관성 규칙 — 평면화·모순 차단]
한 작품 안에서 모든 주연이 함께 살아 움직이는 세계이므로, 다음을 반드시 검증:

1) **나이 격차 일관성** — 컨셉 카드의 관계(선후배·동기·세대차)와 일치
   예: 사랑상대 A·B가 "대학 동기"로 명시 → 두 사람의 나이 차이는 1살 이내
   예: 빌런이 주인공의 "친언니" → 나이는 주인공보다 1~5살 위

2) **가족 관계 통합 검증** — 한 인물의 가족이 다른 인물의 가족과 겹치면 동일 인물로
   예: 주인공의 어머니가 사랑상대 A의 회사 동료 → 동일한 1명의 어머니

3) **학력·출신지 모순 차단**
   - 같은 학교 동문 → 학번·전공 모순 없게
   - 같은 지역 출신 → 사투리·지역 정서 일관

4) **직업 세계 충돌 방지**
   - 사랑상대들이 같은 업계인지 컨셉 카드 확인
   - 같은 회사라면 직급·소속 부서 모순 없게

5) **세계관·시점 통합**
   - 회귀·빙의·환생 코드가 있는 경우 → 모든 캐릭터가 같은 시간선
   - 빌런의 동기가 주인공의 비밀과 연결되는지 확인

★ 위 5가지를 어기면 작가가 후속 회차에서 모순을 발견해 재집필 부담이 큼.

[캐릭터 바이블 필드 (캐릭터당)]
- 이름, 나이(숫자만), 직업/지위, 외모 핵심
- 말투 (예문 2~3개 — 직업 전문 용어 자연스럽게 녹임)
- 행동 패턴 (특유의 버릇/제스처 — 직업적 습관 반영)
- 결핍/비밀 (직업적 스트레스가 개인의 상처와 맞물림)
- 욕망/목표 (직업 세계에서의 야망 포함)
- 변화 아크 (시즌 내 변화 방향)

★ 중요: age 필드는 숫자만 (예: 32). "32세"처럼 단위를 붙이지 말 것.

[직업 디테일 활용 규칙]
- 위에 제공된 직업 블록의 세부 디테일을 캐릭터에 녹일 것
- 전문 용어는 말투 예문에 1~2개 자연스럽게 포함
- 한국 맥락(계급·호칭·조직문화) 반드시 반영{v3_block}

[JSON 출력 — supporting 필드는 빈 배열로 둘 것]
{{
  "protagonist": {{
    "name": "", "age": 0, "occupation": "", "appearance": "",
    "speech_style": "", "behavior_pattern": "", "lack_or_secret": "",
    "desire_goal": "", "arc": "",
    "narrative_role": "",
    "moe_attributes": []
  }},
  "love_interests": [
    {{
      "name": "", "age": 0, "occupation": "", "appearance": "",
      "speech_style": "", "behavior_pattern": "", "lack_or_secret": "",
      "desire_goal": "", "arc": "",
      "narrative_role": "",
      "moe_attributes": []
    }}
  ],
  "villain": {{
    "name": "", "age": 0, "occupation": "", "appearance": "",
    "speech_style": "", "behavior_pattern": "", "lack_or_secret": "",
    "desire_goal": "", "arc": "",
    "narrative_role": "",
    "moe_attributes": []
  }},
  "supporting": []
}}""".strip()


def build_supporting_character_bible_prompt(concept_card_json, main_bible_json, profession_blocks="", prior_facts=None):
    """[v3.0+ 분할 생성 + 일관성 검증] 조연 캐릭터 바이블 — 주연 바이블 + 일관성 사실 컨텍스트로 받음.
    
    조연은 주연과 차별화 + 일관성 모순 차단 두 가지를 동시에 만족해야 함.
    
    Args:
        concept_card_json: 컨셉 카드 JSON
        main_bible_json: 이미 생성된 주연 바이블 JSON (차별화용)
        profession_blocks: 직업 디테일 블록
        prior_facts: extract_char_consistency_facts(main_bible) 결과 — 일관성 모순 차단용
    
    토큰 권장: max_tokens=8,000 (조연 6~10명까지 충분).
    """
    prof_section = f"\n\n{profession_blocks}" if profession_blocks else ""
    
    # 일관성 블록 (선택적)
    consistency_block = build_prior_chars_consistency_block(prior_facts) if prior_facts else ""
    
    v3_block = ""
    if _V3_CHARACTER_AVAILABLE:
        roles_list = list(CHARACTER_ROLE_TAXONOMY.keys())
        moe_appearance = list(MOE_ATTRIBUTES_25.get("외관", {}).keys())
        moe_role = list(MOE_ATTRIBUTES_25.get("역할", {}).keys())
        moe_personality = list(MOE_ATTRIBUTES_25.get("성격", {}).keys())
        v3_block = f"""

[v3.0 신규 — 캐릭터 메타정보]
각 조연에 다음 두 필드 채울 것:

1) narrative_role (9종 중 1):
   {roles_list}
   
   ★ 위 [기존 주연 바이블]에서 사용된 역할은 가능하면 피하고,
   조연만의 다른 역할을 부여할 것. 단 보조적 역할로 적정.

2) moe_attributes (조연당 1~2개, "카테고리:속성명"):
   외관: {moe_appearance}
   역할: {moe_role}
   성격: {moe_personality}
   
   ★ 주연 바이블에 없는 속성을 우선 사용해 차별화."""
    
    return f"""[TASK] 웹소설 ★ 조연 ★ 캐릭터 바이블 생성 (supporting만)

[컨셉 카드]
{concept_card_json}

[★ 이미 생성된 주연 바이블 — 차별화 참고용]
{main_bible_json}
{consistency_block}{prof_section}

[★ 이번 호출 범위: 조연(supporting)만]
- 주인공·사랑상대·빌런은 이미 생성됨. 절대 다시 만들지 말 것
- 컨셉 카드의 시놉시스·세계관에서 필요한 조연 인물을 추출
- 일반적으로 3~8명 정도. 작품 규모에 맞게 결정

[조연이란]
- 주연 인물 주변에서 작품 세계를 풍부화하는 보조 캐릭터
- 가족·친구·동료·이웃·라이벌 등 작품 세계의 살아있는 배경
- 주연만큼 풍부할 필요는 없으나, 단순 들러리는 금지
- 각자 명확한 기능(주인공 도움/방해/거울/대조 등)을 가질 것

[조연 캐릭터 필드 (조연당)]
- 이름, 나이(숫자만), 직업/지위
- 외모 핵심 (간략)
- 말투 (예문 1~2개 — 주연과 명확히 다름)
- 행동 패턴 (1~2가지 특징)
- 결핍/비밀 (주연 서사에 영향 주는 부분만)
- 욕망/목표 (개인적 동기, 주연과의 관계)
- 변화 아크 (조연도 작은 변화 곡선 가짐){v3_block}

★ 중요: age 필드는 숫자만.

[JSON 출력 — supporting 배열만]
{{
  "supporting": [
    {{
      "name": "", "age": 0, "occupation": "", "appearance": "",
      "speech_style": "", "behavior_pattern": "", "lack_or_secret": "",
      "desire_goal": "", "arc": "",
      "narrative_role": "",
      "moe_attributes": []
    }}
  ]
}}""".strip()


def build_episode_plot_prompt(arc_block, plant_map, ep_number,
                              prev_summary, producer_note="",
                              concept_dict=None, total_eps=50,
                              intimacy_schedule=None):
    """회차 플롯 설계 + 제목 생성. v2.4: 캐릭터 플래그 + 페이싱 + 씬 수 강제 + 관능 지시."""
    # v2.4 신규 블록
    character_flags = get_character_flags_block(concept_dict or {})
    pacing_block = get_pacing_block(ep_number, total_eps)
    intimacy_directive = get_intimacy_schedule_for_ep(intimacy_schedule, ep_number)

    return f"""[TASK] EP{ep_number} 회차 플롯 설계 (전체 {total_eps}화 중)

[아크 블록]
{arc_block}

[떡밥 맵 — 이번 회차 관련]
{plant_map}

[이전 회차 요약]
{prev_summary}

{character_flags}

{pacing_block}

{intimacy_directive}

{_pn_block(producer_note)}

{EPISODE_STRUCTURE}

{EPISODE_TITLE_RULES}

{CLIFFHANGER_RULES}

{CLIFFHANGER_REALITY_FILTER}

[씬 구성 엄수 규칙]
★ 반드시 3~4씬으로 구성 (2씬은 분량 부족, 5씬 이상은 밀도 저하)
★ 각 씬은 장소·인물·갈등·결과가 명시되어야 함
★ 씬 간 시간·공간 전환이 있어야 함 (한 장면 연속 금지)
★ 각 씬에 떡밥 심기/회수/힌트가 최소 1개씩 배치 권장

[감정 곡선 규칙]
★ '혼란→절망→불안→경계' 같은 수동적 감정 반복은 금지
★ 반동인물 주인공일 경우 감정 외에 '판단/결심/행동' 축이 40% 이상
★ 감정 곡선은 2~3개 지점으로 구성하되, 마지막 지점이 다음 회차 훅과 연결

[JSON 출력]
- title: 7~15자. 6가지 유형 중 가장 적합한 것 선택. 스포일러 금지.
{{
  "ep": {ep_number},
  "title": "회차 부제 (7~15자)",
  "title_type": "상황|대사|미스터리|감정|의외성|시공간",
  "opening": {{"hook_line":"첫 문장","recap_method":"행동|소지품|대사","question":"독자가 품을 질문"}},
  "development": {{
    "scenes": [
      {{"scene_no":1,"location":"","characters":[],"conflict":"","outcome":"","plant_or_payoff":""}},
      {{"scene_no":2,"location":"","characters":[],"conflict":"","outcome":"","plant_or_payoff":""}},
      {{"scene_no":3,"location":"","characters":[],"conflict":"","outcome":"","plant_or_payoff":""}}
    ],
    "emotion_arc": "감정 곡선 (2~3개 지점, 마지막은 훅 연결)"
  }},
  "cliffhanger": {{"type":"","content":"","next_ep_connection":""}}
}}""".strip()


# =================================================================
# [15] PROMPT BUILDERS — STEP 3: WRITING
# =================================================================

# =================================================================
# [v3.0 / Phase B] 신규 블록 빌더 5종
# 기획↔집필 연결 강제 — 기획에서 정한 모든 재료가 집필 프롬프트에 주입됨
# =================================================================

def build_formula_strategy_block(concept):
    """[v3.0 Phase B] 메인/보조 포뮬러 다이어그램 + 표상 모티프 주입.
    
    concept dict에서 formula_main / formula_sub 키를 읽어, 해당 포뮬러의
    스토리 다이어그램과 표상 모티프 키워드를 프롬프트에 강제 주입한다.
    
    Args:
        concept: 콘셉트 카드 dict. 예: {"formula_main": "운명적_인연물", ...}
    
    Returns:
        프롬프트 블록 문자열. 데이터 없으면 빈 문자열.
    """
    if not concept or not _V3_MOTIFS_AVAILABLE:
        return ""
    
    formula_main = concept.get("formula_main", "")
    formula_sub = concept.get("formula_sub", "")
    
    if not formula_main and not formula_sub:
        return ""
    
    lines = ["[★ 포뮬러 전략 — 기획 단계에서 결정된 메인 라인 ★]"]
    
    # 메인 포뮬러
    if formula_main and formula_main in ROMANCE_FORMULAS:
        f = ROMANCE_FORMULAS[formula_main]
        lines.append(f"\n[메인 포뮬러] {formula_main}")
        lines.append(f"  정의: {f.get('definition', '')}")
        diagram = f.get("story_diagram", [])
        if diagram:
            lines.append("  스토리 다이어그램:")
            for step in diagram:
                lines.append(f"    {step}")
        rep_motifs = f.get("representative_motifs", [])
        if rep_motifs:
            lines.append(f"  ★ 표상 모티프 (이 회차에 1개 이상 반드시 등장): {', '.join(rep_motifs)}")
        keywords = f.get("title_pattern_keywords", [])
        if keywords:
            lines.append(f"  제목 패턴 키워드: {', '.join(keywords[:6])}")
    
    # 보조 포뮬러
    if formula_sub and formula_sub in ROMANCE_FORMULAS:
        f = ROMANCE_FORMULAS[formula_sub]
        lines.append(f"\n[보조 포뮬러] {formula_sub}")
        lines.append(f"  정의: {f.get('definition', '')}")
        rep_motifs = f.get("representative_motifs", [])
        if rep_motifs:
            lines.append(f"  표상 모티프 (등장 회차에 활용): {', '.join(rep_motifs)}")
    
    lines.append("\n[활용 원칙]")
    lines.append("  - 메인 포뮬러는 작품 전체의 척추. 이 회차에서 다이어그램의 어느 지점에 있는지 의식")
    lines.append("  - 표상 모티프 중 최소 1개는 본 회차의 행동·대사·소품 어딘가에 자연스럽게 등장")
    lines.append("  - 모티프를 직접 명명하지 말고 행동·풍경·관계로 보여줄 것")
    
    return "\n".join(lines)


def build_motif_block(concept, ep_number=0):
    """[v3.0 Phase B] 회차별 모티프 등장 가이드.
    
    concept의 relationship_motifs 필드를 읽어 23모티프 중 해당 모티프의 정의를
    주입. 어떤 회차에 어떤 모티프가 등장하는지 가이드 제공.
    
    Args:
        concept: 콘셉트 카드 dict. 예: {"relationship_motifs": {"primary": "재회물", ...}}
        ep_number: 현재 회차 번호 (0이면 모든 모티프 표시)
    
    Returns:
        프롬프트 블록 문자열.
    """
    if not concept or not _V3_MOTIFS_AVAILABLE:
        return ""
    
    motifs_data = concept.get("relationship_motifs", {})
    if not motifs_data:
        return ""
    
    primary = motifs_data.get("primary", "")
    secondary = motifs_data.get("secondary", []) or []
    tertiary = motifs_data.get("tertiary", []) or []
    
    if not (primary or secondary or tertiary):
        return ""
    
    lines = ["[★ 관계성 모티프 — 23종 중 선택된 모티프 ★]"]
    
    # 1순위 모티프 (메인)
    if primary and primary in RELATIONSHIP_MOTIFS_DICT:
        m = RELATIONSHIP_MOTIFS_DICT[primary]
        lines.append(f"\n[1순위 모티프 — 메인 관계 동력] {primary}")
        lines.append(f"  정의: {m.get('definition', '')}")
        combos = m.get("common_combinations", [])
        if combos:
            lines.append(f"  자주 결합되는 모티프: {', '.join(combos)}")
        lines.append(f"  ★ 본 회차 집필 시 이 모티프의 동력이 본문 어딘가에 작동해야 함")
    
    # 2순위 모티프 (보조)
    if secondary:
        valid_sec = [s for s in secondary if s in RELATIONSHIP_MOTIFS_DICT]
        if valid_sec:
            lines.append(f"\n[2순위 모티프 — 보조 라인]")
            for s in valid_sec[:4]:  # 최대 4개
                m = RELATIONSHIP_MOTIFS_DICT[s]
                lines.append(f"  · {s}: {m.get('definition', '')[:60]}...")
    
    # 3순위 모티프 (배경)
    if tertiary:
        valid_ter = [t for t in tertiary if t in RELATIONSHIP_MOTIFS_DICT]
        if valid_ter:
            lines.append(f"\n[3순위 모티프 — 배경 음영]")
            lines.append(f"  {', '.join(valid_ter[:4])}")
    
    lines.append("\n[활용 원칙]")
    lines.append("  - 1순위 모티프의 동력이 본 회차 행동의 1차 추동력")
    lines.append("  - 2순위 모티프는 회차마다 분배 — 모든 회차에 다 쓸 필요 없음")
    lines.append("  - 모티프를 정의대로 설명하지 말고 사건과 인물 관계로 구현")
    
    return "\n".join(lines)


def build_character_role_block(characters_full_data, ep_number=0):
    """[v3.0 Phase B] 9종 인물 역할 + 모에 속성 주입.
    
    캐릭터 풀 데이터에서 narrative_role / moe_attributes 필드를 읽어
    각 캐릭터의 역할 행동 패턴·대사 패턴을 프롬프트에 주입.
    
    Args:
        characters_full_data: 캐릭터 풀 데이터.
            dict 형태: {char_name: {"narrative_role": ..., "moe_attributes": [...]}}
            list 형태: [{"name": ..., "narrative_role": ..., "moe_attributes": [...]}, ...]
        ep_number: 현재 회차 번호 (필터링용 — 현재는 모든 캐릭터 출력)
    
    Returns:
        프롬프트 블록 문자열.
    """
    if not characters_full_data or not _V3_CHARACTER_AVAILABLE:
        return ""
    
    # list → 통일된 dict 형태로 변환 (main.py는 list, 단독 호출은 dict 가능)
    if isinstance(characters_full_data, list):
        char_dict = {}
        for char in characters_full_data:
            if isinstance(char, dict) and char.get("name"):
                char_dict[char["name"]] = char
    elif isinstance(characters_full_data, dict):
        char_dict = characters_full_data
    else:
        return ""
    
    if not char_dict:
        return ""
    
    lines = ["[★ 9종 인물 역할 + 모에 속성 — 캐릭터 평면화 방지 ★]"]
    has_content = False
    
    for char_name, char_data in char_dict.items():
        if not isinstance(char_data, dict):
            continue
        
        role = char_data.get("narrative_role", "")
        moe_attrs = char_data.get("moe_attributes", []) or []
        
        if not role and not moe_attrs:
            continue
        
        has_content = True
        lines.append(f"\n[{char_name}]")
        
        # 9종 인물 역할
        if role and role in CHARACTER_ROLE_TAXONOMY:
            r = CHARACTER_ROLE_TAXONOMY[role]
            lines.append(f"  역할: {role} (소속: {r.get('world', '')})")
            lines.append(f"  행동 패턴: {r.get('behavior_pattern', '')}")
            lines.append(f"  대사 패턴: {r.get('dialogue_pattern', '')}")
        
        # 모에 속성
        if moe_attrs:
            attr_descriptions = []
            for attr in moe_attrs:
                # "성격:쿨데레" 형식 파싱
                if ":" in attr:
                    cat, name = attr.split(":", 1)
                    cat = cat.strip()
                    name = name.strip()
                    desc = MOE_ATTRIBUTES_25.get(cat, {}).get(name, "")
                    if desc:
                        attr_descriptions.append(f"{cat}:{name} ({desc})")
                    else:
                        attr_descriptions.append(attr)
                else:
                    attr_descriptions.append(attr)
            if attr_descriptions:
                lines.append(f"  모에 속성: {' / '.join(attr_descriptions)}")
    
    if not has_content:
        return ""
    
    lines.append("\n[활용 원칙]")
    lines.append("  - 한 회차에 동시 등장하는 인물은 반드시 다른 역할로 차별화")
    lines.append("  - 행동 패턴·대사 패턴이 본문 행동/대사에 묻어나야 함")
    lines.append("  - 모에 속성은 첫 등장 시 자연스러운 1~2개 디테일로 표현 (직접 명명 금지)")
    
    return "\n".join(lines)


def build_mind_flow_arc_block(concept, ep_number=0, total_eps=42):
    """[v3.0 Phase B+] 회차별 마음 흐름 단계 자동 추론·주입.
    
    작품 지향(여성향/남성향/중립)을 콘셉트 카드에서 자동 추론하고,
    해당 지향에 맞는 마음 흐름 패턴을 선택해 프롬프트에 주입한다.
    - 여성향: HEROINE_MIND_FLOW_PATTERNS (5단계 — 불안 흔들림 → ... → 자기 회복)
    - 남성향: HERO_MIND_FLOW_PATTERNS  (3단계 — 각성 → 관문 통과 → 목표 진화)
    
    Args:
        concept: 콘셉트 카드 dict
        ep_number: 현재 회차 번호
        total_eps: 작품 전체 회차 수
    
    Returns:
        프롬프트 블록 문자열.
    """
    if not _V3_CHARACTER_AVAILABLE or not ep_number:
        return ""
    
    # 작품 지향 자동 추론 (1차 타겟팅)
    orientation = detect_work_orientation(concept) if concept else "female"
    
    # 주인공 이름 (지향에 따라 다른 필드)
    protagonist_name = ""
    if concept and isinstance(concept, dict):
        if orientation == "male":
            # 남성향은 protagonist.name 우선
            prot = concept.get("protagonist", {})
            if isinstance(prot, dict):
                protagonist_name = prot.get("name", "")
            if not protagonist_name:
                protagonist_name = concept.get("protagonist_name", "")
        else:
            # 여성향은 heroine_name 우선
            protagonist_name = (
                concept.get("heroine_name", "")
                or concept.get("protagonist_name", "")
            )
    
    # 작품 지향에 맞는 단계 추론
    try:
        current_stage = get_stage_for_episode_with_orientation(
            ep_number, total_eps, orientation
        )
    except Exception:
        return ""
    
    if not current_stage:
        return ""
    
    # 작품 지향에 맞는 패턴 dict 가져오기
    pattern_dict = get_mind_flow_for_orientation(orientation)
    stages = pattern_dict.get("stages", [])
    if not stages:
        return ""
    
    current_idx = current_stage.get("stage", 1) - 1
    total_stages = len(stages)  # 여성 5 / 남성 3
    
    # 헤더 — 작품 지향 명시
    orientation_label = {
        "female": "여성향",
        "male":   "남성향",
        "neutral": "중립",
    }.get(orientation, "여성향")
    
    lines = [
        f"[★ 마음 흐름 가이드 — EP{ep_number} (총 {total_eps}회) ★]",
        f"작품 지향: {orientation_label} ({total_stages}단계 흐름)"
    ]
    
    if protagonist_name:
        role_label = "여주" if orientation == "female" else "주인공"
        lines.append(f"{role_label}: {protagonist_name}")
    
    # 현재 단계
    lines.append(
        f"\n[현재 단계] {current_stage.get('stage', '')}/{total_stages}단계 — "
        f"{current_stage.get('name', '')}"
    )
    lines.append(f"  설명: {current_stage.get('description', '')}")
    
    inner = current_stage.get("inner_state_keywords", [])
    if inner:
        lines.append(f"  내면 키워드: {', '.join(inner)}")
    
    behavior = current_stage.get("behavior_keywords", [])
    if behavior:
        lines.append(f"  행동 키워드: {', '.join(behavior)}")
    
    summary = current_stage.get("internal_state_summary", "")
    if summary:
        lines.append(f"  요약: {summary}")
    
    key_principle = current_stage.get("key_principle", "")
    if key_principle:
        lines.append(f"  ★ 핵심 원칙: {key_principle}")
    
    # 이전 단계 (전환의 자연스러움 확보)
    if current_idx > 0:
        prev_stage = stages[current_idx - 1]
        lines.append(
            f"\n[이전 단계] {prev_stage.get('stage', '')}단계 — "
            f"{prev_stage.get('name', '')}"
        )
        lines.append(f"  → 본 회차에서 이전 단계의 잔향이 자연스럽게 남아있어야 함")
    
    # 다음 단계 (전환점 회차일 때 특히 중요)
    if current_idx < total_stages - 1:
        next_stage = stages[current_idx + 1]
        if ep_number < total_eps:
            try:
                next_ep_stage = get_stage_for_episode_with_orientation(
                    ep_number + 1, total_eps, orientation
                )
            except Exception:
                next_ep_stage = None
            if next_ep_stage and next_ep_stage.get("stage") != current_stage.get("stage"):
                lines.append(f"\n[★ 전환점 회차 ★]")
                lines.append(
                    f"  다음 회차에서 {next_stage.get('stage', '')}단계"
                    f"({next_stage.get('name', '')})로 전환됨"
                )
                lines.append(f"  → 본 회차 마지막 부분에 전환의 씨앗이 자연스럽게 심겨야 함")
                lines.append(f"  → 단, 단계 전환을 노골적으로 선언하지 말 것")
    
    # 작품 지향별 활용 원칙
    lines.append("\n[활용 원칙]")
    if orientation == "male":
        lines.append("  - 주인공의 행동·내면은 현재 단계의 키워드와 일치 (완성된 영웅 패턴)")
        lines.append("  - 결단·자신감·전략적 사고가 회차 본문에 묻어나야 함")
        lines.append("  - 갈등은 회차 안에서 빠르게 해결 — 다음 회차로 끌지 말 것 (고구마 함정 회피)")
        lines.append("  - 단계를 학술 용어로 호명하지 말 것 (행동·결정으로 자연스럽게 표현)")
    else:
        lines.append("  - 여주의 모든 행동·내면 묘사는 현재 단계의 키워드와 일치해야 함")
        lines.append("  - 단계를 학술 용어로 호명하지 말 것 (마음 상태로 자연스럽게 표현)")
        lines.append("  - 단계가 바뀌어도 인물의 어조·말투는 일관 유지")
    
    return "\n".join(lines)


def build_market_viability_block(concept, ep_number=0):
    """[v3.0 Phase B] 시장 트리거 5종 강제 충족 가이드.
    
    KOCCA 2024 데이터의 5대 결정 요인(인기/소재/장르/평점/가격)을
    이 회차에서 어떻게 충족할지 가이드 제공.
    
    Args:
        concept: 콘셉트 카드 dict
        ep_number: 현재 회차 번호
    
    Returns:
        프롬프트 블록 문자열.
    """
    if not concept or not _V3_MARKET_AVAILABLE:
        return ""
    
    formula_main = concept.get("formula_main", "")
    movement_code = concept.get("movement_code", "")
    target_tiers = concept.get("target_consumption_tier", []) or []
    
    if not (formula_main or movement_code or target_tiers):
        return ""
    
    lines = ["[★ 시장 트리거 5종 강제 충족 — 결제 전환 보장 ★]"]
    lines.append("\n[2024 시장 데이터 결정 요인 5종]")
    lines.append("  1. 인기순 부합 (45.4%) — 검증된 모티프 차용 표지")
    lines.append("  2. 소재·줄거리 (42.7%) — 호기심 트리거 강도")
    lines.append("  3. 장르 적합 (35.3%) — 장르 코드 명확성")
    lines.append("  4. 평점 예측 (26.1%) — 캐릭터 매력 + 클리프행어")
    lines.append("  5. 가격 가치 (25.4%) — 회차 분량과 정보 밀도")
    
    lines.append("\n[본 회차 충족 가이드]")
    
    # 1. 인기순 부합 — 메인 포뮬러
    if formula_main:
        lines.append(f"  ① 인기순: 메인 포뮬러 '{formula_main}'의 검증된 결합 패턴 표지가 회차에 등장")
    
    # 2. 소재 강도 — 이동 코드 활용
    if movement_code:
        lines.append(f"  ② 소재: 이동 코드 '{movement_code}'에서 오는 '왜 이 사람이?'의 미스터리 강화")
    
    # 3. 장르 적합 — 장르 약속 준수
    genre = concept.get("genre", "")
    if genre:
        lines.append(f"  ③ 장르: '{genre}'의 장르 약속 준수 (장르 코드 흔들림 금지)")
    
    # 4. 평점 예측 — 타겟 소비자
    if target_tiers:
        tier_str = ", ".join(target_tiers[:2])
        lines.append(f"  ④ 평점: 타겟 소비자({tier_str})의 몰입 트리거 강화 — 캐릭터 매력 + 강한 클리프행어")
    
    # 5. 가격 가치 — 정보 밀도
    lines.append("  ⑤ 가격: 회차당 정보 밀도 유지 — 다음 회차 결제 욕구 자극할 정보·감정 임팩트")
    
    lines.append("\n[강제 원칙]")
    lines.append("  - 5개 요인 중 최소 4개를 본 회차에서 충족시킬 것")
    lines.append("  - 트리거를 직접 노출하지 말고 행동·사건·관계로 구현")
    lines.append("  - 마지막 3~5줄은 결제 전환의 핵심 — 가장 큰 정보·감정 임팩트")
    
    return "\n".join(lines)


# =================================================================
# [v3.0 Phase B] 신규 블록 빌더 5종 — END
# =================================================================


def build_episode_write_prompt(episode_plot, characters, style_dna,
                               genre, rating, prev_3_episodes,
                               plant_map_relevant, formula_tags=None,
                               producer_note="", style_strength="중",
                               target_length=5200, platform="카카오페이지",
                               primary_motif="", secondary_motif="",
                               target_persona="",
                               concept_dict=None,
                               ep_number=0, total_eps=50,
                               intimacy_schedule=None,
                               narrative_tone="",
                               profession_blocks="",
                               characters_full_data=None,
                               char_first_eps=None,
                               scene_types=None,
                               # v3.0 Phase B — 신규 블록 빌더 활성화 플래그
                               # 인자가 비어있어도 v2.6.4 동작 유지 (호환성)
                               use_v3_blocks=True):
    """회차 원고 집필.
    
    v2.6.4: 컨텍스트 인식 묘사 (첫 등장 풀/재등장 압축/씬 타입 차등)
    v3.0:   Phase A 데이터 기반 5종 블록 추가 주입
            (formula_strategy / motif / character_role / mind_flow_arc / market_viability)
            concept_dict와 characters_full_data가 v3.0 신규 필드를 갖고 있으면 자동 주입.
            v2.6.4 호환 — 신규 필드가 비어있으면 v2.6.4와 동일 동작.
    """
    tags_block = get_formula_block(formula_tags or [])
    motif_block = get_motif_block(primary_motif, secondary_motif)
    persona_block = get_reader_persona_block(target_persona)
    # v2.4 신규
    character_flags = get_character_flags_block(concept_dict or {})
    pacing_block = get_pacing_block(ep_number, total_eps) if ep_number and total_eps else ""
    intimacy_directive = get_intimacy_schedule_for_ep(intimacy_schedule, ep_number) if ep_number else ""
    # v2.5 신규
    tone_block = get_narrative_tone_block(narrative_tone) if narrative_tone else ""
    # v2.6 신규 — 직업 블록
    prof_section = f"\n\n{profession_blocks}\n" if profession_blocks else ""
    # v2.6.4 신규 — 컨텍스트 인식 묘사 블록 (첫 등장 풀 / 재등장 압축 / 씬 타입 차등)
    if characters_full_data and char_first_eps is not None and scene_types is not None:
        contextual_desc_block = build_contextual_description_block(
            characters_full_data=characters_full_data,
            ep_number=ep_number,
            char_first_eps=char_first_eps,
            scene_types=scene_types,
            genre=genre,
        )
    elif characters_full_data:
        # v2.6.3 폴백 — 컨텍스트 인자가 없으면 기존 풀 데이터 블록
        contextual_desc_block = build_character_full_block(characters_full_data)
    else:
        contextual_desc_block = ""
    
    # v3.0 Phase B 신규 — 기획↔집필 연결 강제 5종 블록
    # concept_dict / characters_full_data에 v3.0 신규 필드가 있을 때만 활성화.
    # 비어있으면 빈 문자열 반환 → v2.6.4와 동일 동작 (호환성 유지)
    if use_v3_blocks and concept_dict:
        v3_formula_block = build_formula_strategy_block(concept_dict)
        v3_motif_block_v3 = build_motif_block(concept_dict, ep_number=ep_number)
        v3_market_block = build_market_viability_block(concept_dict, ep_number=ep_number)
        v3_mind_flow_block = build_mind_flow_arc_block(
            concept_dict, ep_number=ep_number, total_eps=total_eps
        )
    else:
        v3_formula_block = ""
        v3_motif_block_v3 = ""
        v3_market_block = ""
        v3_mind_flow_block = ""
    
    if use_v3_blocks and characters_full_data:
        v3_char_role_block = build_character_role_block(
            characters_full_data, ep_number=ep_number
        )
    else:
        v3_char_role_block = ""
    
    lp = get_platform_length(platform)
    min_len = lp["min"]
    max_len = lp["max"]
    target_len = lp["target"]
    tol = lp["tolerance"]
    # v2.6.2: 구조 분배 자동 계산
    intro_min = int(target_len * 0.13)   # 도입 13%
    intro_max = int(target_len * 0.17)   # 도입 17%
    dev_min = int(target_len * 0.65)     # 전개 65%
    dev_max = int(target_len * 0.75)     # 전개 75%
    hook_min = int(target_len * 0.13)    # 훅 13%
    hook_max = int(target_len * 0.17)    # 훅 17%

    return f"""[TASK] 웹소설 EP 원고 집필 — 플랫폼: {platform}

{tone_block}

{_genre_block(genre)}

{tags_block}

{motif_block}

{persona_block}

{character_flags}
{prof_section}

{contextual_desc_block}

{v3_char_role_block}

{v3_formula_block}

{v3_motif_block_v3}

{v3_mind_flow_block}

{v3_market_block}

{MISE_EN_SCENE_CHECKLIST}

{pacing_block}

{intimacy_directive}

{_rating_block(rating)}

{NARRATIVE_FUNCTION_CHECK}

{FLOW_INDUCTION_RULES}

{AI_ANTI_PATTERN}

{WEB_NOVEL_PROSE_RULES}

{EPISODE_STRUCTURE}

{EPISODE_TITLE_RULES}

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
★★★ 분량 절대 규칙 ★★★
- 본문 분량: 최소 {min_len}자 이상, 목표 {target_len}자, 최대 {max_len}자 (★공백 포함, 회차 제목 제외★)
- {min_len}자 미만은 "분량 미달"로 실패 처리됨. 절대 짧게 끝내지 말 것.
- 한 씬당 평균 1,200~1,700자 × 3~4씬 = 4,500~6,500자
- 짧게 요약하지 말고 장면을 충실히 전개할 것
- 인물의 내면 독백·감각 묘사·디테일을 충분히 풀어쓸 것
- 대사 사이사이 비언어적 신호(시선·호흡·손짓·정적)를 묘사로 채울 것

[구조 분배 — {target_len}자 기준]
- 플랫폼: {platform} (표준 {min_len}~{max_len}자)
- 도입(15%): {intro_min}~{intro_max}자 — 직전 회차 연결 + 본 회차 진입
- 전개(70%): {dev_min}~{dev_max}자 — 3~4씬 충실 전개
- 훅(15%): {hook_min}~{hook_max}자 — 클리프행어 + 다음 회차 예고

[집필 원칙]
- 클리프행어는 플롯 지정 유형/내용 준수
- 리캡은 자연스럽게 녹이기 (직접 요약 금지)
- 대사 비율 40% 이상
- ★ 웹소설식 줄바꿈: 문장마다 줄바꿈, 문단(2~4줄) 사이 빈 줄 하나
- ★ 대사-지문 반드시 분리 (영어권식 "said" 뒤붙이기 금지)
- AI Anti-Pattern A1~A14 준수
- 마지막 3~5줄이 가장 중요

[분량 미달 방지 체크리스트]
□ 각 씬의 시작 묘사 충분한가 (배경·인물 진입)
□ 대사 직후 반응(표정·생각·행동) 묘사 있는가
□ 감각적 디테일(시각·청각·후각·촉각) 풀어 썼는가
□ 회상·복선 자연스럽게 녹였는가
□ 마지막 훅 전에 충분한 빌드업 있는가

[출력 형식 — 반드시 지킬 것]
첫 줄: 회차 제목만 (예: "EP17. 가면 뒤의 남자")
둘째 줄: 빈 줄
셋째 줄부터: 본문

★ 작품 제목·IP 홀더 인장은 회차 집필 후 코드가 자동 삽입함. LLM은 회차 제목 + 본문만 출력.

JSON/마크다운/주석/설명 금지. 순수 원고 텍스트만.
""".strip()


def build_rating_convert_prompt(episode_19_text):
    """19금 → 15금 변환."""
    return f"""[TASK] 19금 원고를 15금으로 변환

{RATING_CONVERSION_RULES}

{RATING_15}

[변환 원칙]
1. 단순 삭제 금지
2. 서사적 기능 유지
3. 분량 5,000~5,500자 ± 500자 유지
4. 캐릭터 관계 온도 변화 동일
5. 클리프행어 변경 금지
6. ★ 회차 제목(첫 줄)은 그대로 유지

[19금 원본]
{episode_19_text}

[출력]
15금 변환 원고 텍스트만. 첫 줄은 회차 제목 유지.
""".strip()


def build_alternative_scene_prompt(episode_19_text, scene_description,
                                   characters, genre):
    """15금 대체 씬 생성 (B안)."""
    return f"""[TASK] 15금 대체 씬 생성

19금 관능 씬의 서사적 기능(관계 진전/신뢰 구축/취약성 노출)을
15금 기준 다른 씬으로 재구성.

{_genre_block(genre)}
{RATING_15}

[관능 씬의 서사적 기능]
{scene_description}

[캐릭터]
{characters}

[19금 원본 참고]
{episode_19_text}

[대체 작법]
- 정사 대신: 비밀 공유, 위기 속 보호, 진심 고백, 일상 변화 중 선택
- 같은 감정 결과를 다른 경로로
- 분량: 1,500~2,500자

[출력]
15금 대체 씬 텍스트만.
""".strip()


def build_quality_check_prompt(episode_text, episode_number, characters,
                               plant_map, prev_summary, rating):
    """품질 체크."""
    return f"""[TASK] EP{episode_number} 품질 체크

[원고]
{episode_text}

[캐릭터 바이블]
{characters}

[떡밥 맵]
{plant_map}

[이전 회차 요약]
{prev_summary}

[JSON 출력]
{{
  "episode": {episode_number},
  "length": 0,
  "length_pass": true,
  "ai_antipattern_violations": [{{"rule":"A1","location":"","suggestion":""}}],
  "cliffhanger_check": {{"exists":true,"type":"","strength":"상|중|하"}},
  "character_consistency": [{{"character":"","issue":""}}],
  "plant_payoff_check": [{{"id":"","status":"정상|누락|시점오류"}}],
  "dialogue_ratio": 0.0,
  "rating_compliance": {{"target":"{rating}금","pass":true,"violations":[]}},
  "recap_naturalness": "자연스러움|어색함|직접요약",
  "overall_score": 0,
  "top_3_improvements": ["","",""]
}}""".strip()


def build_episode_summary_prompt(episode_text, episode_number):
    """완료 회차 요약 (토큰 관리용)."""
    return f"""다음 EP{episode_number} 원고를 200자 이내 요약.
포함: 핵심 사건, 인물 관계 변화, 공개된 정보, 클리프행어.

[원고]
{episode_text}

[출력]
200자 이내 요약 텍스트만.
""".strip()


# =================================================================
# [v3.0 Phase C] 자가 검수 빌더 — 5축 종합 + 재료 활용 LLM 검수
# =================================================================

def build_validation_prompt(
    episode_text, ep_number, concept_dict, character_bible_str,
    rule_validation_result=None, total_eps=42, prev_summary="",
):
    """[v3.0 Phase C] 회차 자가 검수 — Sonnet이 5축 채점 + 재료 활용 리포트 생성.
    
    engine_validator.py의 1차 텍스트 매칭 결과(rule_validation_result)를
    참고로 Sonnet이 더 깊이 있는 검수를 수행한다.
    
    Args:
        episode_text: 회차 본문
        ep_number: 회차 번호
        concept_dict: 콘셉트 카드 (v3.0 신규 필드 포함)
        character_bible_str: 캐릭터 바이블 JSON 문자열
        rule_validation_result: engine_validator의 1차 검수 결과 (참고용)
        total_eps: 작품 전체 회차 수
        prev_summary: 직전 회차 요약 (누적 흐름 점검용)
    
    Returns:
        Sonnet 호출용 프롬프트 문자열.
    """
    import json as _json
    
    concept_str = _json.dumps(concept_dict, ensure_ascii=False, indent=2)[:2500] if concept_dict else "{}"
    
    # 1차 검수 결과 요약 (있으면)
    rule_section = ""
    if rule_validation_result:
        used = rule_validation_result.get("used", [])
        weak = rule_validation_result.get("weak", [])
        missing = rule_validation_result.get("missing", [])
        rule_section = f"""

[1차 패턴 매칭 검수 결과 — 참고용]
사용된 재료 ({len(used)}): {'; '.join(used[:10]) if used else '없음'}
약하게 반영 ({len(weak)}): {'; '.join(weak[:10]) if weak else '없음'}
누락 ({len(missing)}): {'; '.join(missing[:10]) if missing else '없음'}

위 결과는 단순 텍스트 매칭 결과이므로, 본문 맥락을 보고 정확하게 재판정하세요."""
    
    return f"""[TASK] EP{ep_number} 자가 검수 (v3.0 Phase C)
당신은 한국 웹소설 시장 베테랑 편집장입니다. 다음 회차를 5축으로 채점하세요.

[회차 본문]
{episode_text}

[v3.0 콘셉트 카드 — 기획 단계에서 결정된 재료]
{concept_str}

[캐릭터 바이블]
{character_bible_str[:2500]}

[직전 회차 요약 — 누적 흐름 점검용]
{prev_summary[:600] if prev_summary else '(첫 회차 또는 정보 없음)'}
{rule_section}

[5축 채점 기준]
1. **MATERIAL_USAGE (재료 활용 / critical)**: 콘셉트 카드의 v3.0 재료(formula_main, formula_sub, relationship_motifs, movement_code 등)가 본문에 실제로 작동하는가. 표지가 행동·풍경·관계로 구현됐는가, 아니면 명시적 언급에 그쳤는가.

2. **CHARACTER_CONSISTENCY (캐릭터 차별화 / critical)**: 9종 인물 역할(narrative_role)이 본문 행동·대사에 묻어나는가. 다중 인물 등장 회차에서 각자 식별 가능한가. 모에 속성(moe_attributes)이 자연스럽게 표현됐는가.

3. **CLIFFHANGER_STRENGTH (클리프행어 강도)**: 회차 끝 임팩트가 강한가. Reveal/Tears/Threat/Choice/Reversal/Slap/Arrival 7유형 중 무엇인가. 결제 전환 동력이 있는가.

4. **MISE_EN_SCENE (묘사·장면)**: 분량 적정한가(4500~6500자 권장). 감각 묘사가 풍부한가. 대사 비율이 적정한가. 첫 등장/재등장 묘사 차등이 적절한가.

5. **MARKET_VIABILITY (시장 트리거)**: 5대 결정 요인(인기/소재/장르/평점/가격) 중 몇 개가 충족됐는가. 타겟 소비자 분화의 결제 트리거가 발현됐는가.

[채점 원칙]
- 점수는 0~100 정수
- critical 축(MATERIAL_USAGE, CHARACTER_CONSISTENCY)은 55점 미만이면 자동 REDO
- 종합 75점 이상 = PASS, 65~74 = WARN, 64 이하 = REDO
- 재료를 명시적으로 호명하면 감점 (행동·관계로 보여야 함)

[JSON 출력 — 반드시 이 구조 정확히]
{{
  "episode": {ep_number},
  "axes": {{
    "MATERIAL_USAGE": {{
      "score": 0,
      "verdict": "한 줄 평가",
      "used_materials": ["사용된 v3.0 재료 1", "재료 2"],
      "weak_materials": ["약하게 반영된 재료"],
      "missing_materials": ["누락된 재료"],
      "critical_missing": ["재집필 트리거가 될 핵심 누락"]
    }},
    "CHARACTER_CONSISTENCY": {{
      "score": 0,
      "verdict": "한 줄 평가",
      "differentiated_chars": ["역할 잘 드러난 캐릭터"],
      "flat_chars": ["평면적으로 그려진 캐릭터"],
      "issues": ["구체적 문제점"]
    }},
    "CLIFFHANGER_STRENGTH": {{
      "score": 0,
      "verdict": "한 줄 평가",
      "type_detected": "Reveal|Tears|Threat|Choice|Reversal|Slap|Arrival|None",
      "impact": "강|중|약"
    }},
    "MISE_EN_SCENE": {{
      "score": 0,
      "verdict": "한 줄 평가",
      "length_pass": true,
      "issues": []
    }},
    "MARKET_VIABILITY": {{
      "score": 0,
      "verdict": "한 줄 평가",
      "triggers_met": "0/5",
      "weak_triggers": []
    }}
  }},
  "overall_score": 0,
  "grade": "PASS|WARN|REDO",
  "verdict_summary": "두 줄 종합 평가",
  "redo_targets": ["재집필 시 우선 보강할 부분 1", "보강할 부분 2"],
  "cumulative_flow_check": {{
    "prev_consistency": "이전 회차와의 흐름 일관성 (자연|어색|단절)",
    "transition_seed_planted": true
  }}
}}""".strip()


def build_episode_redo_prompt(
    original_text, ep_number, validation_result,
    concept_dict, character_bible_str, ep_plot,
    target_length=5200, rating="15"
):
    """[v3.0 Phase C] 회차 재집필 — 검수 결과의 redo_targets만 핀포인트 보강.
    
    전체 재집필이 아니라, validation_result의 redo_targets·critical_missing을
    중심으로 본문을 보강하는 핀포인트 재집필.
    
    Args:
        original_text: 원본 회차 본문
        ep_number: 회차 번호
        validation_result: build_validation_prompt() 결과 dict
        concept_dict: 콘셉트 카드
        character_bible_str: 캐릭터 바이블 JSON 문자열
        ep_plot: 회차 플롯
        target_length: 목표 분량
        rating: 수위 (15/19)
    
    Returns:
        Opus 호출용 프롬프트 문자열.
    """
    import json as _json
    
    concept_str = _json.dumps(concept_dict, ensure_ascii=False, indent=2)[:2500] if concept_dict else "{}"
    val_str = _json.dumps(validation_result, ensure_ascii=False, indent=2)[:3000] if validation_result else "{}"
    
    # 재집필 우선순위 추출
    redo_targets = validation_result.get("redo_targets", []) if validation_result else []
    critical_missing = []
    if validation_result:
        mu_axis = validation_result.get("axes", {}).get("MATERIAL_USAGE", {})
        critical_missing = mu_axis.get("critical_missing", [])
    
    redo_section = ""
    if redo_targets or critical_missing:
        redo_section = "\n[★ 재집필 핀포인트 — 반드시 보강할 항목]\n"
        for i, t in enumerate(redo_targets[:5], 1):
            redo_section += f"{i}. {t}\n"
        if critical_missing:
            redo_section += "\n[핵심 누락 재료 — 반드시 본문에 반영]\n"
            for m in critical_missing[:5]:
                redo_section += f"  ❌ {m}\n"
    
    return f"""[TASK] EP{ep_number} 핀포인트 재집필
이전 회차 본문이 자가 검수에서 보강 권장 판정을 받았습니다. 핵심 골격은 유지하되 검수 지적 사항을 본문에 녹여 재집필하세요.

[원본 본문]
{original_text[:8000]}

[자가 검수 결과 요약]
{val_str}
{redo_section}

[v3.0 콘셉트 카드]
{concept_str}

[회차 플롯]
{ep_plot[:1500] if ep_plot else '(별도 플롯 없음 — 원본 본문의 전개 유지)'}

[캐릭터 바이블]
{character_bible_str[:2000]}

[재집필 원칙]
- 원본의 좋은 부분(대사·장면·전개)은 그대로 유지
- 위 핀포인트만 본문 안에 자연스럽게 녹임
- 재료를 명시적으로 호명하지 말고 행동·풍경·관계로 보여줄 것
- 분량 목표: {target_length}자 (±500자)
- 수위: {rating}금 등급 준수

[출력]
재집필된 회차 본문 (제목·회차 번호 포함, 본문만).
""".strip()


# =================================================================
# [v3.0 Phase C END] 자가 검수 빌더
# =================================================================
