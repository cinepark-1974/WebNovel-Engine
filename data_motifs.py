"""
data_motifs.py — Engine v3.0
================================
모티프·포뮬러·이동코드 데이터셋

수록 데이터:
- RELATIONSHIP_MOTIFS_DICT — 23종 관계성 모티프
- ROMANCE_FORMULAS — 6종 장르 포뮬러 + 스토리 다이어그램
- MOVEMENT_NARRATIVE_PATTERNS — 5종 이동 계열 서사 (회귀/빙의/환생/전생/전이)
- HIGH_RATING_ROMANCE_MOTIFS — 고수위 5종 서사 모티프
- EROTICISM_PRINCIPLES — 19금 작동 3요소
- ROFAN_SUBGENRES — 로판 3종 세부장르

원칙:
- 모든 데이터는 "기획↔집필 연결" 강제 시스템에서 사용됨
- 여성향/남성향 발란스 유지
- 4명의 전남편들 작품에 직접 매핑 가능한 구조

사용 예시:
    from data_motifs import RELATIONSHIP_MOTIFS_DICT, ROMANCE_FORMULAS
    formula = ROMANCE_FORMULAS["운명적_인연물"]
    diagram = formula["story_diagram"]
"""

# ============================================================================
# RELATIONSHIP_MOTIFS_DICT — 23종 관계성 모티프
# ============================================================================
# 용도: 작품의 보조 모티프 태그. 한 작품에 1~5개 결합 가능.
# 강제 주입: 해당 모티프가 등장하는 회차의 집필 프롬프트에 정의가 주입됨.

