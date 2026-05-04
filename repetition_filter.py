"""
repetition_filter.py — 회차 본문 반복·중복 자동 탐지·정리 모듈
================================================================

목적:
- LLM이 분량 강제로 인해 무의미한 반복으로 채우는 패턴 잡기
- 단, 의도된 반복(강조·수미상관·대사 반복)은 보존

설계 원칙:
- 안전한 케이스만 자동 정리 (완전 동일 문장 3회+ 등)
- 의심스러운 경우는 검토 리포트로 작가에게 표시
- 작가가 판단하도록 함 (작가의 글쓰기 자유 보장)

핵심 함수:
- detect_repetitions(text)         — 반복 탐지 (자동 정리 대상 + 검토 대상)
- auto_clean_safe_repetitions(text) — 안전한 반복만 자동 정리
- generate_repetition_report(detection) — 작가용 검토 리포트
"""

import re
from collections import Counter
from typing import Dict, List, Tuple


# ══════════════════════════════════════════════
# 의도된 반복 보존 규칙
# ══════════════════════════════════════════════

# 짧은 문장은 강조용일 수 있음 (보존)
PROTECT_SHORT_THRESHOLD = 12  # 12자 이하는 강조 가능성

# 대사 반복은 의도된 경우 많음 (보존)
DIALOGUE_MARKERS = ("'", '"', '"', '"', "'", '「', '『', '<<')

# 짧은 정서적 반복은 의도일 수 있음 — 안전 보호 키워드
INTENT_REPETITION_PATTERNS = [
    "아니", "안돼", "잠깐", "맞아", "응", "네",
    "그래", "정말", "진짜", "어머", "세상에",
]


def _is_dialogue(line: str) -> bool:
    """대사 줄인지 판별."""
    return bool(line) and line.lstrip().startswith(DIALOGUE_MARKERS)


def _is_intentional_short(text: str) -> bool:
    """의도된 짧은 문장(강조)인지 판별.
    
    12자 이하 + 정서·강조 키워드 포함 → 의도된 반복 가능성.
    """
    if len(text.strip()) > PROTECT_SHORT_THRESHOLD:
        return False
    for pattern in INTENT_REPETITION_PATTERNS:
        if pattern in text:
            return True
    return False


# ══════════════════════════════════════════════
# 반복 탐지
# ══════════════════════════════════════════════

