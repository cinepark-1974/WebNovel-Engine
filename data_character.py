"""
data_character.py — Engine v3.0
================================
캐릭터 메타정보 데이터셋

수록 데이터:
- CHARACTER_ROLE_TAXONOMY — 9종 인물 역할 + 4세계 분류
- MOE_ATTRIBUTES_25 — 모에 25속성 (외관/역할/성격)
- HEROINE_MIND_FLOW_PATTERNS — 여성 주인공 마음 흐름 5단계
- COMPLETED_HERO_PATTERNS — 남성향 완성된 영웅 패턴
- HERO_MIND_FLOW_PATTERNS — 남성 주인공 마음 흐름 3단계
- READER_CONSUMPTION_TIERS — 소비자 3분화

원칙:
- 학술 용어 풀어쓰기 (장르 오인 방지)
  · "공포" → "불안·정체성 흔들림" (호러 장르 오인 방지)
  · "이행분노" → "방향 잡힌 분노"
  · "정동" → "마음 흐름"
- 여성향 + 남성향 양쪽 동등 지원
- 캐릭터 풀 데이터에 신규 필드 추가 (narrative_role, moe_attributes,
  inner_state_arc, hero_type 등)

사용 예시:
    from data_character import CHARACTER_ROLE_TAXONOMY, get_role_for_character
    role = get_role_for_character("김지훈")  # → "전사_정신적_스승"
"""

# ============================================================================
# CHARACTER_ROLE_TAXONOMY — 9종 인물 역할 + 4세계 분류
# ============================================================================
# 용도: 모든 등장인물에 narrative_role 태그 부여. EP2 같은 다중 인물 등장
#       회차에서 각자 다른 역할로 분배하여 평면화 방지.

CHARACTER_ROLE_TAXONOMY = {
    
    # ─── 소원세계 인물화 (영웅 + 짝 구조) ──────────────
    "전사_정신적_스승": {
        "world": "소원세계",
        "description": "주인공의 능력·기술 발휘를 돕고 정신적 안식처가 되는 멘토. 영웅과 짝 구조",
        "behavior_pattern": "조용한 지지, 결정적 순간의 가르침, 거리 유지하면서도 일관된 신뢰",
        "dialogue_pattern": "말이 적음, 핵심만 짚음, 명령형보다 시선·표정",
        "applicable_4husbands": "김지훈 (메인 남주, 한시호의 정신적 안식처)",
    },
    "기업가_현로(賢老)": {
        "world": "소원세계",
        "description": "재력·자원으로 주인공을 후원하는 인물. 현명한 노년의 지혜",
        "behavior_pattern": "자원 제공, 사업 조언, 거리 유지",
        "dialogue_pattern": "경험에서 우러난 격언, 단정적 어조",
    },
    "예술_문화창조_제공자": {
        "world": "소원세계",
        "description": "주인공의 예술/창조 활동을 가능하게 하는 환경 제공자",
        "behavior_pattern": "공간·기회 제공, 무조건적 지지",
        "dialogue_pattern": "감성적 어조, 창조성을 인정하는 언어",
    },
    
    # ─── 의도세계 인물화 (대적자 구조) ──────────────
    "세계_패권_적대_악한": {
        "world": "의도세계",
        "description": "주인공과 정면 대립하는 핵심 빌런. 세계 패권을 두고 다툼",
        "behavior_pattern": "조직적 대립, 제도·시스템 활용, 직접적 위협",
        "dialogue_pattern": "권위적 어조, 명령형, 협박 또는 회유",
    },
    "친밀한_타자_가면들": {
        "world": "의도세계",
        "description": "친밀한 척하지만 본심을 숨기는 인물. 가면 뒤에 다른 의도",
        "behavior_pattern": "표면적 호의, 정보 수집, 결정적 순간 배신",
        "dialogue_pattern": "다정한 척, 이중 의미 포함",
        "applicable_4husbands": "이수현 (절친 가면 + 실제로는 위협)",
    },
    "장애물_적대적_흑막": {
        "world": "의도세계",
        "description": "막후에서 주인공을 방해하는 흑막. 직접 대면보다 간접 조종",
        "behavior_pattern": "그림자 작전, 정보 조작, 대리인 활용",
        "dialogue_pattern": "비밀스러운 어조, 정보 비대칭 활용",
        "applicable_4husbands": "최진규 (갤러리 비밀, EP8-19-22 흑막)",
    },
    
    # ─── 지식세계 인물화 (정보·자본 매개) ──────────────
    "정보세계_관문수호자": {
        "world": "지식세계",
        "description": "정보·지식의 입구를 지키는 인물. 통과 조건 부과",
        "behavior_pattern": "조건 제시, 시험 부과, 통과 여부 판정",
        "dialogue_pattern": "공식적 어조, 규칙·기준 강조",
        "applicable_4husbands": "박재윤 (변호사, EP6 정보 게이트키퍼)",
    },
    "자본세계_전령관": {
        "world": "지식세계",
        "description": "자본·기회를 매개하는 인물. 경제적 정보 통로",
        "behavior_pattern": "거래 제안, 자본 흐름 조종",
        "dialogue_pattern": "수치 중심, 효율 언어",
    },
    "보이스피싱_협력자": {
        "world": "지식세계",
        "description": "사기·기만으로 주인공을 위협하는 협력자. 거짓 정보 매개",
        "behavior_pattern": "거짓 정보 제공, 신뢰 획득 후 배신",
        "dialogue_pattern": "신뢰감 있는 어조 가장",
    },
    
    # ─── 의무세계 인물화 (변신·연대) ──────────────
    "외로움_트릭스터": {
        "world": "의무세계",
        "description": "외로움이 깊은 인물, 예측 불가 행동. 코미디·비극 양면",
        "behavior_pattern": "갑작스러운 등장·이탈, 분위기 전환, 진심 숨김",
        "dialogue_pattern": "농담조와 진지함 교차, 갑작스러운 고백",
        "applicable_4husbands": "이준호 (EP11-13-15-31 트릭스터적 행동)",
    },
    "복수_변신자재자": {
        "world": "의무세계",
        "description": "복수 동력으로 변신하는 인물. 모습·역할 변화",
        "behavior_pattern": "정체 위장, 단계별 변신, 결정적 폭로",
        "dialogue_pattern": "다중 페르소나, 어조 변화 자유로움",
    },
    "전략적_동맹_협력자": {
        "world": "의무세계",
        "description": "전략적 동맹으로 주인공을 돕거나 이용하는 인물",
        "behavior_pattern": "이해관계 명확, 조건부 협력, 변심 가능성",
        "dialogue_pattern": "계산적 어조, 거래 언어",
        "applicable_4husbands": "박민수 (EP2 도입, 협력자 또는 적대 가면)",
    },
}


