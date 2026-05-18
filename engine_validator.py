"""
engine_validator.py — Engine v3.3 (구 v3.0 Phase C)
====================================================
회차 자가 검수·재료 활용 검증·전환점 자동 감지

핵심 함수:
- validate_planning_to_writing_mapping() — 기획 재료가 본문에 반영됐는가
- compute_episode_validation_score()    — 11축 종합 점수 (v3.3부터)
- detect_transition_episodes()          — 마음 흐름 단계 전환점 자동 감지
- generate_material_usage_report()      — 작가용 가시화 리포트
- get_validation_mode_for_episode()     — 회차별 검수 모드 결정
- summarize_cumulative_25()             — 25화 모니터링 누적 대시보드 데이터

11축 검수 (v3.3) — 등급별 동적 가중치:
[기존 10축 (v3.2)]
1. MATERIAL_USAGE         — 기획 재료가 본문에 활용됐는가
2. CHARACTER_CONSISTENCY  — 9종 인물 역할로 차별화됐는가
3. CLIFFHANGER_STRENGTH   — 클리프행어 분포가 시장 표준 안인가
4. MISE_EN_SCENE          — 묘사·장면 강도 적정한가
5. MARKET_VIABILITY       — 시장 트리거 5종 충족도
6. PLANT_USAGE            — 떡밥 활용도
7. DIALOGUE_RATIO         — 대사 비율 40% 기준
8. NAMING_DISCIPLINE      — A15·A16 호명·정체성 키워드 절제
9. PROSE_HYGIENE          — said 뒤붙이기 + 회차 간 반복 문구
10. LENGTH_DISCIPLINE     — 회차 분량 미달/초과

[신규 1축 (v3.3)]
11. ADULT_CONTENT_FIDELITY — 19금 콘텐츠 충실도 (관능 묘사 빈도·강도)
    · 19금/듀얼 작품: 가중치 0.40 (단일 최대)
    · 15금 작품: 가중치 0 (비활성)

등급별 동적 가중치:
- 19금/듀얼 작품: ADULT_CONTENT_FIDELITY 0.40 + 기존 10축 0.60 비례 분배
- 15금 작품: 기존 10축 1.00 비례 분배 (ADULT_CONTENT_FIDELITY 측정만 하고 점수 미반영)

원칙:
- 본 모듈은 LLM 호출 없이 텍스트 패턴 매칭으로 1차 검수 (빠름·무비용)
- 깊은 검수가 필요하면 prompt.py의 build_validation_prompt()로 LLM 호출
- 회차별 단독 점수 + 누적 단위 점수 분리 제공

변경 이력:
- v3.0: 5축 + PLANT_USAGE 추가 (6축)
- v3.2: 신규 4축 추가 (10축) + 점수 산출 구조 개편
        · 모든 축의 기본 점수 50점으로 통일 (보너스+페널티 균형)
        · 빈 데이터 자동 점수 부여 폐지 — 측정 불가 시 명시적 N/A
        · 신규 4축이 SYSTEM_PROMPT의 핵심 룰(대사 비율 / A1 / A15 / A16) 측정
        · 가중치 재배분 — 신규 4축 합 50%
- v3.3: ADULT_CONTENT_FIDELITY 축 추가 (11축) + 등급별 동적 가중치
        · 19금/듀얼 작품 핵심 결함 측정 (관능 묘사 빈도·강도)
        · 19금 작품: ADULT_CONTENT_FIDELITY 0.40 (단일 최대 비중)
        · 15금 작품: 자동 비활성 (관능 키워드 없어도 페널티 없음)
        · rating_mode를 받아 자동 분기 (concept_dict.serial_config.rating_mode)
"""

from typing import List, Dict, Optional, Tuple

# v3.0 데이터 모듈 import (선택적 — 실패해도 모듈 자체는 동작)
try:
    from data_motifs import (
        RELATIONSHIP_MOTIFS_DICT,
        ROMANCE_FORMULAS,
        MOVEMENT_NARRATIVE_PATTERNS,
    )
    _MOTIFS_OK = True
except ImportError:
    RELATIONSHIP_MOTIFS_DICT = {}
    ROMANCE_FORMULAS = {}
    MOVEMENT_NARRATIVE_PATTERNS = {}
    _MOTIFS_OK = False

try:
    from data_character import (
        CHARACTER_ROLE_TAXONOMY,
        MOE_ATTRIBUTES_25,
        HEROINE_MIND_FLOW_PATTERNS,
        HERO_MIND_FLOW_PATTERNS,
        detect_work_orientation,
        get_stage_for_episode_with_orientation,
    )
    _CHAR_OK = True
except ImportError:
    CHARACTER_ROLE_TAXONOMY = {}
    MOE_ATTRIBUTES_25 = {}
    HEROINE_MIND_FLOW_PATTERNS = {"stages": []}
    HERO_MIND_FLOW_PATTERNS = {"stages": []}
    detect_work_orientation = lambda c: "female"
    get_stage_for_episode_with_orientation = lambda ep, total=42, o="female": {}
    _CHAR_OK = False

try:
    from data_market import MARKET_DATA_2024, validate_cliffhanger_distribution
    _MARKET_OK = True
except ImportError:
    MARKET_DATA_2024 = {}
    validate_cliffhanger_distribution = lambda *a, **kw: {"in_range": [], "out_of_range": []}
    _MARKET_OK = False


# ============================================================================
# 검수 모드 — 자동/수동/전환점 자동
# ============================================================================
VALIDATION_MODES = {
    "auto_until_25": {
        "name": "1~25화 자동 + 26화부터 모드 결정",
        "description": "초기 정착기는 자동 검수, 25화 모니터링 후 작가가 결정",
        "default": True,
    },
    "transition_only": {
        "name": "전환점 회차만 자동 검수",
        "description": "마음 흐름 단계가 바뀌는 회차만 자동, 나머지는 수동",
        "default": False,
    },
    "all_auto": {
        "name": "모든 회차 자동 검수",
        "description": "비용 부담 있으나 가장 안전",
        "default": False,
    },
    "all_manual": {
        "name": "수동 검수만",
        "description": "작가가 버튼을 누를 때만 검수 실행",
        "default": False,
    },
}

# 검수 합격 임계점
VALIDATION_THRESHOLDS = {
    "episode_pass": 75,      # 회차 단독 점수 합격선
    "episode_warn": 65,      # 경고선 (이하면 권장 보강)
    "episode_redo": 55,      # 재집필 권장선
    "cumulative_pass": 78,   # 누적 점수 합격선
}


# ============================================================================
# 1. validate_planning_to_writing_mapping — 기획↔집필 연결 검증
# ============================================================================
def _semantic_keyword_synonyms() -> dict:
    """[v3.0+ 정밀화] 모티프·포뮬러·이동코드 동의어 사전.
    
    본문에 정확한 키워드가 없어도 동의어/표현이 있으면 매칭 인정.
    """
    return {
        # 이동 코드 동의어
        "환생": ["환생", "다시 태어", "다음 생", "이번 생", "전생", "새로 태어", "두 번째 인생", "두 번째 삶"],
        "빙의": ["빙의", "다른 사람의 몸", "이 몸", "남의 몸", "내 몸이 아니", "몸을 빌려", "정신만"],
        "회귀": ["회귀", "돌아왔", "다시 돌아", "과거로", "어린 시절로", "타임슬립"],
        "전이": ["전이", "이세계", "다른 세계", "차원 이동", "게임 속"],
        "전생": ["전생", "이전 생", "과거의 나", "옛날의 나"],
        
        # 모티프 동의어
        "재회물": ["재회", "다시 만나", "오랜만", "그때 그", "잊지 못한", "기억하시나"],
        "운명적사랑": ["운명", "필연", "정해진", "이끌리", "끌렸", "예정된"],
        "삼각관계": ["삼각", "사이에서", "두 남자", "두 사람 사이"],
        "갑을관계": ["갑을", "권력", "위계", "상사", "사장", "재벌", "신분"],
        "신분차이": ["신분", "계급", "재벌", "가난한", "상류", "하류"],
        "비밀연애": ["비밀", "숨기", "들키면", "몰래"],
        "사내연애": ["회사", "사무실", "동료", "직장"],
        "첫사랑": ["첫사랑", "처음 사랑", "어린 시절", "학창 시절"],
        "소유욕_독점욕_질투": ["질투", "소유욕", "독점", "내 거", "내 사람"],
        
        # 포뮬러 동의어 — 작품 톤·세계관 표지
        "운명적_인연물": ["운명", "필연", "환생", "빙의", "회귀", "다음 생", "전생"],
        "갑을관계_파괴물": ["계약", "정략", "위장", "신분", "계급", "권력 역전"],
        "절대적_지배물": ["재벌", "왕족", "황제", "회장", "지배"],
        "도시적_갈등물": ["회사", "사무실", "직장", "도시", "출근", "팀장"],
        "목가적_힐링물": ["시골", "마을", "카페", "고향", "치유", "회복"],
        "금단의_성장물": ["금기", "사제", "선생", "교수", "위반", "유혹"],
    }


def _check_signal_semantic(signal: str, text: str) -> bool:
    """[v3.0+ 정밀화] 신호(키워드/모티프/포뮬러)가 본문에 의미적으로 들어 있는지 검사.
    
    1) 정확 매칭
    2) 동의어 매칭 (사전 기반)
    3) 부분 매칭 (괄호·언더바 제거 후)
    """
    if not signal or not text:
        return False
    
    # 1) 정확 매칭
    if signal in text:
        return True
    
    # 2) 동의어 매칭
    synonyms = _semantic_keyword_synonyms().get(signal, [])
    for syn in synonyms:
        if syn in text:
            return True
    
    # 3) 부분 매칭 — "갑을관계_파괴물" → "갑을", "관계", "파괴"
    parts = signal.replace("_", " ").split()
    if len(parts) > 1:
        # 부분 키워드 중 2개 이상이 본문에 있으면 인정
        hits = sum(1 for p in parts if len(p) >= 2 and p in text)
        if hits >= 2:
            return True
        # 첫 번째 부분이 핵심 키워드면 그것만 있어도 인정
        if parts[0] and len(parts[0]) >= 2 and parts[0] in text:
            return True
    
    return False


