"""
data_motifs.py — Engine v3.4
================================
모티프·포뮬러·이동코드·플롯구조 데이터셋 (v3.4 통합 재구조화)

수록 데이터:
- NARRATIVE_MOTIFS_205 — 8카테고리 통합 모티프 사전 (v3.4 신규, 약 175개)
- LEGACY_MOTIF_MAPPING — v3.0 23종 → v3.4 자동 변환 매핑
- ROMANCE_FORMULAS — 7종 장르 포뮬러 (v3.4: 버디러브 5단계 추가)
- BAD_FIRST_IMPRESSION_PLOT — 안 좋은 첫인상-한 공간 플롯 (v3.4 신규)
- TWO_TIER_CRISIS_STRUCTURE — 1차/2차 위기 구조 (v3.4 신규)
- MOVEMENT_NARRATIVE_PATTERNS — 5종 이동 계열 서사
- HIGH_RATING_ROMANCE_MOTIFS — 고수위 5종 서사 모티프
- ROFAN_SUBGENRES — 로판 3종 세부장르

변경 이력:
- v3.0: 23종 관계성 모티프 + 6종 포뮬러
- v3.4: NARRATIVE_MOTIFS_205로 재구조화 (이인화 스토리헬퍼 분류 체계 기반)
        - 인물/상황/행위 × 돈/사랑/영생/명예/권력 카테고리
        - 버디러브 5단계 포뮬러 추가 (블레이크 스나이더)
        - 안 좋은 첫인상-한 공간 플롯 추가 (백종인 2022 연구)
        - 1차/2차 위기 구조 추가
        - 기존 23종은 LEGACY_MOTIF_MAPPING으로 자동 변환

학술 출처:
- 이인화 (2016), "스토리텔링 진화론" - 205개 모티프 분류 체계
- 백종인 (2022), 공주대 만화학과 석사학위논문
  "드라마화된 로맨스 웹툰의 서사와 플롯에 관한 연구"
- 블레이크 스나이더, "Save The Cat!" - 버디 러브 5단계
- 로널드 B. 토비아스, "인간의 마음을 사로잡는 스무 가지 플롯"
"""

# ============================================================================
# NARRATIVE_MOTIFS_205 (v3.4 신규)
# ============================================================================
# 출처: 이인화 (2016), 백종인 (2022) [표 16]
# 구조: 카테고리 분류 - 인물/상황/행위 카테고리, 약 175종
# 용도: 작품 기획 시 작가가 1~10개 모티프 선택
# 호환: legacy_alias 필드를 통해 v3.0 키 자동 변환