# ============================================================================
# MOE_ATTRIBUTES_25 — 모에 25속성 (3축 분류)
# ============================================================================
# 용도: 캐릭터 풀 데이터의 보조 태그. 한 캐릭터에 외관/역할/성격 각 1개씩 권장.

MOE_ATTRIBUTES_25 = {
    "외관": {
        "안경소녀": "지적·도서관 분위기, 차분함",
        "포니테일": "활발·운동선수 분위기, 시원함",
        "트윈테일": "어린 분위기, 발랄함",
        "긴머리": "여성성 강조, 우아함",
        "단발머리": "현대적, 깔끔함",
        "가슴_빈약": "어린 분위기, 보호 본능 자극",
        "가슴_풍만": "성숙 분위기, 모성·관능",
        "체구_작음": "보호 본능, 귀여움",
        "키_큼": "모델 분위기, 카리스마",
    },
    "역할": {
        "여동생": "보호 본능, 친밀성",
        "누나": "포용·돌봄 분위기",
        "선배": "동경·존경",
        "후배": "보호·가르침",
        "메이드": "헌신, 봉사",
        "비서": "유능함, 신뢰성",
        "여학생": "청춘·미숙함",
        "교사": "권위·지적 매력",
        "공주_영애": "고귀함, 신분 차이",
        "환생자": "신비, 정체성 미스터리",  # ★ 4명의 전남편들 한시호
        "신비한_단골손님": "수수께끼, 일상 속 비일상",  # ★ 김지훈
    },
    "성격": {
        "츤데레": "겉으로 차갑고 속으로 다정 (대비 매력)",
        "얀데레": "광적 집착, 위험한 사랑",
        "쿨데레": "겉으로 무심하고 속으로 따뜻 (말 적음)",  # ★ 김지훈
        "도짓코": "실수 잦은 덜렁이, 웃음 유발",
        "메가데레": "과도한 호의, 감정 폭발",
        "쿠데레": "차가움 + 진지함 (말이 적고 거리 유지)",  # ★ 한시호 초기
        "단데레": "조용함 + 다정함 (수동적이지만 따뜻)",
    },
}