def detect_repetitions(text: str) -> dict:
    """본문에서 반복·중복 패턴 자동 탐지.
    
    Returns:
        {
            "total_chars": int,
            "auto_clean_targets": [...],  # 안전하게 자동 삭제 가능
            "review_targets": [...],      # 작가 검토 필요
            "stats": {...},               # 통계
        }
    """
    if not text or len(text) < 50:
        return {
            "total_chars": len(text or ""),
            "auto_clean_targets": [],
            "review_targets": [],
            "stats": {},
        }
    
    auto_targets = []
    review_targets = []
    
    # ─── 1) 완전 동일 줄 반복 (한 줄 단위) ─────────────
    # LLM 반복은 한 줄 단위로 자주 발생 (문장 단위보다 줄 단위가 정확)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    line_counter = Counter(lines)
    
    for line, count in line_counter.items():
        if count < 2:
            continue
        if _is_dialogue(line):
            # 대사 반복은 검토만
            if count >= 3:
                review_targets.append({
                    "type": "동일 대사 반복",
                    "content": line,
                    "count": count,
                    "reason": "대사 반복은 의도된 경우 많음 — 작가 검토",
                })
            continue
        if _is_intentional_short(line):
            # 짧은 강조 문장은 검토만
            review_targets.append({
                "type": "짧은 줄 반복 (강조 가능성)",
                "content": line,
                "count": count,
                "reason": "의도된 강조일 수 있음 — 작가 검토",
            })
            continue
        
        # 충분히 긴 줄 (15자+) 3회+ 반복은 안전하게 자동 정리
        if count >= 3 and len(line) >= 15:
            auto_targets.append({
                "type": "동일 줄 3회+ 반복",
                "content": line,
                "count": count,
                "action": "두 번째부터 삭제 (한 번만 보존)",
            })
        elif count == 2 and len(line) >= 30:
            # 긴 줄 2회 반복은 검토 (수미상관 가능)
            review_targets.append({
                "type": "긴 줄 2회 반복",
                "content": line,
                "count": count,
                "reason": "수미상관·재강조 가능 — 작가 검토",
            })
        elif count >= 2 and len(line) >= 15:
            # 중간 길이(15~30자) 2회+ 반복 검토
            review_targets.append({
                "type": "줄 반복",
                "content": line,
                "count": count,
                "reason": "의도 가능성 검토",
            })
    
    # ─── 2) 연속 동일 짧은 표현 ─────────────
    consecutive = _detect_consecutive_repetition(text)
    for item in consecutive:
        if item["safe_to_remove"]:
            auto_targets.append(item)
        else:
            review_targets.append(item)
    
    # ─── 3) 인접 문단 유사도 ─────────────────
    similar_paragraphs = _detect_similar_paragraphs(text)
    for item in similar_paragraphs:
        review_targets.append(item)
    
    # ─── 4) 단어 과다 사용 ─────────────────────
    word_overuse = _detect_word_overuse(text)
    
    # ─── 통계 ──────────────────────────
    auto_chars_to_remove = sum(
        len(item["content"]) * (item["count"] - 1) 
        for item in auto_targets if "count" in item
    )
    
    stats = {
        "total_chars": len(text),
        "total_lines": len(lines),
        "auto_targets_count": len(auto_targets),
        "review_targets_count": len(review_targets),
        "estimated_chars_to_remove": auto_chars_to_remove,
        "word_overuse": word_overuse,
    }
    
    return {
        "total_chars": len(text),
        "auto_clean_targets": auto_targets,
        "review_targets": review_targets,
        "stats": stats,
    }


def _split_sentences(text: str) -> list:
    """문장 단위 분리 (한국어 종결 부호 + 줄바꿈 고려).
    
    한국어 문장은 종종 줄바꿈으로 구분되므로, 줄도 함께 고려.
    """
    # 1) 줄별로 먼저 분리
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # 2) 각 줄 안에서 문장 종결 부호로 추가 분리
    sentences = []
    for line in lines:
        # 종결 부호 + 공백/끝
        parts = re.split(r'(?<=[.!?…])\s+', line)
        for p in parts:
            p = p.strip()
            if 5 <= len(p) <= 300:
                sentences.append(p)
    
    return sentences


def _detect_consecutive_repetition(text: str) -> list:
    """연속된 동일 표현 탐지.
    
    예: "그녀는 웃었다. 그녀는 웃었다." → 자동 정리 대상
    """
    results = []
    paragraphs = [p for p in text.split('\n') if p.strip()]
    
    for i in range(len(paragraphs) - 1):
        p1 = paragraphs[i].strip()
        p2 = paragraphs[i + 1].strip()
        
        # 완전 동일
        if p1 == p2 and len(p1) >= 5:
            if _is_intentional_short(p1) or _is_dialogue(p1):
                # 의도된 반복일 수 있음
                results.append({
                    "type": "연속 동일 문단 (의도 가능)",
                    "content": p1,
                    "position": i,
                    "safe_to_remove": False,
                    "reason": "의도된 강조·대사 반복 가능 — 작가 검토",
                })
            else:
                # 안전하게 정리
                results.append({
                    "type": "연속 동일 문단",
                    "content": p1,
                    "position": i,
                    "safe_to_remove": True,
                    "action": "두 번째 삭제",
                })
    
    return results


def _detect_similar_paragraphs(text: str, threshold: float = 0.5) -> list:
    """인접 문단 유사도 탐지 (3-gram 자카드)."""
    results = []
    paragraphs = [p for p in text.split('\n') if p.strip() and len(p) >= 30]
    
    for i in range(len(paragraphs) - 1):
        p1 = paragraphs[i]
        p2 = paragraphs[i + 1]
        
        set1 = set(p1[j:j+3] for j in range(len(p1) - 2))
        set2 = set(p2[j:j+3] for j in range(len(p2) - 2))
        
        if not set1 or not set2:
            continue
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        similarity = intersection / union if union else 0
        
        if similarity >= threshold:
            results.append({
                "type": "인접 문단 유사도 높음",
                "content_a": p1[:100],
                "content_b": p2[:100],
                "position": i,
                "similarity": round(similarity, 2),
                "reason": f"인접 두 문단이 {similarity:.0%} 유사 — 작가 검토 권장",
            })
    
    return results


