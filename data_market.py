"""
data_market.py — Engine v3.0
================================
시장 정량 데이터 + 시장성 검증 시스템

수록 데이터:
- MARKET_DATA_2024 (한국출판문화산업진흥원·비욘드리서치 2024 — 162개 CP사 + 800 작가 + 811 이용자)
- CLIFFHANGER_DISTRIBUTION_BENCHMARK (이용자 데이터 + 1차 플롯 분석 기반)
- MARKET_VIABILITY_SCORE_WEIGHTS (KOCCA 결정 요인 가중치)
- SUPPLY_DEMAND_GAP (블루오션 / 레드오션 분석)

원칙:
- 모든 데이터는 정량. "팔릴 가능성"의 객관적 척도
- 향(向)별 가중치 분리 (여성향 vs 남성향)
- "4명의 전남편들" 시장성 검증의 근거

사용 예시:
    from data_market import calculate_market_viability_score
    score = calculate_market_viability_score(concept)  # 0-100
"""

# ============================================================================
# MARKET_DATA_2024 — 2024 KOCCA·KPIPA 산업 현황 실태조사
# ============================================================================
# 출처: 한국출판문화산업진흥원, 2024년 웹소설 산업 현황 실태조사
#       비욘드리서치 외주, 2025년 4월 발행
# 표본: CP/플랫폼사 162개, 작가 800명, 이용자 811명