# ============================================================================
# HEROINE_MIND_FLOW_PATTERNS — 여성 주인공 마음 흐름 5단계
# ============================================================================
# ★ 단어 라벨 — 학술용어 풀어쓰기 ★
# - "공포" → "불안·정체성 흔들림" (호러 장르 오인 방지)
# - "이행분노" → "방향 잡힌 분노" (단순 분노가 아님 명시)
# - "정동(affect)" → "마음 흐름"
#
# 적용 대상: 여성 주인공 (악녀 캐릭터뿐 아니라 빙의·회귀·환생 여주 일반)
# 핵심 원칙:
# - 여주의 내면 흐름이 5단계를 거쳐 회복되도록 설계
# - 단계 사이의 전환점이 자연스러워야 함
# - 단계 안에서의 마음 흐름이 일관되어야 함

HEROINE_MIND_FLOW_PATTERNS = {
    "stages": [
        {
            "stage": 1,
            "name": "불안·정체성 흔들림",
            "description": "회·빙·환 직후 또는 트라우마 직후, 불안이 일상이 됨. 정체성이 흔들림",
            "inner_state_keywords": [
                "예측 불가능한 환경에 대한 경계",
                "자기 자신에 대한 의심",
                "어디에도 속하지 못한 외로움",
                "환경에 대한 깊은 불신"
            ],
            "behavior_keywords": [
                "타인 경계, 시선 회피",
                "자기방어적 언행",
                "최소한의 노출",
                "관계 거리두기"
            ],
            "internal_state_summary": "환생 직후 정체성이 흔들리는 불안. 어디에도 속하지 못한 외로움이 표면화",
        },
        {
            "stage": 2,
            "name": "각성·상황 파악",
            "description": "현재 상황 파악, 변화의 필요성 자각",
            "inner_state_keywords": [
                "주변 환경 정보 수집 의지",
                "자신의 위치 점검",
                "변화의 가능성 인식"
            ],
            "behavior_keywords": [
                "주변 환경 탐색",
                "정보 수집 행동",
                "관찰자 모드"
            ],
            "internal_state_summary": "혼란 속에서 결단 직전의 상태. 자신의 위치를 객관적으로 파악하기 시작",
        },
        {
            "stage": 3,
            "name": "자립 의지·생존 행동",
            "description": "생존 전략으로서 능력과 사회적 자원 추구. 적극적 행동",
            "inner_state_keywords": [
                "결의와 야망",
                "자기 증명의 욕구",
                "구체적 목표 설정"
            ],
            "behavior_keywords": [
                "공부, 운동, 인맥 구축",
                "사업 도전, 능력 입증",
                "공격적 행동 개시"
            ],
            "internal_state_summary": "결단을 내리고 적극적으로 행동에 나선다. 자기 자립을 위한 의지가 강해짐",
        },
        {
            "stage": 4,
            "name": "방향 잡힌 분노",
            "description": "단순 복수에서 미래지향적·연민어린 분노로 전환. 분노에 방향과 목적이 생김",
            "inner_state_keywords": [
                "분노가 미래를 향함",
                "연민이 분노에 결합",
                "결단이 명확해짐",
                "타인을 향한 책임감"
            ],
            "behavior_keywords": [
                "타인 구원 시도",
                "시스템 변혁 시도",
                "다른 피해자와의 연대",
                "복수보다 진실 추구"
            ],
            "internal_state_summary": "단순 복수가 아닌, 다른 피해자도 구원하려는 더 큰 분노. 미래를 향한 결단",
            "key_principle": "고통을 고통으로 갚는 것이 아니라, 같은 일이 반복되지 않도록 하는 분노",
        },
        {
            "stage": 5,
            "name": "자기 회복·연결 회복",
            "description": "다른 여성/약자와의 연대, 규범 탈주, 새로운 질서 건설",
            "inner_state_keywords": [
                "확신과 평화",
                "자기 자신과의 화해",
                "타인과의 진정한 연결"
            ],
            "behavior_keywords": [
                "공동체 결성",
                "멘토 역할",
                "규범 거부 또는 새 질서 건설",
                "사랑의 수용"
            ],
            "internal_state_summary": "자기 자신을 되찾고, 다른 사람들과 진정한 관계를 맺는다. 평화와 확신",
        },
    ],
    
    "fluid_threats": {
        "description": "여성 주인공이 마주하는 3가지 위협 영역",
        "threats": [
            "신체·재산 위협",
            "사회 질서 위협",
            "사회적 지위·정체성 위협"
        ]
    },
    
    "applicable_to": [
        "악녀 회귀물 여주",
        "빙의 로맨스 여주",
        "환생 로판 여주",
        "치정 로맨스 여주 (트라우마 보유)"
    ],
}