RELATIONSHIP_MOTIFS_DICT = {
    "재회물": {
        "definition": "과거에 헤어졌던 남주와 여주가 다시 만나서 서사가 진행되는 이야기",
        "common_combinations": ["오래된연인", "첫사랑", "운명적사랑"],
        "typical_genre": ["현대로맨스", "치정로맨스"],
        "platform_strength": ["리디", "카카오페이지"],
    },
    "오래된연인": {
        "definition": "관계가 오래 지속된 연인 혹은 부부가 권태기를 겪으며 이를 통해 성장하는 이야기",
        "common_combinations": ["재회물", "운명적사랑"],
        "typical_genre": ["현대로맨스"],
    },
    "첫사랑": {
        "definition": "주인공 중 한 사람의 첫사랑이 상대 주인공인 경우",
        "common_combinations": ["재회물", "운명적사랑"],
        "typical_genre": ["현대로맨스", "로판"],
    },
    "친구>연인": {
        "definition": "친구인 두 주인공이 연인으로 관계가 전환되는 이야기",
        "common_combinations": ["오래된연인", "사내연애"],
        "typical_genre": ["현대로맨스"],
    },
    "라이벌_앙숙": {
        "definition": "두 주인공이 경쟁하던 사이에서 연인으로 발전하는 이야기",
        "common_combinations": ["사내연애", "갑을관계"],
        "typical_genre": ["현대로맨스", "로판"],
    },
    "사제지간": {
        "definition": "스승과 학생의 신분으로 관계에서 연인으로 발전하는 이야기",
        "common_combinations": ["금단의관계", "신분차이"],
        "typical_genre": ["로판", "현대로맨스"],
    },
    "나이차커플": {
        "definition": "나이 차가 큰 두 주인공의 관계성이 중심이 되는 이야기",
        "common_combinations": ["사제지간", "신분차이"],
        "typical_genre": ["현대로맨스", "치정로맨스"],
    },
    "키잡물": {
        "definition": "키워서 잡아먹는 이야기. 주인공 중 한 사람이 상대를 어릴 때부터 키웠으나 연애 감정이 생겨서 연인이 되는 이야기",
        "common_combinations": ["나이차커플", "금단의관계"],
        "typical_genre": ["로판", "치정로맨스"],
    },
    "사내연애": {
        "definition": "두 주인공이 같은 직장에 다니는 이야기",
        "common_combinations": ["갑을관계", "친구>연인", "라이벌_앙숙"],
        "typical_genre": ["현대로맨스"],
    },
    "비밀연애": {
        "definition": "연애 감정을 외부에 숨기고 관계를 발전시키며, 이러한 비밀이 사건을 촉발하는 이야기",
        "common_combinations": ["사내연애", "사제지간", "금단의관계"],
        "typical_genre": ["현대로맨스", "로판"],
    },
    "삼각관계": {
        "definition": "매력적인 조연이 등장하여 삼각관계를 이루는 이야기",
        "common_combinations": ["라이벌_앙숙", "운명적사랑"],
        "typical_genre": ["현대로맨스", "로판", "치정로맨스"],
        "applicable_4husbands": True,  # ★ 4명의 전남편들 — 다중관계망 변형
    },
    "갑을관계": {
        "definition": "사회 규범상 주인공 간 갑을관계가 형성되고 사건 진행에 주효하게 작용하는 이야기",
        "common_combinations": ["사내연애", "신분차이", "계약연애_결혼"],
        "typical_genre": ["현대로맨스", "치정로맨스", "로판"],
        "applicable_4husbands": True,  # ★ 4명의 전남편 권력관계
    },
    "신분차이": {
        "definition": "사회 규범상 신분 격차가 큰 주인공이 등장하는 이야기",
        "common_combinations": ["갑을관계", "금단의관계"],
        "typical_genre": ["로판", "치정로맨스"],
    },
    "계약연애_결혼": {
        "definition": "주인공이 서로 계약을 맺고 연애나 결혼하는 이야기. 주인공 당사자의 개인적 계약에 의거함",
        "common_combinations": ["갑을관계", "비밀연애"],
        "typical_genre": ["현대로맨스", "치정로맨스"],
    },
    "정략결혼": {
        "definition": "집안, 가문 등 속한 집단의 이익에 따라 결혼하는 이야기",
        "common_combinations": ["신분차이", "선결혼후연애"],
        "typical_genre": ["로판", "치정로맨스"],
    },
    "선결혼후연애": {
        "definition": "결혼 전에는 애정선이 불분명하다가, 결혼 후 연애 감정이 표출되는 이야기",
        "common_combinations": ["정략결혼", "계약연애_결혼"],
        "typical_genre": ["로판", "치정로맨스"],
    },
    "원나잇": {
        "definition": "일회성 관계를 맺은 두 주인공이 감정적으로 발전하는 이야기",
        "common_combinations": ["몸정맘정", "재회물"],
        "typical_genre": ["치정로맨스"],
    },
    "몸정맘정": {
        "definition": "연애 감정 없이 섹스에 길든 후에 사랑이 싹트는 이야기 (선섹후사)",
        "common_combinations": ["원나잇", "갑을관계"],
        "typical_genre": ["치정로맨스"],
    },
    "소유욕_독점욕_질투": {
        "definition": "상대를 소유하고, 독점하려 들며, 질투에 미쳐있는 등장인물의 특성이 도드라지는 이야기",
        "common_combinations": ["갑을관계", "삼각관계", "운명적사랑"],
        "typical_genre": ["치정로맨스", "현대로맨스"],
        "applicable_4husbands": True,  # ★ 질투의 화염 EP13
    },
    "여공남수": {
        "definition": "여자가 공격, 남자가 수비. 주로 섹스 묘사에서 여자가 주도하며 남자가 당하는 듯한 이야기",
        "common_combinations": ["소유욕_독점욕_질투"],
        "typical_genre": ["치정로맨스", "BL"],
    },
    "금단의관계": {
        "definition": "사회 규범상 사랑을 이루기 어려운 관계가 나오는 이야기",
        "common_combinations": ["사제지간", "신분차이", "비밀연애"],
        "typical_genre": ["치정로맨스", "로판"],
    },
    "운명적사랑": {
        "definition": "등장인물의 사랑이 운명적 관계라고 설명되는 경우",
        "common_combinations": ["재회물", "첫사랑", "삼각관계"],
        "typical_genre": ["로판", "현대로맨스", "치정로맨스"],
        "applicable_4husbands": True,  # ★ 김지훈과의 운명 — 메인 라인
    },
    "키재기_키빠짐": {
        "definition": "주인공의 키 차이가 크게 강조되는 관계성. 보통 남주가 압도적으로 큼",
        "common_combinations": ["갑을관계", "소유욕_독점욕_질투"],
        "typical_genre": ["로판", "현대로맨스"],
    },
}