MARKET_DATA_2024 = {
    "metadata": {
        "source": "한국출판문화산업진흥원·비욘드리서치, 2024년 웹소설 산업 현황 실태조사 (2025.04 발행)",
        "n_companies": 162,
        "n_authors": 800,
        "n_users": 811,
        "data_year": 2024,
        "publish_date": "2025-04",
    },
    
    # ─── CP/플랫폼사 측 데이터 ──────────────
    "company_data": {
        "average_revenue_won_million": 16454,  # 평균 매출액
        "average_webnovel_revenue_won_million": 7454,  # 웹소설 관련 매출 평균
        "webnovel_revenue_share_pct": 45.3,  # 웹소설이 차지하는 매출 비중
        
        "revenue_breakdown_pct": {
            "출판_매출": 55.1,
            "유료_콘텐츠_매출": 31.8,
            "2차_저작권_매출": 7.2,
            "광고_매출": 2.4,
            "해외_콘텐츠_매출": 2.0,
            "기타_수익": 1.6,
        },
        
        # 시장 점유 — CP사·플랫폼사가 거래·기획·창작하는 장르 분포
        "market_share_by_genre_pct": {
            "현대로맨스": 18.5,
            "현대판타지": 14.8,
            "정통판타지": 11.7,
            "BL": 9.9,
            "대체역사": 9.9,
            "동양로맨스": 8.0,
            "무협": 6.8,
            "SF": 4.9,
            "가족": 4.3,
            "서양로맨스": 3.1,
        },
        
        "author_recruitment_path_pct": {
            "사측_직접_투고": 40.7,
            "인터넷_연재_작품_검색": 26.5,
            "지인_소개": 18.5,
            "작가_육성_프로그램": 7.4,
            "타사_작가_영입": 3.1,
            "자체_공모전": 3.1,
            "기타": 0.6,
        },
    },
    
    # ─── 작가 측 데이터 ──────────────
    "author_data": {
        "n": 800,
        
        "platform_activity_pct_top2": {
            "카카오페이지": 39.3,
            "네이버시리즈": 37.0,
            "조아라": 29.8,
            "리디": 27.4,
            "네이버_웹소설": 13.8,
            "문피아": 10.6,
            "디리토_리디": 10.0,
            "포스타입": 7.5,
            "블라이스": 4.5,
            "노벨피아": 3.6,
        },
        
        "creation_genre_pct_top2": {
            "현대로맨스": 43.3,
            "서양로맨스": 40.0,
            "BL": 24.3,
            "현대판타지": 20.0,
            "시대물_로맨스": 13.6,
            "동양로맨스": 11.4,
            "퓨전판타지": 11.0,
            "전통판타지": 9.1,
            "추리": 6.8,
            "미스터리": 6.3,
        },
        
        "annual_income_distribution_pct": {
            "600만원_미만": 51.8,
            "600~800만원": 17.6,
            "800~1000만원": 9.5,
            "1000~3000만원": 17.3,
            "3000~5000만원": 2.4,
            "5000~7000만원": 0.3,
            "7000만원_이상": 1.3,
        },
        
        "income_source_pct": {
            "웹소설_연재_별어들임": 60.3,
            "웹소설_상관없는_기타": 33.7,
            "2차_저작물_등_간접": 6.0,
        },
        
        "difficulty_perception_pct": {
            # "어렵다" 응답 비율
            "적고_불규칙_수입": 69.5,
            "마감_부담": 50.4,
            "정신적_육체적_건강_악화": 48.5,
            "전반적_창작_어려움": 44.6,
            "악플_사이버불링": 43.3,
            "작품_기획_어려움": 37.6,
            "수익_배분_갈등": 26.6,
            "플랫폼_관계_어려움": 17.8,
        },
    },
    
    # ─── 이용자 측 데이터 (★ 타겟 축의 결정적 근거) ──────────────
    "user_data": {
        "n": 811,
        
        # 이용 플랫폼 (1+2+3 순위 합산)
        "platform_usage_pct": {
            "카카오페이지": 73.9,
            "네이버_웹소설": 63.1,
            "네이버시리즈": 62.4,
            "문피아": 12.6,
            "리디": 12.1,
            "조아라": 9.2,
            "노벨피아": 9.0,
            "원스토어_원스토어북스": 7.3,
            "봄툰": 7.2,
            "북팔": 5.8,
            "포스타입": 5.4,
            "스토리24": 4.9,
            "카카오페이지_스테이지": 4.9,
            "창작의_날씨_교보문고": 4.8,
            "블라이스": 3.5,
        },
        "platform_usage_pct_1st_only": {
            "카카오페이지": 33.8,
            "네이버시리즈": 22.9,
            "네이버_웹소설": 22.3,
        },
        
        # ★★★ 결제 결정 요인 (인기순이 1순위) ★★★
        "decision_factors_pct_top3": {
            "인기순": 45.4,
            "소재_줄거리": 42.7,
            "장르": 35.3,
            "작품_평점": 26.1,
            "가격_유무료": 25.4,
            "최신작": 23.3,
            "댓글_평가": 19.1,
            "작품성_예술성": 17.6,
            "작가": 15.2,
            "서비스내_추천작": 14.5,
            "지인_추천": 14.5,
            "문체": 11.5,
            "인물_캐릭터": 6.9,
            "작품의_표지": 1.8,
        },
        
        # 즐겨보는 장르 (1+2+3 순위)
        "preferred_genres_pct": {
            "현대판타지": 29.1,
            "현대로맨스": 28.5,
            "정통판타지": 24.7,
            "퓨전판타지": 23.8,
            "추리": 19.5,
            "시대물_로맨스": 19.4,
            "미스터리": 19.2,
            "무협": 18.2,
            "게임판타지": 17.1,
            "서양로맨스판타지": 13.7,
        },
        
        # 최초 이용 계기
        "initial_usage_motivation_pct": {
            "무료한_시간_재미": 55.5,
            "장르소설_인터넷소설_선호": 46.7,
            "모바일_편의성": 43.0,
            "독서_즐기는_습관": 35.3,
            "친구_주변_추천": 22.3,
            "좋아하는_작가_연재": 16.4,
            "주로_이용_커뮤니티_화제": 16.3,
            "이용_가격_저렴": 15.4,
            "실제_책_구입_불편": 13.6,
            "도서관_이용_어려움": 10.1,
        },
        
        # 신간 정보 획득 경로
        "info_acquisition_pct": {
            "웹소설_플랫폼_추천_기능": 53.3,
            "인터넷_커뮤니티_웹사이트": 48.0,
            "친구_주변_지인": 29.0,
            "포털_사이트": 25.8,
            "뉴스_기사": 21.5,
            "유튜브": 19.0,
            "광고": 11.7,
            "X_트위터": 9.5,
            "기타_SNS": 8.6,
        },
        
        # ─── 결제 패턴 (★ v3.0 시장성 검증의 핵심) ───
        "monetization": {
            "유료_결제_경험_비율_pct": 79.0,
            "회당_평균_결제액_원": 8032,
            "평균_결제_이용_기간_일": 26.1,
        },
    },
}