# 하위 호환 별칭 (Phase B 진입 전 기존 코드 보호용)
VILLAINESS_AFFECT_PATTERNS = HEROINE_MIND_FLOW_PATTERNS


# ============================================================================
# COMPLETED_HERO_PATTERNS — 남성향 완성된 영웅 패턴
# ============================================================================
# 용도: 남성향 작품 (헌터물·회귀물·빙의물·랭커물 등) 주인공 설계
# 분석 사례: 재벌집 막내아들(2022), 중증외상센터(2025), 전지적 독자 시점,
#           나 혼자만 레벨업 등 2020년대 이후 남성향 흥행작

COMPLETED_HERO_PATTERNS = {
    "completed_hero": {
        "name": "완성된 영웅",
        "description": "결함이 최소화된 완성형 영웅. 시작부터 능력·자신감 보유",
        "starting_state": [
            "능력 보유 (회귀·빙의·환생으로 미래 지식 또는 우월 능력)",
            "자기 확신",
            "정체성 안정",
            "내적 결함 부재 (외부 환경에 의해서만 위기 발생)"
        ],
        "growth_pattern": "최소 (성장 서사 거부). 외부 환경 변화에 대응할 뿐, 내적 변화는 작음",
        "conflict_resolution": "신속 (단일 회차 내 해결). 갈등이 다음 회차로 끌리지 않음",
        "internal_change": "방향 전환 (예: 가족 결핍 → 그룹 인수, 의사 자존감 → 시스템 변혁 등 목표가 진화)",
        "function_internalization": "정신적 스승 원형을 내재화 (가르침을 받기보다 제공)",
        "behavior_keywords": [
            "주변 인물에게 가르침 제공",
            "정보 비대칭성 활용",
            "사이다 임팩트 발휘",
            "위기에 신속 대응",
            "관문 통과의 빠른 반복"
        ],
        "dialogue_pattern": "단정적 어조, 명령보다 사실 진술, 결과로 증명",
        "applicable_genres": [
            "헌터물", "회귀물", "빙의물(남성향)",
            "랭커물", "재벌물", "현대판타지", "정통판타지", "게임판타지"
        ],
        "anti_patterns": [
            "A28 — 성장 강박: 남성향 주인공에게 성장 단계를 강제로 만들지 말 것",
            "A29 — 고구마 함정: 갈등을 회차 너머로 끄는 것은 결제 이탈의 1번 원인",
            "A30 — 약한 대적자: 대적자가 단순 위협이 아니라 시험 부과 기능을 해야 함",
            "A31 — 협력자 독립성 과잉: 협력자가 자체 서사 동력을 가지면 영웅 중심 구조 흐림",
        ],
        "representative_works": [
            "재벌집 막내아들 (진도준)",
            "중증외상센터 (백강혁)",
            "전지적 독자 시점 (김독자)",
            "나 혼자만 레벨업 (성진우)"
        ],
    },
    
    "growing_hero_supporting": {
        "name": "성장하는 협력자 영웅",
        "description": "주인공이 아닌 협력자가 성장하는 패턴. 메인 영웅의 가르침 받음",
        "function": "메인 영웅의 정신적 스승 능력을 입증하는 거울 역할",
        "starting_state": "잠재력 있으나 미완성",
        "growth_pattern": "메인 영웅의 가르침으로 성장 (기존 영웅 여정 패턴)",
        "representative_works": [
            "중증외상센터 양재원 (백강혁의 협력자)"
        ],
    },
}


# ============================================================================
# HERO_MIND_FLOW_PATTERNS — 남성 주인공 마음 흐름 패턴
# ============================================================================
# 여성 주인공 마음 흐름(HEROINE_MIND_FLOW_PATTERNS)에 대응하는 남성향 버전
# 단, 5단계가 아니라 3단계로 축약 (완성된 영웅은 변화 최소이므로)

