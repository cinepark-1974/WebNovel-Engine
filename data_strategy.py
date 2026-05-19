"""
data_strategy.py — Engine v3.4
================================
창작 전략·문체·세계 구축 데이터셋

수록 데이터 (v3.0):
- ROFAN_CREATION_STRATEGY — 로판 3종 세부장르별 창작 전략
- HETEROTOPIA_FRAME — 헤테로토피아(낭만적 이세계) 구축 사양
- POV_BLENDING_GUIDE — 시점 혼용 가이드 (비개성적 문체)
- READER_DESIRES_ROFAN — 로판 3대 독자 욕망 (보조 가이드)

신규 데이터 (v3.4):
- FIRST_SCENE_TYPES_9 — 첫 장면 9가지 유형 (백종인 2022 [표 13/14])
- MEDIA_CONVERSION_RATIO — 매체 전환 비율 (웹툰 5화 = 드라마 1편)

원칙:
- 작품 콘셉트의 sub_genre 필드에 따라 자동 적용 가능
- 4명의 전남편들에는 "치유물 전략 + 헤테로토피아(빙의 후 카페 공간)" 부분 적용
- POV 혼용 가이드는 모든 작품에 공통 적용 (웹소설 비개성적 문체)
- 첫 장면 9유형: EP1 빌더에 강제 선택지로 주입
- 매체 전환 비율: 작품이 OTT 시리즈 전환을 염두에 둘 경우 활용

학술 출처 (v3.4 추가분):
- 백종인 (2022), 공주대 만화학과 석사학위논문
  "드라마화된 로맨스 웹툰의 서사와 플롯에 관한 연구"
- 방현석 (2013), "서사패턴 959 (이야기를 완성하는)"

사용 예시:
    from data_strategy import ROFAN_CREATION_STRATEGY, FIRST_SCENE_TYPES_9
    strategy = ROFAN_CREATION_STRATEGY["치유물"]
    scene_types = list(FIRST_SCENE_TYPES_9.keys())
"""


# ============================================================================
# ROFAN_CREATION_STRATEGY — 로판 3종 세부장르별 창작 전략
# ============================================================================
# 용도: 로판 작품 기획 시 sub_genre 필드(성장물/복수물/치유물)에 따라 자동 주입.
#       로판이 아닌 작품(현대 빙의 치정 등)에도 부분 차용 가능.

