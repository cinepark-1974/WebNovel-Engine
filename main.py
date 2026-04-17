"""
👖 BLUE JEANS WEB NOVEL ENGINE v1.0 — main.py
웹소설 연재 최적화 생산 엔진
8단계 파이프라인 · 19금/15금 듀얼 · 클리프행어 · 떡밥 관리
© 2026 BLUE JEANS PICTURES
"""

import streamlit as st
import anthropic
import json
import re
import io
import zipfile
from datetime import datetime

from prompt import (
    SYSTEM_PROMPT, GENRE_RULES, CLIFFHANGER_TYPES,
    CLIFFHANGER_RULES, EPISODE_STRUCTURE,
    AI_ANTI_PATTERN, WEB_NOVEL_PROSE_RULES,
    RATING_19, RATING_15, RATING_CONVERSION_RULES,
    PAYWALL_DESIGN, RECAP_RULES,
    detect_genre_key, get_genre_rules_block,
    build_season_arc_prompt,
    build_plant_payoff_prompt,
    build_episode_plot_prompt,
    build_episode_write_prompt,
    build_rating_convert_prompt,
    build_alternative_scene_prompt,
    build_quality_check_prompt,
    build_episode_summary_prompt,
)

# ══════════════════════════════════════════════
# Page Config
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="BLUE JEANS · Web Novel Engine",
    page_icon="👖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════
# CSS — 블루진픽처스 디자인 시스템
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-3@latest/Paperlogy.css');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');

:root {
    --navy: #191970;
    --y: #FFCB05;
    --bg: #F7F7F5;
    --card: #FFFFFF;
    --card-border: #E2E2E0;
    --t: #1A1A2E;
    --r: #D32F2F;
    --g: #2EC484;
    --dim: #8E8E99;
    --light-bg: #EEEEF6;
    --display: 'Playfair Display', 'Paperlogy', 'Georgia', serif;
    --heading: 'Paperlogy', 'Pretendard', sans-serif;
    --body: 'Pretendard', -apple-system, sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--body) !important;
    color: var(--t);
    -webkit-font-smoothing: antialiased;
}

/* 라이트모드 강제 */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"], [data-testid="stHeader"],
[data-testid="stBottom"], [data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background-color: var(--bg) !important;
    color: var(--t) !important;
}

/* 브랜드 헤더 */
.brand-header {
    text-align: center;
    padding: 2rem 0 1.5rem;
    border-bottom: 2px solid var(--y);
    margin-bottom: 1.5rem;
}
.brand-header .company {
    font-family: var(--display);
    font-weight: 900;
    font-size: 0.85rem;
    letter-spacing: 0.35em;
    color: var(--navy);
    margin-bottom: 0.25rem;
}
.brand-header .engine {
    font-family: var(--heading);
    font-weight: 700;
    font-size: 1.6rem;
    letter-spacing: 0.5em;
    color: var(--navy);
    margin-bottom: 0.3rem;
}
.brand-header .tagline {
    font-family: var(--body);
    font-weight: 300;
    font-size: 0.7rem;
    letter-spacing: 0.3em;
    color: var(--dim);
}

/* 노란 섹션 헤더 */
.section-header {
    background: var(--y);
    padding: 8px 16px;
    border-radius: 4px;
    margin: 1.2rem 0 0.6rem;
    display: inline-block;
}
.section-header span {
    font-family: var(--heading);
    font-weight: 700;
    color: var(--navy);
    font-size: 0.85rem;
    letter-spacing: 0.05em;
}

/* 카드 */
.card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 1.2rem;
    margin: 0.6rem 0;
}

/* 버튼 */
.stButton > button {
    background: var(--navy) !important;
    color: #FFFFFF !important;
    border: none !important;
    font-family: var(--heading) !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.5rem !important;
}
.stButton > button:hover {
    background: var(--y) !important;
    color: var(--navy) !important;
}