NARRATIVE_MOTIFS_205 = {

    # --- 카테고리: 인물_돈 ---
    "강도": {"category": "인물_돈", "definition": "재산이나 권력을 폭력적으로 빼앗는 인물이 등장하는 이야기", "typical_genre": ["스릴러", "현대로맨스"]},
    "고등 사기꾼": {"category": "인물_돈", "definition": "지능적이고 정교한 사기로 사람을 속이는 인물이 중심에 있는 이야기", "typical_genre": ["로맨스", "스릴러"]},
    "고리대금업자": {"category": "인물_돈", "definition": "고리채로 약자를 옭아매는 인물이 등장하는 이야기", "typical_genre": ["치정로맨스", "현대로맨스"]},
    "도둑": {"category": "인물_돈", "definition": "타인의 물건이나 비밀을 훔치는 인물이 중심에 있는 이야기", "typical_genre": ["로맨스", "스릴러"]},
    "돈을 노리는 유혹자": {"category": "인물_돈", "definition": "재산을 노리고 접근하는 매력적인 유혹자가 등장하는 이야기", "typical_genre": ["치정로맨스", "현대로맨스"]},
    "마약 거래자": {"category": "인물_돈", "definition": "마약 유통에 관여하는 인물이 사랑이나 사건의 중심에 있는 이야기", "typical_genre": ["스릴러", "현대로맨스"]},
    "변장": {"category": "인물_돈", "definition": "정체를 숨기기 위해 외모나 신분을 바꾸는 인물이 등장하는 이야기", "typical_genre": ["로맨스", "사극"]},
    "사이코패스": {"category": "인물_돈", "definition": "공감 능력이 결여된 채 목적을 추구하는 인물이 등장하는 이야기", "typical_genre": ["스릴러", "치정로맨스"]},
    "살인 청부업자": {"category": "인물_돈", "definition": "대가를 받고 살인을 실행하는 인물이 중심에 있는 이야기", "typical_genre": ["스릴러", "현대로맨스"]},
    "야망가": {"category": "인물_돈", "definition": "권력이나 재산에 대한 강한 야망을 가진 인물이 중심에 있는 이야기", "typical_genre": ["현대로맨스", "사극"]},
    "의적": {"category": "인물_돈", "definition": "정의를 위해 강자에게서 빼앗아 약자에게 나누는 인물이 등장하는 이야기", "typical_genre": ["사극", "현대로맨스"]},
    "인질": {"category": "인물_돈", "definition": "협상의 담보로 잡힌 인물을 둘러싼 사건이 진행되는 이야기", "typical_genre": ["스릴러", "현대로맨스"]},
    "파산": {"category": "인물_돈", "definition": "재산을 잃고 무너진 인물이 회복하거나 무너지는 이야기", "typical_genre": ["현대로맨스"]},
    "해적": {"category": "인물_돈", "definition": "바다에서 약탈하거나 자유롭게 사는 인물이 등장하는 이야기", "typical_genre": ["판타지", "사극"]},
    "횡재": {"category": "인물_돈", "definition": "갑작스러운 행운으로 큰 재산을 얻은 인물의 변화 이야기", "typical_genre": ["현대로맨스"]},

    # --- 카테고리: 인물_사랑 ---
    "기억상실증": {"category": "인물_사랑", "definition": "사랑하는 이의 기억을 잃은 인물이 다시 사랑을 찾아가는 이야기", "typical_genre": ["현대로맨스", "치정로맨스"]},
    "도플갱어": {"category": "인물_사랑", "definition": "쌍둥이처럼 똑같이 닮은 두 인물 사이에서 사랑이 진행되는 이야기", "typical_genre": ["로맨스", "스릴러"]},
    "동성애자": {"category": "인물_사랑", "definition": "동성 간의 사랑이 중심에 있는 이야기", "typical_genre": ["BL", "GL"]},
    "뜻밖의 편지": {"category": "인물_사랑", "definition": "예상치 못한 편지가 사랑을 촉발하거나 사건을 바꾸는 이야기", "typical_genre": ["현대로맨스", "사극"]},
    "바람둥이": {"category": "인물_사랑", "definition": "여러 상대와 가볍게 관계를 맺던 인물이 한 사람에게 정착하는 이야기", "typical_genre": ["현대로맨스", "치정로맨스"]},
    "버려진 아이": {"category": "인물_사랑", "definition": "버려진 채 자란 인물이 사랑이나 가족을 찾아가는 이야기", "typical_genre": ["사극", "로판"]},
    "숨겨진 연인": {"category": "인물_사랑", "definition": "비밀스럽게 만나야 하는 관계의 두 사람이 사회·가족과 갈등하는 이야기", "typical_genre": ["치정로맨스", "현대로맨스"]},
    "신분 상승 결혼": {"category": "인물_사랑", "definition": "낮은 신분의 인물이 결혼을 통해 상승하거나, 신분 격차를 극복하는 이야기", "typical_genre": ["현대로맨스", "사극", "로판"], "applicable_4husbands": True},
    "아웃사이더": {"category": "인물_사랑", "definition": "사회에서 배제된 인물이 사랑을 통해 안으로 들어오거나, 자기 자리를 찾아가는 이야기", "typical_genre": ["현대로맨스", "치정로맨스"]},
    "팜므파탈": {"category": "인물_사랑", "definition": "치명적인 매력으로 남성을 파멸로 이끄는 여성 인물이 등장하는 이야기", "typical_genre": ["치정로맨스", "스릴러"]},
    "자폐증": {"category": "인물_사랑", "definition": "자폐 스펙트럼을 가진 인물이 사랑을 통해 세상과 연결되는 이야기", "typical_genre": ["현대로맨스"]},
    "장애인": {"category": "인물_사랑", "definition": "신체·정신 장애가 있는 인물의 사랑과 성장 이야기", "typical_genre": ["현대로맨스"]},
    "지인의 실종": {"category": "인물_사랑", "definition": "사라진 사람을 찾는 과정에서 사랑이나 진실이 밝혀지는 이야기", "typical_genre": ["스릴러", "현대로맨스"]},
    "창녀": {"category": "인물_사랑", "definition": "직업적으로 몸을 팔아온 인물이 진정한 사랑을 만나는 이야기", "typical_genre": ["치정로맨스", "사극"]},
    "피그말리온": {"category": "인물_사랑", "definition": "자신이 만들거나 다듬은 대상에게 사랑을 느끼는 이야기", "typical_genre": ["현대로맨스", "로판"]},
    "학대하는 계모(계부)": {"category": "인물_사랑", "definition": "양육자의 학대를 견디며 자란 인물이 사랑이나 복수를 추구하는 이야기", "typical_genre": ["로판", "사극"]},
    "사랑에 빠진 노인": {"category": "인물_사랑", "definition": "노년에 새로운 사랑을 만난 인물이 인생의 한 챕터를 다시 여는 이야기", "typical_genre": ["현대로맨스"]},

    # --- 카테고리: 인물_영생 ---
    "고귀한 창녀": {"category": "인물_영생", "definition": "직업은 천하지만 영혼은 고귀한 여성 인물의 이야기", "typical_genre": ["사극", "치정로맨스"]},
    "고귀한 하녀": {"category": "인물_영생", "definition": "신분은 낮으나 본디 고귀한 출신이거나 영혼이 귀한 인물의 이야기", "typical_genre": ["사극", "로판"], "applicable_4husbands": True},
    "고상한 야만인": {"category": "인물_영생", "definition": "교양 없는 듯 보이나 본질은 순수하고 고귀한 인물의 이야기", "typical_genre": ["판타지", "사극"]},
    "기이한 선생": {"category": "인물_영생", "definition": "독특한 가르침을 주는 비범한 스승 인물이 등장하는 이야기", "typical_genre": ["판타지", "현대로맨스"]},
    "다중인격": {"category": "인물_영생", "definition": "한 몸에 여러 인격을 가진 인물이 사랑이나 사건의 중심에 있는 이야기", "typical_genre": ["스릴러", "치정로맨스"]},
    "똑똑한 바보": {"category": "인물_영생", "definition": "어리석어 보이지만 본질적 지혜를 가진 인물의 이야기", "typical_genre": ["현대로맨스", "코미디"]},
    "몰락한 귀족": {"category": "인물_영생", "definition": "가문이 무너진 귀족이 재기하거나 새 사랑을 만나는 이야기", "typical_genre": ["사극", "로판"]},
    "불우한 천재": {"category": "인물_영생", "definition": "비범한 재능을 가졌으나 환경이 받쳐주지 못해 좌절하는 인물의 이야기", "typical_genre": ["현대로맨스", "사극"]},
    "소년 영웅": {"category": "인물_영생", "definition": "어린 나이에 큰 책임을 짊어진 인물의 성장 이야기", "typical_genre": ["판타지", "사극"]},
    "순교자": {"category": "인물_영생", "definition": "신념을 위해 자신을 희생하는 인물의 이야기", "typical_genre": ["사극", "치정로맨스"]},
    "악동": {"category": "인물_영생", "definition": "장난스러운 겉모습 뒤에 깊이를 가진 인물의 이야기", "typical_genre": ["현대로맨스", "코미디"]},
    "악마적인 예술가": {"category": "인물_영생", "definition": "재능에 사로잡혀 도덕을 넘어서는 예술가 인물의 이야기", "typical_genre": ["치정로맨스", "스릴러"]},
    "처녀 영웅": {"category": "인물_영생", "definition": "순결과 강인함을 동시에 가진 여성 영웅의 이야기", "typical_genre": ["판타지", "사극"]},

    # --- 카테고리: 인물_권력 ---
    "가문의 여주인": {"category": "인물_권력", "definition": "가문의 운명을 짊어진 여성 인물의 이야기", "typical_genre": ["사극", "로판"]},
    "고뇌하는 깡패": {"category": "인물_권력", "definition": "어두운 세계에 속했으나 양심과 갈등하는 인물의 이야기", "typical_genre": ["치정로맨스", "스릴러"]},
    "덜떨어진 영웅": {"category": "인물_권력", "definition": "겉보기엔 부족하나 결정적 순간에 영웅이 되는 인물의 이야기", "typical_genre": ["현대로맨스", "코미디"]},
    "독재정치": {"category": "인물_권력", "definition": "한 인물이 절대권력을 행사하는 사회에서 펼쳐지는 사랑과 저항의 이야기", "typical_genre": ["사극", "판타지"]},
    "미지의 후견인": {"category": "인물_권력", "definition": "정체를 숨긴 채 주인공을 돕는 후견인이 등장하는 이야기", "typical_genre": ["사극", "로판"]},
    "배반자": {"category": "인물_권력", "definition": "신뢰받던 인물이 등을 돌리며 사건을 뒤집는 이야기", "typical_genre": ["사극", "스릴러"]},
    "부패 경찰": {"category": "인물_권력", "definition": "공권력 내부의 부패가 사랑이나 사건의 중심에 있는 이야기", "typical_genre": ["스릴러", "치정로맨스"]},
    "신분 위장": {"category": "인물_권력", "definition": "신분을 숨기거나 다른 신분으로 위장하며 진행되는 이야기", "typical_genre": ["사극", "로판"]},
    "우월한 하급자": {"category": "인물_권력", "definition": "지위는 낮으나 능력이나 인격이 상사를 능가하는 인물의 이야기", "typical_genre": ["현대로맨스"]},
    "운명에 대한 반역": {"category": "인물_권력", "definition": "정해진 운명에 맞서 자기 길을 가는 인물의 이야기", "typical_genre": ["판타지", "사극"]},
    "전쟁 포로": {"category": "인물_권력", "definition": "전쟁에서 포로가 된 인물의 사랑과 생존 이야기", "typical_genre": ["사극", "치정로맨스"]},
    "출세주의자": {"category": "인물_권력", "definition": "오로지 출세를 위해 모든 것을 거는 인물의 이야기", "typical_genre": ["현대로맨스"]},
    "불청객": {"category": "인물_권력", "definition": "초대받지 않은 인물이 등장해 사건을 일으키는 이야기", "typical_genre": ["현대로맨스", "스릴러"]},

    # --- 카테고리: 상황_사랑 ---
    "사랑하는 이의 죽음": {"category": "상황_사랑", "definition": "사랑하는 사람을 잃은 인물의 슬픔과 회복의 이야기", "typical_genre": ["현대로맨스", "치정로맨스"], "applicable_4husbands": True},
    "조난": {"category": "상황_사랑", "definition": "낯선 환경에 고립된 두 인물 사이에 사랑이 싹트는 이야기", "typical_genre": ["로맨스", "판타지"]},
    "불면증": {"category": "상황_사랑", "definition": "잠 못 이루는 밤이 만남과 사랑을 만드는 이야기", "typical_genre": ["현대로맨스"]},
    "아동학대": {"category": "상황_사랑", "definition": "어린 시절 학대의 트라우마를 가진 인물이 사랑을 통해 치유되는 이야기", "typical_genre": ["현대로맨스", "치정로맨스"]},
    "연인 상실": {"category": "상황_사랑", "definition": "사랑하는 연인을 잃은 인물의 새로운 시작 이야기", "typical_genre": ["현대로맨스"]},
    "외상 후 스트레스 장애": {"category": "상황_사랑", "definition": "트라우마를 가진 인물이 사랑을 통해 회복하는 이야기", "typical_genre": ["현대로맨스", "치정로맨스"]},
    "우울증": {"category": "상황_사랑", "definition": "우울을 안고 사는 인물이 사랑을 통해 빛을 찾는 이야기", "typical_genre": ["현대로맨스"]},
    "청소년기 일탈": {"category": "상황_사랑", "definition": "방황하던 청소년이 사랑과 만남을 통해 자기 길을 찾는 이야기", "typical_genre": ["현대로맨스"]},
    "옛 연인의 출현": {"category": "상황_사랑", "definition": "헤어졌던 연인이 다시 나타나 흔들리는 관계의 이야기", "typical_genre": ["현대로맨스", "치정로맨스"], "legacy_alias": "재회물"},
    "가족 분열(이산가족)": {"category": "상황_사랑", "definition": "가족이 흩어진 채 살아온 인물의 재회 이야기", "typical_genre": ["사극", "현대로맨스"]},
    "간통": {"category": "상황_사랑", "definition": "기혼자 간의 금지된 사랑이 사건을 일으키는 이야기", "typical_genre": ["치정로맨스"]},
    "계급을 초월한 사랑": {"category": "상황_사랑", "definition": "사회적 계급의 격차를 뛰어넘는 사랑의 이야기", "typical_genre": ["사극", "치정로맨스"], "legacy_alias": "신분차이"},
    "관음증": {"category": "상황_사랑", "definition": "타인을 몰래 관찰하는 행위가 사랑이나 사건의 중심에 있는 이야기", "typical_genre": ["치정로맨스", "스릴러"]},
    "광기 어린 사랑": {"category": "상황_사랑", "definition": "이성을 잃을 정도로 강렬한 사랑이 인물을 사로잡는 이야기", "typical_genre": ["치정로맨스"]},
    "구혼 시험": {"category": "상황_사랑", "definition": "사랑을 얻기 위해 시험을 통과해야 하는 인물의 이야기", "typical_genre": ["사극", "판타지"]},
    "근친상간": {"category": "상황_사랑", "definition": "혈연 간의 금지된 사랑이 비극을 만드는 이야기", "typical_genre": ["치정로맨스", "사극"]},
    "나쁜 남자에게 반하기": {"category": "상황_사랑", "definition": "위험한 남성에게 끌리는 여성의 이야기", "typical_genre": ["치정로맨스", "현대로맨스"]},
    "나이 차를 극복한 사랑": {"category": "상황_사랑", "definition": "나이 차가 큰 두 인물의 사랑 이야기", "typical_genre": ["현대로맨스", "치정로맨스"], "legacy_alias": "나이차커플"},
    "동물과의 우정": {"category": "상황_사랑", "definition": "동물과 깊은 유대를 맺은 인물의 이야기", "typical_genre": ["현대로맨스", "판타지"]},
    "롤리타": {"category": "상황_사랑", "definition": "어린 소녀에 대한 성인의 집착이 사건을 만드는 이야기", "typical_genre": ["치정로맨스"]},
    "마조히즘": {"category": "상황_사랑", "definition": "고통과 굴종에서 쾌락을 느끼는 인물의 이야기", "typical_genre": ["치정로맨스"]},
    "백치 미인": {"category": "상황_사랑", "definition": "외모는 빛나나 순진한 면이 강조되는 인물의 이야기", "typical_genre": ["현대로맨스", "코미디"]},
    "사디즘": {"category": "상황_사랑", "definition": "타인에게 고통을 주며 쾌락을 느끼는 인물의 이야기", "typical_genre": ["치정로맨스"]},
    "사랑의 연기": {"category": "상황_사랑", "definition": "사랑하는 척하다가 진짜 사랑이 되는 이야기 (계약연애 포함)", "typical_genre": ["현대로맨스", "치정로맨스"], "legacy_alias": "계약연애_결혼"},
    "삼각관계": {"category": "상황_사랑", "definition": "세 인물 사이의 사랑이 얽혀 갈등을 만드는 이야기", "typical_genre": ["현대로맨스", "치정로맨스", "로판"], "applicable_4husbands": True},
    "성생활 장애": {"category": "상황_사랑", "definition": "성적 어려움을 가진 인물이 사랑을 통해 극복하는 이야기", "typical_genre": ["치정로맨스"]},
    "세대를 초월한 우정": {"category": "상황_사랑", "definition": "큰 나이 차이의 두 인물이 깊은 우정이나 사랑을 나누는 이야기", "typical_genre": ["현대로맨스"]},
    "스와핑": {"category": "상황_사랑", "definition": "두 커플이 서로 파트너를 바꾸는 행위가 사건을 일으키는 이야기", "typical_genre": ["치정로맨스"]},
    "스토킹": {"category": "상황_사랑", "definition": "집착적으로 한 사람을 따라다니는 행위가 사건의 중심에 있는 이야기", "typical_genre": ["스릴러", "치정로맨스"]},
    "시라노 콤플렉스": {"category": "상황_사랑", "definition": "자신의 외모에 자신 없어 다른 사람을 대신 내세우는 인물의 이야기", "typical_genre": ["현대로맨스"]},
    "아름다운 불륜": {"category": "상황_사랑", "definition": "사회적으로는 비난받지만 절절한 감정이 있는 외도의 이야기", "typical_genre": ["치정로맨스"]},
    "위험한 비밀 결혼": {"category": "상황_사랑", "definition": "들키면 위험한 결혼을 비밀로 유지하는 두 사람의 이야기", "typical_genre": ["사극", "치정로맨스"], "legacy_alias": "비밀연애"},
    "엘렉트라 콤플렉스": {"category": "상황_사랑", "definition": "아버지에 대한 강한 애착을 가진 여성 인물의 이야기", "typical_genre": ["치정로맨스"]},
    "적과의 사랑": {"category": "상황_사랑", "definition": "원수나 적대 관계의 두 인물이 사랑에 빠지는 이야기", "typical_genre": ["사극", "현대로맨스"], "legacy_alias": "라이벌_앙숙"},
    "적군과의 우정": {"category": "상황_사랑", "definition": "전쟁의 양 진영에 속한 두 인물 사이의 우정 이야기", "typical_genre": ["사극"]},
    "전우 구출": {"category": "상황_사랑", "definition": "위험에 처한 동료를 구하는 과정에서 사랑이 싹트는 이야기", "typical_genre": ["사극", "현대로맨스"]},
    "짝사랑": {"category": "상황_사랑", "definition": "혼자만 사랑하는 인물의 절절한 감정 이야기", "typical_genre": ["현대로맨스", "치정로맨스"]},
    "첫 관계": {"category": "상황_사랑", "definition": "처음으로 신체적 관계를 가진 두 인물의 변화 이야기", "typical_genre": ["치정로맨스", "현대로맨스"], "legacy_alias": "원나잇"},
    "첫눈에 반한 사랑": {"category": "상황_사랑", "definition": "만난 순간 사랑에 빠지는 강렬한 운명적 만남의 이야기", "typical_genre": ["로판", "현대로맨스"], "legacy_alias": "첫사랑"},
    "부부 싸움": {"category": "상황_사랑", "definition": "결혼한 두 사람이 갈등을 겪으며 다시 사랑을 확인하는 이야기", "typical_genre": ["현대로맨스"], "legacy_alias": "오래된연인"},
    "운명적 사랑": {"category": "상황_사랑", "definition": "필연으로 만난 두 사람이 거역할 수 없는 사랑에 빠지는 이야기", "typical_genre": ["로판", "현대로맨스", "치정로맨스"], "legacy_alias": "운명적사랑", "applicable_4husbands": True},

    # --- 카테고리: 상황_명예 ---
    "도제 수련": {"category": "상황_명예", "definition": "스승 아래에서 기술이나 도를 익히는 과정의 이야기", "typical_genre": ["사극", "판타지"], "legacy_alias": "사제지간"},
    "강박증": {"category": "상황_명예", "definition": "강박적 행동에 사로잡힌 인물이 사랑이나 사건을 통해 변화하는 이야기", "typical_genre": ["현대로맨스"]},
    "경계성 인격장애": {"category": "상황_명예", "definition": "정서적 불안정을 가진 인물의 사랑과 회복 이야기", "typical_genre": ["치정로맨스"]},
    "공황장애": {"category": "상황_명예", "definition": "공황 발작을 가진 인물이 사랑을 통해 안정을 찾는 이야기", "typical_genre": ["현대로맨스"]},
    "누명": {"category": "상황_명예", "definition": "억울한 누명을 쓴 인물이 진실을 밝히는 이야기", "typical_genre": ["스릴러", "사극"]},
    "명예 손상": {"category": "상황_명예", "definition": "명예를 잃은 인물이 회복하거나 복수하는 이야기", "typical_genre": ["사극", "현대로맨스"]},
    "성 정체성 혼란": {"category": "상황_명예", "definition": "자신의 성 정체성을 탐색하는 인물의 이야기", "typical_genre": ["현대로맨스", "BL", "GL"]},
    "알코올 중독": {"category": "상황_명예", "definition": "술에 의존하는 인물의 사랑과 회복 이야기", "typical_genre": ["현대로맨스", "치정로맨스"]},
    "중년의 위기": {"category": "상황_명예", "definition": "중년에 인생의 의미를 다시 묻게 된 인물의 이야기", "typical_genre": ["현대로맨스"]},

    # --- 카테고리: 상황_권력 ---
    "감춰진 혈통 찾기": {"category": "상황_권력", "definition": "자신의 진짜 출생 비밀을 찾아가는 인물의 이야기", "typical_genre": ["사극", "로판"]},
    "도망자": {"category": "상황_권력", "definition": "쫓기는 인물이 도망 중에 사랑이나 진실을 만나는 이야기", "typical_genre": ["스릴러", "사극"]},
    "모반": {"category": "상황_권력", "definition": "권력에 맞서 일어나는 음모와 반란의 이야기", "typical_genre": ["사극"]},
    "무장봉기": {"category": "상황_권력", "definition": "민중이 무기를 들고 권력에 맞서는 이야기", "typical_genre": ["사극"]},
    "미결의 살인 사건": {"category": "상황_권력", "definition": "해결되지 않은 살인 사건이 현재를 흔드는 이야기", "typical_genre": ["스릴러"]},
    "복수혈전": {"category": "상황_권력", "definition": "복수를 위해 모든 것을 거는 인물의 이야기", "typical_genre": ["사극", "스릴러"]},
    "부당한 차별": {"category": "상황_권력", "definition": "차별에 맞서 자기 자리를 찾아가는 인물의 이야기", "typical_genre": ["현대로맨스", "사극"]},
    "오이디푸스 콤플렉스": {"category": "상황_권력", "definition": "어머니에 대한 강한 애착을 가진 남성 인물의 이야기", "typical_genre": ["치정로맨스"]},
    "부모 찾기": {"category": "상황_권력", "definition": "헤어진 부모를 찾아가는 인물의 이야기", "typical_genre": ["사극", "현대로맨스"]},
    "의처증(의부증)": {"category": "상황_권력", "definition": "배우자를 의심하는 병적 의심이 사건을 만드는 이야기", "typical_genre": ["치정로맨스", "스릴러"], "legacy_alias": "소유욕_독점욕_질투", "applicable_4husbands": True},
    "이혼": {"category": "상황_권력", "definition": "이혼을 둘러싼 갈등과 새 사랑의 이야기", "typical_genre": ["현대로맨스", "치정로맨스"]},
    "죄의 고백": {"category": "상황_권력", "definition": "오랫동안 숨겨온 죄를 고백하는 인물의 이야기", "typical_genre": ["치정로맨스", "스릴러"]},
    "취향의 재발견": {"category": "상황_권력", "definition": "잊었던 자신의 진짜 취향을 다시 발견하는 인물의 이야기", "typical_genre": ["현대로맨스"]},
    "파계": {"category": "상황_권력", "definition": "종교적 계율을 깨고 사랑이나 욕망을 따르는 인물의 이야기", "typical_genre": ["사극", "치정로맨스"]},
    "귀향": {"category": "상황_권력", "definition": "오랜 시간 떠나 있던 인물이 고향이나 옛 자리로 돌아오는 이야기", "typical_genre": ["현대로맨스", "사극"]},

    # --- 카테고리: 상황_영생 ---
    "무인도 조난": {"category": "상황_영생", "definition": "무인도에 떨어진 두 사람의 사랑과 생존 이야기", "typical_genre": ["로맨스", "판타지"]},
    "노년기 과제": {"category": "상황_영생", "definition": "노년에 풀어야 할 마지막 과제를 가진 인물의 이야기", "typical_genre": ["현대로맨스"]},
    "시한부 선고": {"category": "상황_영생", "definition": "시한부 인생을 선고받은 인물의 사랑과 결단의 이야기", "typical_genre": ["현대로맨스", "치정로맨스"]},
    "예언": {"category": "상황_영생", "definition": "예언에 따라 살거나 예언에 맞서는 인물의 이야기", "typical_genre": ["판타지", "사극"]},
    "빙의": {"category": "상황_영생", "definition": "다른 사람의 몸이나 책 속 인물에 들어간 인물의 이야기", "typical_genre": ["판타지", "로판"], "applicable_4husbands": True},
    "외계인 침입": {"category": "상황_영생", "definition": "외계 존재의 등장이 일상을 뒤흔드는 이야기", "typical_genre": ["SF", "판타지"]},
    "악마와의 계약": {"category": "상황_영생", "definition": "악마와 계약을 맺은 인물이 대가를 치르는 이야기", "typical_genre": ["판타지", "치정로맨스"]},
    "인공 동면": {"category": "상황_영생", "definition": "동면에서 깨어난 인물이 새 시대를 마주하는 이야기", "typical_genre": ["SF"]},
    "지구 종말": {"category": "상황_영생", "definition": "세상의 끝을 앞두고 살아가는 인물의 이야기", "typical_genre": ["SF", "판타지"]},
    "환생": {"category": "상황_영생", "definition": "다시 태어난 인물이 전생의 기억을 가지고 살아가는 이야기", "typical_genre": ["판타지", "로판"], "applicable_4husbands": True},
    "도시 재난": {"category": "상황_영생", "definition": "도시를 덮친 재난 속에서 펼쳐지는 사랑과 생존 이야기", "typical_genre": ["스릴러", "현대로맨스"]},
    "생물학적 재앙": {"category": "상황_영생", "definition": "감염병이나 생물학적 재해 속에서 펼쳐지는 이야기", "typical_genre": ["스릴러", "SF"]},
    "감금": {"category": "상황_영생", "definition": "갇힌 인물이 사랑이나 자유를 찾아가는 이야기", "typical_genre": ["치정로맨스", "스릴러"]},
    "갑작스러운 사고": {"category": "상황_영생", "definition": "예기치 못한 사고가 인물의 삶을 뒤바꾸는 이야기", "typical_genre": ["현대로맨스"]},
    "시간 여행": {"category": "상황_영생", "definition": "다른 시대로 이동한 인물의 사랑과 사건 이야기", "typical_genre": ["판타지", "SF"]},
    "유령": {"category": "상황_영생", "definition": "유령이 된 인물의 미련과 사랑의 이야기", "typical_genre": ["판타지", "치정로맨스"]},
    "이계 방문": {"category": "상황_영생", "definition": "다른 세계로 넘어간 인물의 이야기", "typical_genre": ["판타지", "로판"]},
    "이계 생명체와의 우정": {"category": "상황_영생", "definition": "이세계의 존재와 깊은 유대를 맺은 인물의 이야기", "typical_genre": ["판타지"]},
    "자살": {"category": "상황_영생", "definition": "자살 충동을 가진 인물이 사랑을 통해 회복하는 이야기", "typical_genre": ["현대로맨스", "치정로맨스"]},
    "저주": {"category": "상황_영생", "definition": "저주에 걸린 인물이 풀어가는 과정의 이야기", "typical_genre": ["판타지", "사극"]},
    "저주받은 장소": {"category": "상황_영생", "definition": "저주 받은 공간에서 펼쳐지는 사건과 사랑의 이야기", "typical_genre": ["판타지", "스릴러"]},
    "사람이 된 인형": {"category": "상황_영생", "definition": "인형이 사람이 된 인물의 정체성과 사랑의 이야기", "typical_genre": ["판타지", "로판"]},
    "동반 자살": {"category": "상황_영생", "definition": "두 사람이 함께 죽음을 택하는 비극적 사랑의 이야기", "typical_genre": ["치정로맨스"]},

    # --- 카테고리: 행위_사건 ---
    "강제된 과업": {"category": "행위_사건", "definition": "원치 않는 과업을 떠맡은 인물의 이야기", "typical_genre": ["사극", "판타지"]},
    "거짓된 진술": {"category": "행위_사건", "definition": "거짓 증언이나 진술이 사건을 꼬이게 만드는 이야기", "typical_genre": ["스릴러", "사극"]},
    "고발": {"category": "행위_사건", "definition": "누군가를 고발하는 행위가 사건의 중심에 있는 이야기", "typical_genre": ["스릴러", "현대로맨스"]},
    "도박": {"category": "행위_사건", "definition": "도박에 빠진 인물의 사랑과 파멸의 이야기", "typical_genre": ["치정로맨스", "스릴러"]},
    "보물 찾기": {"category": "행위_사건", "definition": "감춰진 보물을 찾는 모험의 이야기", "typical_genre": ["판타지", "사극"]},
    "수사 의뢰": {"category": "행위_사건", "definition": "수사를 의뢰받은 인물이 사건을 풀어가는 이야기", "typical_genre": ["스릴러"]},
    "수수께끼": {"category": "행위_사건", "definition": "풀어야 할 수수께끼가 인물을 끌어들이는 이야기", "typical_genre": ["스릴러", "판타지"]},
    "아동 유괴": {"category": "행위_사건", "definition": "아이가 유괴된 사건이 사랑이나 진실을 드러내는 이야기", "typical_genre": ["스릴러", "치정로맨스"]},
    "연쇄 살인": {"category": "행위_사건", "definition": "연쇄 살인 사건이 사랑이나 운명을 흔드는 이야기", "typical_genre": ["스릴러"]},
    "오해(착각)": {"category": "행위_사건", "definition": "오해가 사건의 시작과 끝을 좌우하는 이야기", "typical_genre": ["현대로맨스", "치정로맨스"]},
    "우발적 살인": {"category": "행위_사건", "definition": "의도하지 않은 살인이 인물의 삶을 뒤집는 이야기", "typical_genre": ["스릴러", "치정로맨스"]},
    "원 나잇 스탠드": {"category": "행위_사건", "definition": "하룻밤의 만남이 사랑이나 사건의 시작이 되는 이야기", "typical_genre": ["치정로맨스"], "legacy_alias": "몸정맘정"},
    "지리적 고립": {"category": "행위_사건", "definition": "외딴 곳에 갇힌 인물들의 사랑과 사건 이야기", "typical_genre": ["로맨스", "스릴러"]},
    "추격자": {"category": "행위_사건", "definition": "쫓고 쫓기는 관계가 사건의 동력이 되는 이야기", "typical_genre": ["스릴러", "사극"]},
    "테러": {"category": "행위_사건", "definition": "테러가 일상을 뒤흔드는 가운데 펼쳐지는 사랑과 갈등의 이야기", "typical_genre": ["스릴러"]},
    "파업": {"category": "행위_사건", "definition": "파업과 노동 갈등이 사랑이나 사건의 배경이 되는 이야기", "typical_genre": ["현대로맨스"]},

    # --- 카테고리: 행위_폭력 ---
    "강간": {"category": "행위_폭력", "definition": "성폭력이 사건과 트라우마의 중심에 있는 이야기", "typical_genre": ["스릴러", "치정로맨스"]},
    "납치": {"category": "행위_폭력", "definition": "납치된 인물을 둘러싼 사건의 이야기", "typical_genre": ["스릴러", "치정로맨스"]},
    "낯선 곳으로의 이주": {"category": "행위_폭력", "definition": "낯선 곳에 이주한 인물의 새로운 삶 이야기", "typical_genre": ["현대로맨스"]},
    "네크로필리아": {"category": "행위_폭력", "definition": "죽음에 대한 비정상적 매혹이 사건의 중심에 있는 이야기", "typical_genre": ["스릴러"]},
    "대전 격투": {"category": "행위_폭력", "definition": "정면 대결을 통해 풀리는 갈등의 이야기", "typical_genre": ["사극", "판타지"]},
    "대학살": {"category": "행위_폭력", "definition": "대량 학살이 배경이 된 사랑과 생존의 이야기", "typical_genre": ["사극", "스릴러"]},
    "대항해와 원정": {"category": "행위_폭력", "definition": "거대한 항해나 원정에 나선 인물의 사랑과 모험 이야기", "typical_genre": ["판타지", "사극"]},
    "뜻밖의 초능력": {"category": "행위_폭력", "definition": "갑자기 초능력을 얻은 인물의 사랑과 갈등의 이야기", "typical_genre": ["판타지", "SF"]},
    "아내 강탈": {"category": "행위_폭력", "definition": "한 인물의 배우자를 빼앗는 사건의 이야기", "typical_genre": ["치정로맨스", "사극"]},
    "이간질": {"category": "행위_폭력", "definition": "둘 사이를 이간시키는 행위가 사건을 꼬는 이야기", "typical_genre": ["사극", "치정로맨스"]},
    "이지메": {"category": "행위_폭력", "definition": "집단 따돌림이 사건의 배경이 된 이야기", "typical_genre": ["현대로맨스", "스릴러"]},
    "지배자 희롱": {"category": "행위_폭력", "definition": "권력자를 우롱하는 행위가 사건의 중심에 있는 이야기", "typical_genre": ["사극", "코미디"]},
    "탈옥": {"category": "행위_폭력", "definition": "감옥을 탈출한 인물의 사랑과 도주의 이야기", "typical_genre": ["스릴러", "사극"]},
    "형제 간의 경쟁": {"category": "행위_폭력", "definition": "형제·자매가 같은 사랑이나 자리를 두고 경쟁하는 이야기", "typical_genre": ["사극", "치정로맨스"]},
    "고부 갈등": {"category": "행위_폭력", "definition": "시어머니와 며느리 사이의 갈등이 사건이 되는 이야기", "typical_genre": ["현대로맨스"]},
    "고립된 남녀": {"category": "행위_폭력", "definition": "두 사람이 고립된 공간에서 사랑과 갈등을 경험하는 이야기", "typical_genre": ["로맨스", "스릴러"]},

    # --- 카테고리: 환경_세계관 ---
    "대체 역사": {"category": "환경_세계관", "definition": "실제 역사와 다른 가상의 역사를 배경으로 펼쳐지는 이야기", "typical_genre": ["사극", "판타지"]},
    "식민지화": {"category": "환경_세계관", "definition": "식민지 시대를 배경으로 한 사랑과 저항의 이야기", "typical_genre": ["사극"]},
    "집단 광기": {"category": "환경_세계관", "definition": "집단이 광기에 빠지는 사회를 배경으로 한 이야기", "typical_genre": ["스릴러", "사극"]},
    "천재지변": {"category": "환경_세계관", "definition": "거대한 자연재해를 배경으로 한 사랑과 생존의 이야기", "typical_genre": ["스릴러", "판타지"]},
    "비대칭 전투": {"category": "환경_세계관", "definition": "강자와 약자 사이의 전투가 배경이 된 이야기", "typical_genre": ["사극", "판타지"]},
    "용호상박": {"category": "환경_세계관", "definition": "비등한 실력자들의 대결이 배경이 된 이야기", "typical_genre": ["사극", "판타지"]},
    "전쟁 발발": {"category": "환경_세계관", "definition": "전쟁이 일상을 뒤바꾸는 가운데 펼쳐지는 사랑과 운명의 이야기", "typical_genre": ["사극"]},

    # --- 카테고리: 인물_판타지 ---
    "갑작스러운 병": {"category": "인물_판타지", "definition": "갑작스러운 질병이 인물의 삶을 뒤바꾸는 이야기", "typical_genre": ["현대로맨스", "치정로맨스"]},
    "구세주 출현": {"category": "인물_판타지", "definition": "구원자를 자처하는 인물이 등장해 사건을 풀어가는 이야기", "typical_genre": ["판타지", "현대로맨스"]},
    "귀신 소환": {"category": "인물_판타지", "definition": "귀신을 불러내는 인물이 사건의 중심에 있는 이야기", "typical_genre": ["판타지", "스릴러"]},
    "돌연변이": {"category": "인물_판타지", "definition": "변이가 일어난 인물의 사랑과 갈등의 이야기", "typical_genre": ["SF", "판타지"]},
    "마법사/마녀": {"category": "인물_판타지", "definition": "마법사나 마녀가 사랑과 사건의 중심에 있는 이야기", "typical_genre": ["판타지", "로판"]},
    "미친 전도사": {"category": "인물_판타지", "definition": "광기에 사로잡힌 종교 인물이 등장하는 이야기", "typical_genre": ["스릴러", "사극"]},
    "반인반수": {"category": "인물_판타지", "definition": "반은 인간 반은 짐승인 존재가 사랑이나 사건의 중심에 있는 이야기", "typical_genre": ["판타지", "로판"]},
    "뱀파이어": {"category": "인물_판타지", "definition": "뱀파이어가 사랑과 사건의 중심에 있는 이야기", "typical_genre": ["판타지", "치정로맨스"]},
    "뱀파이어 헌터": {"category": "인물_판타지", "definition": "뱀파이어를 사냥하는 인물의 사랑과 갈등의 이야기", "typical_genre": ["판타지", "스릴러"]},
    "복제인간": {"category": "인물_판타지", "definition": "복제된 인물이 자기 정체성을 찾는 이야기", "typical_genre": ["SF"]},
    "사이보그": {"category": "인물_판타지", "definition": "기계와 인간이 결합된 존재의 사랑과 갈등의 이야기", "typical_genre": ["SF"]},
    "악마의 아이": {"category": "인물_판타지", "definition": "악마의 자식이 자라는 가운데 펼쳐지는 사랑과 운명의 이야기", "typical_genre": ["판타지", "스릴러"]},
    "저승 방문자": {"category": "인물_판타지", "definition": "저승에서 온 인물이 사건의 중심에 있는 이야기", "typical_genre": ["판타지", "스릴러"]},
    "좀비": {"category": "인물_판타지", "definition": "좀비의 등장이 사랑과 생존의 동력이 되는 이야기", "typical_genre": ["스릴러", "판타지"]},
    "치매": {"category": "인물_판타지", "definition": "치매를 가진 인물의 사랑과 기억의 이야기", "typical_genre": ["현대로맨스"]},
    "퇴마사": {"category": "인물_판타지", "definition": "악령을 쫓는 퇴마사의 사랑과 사건 이야기", "typical_genre": ["판타지"]},
    "거대 괴수": {"category": "인물_판타지", "definition": "거대 괴물이 인물의 운명을 뒤흔드는 이야기", "typical_genre": ["SF", "판타지"]},
    "천사": {"category": "인물_판타지", "definition": "천사적 존재가 사랑과 사건의 중심에 있는 이야기", "typical_genre": ["판타지", "로판"]},
}


