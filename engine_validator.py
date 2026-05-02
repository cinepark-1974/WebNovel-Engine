"""
engine_validator.py — Engine v3.0 Phase C
==========================================
회차 자가 검수·재료 활용 검증·전환점 자동 감지

핵심 함수:
- validate_planning_to_writing_mapping() — 기획 재료가 본문에 반영됐는가
- compute_episode_validation_score()    — 5축 종합 점수
- detect_transition_episodes()          — 마음 흐름 단계 전환점 자동 감지
- generate_material_usage_report()      — 작가용 가시화 리포트
- get_validation_mode_for_episode()     — 회차별 검수 모드 결정
- summarize_cumulative_25()             — 25화 모니터링 누적 대시보드 데이터

5축 검수:
1. MATERIAL_USAGE        — 기획 재료가 본문에 활용됐는가 (★ critical)
2. CHARACTER_CONSISTENCY — 9종 인물 역할로 차별화됐는가 (★ critical)
3. CLIFFHANGER_STRENGTH  — 클리프행어 분포가 시장 표준 안인가
4. MISE_EN_SCENE         — 묘사·장면 강도 적정한가
5. MARKET_VIABILITY      — 시장 트리거 5종 충족도

원칙:
- 본 모듈은 LLM 호출 없이 텍스트 패턴 매칭으로 1차 검수 (빠름·무비용)
- 깊은 검수가 필요하면 prompt.py의 build_validation_prompt()로 LLM 호출
- 회차별 단독 점수 + 누적 단위 점수 분리 제공
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
# 2. compute_episode_validation_score — 5축 종합 점수
# ============================================================================
def compute_episode_validation_score(
    concept: dict,
    character_bible,
    written_text: str,
    ep_number: int = 0,
    total_eps: int = 42,
    cliffhanger_type: Optional[str] = None,
    plant_map: Optional[dict] = None,  # ★ v3.0+ — 떡밥 활용도 검수용
) -> dict:
    """회차 단독 6축 종합 점수.
    
    Returns:
        {
            "axes": {
                "MATERIAL_USAGE":       {score, critical, detail},
                "CHARACTER_CONSISTENCY":{...},
                "CLIFFHANGER_STRENGTH": {...},
                "MISE_EN_SCENE":        {...},
                "MARKET_VIABILITY":     {...},
                "PLANT_USAGE":          {...},  # ★ 신규 — 떡밥 활용도
            },
            "overall": 0~100,
            "grade": "PASS|WARN|REDO",
            "verdict": "이 회차는 ...",
        }
    """
    axes = {}
    
    # 1) MATERIAL_USAGE
    mu = validate_planning_to_writing_mapping(
        concept, character_bible, written_text, ep_number, total_eps
    )
    axes["MATERIAL_USAGE"] = {
        "score": mu["score"],
        "critical": True,  # 누락 시 재집필 트리거
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
    
    # 6) ★ PLANT_USAGE — 떡밥 활용도 (v3.0+ 신규)
    plant_score = _score_plant_usage(plant_map, written_text, ep_number)
    axes["PLANT_USAGE"] = {
        "score": plant_score["score"],
        "critical": plant_score.get("critical", False),  # 회수 누락 시 critical
        "detail": plant_score["detail"],
    }
    
    # 종합 점수 (가중 평균) — 6축으로 재조정
    weights = {
        "MATERIAL_USAGE":         0.25,  # 0.30 → 0.25
        "CHARACTER_CONSISTENCY":  0.20,  # 0.25 → 0.20
        "CLIFFHANGER_STRENGTH":   0.15,  # 유지
        "MISE_EN_SCENE":          0.10,  # 유지
        "MARKET_VIABILITY":       0.15,  # 0.20 → 0.15
        "PLANT_USAGE":            0.15,  # 신규
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