# ============================================================================
# ROMANCE_FORMULAS — 6종 장르 포뮬러 (★ v3.0 척추)
# ============================================================================
# 용도: 작품의 메인/보조 포뮬러 태그. 1~2개 결합 권장.
# 강제 주입: 모든 회차 집필 프롬프트에 메인 포뮬러의 다이어그램·표상 모티프 주입.

ROMANCE_FORMULAS = {
    "절대적_지배물": {
        "definition": "남주의 결핍을 채워줄 요소를 여주가 가지고 있음. 권력 차이 + 결핍 채움 구조",
        "core_mechanism": "남자 주인공이 갖고 있는 결핍을 여자 주인공이 채워줄 수 있다",
        "story_diagram": [
            "결핍 가진 절대 권력자 남주 + 그 결핍을 채울 수 있는 여주",
            "→ 강제적 만남 또는 일방적 점유",
            "→ 남주의 일방적 점유, 여주의 저항/적응",
            "→ 결핍 채움 + 감정 형성 (강제성이 점차 애정으로)",
            "→ 권력 관계 유지 또는 변형",
            "→ 해피엔드"
        ],
        "representative_motifs": ["갑을관계", "신분차이", "계약연애_결혼", "소유욕_독점욕_질투", "정략결혼"],
        "title_pattern_keywords": ["순종", "지배", "독", "구속", "도버맨", "훼손", "임신계약", "반쪽"],
        "representative_works": [
            "임신 계약 (달케이크, 2018)",
            "화제의 여학생 (연초, 2018)",
            "훼손 (달로, 2019)",
            "반쪽 (횸횸, 2020)",
            "도버맨 (횸횸, 2021)",
            "내게 빌어봐 (리베냐, 2022)",
            "욕패도 (교결, 2022)"
        ],
        "representative_authors": ["횸횸", "달케이크", "이른꽃", "리베냐"],
        "market_position": "치정 로맨스의 주력 포뮬러. 19금 강한 결합 빈도 높음",
        "platform_strength": ["리디", "카카오페이지 19+"],
        "applicable_4husbands": False,
    },
    
    "목가적_힐링물": {
        "definition": "도시 상처 여주 + 시골 유유자적 남주 → 환경 차이로 이별 위기 → 남주 애정으로 결핍 치유",
        "core_mechanism": "남주의 애정이 여주의 결핍과 상처를 치유하면서 두 사람은 사랑을 완성한다 (부분적 구원 서사)",
        "story_diagram": [
            "도시 상처 여주 + 시골 유유자적 남주",
            "→ 우연한 만남 또는 재회 (시골이 고향/조부모 연고)",
            "→ 여주의 무관심, 남주의 일방적 애정",
            "→ 환경 차이로 이별 위기 (여주가 시골 떠날 때)",
            "→ 남주 애정으로 여주 결핍·상처 치유",
            "→ 해피엔드"
        ],
        "representative_motifs": ["재회물", "첫사랑", "운명적사랑"],
        "title_pattern_keywords": ["겨울", "봄", "가을", "여름", "눈", "비", "꽃", "살구골", "겨울 문방구"],
        "representative_works": [
            "그 겨울의 순정", "만추여관", "나의 살구골에게", "겨울 문방구",
            "비겁한 너의 겨울은", "가을이 머물던 밤", "서랍 속 청개구리",
            "애프터 레인", "봄과 꽃"
        ],
        "representative_authors": ["백선암"],
        "market_position": "현대로맨스 힐링 분야",
        "applicable_4husbands": False,
    },
    
    "도시적_갈등물": {
        "definition": "능력녀 여주 + 재벌남 남주, 사내 만남, 시너지 결말",
        "core_mechanism": "능력녀의 능력과 재벌남의 재력이 시너지를 일으키며 둘 다 성장",
        "story_diagram": [
            "능력녀 여주 (바쁜 소시민 일상) + 재벌남 남주 (더 바쁜 재벌 일상)",
            "→ 사내 만남",
            "→ 경외와 무시, 그리고 (쌍방 애정선 / 일방 애정선 / 혐오 관계) 중 하나",
            "→ 사건 발생",
            "→ (견고한 감정선 유지 / 이별 위기 / 이별과 동시에 감정 자각) 중 하나",
            "→ 남주의 재력 + 여주의 능력 시너지",
            "→ 해피엔드"
        ],
        "representative_motifs": ["사내연애", "갑을관계", "라이벌_앙숙"],
        "title_pattern_keywords": ["전무", "본부장", "이사", "비서", "신입사원"],
        "market_position": "현대로맨스 베스트셀러 대표 포뮬러",
        "platform_strength": ["카카오페이지", "네이버시리즈"],
        "applicable_4husbands": False,  # 사내연애 아님
    },
    
    "운명적_인연물": {
        "definition": "전문직 주인공의 심리 깊이 + 상류사회 관계망 + 운명적 사랑",
        "core_mechanism": "사회적 장애를 운명적 끌림이 극복",
        "story_diagram": [
            "전문직 여주 + 상류사회 남주",
            "→ 우연한 마주침",
            "→ 운명적 끌림 (이성적 거부 시도)",
            "→ 사회적 장애 (신분/위치/과거)",
            "→ 운명 인정 또는 거부",
            "→ 사회적 장애 극복",
            "→ 해피엔드"
        ],
        "representative_motifs": ["운명적사랑", "신분차이", "재회물"],
        "title_pattern_keywords": ["훼손", "세상의 끝", "결혼의 의무"],
        "representative_works": [
            "훼손 (달로, 2019)",
            "세상의 끝 (달로, 2021)",
            "결혼의 의무 (달로, 2021)"
        ],
        "representative_authors": ["달로"],
        "author_motifs_wordcloud": [
            "절륜남", "재벌남", "직진남", "능력녀", "전문직", "유혹남",
            "소유욕_독점욕_질투", "후회남", "상처녀", "집착남",
            "다정남", "능글남", "뇌섹남", "외국인_혼혈", "이야기 중심형",
            "달달물", "스포츠물", "재회물", "고수위", "오해", "연하남"
        ],
        "market_position": "현대로맨스 + 치정 결합형. 카카오/리디 양쪽 강세",
        "applicable_4husbands": True,  # ★ 메인 포뮬러
        "_4husbands_notes": "김지훈 ↔ 한시호 라인이 정확히 운명적_인연물 다이어그램. EP3 신비한 단골 → EP38 진짜 첫 만남 → EP41 첫 데이트 → EP42 한시호라는 이름의 곡",
    },
    
    "금단의_성장물": {
        "definition": "폐쇄 공간(고등학교/대학교/법원/경찰서/병원) + 선후배·멘토멘티·사제 관계 → 수직 상하 → 위기 → 정신적 뒷받침 → 둘 다 성장",
        "core_mechanism": "사랑해서는 안 되는 상대를 사랑함으로 인해 각각의 성장 서사를 완성",
        "story_diagram": [
            "폐쇄 공간(학교/병원/법원 등)에서 사제·선후배·멘토멘티 관계 시작",
            "→ 수직 상하 관계, 남주 우위",
            "→ 어리숙한 후배/멘티/제자 → 가르침 제공자(선배/멘토/스승)에 호감",
            "→ 짝사랑 → 욕망에 이끌린 연애선",
            "→ 여주 위기 (돌이키지 못할 실수)",
            "→ 남주의 정신적 뒷받침 + 길잡이",
            "→ 둘 다 지적/업무적/인격적 성장",
            "→ 해피엔드"
        ],
        "representative_motifs": ["사제지간", "사내연애", "금단의관계", "비밀연애"],
        "title_pattern_keywords": ["선생", "교수", "검사", "의사", "변호사"],
        "market_position": "현대로맨스 + 로판 양쪽에 결합",
        "applicable_4husbands": False,
    },
    
    "갑을관계_파괴물": {
        "definition": "계약상 갑/을 관계 시작 → 계약 파기 → 갑을 관계 전복 → 해피엔드",
        "core_mechanism": "초기 갑을관계가 점차 동등 관계로 전복되며 권력의 재분배 발생",
        "story_diagram": [
            "계약서 상 을 여주 (금전·남자 등 필요) + 계약서 상 갑 남주 (관계·여자 등 필요)",
            "→ 계약으로 맺어진 만남",
            "→ 경계와 충동",
            "→ (쌍방 애정선 / 일방 애정선 / 혐오 관계) 중 하나",
            "→ 계약 파기",
            "→ (견고한 감정선 / 이별 위기 / 이별과 동시 감정 자각) 중 하나",
            "→ 갑을 관계의 전복",
            "→ 해피엔드"
        ],
        "representative_motifs": ["계약연애_결혼", "정략결혼", "갑을관계", "소유욕_독점욕_질투"],
        "title_pattern_keywords": ["계약", "정략", "거래", "약정"],
        "market_position": "현대로맨스 + 치정 결합형",
        "applicable_4husbands": True,  # ★ 보조 포뮬러
        "_4husbands_notes": "4명의 전남편들이 유빈에게 가졌던 권력관계의 전복. EP2-EP6-EP30-EP40 라인",
    },
}