# ============================================================================
# LEGACY_MOTIF_MAPPING - v3.0 23종 자동 변환 매핑
# ============================================================================

LEGACY_MOTIF_MAPPING = {
    "재회물": "옛 연인의 출현",
    "오래된연인": "부부 싸움",
    "첫사랑": "첫눈에 반한 사랑",
    "친구>연인": "세대를 초월한 우정",
    "라이벌_앙숙": "적과의 사랑",
    "사제지간": "도제 수련",
    "나이차커플": "나이 차를 극복한 사랑",
    "키잡물": "피그말리온",
    "사내연애": "관음증",
    "비밀연애": "위험한 비밀 결혼",
    "삼각관계": "삼각관계",
    "갑을관계": "신분 위장",
    "신분차이": "계급을 초월한 사랑",
    "계약연애_결혼": "사랑의 연기",
    "정략결혼": "신분 상승 결혼",
    "선결혼후연애": "사랑의 연기",
    "원나잇": "첫 관계",
    "몸정맘정": "원 나잇 스탠드",
    "소유욕_독점욕_질투": "의처증(의부증)",
    "여공남수": "사디즘",
    "금단의관계": "위험한 비밀 결혼",
    "운명적사랑": "운명적 사랑",
    "키재기_키빠짐": "나쁜 남자에게 반하기",
}