ROFAN_CREATION_STRATEGY = {
    "성장물": {
        "core_strategy": "성장을 지연하는 성장 서사",
        "key_principle": "주인공이 한 번에 성장하지 않고, 성장 → 시련 → 후퇴 → 재성장 반복",
        "story_logic": [
            "초기 무능·미숙한 여주",
            "→ 작은 성취 (1차 성장)",
            "→ 강력한 시련 (성장 부정)",
            "→ 후퇴 또는 정체",
            "→ 새로운 깨달음 (2차 성장)",
            "→ 반복 (성장의 계단식 구조)"
        ],
        "core_satisfaction": "지연된 성장의 누적적 카타르시스",
        "key_devices": [
            "성장의 단계별 시각화 (능력·지위·인간관계)",
            "시련의 점층적 강화",
            "조력자 점진적 등장",
            "회차마다 작은 성취 또는 작은 후퇴"
        ],
        "anti_patterns": [
            "한 회차에 성장 완성 금지",
            "시련 없는 직선적 성장 금지",
            "성장 동력이 외부 능력(시스템·치트)에만 의존하는 것 금지"
        ],
        "applicable_4husbands": False,
    },
    
    "복수물": {
        "core_strategy": "복수를 가속하는 회귀 서사",
        "key_principle": "회귀 후 즉각적 복수 시작. 복수 동력은 미래 지식. 사이다 우선",
        "story_logic": [
            "회귀 직전의 처참한 결말 (프롤로그)",
            "→ 회귀 (또는 빙의·환생)",
            "→ 미래 지식 활용 즉각적 행동",
            "→ 1차 표적 처단 (사이다)",
            "→ 더 큰 표적 등장",
            "→ 복수 단계 누적",
            "→ 최종 표적 처단 + 새 삶 안착"
        ],
        "core_satisfaction": "사이다의 즉각성 + 누적성",
        "key_devices": [
            "프롤로그에서 처참한 회귀 직전 상황 묘사",
            "회귀 직후 빠른 행동 개시 (망설임 최소화)",
            "단계별 표적 명확화",
            "정보 비대칭성(미래 지식)의 명시적 활용",
            "복수 후 약자 구원 장면"
        ],
        "anti_patterns": [
            "회귀 후 망설임 길게 끄는 것 금지 (고구마)",
            "복수 동력이 약하게 묘사되는 것 금지",
            "최종 표적이 단순 강자로만 그려지는 것 금지 (시험 부과 기능 필요)"
        ],
        "applicable_4husbands": False,
    },
    
    "치유물": {
        "core_strategy": "자립을 유도하는 애정 서사",
        "key_principle": "남주의 애정이 여주의 자립을 돕는 도구. 의존이 아니라 자립을 향함",
        "story_logic": [
            "트라우마 또는 결핍을 가진 여주",
            "→ 남주의 일관된 애정 등장",
            "→ 여주의 경계와 거부",
            "→ 남주의 거리 유지 + 신뢰 누적",
            "→ 여주의 작은 자기 회복 시도",
            "→ 자립의 누적 (남주는 도구가 아니라 동반자)",
            "→ 자기 정체성 회복 + 사랑의 수용"
        ],
        "core_satisfaction": "회복의 점진성 + 자기 발견",
        "key_devices": [
            "여주의 트라우마 단계별 노출 (한 번에 다 풀지 않음)",
            "남주의 무조건적 신뢰 + 거리 유지의 조화",
            "여주의 자기 결정 장면 강조 (남주가 대신 결정 안 함)",
            "조용한 일상 묘사 비중 높임",
            "치유의 매개 공간 활용 (카페·작업실·정원 등)"
        ],
        "anti_patterns": [
            "남주가 모든 문제를 해결하는 것 금지 (자립 부정)",
            "트라우마를 한 회차에 다 풀어내는 것 금지",
            "남주의 일방적 구원 서사 금지"
        ],
        "applicable_4husbands": True,  # 부분 적용
        "4husbands_application": (
            "한시호의 자립·정체성 회복 라인에 차용. "
            "김지훈의 애정은 한시호의 '자기 자신으로 돌아가기'를 돕는 도구. "
            "EP37-EP42에서 한시호가 김지훈의 도움으로 한시호로 돌아가는 흐름과 일치."
        ),
    },
}


# ============================================================================
# HETEROTOPIA_FRAME — 헤테로토피아(낭만적 이세계) 구축 사양
# ============================================================================
# 핵심 개념:
# 헤테로토피아는 '현실 안에 존재하지만 일상과 분리된 공간'. 웹소설에서는 여주의
# 일상적 고통이 일시적으로 차단되는 안전한 공간으로 작동한다. 카페·정원·작업실·
# 호텔 스위트룸·서재·바닷가 빌라 등이 전형적 사례.
#
# 적용 원칙:
# - 모든 로맨스 작품에 1개 이상의 헤테로토피아 권장
# - 고수위 로맨스에서는 필수 (성애 장면이 일상의 죄책감으로부터 분리된 공간 필요)
# - 4명의 전남편들 → 한시호의 카페가 헤테로토피아

