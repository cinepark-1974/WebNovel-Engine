"""
👖 BLUE JEANS WEB NOVEL ENGINE v2.3 — prompt.py
3단계 파이프라인 (CONCEPT → BUILD-UP → WRITING) + EXTENSION
Core Arc 완결형 설계 + 인기 대응 확장 모드
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

[연재형 웹소설 구조 원칙]
- Core Arc는 독립 완결 가능해야 한다. Extension이 없어도 이야기가 성립.
- 미회수 떡밥은 "열린 결말"로, 회수된 떡밥은 "닫힌 결말"로.
- Extension은 기존 떡밥 재활용 + 신규 떡밥 결합으로 설계.
""".strip()

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
# [2-2] 서사 모티프 이중 구조 — 고경은(2022) 연구 기반
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
# [2-3] READER PERSONAS — 강종현(2024) 수용자 연구 + KOCCA 2020/2022 데이터
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
# [2-4] FLOW INDUCTION — 강종현(2024) 몰입 이론 기반
# =================================================================
FLOW_INDUCTION_RULES = """[독자 몰입 유도 규칙 — 강종현(2024) 몰입(Flow) 이론 기반]

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
# [2-5] READER SIMULATION — 시뮬레이션 프롬프트 (강종현 2024)
# =================================================================
def build_reader_simulation_prompt(episode_text, persona, genre=""):
    """타겟 독자 페르소나로 가장해 회차에 대한 피드백 생성."""
    persona_block = get_reader_persona_block(persona)
    g_block = f"\n[장르] {genre}" if genre else ""
    return f"""당신은 이 작품의 타겟 독자 '{persona}'입니다. 아래 웹소설 회차를 실제 독자처럼 읽고, 몰입 이론(강종현, 2024) 관점에서 피드백하세요.

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
            "인물 이름 과다",
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
    """기획서 텍스트를 컨셉 카드 JSON으로 파싱."""
    primary_list = list(NARRATIVE_MOTIFS["primary"].keys())
    secondary_list = list(NARRATIVE_MOTIFS["secondary"].keys())
    persona_list = list(READER_PERSONAS.keys())
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
- 주인공 성격이 실리적이거나 반동인물적이면 is_antihero=true

[JSON 출력 — 이 구조를 정확히 따를 것]
{{
  "title": "작품 제목",
  "genre": "장르",
  "logline": "로그라인",
  "formula_tags": ["환생","역하렘","치정" 등 해당되는 태그만],
  "primary_motif": "회귀|빙의|환생|귀환|차원이동|일상 중 하나",
  "secondary_motif": "성장물|먼치킨물|사이다물|시한부물|책빙의물|육아물|법정물|학원물|아이돌물|전문직물|연예계물|헌터물 중 하나 (없으면 빈 문자열)",
  "target_persona": "10대 여성|20~30대 여성|20~30대 남성|40대 이상 여성|청소년 남성 중 하나",
  "protagonist": {{
    "name": "", "age": 0, "role": "직업/지위",
    "goal": "원하는 것", "need": "필요한 것", "fatal_flaw": "치명적 결함",
    "is_antihero": false,
    "identification_strategy": {{
      "naming_style": "실명 사용 | 일반명사 통일 | 애칭 중심 중 하나",
      "empathy_points": ["독자가 공감할 감정/상황 1~3개"],
      "inner_monologue_style": "내면 독백 톤 서술 (예: 냉소적 자기 관찰, 체념적 짧은 사유)"
    }}
  }},
  "love_interests": [
    {{"name": "", "role": "", "appeal": "매력 포인트", "conflict": "관계의 갈등 요소"}}
  ],
  "villain": {{
    "name": "", "role": "", "wants": "", "justification": "", "limits": "", "win_rate": ""
  }},
  "world": "세계관/배경",
  "relationships": "관계 구도 서술",
  "season_questions": {{"romance": "", "mystery": ""}},
  "synopsis": "전체 시놉시스 3~5문장"
}}""".strip()


def build_generate_concept_prompt(idea_text, genre=""):
    """한 줄 아이디어에서 컨셉 카드 자동 생성."""
    g_block = f"\n[장르]\n{genre}" if genre else ""
    primary_list = list(NARRATIVE_MOTIFS["primary"].keys())
    secondary_list = list(NARRATIVE_MOTIFS["secondary"].keys())
    persona_list = list(READER_PERSONAS.keys())
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
- 시놉시스 3~5문장

[JSON 출력]
{{
  "title": "", "genre": "", "logline": "",
  "formula_tags": [],
  "primary_motif": "",
  "secondary_motif": "",
  "target_persona": "",
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
    """Core Arc 설계 — 25화 × 2청크 (총 50화 완결형)."""
    paywall_ep = concept_card.get("serial_config", {}).get("paywall_ep", 25)
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

{CORE_ARC_DESIGN}

{CLIFFHANGER_RULES}

{PAYWALL_DESIGN}

{_pn_block(producer_note)}{prev_block}{paywall_note}

[이 청크의 국면]
{chunk_phases_50.get(chunk, '')}

[JSON 출력 — 이 청크의 5블록(25화)만]
{{
  "chunk": {chunk},
  "chunk_summary": "이 청크 25화 흐름 요약 2~3문장",
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


def build_character_bible_prompt(concept_card):
    """웹소설 경량 캐릭터 바이블 생성."""
    return f"""[TASK] 웹소설 캐릭터 바이블 생성