_WEAK_MAPPING = {"친구>연인", "사내연애", "여공남수", "키재기_키빠짐"}


def convert_legacy_motifs(legacy_motif_list: list) -> dict:
    """v3.0 23종 모티프 키를 v3.4 키로 변환.

    Returns:
        {"converted": [...], "unmapped": [...], "warnings": [...]}
    """
    converted = []
    unmapped = []
    warnings = []
    for legacy in legacy_motif_list:
        if legacy in LEGACY_MOTIF_MAPPING:
            new_motif = LEGACY_MOTIF_MAPPING[legacy]
            converted.append(new_motif)
            if legacy in _WEAK_MAPPING:
                warnings.append(f"'{legacy}' -> '{new_motif}' (약한 매핑, 작가 확인 권장)")
        else:
            unmapped.append(legacy)
    return {"converted": converted, "unmapped": unmapped, "warnings": warnings}


def get_motif_definition(motif_name: str) -> str:
    """v3.4 모티프 정의 검색. 신규 사전 + 레거시 매핑 모두 시도."""
    if motif_name in NARRATIVE_MOTIFS_205:
        return NARRATIVE_MOTIFS_205[motif_name]["definition"]
    if motif_name in LEGACY_MOTIF_MAPPING:
        new_key = LEGACY_MOTIF_MAPPING[motif_name]
        if new_key in NARRATIVE_MOTIFS_205:
            return NARRATIVE_MOTIFS_205[new_key]["definition"]
    return ""