def _detect_word_overuse(text: str) -> list:
    """[v3.0+ 보강] 과다 사용 단어 탐지 (통계 + 정체성 키워드 전용 검사)."""
    if not text:
        return []
    
    words = re.findall(r'[가-힣]{3,}', text)
    if not words:
        return []
    
    word_counter = Counter(words)
    total = len(words)
    
    common = {
        "있었다", "없었다", "되었다", "이었다", "것이다", "그것이",
        "그리고", "그러나", "하지만", "그래서", "따라서", "그러면",
        "그것은", "이것은", "저것은",
    }
    
    overused = []
    for word, count in word_counter.most_common(20):
        if word in common:
            continue
        ratio = count / total
        if ratio > 0.008:  # 0.8% 이상
            overused.append({
                "word": word,
                "count": count,
                "ratio_percent": round(ratio * 100, 2),
                "type": "일반 단어",
            })
    
    # ★ v3.0+ 정체성 키워드 전용 검사 (숫자+나이 조합)
    # 한국 웹소설 LLM이 자주 빠지는 함정:
    # 주인공 정체성을 매 단락마다 강조하는 강박
    # 주의: 한국어는 \b 워드 경계가 안 먹히므로 사용 X
    identity_patterns = [
        # 나이 표현 (다양한 형태)
        (r'\d{1,3}세', "나이(N세)"),
        (r'\d{1,3}년', "기간(N년)"),
        (r'\d{1,3}살', "나이(N살)"),
        # 한자어 나이
        (r'마흔[일이삼사오육칠팔구]?', "한자나이(마흔X)"),
        (r'서른[일이삼사오육칠팔구]?', "한자나이(서른X)"),
        (r'쉰[일이삼사오육칠팔구]?', "한자나이(쉰X)"),
        (r'스물[일이삼사오육칠팔구]?', "한자나이(스물X)"),
    ]
    
    for pattern, label in identity_patterns:
        matches = re.findall(pattern, text)
        if not matches:
            continue
        # 같은 매칭들 카운트
        match_counter = Counter(matches)
        for matched_text, count in match_counter.items():
            if count >= 5:  # 회차당 5회 이상이면 과다
                # 본문 분량 대비 비율도 계산
                ratio_per_1000 = (count / len(text)) * 1000
                overused.append({
                    "word": matched_text,
                    "count": count,
                    "ratio_percent": round(ratio_per_1000, 2),  # 1000자당
                    "type": f"★ 정체성 키워드 ({label})",
                    "warning": "캐릭터 정체성 키워드는 회차당 5회 이하 권장 (A15 규칙)",
                })
    
    return overused[:8]  # 5 → 8개로 늘림 (정체성 키워드 추가 위해)


# ══════════════════════════════════════════════
# 자동 정리 (안전한 케이스만)
# ══════════════════════════════════════════════