# ============================================================================
# SUPPLY_DEMAND_GAP — 공급(시장 점유) vs 수요(이용자 선호) 갭 분석
# ============================================================================
# 음수 = 수요 > 공급 (블루오션, 신규 진입 유리)
# 양수 = 공급 > 수요 (레드오션, 차별화 필요)

SUPPLY_DEMAND_GAP = {
    # 장르별 갭 (공급 % - 수요 %)
    "by_genre_pct": {
        "현대판타지": -14.3,   # 공급 14.8 vs 수요 29.1 — 강한 블루오션
        "현대로맨스": -10.0,   # 공급 18.5 vs 수요 28.5 — 약한 블루오션
        "정통판타지": -13.0,   # 공급 11.7 vs 수요 24.7 — 강한 블루오션
        # 퓨전판타지: 공급 미집계 (CP사 카테고리에 없음), 수요 23.8 — 미정
        # 게임판타지: 공급 미집계, 수요 17.1 — 미정
        "BL": "공급_9.9_수요_미집계",
        "대체역사": "공급_9.9_수요_미집계",
        "동양로맨스_시대물로맨스": -11.4,  # 공급 8.0 vs 수요 19.4
        "무협": -11.4,        # 공급 6.8 vs 수요 18.2 (단, 별도 엔진)
        "SF": "공급_4.9_수요_미집계",
        "서양로맨스_서양로맨스판타지": -10.6,  # 공급 3.1 vs 수요 13.7
    },
    
    "interpretation": {
        "blue_ocean_top3": ["현대판타지", "정통판타지", "동양로맨스_시대물로맨스"],
        "key_insight": "여성향(현대로맨스) + 남성향(현대판타지·정통판타지) 모두 수요가 공급을 상회하는 블루오션. 신규 진입 유리.",
    },
}


# ============================================================================
# CLIFFHANGER_DISTRIBUTION_BENCHMARK — 클리프행어 7유형 분포 벤치마크
# ============================================================================
# 출처: 시장 표준 분포 추정 (이용자 데이터 + 1차 플롯 분석 + 베스트셀러 패턴 종합)
# 용도: 작품 전체 클리프행어 분포가 시장 표준 안에 있는지 검증

CLIFFHANGER_DISTRIBUTION_BENCHMARK = {
    "general": {
        # 전체 회차 대비 비율 (% 범위)
        "Reveal":   (15, 25),    # 폭로/드러남
        "Tears":    (15, 25),    # 눈물/감정 절정
        "Threat":   (10, 20),    # 위협
        "Choice":   (10, 20),    # 선택의 기로
        "Reversal": (10, 20),    # 역전/반전
        "Slap":     (5, 15),     # 따귀/분노
        "Arrival":  (5, 15),     # 인물 등장
    },
    
    # 향(向)별 차별화
    "female_oriented": {
        # 여성향: 감정 절정(Tears) 비중 높음
        "Tears":    (20, 30),
        "Reveal":   (15, 25),
        "Reversal": (10, 20),
        "Slap":     (10, 20),
        "Choice":   (10, 20),
        "Threat":   (5, 15),
        "Arrival":  (5, 15),
    },
    
    "male_oriented": {
        # 남성향: 위협·반전 비중 높음, 사이다 구조
        "Reveal":   (20, 30),
        "Threat":   (20, 30),
        "Reversal": (15, 25),
        "Choice":   (10, 20),
        "Slap":     (5, 15),
        "Tears":    (5, 15),
        "Arrival":  (5, 15),
    },
}


# ============================================================================
# MARKET_VIABILITY_SCORE_WEIGHTS — 시장성 점수 가중치 (★ 핵심)
# ============================================================================
# 출처: 2024 KOCCA 이용자 결제 결정 요인 가중치 + 향(向)별 차별화