HERO_MIND_FLOW_PATTERNS = {
    "stages": [
        {
            "stage": 1,
            "name": "각성·동기 발현",
            "description": "회귀·빙의·환생 직후 또는 능력 각성 직후",
            "inner_state_keywords": [
                "결단 (망설임 짧음)",
                "방향성 명확",
                "자신감 형성"
            ],
            "behavior_keywords": [
                "즉각적 행동 시작",
                "미래 지식 활용 결심",
                "초기 성취 달성"
            ],
            "internal_state_summary": "회귀/빙의 직후 빠르게 결단하고 행동에 나선다. 망설임이 짧음",
        },
        {
            "stage": 2,
            "name": "관문 통과·세력 확장",
            "description": "관문수호자들의 시험을 통과하며 세력·자원·인맥 확장",
            "inner_state_keywords": [
                "전략적 사고",
                "체계적 진행",
                "사이다 카타르시스"
            ],
            "behavior_keywords": [
                "관문 빠른 통과",
                "정보 비대칭성 활용",
                "협력자·자원 획득",
                "약자 가르침"
            ],
            "internal_state_summary": "단계별 시험을 신속히 통과하며 세력을 키운다. 사이다의 핵심 단계",
        },
        {
            "stage": 3,
            "name": "목표 진화·재정의",
            "description": "초기 목표(개인적 복수·생존)에서 더 큰 목표(시스템 변혁·세계 구원)로 진화",
            "inner_state_keywords": [
                "더 큰 책임감",
                "시야 확장",
                "공동체 의식"
            ],
            "behavior_keywords": [
                "체계 변혁 시도",
                "타인 구원",
                "더 큰 적과 대결"
            ],
            "internal_state_summary": "개인적 동기에서 더 큰 차원의 목표로 시야를 확장한다",
        },
    ],
}


# 하위 호환 별칭
HERO_AFFECT_PATTERNS = HERO_MIND_FLOW_PATTERNS


# ============================================================================
# READER_CONSUMPTION_TIERS — 소비자 3분화
# ============================================================================
# 용도: 작품 콘셉트의 target_consumption_tier 필드. 1~2개 선택.

READER_CONSUMPTION_TIERS = {
    "팬": {
        "intensity": "약~중",
        "spending_monthly_won": "0~10000",
        "behavior": "무료 회차 위주, 화제작 결제 가끔",
        "decision_factor": "추천 알고리즘, 주변 추천",
        "trigger": "표지·제목·시놉시스의 첫인상",
        "platform_preference": ["카카오페이지", "네이버 웹소설"],
    },
    "매니아": {
        "intensity": "중~강",
        "spending_monthly_won": "30000~50000",
        "behavior": "선호 작가 모든 작품 추적, 신간 즉시 결제",
        "decision_factor": "작가 충성도, 장르 일관성",
        "trigger": "작가의 신작 알림",
        "platform_preference": ["리디", "카카오페이지", "네이버시리즈"],
    },
    "오타쿠": {
        "intensity": "강",
        "spending_monthly_won": "100000+",
        "behavior": "전 회차 일괄 결제, 특정 모티프 깊은 몰입",
        "decision_factor": "특정 모티프(예: 빙의, 회귀, 악녀) 부합도",
        "trigger": "특정 ~물 태그, 모에 속성 조합",
        "platform_preference": ["리디", "문피아", "조아라"],
    },
}


# ============================================================================
# 헬퍼 함수
# ============================================================================

def find_roles_for_4husbands() -> dict:
    """4명의 전남편들 5명 남자에 매핑된 역할 자동 추출."""
    result = {}
    for role_name, role_data in CHARACTER_ROLE_TAXONOMY.items():
        if role_data.get("applicable_4husbands"):
            result[role_name] = role_data["applicable_4husbands"]
    return result


def get_role_world(role_name: str) -> str:
    """역할이 속한 세계 반환."""
    role = CHARACTER_ROLE_TAXONOMY.get(role_name)
    if not role:
        return ""
    return role.get("world", "")


def get_role_behavior(role_name: str) -> list:
    """역할의 행동 패턴 반환 (집필 프롬프트 주입용)."""
    role = CHARACTER_ROLE_TAXONOMY.get(role_name)
    if not role:
        return []
    return [role.get("behavior_pattern", ""), role.get("dialogue_pattern", "")]


def get_mind_flow_stage_for_episode(ep_num: int, total_eps: int = 42) -> dict:
    """회차 번호로 마음 흐름 단계 자동 추론 (4명의 전남편들 분포 기준).
    
    분포 (총 42회):
    - EP1-2 (4.8%): 1단계 불안·정체성 흔들림
    - EP3-5 (7.1%): 2단계 각성·상황 파악
    - EP6-18 (31.0%): 3단계 자립 의지·생존 행동
    - EP19-30 (28.6%): 4단계 방향 잡힌 분노
    - EP31-42 (28.6%): 5단계 자기 회복·연결 회복
    """
    pct = ep_num / total_eps
    
    if pct <= 0.05:
        stage_idx = 0  # 1단계
    elif pct <= 0.12:
        stage_idx = 1  # 2단계
    elif pct <= 0.43:
        stage_idx = 2  # 3단계
    elif pct <= 0.72:  # EP30/42=0.714 → 4단계 포함, EP31/42=0.738 → 5단계
        stage_idx = 3  # 4단계
    else:
        stage_idx = 4  # 5단계
    
    return HEROINE_MIND_FLOW_PATTERNS["stages"][stage_idx]