def validate_planning_to_writing_mapping(
    concept: dict,
    character_bible,
    written_text: str,
    ep_number: int = 0,
    total_eps: int = 42,
) -> dict:
    """[v3.0+ 정밀화] 기획 재료가 본문에 실제로 반영됐는지 검증.
    
    LLM 호출 없이 텍스트 패턴 매칭으로 1차 검수.
    이번 버전: 정확 매칭 + 동의어 매칭 + 부분 매칭 3중 검사로 거짓 음성 감소.
    
    Args:
        concept: 콘셉트 카드 dict
        character_bible: 캐릭터 풀 데이터 (list 또는 dict)
        written_text: 회차 본문 텍스트
        ep_number: 회차 번호
        total_eps: 작품 전체 회차 수
    
    Returns:
        {
            "used": [...],           # 사용된 재료
            "weak": [...],           # 약하게 반영된 재료
            "missing": [...],        # 누락된 재료
            "score": 0~100,          # 재료 활용 점수
            "critical_missing": []   # 재집필 트리거가 될 누락
        }
    """
    if not written_text:
        return {
            "used": [], "weak": [], "missing": [],
            "score": 0, "critical_missing": ["본문 비어있음"]
        }
    
    used = []
    weak = []
    missing = []
    critical_missing = []
    
    text = written_text  # 검색 효율을 위해 원본 그대로 사용
    
    # ─── 1) 메인 포뮬러 표상 모티프 검증 (의미 매칭) ─────────────────
    formula_main = concept.get("formula_main", "")
    if formula_main and formula_main in ROMANCE_FORMULAS:
        f = ROMANCE_FORMULAS[formula_main]
        rep_motifs = f.get("representative_motifs", []) or []
        keywords = f.get("title_pattern_keywords", []) or []
        all_signals = rep_motifs + keywords + [formula_main]  # 포뮬러 자체도 검사
        
        if all_signals:
            # ★ 의미 매칭으로 변경 (정확 매칭 + 동의어 + 부분)
            hits = [s for s in all_signals if _check_signal_semantic(s, text)]
            if hits:
                used.append(f"메인 포뮬러: {formula_main} (표지 발견: {', '.join(hits[:3])})")
            else:
                weak.append(f"메인 포뮬러 '{formula_main}' 표상 모티프 약함")
                # critical_missing에서 빼기 — 너무 엄격함
    
    # ─── 2) 보조 포뮬러 — 누락은 약함으로만 분류 ─────────
    formula_sub = concept.get("formula_sub", "")
    if formula_sub and formula_sub in ROMANCE_FORMULAS:
        f = ROMANCE_FORMULAS[formula_sub]
        rep_motifs = (f.get("representative_motifs", []) or []) + [formula_sub]
        if rep_motifs:
            hits = [s for s in rep_motifs if _check_signal_semantic(s, text)]
            if hits:
                used.append(f"보조 포뮬러: {formula_sub}")
            else:
                weak.append(f"보조 포뮬러 '{formula_sub}' 흔적 없음 (특정 회차에서만 등장 가능)")
    
    # ─── 3) 1순위 모티프 검증 (의미 매칭) ─────────────────────────
    rel_motifs = concept.get("relationship_motifs", {}) or {}
    primary = rel_motifs.get("primary", "")
    if primary and primary in RELATIONSHIP_MOTIFS_DICT:
        # ★ 의미 매칭 — 동의어 사전 활용
        if _check_signal_semantic(primary, text):
            used.append(f"1순위 모티프: {primary}")
        else:
            primary_clean = primary.replace("물", "").strip()
            if primary_clean and primary_clean in text:
                used.append(f"1순위 모티프: {primary}")
            else:
                weak.append(f"1순위 모티프 '{primary}' 표지 약함")
    
    # ─── 3-1) 보조 모티프(secondary) 검증 (의미 매칭) ────────────
    secondary = rel_motifs.get("secondary", []) or []
    for s_motif in secondary[:3]:  # 최대 3개만
        if s_motif and _check_signal_semantic(s_motif, text):
            used.append(f"보조 모티프: {s_motif}")
    
    # ─── 4) 이동 코드 — 빙의·회귀·환생 등 (의미 매칭) ─────────────
    movement_code = concept.get("movement_code", "")
    if movement_code:
        # ★ 의미 매칭 — "빙의" 정확 키워드 없어도 "다른 사람의 몸" 같은 표현이면 인정
        if _check_signal_semantic(movement_code, text):
            used.append(f"이동 코드: {movement_code}")
        else:
            weak.append(f"이동 코드 '{movement_code}' 본문 표지 부재 (배경 설정으로 충분 가능)")
    
    # ─── 5) 9종 인물 역할 — 캐릭터별 등장·차별화 ─────
    char_dict = _normalize_character_data(character_bible)
    if char_dict:
        chars_in_text = []
        for name, data in char_dict.items():
            if not isinstance(data, dict) or not name:
                continue
            if name in text:
                chars_in_text.append(name)
                role = data.get("narrative_role", "")
                if role:
                    used.append(f"인물 등장: {name} ({role})")
        
        # 동시 등장 회차에서 역할 다양성 검증
        if len(chars_in_text) >= 3:
            roles = [
                char_dict.get(n, {}).get("narrative_role", "")
                for n in chars_in_text
                if char_dict.get(n, {}).get("narrative_role")
            ]
            unique_roles = set(filter(None, roles))
            if len(unique_roles) < len(roles):
                weak.append(
                    f"다중 인물 회차인데 같은 역할 중복 — 평면화 위험 ({len(chars_in_text)}명 등장 / {len(unique_roles)}개 역할)"
                )
    
    # ─── 6) 마음 흐름 단계 키워드 검증 ────────────────
    if ep_number > 0 and total_eps > 0 and _CHAR_OK:
        orientation = detect_work_orientation(concept)
        try:
            stage = get_stage_for_episode_with_orientation(ep_number, total_eps, orientation)
        except Exception:
            stage = None
        
        if stage:
            inner_kw = stage.get("inner_state_keywords", []) or []
            behavior_kw = stage.get("behavior_keywords", []) or []
            stage_name = stage.get("name", "")
            
            # 키워드 부분 매칭 (전체 단어가 아니어도 핵심 명사가 들어가면 인정)
            inner_hits = _count_keyword_partial_hits(inner_kw, text)
            behavior_hits = _count_keyword_partial_hits(behavior_kw, text)
            
            if inner_hits + behavior_hits >= 3:
                used.append(f"마음 흐름 {stage.get('stage', '')}단계 ({stage_name}) — 키워드 {inner_hits + behavior_hits}개 반영")
            elif inner_hits + behavior_hits >= 1:
                weak.append(f"마음 흐름 {stage_name} 키워드 약함 (반영 {inner_hits + behavior_hits}개)")
            else:
                missing.append(f"마음 흐름 {stage_name} 본문 표지 거의 없음")
    
    # ─── 점수 산출 (정밀화) ─────────────────────────
    used_count = len(used)
    weak_count = len(weak)
    missing_count = len(missing)
    critical_count = len(critical_missing)
    
    total_signals = used_count + weak_count + missing_count
    if total_signals == 0:
        score = 60  # 검사할 신호 없으면 중립
    else:
        # 사용=10점, 약함=6점(이전 5점→6점), 누락=-3점(이전 -5점→-3점), 핵심누락=-10점(이전 -15점→-10점)
        # 페널티 완화로 거짓 음성 감소
        raw = used_count * 10 + weak_count * 6 - missing_count * 3 - critical_count * 10
        target = total_signals * 10
        score = int(max(0, min(100, (raw / target) * 100))) if target > 0 else 60
        
        # ★ 거짓 음성 완화 — 최소 40점 보장 (사용 신호가 1개 이상이면)
        if used_count >= 1 and score < 40:
            score = 40
        # ★ 사용 신호가 풍부하면(3개+) 최소 65점 보장
        if used_count >= 3 and score < 65:
            score = 65
    
    return {
        "used": used,
        "weak": weak,
        "missing": missing,
        "score": score,
        "critical_missing": critical_missing,
    }


def _normalize_character_data(character_bible):
    """캐릭터 데이터를 list/dict 어느 형태로 들어와도 dict로 변환."""
    if not character_bible:
        return {}
    if isinstance(character_bible, dict):
        # 이미 dict — 단, "protagonist" 같은 v2.6.4 구조면 평탄화
        if "protagonist" in character_bible or "love_interests" in character_bible:
            return _flatten_v264_bible(character_bible)
        return character_bible
    if isinstance(character_bible, list):
        result = {}
        for c in character_bible:
            if isinstance(c, dict) and c.get("name"):
                result[c["name"]] = c
        return result
    return {}


def _flatten_v264_bible(bible: dict) -> dict:
    """v2.6.4 캐릭터 바이블 구조를 {name: data} 평면 dict로 변환."""
    result = {}
    # protagonist
    p = bible.get("protagonist")
    if isinstance(p, dict) and p.get("name"):
        result[p["name"]] = p
    # villain
    v = bible.get("villain")
    if isinstance(v, dict) and v.get("name"):
        result[v["name"]] = v
    # love_interests, supporting (list)
    for key in ("love_interests", "supporting"):
        items = bible.get(key, [])
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and item.get("name"):
                    result[item["name"]] = item
    return result


def _count_keyword_partial_hits(keywords: list, text: str) -> int:
    """키워드 리스트에서 본문에 부분 매칭되는 개수 카운트.
    
    "분노가 미래를 향함" 같은 긴 구절은 "분노", "미래" 핵심 명사로 분리해 검사.
    """
    hits = 0
    matched_kw = set()
    for kw in keywords:
        if not kw or kw in matched_kw:
            continue
        # 직접 매칭
        if kw in text:
            hits += 1
            matched_kw.add(kw)
            continue
        # 핵심 명사 분리 매칭 (한글 2~4자 명사 추출)
        nouns = [w for w in kw.replace(",", " ").replace("·", " ").split() 
                 if len(w) >= 2]
        for noun in nouns:
            if noun in text and noun not in matched_kw:
                hits += 1
                matched_kw.add(noun)
                break
    return hits