HETEROTOPIA_FRAME = {
    "definition": (
        "현실 안에 존재하지만 일상의 규범·고통과 분리된 공간. "
        "여주의 트라우마·외로움·정체성 흔들림이 일시적으로 차단되고, "
        "자기 자신으로 존재할 수 있는 영역."
    ),
    
    "construction_elements": [
        "공간의 경계 명시 (들어가는 행위 = 의례)",
        "외부 시간과 다른 시간 흐름 (느림·정지·반복)",
        "외부에 알려지지 않은 비밀스러움 또는 폐쇄성",
        "여주가 통제권을 가진 공간 (또는 안전을 보장받는 공간)",
        "감각적 디테일의 풍부함 (향·소리·온도·질감)"
    ],
    
    "typical_spaces": {
        "카페": "여주가 운영 또는 단골인 공간. 단골손님과의 만남 매개",
        "정원_온실": "외부와 차단된 식물 공간. 시간이 느리게 흐름",
        "작업실_서재": "창조 활동의 공간. 자기 정체성과 직결",
        "호텔_스위트룸": "익명성 + 고급스러움. 일탈적 만남의 무대",
        "별장_바닷가_빌라": "도시 일상으로부터의 물리적 분리",
        "오래된 서점·갤러리": "과거의 시간이 현재에 침투하는 공간"
    },
    
    "function_in_narrative": [
        "여주의 일상적 고통이 일시 정지되는 회복 공간",
        "남주와의 사적 만남이 가능한 무대 (외부 시선 차단)",
        "성애 장면의 자연스러운 배경 (일상의 죄책감 분리)",
        "비밀의 발견·고백·재회의 장소"
    ],
    
    "key_devices": [
        "공간 진입 의례 묘사 (문 열림·계단 오름·향 변화)",
        "외부와 다른 감각 강조 (조명·온도·소리·냄새)",
        "공간 안에서의 시간 감각 변형 ('얼마나 있었는지 모르겠다')",
        "공간이 인물의 마음을 비추는 거울로 기능",
        "공간을 나가는 순간의 단절감 묘사"
    ],
    
    "anti_patterns": [
        "공간을 단순 배경으로만 사용 금지 (서사적 기능 필수)",
        "헤테로토피아가 너무 자주 등장해 일상화되는 것 경계",
        "공간 묘사가 과잉 정보로 흐르는 것 금지 (감각 디테일 우선)"
    ],
    
    "applicable_4husbands": (
        "한시호의 카페가 핵심 헤테로토피아. "
        "유빈의 일상(전남편들·갤러리·소문)으로부터 분리된 공간이며, "
        "김지훈과의 만남이 이루어지는 무대. "
        "EP3에서 김지훈이 카페에 단골손님으로 등장하는 순간이 "
        "헤테로토피아 진입 의례."
    ),
}


# ============================================================================
# POV_BLENDING_GUIDE — 시점 혼용 가이드
# ============================================================================
# 한국 웹소설의 비개성적 문체 특성:
# - 1인칭과 3인칭이 자주 혼용됨
# - 시점 변화가 회차 안에서도 일어남
# - 독자는 시점 전환에 익숙하므로 매끄럽기만 하면 거부감 없음

POV_BLENDING_GUIDE = {
    "default_pov": {
        "여성향_치정_빙의": "1인칭 (여주) 70% + 3인칭 객관 30%",
        "여성향_로판": "1인칭 (여주) 60% + 3인칭 객관 40%",
        "남성향_헌터물_재벌물": "3인칭 객관 70% + 1인칭 (남주 회상) 30%",
        "여성향_고수위": "1인칭 (여주) 80% + 남주 시점 회상 20%",
        "남성향_회귀물": "1인칭 (남주) 50% + 3인칭 객관 50%"
    },
    
    "blending_rules": {
        "기본_원칙": "한 씬 안에서 시점 통일. 다른 씬 진입 시 전환 자연스럽게.",
        "전환_시점": [
            "씬 전환과 동시에 (씬 구분 ───)",
            "회상 진입 시 (다른 인물 시점)",
            "급박한 사건의 객관 묘사 필요 시",
            "남주의 마음을 짧게 노출할 때"
        ],
        "전환_금지": [
            "한 문단 안에서 시점 전환 금지",
            "대화 도중 시점 전환 금지",
            "정보 누설 목적의 시점 전환 금지 (서사적 필연성 필요)"
        ]
    },
    
    "free_indirect_discourse": {
        "definition": "자유간접화법. 3인칭 서술 안에 인물의 내면이 직접 침투",
        "example": "그녀는 카운터를 닦았다. 손이 떨렸다. 왜 하필 오늘이지.",
        "function": "1인칭의 친밀성 + 3인칭의 객관성 동시 확보",
        "frequency": "여성향 작품에서 회차당 5~10회 권장"
    },
    
    "voice_consistency": {
        "원칙": "시점이 바뀌어도 인물의 목소리(어조·어휘)는 일관 유지",
        "체크리스트": [
            "여주 1인칭의 어휘가 여주 대사 어휘와 일치",
            "남주 시점의 어휘가 남주 대사 어휘와 일치",
            "3인칭 객관 시점은 작가 목소리(작품 기본 톤) 유지"
        ]
    },
    
    "anti_patterns": [
        "P1 — 시점 혼란: 한 문단에서 시점이 두 번 이상 바뀜",
        "P2 — 무신호 전환: 시점 전환 표지(씬 구분, 시간 변화) 없이 갑작스럽게 전환",
        "P3 — 목소리 붕괴: 시점이 바뀌면서 인물의 어조가 갑자기 달라짐",
        "P4 — 정보 누설형 전환: 독자에게 정보를 흘리려는 목적만으로 시점 전환"
    ],
}