def get_motifs_by_category(category: str) -> list:
    """카테고리별 모티프 목록 반환."""
    return [k for k, v in NARRATIVE_MOTIFS_205.items() if v.get("category") == category]


def get_motifs_for_genre(genre: str) -> list:
    """장르에 맞는 모티프 목록 반환."""
    return [k for k, v in NARRATIVE_MOTIFS_205.items() if genre in v.get("typical_genre", [])]


def find_motifs_for_4husbands() -> list:
    """4명의 전남편들에 적용 가능한 모티프 목록."""
    return [k for k, v in NARRATIVE_MOTIFS_205.items() if v.get("applicable_4husbands")]


# v3.0 호환성 alias - prompt.py가 RELATIONSHIP_MOTIFS_DICT를 import할 때 사용
RELATIONSHIP_MOTIFS_DICT = {
    k: v for k, v in NARRATIVE_MOTIFS_205.items()
    if v.get("category", "").startswith(("인물_사랑", "상황_사랑"))
}


# ============================================================================
# ROMANCE_FORMULAS - 7종 (v3.4: 버디러브 추가)
# ============================================================================

ROMANCE_FORMULAS = {
    "운명적_인연물": {
        "definition": "운명으로 정해진 두 사람이 거역할 수 없는 사랑을 완성하는 포뮬러",
        "story_diagram": [
            "운명의 만남 -> 의식하기 -> 운명을 거부 -> 거부 실패",
            "-> 운명 인정 -> 위기 -> 운명적 결합"
        ],
        "primary_motifs": ["운명적 사랑", "첫눈에 반한 사랑", "옛 연인의 출현"],
        "typical_genre": ["로판", "현대로맨스", "치정로맨스"],
        "applicable_4husbands": True,
    },
    "계약연애_결혼물": {
        "definition": "처음엔 계약으로 시작했으나 진짜 사랑이 싹트는 포뮬러",
        "story_diagram": [
            "계약 체결 -> 거짓 연기 시작 -> 진심 발견",
            "-> 계약 위반 -> 위기 -> 진짜 사랑 고백"
        ],
        "primary_motifs": ["사랑의 연기", "신분 상승 결혼", "위험한 비밀 결혼"],
        "typical_genre": ["현대로맨스", "치정로맨스", "로판"],
    },
    "재회_복귀물": {
        "definition": "헤어진 두 사람이 다시 만나 새로운 사랑을 완성하는 포뮬러",
        "story_diagram": [
            "과거 이별 -> 시간의 흐름 -> 재회 -> 옛 감정 재발견",
            "-> 새로운 갈등 -> 진짜 사랑 확인"
        ],
        "primary_motifs": ["옛 연인의 출현", "운명적 사랑", "기억상실증"],
        "typical_genre": ["현대로맨스", "치정로맨스"],
    },
    "갑을_권력관계물": {
        "definition": "권력 비대칭이 사랑의 긴장을 만드는 포뮬러",
        "story_diagram": [
            "권력 격차 만남 -> 권력 행사 -> 굴복과 저항",
            "-> 권력자의 흔들림 -> 약자의 자기 결단 -> 평등한 사랑 완성"
        ],
        "primary_motifs": ["계급을 초월한 사랑", "신분 위장", "의처증(의부증)"],
        "typical_genre": ["치정로맨스", "현대로맨스", "로판"],
        "applicable_4husbands": True,
    },
    "다중_관계망_치정물": {
        "definition": "여러 인물이 한 사람을 둘러싸고 얽히는 치정 포뮬러",
        "story_diagram": [
            "다중 인물 등장 -> 각자의 욕망 -> 삼각·사각 관계",
            "-> 폭로와 갈등 -> 진짜 사랑 확정 -> 남은 인물들의 결말"
        ],
        "primary_motifs": ["삼각관계", "의처증(의부증)", "광기 어린 사랑"],
        "typical_genre": ["치정로맨스"],
        "applicable_4husbands": True,
    },
    "성장_치유_로판물": {
        "definition": "여주인공이 시련을 겪으며 성장·치유되는 포뮬러",
        "story_diagram": [
            "여주의 결핍 -> 시련 -> 작은 성장 -> 큰 시련",
            "-> 후퇴 -> 결정적 깨달음 -> 완성"
        ],
        "primary_motifs": ["외상 후 스트레스 장애", "아동학대", "신분 상승 결혼"],
        "typical_genre": ["로판", "현대로맨스"],
    },
    "버디러브_5단계": {
        "definition": "블레이크 스나이더 Save The Cat의 5단계 러브스토리 포뮬러 (v3.4 신규)",
        "story_diagram": [
            "1단계: 처음에는 서로 싫어한다",
            "2단계: 모험을 함께 해나가며 서로를 필요로 한다는 걸 깨닫는다",
            "3단계: 깨달음이 더 큰 갈등으로 이어진다 (의존 거부)",
            "4단계: 절망의 순간 - 두 인물이 싸우고 헤어진다",
            "5단계: 서로를 필요로 한다는 사실을 깨닫고 자존심을 숙여 재결합"
        ],
        "primary_motifs": ["적과의 사랑", "운명적 사랑", "첫눈에 반한 사랑"],
        "typical_genre": ["현대로맨스", "치정로맨스", "로판"],
        "applicable_4husbands": True,
        "source": "Blake Snyder, Save The Cat!",
    },
}