def auto_clean_safe_repetitions(text: str) -> Tuple[str, dict]:
    """안전한 반복만 자동 삭제.
    
    Returns:
        (cleaned_text, removal_log)
    """
    if not text:
        return text, {"removed_count": 0, "removed_chars": 0, "items": []}
    
    detection = detect_repetitions(text)
    auto_targets = detection["auto_clean_targets"]
    
    if not auto_targets:
        return text, {"removed_count": 0, "removed_chars": 0, "items": []}
    
    cleaned = text
    removal_log = []
    
    for target in auto_targets:
        target_type = target.get("type", "")
        content = target.get("content", "")
        
        if not content or content not in cleaned:
            continue
        
        if "동일 줄 3회+" in target_type or "동일 문장 3회+" in target_type:
            # 첫 번째 occurrence만 남기고 나머지 삭제
            count_in_text = cleaned.count(content)
            if count_in_text >= 3:
                # 첫 occurrence 위치 찾기
                first_idx = cleaned.find(content)
                first_part = cleaned[:first_idx + len(content)]
                rest = cleaned[first_idx + len(content):]
                # rest에서 모든 추가 occurrence 제거
                rest_cleaned = rest.replace(content, "")
                cleaned = first_part + rest_cleaned
                
                removed_count = count_in_text - 1
                removal_log.append({
                    "content": content[:60] + ("..." if len(content) > 60 else ""),
                    "removed_count": removed_count,
                    "removed_chars": len(content) * removed_count,
                })
        
        elif "연속 동일 문단" in target_type:
            # 연속 두 줄이 같으면 두 번째 삭제
            pattern = f"{content}\n{content}"
            if pattern in cleaned:
                cleaned = cleaned.replace(pattern, content, 1)
                removal_log.append({
                    "content": content[:60] + ("..." if len(content) > 60 else ""),
                    "removed_count": 1,
                    "removed_chars": len(content),
                })
    
    total_removed = sum(item.get("removed_count", 0) for item in removal_log)
    total_chars = sum(item.get("removed_chars", 0) for item in removal_log)
    
    return cleaned, {
        "removed_count": total_removed,
        "removed_chars": total_chars,
        "items": removal_log,
    }


# ══════════════════════════════════════════════
# 검토 리포트 생성
# ══════════════════════════════════════════════

def generate_repetition_report(detection: dict) -> str:
    """작가용 검토 리포트 마크다운 생성."""
    auto_targets = detection.get("auto_clean_targets", [])
    review_targets = detection.get("review_targets", [])
    stats = detection.get("stats", {})
    word_overuse_check = stats.get("word_overuse", [])
    has_identity_overuse = any(
        w.get("type", "").startswith("★") for w in word_overuse_check
    )
    
    # 자동/검토 대상 + 정체성 키워드 모두 없을 때만 "깨끗" 메시지
    if not auto_targets and not review_targets and not has_identity_overuse:
        return "✅ 반복·중복 패턴 없음. 본문 깨끗합니다."
    
    lines = []
    
    # 자동 정리 대상
    if auto_targets:
        lines.append(f"### 🟢 자동 정리 가능 ({len(auto_targets)}개)")
        lines.append("아래 항목은 안전하게 자동 삭제 가능합니다:")
        lines.append("")
        for item in auto_targets[:10]:
            content = item.get("content", "")
            preview = content[:60] + ("..." if len(content) > 60 else "")
            lines.append(f"- **{item.get('type', '')}** ({item.get('count', '?')}회)")
            lines.append(f"  - \"`{preview}`\"")
            if item.get("action"):
                lines.append(f"  - 처리: {item['action']}")
        lines.append("")
    
    # 검토 대상
    if review_targets:
        lines.append(f"### 🟡 작가 검토 필요 ({len(review_targets)}개)")
        lines.append("아래 항목은 의도된 반복일 수 있어 작가 판단 필요:")
        lines.append("")
        for item in review_targets[:10]:
            target_type = item.get("type", "")
            
            if "유사도" in target_type:
                lines.append(f"- **{target_type}** (유사도 {item.get('similarity', 0):.0%})")
                lines.append(f"  - 문단 A: \"`{item.get('content_a', '')[:60]}...`\"")
                lines.append(f"  - 문단 B: \"`{item.get('content_b', '')[:60]}...`\"")
            else:
                content = item.get("content", "")
                preview = content[:60] + ("..." if len(content) > 60 else "")
                count = item.get("count", "?")
                lines.append(f"- **{target_type}** ({count}회)")
                lines.append(f"  - \"`{preview}`\"")
            
            if item.get("reason"):
                lines.append(f"  - 사유: {item['reason']}")
        lines.append("")
    
    # 단어 과다 사용
    word_overuse = stats.get("word_overuse", [])
    if word_overuse:
        # 정체성 키워드는 우선 표시 (★)
        identity_words = [w for w in word_overuse if w.get("type", "").startswith("★")]
        normal_words = [w for w in word_overuse if not w.get("type", "").startswith("★")]
        
        if identity_words:
            lines.append("### ⚠️ 정체성 키워드 과다 사용 (A15 규칙 위반)")
            lines.append("캐릭터 식별자(나이·정체성)는 회차당 5회 이하 권장. "
                         "다양한 표현으로 우회하세요.")
            lines.append("")
            for w in identity_words:
                lines.append(f"- 🚨 `{w['word']}`: **{w['count']}회** "
                             f"({w.get('type', '')})")
            lines.append("")
        
        if normal_words:
            lines.append(f"### 📊 과다 사용 단어 (참고)")
            for w in normal_words[:5]:
                lines.append(f"- `{w['word']}`: {w['count']}회 ({w.get('ratio_percent', 0):.2f}%)")
            lines.append("")
    
    # 요약
    estimated_chars = stats.get("estimated_chars_to_remove", 0)
    if estimated_chars > 0:
        lines.append(f"💡 자동 정리 시 예상 절감: 약 **{estimated_chars:,}자**")
    
    return "\n".join(lines)