# ============================================================================
# READER_DESIRES_ROFAN — 로판 3대 독자 욕망 (보조 가이드)
# ============================================================================
# 로판 작품 기획 시 욕망 충족 트리거로 활용
# 4명의 전남편들 — 로판이 아니므로 직접 적용 안 됨, 부분 차용만

READER_DESIRES_ROFAN = {
    "여성성_긍정": {
        "description": "여주가 여성으로서의 자기 정체성을 긍정하는 서사",
        "key_devices": [
            "여주가 자기 외모·감성·취향을 부끄러워하지 않음",
            "전형적 '여성성'이 약점이 아니라 강점으로 작동",
            "'여자라서'의 부정적 시선을 작품 안에서 반박"
        ],
        "platform_strength": ["카카오페이지", "리디"],
    },
    
    "주체적_여성상": {
        "description": "여주가 자기 인생의 주체로 행동하는 서사",
        "key_devices": [
            "여주의 결정으로 사건이 진행됨 (수동적 피해자 아님)",
            "남주의 도움 없이 해결하는 장면 비중",
            "여주의 사회적 성취 가시화 (사업·예술·정치)"
        ],
        "platform_strength": ["리디", "카카오페이지"],
    },
    
    "공정한_평가": {
        "description": "여주의 능력이 정당하게 평가받는 서사",
        "key_devices": [
            "여주의 실력이 결과로 증명됨",
            "편견에 의한 무시가 결국 깨짐",
            "조력자가 여주의 가치를 알아봄"
        ],
        "platform_strength": ["카카오페이지", "리디", "네이버시리즈"],
    },
}


# ============================================================================
# 헬퍼 함수
# ============================================================================

def get_strategy_for_subgenre(sub_genre: str) -> dict:
    """세부장르 키로 창작 전략 반환."""
    return ROFAN_CREATION_STRATEGY.get(sub_genre, {})


def get_pov_default(genre_orientation: str) -> str:
    """장르 지향에 따른 기본 시점 권장."""
    return POV_BLENDING_GUIDE["default_pov"].get(genre_orientation, "")


def get_heterotopia_devices() -> list:
    """헤테로토피아 핵심 장치 키워드 반환 (집필 프롬프트 주입용)."""
    return HETEROTOPIA_FRAME["key_devices"]


def is_4husbands_applicable_strategy(strategy_name: str) -> bool:
    """해당 창작 전략이 4명의 전남편들에 적용 가능한지 판정."""
    strategy = ROFAN_CREATION_STRATEGY.get(strategy_name)
    if not strategy:
        return False
    return strategy.get("applicable_4husbands", False)


# ============================================================================
# FIRST_SCENE_TYPES_9 — 첫 장면 9가지 유형 (v3.4 신규)
# ============================================================================
# 출처: 백종인 (2022) [표 13/14], 방현석 (2013) 《서사패턴 959》
# 용도: EP1 빌더에서 작가가 첫 장면 유형을 명시적으로 선택하여 도입부 흡인력 강화
# 강제 주입: EP1 집필 프롬프트에 선택된 유형의 정의·디바이스가 자동 주입됨