# ============================================================================
# BAD_FIRST_IMPRESSION_PLOT (v3.4 신규)
# ============================================================================
# 출처: 백종인 (2022) [표 40]
# 한국 로맨스 드라마 27편 모두에서 사용되는 시장 표준 플롯

BAD_FIRST_IMPRESSION_PLOT = {
    "name": "안 좋은 첫인상, 그러나 한 공간",
    "definition": "남주와 여주가 안 좋은 첫인상으로 만나지만, 어쩔 수 없이 같은 공간에서 계속 마주치며 감정이 발전하는 플롯",
    "principle": "첫인상이 안 좋고 갈등 구조가 형성되지만 함께하는 상황이 없다면 어떠한 감정도 생길 수 없다",
    "structure": {
        "ep_range": "1~5화",
        "components": [
            "1. 첫 마주침 - 책 부딪치기, 어깨 부딪치기, 오해, 같은 자리 다툼",
            "2. 첫인상 결정 - '저 사람 이상해', '저 사람 싫어'",
            "3. 한 공간 강제 - 회사, 학교, 동아리, 카페, 계약 등의 이유로 같은 공간에서 마주칠 수밖에 없음",
            "4. 미세한 변화 - 일상적 접촉이 누적되며 감정이 미세하게 흔들림",
            "5. 첫 감정 인지 - 5화 무렵 '내가 이 사람을 의식하고 있다'는 자각"
        ]
    },
    "examples": [
        "치즈 인 더 트랩 - 같은 학교 같은 수업 같은 동아리",
        "김비서가 왜 그럴까 - 비서와 부회장",
        "편의점 샛별이 - 편의점 사장과 아르바이트",
        "내 ID는 강남미인 - 같은 대학 같은 과",
        "녹두전 - 과부촌 한 방에서",
    ],
    "typical_genre": ["현대로맨스", "치정로맨스", "로판", "사극"],
    "source": "백종인 (2022), 공주대 만화학과 석사논문, [표 40]",
}