# ============================================================================
# MOVEMENT_NARRATIVE_PATTERNS — 5종 이동 계열 서사
# ============================================================================
# 용도: 이동 계열 작품의 첫 몇 회차 가이드. 한국 3종 + 일본 2종.
# 강제 주입: 이동 코드가 있는 작품의 EP1-3에 first_act_pattern 주입.

MOVEMENT_NARRATIVE_PATTERNS = {
    "회귀": {
        "definition": "동일 인물이 시간을 거슬러 과거의 자신으로 돌아감",
        "origin": "한국형. 성취·목표 지향",
        "trigger_typical": ["죽음 직전", "절망 순간", "치명적 후회", "배신"],
        "first_act_pattern": "회귀 직후 자각 + 미래 지식 활용 결심 + 즉각적 행동 시작",
        "middle_pattern": "미래 정보 비대칭성 활용 → 빠른 성취 → 사이다",
        "ending_pattern": "원래 시점 도달 + 결과 변경 + 강자 등극",
        "market_examples": [
            "재벌집 막내아들 (회귀물)",
            "검은머리 미군 대원수 (대체역사+회귀)"
        ],
        "applicable_genres": ["현대판타지", "퓨전판타지", "대체역사", "회귀+로맨스"],
    },
    
    "빙의": {
        "definition": "주인공의 정신/영혼이 다른 인물의 몸으로 이동",
        "origin": "한국형 + 일본형 혼합",
        "trigger_typical": ["사고", "병", "원작 작품 속 인물 빙의"],
        "first_act_pattern": "빙의 직후 정체성 혼란 + 새 몸의 사회적 위치 파악 + 적응 결심",
        "middle_pattern": "원작 지식 활용 또는 새 몸의 능력 발견 → 원작 변형",
        "ending_pattern": "원래 자아 회복 또는 새 자아 수용",
        "market_examples": [
            "전지적 독자 시점 (빙의물+데스게임물+성좌물+시스템물)",
            "백작가의 망나니가 되었다 (빙의물+착각계+망나니물)",
            "악녀는 마리오네트 (로판 빙의)"
        ],
        "applicable_genres": ["현대판타지", "로판", "퓨전판타지", "빙의+로맨스"],
        "applicable_4husbands": True,  # ★ 4명의 전남편들 핵심 코드
        "_4husbands_notes": "한시호의 정신이 유빈의 몸에 들어감. EP1-2 빙의 직후 정체성 혼란기. 단, 원작 작품 빙의가 아니라 *현실 인물 → 다른 현실 인물* 빙의의 변형",
    },
    
    "환생": {
        "definition": "주인공이 죽은 후 새로운 인물로 다시 태어남 (보통 어린 시절부터)",
        "origin": "한국형",
        "trigger_typical": ["사고사", "병사", "살해", "자살"],
        "first_act_pattern": "새 인생 자각 + 전생 기억 활용 + 어린 몸으로 미래 준비",
        "middle_pattern": "전생 정보 활용 + 새 인생의 역량 구축",
        "ending_pattern": "전생의 한 풀기 + 새 인생 정착 + 강자 등극",
        "market_examples": [
            "황제의 외동딸 (로판 환생물)",
            "검은머리 미군 대원수 일부 (대체역사+회귀+환생)"
        ],
        "applicable_genres": ["로판", "현대판타지", "퓨전판타지"],
    },
    
    "전생": {
        "definition": "이세계로 새로운 인물로 태어남",
        "origin": "일본형 (이세계 전생물)",
        "trigger_typical": ["급사", "사고사", "병사"],
        "first_act_pattern": "이세계 적응 + 능력 발견 (마법·검술·시스템 등)",
        "middle_pattern": "이세계 사회 진입 + 강자로 부상",
        "ending_pattern": "이세계 정착 + 영웅·왕·신 등극",
        "market_examples": ["전생했더니 슬라임이었던 건에 대하여"],
        "applicable_genres": ["퓨전판타지", "정통판타지"],
    },
    
    "전이": {
        "definition": "현세 그대로의 몸이 이세계로 이동",
        "origin": "일본형 (이세계 전이물)",
        "trigger_typical": ["갑작스러운 소환", "사고", "차원 균열"],
        "first_act_pattern": "이세계 도착 + 현세 지식·기술 활용",
        "middle_pattern": "현세 지식으로 이세계 변혁",
        "ending_pattern": "이세계 영웅화 또는 귀환",
        "market_examples": ["이세계물 일반"],
        "applicable_genres": ["퓨전판타지", "정통판타지"],
    },
}