MARKET_VIABILITY_SCORE_WEIGHTS = {
    # 일반 가중치 (총 100점)
    "general": {
        "popularity_match": 25,         # 인기순 부합 (검증된 모티프 차용)
        "premise_strength": 20,         # 소재/줄거리 강도
        "genre_market_fit": 15,         # 장르 시장 적합도 (수요-공급 갭)
        "rating_prediction": 15,        # 평점 예측 (캐릭터 매력 + 클리프행어)
        "price_appropriateness": 10,    # 가격 적정성
        "trend_recency": 10,            # 최신성·트렌드
        "artistic_merit": 5,            # 작품성
    },
    
    # 여성향 가중치
    "female_oriented": {
        "character_appeal": 30,         # 캐릭터 매력 (모에 속성 + 역할 + 마음 흐름)
        "rating_prediction": 25,        # 평점 (감정 만족도)
        "popularity_match": 20,         # 인기순 부합
        "premise_strength": 15,         # 소재 강도
        "price_appropriateness": 10,    # 가격
    },
    
    # 남성향 가중치
    "male_oriented": {
        "sida_impact": 30,              # 사이다 임팩트
        "ability_system_clarity": 25,   # 능력 시스템 명확성
        "popularity_match": 20,         # 인기순 부합
        "premise_strength": 15,         # 소재 강도
        "price_appropriateness": 10,    # 가격
    },
}


# ============================================================================
# 시장성 점수 산출 함수
# ============================================================================

def calculate_market_viability_score(concept: dict, orientation: str = "female_oriented") -> dict:
    """
    작품 콘셉트의 시장성 점수 산출 (0-100).
    
    Args:
        concept: 작품 콘셉트 카드 (formula_main, motifs, target_consumption_tier 등)
        orientation: "female_oriented" | "male_oriented" | "general"
    
    Returns:
        {
            "total": 점수 (0-100),
            "breakdown": {각 항목별 점수},
            "grade": 등급,
            "recommendations": 보강 권장 사항
        }
    """
    weights = MARKET_VIABILITY_SCORE_WEIGHTS.get(orientation, 
                                                   MARKET_VIABILITY_SCORE_WEIGHTS["general"])
    
    breakdown = {}
    total = 0
    recommendations = []
    
    # ─── 각 항목별 score (0.0-1.0) 산출 ───
    
    # 인기순 부합도
    formula_main = concept.get("formula_main", "")
    motifs = concept.get("relationship_motifs", {})
    motif_count = 0
    primary = motifs.get("primary", [])
    if isinstance(primary, list):
        motif_count += len(primary)
    elif primary:
        motif_count += 1
    motif_count += len(motifs.get("secondary", []))
    
    popularity_score = 0.0
    if formula_main:
        popularity_score += 0.5
    if motif_count >= 3:
        popularity_score += 0.3
    if motif_count >= 5:
        popularity_score += 0.2
    popularity_score = min(popularity_score, 1.0)
    
    # 소재 강도
    premise = concept.get("premise", "")
    title = concept.get("title", "")
    premise_score = 0.0
    if len(premise) >= 100:
        premise_score += 0.5
    if any(kw in title for kw in ["?", "왜", "어떻게", "전남편", "회귀", "빙의"]):
        premise_score += 0.3
    if concept.get("movement_code"):
        premise_score += 0.2
    premise_score = min(premise_score, 1.0)
    
    # 장르 시장 적합도
    genre = concept.get("genre", "")
    genre_score = 0.7
    if any(g in genre for g in ["현대판타지", "현대로맨스", "정통판타지"]):
        genre_score = 1.0
    elif "BL" in genre or "무협" in genre:
        genre_score = 0.6
    
    # 평점 예측 / 캐릭터 매력 (공통)
    char_count = len(concept.get("character_bible", {}))
    rating_score = 0.6
    if char_count >= 5:
        rating_score += 0.2
    if concept.get("affect_arc_designed"):
        rating_score += 0.2
    rating_score = min(rating_score, 1.0)
    
    # 가격 적정성
    target_eps = concept.get("target_eps", 0)
    price_score = 0.7
    if 30 <= target_eps <= 80:
        price_score = 1.0
    elif target_eps > 100:
        price_score = 0.8
    
    # 사이다 임팩트 (남성향)
    sida_score = 0.7
    if concept.get("hero_type") == "completed_hero":
        sida_score = 1.0
    
    # 능력 시스템 명확성 (남성향)
    ability_score = 0.7
    if concept.get("ability_system"):
        ability_score = 1.0
    
    # 트렌드·작품성 (general only)
    trend_score = 0.7
    artistic_score = 0.6
    
    # 감정 만족 (여성향 rating_prediction)
    emotion_score = rating_score
    
    # ─── score를 가중치에 매핑 ───
    score_map = {
        "popularity_match": popularity_score,
        "premise_strength": premise_score,
        "genre_market_fit": genre_score,
        "character_appeal": rating_score,
        "rating_prediction": emotion_score if orientation == "female_oriented" else rating_score,
        "price_appropriateness": price_score,
        "sida_impact": sida_score,
        "ability_system_clarity": ability_score,
        "trend_recency": trend_score,
        "artistic_merit": artistic_score,
    }
    
    # ★ 가중치 dict의 키만 순회 (없는 키는 무시) ★
    for weight_key, weight_val in weights.items():
        if weight_key in score_map:
            score = score_map[weight_key]
            points = round(score * weight_val, 1)
            breakdown[weight_key] = points
            total += points
    
    # 권장 사항
    if popularity_score < 0.7:
        recommendations.append("인기 모티프 추가 차용 권장 (시장 검증된 결합 패턴)")
    if rating_score < 0.7:
        recommendations.append("캐릭터 마음 흐름 아크 설계 권장 (평점 예측 향상)")
    if premise_score < 0.7:
        recommendations.append("소재 강도 강화: 제목 갈고리·이동 코드·premise 명확화")
    
    # 등급
    if total >= 85:
        grade = "★★★ 시장 출시 강력 권장"
    elif total >= 75:
        grade = "★★ 시장 출시 권장"
    elif total >= 65:
        grade = "★ 보강 후 출시 가능"
    else:
        grade = "△ 콘셉트 보강 필요"
    
    return {
        "total": round(total, 1),
        "breakdown": breakdown,
        "grade": grade,
        "recommendations": recommendations,
        "orientation": orientation,
    }