[컨셉 카드]
{concept_card}

[캐릭터 바이블 필드 (캐릭터당)]
- 이름, 나이, 직업/지위, 외모 핵심
- 말투 (예문 2~3개)
- 행동 패턴 (특유의 버릇/제스처)
- 결핍/비밀
- 욕망/목표
- 변화 아크 (시즌 내 변화 방향)

[JSON 출력]
{{
  "protagonist": {{...}},
  "love_interests": [{{...}},{{...}}],
  "villain": {{...}},
  "supporting": [{{...}}]
}}""".strip()


def build_episode_plot_prompt(arc_block, plant_map, ep_number,
                              prev_summary, producer_note=""):
    """회차 플롯 설계 + 제목 생성."""
    return f"""[TASK] EP{ep_number} 회차 플롯 설계

[아크 블록]
{arc_block}

[떡밥 맵 — 이번 회차 관련]
{plant_map}

[이전 회차 요약]
{prev_summary}

{_pn_block(producer_note)}

{EPISODE_STRUCTURE}

{EPISODE_TITLE_RULES}

{CLIFFHANGER_RULES}

[JSON 출력]
- title: 7~15자. 6가지 유형 중 가장 적합한 것 선택. 스포일러 금지.
{{
  "ep": {ep_number},
  "title": "회차 부제 (7~15자)",
  "title_type": "상황|대사|미스터리|감정|의외성|시공간",
  "opening": {{"hook_line":"첫 문장","recap_method":"행동|소지품|대사","question":"독자가 품을 질문"}},
  "development": {{
    "scenes": [
      {{"scene_no":1,"location":"","characters":[],"conflict":"","outcome":"","plant_or_payoff":""}}
    ],
    "emotion_arc": "감정 곡선 (예: 불안→안도→충격)"
  }},
  "cliffhanger": {{"type":"","content":"","next_ep_connection":""}}
}}""".strip()


# =================================================================
# [15] PROMPT BUILDERS — STEP 3: WRITING
# =================================================================

def build_episode_write_prompt(episode_plot, characters, style_dna,
                               genre, rating, prev_3_episodes,
                               plant_map_relevant, formula_tags=None,
                               producer_note="", style_strength="중",
                               target_length=5200, platform="카카오페이지",
                               primary_motif="", secondary_motif="",
                               target_persona=""):
    """회차 원고 집필 — 플랫폼별 분량 + 서사 모티프 + 독자 페르소나 반영."""
    tags_block = get_formula_block(formula_tags or [])
    motif_block = get_motif_block(primary_motif, secondary_motif)
    persona_block = get_reader_persona_block(target_persona)
    lp = get_platform_length(platform)
    min_len = lp["min"]
    max_len = lp["max"]
    tol = lp["tolerance"]

    return f"""[TASK] 웹소설 EP 원고 집필 — 플랫폼: {platform}

{_genre_block(genre)}

{tags_block}

{motif_block}

{persona_block}

{_rating_block(rating)}

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
- 플랫폼: {platform} (표준 분량 {min_len}~{max_len}자, 허용 오차 ±{tol}자)
- 도입(500~700자) → 전개(3,500~4,000자) → 훅(500~800자)
- 클리프행어는 플롯 지정 유형/내용 준수
- 리캡은 자연스럽게 녹이기 (직접 요약 금지)
- 대사 비율 40% 이상
- ★ 웹소설식 줄바꿈: 문장마다 줄바꿈, 문단(2~4줄) 사이 빈 줄 하나
- ★ 대사-지문 반드시 분리 (영어권식 "said" 뒤붙이기 금지)
- AI Anti-Pattern A1~A14 준수
- 마지막 3~5줄이 가장 중요

[출력 형식 — 반드시 지킬 것]
첫 줄: 회차 제목만 (예: "EP17. 가면 뒤의 남자")
둘째 줄: 빈 줄
셋째 줄부터: 본문

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