# ============================================================================
# HIGH_RATING_ROMANCE_MOTIFS — 고수위 5종 서사 모티프
# ============================================================================
# 분석 대상: 리디 평점 4.0+ 리뷰 3000+ 70편
# 용도: 19금 치정 로맨스 작품의 모티프 결합 가이드.

HIGH_RATING_ROMANCE_MOTIFS = {
    "강압_관계_모티프": {
        "definition": "신분/경제력/물리력/사회적 지위의 다층적 권력 불균형 → 초기 강제성이 점차 애정으로 전환",
        "key_principle": "초기 강제성이 점차 애정으로 전환되는 과정 자체가 핵심",
        "safety_devices": ["계약 결혼", "신분제", "판타지 세계관"],
        "common_combinations": ["성적_취향_모티프", "특수_세계관_모티프"],
        "representative_works": [
            "임신 계약 (달케이크 2018)", "도버맨 (횸횸 2021)",
            "반쪽 (횸횸 2020)", "내게 빌어봐 (리베냐 2022)"
        ],
    },
    
    "성적_취향_모티프": {
        "definition": "BDSM·페티시 같은 비주류 성적 선호가 서사의 중심 동력. 합의 아래 이뤄지며 주체의 욕망과 합치",
        "key_principle": "행위가 합의 아래 이뤄지며 주체의 욕망과 합치한다 (강압과의 차이점)",
        "safety_devices": ["합의된 규칙", "세이프워드"],
        "common_combinations": ["일탈적_성애_모티프"],
        "representative_works": [
            "우아한 공작님의 조교법 (에이비 2016)",
            "내가 M이라니 (죄송한취향 2021)",
            "젖과 꿀과 아가씨 (박수정 2021)"
        ],
    },
    
    "일탈적_성애_모티프": {
        "definition": "사회 규범 벗어난 관계. 만남 → 육체적 교류 → 낭만적 사랑 역순 구조",
        "key_principle": "만남 → 육체적 교류 → 낭만적 사랑 역순 (전통 로맨스: 만남 → 사랑 → 육체)",
        "common_combinations": ["금기_성애_모티프"],
        "representative_works": [
            "원나잇 후 재회물 일반",
            "오빠 친구 밀착 체험기"
        ],
    },
    
    "금기_성애_모티프": {
        "definition": "관계 자체가 터부 — 근친·새어머니/의붓아들·형제 공유 등",
        "key_principle": "본능에 의한 위반 변명 + 방문 너머 일상 공존이 만드는 헤테로토피아",
        "safety_devices": ["오메가버스 생물학적 본능", "혈연 아닌 의붓 관계"],
        "common_combinations": ["일탈적_성애_모티프", "특수_세계관_모티프"],
        "representative_works": [
            "마더 올가 (새어머니-의붓아들 + 형제 공유 다자연애)"
        ],
    },
    
    "특수_세계관_모티프": {
        "definition": "판타지 설정이 서사적 면죄부 제공 — 오메가버스, 게임 빙의, 회귀 등",
        "key_principle": "세계관 법칙 자체가 위반의 정당성. 가장 정교한 헤테로토피아 형태",
        "safety_devices": ["오메가버스 발정기", "게임 시스템 강제", "회귀 반복 합의"],
        "common_combinations": ["강압_관계_모티프", "금기_성애_모티프"],
        "representative_works": [
            "피폐 역하렘 게임에 갇혀 버렸다 (도위 2016)",
            "메리 배드 엔딩을 위한 공략집 (프레티아 2021)",
            "키스 앤 체이스 (김살구 2020)",
            "딜 브레이커 (리베냐 2022)"
        ],
    },
}