/* 탭 */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid var(--card-border);
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--heading) !important;
    font-weight: 600 !important;
    color: var(--dim) !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.03em !important;
    padding: 0.6rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--navy) !important;
    border-bottom: 3px solid var(--y) !important;
}

/* 프로그레스 */
.stProgress > div > div {
    background-color: var(--y) !important;
}

/* 텍스트 에어리어 */
textarea {
    font-family: var(--body) !important;
    font-size: 0.9rem !important;
}

/* 셀렉트/인풋 */
[data-baseweb="select"], [data-baseweb="input"] {
    font-family: var(--body) !important;
}

/* 수위 비교 */
.rating-compare {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}
.rating-badge-19 {
    background: var(--r);
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
}
.rating-badge-15 {
    background: var(--g);
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
}

/* 시퀀스 배지 */
.seq {
    display: inline-block;
    background: var(--navy);
    color: #FFFFFF !important;
    padding: 2px 10px;
    border-radius: 12px;
    font-family: var(--heading);
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 0.03em;
    margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# Brand Header
# ══════════════════════════════════════════════
st.markdown("""
<div class="brand-header">
    <div class="company">BLUE JEANS PICTURES</div>
    <div class="engine">WEB NOVEL ENGINE</div>
    <div class="tagline">YOUNG · VINTAGE · FREE · INNOVATIVE</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# API Client
# ══════════════════════════════════════════════
MODEL_OPUS = "claude-opus-4-20250514"
MODEL_SONNET = "claude-sonnet-4-20250514"
MAX_TOKENS_ARC = 12000
MAX_TOKENS_EPISODE = 8000
MAX_TOKENS_STRUCTURE = 6000
MAX_TOKENS_ANALYSIS = 4000

@st.cache_resource
def get_client():
    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

def call_claude(prompt, max_tokens=4096, model=None, system=None):
    """Claude API 호출 (스트리밍)."""
    if model is None:
        model = MODEL_SONNET
    if system is None:
        system = SYSTEM_PROMPT
    client = get_client()
    full = []
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            full.append(text)
    return "".join(full)

def call_claude_opus(prompt, max_tokens=8000, system=None):
    """Opus 모델 전용 호출 (집필용)."""
    return call_claude(prompt, max_tokens=max_tokens, model=MODEL_OPUS, system=system)

def safe_json(raw):
    """JSON 안전 파싱. 마크다운 펜스 제거 + 복구 시도."""
    if not raw:
        return None
    cleaned = re.sub(r"```json\s*", "", raw)
    cleaned = re.sub(r"```\s*$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # 후행 쉼표 제거 시도
        cleaned2 = re.sub(r",\s*([}\]])", r"\1", cleaned)
        try:
            return json.loads(cleaned2)
        except json.JSONDecodeError:
            return None

# ══════════════════════════════════════════════
# Session State 초기화
# ══════════════════════════════════════════════
defaults = {
    "step": 0,
    "concept": {},
    "season_arc": [],
    "season_arc_summaries": [],
    "plant_map": {},
    "episode_plots": {},
    "episodes_19": {},
    "episodes_15": {},
    "episode_summaries": {},
    "producer_note": "",
    "cliffhanger_history": [],
    "style_dna": "",
    "style_strength": "중",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════
# 프로듀서 노트 (전역)
# ══════════════════════════════════════════════
with st.expander("🎬 프로듀서 노트", expanded=False):
    st.session_state.producer_note = st.text_area(
        "세션 전체에 적용할 지시사항",
        value=st.session_state.producer_note,
        height=80,
        placeholder="예: 대사를 짧고 건조하게. 관능 씬은 촉각 중심. 여주 내면 독백 비중 높게.",
    )

# ══════════════════════════════════════════════
# 유틸 함수
# ══════════════════════════════════════════════
def section_header(kr, en=""):
    """노란 섹션 헤더."""
    label = f"{kr} {en}" if en else kr
    st.markdown(f'<div class="section-header"><span>{label}</span></div>', unsafe_allow_html=True)

def seq_badge(num):
    """시퀀스 배지 HTML."""
    return f'<span class="seq">{num}</span>'

def get_all_episodes_text(arc_blocks):
    """시즌 아크 블록에서 전체 에피소드 리스트 추출."""
    episodes = []
    for block in arc_blocks:
        for ep in block.get("episodes", []):
            episodes.append(ep)
    return episodes

def get_prev_episodes_summary(ep_number, count=3):
    """이전 N개 회차 요약 텍스트."""
    summaries = []
    for i in range(max(1, ep_number - count), ep_number):
        s = st.session_state.episode_summaries.get(i, "")
        if s:
            summaries.append(f"EP{i}: {s}")
    return "\n".join(summaries) if summaries else "첫 회차입니다."

def get_relevant_plants(plant_map, ep_number):
    """이번 회차에 관련된 떡밥만 필터링."""
    if not plant_map or "plants" not in plant_map:
        return "떡밥 맵 없음"
    relevant = []
    for p in plant_map["plants"]:
        if p.get("plant_ep") == ep_number:
            relevant.append(f"[심기] {p['name']}: {p.get('description', '')}")
        elif ep_number in p.get("hints", []):
            relevant.append(f"[힌트] {p['name']}: 은근히 상기시킬 것")
        elif p.get("payoff_ep") == ep_number:
            relevant.append(f"[회수] {p['name']}: 이번 회차에서 밝혀진다")
    return "\n".join(relevant) if relevant else "이번 회차 관련 떡밥 없음"

# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tabs = st.tabs([
    "STEP 1 자료입력",
    "STEP 2 시즌아크",
    "STEP 3 떡밥맵",
    "STEP 4 회차플롯",
    "STEP 5 집필",
    "STEP 6 15금변환",
    "STEP 7 품질체크",
    "STEP 8 내보내기",
])

# ──────────────────────────────────────────────
# STEP 1: 자료 입력
# ──────────────────────────────────────────────
with tabs[0]:
    section_header("자료 입력", "INPUT")

    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("가제", value=st.session_state.concept.get("title", ""))
        genre = st.selectbox("장르", list(GENRE_RULES.keys()),
                             index=0)
        logline = st.text_area("로그라인", height=80,
                               value=st.session_state.concept.get("logline", ""),
                               placeholder="but/except/and then 포함 1~2문장")
        protagonist = st.text_area("주인공", height=100,
                                   value=st.session_state.concept.get("protagonist", ""),
                                   placeholder="이름, 나이, Goal, Need, Fatal Flaw")
        love_interest = st.text_area("남주/여주 (상대역)", height=100,
                                     value=st.session_state.concept.get("love_interest", ""),
                                     placeholder="이름, 특징, 매력 포인트")
    with col2:
        villain = st.text_area("빌런 (Villain 4 Questions)", height=120,
                               value=st.session_state.concept.get("villain", ""),
                               placeholder="원하는 것 / 정당성 / 한계 / 승률")
        world = st.text_area("세계관", height=100,
                             value=st.session_state.concept.get("world", ""),
                             placeholder="배경, 시대, 특수 설정")
        relationships = st.text_area("관계 구도", height=80,
                                     value=st.session_state.concept.get("relationships", ""),
                                     placeholder="주요 인물 간 삼각/사각 관계")
        synopsis = st.text_area("시놉시스", height=120,
                                value=st.session_state.concept.get("synopsis", ""),
                                placeholder="전체 줄거리 개요")

    section_header("웹소설 설정", "SERIAL CONFIG")
    col3, col4, col5 = st.columns(3)
    with col3:
        total_eps = st.number_input("총 회차", min_value=20, max_value=200, value=80, step=10)
        target_length = st.number_input("회차당 분량(자)", min_value=2000, max_value=6000, value=3500, step=500)
    with col4:
        rating_mode = st.selectbox("수위 모드", ["듀얼(19+15)", "19금만", "15금만"])
        paywall_ep = st.number_input("과금 전환 회차", min_value=10, max_value=50, value=25, step=5)
    with col5:
        season_question = st.text_input("시즌 질문",
                                        placeholder="독자가 시즌 내내 품는 핵심 질문")
        style_strength = st.selectbox("문체 강도", ["약", "중", "강"], index=1)
        st.session_state.style_strength = style_strength

    section_header("문체 샘플", "STYLE DNA")
    style_sample = st.text_area("문체 샘플 (선택)", height=100,
                                placeholder="작가 고유 문체를 보여주는 텍스트 500자 이상")

    if st.button("✅ 자료 확정 → STEP 2로", type="primary"):
        st.session_state.concept = {
            "title": title, "genre": genre, "logline": logline,
            "protagonist": protagonist, "love_interest": love_interest,
            "villain": villain, "world": world, "relationships": relationships,
            "synopsis": synopsis, "season_question": season_question,
            "total_eps": total_eps, "target_length": target_length,
            "rating_mode": rating_mode, "paywall_ep": paywall_ep,
        }
        st.session_state.style_dna = style_sample
        st.session_state.step = 1
        st.success(f"✅ '{title}' — {genre} · {total_eps}회차 · {rating_mode} 확정. STEP 2 탭으로 이동하세요.")

# ──────────────────────────────────────────────
# STEP 2: 시즌 아크
# ──────────────────────────────────────────────
with tabs[1]:
    section_header("시즌 아크 설계", "SEASON ARC")

    concept = st.session_state.concept
    if not concept.get("title"):
        st.info("STEP 1에서 자료를 먼저 입력하세요.")
    else:
        total = concept.get("total_eps", 80)
        total_chunks = 4
        st.markdown(f"**{concept['title']}** — {concept['genre']} · {total}회차 · {total_chunks}청크 순차 생성")

        if st.button("🚀 시즌 아크 생성 (4청크)", type="primary"):
            all_blocks = []
            all_summaries = []
            prev_summary = ""
            progress = st.progress(0)
            status = st.empty()

            for chunk in range(1, total_chunks + 1):
                start_ep = (chunk - 1) * 25 + 1
                end_ep = min(chunk * 25, total)
                status.info(f"🔄 청크 {chunk}/{total_chunks} 생성 중... (EP{start_ep}~{end_ep})")

                raw = call_claude(
                    build_season_arc_prompt(
                        concept, total,
                        producer_note=st.session_state.producer_note,
                        chunk=chunk, total_chunks=total_chunks,
                        prev_summary=prev_summary,
                    ),
                    MAX_TOKENS_ARC,
                )
                result = safe_json(raw)
                if not result:
                    st.error(f"청크 {chunk} 생성 실패. 다시 시도해 주세요.")
                    break

                chunk_blocks = result.get("blocks", [])
                chunk_summary = result.get("chunk_summary", "")
                all_blocks.extend(chunk_blocks)
                all_summaries.append(chunk_summary)
                prev_summary = chunk_summary
                progress.progress(chunk / total_chunks)

            st.session_state.season_arc = all_blocks
            st.session_state.season_arc_summaries = all_summaries
            st.session_state.step = 2
            status.success(f"✅ 시즌 아크 완성 — {len(all_blocks)}블록, {sum(len(b.get('episodes', [])) for b in all_blocks)}회차")

        # 결과 표시
        if st.session_state.season_arc:
            for block in st.session_state.season_arc:
                block_no = block.get("block_no", "?")
                ep_range = block.get("ep_range", "")
                theme = block.get("theme", "")
                st.markdown(f"**블록 {block_no}** ({ep_range}) — {theme}")
                for ep in block.get("episodes", []):
                    ep_num = ep.get("ep", "?")
                    ep_title = ep.get("title", "")
                    summary = ep.get("summary", "")
                    cliff = ep.get("cliffhanger_type", "")
                    plant = ep.get("plant_or_payoff", "")
                    badge = f'<span class="seq">EP{ep_num}</span>'
                    plant_tag = f" 🌱{plant}" if plant and plant != "없음" else ""
                    st.markdown(
                        f'{badge} **{ep_title}** — {summary} [{cliff}]{plant_tag}',
                        unsafe_allow_html=True,
                    )
                st.markdown("---")

# ──────────────────────────────────────────────
# STEP 3: 떡밥 맵
# ──────────────────────────────────────────────
with tabs[2]:
    section_header("떡밥 맵", "PLANT & PAYOFF MAP")

    if not st.session_state.season_arc:
        st.info("STEP 2에서 시즌 아크를 먼저 생성하세요.")
    else:
        if st.button("🌱 떡밥 맵 생성", type="primary"):
            arc_text = json.dumps(st.session_state.season_arc, ensure_ascii=False, indent=2)
            chars = st.session_state.concept.get("protagonist", "") + "\n" + \
                    st.session_state.concept.get("love_interest", "") + "\n" + \
                    st.session_state.concept.get("villain", "")

            with st.spinner("떡밥 맵 분석 중..."):
                raw = call_claude(
                    build_plant_payoff_prompt(arc_text, chars),
                    MAX_TOKENS_STRUCTURE,
                )
            result = safe_json(raw)
            if result:
                st.session_state.plant_map = result
                st.session_state.step = 3
                st.success(f"✅ 떡밥 {len(result.get('plants', []))}개 설계 완료")
            else:
                st.error("떡밥 맵 생성 실패. 다시 시도해 주세요.")

        if st.session_state.plant_map and "plants" in st.session_state.plant_map:
            for p in st.session_state.plant_map["plants"]:
                ptype = p.get("type", "")
                color = {"핵심": "🔴", "중기": "🟡", "단기": "🟢", "미끼": "⚫"}.get(ptype, "⚪")
                hints = ", ".join([f"EP{h}" for h in p.get("hints", [])])
                st.markdown(
                    f'{color} **{p["name"]}** ({ptype}) — '
                    f'심기 EP{p.get("plant_ep", "?")} → 힌트 [{hints}] → '
                    f'회수 EP{p.get("payoff_ep", "?")}'
                )
                st.caption(p.get("description", ""))

# ──────────────────────────────────────────────
# STEP 4: 회차 플롯
# ──────────────────────────────────────────────
with tabs[3]:
    section_header("회차 플롯 설계", "EPISODE PLOT")

    if not st.session_state.season_arc:
        st.info("STEP 2에서 시즌 아크를 먼저 생성하세요.")
    else:
        all_eps = get_all_episodes_text(st.session_state.season_arc)
        total = len(all_eps)
        ep_select = st.number_input("회차 번호", min_value=1, max_value=total, value=1)

        if st.button(f"📋 EP{ep_select} 플롯 설계", type="primary"):
            # 해당 에피소드가 속한 블록 찾기
            target_block = None
            for block in st.session_state.season_arc:
                for ep in block.get("episodes", []):
                    if ep.get("ep") == ep_select:
                        target_block = block
                        break

            block_text = json.dumps(target_block, ensure_ascii=False, indent=2) if target_block else ""
            plant_relevant = get_relevant_plants(st.session_state.plant_map, ep_select)
            prev_summary = get_prev_episodes_summary(ep_select)

            with st.spinner(f"EP{ep_select} 플롯 설계 중..."):
                raw = call_claude(
                    build_episode_plot_prompt(
                        block_text, plant_relevant, ep_select,
                        prev_summary, st.session_state.producer_note,
                    ),
                    MAX_TOKENS_STRUCTURE,
                )
            result = safe_json(raw)
            if result:
                st.session_state.episode_plots[ep_select] = result
                st.success(f"✅ EP{ep_select} 플롯 완료")
            else:
                st.error("플롯 생성 실패. 다시 시도해 주세요.")

        # 플롯 표시
        if ep_select in st.session_state.episode_plots:
            plot = st.session_state.episode_plots[ep_select]
            opening = plot.get("opening", {})
            dev = plot.get("development", {})
            cliff = plot.get("cliffhanger", {})

            st.markdown(f"### EP{ep_select}. {plot.get('title', '')}")

            st.markdown("**도입**")
            st.markdown(f"- 첫 문장: {opening.get('hook_line', '')}")
            st.markdown(f"- 리캡 방식: {opening.get('recap_method', '')}")
            st.markdown(f"- 독자 질문: {opening.get('question', '')}")

            st.markdown("**전개**")
            for scene in dev.get("scenes", []):
                st.markdown(
                    f"  씬 {scene.get('scene_no', '')}: "
                    f"{scene.get('location', '')} — {scene.get('conflict', '')} "
                    f"→ {scene.get('outcome', '')}"
                )
            st.markdown(f"- 감정 곡선: {dev.get('emotion_arc', '')}")

            st.markdown("**클리프행어**")
            st.markdown(f"- 유형: {cliff.get('type', '')} — {cliff.get('content', '')}")

# ──────────────────────────────────────────────
# STEP 5: 집필
# ──────────────────────────────────────────────
with tabs[4]:
    section_header("회차 집필", "WRITING")

    concept = st.session_state.concept
    if not concept.get("title"):
        st.info("STEP 1에서 자료를 먼저 입력하세요.")
    else:
        ep_write = st.number_input("집필할 회차", min_value=1,
                                    max_value=concept.get("total_eps", 80), value=1,
                                    key="ep_write_num")

        if ep_write not in st.session_state.episode_plots:
            st.warning(f"EP{ep_write} 플롯이 없습니다. STEP 4에서 먼저 설계하세요.")
        else:
            rating_mode = concept.get("rating_mode", "듀얼(19+15)")
            write_rating = "19" if "19" in rating_mode else "15"

            if st.button(f"✍️ EP{ep_write} 집필 시작 ({write_rating}금)", type="primary"):
                plot_text = json.dumps(st.session_state.episode_plots[ep_write], ensure_ascii=False, indent=2)
                chars = concept.get("protagonist", "") + "\n" + \
                        concept.get("love_interest", "") + "\n" + \
                        concept.get("villain", "")
                prev_3 = get_prev_episodes_summary(ep_write, count=3)
                plant_rel = get_relevant_plants(st.session_state.plant_map, ep_write)

                with st.spinner(f"EP{ep_write} 집필 중 (Opus)..."):
                    result = call_claude_opus(
                        build_episode_write_prompt(
                            episode_plot=plot_text,
                            characters=chars,
                            style_dna=st.session_state.style_dna,
                            genre=concept.get("genre", "로맨스판타지"),
                            rating=write_rating,
                            prev_3_episodes=prev_3,
                            plant_map_relevant=plant_rel,
                            producer_note=st.session_state.producer_note,
                            style_strength=st.session_state.style_strength,
                            target_length=concept.get("target_length", 3500),
                        ),
                        MAX_TOKENS_EPISODE,
                    )

                if result:
                    st.session_state.episodes_19[ep_write] = result
                    # 자동 요약 생성
                    summary_raw = call_claude(
                        build_episode_summary_prompt(result, ep_write),
                        MAX_TOKENS_ANALYSIS,
                    )
                    st.session_state.episode_summaries[ep_write] = summary_raw.strip()
                    st.success(f"✅ EP{ep_write} 집필 완료 ({len(result)}자)")

            # 결과 표시
            if ep_write in st.session_state.episodes_19:
                text = st.session_state.episodes_19[ep_write]
                st.markdown(f'<span class="rating-badge-19">19금</span> **EP{ep_write}** — {len(text)}자',
                           unsafe_allow_html=True)
                st.text_area("원고", value=text, height=500, key=f"ep19_{ep_write}")

# ──────────────────────────────────────────────
# STEP 6: 15금 변환
# ──────────────────────────────────────────────
with tabs[5]:
    section_header("15금 변환", "RATING CONVERSION")

    concept = st.session_state.concept
    rating_mode = concept.get("rating_mode", "")

    if "15" not in rating_mode and "듀얼" not in rating_mode:
        st.info("수위 모드가 '19금만'으로 설정되어 있습니다. 15금 변환이 필요하면 STEP 1에서 변경하세요.")
    else:
        written_eps = sorted(st.session_state.episodes_19.keys())
        if not written_eps:
            st.info("STEP 5에서 먼저 집필하세요.")
        else:
            ep_convert = st.selectbox("변환할 회차", written_eps, key="ep_convert_select")

            if st.button(f"🔄 EP{ep_convert} → 15금 변환", type="primary"):
                text_19 = st.session_state.episodes_19[ep_convert]

                with st.spinner(f"EP{ep_convert} 15금 변환 중..."):
                    result = call_claude(
                        build_rating_convert_prompt(text_19),
                        MAX_TOKENS_EPISODE,
                    )

                if result:
                    st.session_state.episodes_15[ep_convert] = result
                    st.success(f"✅ EP{ep_convert} 15금 변환 완료 ({len(result)}자)")

            # 좌우 비교
            if ep_convert in st.session_state.episodes_19 and ep_convert in st.session_state.episodes_15:
                col_19, col_15 = st.columns(2)
                with col_19:
                    st.markdown('<span class="rating-badge-19">19금 원본</span>', unsafe_allow_html=True)
                    st.text_area("19금", value=st.session_state.episodes_19[ep_convert],
                                height=400, key=f"compare_19_{ep_convert}")
                with col_15:
                    st.markdown('<span class="rating-badge-15">15금 변환</span>', unsafe_allow_html=True)
                    st.text_area("15금", value=st.session_state.episodes_15[ep_convert],
                                height=400, key=f"compare_15_{ep_convert}")

# ──────────────────────────────────────────────
# STEP 7: 품질 체크
# ──────────────────────────────────────────────
with tabs[6]:
    section_header("품질 체크", "QUALITY CHECK")

    written_eps_all = sorted(set(
        list(st.session_state.episodes_19.keys()) +
        list(st.session_state.episodes_15.keys())
    ))
    if not written_eps_all:
        st.info("집필된 회차가 없습니다.")
    else:
        ep_check = st.selectbox("검사할 회차", written_eps_all, key="ep_check_select")
        check_rating = st.radio("검사 대상", ["19금", "15금"], horizontal=True, key="check_rating")

        if st.button(f"🔍 EP{ep_check} 품질 검사", type="primary"):
            if check_rating == "19금":
                text = st.session_state.episodes_19.get(ep_check, "")
            else:
                text = st.session_state.episodes_15.get(ep_check, "")

            if not text:
                st.warning(f"EP{ep_check} {check_rating} 원고가 없습니다.")
            else:
                chars = st.session_state.concept.get("protagonist", "") + "\n" + \
                        st.session_state.concept.get("love_interest", "") + "\n" + \
                        st.session_state.concept.get("villain", "")
                plant_text = json.dumps(st.session_state.plant_map, ensure_ascii=False) if st.session_state.plant_map else ""
                prev_sum = get_prev_episodes_summary(ep_check)
                rating_num = "19" if check_rating == "19금" else "15"

                with st.spinner("품질 검사 중..."):
                    raw = call_claude(
                        build_quality_check_prompt(
                            text, ep_check, chars, plant_text, prev_sum, rating_num,
                        ),
                        MAX_TOKENS_ANALYSIS,
                    )
                result = safe_json(raw)
                if result:
                    score = result.get("overall_score", 0)
                    color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                    st.markdown(f"### {color} 종합 점수: {score}/100")

                    # AI Anti-Pattern
                    violations = result.get("ai_antipattern_violations", [])
                    if violations:
                        st.markdown("**AI Anti-Pattern 위반:**")
                        for v in violations:
                            st.markdown(f"- {v.get('rule', '')}: {v.get('suggestion', '')}")
                    else:
                        st.markdown("✅ AI Anti-Pattern 위반 없음")

                    # 떡밥
                    pp = result.get("plant_payoff_check", [])
                    if pp:
                        st.markdown("**떡밥 배치:**")
                        for p in pp:
                            st.markdown(f"- {p.get('id', '')}: {p.get('status', '')}")

                    # 개선 사항
                    improvements = result.get("top_3_improvements", [])
                    if improvements:
                        st.markdown("**Top 3 개선 사항:**")
                        for idx, imp in enumerate(improvements, 1):
                            st.markdown(f"{idx}. {imp}")
                else:
                    st.error("품질 검사 파싱 실패.")

# ──────────────────────────────────────────────
# STEP 8: 내보내기
# ──────────────────────────────────────────────
with tabs[7]:
    section_header("내보내기", "EXPORT")

    eps_19 = st.session_state.episodes_19
    eps_15 = st.session_state.episodes_15

    if not eps_19 and not eps_15:
        st.info("집필된 회차가 없습니다.")
    else:
        st.markdown(f"**19금:** {len(eps_19)}회차 | **15금:** {len(eps_15)}회차")

        # ZIP 다운로드
        if st.button("📦 전체 ZIP 다운로드", type="primary"):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                title = st.session_state.concept.get("title", "webnovel")
                # 19금
                for ep_num in sorted(eps_19.keys()):
                    fname = f"19금/EP{ep_num:03d}.txt"
                    zf.writestr(fname, eps_19[ep_num])
                # 15금
                for ep_num in sorted(eps_15.keys()):
                    fname = f"15금/EP{ep_num:03d}.txt"
                    zf.writestr(fname, eps_15[ep_num])
                # 메타데이터
                if st.session_state.season_arc:
                    zf.writestr("metadata/season_arc.json",
                               json.dumps(st.session_state.season_arc, ensure_ascii=False, indent=2))
                if st.session_state.plant_map:
                    zf.writestr("metadata/plant_payoff_map.json",
                               json.dumps(st.session_state.plant_map, ensure_ascii=False, indent=2))
                if st.session_state.episode_plots:
                    zf.writestr("metadata/episode_plots.json",
                               json.dumps({str(k): v for k, v in st.session_state.episode_plots.items()},
                                         ensure_ascii=False, indent=2))

            st.download_button(
                label=f"⬇️ {title}_전체.zip",
                data=buf.getvalue(),
                file_name=f"{title}_{datetime.now().strftime('%Y%m%d')}.zip",
                mime="application/zip",
            )

        # 개별 TXT 다운로드
        section_header("개별 회차 다운로드", "INDIVIDUAL")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.markdown("**19금**")
            for ep_num in sorted(eps_19.keys()):
                st.download_button(
                    f"EP{ep_num:03d}.txt",
                    eps_19[ep_num],
                    f"19금_EP{ep_num:03d}.txt",
                    key=f"dl19_{ep_num}",
                )
        with col_dl2:
            st.markdown("**15금**")
            for ep_num in sorted(eps_15.keys()):
                st.download_button(
                    f"EP{ep_num:03d}.txt",
                    eps_15[ep_num],
                    f"15금_EP{ep_num:03d}.txt",
                    key=f"dl15_{ep_num}",
                )

# ══════════════════════════════════════════════
# Footer
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown(
    '<p style="text-align:center;font-family:var(--body);font-size:0.7rem;color:var(--dim);">'
    '© 2026 BLUE JEANS PICTURES · Web Novel Engine v1.0'
    '</p>',
    unsafe_allow_html=True,
)