FIRST_SCENE_TYPES_9 = {
    # ─── 독자를 마중하는 5유형 (현재 → 픽션) ──────────────────────
    "인물제시형": {
        "category": "독자를_마중",
        "definition": "인물의 성격을 단적으로 알 수 있는 장면을 보여주며, 앞으로 벌어질 사건을 짐작하게 하고 사건의 전개에 개연성을 부여",
        "key_devices": [
            "인물의 특징적 습관·말투·외모를 한 장면에 응축",
            "그 인물이 처한 상황 한 컷",
            "독자가 '이 인물이 누구인지' 즉시 파악 가능",
        ],
        "example": "내 ID는 강남미인 — 강미래가 과거 못생긴 외모로 거절당하던 장면부터 시작",
        "best_for_genre": ["현대로맨스", "치정로맨스", "로판"],
        "best_for_4husbands": True,  # 환생 정체성 작품 — 시호 47년 직장인 어법 도입 적합
    },
    "사건발생형": {
        "category": "독자를_유혹",
        "definition": "갑작스럽게 발생한 사건을 먼저 제시. 독자는 사건에 매혹되어 자연스럽게 다음 페이지로 시선을 옮김",
        "key_devices": [
            "1단락 안에 사건 발생",
            "독자가 '무슨 일이지?' 즉시 의문",
            "사건의 발단·전개·중단이 명확",
        ],
        "example": "김비서가 왜 그럴까 — 김비서가 그만둔다는 사건이 발생하고 이영준의 심리부터 시작",
        "best_for_genre": ["스릴러", "현대로맨스", "치정로맨스"],
    },
    "일상제시형": {
        "category": "독자를_마중",
        "definition": "인물이 어떤 사건에 던져지기 전의 모습을 객관적인 시선으로 묘사",
        "key_devices": [
            "평범한 일상의 한 컷",
            "그 일상에 작은 균열을 예고하는 디테일",
            "독자가 인물의 평소 모습에 공감",
        ],
        "example": "저녁 같이 드실래요 — 사건 일어나기 전 도희의 일상에서 시작",
        "best_for_genre": ["현대로맨스", "일상물"],
    },
    "배경제시형": {
        "category": "독자를_마중",
        "definition": "사건이 벌어질 시공간에 대한 설명과 묘사",
        "key_devices": [
            "압도적 배경 스케일",
            "세계관의 규모를 한 단락에 응축",
            "독자가 '이 세계로 들어가고 싶다'고 느낌",
        ],
        "example": "판타지·무협에서 주로 — 과거 이런저런 인물이 세상을 지배했다는 식의 도입",
        "best_for_genre": ["판타지", "무협", "사극"],
    },
    "회상형": {
        "category": "독자를_마중",
        "definition": "지나간 일들에 대한 회상으로 시작",
        "key_devices": [
            "과거의 결정적 사건을 먼저 보여줌",
            "그 사건이 현재의 인물을 만들었다는 암시",
            "독자가 '왜 그렇게 됐는지' 알고 싶어함",
        ],
        "example": "내 ID는 강남미인 — 강미래의 과거 회상으로 도입",
        "best_for_genre": ["현대로맨스", "사극", "치정로맨스"],
    },
    "전체압축형": {
        "category": "독자를_마중",
        "definition": "서사 전체의 문제의식을 아우르는 질문을 독자에게 던지거나 은유하는 형식",
        "key_devices": [
            "프롤로그 형식의 압축",
            "전체 서사를 1~2단락에 응축",
            "본편 시작 전 '예고편'",
        ],
        "example": "치즈 인 더 트랩 — 홍설이 복학하는 과정과 유정과의 관계 예고편",
        "best_for_genre": ["현대로맨스", "스릴러", "치정로맨스"],
    },
    # ─── 독자를 유혹하는 4유형 (사건/행동 중심) ──────────────────
    "행동형": {
        "category": "독자를_유혹",
        "definition": "인물의 습관적 행위에 집중. 반복성을 띠며 의미와 상징성을 가짐",
        "key_devices": [
            "인물의 특징적 행동을 반복적으로 보여줌",
            "그 행동이 그 인물의 본질을 표현",
            "독자에게 모방 욕구까지 불러일으킴",
        ],
        "example": "슬램덩크 — 강백호의 박치기 습관과 빨간머리·큰 덩치가 한 장면에 응축",
        "best_for_genre": ["액션", "스포츠", "현대로맨스"],
    },
    "대비상징형": {
        "category": "독자를_유혹",
        "definition": "인물간의 극명한 대비를 통해서 필연적인 갈등을 암시",
        "key_devices": [
            "두 인물 또는 두 상황의 강한 대비",
            "그 대비가 사건의 동력이 될 것임을 암시",
            "독자가 '둘이 어떻게 부딪칠지' 궁금해함",
        ],
        "example": "겟백 — 천재 다정과 그런 천재가 부러웠던 언니 은정의 대비",
        "best_for_genre": ["현대로맨스", "성장물", "스포츠"],
    },
    "의문유발형": {
        "category": "독자를_유혹",
        "definition": "첫 장면에서 독자에게 궁금증을 유발. 비일상적 사건이나 자연법칙과 동떨어진 비현실적 상황 제시",
        "key_devices": [
            "이해할 수 없는 사건·상황 제시",
            "독자가 '이게 뭐지?' 즉시 의문",
            "수수께끼 해결 욕구가 다음 페이지로 견인",
        ],
        "example": "어느날 갑자기 서울은 — 산책 중 발견한 개구리 알 같은 것을 만지면서 사건 발생",
        "best_for_genre": ["판타지", "SF", "스릴러", "환생"],
        "best_for_4husbands": True,  # 환생/빙의 작품 도입에 적합
    },
}