# ============================================================================
# 2. compute_episode_validation_score — 11축 종합 점수 (v3.3)
# ============================================================================
def compute_episode_validation_score(
    concept: dict,
    character_bible,
    written_text: str,
    ep_number: int = 0,
    total_eps: int = 42,
    cliffhanger_type: Optional[str] = None,
    plant_map: Optional[dict] = None,  # ★ v3.0+ — 떡밥 활용도 검수용
    platform: str = "카카오페이지",     # ★ v3.2+ — 분량 표준 결정용
    intimacy_schedule: Optional[list] = None,  # ★ v3.3+ — 19금 콘텐츠 검수용
    rating_mode: str = "",              # ★ v3.3+ — 등급별 가중치 결정용
) -> dict:
    """회차 단독 11축 종합 점수 (v3.3부터 확장).
    
    Returns:
        {
            "axes": {
                # 기존 10축 (v3.2)
                "MATERIAL_USAGE":         {score, critical, detail},
                "CHARACTER_CONSISTENCY":  {...},
                "CLIFFHANGER_STRENGTH":   {...},
                "MISE_EN_SCENE":          {...},
                "MARKET_VIABILITY":       {...},
                "PLANT_USAGE":            {...},
                "DIALOGUE_RATIO":         {...},
                "NAMING_DISCIPLINE":      {...},
                "PROSE_HYGIENE":          {...},
                "LENGTH_DISCIPLINE":      {...},
                # 신규 1축 (v3.3)
                "ADULT_CONTENT_FIDELITY": {score, applicable, detail},
            },
            "overall": 0~100,
            "grade": "PASS|WARN|REDO",
            "verdict": "이 회차는 ...",
            "weights_used": dict,  # 적용된 가중치 (등급별 동적)
        }
    """
    # rating_mode를 concept에서 자동 추출 (직접 인자 없으면)
    if not rating_mode and concept:
        serial_config = concept.get("serial_config", {}) if isinstance(concept, dict) else {}
        rating_mode = serial_config.get("rating_mode", "")
    
    axes = {}
    
    # ─── 기존 6축 ─────────────────────────────────
    # 1) MATERIAL_USAGE
    mu = validate_planning_to_writing_mapping(
        concept, character_bible, written_text, ep_number, total_eps
    )
    axes["MATERIAL_USAGE"] = {
        "score": mu["score"],
        "critical": True,
        "detail": {
            "used_count": len(mu["used"]),
            "weak_count": len(mu["weak"]),
            "missing_count": len(mu["missing"]),
            "critical_missing": mu["critical_missing"],
        }
    }
    
    # 2) CHARACTER_CONSISTENCY
    char_score = _score_character_consistency(character_bible, written_text)
    axes["CHARACTER_CONSISTENCY"] = {
        "score": char_score["score"],
        "critical": True,
        "detail": char_score["detail"],
    }
    
    # 3) CLIFFHANGER_STRENGTH
    cliff_score = _score_cliffhanger_strength(written_text, cliffhanger_type)
    axes["CLIFFHANGER_STRENGTH"] = {
        "score": cliff_score["score"],
        "critical": False,
        "detail": cliff_score["detail"],
    }
    
    # 4) MISE_EN_SCENE
    mise_score = _score_mise_en_scene(written_text)
    axes["MISE_EN_SCENE"] = {
        "score": mise_score["score"],
        "critical": False,
        "detail": mise_score["detail"],
    }
    
    # 5) MARKET_VIABILITY (회차 단위)
    market_score = _score_market_viability_episode(
        concept, written_text, ep_number, total_eps
    )
    axes["MARKET_VIABILITY"] = {
        "score": market_score["score"],
        "critical": False,
        "detail": market_score["detail"],
    }
    
    # 6) PLANT_USAGE — 떡밥 활용도 (v3.0+)
    plant_score = _score_plant_usage(plant_map, written_text, ep_number)
    axes["PLANT_USAGE"] = {
        "score": plant_score["score"],
        "critical": plant_score.get("critical", False),
        "detail": plant_score["detail"],
    }
    
    # ─── 신규 4축 (v3.2) ──────────────────────────
    # 7) DIALOGUE_RATIO
    dlg_score = _score_dialogue_ratio(written_text)
    axes["DIALOGUE_RATIO"] = {
        "score": dlg_score["score"],
        "critical": False,
        "detail": dlg_score["detail"],
    }
    
    # 8) NAMING_DISCIPLINE
    naming_score = _score_naming_discipline(written_text, character_bible)
    axes["NAMING_DISCIPLINE"] = {
        "score": naming_score["score"],
        "critical": False,
        "detail": naming_score["detail"],
    }
    
    # 9) PROSE_HYGIENE
    hygiene_score = _score_prose_hygiene(written_text)
    axes["PROSE_HYGIENE"] = {
        "score": hygiene_score["score"],
        "critical": False,
        "detail": hygiene_score["detail"],
    }
    
    # 10) LENGTH_DISCIPLINE
    length_score = _score_length_discipline(written_text, platform=platform)
    axes["LENGTH_DISCIPLINE"] = {
        "score": length_score["score"],
        "critical": False,
        "detail": length_score["detail"],
    }
    
    # ─── [v3.3 신규] 11번째 축 ──────────────────────
    # 11) ADULT_CONTENT_FIDELITY — 19금 콘텐츠 충실도
    intimacy_for_ep = _get_intimacy_schedule_for_ep_helper(intimacy_schedule, ep_number)
    target_audience = ""
    if concept and isinstance(concept, dict):
        target_audience = concept.get("target_audience", "")
    
    adult_score = _score_adult_content_fidelity(
        text=written_text,
        rating_mode=rating_mode,
        target_audience=target_audience,
        ep_number=ep_number,
        intimacy_schedule_for_ep=intimacy_for_ep,
    )
    axes["ADULT_CONTENT_FIDELITY"] = {
        "score": adult_score["score"],
        "critical": False,
        "applicable": adult_score["applicable"],
        "detail": adult_score["detail"],
    }
    
    # ─── 등급별 동적 가중치 (v3.3) ─────────────────
    is_adult = bool(rating_mode and ("19" in rating_mode or "듀얼" in rating_mode))
    
    if is_adult:
        # 19금/듀얼 작품 — ADULT_CONTENT_FIDELITY 0.40, 나머지 10축 0.60
        weights = {
            "ADULT_CONTENT_FIDELITY": 0.40,
            "DIALOGUE_RATIO":         0.12,
            "MATERIAL_USAGE":         0.08,
            "NAMING_DISCIPLINE":      0.08,
            "PROSE_HYGIENE":          0.08,
            "PLANT_USAGE":            0.06,
            "CHARACTER_CONSISTENCY":  0.04,
            "CLIFFHANGER_STRENGTH":   0.04,
            "MARKET_VIABILITY":       0.04,
            "MISE_EN_SCENE":          0.03,
            "LENGTH_DISCIPLINE":      0.03,
        }
    else:
        # 15금/미설정 작품 — ADULT_CONTENT_FIDELITY 0, 기존 10축 v3.2 가중치 유지
        weights = {
            "ADULT_CONTENT_FIDELITY": 0.00,
            "MATERIAL_USAGE":         0.12,
            "CHARACTER_CONSISTENCY":  0.08,
            "CLIFFHANGER_STRENGTH":   0.08,
            "MISE_EN_SCENE":          0.05,
            "MARKET_VIABILITY":       0.08,
            "PLANT_USAGE":            0.09,
            "DIALOGUE_RATIO":         0.20,
            "NAMING_DISCIPLINE":      0.12,
            "PROSE_HYGIENE":          0.12,
            "LENGTH_DISCIPLINE":      0.06,
        }
    
    overall = sum(axes[ax]["score"] * w for ax, w in weights.items())
    overall = int(round(overall))
    
    # 등급
    if overall >= VALIDATION_THRESHOLDS["episode_pass"]:
        grade = "PASS"
    elif overall >= VALIDATION_THRESHOLDS["episode_warn"]:
        grade = "WARN"
    else:
        grade = "REDO"
    
    # critical 누락이 있으면 강제 REDO
    has_critical = any(
        axes[ax]["critical"] and axes[ax]["score"] < VALIDATION_THRESHOLDS["episode_redo"]
        for ax in axes
    )
    if has_critical and grade == "PASS":
        grade = "WARN"
    
    # verdict
    verdict = _generate_verdict(grade, axes, overall)
    
    return {
        "axes": axes,
        "overall": overall,
        "grade": grade,
        "verdict": verdict,
        "weights_used": weights,
        "rating_mode": rating_mode,
    }


def _score_character_consistency(character_bible, text: str) -> dict:
    """[v3.0+ 정밀화] 캐릭터 일관성·차별화 점수.
    
    이번 버전: 부분 이름 매칭 + 단독 회차 보너스 + 풀네임/별명 모두 인정.
    """
    char_dict = _normalize_character_data(character_bible)
    if not char_dict:
        return {"score": 70, "detail": {"reason": "캐릭터 바이블 없음"}}
    
    chars_in_text = []
    for name in char_dict.keys():
        if not name:
            continue
        # ★ 정확 매칭
        if name in text:
            chars_in_text.append(name)
            continue
        # ★ 부분 매칭 — 풀네임이 안 나와도 핵심 부분(성+이름 첫 글자 등)이 나오면 인정
        # "한시호 (유빈의 몸)" → "한시호" 또는 "시호"가 나오면 인정
        # 괄호·공백·물음표 제거 후 핵심 이름 추출
        import re
        # 괄호 안 부가 정보 제거
        clean_name = re.sub(r'[\(\[].*?[\)\]]', '', name).strip()
        # 한글 이름 부분만 추출
        name_parts = re.findall(r'[가-힣]{2,5}', clean_name)
        for part in name_parts:
            if part in text:
                chars_in_text.append(name)
                break
    
    chars_in_text = list(set(chars_in_text))  # 중복 제거
    
    if not chars_in_text:
        return {
            "score": 65,  # 60 → 65 (이름 안 나와도 너무 페널티 주지 말 것)
            "detail": {"reason": "본문에 캐릭터 이름 등장 없음 (1인칭 시점일 수 있음)"}
        }
    
    # 동시 등장 인물 수
    n = len(chars_in_text)
    if n == 1:
        # ★ 단독 회차 — 보너스 (1인칭 정체성 게임 회차에 자주 발생)
        return {
            "score": 88,  # 85 → 88
            "detail": {"chars": chars_in_text, "differentiation": "단독 회차 (정체성 집중)"}
        }
    
    # 역할 다양성 검사
    roles = []
    for name in chars_in_text:
        role = char_dict.get(name, {}).get("narrative_role", "")
        if role:
            roles.append(role)
    
    if not roles:
        return {
            "score": 75,  # 65 → 75 (narrative_role 미설정만으로 너무 깎지 말 것)
            "detail": {
                "chars": chars_in_text,
                "reason": "narrative_role 미설정 인물 다수 (작가 결정 영역)"
            }
        }
    
    role_diversity = len(set(roles)) / len(roles) if roles else 0
    
    # 모에 속성 검출
    moe_signals = 0
    for name in chars_in_text:
        moe_attrs = char_dict.get(name, {}).get("moe_attributes", []) or []
        for attr in moe_attrs:
            attr_name = attr.split(":", 1)[-1].strip() if ":" in attr else attr
            if attr_name and attr_name in text:
                moe_signals += 1
    
    # ★ 점수 산출 (기준점 70 → 75)
    base = 75
    base += int(role_diversity * 20)         # 역할 다양성 최대 +20
    base += min(15, moe_signals * 3)         # 모에 표지 최대 +15
    base = max(0, min(100, base))
    
    return {
        "score": base,
        "detail": {
            "chars": chars_in_text,
            "role_diversity": round(role_diversity, 2),
            "moe_signals": moe_signals,
        }
    }


def _score_cliffhanger_strength(text: str, cliff_type: Optional[str] = None) -> dict:
    """클리프행어 강도 점수 (본문 마지막 500자 분석)."""
    if not text or len(text) < 100:
        return {"score": 50, "detail": {"reason": "본문 너무 짧음"}}
    
    last_chunk = text[-600:]
    
    # 클리프행어 신호 패턴
    signals = {
        "Reveal":   ["밝혀졌", "드러났", "알게 되", "그제야 알", "정체"],
        "Tears":    ["눈물", "흐느꼈", "울었", "흐려진", "젖은"],
        "Threat":   ["위험", "다가왔", "다가오", "노려보", "위협"],
        "Choice":   ["선택", "결정해", "결정해야", "갈림길", "기로"],
        "Reversal": ["뒤집힌", "달랐다", "정반대", "예상과 달", "착각"],
        "Slap":     ["뺨", "쳤다", "후려", "주먹"],
        "Arrival":  ["도착했", "들어왔", "나타났", "마주쳤"],
    }
    
    detected_types = []
    total_hits = 0
    for ctype, patterns in signals.items():
        hits = sum(1 for p in patterns if p in last_chunk)
        if hits > 0:
            detected_types.append(ctype)
            total_hits += hits
    
    # 마지막 문장 길이 (짧은 단문이 임팩트 강함)
    last_sentence = last_chunk.split(".")[-2] if "." in last_chunk else last_chunk[-100:]
    impact_short = len(last_sentence.strip()) < 80
    
    # 점수
    base = 60
    if detected_types:
        base += min(25, total_hits * 5)
    if impact_short:
        base += 10
    if cliff_type and cliff_type in detected_types:
        base += 10  # 의도한 유형이 실제 발현됨
    
    base = max(0, min(100, base))
    
    return {
        "score": base,
        "detail": {
            "detected_types": detected_types,
            "intended_type": cliff_type or "(미지정)",
            "impact_short": impact_short,
        }
    }