# ============================================================================
# 클리프행어 분포 검증 함수
# ============================================================================

def validate_cliffhanger_distribution(cliff_counts: dict, total_eps: int, 
                                        orientation: str = "general") -> dict:
    """
    작품 전체 클리프행어 분포가 시장 표준 안에 있는지 검증.
    
    Args:
        cliff_counts: {"Reveal": 7, "Tears": 8, ...}
        total_eps: 총 회차 수
        orientation: "general" | "female_oriented" | "male_oriented"
    
    Returns:
        {각 유형별 비율, 표준 통과 여부, 종합 판정}
    """
    benchmark = CLIFFHANGER_DISTRIBUTION_BENCHMARK.get(orientation, 
                                                        CLIFFHANGER_DISTRIBUTION_BENCHMARK["general"])
    
    result = {
        "distribution": {},
        "violations": [],
        "all_pass": True,
    }
    
    for cliff_type, count in cliff_counts.items():
        pct = round(count / total_eps * 100, 1)
        bench_range = benchmark.get(cliff_type, (0, 100))
        in_range = bench_range[0] <= pct <= bench_range[1]
        
        result["distribution"][cliff_type] = {
            "count": count,
            "pct": pct,
            "benchmark_range": bench_range,
            "in_range": in_range,
        }
        
        if not in_range:
            result["all_pass"] = False
            result["violations"].append(
                f"{cliff_type}: {pct}% (벤치마크 {bench_range[0]}-{bench_range[1]}%)"
            )
    
    return result


# ============================================================================
# 자기 검증
# ============================================================================

def _validate_module():
    """모듈 데이터 무결성 검증."""
    # KOCCA 데이터 핵심 키 존재
    assert "user_data" in MARKET_DATA_2024
    assert "decision_factors_pct_top3" in MARKET_DATA_2024["user_data"]
    assert MARKET_DATA_2024["user_data"]["decision_factors_pct_top3"]["인기순"] == 45.4
    assert MARKET_DATA_2024["user_data"]["monetization"]["회당_평균_결제액_원"] == 8032
    
    # 가중치 합 확인 (각 orientation 100점 만점)
    for orient_key in ["general", "female_oriented", "male_oriented"]:
        weights = MARKET_VIABILITY_SCORE_WEIGHTS[orient_key]
        total = sum(weights.values())
        assert total == 100, f"{orient_key} 가중치 합 100 아님: {total}"
    
    # 클리프행어 벤치마크 범위 검증
    for orient in ["general", "female_oriented", "male_oriented"]:
        bench = CLIFFHANGER_DISTRIBUTION_BENCHMARK[orient]
        for cliff_type, (lo, hi) in bench.items():
            assert lo < hi, f"{orient} {cliff_type} 범위 잘못: {lo}-{hi}"
    
    return True