# ============================================================================
# EROTICISM_PRINCIPLES — 고수위 작동 3요소 (시스템 프롬프트)
# ============================================================================
# 용도: 19금 작품 집필 시 시스템 프롬프트에 강제 주입
# 주의: 학술 용어 풀어쓰기 적용 (장르 오인 방지)

EROTICISM_PRINCIPLES_PROMPT = """[★ 19금 치정 로맨스 — 작동 원리 ★]

본 장르의 핵심은 단순한 성적 자극의 나열이 아니라,
세 가지 요소의 유기적 결합이다.

1. 금기와 위반의 강한 자극
   - 사회적·도덕적 금기를 의도적으로 침범할 때 강한 자극 발생
   - 권력/신분 차이의 강압, 다자연애, 집단 성애, 불륜, 근친 등
   - 위반할 금기가 없는 직설적 성애는 약함
   - 계약 결혼·신분제·판타지 세계관 같은 형식적 안전장치를 통해 위반을 정당화

2. 여성 독자 능동성
   - 타겟 페르소나는 여성. 여성 독자를 욕망의 능동적 주체로 설정
   - 서사 속 여주가 수동적이어도 독자는 능동적으로 텍스트를 통제
   - 남성 시선의 성적 자극 나열은 약함

3. 안전 공간 (격리된 판타지 영역)
   - 웹·모바일이 만든 격리된 안전 공간
   - 현실 윤리가 일시 유예되어 죄책감 없이 소비 가능
   - 안전 공간이 약하면 강한 금기 위반은 거부감으로 전환됨

★ 세 요소 중 하나라도 약하면 작품이 무너진다.

[안티패턴]
- A20 — 금기 없는 성애: 위반할 사회적·도덕적 금기 없이 직설적 성애만 묘사
- A21 — 남성 시선 답습: 여성 독자가 능동 주체임을 잊고 시선을 외부에 둠
- A22 — 안전 공간 깨기: 현실 윤리·도덕을 작중에서 정색하고 비판하면 몰입 붕괴
"""