def _score_mise_en_scene(text: str) -> dict:
    """묘사·장면 강도 점수."""
    if not text:
        return {"score": 50, "detail": {}}
    
    length = len(text)
    
    # 대사 비율
    dialogue_count = text.count("\u201c") + text.count("\"") + text.count("「")
    dialogue_count = dialogue_count // 2  # 시작·끝 쌍이므로 절반
    
    # 감각 묘사 키워드
    sensory_kw = [
        "보였다", "보이는", "느껴졌", "느껴지는", "들렸다", "들리는",
        "맡았다", "맡은", "스쳤다", "차가웠", "뜨거웠", "달콤", "쓰라린",
    ]
    sensory_hits = sum(1 for kw in sensory_kw if kw in text)
    
    # 회차 분량 적정성
    if 4500 <= length <= 6500:
        length_score = 25
    elif 4000 <= length <= 7500:
        length_score = 20
    elif 3000 <= length <= 8500:
        length_score = 15
    else:
        length_score = 10
    
    base = 50 + length_score + min(15, sensory_hits * 3) + min(10, dialogue_count // 5)
    base = max(0, min(100, base))
    
    return {
        "score": base,
        "detail": {
            "length": length,
            "sensory_hits": sensory_hits,
            "approx_dialogue_count": dialogue_count,
        }
    }


def _score_market_viability_episode(
    concept: dict, text: str, ep_number: int, total_eps: int
) -> dict:
    """[v3.0+ 정밀화] 회차 단위 시장 트리거 충족도.
    
    이전: 5개 트리거 (메인 포뮬러, 이동 코드, 장르, 클리프행어, 분량)
    이번: 8개 트리거 + 본문 신호 풍부 인식
    """
    if not text:
        return {"score": 50, "detail": {}}
    
    triggers_met = 0
    detail = {}
    total_triggers = 8  # 5 → 8개로 확장
    
    # 1) 인기순 부합 — 검증된 모티프 차용 표지
    formula_main = concept.get("formula_main", "")
    if formula_main:
        triggers_met += 1
        detail["popular_formula"] = formula_main
    
    # 2) 소재 강도 — 이동 코드 또는 강한 premise
    movement = concept.get("movement_code", "")
    if movement:
        triggers_met += 1
        detail["movement_code"] = movement
    
    # 3) 장르 적합
    if concept.get("genre", ""):
        triggers_met += 1
    
    # 4) 클리프행어 임팩트 (확장 키워드)
    last_chunk = text[-500:] if len(text) > 500 else text
    cliff_signals = [
        "선택", "결정", "위협", "도착", "정체", "뒤집",
        "누구", "왜", "어떻게", "정말", "진짜", "사실은",
        "?", "...", "—", "그런데", "그러나",
    ]
    cliff_hits = sum(1 for s in cliff_signals if s in last_chunk)
    if cliff_hits >= 2:
        triggers_met += 1
        detail["cliffhanger_impact"] = f"강함 (신호 {cliff_hits}개)"
    elif cliff_hits >= 1:
        detail["cliffhanger_impact"] = f"약함 (신호 {cliff_hits}개)"
    
    # 5) 가격 가치 — 분량 적정
    length = len(text)
    if 4500 <= length <= 6500:
        triggers_met += 1
        detail["length_appropriate"] = length
    elif 3500 <= length < 4500 or 6500 < length <= 7500:
        # 약간 벗어나도 절반 인정
        triggers_met += 0.5
        detail["length_borderline"] = length
    
    # ★ v3.0+ 신규 트리거 6) 첫 문장 임팩트 (★ 매우 중요)
    first_lines = text.split('\n')[:5]
    first_text = ' '.join(first_lines)[:200]
    impact_first = [
        "죽었", "사라졌", "끝났", "시작", "처음",
        "그날", "그때", "갑자기", "분명히", "확실히",
        "?", "!",
    ]
    if any(s in first_text for s in impact_first):
        triggers_met += 1
        detail["opening_hook"] = "첫 문장 임팩트 강함"
    
    # ★ v3.0+ 신규 트리거 7) 정체성 게임 (환생·빙의 작품 핵심)
    if movement in ("환생", "빙의", "회귀", "전생"):
        identity_signals = [
            "누구", "내가 누구", "여기는 어디", "이 몸",
            "거울", "낯설", "다른 사람", "내가 아니",
        ]
        if sum(1 for s in identity_signals if s in text) >= 1:
            triggers_met += 1
            detail["identity_game"] = "정체성 게임 신호 감지"
    else:
        # 환생물 아닌 경우 자동 인정
        triggers_met += 0.5
    
    # ★ v3.0+ 신규 트리거 8) 정서 강도 (감각·감정 키워드)
    emotion_signals = [
        "심장", "가슴", "숨", "떨렸", "흔들렸", "울렸", "울컥",
        "차가웠", "뜨거웠", "타올랐", "얼어붙",
    ]
    emotion_hits = sum(1 for s in emotion_signals if s in text)
    if emotion_hits >= 3:
        triggers_met += 1
        detail["emotional_intensity"] = f"강함 ({emotion_hits}개)"
    elif emotion_hits >= 1:
        triggers_met += 0.5
        detail["emotional_intensity"] = f"중간 ({emotion_hits}개)"
    
    score = int((triggers_met / total_triggers) * 100)
    detail["triggers_met"] = f"{triggers_met}/{total_triggers}"
    
    # ★ 거짓 음성 방지 — 본문 분량 적정 + 형식 다 갖췄으면 최소 60점
    if length >= 4500 and length <= 6500 and formula_main:
        score = max(score, 60)
    
    return {"score": score, "detail": detail}


def _score_plant_usage(plant_map: Optional[dict], text: str, ep_number: int) -> dict:
    """[v3.0+] 떡밥 활용도 점수.
    
    이번 회차에 심기·힌트·회수해야 할 떡밥이 본문에 실제로 반영됐는지 검증.
    
    채점 기준:
    - 심기 떡밥: 떡밥 명사·대표 키워드가 본문에 등장 (50% 비중)
    - 힌트 떡밥: 떡밥 명사가 본문에 한 번이라도 등장 (30% 비중)
    - 회수 떡밥: payoff_description 키워드가 본문에 등장 (★ critical, 누락 시 강제 REDO)
    
    회차에 떡밥이 없으면 N/A 처리 (점수 80, 중립).
    
    Args:
        plant_map: {"plants": [...]} 형태의 떡밥 맵
        text: 회차 본문
        ep_number: 회차 번호
    
    Returns:
        {
            "score": 0~100,
            "critical": bool (회수 누락 시 True),
            "detail": {
                "plants_to_plant": [...],   # 이번 회차 심기 대상
                "plants_to_hint": [...],    # 이번 회차 힌트 대상
                "plants_to_payoff": [...],  # 이번 회차 회수 대상
                "planted_ok": [...],        # 잘 반영된 떡밥
                "missed": [...],            # 누락된 떡밥 (★ critical)
            }
        }
    """
    if not plant_map or not isinstance(plant_map, dict):
        return {
            "score": 80,
            "critical": False,
            "detail": {"reason": "떡밥 맵 없음 — 검수 생략 (중립 80점)"}
        }
    
    plants = plant_map.get("plants", [])
    if not plants:
        return {
            "score": 80,
            "critical": False,
            "detail": {"reason": "떡밥 맵 비어있음 — 중립 80점"}
        }
    
    # 이번 회차 관련 떡밥 분류
    to_plant = [p for p in plants if p.get("plant_ep") == ep_number]
    to_hint = [p for p in plants if ep_number in p.get("hints", [])]
    to_payoff = [p for p in plants if p.get("payoff_ep") == ep_number]
    
    if not (to_plant or to_hint or to_payoff):
        return {
            "score": 85,
            "critical": False,
            "detail": {
                "reason": "이번 회차에 관련 떡밥 없음",
                "plants_to_plant": [],
                "plants_to_hint": [],
                "plants_to_payoff": [],
                "planted_ok": [],
                "missed": [],
            }
        }
    
    # 검수 — 본문에 흔적 검색
    planted_ok = []
    missed = []
    critical_missed = []
    
    # ─── [심기] 떡밥 검증 ─────────────────
    plant_score_sum = 0
    plant_score_max = 0
    for p in to_plant:
        plant_score_max += 50
        name = p.get("name", "")
        # ★ 정밀화 — 동의어 매칭도 시도
        keywords = _extract_plant_keywords(name, p.get("description", ""))
        # 1) 정확 키워드 매칭
        hits = sum(1 for kw in keywords if kw and kw in text)
        # 2) 떡밥 이름 자체의 동의어 매칭 (의미 매칭 함수 활용)
        if _check_signal_semantic(name, text):
            hits += 2  # 동의어 매칭은 강한 신호로 인정
        
        if hits >= 3:  # 2 → 3 (동의어 보너스 반영)
            planted_ok.append(f"[심기] {name} (키워드 {hits}개)")
            plant_score_sum += 50
        elif hits >= 1:
            planted_ok.append(f"[심기] {name} (반영, 키워드 {hits}개)")
            plant_score_sum += 35  # 30 → 35 (1개도 인정)
        else:
            missed.append(f"[심기] {name} 본문에 흔적 없음")
            plant_score_sum += 10  # 0 → 10 (완전 0점은 너무 가혹)
    
    # ─── [힌트] 떡밥 검증 ─────────────────
    hint_score_sum = 0
    hint_score_max = 0
    for p in to_hint:
        hint_score_max += 30
        name = p.get("name", "")
        keywords = _extract_plant_keywords(name, p.get("description", ""))
        hits = sum(1 for kw in keywords if kw and kw in text)
        if _check_signal_semantic(name, text):
            hits += 2
        if hits >= 1:
            planted_ok.append(f"[힌트] {name}")
            hint_score_sum += 30
        else:
            missed.append(f"[힌트] {name} 본문에 흔적 없음")
            hint_score_sum += 10  # 0 → 10
    
    # ─── [회수] 떡밥 검증 (★ critical) ────
    payoff_score_sum = 0
    payoff_score_max = 0
    for p in to_payoff:
        payoff_score_max += 100
        name = p.get("name", "")
        payoff_desc = p.get("payoff_description", "")
        # 회수 방식 키워드도 검색
        keywords = _extract_plant_keywords(name, p.get("description", ""))
        payoff_keywords = _extract_plant_keywords("", payoff_desc) if payoff_desc else []
        all_kw = keywords + payoff_keywords
        
        plant_hits = sum(1 for kw in keywords if kw and kw in text)
        payoff_hits = sum(1 for kw in payoff_keywords if kw and kw in text)
        total_hits = plant_hits + payoff_hits
        
        if total_hits >= 3:
            planted_ok.append(f"[회수] {name} (강함, 키워드 {total_hits}개)")
            payoff_score_sum += 100
        elif total_hits >= 1:
            planted_ok.append(f"[회수] {name} (약함, 키워드 {total_hits}개)")
            payoff_score_sum += 60
            missed.append(f"⚠️ [회수] {name} 약하게 회수됨 — 카타르시스 부족 가능")
        else:
            critical_missed.append(f"❌ [회수] {name} 회수 누락 (★ 재집필 필수)")
            missed.append(f"❌ [회수] {name} 회수 누락")
            payoff_score_sum += 0
    
    # ─── 종합 점수 ───────────────────────
    total_max = plant_score_max + hint_score_max + payoff_score_max
    total_sum = plant_score_sum + hint_score_sum + payoff_score_sum
    
    score = int((total_sum / total_max) * 100) if total_max > 0 else 80
    
    # 회수 누락 시 critical
    is_critical = bool(critical_missed)
    if is_critical:
        score = min(score, 50)  # 회수 누락은 50점 이하로 강제
    
    return {
        "score": score,
        "critical": is_critical,
        "detail": {
            "plants_to_plant": [p.get("name", "") for p in to_plant],
            "plants_to_hint": [p.get("name", "") for p in to_hint],
            "plants_to_payoff": [p.get("name", "") for p in to_payoff],
            "planted_ok": planted_ok,
            "missed": missed,
            "critical_missed": critical_missed,
        }
    }


# ============================================================================
# [v3.2 신규] 신규 4축 점수 함수
# ============================================================================

def _score_dialogue_ratio(text: str) -> dict:
    """[v3.2 신규] 대사 비율 점수.
    
    SYSTEM_PROMPT 룰: 대사 비율 40% 이상 (모바일 가독성).
    
    측정:
    - 단락 단위로 큰따옴표(")로 시작하는 단락의 글자수 비율
    - 40% 이상 = 90~100점 (시장 표준)
    - 30~40%  = 60~89점 (양호)
    - 20~30%  = 30~59점 (미달)
    - 20% 미만 = 0~29점 (심각)
    
    Returns:
        {"score": 0~100, "detail": {"ratio_pct", "dialogue_chars", "total_chars", "threshold"}}
    """
    # 기본 detail 구조 (가드 케이스에서도 유지)
    default_detail = {
        "ratio_pct": 0.0,
        "dialogue_chars": 0,
        "total_chars": 0,
        "threshold": 40,
    }
    
    if not text or len(text) < 100:
        return {"score": 50, "detail": {**default_detail, "reason": "본문 너무 짧음"}}
    
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return {"score": 50, "detail": {**default_detail, "reason": "단락 없음"}}
    
    # 회차 제목(EP로 시작) 제외
    body_lines = [l for l in lines if not l.startswith("EP")]
    
    dialogue_chars = 0
    total_chars = 0
    for line in body_lines:
        line_len = len(line)
        total_chars += line_len
        # 큰따옴표로 시작 = 대사 단락
        if line.startswith('"') or line.startswith('\u201c') or line.startswith('\u201d'):
            dialogue_chars += line_len
    
    if total_chars == 0:
        return {"score": 50, "detail": {**default_detail, "reason": "본문 글자수 0"}}
    
    ratio = dialogue_chars / total_chars
    ratio_pct = ratio * 100
    
    # 점수 산출
    if ratio_pct >= 40:
        # 40% 이상 — 표준 충족. 50% 이상이면 만점
        score = min(100, 90 + int((ratio_pct - 40) * 1.0))
    elif ratio_pct >= 30:
        # 30~40% — 양호. 선형 60→89
        score = 60 + int((ratio_pct - 30) * 2.9)
    elif ratio_pct >= 20:
        # 20~30% — 미달. 선형 30→59
        score = 30 + int((ratio_pct - 20) * 2.9)
    else:
        # 20% 미만 — 심각. 선형 0→29
        score = max(0, int(ratio_pct * 1.45))
    
    return {
        "score": score,
        "detail": {
            "ratio_pct": round(ratio_pct, 1),
            "dialogue_chars": dialogue_chars,
            "total_chars": total_chars,
            "threshold": 40,
        }
    }


def _score_naming_discipline(text: str, character_bible=None) -> dict:
    """[v3.2 신규] 캐릭터 호명 + 정체성 키워드 절제 점수.
    
    A15: 정체성 키워드(회귀·환생·이세계 등 추상 명사) 회차당 5회 이하
    A16: 캐릭터 이름 호명 단락당 2회 이하
    
    측정:
    - 단락당 같은 이름 3회 이상 등장 = 위반
    - 회차 전체에서 핵심 캐릭터 이름 등장 횟수 (관대 기준: 회차당 30회 초과 시 페널티)
    - 정체성 키워드(환생/회귀/빙의/이번 생/다른 사람 등) 회차당 등장 횟수
    
    Returns:
        {"score": 0~100, "detail": {위반 내용}}
    """
    if not text:
        return {"score": 50, "detail": {"reason": "본문 없음"}}
    
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    body_paragraphs = [p for p in paragraphs if not p.startswith("EP")]
    
    # 캐릭터 이름 후보 추출 (풀네임 + 줄임형 모두)
    # 예: "한시호 (유빈의 몸)" → ["한시호", "시호"] 둘 다 추출
    name_candidates = []
    if character_bible:
        char_dict = _normalize_character_data(character_bible)
        import re
        for full_name in char_dict.keys():
            if not full_name:
                continue
            # 괄호 안 부가 정보 제거
            clean = re.sub(r'[\(\[].*?[\)\]]', '', full_name).strip()
            # 한글 이름 부분 추출
            parts = re.findall(r'[가-힣]{2,5}', clean)
            for part in parts:
                if part not in name_candidates:
                    name_candidates.append(part)
                # ★ 한국 이름 풀네임(3글자)에서 성을 떼고 줄임형도 추가
                # 예: "한시호" → "시호", "박재윤" → "재윤"
                if len(part) == 3:
                    short = part[1:]
                    if len(short) == 2 and short not in name_candidates:
                        name_candidates.append(short)
                # 4글자 이름(예: 김지훈우)도 비슷하게
                elif len(part) == 4:
                    short = part[1:]  # 3글자 줄임
                    if short not in name_candidates:
                        name_candidates.append(short)
    
    # 단락당 같은 이름 3회 이상 위반 카운트 (풀네임 + 줄임형 중복 카운트 방지)
    # 풀네임이 단락에 있으면 그 부분은 빼고 줄임형 카운트
    a16_violations = 0
    for para in body_paragraphs:
        violated = False
        for name in name_candidates:
            count = para.count(name)
            # 단축형 카운트 시 풀네임에 포함된 건 빼기
            for other in name_candidates:
                if other != name and len(other) > len(name) and name in other:
                    count -= para.count(other)
            if count >= 3:
                a16_violations += 1
                violated = True
                break  # 단락당 1번만 카운트
        # done
    
    # 회차 전체 이름 호명 빈도 (단축형은 풀네임 매칭 제외)
    name_total_counts = {}
    for name in name_candidates:
        if not name:
            continue
        raw_count = text.count(name)
        # 단축형이면 풀네임에 포함된 건 빼기
        for other in name_candidates:
            if other != name and len(other) > len(name) and name in other:
                raw_count -= text.count(other)
        if raw_count > 0:
            name_total_counts[name] = raw_count
    
    # 회차당 30회 초과 이름 수
    over_30_names = [n for n, c in name_total_counts.items() if c > 30]
    
    # A15 정체성 키워드 (추상 명사)
    identity_kws = ["환생", "회귀", "빙의", "전이", "이세계", "다음 생", "이번 생", "다른 사람", "내 몸", "이 몸"]
    identity_total = sum(text.count(kw) for kw in identity_kws)
    
    # ─ 점수 산출 ─
    score = 100  # 기본 만점에서 페널티 차감
    
    # A16 위반 페널티 (단락당 같은 이름 3회+)
    if a16_violations > 0:
        # 회차 단락 수 대비 위반 비율
        violation_rate = a16_violations / max(len(body_paragraphs), 50)
        a16_penalty = min(40, int(violation_rate * 200))  # 최대 40점 차감
        score -= a16_penalty
    
    # 회차당 호명 페널티 — 초과 횟수에 비례
    # 30~40회: -5, 40~50회: -15, 50~70회: -25, 70회+: -40
    for name, count in name_total_counts.items():
        if count > 70:
            score -= 40
        elif count > 50:
            score -= 25
        elif count > 40:
            score -= 15
        elif count > 30:
            score -= 5
    # 최대 차감 캡 (캐릭터 여러 명 초과해도 50점까지만 차감)
    if score < 50:
        score = max(50, score)
    
    # A15 정체성 키워드 초과 페널티 (15회 이상)
    if identity_total > 15:
        kw_penalty = min(20, int((identity_total - 15) * 1.5))
        score -= kw_penalty
    
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "detail": {
            "a16_paragraph_violations": a16_violations,
            "names_over_30": over_30_names,
            "name_total_counts": {n: c for n, c in name_total_counts.items() if c > 10},
            "identity_keyword_total": identity_total,
            "threshold_a16": "단락당 3회 이상 위반",
            "threshold_naming": "회차당 30회 초과",
            "threshold_identity": "회차당 15회 초과",
        }
    }