def get_first_scene_type(type_name: str) -> dict:
    """첫 장면 유형 정의 반환."""
    return FIRST_SCENE_TYPES_9.get(type_name, {})


def get_first_scene_types_for_genre(genre: str) -> list:
    """장르에 맞는 첫 장면 유형 목록 반환."""
    return [
        k for k, v in FIRST_SCENE_TYPES_9.items()
        if genre in v.get("best_for_genre", [])
    ]


def get_first_scene_types_for_4husbands() -> list:
    """4명의 전남편들에 적합한 첫 장면 유형 목록 반환."""
    return [
        k for k, v in FIRST_SCENE_TYPES_9.items()
        if v.get("best_for_4husbands")
    ]


# ============================================================================
# MEDIA_CONVERSION_RATIO — 매체 전환 비율 (v3.4 신규)
# ============================================================================
# 출처: 백종인 (2022) IV-1 "웹툰 5화는 드라마 한편"
# 용도: 작품이 OTT 시리즈 전환을 염두에 둘 경우 분량·구조 산정에 활용

MEDIA_CONVERSION_RATIO = {
    "name": "웹툰·웹소설 ↔ 드라마 전환 비율",
    "core_ratio": {
        "webtoon_to_drama": "웹툰 5화 ≈ 드라마 1편",
        "webnovel_to_drama": "웹소설 8~10화 ≈ 드라마 1편 (분량에 따라 변동)",
    },
    "rationale": [
        "주 2회 방영되는 드라마의 한 회차 분량은 약 60~70분",
        "웹툰 1화는 평균 50~80컷, 약 12~15분 분량",
        "웹소설 1화는 약 5,000~7,000자, 약 10분 분량",
        "따라서 웹툰 10화는 드라마 2회, 웹소설 50화는 드라마 5~6회 분량",
    ],
    "application_for_planning": {
        "50화 웹소설": "드라마 5~6회분 분량 — OTT 미니시리즈(6~12회) 전환 시 추가 8~10화 분량 필요",
        "100화 웹소설": "드라마 10~12회분 분량 — OTT 미니시리즈 한 시즌과 호환",
        "16부작 드라마 역산": "웹소설로는 약 130~160화 필요",
    },
    "key_structural_difference": [
        "웹소설: 매 화차마다 결제 유도하는 클리프행어 필요",
        "드라마: 매 회차마다 한 단원 마무리 + 다음 회 예고",
        "웹소설→드라마 각색 시: 회차 5개를 묶어 한 드라마 회차로 재구성",
    ],
    "applicable_4husbands": True,  # 50화 완성작 — OTT 시리즈 전환 시 추가 분량 필요
    "source": "백종인 (2022), 공주대 만화학과 석사논문, IV-1",
}