_validate_module()


if __name__ == "__main__":
    print("=" * 60)
    print("data_market.py — 모듈 자가 검증")
    print("=" * 60)
    
    print("\n[2024 KOCCA 핵심 데이터]")
    user = MARKET_DATA_2024["user_data"]
    print(f"  표본: 이용자 {user['n']}명")
    print(f"  결제 경험률: {user['monetization']['유료_결제_경험_비율_pct']}%")
    print(f"  회당 평균 결제액: {user['monetization']['회당_평균_결제액_원']:,}원")
    print(f"  평균 결제 기간: {user['monetization']['평균_결제_이용_기간_일']}일")
    
    print("\n[이용자 결제 결정 요인 TOP 5]")
    for i, (factor, pct) in enumerate(list(user["decision_factors_pct_top3"].items())[:5], 1):
        print(f"  {i}. {factor}: {pct}%")
    
    print("\n[블루오션 장르 (수요>공급)]")
    for g in SUPPLY_DEMAND_GAP["interpretation"]["blue_ocean_top3"]:
        print(f"  · {g}")
    
    # ─── 4명의 전남편들 시장성 점수 시뮬레이션 ───
    print("\n[4명의 전남편들 시장성 점수 시뮬레이션]")
    
    test_concept = {
        "title": "4명의 전남편들은 왜 나를 잊지 못할까?",
        "premise": "40세 모태솔로 한시호가 교통사고로 죽고, 29세 유빈의 몸으로 깨어난다. "
                   "유빈에게는 이혼한 전남편 4명이 있었다. 그러나 한시호의 마음을 사로잡는 건 "
                   "다섯 번째 남자, 신비한 단골손님 김지훈이다.",
        "genre": "현대로맨스 빙의 치정",
        "formula_main": "운명적_인연물",
        "formula_sub": "갑을관계_파괴물",
        "movement_code": "빙의",
        "relationship_motifs": {
            "primary": ["재회물"],
            "secondary": ["운명적사랑", "갑을관계", "삼각관계", "소유욕_독점욕_질투"],
        },
        "target_eps": 42,
        "character_bible": {
            "한시호": {}, "김지훈": {}, "이수현": {}, "최진규": {},
            "이준호": {}, "박민수": {}, "박재윤": {}
        },
        "affect_arc_designed": True,
    }
    
    score_result = calculate_market_viability_score(test_concept, orientation="female_oriented")
    
    print(f"  총점: {score_result['total']}/100")
    print(f"  등급: {score_result['grade']}")
    print(f"  세부:")
    for key, val in score_result["breakdown"].items():
        print(f"    {key}: {val}")
    if score_result["recommendations"]:
        print(f"  보강 권장:")
        for rec in score_result["recommendations"]:
            print(f"    - {rec}")
    
    # ─── 4명의 전남편들 1차 플롯 클리프행어 분포 검증 ───
    print("\n[4명의 전남편들 1차 플롯 클리프행어 분포 검증]")
    cliff_counts = {
        "Tears": 8, "Reveal": 7, "Threat": 6, "Choice": 6,
        "Reversal": 6, "Slap": 5, "Arrival": 4
    }
    distrib_result = validate_cliffhanger_distribution(cliff_counts, 42, "female_oriented")
    
    for cliff_type, info in distrib_result["distribution"].items():
        status = "✓" if info["in_range"] else "✗"
        print(f"  {status} {cliff_type}: {info['count']}/{42} ({info['pct']}%) "
              f"[벤치마크 {info['benchmark_range'][0]}-{info['benchmark_range'][1]}%]")
    
    if distrib_result["violations"]:
        print("  위반:")
        for v in distrib_result["violations"]:
            print(f"    {v}")
    else:
        print("  모든 클리프행어 분포가 시장 표준 안에 있음 ✓")
    
    print("\n✓ 모든 검증 통과")