def _score_prose_hygiene(text: str, prev_episodes_text: str = "") -> dict:
    """[v3.2 신규] 산문 위생 점수 — said 뒤붙이기 + 회차 간 반복 문구.
    
    A1: said 뒤붙이기 금지 ("X가 말했다" 패턴)
    회차 간 반복 문구 — 본 회차에서 너무 자주 등장하는 짧은 구절
    
    측정:
    - "X가 말했다" / "X는 말했다" / "X가 물었다" / "X가 대답했다" 같은 패턴 빈도
    - 같은 짧은 구절(8~25자) 이번 회차에서 4회 이상 반복
    
    Returns:
        {"score": 0~100, "detail": {...}}
    """
    if not text:
        return {"score": 50, "detail": {"reason": "본문 없음"}}
    
    import re
    
    # A1: said 뒤붙이기 패턴 (한글 이름 + 조사 + 발화 동사)
    said_patterns = [
        r'[가-힣]{2,4}[가는이은]\s*말했다\.?',
        r'[가-힣]{2,4}[가는이은]\s*물었다\.?',
        r'[가-힣]{2,4}[가는이은]\s*대답했다\.?',
        r'[가-힣]{2,4}[가는이은]\s*외쳤다\.?',
        r'[가-힣]{2,4}[가는이은]\s*속삭였다\.?',
        r'[가-힣]{2,4}[가는이은]\s*되물었다\.?',
        r'[가-힣]{2,4}의\s*입에서\s*나왔다\.?',
    ]
    
    said_count = 0
    said_examples = []
    for pat in said_patterns:
        matches = re.findall(pat, text)
        said_count += len(matches)
        if matches and len(said_examples) < 5:
            said_examples.extend(matches[:3])
    
    # 회차 내 반복 문구 (8~25자 짧은 구절)
    from collections import Counter
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    # 따옴표 정리한 짧은 구절 카운트
    short_phrases = Counter()
    for line in paragraphs:
        clean = line.strip().strip('"').strip("'").strip('\u201c').strip('\u201d').strip('\u2018').strip('\u2019').strip()
        if 8 <= len(clean) <= 25:
            short_phrases[clean] += 1
    
    # 이번 회차에서 3회 이상 반복된 구절 (캐릭터 시그니처 대사는 어쩔 수 없음)
    heavy_repeats_in_ep = [(p, c) for p, c in short_phrases.items() if c >= 3]
    
    # ─ 점수 산출 ─
    score = 100
    
    # said 뒤붙이기 페널티
    if said_count >= 1:
        # 회차당 said 패턴: 1~3회 = -5, 4~7회 = -15, 8~14회 = -30, 15회+ = -50
        if said_count <= 3:
            score -= 5
        elif said_count <= 7:
            score -= 15
        elif said_count <= 14:
            score -= 30
        else:
            score -= 50
    
    # 회차 내 짧은 구절 반복 페널티
    if heavy_repeats_in_ep:
        # 시그니처 대사 보호 — 가장 많이 반복된 1개는 페널티 50%만
        sorted_reps = sorted(heavy_repeats_in_ep, key=lambda x: -x[1])
        for i, (phrase, count) in enumerate(sorted_reps):
            penalty_per = 5 if i == 0 else 8  # 첫 번째(시그니처 추정) 가벼움
            total_penalty = penalty_per * (count - 2)  # 3회부터 페널티
            score -= min(20, total_penalty)  # 구절당 최대 20점
    
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "detail": {
            "said_pattern_count": said_count,
            "said_examples": said_examples[:5],
            "heavy_repeats_in_ep": [(p, c) for p, c in heavy_repeats_in_ep[:5]],
            "threshold_said": "회차당 4회 이상 페널티 증가",
            "threshold_repeat": "회차 내 같은 구절 3회 이상",
        }
    }


def _score_length_discipline(text: str, platform: str = "카카오페이지") -> dict:
    """[v3.2 신규] 회차 분량 규율 점수.
    
    카카오페이지 표준: 5,000~6,500자 (공백 포함)
    - 5,000~6,500자: 만점 100점
    - 4,500~5,000자: 80~99점 (약간 짧음)
    - 6,500~7,500자: 80~99점 (약간 김)
    - 4,000~4,500자 또는 7,500~8,500자: 60~79점
    - 3,000~4,000자 또는 8,500~9,500자: 30~59점
    - 3,000자 미만 또는 9,500자 초과: 0~29점 (심각)
    
    Returns:
        {"score": 0~100, "detail": {"length": int, "in_range": bool}}
    """
    if not text:
        return {"score": 0, "detail": {"reason": "본문 없음"}}
    
    # 회차 제목 줄 제외
    lines = text.split('\n')
    if lines and lines[0].startswith("EP"):
        body = '\n'.join(lines[1:]).strip()
    else:
        body = text.strip()
    
    # 공백 포함 글자수 (개행 제외)
    length = len(body.replace('\n', ''))
    
    if 5000 <= length <= 6500:
        score = 100
        in_range = True
    elif 4500 <= length < 5000:
        score = 80 + int((length - 4500) / 500 * 19)
        in_range = False
    elif 6500 < length <= 7500:
        score = 99 - int((length - 6500) / 1000 * 19)
        in_range = False
    elif 4000 <= length < 4500:
        score = 60 + int((length - 4000) / 500 * 19)
        in_range = False
    elif 7500 < length <= 8500:
        score = 79 - int((length - 7500) / 1000 * 19)
        in_range = False
    elif 3000 <= length < 4000:
        score = 30 + int((length - 3000) / 1000 * 29)
        in_range = False
    elif 8500 < length <= 9500:
        score = 59 - int((length - 8500) / 1000 * 29)
        in_range = False
    else:
        # 심각한 미달 또는 초과
        if length < 3000:
            score = max(0, int(length / 3000 * 29))
        else:
            score = max(0, 29 - int((length - 9500) / 1000 * 10))
        in_range = False
    
    return {
        "score": score,
        "detail": {
            "length": length,
            "in_range": in_range,
            "target_range": "5,000~6,500자",
            "platform": platform,
        }
    }