# ============================================================================
# TWO_TIER_CRISIS_STRUCTURE (v3.4 신규)
# ============================================================================

TWO_TIER_CRISIS_STRUCTURE = {
    "name": "1차 위기 - 2차 위기 구조",
    "definition": "로맨스 작품 후반의 긴장 곡선을 만드는 표준 구조. 1차 위기는 메인플롯, 2차 위기는 서브플롯",
    "primary_crisis": {
        "name": "1차 위기 (메인 플롯)",
        "ep_position": "전체의 50~65% 지점",
        "scale": "감정 차원의 위기 - 잠시의 갈등",
        "typical_form": [
            "'우리는 맞지 않는 사이였어'",
            "'우리 사이는 대체 뭐야'",
            "오해, 일시적 이별, 가족 반대",
        ],
        "resolution": "두 인물의 감정 확인 -> 더 강한 결합",
        "duration": "2~5회차 정도",
    },
    "secondary_crisis": {
        "name": "2차 위기 (서브 플롯)",
        "ep_position": "전체의 75~85% 지점",
        "scale": "모든 것을 걸어야 하는 규모 - 자기 인생의 토대를 잃을 수 있는 위기",
        "typical_form": [
            "기업의 음모 - 남주의 회사가 위협받음",
            "권력자의 보복 - 적이 등장해 두 사람을 공격",
            "사회·신분 차이의 폭발 - 가문이 둘을 갈라놓으려 함",
            "이수연 같은 잠재 빌런의 본격 등장",
        ],
        "key_choice": "'당신이 가진 모든 걸 잃어도 그 사람을 선택할 것이냐?'",
        "resolution": "남주가 모든 것을 포기하고 사랑을 선택 -> 결국 잃은 것도 회복",
        "duration": "5~10회차 정도",
    },
    "principle": "1차 위기는 감정 확인, 2차 위기는 진짜 결단. 1차 없이 2차로 가면 감정 빌드가 약함",
    "applicable_4husbands": True,
    "source": "백종인 (2022), 공주대 만화학과 석사논문, IV-4",
}


# ============================================================================
# MOVEMENT_NARRATIVE_PATTERNS - 5종 이동 계열 서사 (v3.0 유지)
# ============================================================================

MOVEMENT_NARRATIVE_PATTERNS = {
    "회귀물": {
        "definition": "과거의 시점으로 돌아가 인생을 다시 사는 이야기",
        "first_act_signature": "회귀 시점 명시 + 회귀 동기 + 첫 행동",
        "key_devices": ["미래 정보 활용", "과거의 후회 회복", "운명 변경"],
        "typical_genre": ["로판", "판타지", "현대판타지"],
    },
    "빙의물": {
        "definition": "다른 사람의 몸에 영혼이 들어가는 이야기",
        "first_act_signature": "빙의 사실 발견 + 정체성 혼란 + 적응 시도",
        "key_devices": ["원래 몸 주인과의 관계", "정체성 위장", "원래 인격과의 갈등"],
        "typical_genre": ["판타지", "로판", "현대로맨스"],
        "applicable_4husbands": True,
    },
    "환생물": {
        "definition": "죽은 후 다른 사람으로 다시 태어나는 이야기",
        "first_act_signature": "환생 자각 + 전생 기억 + 새 삶 시작",
        "key_devices": ["전생 기억과 능력", "전생 인연", "새 삶의 의미 찾기"],
        "typical_genre": ["로판", "판타지"],
        "applicable_4husbands": True,
    },
    "전생물": {
        "definition": "전생을 기억하거나 전생의 인연이 현생에 이어지는 이야기",
        "first_act_signature": "전생 기억 단서 + 현생 인물과 전생 연결",
        "key_devices": ["전생-현생 인연", "운명 반복", "기억 회복"],
        "typical_genre": ["로판", "판타지"],
    },
    "전이물": {
        "definition": "다른 세계로 이동하는 이야기 (이세계 전이)",
        "first_act_signature": "세계 이동 + 새 세계 적응 + 능력 획득",
        "key_devices": ["이세계 룰", "능력 부여", "원래 세계와의 단절"],
        "typical_genre": ["판타지", "로판"],
    },
}


# ============================================================================
# HIGH_RATING_ROMANCE_MOTIFS - 19금 5종 (v3.0 유지)
# ============================================================================