# ============================================================================
# ROFAN_SUBGENRES — 로판 세부장르 통합 (3대 하위장르 + 보조 분류)
# ============================================================================
# 용도: 로판 작품 기획 시 세부장르 매핑

ROFAN_SUBGENRES = {
    # 메인 분류 (성장물/복수물/치유물)
    "성장물": {
        "core_strategy": "성장을 지연하는 성장 서사",
        "key_principle": "주인공이 한 번에 성장하지 않고, 성장 → 시련 → 후퇴 → 재성장 반복",
        "typical_pattern": "어린 여주 → 능력 각성 → 시련 → 성장 → 다음 시련 → 더 큰 성장",
        "applicable_4husbands": False,
    },
    "복수물": {
        "core_strategy": "복수를 가속하는 회귀 서사",
        "key_principle": "회귀 후 즉각적 복수 시작. 복수 동력은 미래 지식",
        "typical_pattern": "회귀 → 즉각 결단 → 복수 가속 → 시원한 응징",
        "applicable_4husbands": False,
    },
    "치유물": {
        "core_strategy": "자립을 유도하는 애정 서사",
        "key_principle": "남주의 애정이 여주의 자립을 돕는 도구. 의존이 아니라 자립을 향함",
        "typical_pattern": "상처 입은 여주 → 남주의 애정 (강압 아닌 지지) → 여주의 자기 회복",
        "applicable_4husbands": True,  # ★ 부분 차용
        "_4husbands_notes": "EP37-EP42에서 김지훈의 애정이 한시호의 자립(자기 정체성 회복)을 돕는 흐름과 일치",
    },
    
    # 보조 분류 (여성영웅물/신데렐라활용/영애물)
    "여성영웅물": {
        "core_strategy": "여성 영웅의 능동적 활약",
        "key_principle": "여성성을 긍정하면서 남성 영역을 침범 (정치·전쟁·기사도)",
        "applicable_4husbands": False,
    },
    "신데렐라_변주": {
        "core_strategy": "전통 신데렐라의 능동성 강화",
        "key_principle": "구원받는 신데렐라가 아니라 스스로 일어서는 여주",
        "applicable_4husbands": False,
    },
    "영애물": {
        "core_strategy": "귀족 영애의 사회적 위치 활용",
        "key_principle": "신분 권력 + 영애의 영민함 결합",
        "applicable_4husbands": False,
    },
}