# ══════════════════════════════════════════════
# 자가 검증
# ══════════════════════════════════════════════

def _self_test():
    """모듈 자가 검증."""
    # 케이스 1: 깨끗한 본문
    clean_text = """죽으면 끝인 줄 알았다.
47년을 그렇게 믿고 살았다.
그런데 깼다.
천장이 하얗다."""
    
    detection = detect_repetitions(clean_text)
    assert len(detection["auto_clean_targets"]) == 0
    
    # 케이스 2: 명백한 반복
    bad_text = """이수연은 웃었다. 정말로 차가운 미소였다.
이수연은 웃었다. 정말로 차가운 미소였다.
이수연은 웃었다. 정말로 차가운 미소였다.
나는 그 미소를 보았다."""
    
    detection = detect_repetitions(bad_text)
    assert len(detection["auto_clean_targets"]) > 0, "동일 문장 3회+ 미감지"
    
    cleaned, log = auto_clean_safe_repetitions(bad_text)
    assert len(cleaned) < len(bad_text), "자동 정리 실패"
    assert log["removed_count"] >= 1
    
    # 케이스 3: 의도된 반복은 보존
    intentional = """아니야.
아니야.
아니야, 그럴 리 없어."""
    
    detection = detect_repetitions(intentional)
    # 짧은 정서 반복은 검토 대상이지 자동 정리 대상이 아님
    auto_count = len(detection["auto_clean_targets"])
    # "아니야"는 12자 이하 + 정서 키워드 → 자동 정리 안 됨
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("repetition_filter.py — 반복 자동 탐지·정리 모듈")
    print("=" * 60)
    
    _self_test()
    print("\n✓ 자가 검증 통과")
    
    # 실제 EP6 시뮬레이션
    sample = """그녀는 웃었다. 정말 차가운 미소였다.
그녀는 웃었다. 정말 차가운 미소였다.
그녀는 웃었다. 정말 차가운 미소였다.

나는 카운터를 잡았다. 손이 떨렸다.

아니야.
아니야, 그럴 리 없어.

이수연이 다가왔다. 이수연이 카운터 앞에 섰다.
이수연이 손을 뻗었다. 이수연이 내 손을 잡았다.
이수연이 미소 지었다."""
    
    print("\n[시뮬레이션 본문]")
    print(sample)
    print(f"\n원본 분량: {len(sample)}자")
    
    detection = detect_repetitions(sample)
    print(f"\n[탐지 결과]")
    print(f"  자동 정리 대상: {len(detection['auto_clean_targets'])}개")
    print(f"  검토 대상: {len(detection['review_targets'])}개")
    
    cleaned, log = auto_clean_safe_repetitions(sample)
    print(f"\n[자동 정리 후]")
    print(cleaned)
    print(f"\n정리 후 분량: {len(cleaned)}자 (절감: {len(sample) - len(cleaned)}자)")
    
    print(f"\n[리포트]")
    report = generate_repetition_report(detection)
    print(report)