HIGH_RATING_ROMANCE_MOTIFS = {
    "선섹스_후연애": {
        "definition": "신체 관계가 먼저, 감정이 나중에 따라오는 19금 서사",
        "key_principle": "관능 -> 의식 -> 감정 -> 인정의 순서",
        "typical_intimacy_arc": ["tension", "first_scene", "power_tension", "emotional_union"],
        "platform": ["리디 성인관", "카카오페이지 19금"],
    },
    "권력_정복_치정": {
        "definition": "권력자의 정복욕과 약자의 흔들림이 핵심 동력인 치정",
        "key_principle": "거리감 제로 + 권력 비대칭 + 굴종과 저항",
        "typical_intimacy_arc": ["power_tension", "deep_intimacy"],
        "platform": ["리디 성인관"],
    },
    "옵세션_광기": {
        "definition": "한 인물이 다른 인물에게 광적으로 집착하는 서사",
        "key_principle": "독점욕 + 질투 + 소유의 극한",
        "typical_intimacy_arc": ["first_scene", "deep_intimacy"],
        "platform": ["리디 성인관"],
    },
    "다정한_관능": {
        "definition": "부드럽고 다정한 톤의 관능 서사",
        "key_principle": "신뢰 -> 친밀 -> 깊은 결합",
        "typical_intimacy_arc": ["tension", "emotional_union"],
        "platform": ["카카오페이지 19금", "조아라"],
    },
    "비밀_금단_관계": {
        "definition": "사회가 금지한 관계의 19금 서사 (불륜·사제·근친 등)",
        "key_principle": "비밀 + 죄책감 + 폭로의 긴장",
        "typical_intimacy_arc": ["tension", "first_scene", "power_tension"],
        "platform": ["리디 성인관"],
    },
}


# ============================================================================
# ROFAN_SUBGENRES - 로판 3종 (v3.0 유지)
# ============================================================================

ROFAN_SUBGENRES = {
    "성장물": {
        "definition": "여주인공의 단계적 성장이 핵심 동력인 로판",
        "core_arc": "결핍 -> 작은 성장 -> 시련 -> 후퇴 -> 큰 성장",
        "typical_length": "60~120화",
    },
    "복수물": {
        "definition": "여주인공의 복수가 핵심 동력인 로판",
        "core_arc": "전생/과거 트라우마 -> 복수 계획 -> 단계적 실행 -> 복수 완성과 새 사랑",
        "typical_length": "50~100화",
    },
    "치유물": {
        "definition": "여주인공의 상처가 치유되는 과정이 핵심인 로판",
        "core_arc": "상처 -> 새 환경 -> 만남 -> 치유 -> 새 자아",
        "typical_length": "40~80화",
    },
}


# ============================================================================
# v3.0 호환 보조 함수들
# ============================================================================

def get_formula_diagram(formula_name: str) -> list:
    if formula_name in ROMANCE_FORMULAS:
        return ROMANCE_FORMULAS[formula_name].get("story_diagram", [])
    return []


def get_formula_motifs(formula_name: str) -> list:
    if formula_name in ROMANCE_FORMULAS:
        return ROMANCE_FORMULAS[formula_name].get("primary_motifs", [])
    return []


def get_movement_first_act(movement_code: str) -> str:
    if movement_code in MOVEMENT_NARRATIVE_PATTERNS:
        return MOVEMENT_NARRATIVE_PATTERNS[movement_code].get("first_act_signature", "")
    return ""


def find_formulas_for_4husbands() -> list:
    return [k for k, v in ROMANCE_FORMULAS.items() if v.get("applicable_4husbands")]


# ============================================================================
# 자가 검증
# ============================================================================

def _validate_module():
    """모듈 자가 검증."""
    # 1. NARRATIVE_MOTIFS_205 크기 (목표 170+)
    assert len(NARRATIVE_MOTIFS_205) >= 170, \
        f"NARRATIVE_MOTIFS_205 크기 부족: {len(NARRATIVE_MOTIFS_205)}"

    # 2. 모든 모티프에 category, definition 필드
    for k, v in NARRATIVE_MOTIFS_205.items():
        assert "category" in v, f"{k}에 category 누락"
        assert "definition" in v, f"{k}에 definition 누락"

    # 3. LEGACY 23종 매핑 완전성
    legacy_keys = [
        "재회물", "오래된연인", "첫사랑", "친구>연인", "라이벌_앙숙",
        "사제지간", "나이차커플", "키잡물", "사내연애", "비밀연애",
        "삼각관계", "갑을관계", "신분차이", "계약연애_결혼", "정략결혼",
        "선결혼후연애", "원나잇", "몸정맘정", "소유욕_독점욕_질투",
        "여공남수", "금단의관계", "운명적사랑", "키재기_키빠짐",
    ]
    for legacy in legacy_keys:
        assert legacy in LEGACY_MOTIF_MAPPING, f"레거시 키 '{legacy}' 매핑 누락"
        # 매핑된 v3.4 키가 NARRATIVE_MOTIFS_205에 실제로 존재
        new_key = LEGACY_MOTIF_MAPPING[legacy]
        assert new_key in NARRATIVE_MOTIFS_205, f"매핑 대상 '{new_key}' 사전에 없음 (legacy: {legacy})"

    # 4. 변환 함수 동작 확인
    result = convert_legacy_motifs(["재회물", "운명적사랑", "삼각관계"])
    assert "옛 연인의 출현" in result["converted"]
    assert "운명적 사랑" in result["converted"]
    assert "삼각관계" in result["converted"]

    # 5. ROMANCE_FORMULAS 7종, 버디러브 포함
    assert "버디러브_5단계" in ROMANCE_FORMULAS, "버디러브 포뮬러 누락"
    assert len(ROMANCE_FORMULAS) == 7, f"포뮬러 개수 불일치: {len(ROMANCE_FORMULAS)}"

    # 6. v3.4 신규 데이터
    assert BAD_FIRST_IMPRESSION_PLOT is not None
    assert TWO_TIER_CRISIS_STRUCTURE is not None

    # 7. v3.0 호환 alias
    assert len(RELATIONSHIP_MOTIFS_DICT) > 0, "RELATIONSHIP_MOTIFS_DICT alias 비어있음"

    return True


if __name__ == "__main__":
    assert _validate_module()
    print(f"✓ NARRATIVE_MOTIFS_205: {len(NARRATIVE_MOTIFS_205)}개")
    print(f"✓ LEGACY_MOTIF_MAPPING: {len(LEGACY_MOTIF_MAPPING)}개 매핑")
    print(f"✓ RELATIONSHIP_MOTIFS_DICT (v3.0 alias): {len(RELATIONSHIP_MOTIFS_DICT)}개")
    print(f"✓ ROMANCE_FORMULAS: {len(ROMANCE_FORMULAS)}종 (v3.4 버디러브 포함)")
    print(f"✓ BAD_FIRST_IMPRESSION_PLOT 로드")
    print(f"✓ TWO_TIER_CRISIS_STRUCTURE 로드")
    print(f"✓ MOVEMENT_NARRATIVE_PATTERNS: {len(MOVEMENT_NARRATIVE_PATTERNS)}종")
    print(f"✓ HIGH_RATING_ROMANCE_MOTIFS: {len(HIGH_RATING_ROMANCE_MOTIFS)}종")
    print(f"✓ ROFAN_SUBGENRES: {len(ROFAN_SUBGENRES)}종")
    print()

    # 카테고리별 분포
    from collections import Counter
    cat_count = Counter(v.get("category", "unknown") for v in NARRATIVE_MOTIFS_205.values())
    print("카테고리별 분포:")
    for cat, n in sorted(cat_count.items()):
        print(f"  {cat:20s}: {n}개")

    # 변환 테스트
    print()
    print("4명의 전남편들 추정 모티프 변환 테스트:")
    test_legacy = ["재회물", "삼각관계", "운명적사랑", "갑을관계", "소유욕_독점욕_질투"]
    result = convert_legacy_motifs(test_legacy)
    for legacy, new in zip(test_legacy, result["converted"]):
        print(f"  {legacy:20s} -> {new}")
    if result["warnings"]:
        print("\n경고:")
        for w in result["warnings"]:
            print(f"  ⚠ {w}")