# ============================================================================
# 헬퍼 함수
# ============================================================================

def get_motif_definition(motif_name: str) -> str:
    """단일 모티프의 정의 반환 (집필 프롬프트 주입용)."""
    motif = RELATIONSHIP_MOTIFS_DICT.get(motif_name)
    if not motif:
        return ""
    return motif["definition"]


def get_formula_diagram(formula_name: str) -> list:
    """포뮬러의 스토리 다이어그램 반환."""
    formula = ROMANCE_FORMULAS.get(formula_name)
    if not formula:
        return []
    return formula["story_diagram"]


def get_formula_motifs(formula_name: str) -> list:
    """포뮬러의 표상 모티프 반환."""
    formula = ROMANCE_FORMULAS.get(formula_name)
    if not formula:
        return []
    return formula.get("representative_motifs", [])


def get_movement_first_act(movement_code: str) -> str:
    """이동 계열 작품의 첫 act 패턴 반환."""
    pattern = MOVEMENT_NARRATIVE_PATTERNS.get(movement_code)
    if not pattern:
        return ""
    return pattern["first_act_pattern"]


def find_formulas_for_4husbands() -> list:
    """4명의 전남편들에 적용되는 포뮬러 자동 추출."""
    return [
        name for name, formula in ROMANCE_FORMULAS.items()
        if formula.get("applicable_4husbands")
    ]


def find_motifs_for_4husbands() -> list:
    """4명의 전남편들에 적용되는 관계성 모티프 자동 추출."""
    return [
        name for name, motif in RELATIONSHIP_MOTIFS_DICT.items()
        if motif.get("applicable_4husbands")
    ]


# ============================================================================
# 자기 검증 (모듈 import 시 자동 실행)
# ============================================================================

def _validate_module():
    """모듈 데이터 무결성 검증."""
    assert len(RELATIONSHIP_MOTIFS_DICT) >= 22, f"관계성 모티프 부족: {len(RELATIONSHIP_MOTIFS_DICT)}"
    assert len(ROMANCE_FORMULAS) == 6, f"로맨스 포뮬러 6종 아님: {len(ROMANCE_FORMULAS)}"
    assert len(MOVEMENT_NARRATIVE_PATTERNS) == 5, f"이동 코드 5종 아님: {len(MOVEMENT_NARRATIVE_PATTERNS)}"
    assert len(HIGH_RATING_ROMANCE_MOTIFS) == 5, f"고수위 모티프 5종 아님: {len(HIGH_RATING_ROMANCE_MOTIFS)}"
    
    # 4명의 전남편들 매핑 검증
    assert "운명적_인연물" in find_formulas_for_4husbands(), "운명적_인연물 매핑 누락"
    assert "갑을관계_파괴물" in find_formulas_for_4husbands(), "갑을관계_파괴물 매핑 누락"
    
    return True


_validate_module()


if __name__ == "__main__":
    print("=" * 60)
    print("data_motifs.py — 모듈 자가 검증")
    print("=" * 60)
    print(f"관계성 모티프: {len(RELATIONSHIP_MOTIFS_DICT)}종")
    print(f"로맨스 포뮬러: {len(ROMANCE_FORMULAS)}종")
    print(f"이동 계열 서사: {len(MOVEMENT_NARRATIVE_PATTERNS)}종")
    print(f"고수위 모티프: {len(HIGH_RATING_ROMANCE_MOTIFS)}종")
    print(f"로판 세부장르: {len(ROFAN_SUBGENRES)}종")
    print()
    print("[4명의 전남편들 자동 매핑]")
    print(f"  포뮬러: {find_formulas_for_4husbands()}")
    print(f"  관계성 모티프: {find_motifs_for_4husbands()}")
    print()
    print("[운명적_인연물 다이어그램 샘플]")
    for step in get_formula_diagram("운명적_인연물"):
        print(f"  {step}")
    print()
    print("[빙의 first_act_pattern]")
    print(f"  {get_movement_first_act('빙의')}")
    print()
    print("✓ 모든 검증 통과")