# 하위 호환 별칭
get_affect_stage_for_episode = get_mind_flow_stage_for_episode


def get_moe_attribute(category: str, attribute: str) -> str:
    """모에 속성의 의미 반환."""
    return MOE_ATTRIBUTES_25.get(category, {}).get(attribute, "")


# ============================================================================
# 자기 검증
# ============================================================================

def _validate_module():
    """모듈 데이터 무결성 검증."""
    assert len(CHARACTER_ROLE_TAXONOMY) >= 9, f"인물 역할 9종 미달: {len(CHARACTER_ROLE_TAXONOMY)}"
    
    # 4명의 전남편들 5명 매핑 검증
    husbands_map = find_roles_for_4husbands()
    assert len(husbands_map) >= 5, f"4명의 전남편들 매핑 5명 미달: {len(husbands_map)}"
    
    # 여주 마음 흐름 5단계
    assert len(HEROINE_MIND_FLOW_PATTERNS["stages"]) == 5, "여성 마음 흐름 5단계 아님"
    
    # 영웅 마음 흐름 3단계
    assert len(HERO_MIND_FLOW_PATTERNS["stages"]) == 3, "남성 영웅 마음 흐름 3단계 아님"
    
    # 모에 속성 25종 (외관 9 + 역할 11 + 성격 7 = 27, 25+ 통과)
    total_moe = sum(len(v) for v in MOE_ATTRIBUTES_25.values())
    assert total_moe >= 25, f"모에 속성 25종 미달: {total_moe}"
    
    # 소비자 3분화
    assert len(READER_CONSUMPTION_TIERS) == 3, "소비자 3분화 아님"
    
    return True


_validate_module()


if __name__ == "__main__":
    print("=" * 60)
    print("data_character.py — 모듈 자가 검증")
    print("=" * 60)
    print(f"인물 역할 분류: {len(CHARACTER_ROLE_TAXONOMY)}종")
    total_moe = sum(len(v) for v in MOE_ATTRIBUTES_25.values())
    print(f"모에 속성: {total_moe}종 (외관/역할/성격)")
    print(f"여성 마음 흐름 단계: {len(HEROINE_MIND_FLOW_PATTERNS['stages'])}단계")
    print(f"남성 영웅 마음 흐름 단계: {len(HERO_MIND_FLOW_PATTERNS['stages'])}단계")
    print(f"소비자 분화: {len(READER_CONSUMPTION_TIERS)}종")
    print()
    
    print("[4명의 전남편들 5명 자동 매핑]")
    for role, person in find_roles_for_4husbands().items():
        world = get_role_world(role)
        print(f"  {role} ({world}) → {person}")
    print()
    
    print("[한시호 마음 흐름 5단계 회차별 자동 분배 (총 42회 기준)]")
    test_eps = [1, 3, 10, 19, 30, 35, 42]
    for ep in test_eps:
        stage = get_mind_flow_stage_for_episode(ep, 42)
        print(f"  EP{ep:>2}: {stage['stage']}단계 [{stage['name']}]")
    print()
    
    print("[마음 흐름 4단계 풀 출력 — 한시호 EP19~30 가이드]")
    stage4 = HEROINE_MIND_FLOW_PATTERNS["stages"][3]
    print(f"  이름: {stage4['name']}")
    print(f"  설명: {stage4['description']}")
    print(f"  내면 키워드: {', '.join(stage4['inner_state_keywords'])}")
    print(f"  행동 키워드: {', '.join(stage4['behavior_keywords'])}")
    print(f"  요약: {stage4['internal_state_summary']}")
    print()
    
    print("[김지훈 캐릭터 풀 매핑 예시]")
    print(f"  역할: 전사_정신적_스승 ({get_role_world('전사_정신적_스승')})")
    print(f"  외관: 긴머리 / 역할: 신비한_단골손님 / 성격: 쿨데레")
    print(f"  쿨데레 의미: {get_moe_attribute('성격', '쿨데레')}")
    print()
    
    print("✓ 모든 검증 통과")