# ============================================================================
# [v3.3 신규] ADULT_CONTENT_FIDELITY — 19금 콘텐츠 충실도
# ============================================================================

def _score_adult_content_fidelity(
    text: str,
    rating_mode: str = "",
    target_audience: str = "",
    ep_number: int = 0,
    intimacy_schedule_for_ep: dict = None,
) -> dict:
    """[v3.3 신규] 19금 콘텐츠 충실도 점수.
    
    19금/듀얼 작품에서 회차마다 관능 묘사·신체 접촉·긴장이 충분히 있는가 측정.
    
    측정 카테고리:
    1. 직접 신체 접촉 (키스/포옹/맨살/허벅지 등) — 가장 강한 신호
    2. 관능 감각 (달아오/뜨거워/숨이 가빠/전율 등) — 핵심 신호
    3. 신체 부위 묘사 (입술/목덜미/쇄골/어깨 등) — 보조 신호
    4. 거리·긴장 (가까이/끌어당/맞닿/감싸 안 등) — 약한 신호
    
    점수 산출:
    - 카테고리별 점수를 가중 합산
    - intimacy_schedule_for_ep가 있으면 해당 level에 따라 기대치 조정
      · "tension" 단계: 가벼운 접촉만 있어도 합격
      · "first_scene" 단계: 본격 관능 씬이 있어야 함
      · "power_tension"/"emotional_union": 깊은 관능·감정 묘사 기대
    
    Args:
        text: 회차 본문
        rating_mode: 작품 등급 ("19금만"/"듀얼(19+15)"/"15금만")
        target_audience: 타깃 ("여성향"/"남성향" — 가중치 미세 조정용)
        ep_number: 회차 번호
        intimacy_schedule_for_ep: 이 회차에 배정된 관능 스케줄 (level/description)
    
    Returns:
        {"score": 0~100, "applicable": bool, "detail": {...}}
        applicable=False면 15금 작품 등으로 측정 비대상 (점수 무시)
    """
    # 등급 판단
    is_adult = bool(rating_mode and ("19" in rating_mode or "듀얼" in rating_mode))
    
    if not is_adult:
        # 15금 작품 — 측정 비대상
        return {
            "score": 100,  # 점수는 만점으로 처리하되 applicable=False로 가중치 0 처리
            "applicable": False,
            "detail": {
                "reason": "15금 작품 — ADULT_CONTENT_FIDELITY 비측정",
                "rating_mode": rating_mode,
            }
        }
    
    if not text or len(text) < 100:
        return {
            "score": 30,
            "applicable": True,
            "detail": {"reason": "본문 너무 짧음"}
        }
    
    # ─── 카테고리별 키워드 정의 (v3.3.1 — 한국어 활용형 확장) ─────
    # 1. 직접 신체 접촉 (강한 신호 — 가중치 3.0)
    direct_contact = [
        "키스", "입맞춤", "혀가", "혀를", "맨살", "벗은",
        "허벅지", "허리를 끌", "허리를 감", "포옹", "끌어안", "끌어당",
        "안기", "품에", "몸을 겹", "몸이 겹", "맞닿", "맞붙",
        "옷이 벗", "옷을 벗", "단추", "지퍼", "넥타이를 풀",
        # v3.3.1 추가 — 손목 잡기, 손가락 접촉
        "손목을 잡", "손목이 잡", "손목 안쪽에 그의", "손목에 그의 체온",
        "손가락 끝이 닿", "손가락 끝이 카운터 위에서", "손이 시호의 손",
    ]
    
    # 2. 관능 감각 (핵심 신호 — 가중치 2.5)
    arousal_sensations = [
        "달아오", "뜨거워", "뜨거운 숨", "숨이 가빠", "숨이 막",
        "전율", "떨림이 번", "달뜬", "흥분", "전기처럼",
        "온몸이 떨", "온몸이 뜨", "몸이 떨", "몸이 녹",
        "심장이 빠르게", "심장이 미친듯", "심장이 터질",
        "녹아내", "녹아들", "스며들", "젖어", "갈증",
        "신음", "낮은 소리", "낮은 신음", "옅은 소리",
        # v3.3.1 추가 — 활용형
        "뜨거웠다", "뜨거운", "뜨끔", "심장이 한 번", "심장이 크게 떨어",
        "떨림이", "떨렸다", "호흡이 한 박자", "호흡이 멈췄다", "호흡이 얕",
        "한 박자 멈췄다", "분석 회로가 멈췄", "분석 회로가 안 켜",
        "47년 인생에 한 번도", "47년 모태솔로",
    ]
    
    # 3. 신체 부위 묘사 (보조 신호 — 가중치 1.5)
    body_parts_intimate = [
        "입술이", "입술을", "입술에", "입술 끝",
        "쇄골", "목덜미", "목선", "목 아래",
        "어깨에 손", "어깨에 입", "등을 쓸",
        "손가락이 입", "손가락이 목", "손끝이 닿",
        "체온", "체취", "냄새가 가까이",
        "혀끝", "이로 살짝",
        # v3.3.1 추가 — 시호 톤 (손목 + 어깨)
        "손목 안쪽", "어깨가 굳", "어깨에 닿", "그의 어깨가",
        "체온이 닿", "체온이 거기", "향수 냄새가", "향수가 시호",
    ]
    
    # 4. 거리·긴장 (약한 신호 — 가중치 1.0)
    tension_proximity = [
        "가까이 다가", "한 뼘 거리", "코끝이 닿",
        "이마가 닿", "이마를 맞", "숨결이 닿",
        "거리가 좁", "거리가 줄",
        "그의 그림자가 위", "그의 그림자 안",
        "손이 손을 잡", "손을 잡았", "손을 잡혔",
        # v3.3.1 추가
        "한 뼘", "반 뼘", "0.5cm", "1cm", "그림자가 시호", "그림자 밖으로",
        "닿을 듯 말 듯", "닿지 않은 채", "그의 시선이 시호",
        "거리감 제로", "거리감이",
    ]
    
    # ─── 카테고리별 카운트 ─────────────────────────────
    contact_count = sum(text.count(kw) for kw in direct_contact)
    arousal_count = sum(text.count(kw) for kw in arousal_sensations)
    body_count = sum(text.count(kw) for kw in body_parts_intimate)
    tension_count = sum(text.count(kw) for kw in tension_proximity)
    
    # 가중 점수 (raw score)
    raw_score = (
        contact_count * 3.0 +
        arousal_count * 2.5 +
        body_count * 1.5 +
        tension_count * 1.0
    )
    
    # ─── intimacy_schedule 기반 기대치 조정 ─────────
    expected_level = ""
    level_threshold = {
        # 기대 raw_score (이 점수면 만점)
        "tension": 6,           # 가벼운 접촉만 있어도 합격
        "first_scene": 25,      # 본격 첫 관능 씬 — 강한 묘사 필요
        "power_tension": 18,    # 권력·긴장 기반 친밀 — 중강도
        "emotional_union": 22,  # 감정 절정 관능 — 강도 높음
        "deep_intimacy": 30,    # 깊은 관능 — 최강도
    }
    
    if intimacy_schedule_for_ep and isinstance(intimacy_schedule_for_ep, dict):
        expected_level = intimacy_schedule_for_ep.get("level", "")
    
    if expected_level and expected_level in level_threshold:
        target = level_threshold[expected_level]
    else:
        # 기본 기대치 — 19금 작품 일반 회차는 최소한의 친밀 신호
        target = 5
    
    # raw_score를 점수로 변환
    # raw_score=0이면 0점, raw_score>=target이면 90~100점, 그 사이는 선형
    if raw_score >= target * 1.5:
        score = 100
    elif raw_score >= target:
        # target~target*1.5: 90~100
        score = 90 + int((raw_score - target) / (target * 0.5) * 10)
    elif raw_score >= target * 0.6:
        # target*0.6~target: 60~89
        score = 60 + int((raw_score - target * 0.6) / (target * 0.4) * 29)
    elif raw_score >= target * 0.3:
        # target*0.3~target*0.6: 30~59
        score = 30 + int((raw_score - target * 0.3) / (target * 0.3) * 29)
    else:
        # 0~target*0.3: 0~29
        score = max(0, int(raw_score / (target * 0.3) * 29))
    
    # 19금인데 raw_score=0이면 강한 페널티 (회차에 19금 흔적 전혀 없음)
    if raw_score == 0:
        score = 0
    
    return {
        "score": score,
        "applicable": True,
        "detail": {
            "raw_score": round(raw_score, 1),
            "target_raw": target,
            "expected_level": expected_level or "기본 (관능 스케줄 미배정)",
            "direct_contact": contact_count,
            "arousal_sensations": arousal_count,
            "body_parts_intimate": body_count,
            "tension_proximity": tension_count,
            "rating_mode": rating_mode,
        }
    }


def _get_intimacy_schedule_for_ep_helper(intimacy_schedule: list, ep_number: int) -> dict:
    """[v3.3 신규] intimacy_schedule 리스트에서 해당 회차의 항목 찾기 헬퍼.
    
    Args:
        intimacy_schedule: [{"ep_range": "EP5" 또는 "3-5", "level": "...", "description": "..."}, ...]
        ep_number: 회차 번호
    
    Returns:
        매칭되는 dict 또는 빈 dict
    """
    if not intimacy_schedule or not isinstance(intimacy_schedule, list):
        return {}
    
    for item in intimacy_schedule:
        if not isinstance(item, dict):
            continue
        ep_range = item.get("ep_range", "")
        # "EP5" 형식
        if ep_range.startswith("EP"):
            try:
                target_ep = int(ep_range[2:])
                if target_ep == ep_number:
                    return item
            except ValueError:
                continue
        # "3-5" 또는 "3~5" 형식
        parts = ep_range.replace("~", "-").split("-")
        if len(parts) == 2:
            try:
                start, end = int(parts[0].strip()), int(parts[1].strip())
                if start <= ep_number <= end:
                    return item
            except ValueError:
                continue
    return {}


def _extract_plant_keywords(name: str, description: str) -> list:
    """[v3.0+ 정밀화] 떡밥 명사·설명에서 검색용 키워드 풍부 추출.
    
    동의어·부분 매칭 강화 + 한자·영문 포함, 최대 20개.
    """
    import re
    keywords = set()
    
    # 떡밥 이름에서 추출
    if name:
        parts = re.split(r"[\s,\.\(\)\[\]\-/'\"!?]+", name)
        for part in parts:
            part = part.strip()
            if re.match(r'^[가-힣]{2,10}$', part):
                keywords.add(part)
            elif re.match(r'^[A-Za-z]{2,15}$', part):
                keywords.add(part)
            elif re.match(r'^[一-龥]{2,6}$', part):
                keywords.add(part)
            elif 2 <= len(part) <= 10 and not part.endswith(("의", "은", "는", "이", "가", "을", "를")):
                keywords.add(part)
        
        # 조사 제거 후 핵심 명사 추출
        cleaned = re.sub(r"의\s|은\s|는\s|이\s|가\s|을\s|를\s|에서\s|에게\s|에\s", " ", name)
        for w in re.findall(r'[가-힣]{2,8}', cleaned):
            keywords.add(w)
    
    # 설명에서 추출 — 한글 2~6자
    if description:
        words = re.findall(r'[가-힣]{2,6}', description)
        common = {
            "있다", "없다", "되다", "하다", "이다", "그리고", "그러나", "하지만",
            "한다", "된다", "이며", "에서", "그것", "이것", "저것", "위해",
            "통해", "지금", "이런", "저런", "그런", "어떤", "모든", "어느",
            "함께", "다른", "또한", "또는", "그리", "따라", "아니",
        }
        for w in words:
            if w not in common and len(w) >= 2:
                keywords.add(w)
    
    # 영문/한자 핵심어
    if description:
        for w in re.findall(r'[A-Za-z]{2,15}', description):
            keywords.add(w)
        for w in re.findall(r'[一-龥]{2,6}', description):
            keywords.add(w)
    
    return list(keywords)[:20]