def get_media_conversion_for_length(total_episodes: int) -> dict:
    """작품 분량에 따른 드라마 전환 비율 계산.

    Args:
        total_episodes: 웹소설 총 화수

    Returns:
        {"webnovel_episodes": N, "drama_episodes_estimated": N, "ott_compatible": bool}
    """
    # 웹소설 8화당 드라마 1편 (중간값)
    drama_episodes = round(total_episodes / 8, 1)
    ott_compatible = 6 <= drama_episodes <= 16  # 일반 OTT 미니시리즈 회차 범위
    return {
        "webnovel_episodes": total_episodes,
        "drama_episodes_estimated": drama_episodes,
        "ott_compatible": ott_compatible,
        "note": "OTT 미니시리즈는 보통 8~12회. 한 시즌으로 압축하려면 80~96화 권장",
    }


# ============================================================================
# 자기 검증
# ============================================================================

def _validate_module():
    """모듈 데이터 무결성 검증."""
    # 로판 3종 창작 전략
    assert len(ROFAN_CREATION_STRATEGY) == 3, "로판 창작 전략 3종 아님"
    
    # 4명의 전남편들 적용 가능 전략 1개 이상
    applicable = [k for k, v in ROFAN_CREATION_STRATEGY.items() 
                  if v.get("applicable_4husbands")]
    assert len(applicable) >= 1, "4명의 전남편들 적용 전략 없음"
    
    # 헤테로토피아 프레임 핵심 필드
    assert "construction_elements" in HETEROTOPIA_FRAME
    assert "typical_spaces" in HETEROTOPIA_FRAME
    assert "function_in_narrative" in HETEROTOPIA_FRAME
    
    # POV 혼용 가이드
    assert len(POV_BLENDING_GUIDE["default_pov"]) >= 5, "기본 시점 5종 미달"
    assert "free_indirect_discourse" in POV_BLENDING_GUIDE
    
    # 로판 3대 독자 욕망
    assert len(READER_DESIRES_ROFAN) == 3, "로판 독자 욕망 3종 아님"
    
    # v3.4 신규 — 첫 장면 9유형
    assert len(FIRST_SCENE_TYPES_9) == 9, f"첫 장면 유형 9종 아님: {len(FIRST_SCENE_TYPES_9)}"
    for k, v in FIRST_SCENE_TYPES_9.items():
        assert "definition" in v, f"{k}에 definition 누락"
        assert "category" in v, f"{k}에 category 누락"
        assert "key_devices" in v, f"{k}에 key_devices 누락"
    
    # v3.4 신규 — 매체 전환 비율
    assert "core_ratio" in MEDIA_CONVERSION_RATIO
    assert "webnovel_to_drama" in MEDIA_CONVERSION_RATIO["core_ratio"]
    
    return True


_validate_module()


if __name__ == "__main__":
    print("=" * 60)
    print("data_strategy.py v3.4 — 모듈 자가 검증")
    print("=" * 60)
    print(f"로판 창작 전략: {len(ROFAN_CREATION_STRATEGY)}종")
    print(f"헤테로토피아 핵심 장치: {len(HETEROTOPIA_FRAME['key_devices'])}개")
    print(f"기본 시점 권장: {len(POV_BLENDING_GUIDE['default_pov'])}종")
    print(f"로판 독자 욕망: {len(READER_DESIRES_ROFAN)}종")
    print(f"첫 장면 9유형 (v3.4): {len(FIRST_SCENE_TYPES_9)}종")
    print(f"매체 전환 비율 (v3.4): {MEDIA_CONVERSION_RATIO['core_ratio']['webnovel_to_drama']}")
    print()
    
    print("[4명의 전남편들 적용 가능 전략]")
    for name, data in ROFAN_CREATION_STRATEGY.items():
        if data.get("applicable_4husbands"):
            print(f"  ✓ {name}")
            print(f"    적용 메모: {data.get('4husbands_application', '')}")
    print()
    
    print("[첫 장면 9유형 — 4명의 전남편들 적합]")
    for name in get_first_scene_types_for_4husbands():
        scene = FIRST_SCENE_TYPES_9[name]
        print(f"  ✓ {name} ({scene['category']})")
        print(f"    {scene['definition'][:60]}...")
    print()
    
    print("[매체 전환 — 50화 작품 기준]")
    conversion = get_media_conversion_for_length(50)
    print(f"  웹소설 50화 → 드라마 약 {conversion['drama_episodes_estimated']}회")
    print(f"  OTT 호환: {conversion['ott_compatible']}")
    print()
    
    print("✓ v3.4 모든 검증 통과")