def _generate_verdict(grade: str, axes: dict, overall: int) -> str:
    """등급별 한 줄 판정문."""
    weak_axes = [
        ax for ax, data in axes.items()
        if data["score"] < VALIDATION_THRESHOLDS["episode_warn"]
    ]
    
    if grade == "PASS":
        return f"합격 ({overall}/100). 5축 모두 안정적."
    if grade == "WARN":
        if weak_axes:
            return f"경고 ({overall}/100). 약축: {', '.join(weak_axes)}. 보강 권장."
        return f"경고 ({overall}/100). 종합 점수 임계 미달."
    # REDO
    return f"재집필 권장 ({overall}/100). 핵심 축 미달: {', '.join(weak_axes) if weak_axes else '종합'}"


# ============================================================================
# 3. detect_transition_episodes — 단계 전환점 자동 감지
# ============================================================================
def detect_transition_episodes(
    concept: dict, total_eps: int = 42
) -> List[int]:
    """작품 지향에 맞춰 마음 흐름 단계 전환점 회차 자동 추출.
    
    Args:
        concept: 콘셉트 카드 dict (작품 지향 추론용)
        total_eps: 작품 전체 회차 수
    
    Returns:
        전환점 회차 번호 리스트. 예: [3, 6, 19, 31] (4명의 전남편들 42화)
    """
    if not _CHAR_OK or total_eps <= 1:
        return []
    
    orientation = detect_work_orientation(concept) if concept else "female"
    
    transitions = []
    prev_stage = None
    for ep in range(1, total_eps + 1):
        try:
            stage = get_stage_for_episode_with_orientation(ep, total_eps, orientation)
        except Exception:
            continue
        if not stage:
            continue
        cur = stage.get("stage")
        if prev_stage is not None and cur != prev_stage:
            transitions.append(ep)
        prev_stage = cur
    
    return transitions


# ============================================================================
# 4. get_validation_mode_for_episode — 회차별 검수 자동 트리거 결정
# ============================================================================
def get_validation_mode_for_episode(
    ep_number: int,
    mode: str,
    concept: dict,
    total_eps: int = 42,
) -> dict:
    """현재 회차에서 자가 검수를 자동 실행할지 결정.
    
    Args:
        ep_number: 현재 회차
        mode: VALIDATION_MODES 키 (auto_until_25 / transition_only / all_auto / all_manual)
        concept: 콘셉트 카드
        total_eps: 작품 전체 회차 수
    
    Returns:
        {
            "should_run_auto": bool,
            "reason": str,
            "is_transition": bool,
        }
    """
    is_transition = ep_number in detect_transition_episodes(concept, total_eps)
    
    if mode == "all_manual":
        return {
            "should_run_auto": False,
            "reason": "수동 모드 — 작가가 검수 버튼 누를 때만 실행",
            "is_transition": is_transition,
        }
    if mode == "all_auto":
        return {
            "should_run_auto": True,
            "reason": "전체 자동 모드",
            "is_transition": is_transition,
        }
    if mode == "auto_until_25":
        if ep_number <= 25:
            return {
                "should_run_auto": True,
                "reason": "1~25화 자동 검수 구간",
                "is_transition": is_transition,
            }
        # 26화 이후 — 전환점만 자동
        if is_transition:
            return {
                "should_run_auto": True,
                "reason": "26화+ 구간이지만 전환점 회차이므로 자동 검수",
                "is_transition": True,
            }
        return {
            "should_run_auto": False,
            "reason": "26화+ 구간 — 작가 결정 대기",
            "is_transition": False,
        }
    if mode == "transition_only":
        if is_transition:
            return {
                "should_run_auto": True,
                "reason": "전환점 회차 자동 검수",
                "is_transition": True,
            }
        return {
            "should_run_auto": False,
            "reason": "전환점 아님 — 수동 검수만 가능",
            "is_transition": False,
        }
    
    # 미정의 모드는 안전하게 수동
    return {
        "should_run_auto": False,
        "reason": f"알 수 없는 모드 {mode} — 수동으로 폴백",
        "is_transition": is_transition,
    }


# ============================================================================
# 5. generate_material_usage_report — 작가용 가시화 리포트
# ============================================================================
def generate_material_usage_report(
    validation_result: dict,
    ep_number: int = 0,
) -> str:
    """검증 결과 dict를 작가용 가시화 리포트 문자열로 변환.
    
    Args:
        validation_result: compute_episode_validation_score() 결과 dict
        ep_number: 회차 번호
    
    Returns:
        화면에 표시할 마크다운 문자열.
    """
    if not validation_result:
        return "(검증 결과 없음)"
    
    overall = validation_result.get("overall", 0)
    grade = validation_result.get("grade", "?")
    verdict = validation_result.get("verdict", "")
    axes = validation_result.get("axes", {})
    
    grade_emoji = {"PASS": "🟢", "WARN": "🟡", "REDO": "🔴"}.get(grade, "⚫")
    
    lines = [
        f"### {grade_emoji} EP{ep_number} 자가 검수 — 종합 {overall}/100 [{grade}]",
        "",
        f"_{verdict}_",
        "",
        "**6축 점수** (v3.0+ PLANT_USAGE 추가)",
    ]
    
    axis_labels = {
        "MATERIAL_USAGE":         "재료 활용",
        "CHARACTER_CONSISTENCY":  "캐릭터 차별화",
        "CLIFFHANGER_STRENGTH":   "클리프행어",
        "MISE_EN_SCENE":          "묘사·장면",
        "MARKET_VIABILITY":       "시장 트리거",
        "PLANT_USAGE":            "떡밥 활용",  # ★ 신규
    }
    
    for ax_key, ax_data in axes.items():
        label = axis_labels.get(ax_key, ax_key)
        score = ax_data.get("score", 0)
        critical = ax_data.get("critical", False)
        critical_mark = " ★" if critical else ""
        score_emoji = "🟢" if score >= 75 else "🟡" if score >= 65 else "🔴"
        lines.append(f"- {score_emoji} **{label}**{critical_mark}: {score}/100")
    
    # MATERIAL_USAGE 상세
    mu_detail = axes.get("MATERIAL_USAGE", {}).get("detail", {})
    if mu_detail:
        lines.extend([
            "",
            "**재료 활용 상세**",
            f"- 사용된 재료: {mu_detail.get('used_count', 0)}개",
            f"- 약하게 반영: {mu_detail.get('weak_count', 0)}개",
            f"- 누락: {mu_detail.get('missing_count', 0)}개",
        ])
        critical_missing = mu_detail.get("critical_missing", [])
        if critical_missing:
            lines.append("- ❌ **핵심 누락**:")
            for cm in critical_missing:
                lines.append(f"  - {cm}")
    
    # ★ PLANT_USAGE 상세 (신규)
    plant_detail = axes.get("PLANT_USAGE", {}).get("detail", {})
    if plant_detail and not plant_detail.get("reason"):  # 떡밥 맵이 있는 경우만
        plants_to_payoff = plant_detail.get("plants_to_payoff", [])
        plants_to_plant = plant_detail.get("plants_to_plant", [])
        plants_to_hint = plant_detail.get("plants_to_hint", [])
        planted_ok = plant_detail.get("planted_ok", [])
        missed = plant_detail.get("missed", [])
        critical_missed = plant_detail.get("critical_missed", [])
        
        if plants_to_payoff or plants_to_plant or plants_to_hint:
            lines.extend([
                "",
                "**떡밥 활용 상세**",
            ])
            if plants_to_plant:
                lines.append(f"- [심기] 대상 {len(plants_to_plant)}개: {', '.join(plants_to_plant[:3])}")
            if plants_to_hint:
                lines.append(f"- [힌트] 대상 {len(plants_to_hint)}개: {', '.join(plants_to_hint[:3])}")
            if plants_to_payoff:
                lines.append(f"- [회수] 대상 {len(plants_to_payoff)}개: {', '.join(plants_to_payoff[:3])}")
            if planted_ok:
                lines.append(f"- ✅ 잘 반영: {len(planted_ok)}개")
            if critical_missed:
                lines.append("- ❌ **★ 회수 누락 (재집필 필수)**:")
                for cm in critical_missed:
                    lines.append(f"  - {cm}")
            elif missed:
                lines.append("- ⚠️ 약하게 반영:")
                for m in missed[:3]:
                    lines.append(f"  - {m}")
    
    return "\n".join(lines)


# ============================================================================
# 6. summarize_cumulative_25 — 25화 모니터링 누적 대시보드 데이터
# ============================================================================
def summarize_cumulative_25(
    validation_history: List[dict],
    cliffhanger_counts: Optional[Dict[str, int]] = None,
    total_eps: int = 42,
) -> dict:
    """1~25화 누적 검증 결과를 작가 모니터링용으로 요약.
    
    Args:
        validation_history: 회차별 compute_episode_validation_score() 결과의 list
                            [{"ep": 1, "result": {...}}, ...]
        cliffhanger_counts: 클리프행어 유형별 누적 카운트
        total_eps: 작품 전체 회차 수 (벤치마크 비교용)
    
    Returns:
        대시보드 표시용 dict.
    """
    if not validation_history:
        return {
            "n_episodes": 0,
            "avg_overall": 0,
            "axis_avgs": {},
            "weakest_episodes": [],
            "strongest_episodes": [],
            "frequent_missing": [],
            "cliffhanger_balance": {},
            "recommendation": "검수된 회차가 없습니다.",
        }
    
    n = len(validation_history)
    
    # 종합 평균
    overalls = [h.get("result", {}).get("overall", 0) for h in validation_history]
    avg_overall = sum(overalls) / n if n > 0 else 0
    
    # 6축별 평균 (v3.0+ PLANT_USAGE 추가)
    axis_keys = [
        "MATERIAL_USAGE", "CHARACTER_CONSISTENCY", "CLIFFHANGER_STRENGTH",
        "MISE_EN_SCENE", "MARKET_VIABILITY", "PLANT_USAGE",
    ]
    axis_avgs = {}
    for ax in axis_keys:
        scores = [
            h.get("result", {}).get("axes", {}).get(ax, {}).get("score", 0)
            for h in validation_history
        ]
        axis_avgs[ax] = round(sum(scores) / n, 1) if n > 0 else 0
    
    # 위험 회차 Top 3 (점수 낮은 순)
    sorted_eps = sorted(
        validation_history,
        key=lambda h: h.get("result", {}).get("overall", 0)
    )
    weakest = [
        {
            "ep": h.get("ep"),
            "overall": h.get("result", {}).get("overall", 0),
            "grade": h.get("result", {}).get("grade", ""),
        }
        for h in sorted_eps[:3]
    ]
    strongest = [
        {
            "ep": h.get("ep"),
            "overall": h.get("result", {}).get("overall", 0),
            "grade": h.get("result", {}).get("grade", ""),
        }
        for h in sorted_eps[-3:][::-1]
    ]
    
    # 누락 패턴 — 가장 자주 누락된 재료
    missing_patterns = {}
    for h in validation_history:
        critical = (
            h.get("result", {}).get("axes", {})
             .get("MATERIAL_USAGE", {}).get("detail", {})
             .get("critical_missing", [])
        )
        for cm in critical:
            # 첫 번째 단어로 그룹화 (모티프명 등 핵심)
            key = cm.split(" ")[0] if cm else ""
            if key:
                missing_patterns[key] = missing_patterns.get(key, 0) + 1
    
    frequent_missing = sorted(
        missing_patterns.items(), key=lambda x: x[1], reverse=True
    )[:5]
    
    # 클리프행어 분포
    cliff_balance = {}
    if cliffhanger_counts and _MARKET_OK:
        try:
            cliff_balance = validate_cliffhanger_distribution(
                cliffhanger_counts, total_eps
            )
        except Exception:
            cliff_balance = {}
    
    # 권장 모드 결정
    recommendation = _recommend_next_mode(avg_overall, axis_avgs, weakest)
    
    return {
        "n_episodes": n,
        "avg_overall": round(avg_overall, 1),
        "axis_avgs": axis_avgs,
        "weakest_episodes": weakest,
        "strongest_episodes": strongest,
        "frequent_missing": [{"key": k, "count": c} for k, c in frequent_missing],
        "cliffhanger_balance": cliff_balance,
        "recommendation": recommendation,
    }


def _recommend_next_mode(avg_overall: float, axis_avgs: dict, weakest: list) -> str:
    """누적 결과 기반으로 26화 이후 검수 모드 추천."""
    pass_threshold = VALIDATION_THRESHOLDS["cumulative_pass"]
    
    if avg_overall >= pass_threshold:
        # 약축이 있는지 점검
        weak_axis = None
        for ax, score in axis_avgs.items():
            if score < 70:
                weak_axis = ax
                break
        
        if weak_axis:
            return (
                f"📊 누적 평균 {avg_overall:.1f}/100 — 합격선 통과. "
                f"단, '{weak_axis}' 축이 약함({axis_avgs[weak_axis]:.1f}). "
                f"**전환점 회차만 자동 검수** 권장 (안전망 유지)."
            )
        return (
            f"📊 누적 평균 {avg_overall:.1f}/100 — 우수. "
            f"**26화 이후 수동 모드** 가능. 전환점 회차만 자동도 안전."
        )
    elif avg_overall >= 70:
        return (
            f"⚠️ 누적 평균 {avg_overall:.1f}/100 — 보강 필요. "
            f"**26화 이후도 자동 검수** 권장. 위험 회차 재집필 검토."
        )
    else:
        return (
            f"🔴 누적 평균 {avg_overall:.1f}/100 — 콘셉트·캐릭터 재점검 필요. "
            f"**26화 이후 자동 검수 + 위험 회차 재집필 강제** 권장."
        )


# ============================================================================
# 자기 검증
# ============================================================================
def _self_test():
    """모듈 자가 검증."""
    # 1) 4명의 전남편들 콘셉트로 전환점 감지
    concept_4h = {
        "title": "4명의 전남편들",
        "genre": "현대로맨스",
        "heroine_name": "한시호",
    }
    transitions_4h = detect_transition_episodes(concept_4h, 42)
    assert transitions_4h == [3, 6, 19, 31], f"4명전남편 전환점 불일치: {transitions_4h}"
    
    # 2) 만물탐정 (남성향 8화) 전환점
    manmul = {
        "title": "만물탐정",
        "genre": "심리 스릴러",
        "target_persona": "25~45세 남성 OTT 헤비유저",
    }
    transitions_m = detect_transition_episodes(manmul, 8)
    assert len(transitions_m) >= 2, f"만물탐정 전환점 부족: {transitions_m}"
    
    # 3) 검수 모드 결정 — 25화 자동
    mode_decision = get_validation_mode_for_episode(15, "auto_until_25", concept_4h, 42)
    assert mode_decision["should_run_auto"] is True
    
    mode_decision_30 = get_validation_mode_for_episode(30, "auto_until_25", concept_4h, 42)
    # 30화는 24~26화 구간 밖이고 전환점도 아님 (전환점은 31)
    assert mode_decision_30["should_run_auto"] is False
    
    # 31화는 전환점 → 자동
    mode_decision_31 = get_validation_mode_for_episode(31, "auto_until_25", concept_4h, 42)
    assert mode_decision_31["should_run_auto"] is True
    
    # ★ [v3.2] 신규 4축 검증
    # 대사 비율: 대사 풍부한 본문은 90+, 지문만은 0~30
    high_dlg = ('일반 도입부 문장입니다. 그가 다가왔다.\n'
                '"안녕하세요. 처음 뵙겠습니다. 정말 만나서 반갑습니다."\n'
                '시호는 천천히 고개를 들었다.\n'
                '"네, 안녕하세요. 처음 뵙겠습니다."\n'
                '"여기서 일하시는 분이세요? 어제는 못 봤는데요."\n'
                '짧은 침묵이 흘렀다.\n'
                '"네, 오늘부터 시작입니다. 어떻게 알고 오셨나요?"\n'
                '"이 카페에 자주 오는 친구가 있어서요."\n')
    r = _score_dialogue_ratio(high_dlg)
    assert r["score"] >= 60, f"대사 풍부 본문 점수 미달: {r['score']}"
    
    low_dlg = ('지문만 가득한 본문입니다. ' * 50)
    r = _score_dialogue_ratio(low_dlg)
    assert r["score"] <= 30, f"지문만 본문 점수 과다: {r['score']}"
    
    # said 뒤붙이기 다수 → 페널티
    said_heavy = ('시호가 말했다. 어쩌고.\n' * 15) + "일반 본문 " * 100
    r = _score_prose_hygiene(said_heavy)
    assert r["score"] < 60, f"said 다수 페널티 미작동: {r['score']}"
    
    # 분량 표준
    normal = ("표준 분량 회차입니다. " * 500)
    r = _score_length_discipline(normal)
    assert r["score"] == 100, f"표준 분량 점수 이상: {r['score']}"
    
    # 분량 미달
    short = "짧은 회차." * 50
    r = _score_length_discipline(short)
    assert r["score"] < 30, f"미달 분량 페널티 미작동: {r['score']}"
    
    # 호명 과다 → 페널티
    char_bible_test = {"한시호": {"name": "한시호"}}
    over_naming = "시호는 일했다. " * 60  # 시호 60회 등장
    r = _score_naming_discipline(over_naming, char_bible_test)
    assert r["score"] < 80, f"호명 과다 페널티 미작동: {r['score']}"
    
    # 10축 종합 — 정상 데이터로 PASS 나오는지
    test_text = """EP1. 테스트
첫 단락 본문입니다. 그가 다가왔다.
"안녕하세요."
시호는 천천히 고개를 들었다.
"네, 처음 뵙겠습니다."
""" + ('일반 본문 한 단락. ' * 200) + ('\n"대사 한 줄." ' * 50)
    result = compute_episode_validation_score(
        {"title": "테스트", "genre": "현대로맨스"},
        char_bible_test,
        test_text,
        ep_number=1, total_eps=50,
    )
    assert "DIALOGUE_RATIO" in result["axes"], "DIALOGUE_RATIO 축 누락"
    assert "NAMING_DISCIPLINE" in result["axes"], "NAMING_DISCIPLINE 축 누락"
    assert "PROSE_HYGIENE" in result["axes"], "PROSE_HYGIENE 축 누락"
    assert "LENGTH_DISCIPLINE" in result["axes"], "LENGTH_DISCIPLINE 축 누락"
    # v3.3 신규
    assert "ADULT_CONTENT_FIDELITY" in result["axes"], "ADULT_CONTENT_FIDELITY 축 누락"
    assert len(result["axes"]) == 11, f"축 개수 불일치: {len(result['axes'])}"
    
    # ★ [v3.3] ADULT_CONTENT_FIDELITY 동작 검증
    # 15금 작품 — applicable=False
    r = _score_adult_content_fidelity(
        text="일반 본문." * 100, rating_mode="15금만",
    )
    assert r["applicable"] is False, "15금 작품에서 applicable=True가 되면 안 됨"
    
    # 19금 작품 — 관능 키워드 0개 → 0점
    r = _score_adult_content_fidelity(
        text="일반 본문. 시호는 카페에서 일했다." * 100, rating_mode="19금만",
    )
    assert r["applicable"] is True, "19금 작품에서 applicable=True여야 함"
    assert r["score"] == 0, f"관능 키워드 0개일 때 0점 아님: {r['score']}"
    
    # 19금 작품 — 충분한 관능 묘사 → 높은 점수
    intimacy_text = """그가 시호의 허리를 끌어당겼다. 시호의 입술이 떨렸다.
숨이 가빠졌다. 키스에 가까운 거리. 맞닿은 가슴. 심장이 빠르게 뛰었다.
달아오른 체온. 뜨거운 숨결.""" * 3
    r = _score_adult_content_fidelity(
        text=intimacy_text, rating_mode="19금만",
        intimacy_schedule_for_ep={"level": "first_scene"},
    )
    assert r["score"] >= 70, f"충분한 관능 묘사에서 점수 미달: {r['score']}"
    
    # 등급별 동적 가중치 — 19금 작품 weights 확인
    result_19 = compute_episode_validation_score(
        {"title": "테스트", "genre": "현대로맨스", "serial_config": {"rating_mode": "19금만"}},
        char_bible_test,
        test_text,
        ep_number=1, total_eps=50,
    )
    assert result_19["weights_used"]["ADULT_CONTENT_FIDELITY"] == 0.40, \
        f"19금 ACF 가중치 0.40 아님: {result_19['weights_used']['ADULT_CONTENT_FIDELITY']}"
    
    # 15금 작품 weights 확인
    result_15 = compute_episode_validation_score(
        {"title": "테스트", "genre": "현대로맨스", "serial_config": {"rating_mode": "15금만"}},
        char_bible_test,
        test_text,
        ep_number=1, total_eps=50,
    )
    assert result_15["weights_used"]["ADULT_CONTENT_FIDELITY"] == 0.00, \
        f"15금 ACF 가중치 0 아님: {result_15['weights_used']['ADULT_CONTENT_FIDELITY']}"
    
    return True


_self_test()


if __name__ == "__main__":
    print("=" * 60)
    print("engine_validator.py — Phase C 자가 검수 모듈 자가 검증")
    print("=" * 60)
    
    concept_4h = {
        "title": "4명의 전남편들",
        "genre": "현대로맨스",
        "formula_main": "운명적_인연물",
        "heroine_name": "한시호",
    }
    
    print("\n[4명의 전남편들 — 전환점 회차 자동 감지]")
    transitions = detect_transition_episodes(concept_4h, 42)
    print(f"  전환점: {transitions}")
    
    print("\n[검수 모드 — auto_until_25 시뮬레이션]")
    test_eps = [1, 15, 25, 26, 30, 31, 35, 42]
    for ep in test_eps:
        d = get_validation_mode_for_episode(ep, "auto_until_25", concept_4h, 42)
        mark = "🤖 자동" if d["should_run_auto"] else "👤 수동"
        trans = " (전환점)" if d["is_transition"] else ""
        print(f"  EP{ep:>2}: {mark}{trans} — {d['reason']}")
    
    print("\n[만물탐정 8화 — 전환점 + 모드 결정]")
    manmul = {
        "title": "만물탐정",
        "genre": "심리 스릴러",
        "target_persona": "25~45세 남성 OTT 헤비유저",
    }
    transitions_m = detect_transition_episodes(manmul, 8)
    print(f"  전환점: {transitions_m}")
    for ep in range(1, 9):
        d = get_validation_mode_for_episode(ep, "auto_until_25", manmul, 8)
        mark = "🤖" if d["should_run_auto"] else "👤"
        trans = "★" if d["is_transition"] else " "
        print(f"  EP{ep}: {mark} {trans} {d['reason']}")
    
    print("\n✓ 모든 자가 검증 통과")
