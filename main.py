"""
👖 BLUE JEANS WEB NOVEL ENGINE v2.5 — main.py
3단계 파이프라인 (CONCEPT → BUILD-UP → WRITING) + EXTENSION
Core Arc 완결형 설계 + 인기 대응 확장 모드
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
    SYSTEM_PROMPT, GENRE_RULES, WEB_NOVEL_FORMULAS, CLIFFHANGER_TYPES,
    PLATFORM_LENGTH, get_platform_length, NARRATIVE_MOTIFS, READER_PERSONAS,
    NARRATIVE_TONE_PRESETS, build_system_prompt,
    build_parse_brief_prompt, build_generate_concept_prompt, build_augment_concept_prompt,
    build_core_arc_prompt, build_extension_arc_prompt,
    build_plant_payoff_prompt, build_character_bible_prompt,
    build_episode_plot_prompt, build_episode_write_prompt,
    build_rating_convert_prompt, build_alternative_scene_prompt,
    build_quality_check_prompt, build_episode_summary_prompt,
    build_reader_simulation_prompt,
)
from parser import parse_brief
from docx_builder import (
    build_episode_docx, build_season_docx, build_proposal_docx,
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
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"], [data-testid="stHeader"],
[data-testid="stBottom"], [data-testid="stSidebar"] {
    background-color: var(--bg) !important;
    color: var(--t) !important;
}
.brand-header {
    text-align: center;
    padding: 2rem 0 1.5rem;
    border-bottom: 2px solid var(--y);
    margin-bottom: 1.5rem;
}
.brand-header .company {
    font-family: var(--display);
    font-weight: 900; font-size: 0.85rem;
    letter-spacing: 0.35em; color: var(--navy);
    margin-bottom: 0.25rem;
}
.brand-header .engine {
    font-family: var(--heading);
    font-weight: 700; font-size: 1.6rem;
    letter-spacing: 0.5em; color: var(--navy);
    margin-bottom: 0.3rem;
}
.brand-header .tagline {
    font-family: var(--body);
    font-weight: 300; font-size: 0.7rem;
    letter-spacing: 0.3em; color: var(--dim);
}
.section-header {
    background: var(--y);
    padding: 8px 16px; border-radius: 4px;
    margin: 1.2rem 0 0.6rem; display: inline-block;
}
.section-header span {
    font-family: var(--heading);
    font-weight: 700; color: var(--navy);
    font-size: 0.85rem; letter-spacing: 0.05em;
}
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
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid var(--card-border);
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--heading) !important;
    font-weight: 600 !important;
    color: var(--dim) !important;
    font-size: 0.9rem !important;
    padding: 0.8rem 2rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--navy) !important;
    border-bottom: 3px solid var(--y) !important;
}
.stProgress > div > div {
    background-color: var(--y) !important;
}
textarea { font-family: var(--body) !important; font-size: 0.9rem !important; }
.rating-badge-19 {
    background: var(--r); color: white;
    padding: 2px 8px; border-radius: 4px;
    font-size: 0.75rem; font-weight: 700;
}
.rating-badge-15 {
    background: var(--g); color: white;
    padding: 2px 8px; border-radius: 4px;
    font-size: 0.75rem; font-weight: 700;
}
.seq {
    display: inline-block;
    background: var(--navy); color: #FFFFFF !important;
    padding: 2px 10px; border-radius: 12px;
    font-family: var(--heading);
    font-weight: 700; font-size: 0.75rem;
    letter-spacing: 0.03em; margin-right: 6px;
}
.sub-tab-header {
    font-family: var(--heading);
    font-weight: 700; color: var(--navy);
    font-size: 1rem; margin: 1rem 0 0.5rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid var(--card-border);
}
.mode-card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
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
    return call_claude(prompt, max_tokens=max_tokens, model=MODEL_OPUS, system=system)


def safe_json(raw):
    """
    LLM이 반환한 텍스트에서 JSON 추출 & 파싱.
    여러 단계 정제를 거침:
      1. 마크다운 코드블록 제거
      2. { ... } 또는 [ ... ] 블록만 추출 (JSON 앞뒤에 설명 섞여도 OK)
      3. 제어 문자 제거
      4. 끝부분 trailing comma 제거
    """
    if not raw:
        return None

    # 1단계: 마크다운 코드블록 제거
    cleaned = re.sub(r"```json\s*", "", raw)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()

    # 2단계: 첫 { 부터 매칭되는 } 까지 추출 (또는 [ ... ])
    def extract_json_block(text):
        """중괄호/대괄호 균형 맞는 JSON 블록 추출."""
        for open_c, close_c in [("{", "}"), ("[", "]")]:
            start = text.find(open_c)
            if start < 0:
                continue
            depth = 0
            in_string = False
            escape = False
            for i in range(start, len(text)):
                ch = text[i]
                if escape:
                    escape = False
                    continue
                if ch == "\\":
                    escape = True
                    continue
                if ch == '"' and not escape:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if ch == open_c:
                    depth += 1
                elif ch == close_c:
                    depth -= 1
                    if depth == 0:
                        return text[start:i + 1]
        return None

    block = extract_json_block(cleaned)
    if block:
        cleaned = block

    # 3단계: 문제되는 제어 문자 제거 (JSON 외 문자열 안 제어 문자는 유지)
    cleaned = "".join(
        ch for ch in cleaned
        if ch >= " " or ch in "\n\r\t"
    )

    # 4단계: trailing comma 제거
    cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None

# ══════════════════════════════════════════════
# Session State 초기화
# ══════════════════════════════════════════════
defaults = {
    "concept_card": {},
    "core_arc": [],
    "core_arc_summaries": [],
    "extension_arc": [],
    "extension_mode": "bridge",
    "extension_eps": 50,
    "reader_feedback": "",
    "plant_map_core": {},
    "plant_map_extension": {},
    "character_bible": {},
    "episode_plots": {},
    "episodes_19": {},
    "episodes_15": {},
    "episode_summaries": {},
    "producer_note": "",
    "style_dna": "",
    "style_strength": "중",
    "brief_text": "",
    "intimacy_schedule": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════
# 프로듀서 노트 (전역)
# ══════════════════════════════════════════════
with st.expander("🎬 프로듀서 노트 (전역 적용)", expanded=False):
    st.session_state.producer_note = st.text_area(
        "세션 전체에 적용할 지시사항",
        value=st.session_state.producer_note,
        height=80,
        placeholder="예: 대사 짧고 건조하게. 관능 씬은 촉각 중심. 여주 내면 독백 비중 높게.",
        label_visibility="collapsed",
    )

# ══════════════════════════════════════════════
# 프로젝트 Save/Load (전역)
# ══════════════════════════════════════════════
PROJECT_KEYS = [
    "concept_card", "core_arc", "core_arc_summaries",
    "extension_arc", "extension_mode", "extension_eps", "reader_feedback",
    "plant_map_core", "plant_map_extension", "character_bible",
    "episode_plots", "episodes_19", "episodes_15", "episode_summaries",
    "producer_note", "style_dna", "style_strength", "brief_text",
    "intimacy_schedule",
]


def build_project_snapshot():
    """현재 세션 상태 전체를 JSON-serializable dict로 변환."""
    snap = {"_engine_version": "2.1", "_saved_at": datetime.now().isoformat()}
    for k in PROJECT_KEYS:
        val = st.session_state.get(k)
        # episode_plots, episodes_19/15, episode_summaries는 int 키 → str 키
        if isinstance(val, dict) and val and all(isinstance(kk, int) for kk in val.keys()):
            snap[k] = {str(kk): vv for kk, vv in val.items()}
        else:
            snap[k] = val
    return snap


def restore_project_snapshot(snap):
    """저장된 스냅샷을 세션 상태에 복원."""
    if not isinstance(snap, dict):
        return False
    for k in PROJECT_KEYS:
        if k not in snap:
            continue
        val = snap[k]
        # episodes_*, episode_plots는 키를 다시 int로
        if k in ("episode_plots", "episodes_19", "episodes_15", "episode_summaries"):
            if isinstance(val, dict):
                try:
                    val = {int(kk): vv for kk, vv in val.items()}
                except (ValueError, TypeError):
                    pass
        st.session_state[k] = val
    return True


with st.expander("💾 프로젝트 저장 / 불러오기", expanded=False):
    col_save, col_load = st.columns(2)

    with col_save:
        st.markdown("**💾 현재 작업 저장**")
        st.caption("지금까지의 모든 작업(컨셉 카드·아크·떡밥·바이블·플롯·원고)을 JSON 파일로 백업")
        snapshot = build_project_snapshot()
        snapshot_json = json.dumps(snapshot, ensure_ascii=False, indent=2)

        title_for_file = st.session_state.concept_card.get("title", "webnovel")
        st.download_button(
            "⬇️ 프로젝트 JSON 다운로드",
            data=snapshot_json.encode("utf-8"),
            file_name=f"{title_for_file}_project_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            key="proj_save",
        )

        # 상태 요약
        status_bits = []
        if st.session_state.concept_card.get("title"):
            status_bits.append(f"컨셉: {st.session_state.concept_card.get('title', '')}")
        if st.session_state.core_arc:
            n_eps = sum(len(b.get("episodes", [])) for b in st.session_state.core_arc)
            status_bits.append(f"Core Arc {n_eps}화")
        if st.session_state.plant_map_core:
            status_bits.append(f"떡밥 {len(st.session_state.plant_map_core.get('plants', []))}개")
        if st.session_state.character_bible:
            status_bits.append("바이블 ✓")
        if st.session_state.episode_plots:
            status_bits.append(f"플롯 {len(st.session_state.episode_plots)}개")
        if st.session_state.episodes_19:
            status_bits.append(f"19금 원고 {len(st.session_state.episodes_19)}회차")
        if st.session_state.episodes_15:
            status_bits.append(f"15금 원고 {len(st.session_state.episodes_15)}회차")
        if status_bits:
            st.info(" · ".join(status_bits))
        else:
            st.caption("아직 저장할 작업 없음")

    with col_load:
        st.markdown("**📂 저장된 프로젝트 불러오기**")
        st.caption("이전에 저장한 프로젝트 JSON을 업로드하면 세션이 복원됨")
        uploaded_proj = st.file_uploader(
            "프로젝트 JSON 업로드",
            type=["json"],
            key="proj_upload",
            label_visibility="collapsed",
        )
        if uploaded_proj:
            try:
                snap_raw = uploaded_proj.getvalue().decode("utf-8")
                snap = json.loads(snap_raw)
                if st.button("📂 불러오기 실행", type="primary", key="proj_load_btn"):
                    if restore_project_snapshot(snap):
                        st.success(
                            f"✅ 프로젝트 복원 완료 — "
                            f"'{snap.get('concept_card', {}).get('title', '(제목 없음)')}' "
                            f"(저장 시각: {snap.get('_saved_at', '?')[:16]})"
                        )
                        st.rerun()
                    else:
                        st.error("프로젝트 복원 실패 — JSON 형식을 확인해 주세요.")
            except Exception as e:
                st.error(f"JSON 파싱 실패: {e}")

# ══════════════════════════════════════════════
# 유틸
# ══════════════════════════════════════════════
def section_header(kr, en=""):
    label = f"{kr} {en}" if en else kr
    st.markdown(f'<div class="section-header"><span>{label}</span></div>', unsafe_allow_html=True)


def sub_header(text):
    st.markdown(f'<div class="sub-tab-header">{text}</div>', unsafe_allow_html=True)


def get_all_episodes(arc_blocks):
    episodes = []
    for block in arc_blocks:
        for ep in block.get("episodes", []):
            episodes.append(ep)
    return episodes


def get_prev_summary(ep_number, count=3):
    summaries = []
    for i in range(max(1, ep_number - count), ep_number):
        s = st.session_state.episode_summaries.get(i, "")
        if s:
            summaries.append(f"EP{i}: {s}")
    return "\n".join(summaries) if summaries else "첫 회차입니다."


def get_relevant_plants(plant_map, ep_number):
    if not plant_map or "plants" not in plant_map:
        return "떡밥 맵 없음"
    relevant = []
    for p in plant_map["plants"]:
        if p.get("plant_ep") == ep_number:
            relevant.append(f"[심기] {p['name']}: {p.get('description','')}")
        elif ep_number in p.get("hints", []):
            relevant.append(f"[힌트] {p['name']}: 은근히 상기")
        elif p.get("payoff_ep") == ep_number:
            relevant.append(f"[회수] {p['name']}")
    return "\n".join(relevant) if relevant else "이번 회차 관련 떡밥 없음"


def render_concept_card(card):
    """컨셉 카드를 화면에 렌더링."""
    if not card:
        return

    with st.container():
        st.markdown(f"### {card.get('title', '(제목 없음)')}")
        st.markdown(f"**장르:** {card.get('genre', '')}  |  **로그라인:** {card.get('logline', '')}")

        tags = card.get("formula_tags", [])
        if tags:
            tag_html = " ".join([f'<span class="seq">{t}</span>' for t in tags])
            st.markdown(tag_html, unsafe_allow_html=True)

        # 서사 모티프 표시
        pm = card.get("primary_motif", "")
        sm = card.get("secondary_motif", "")
        tp = card.get("target_persona", "")
        if pm or sm or tp:
            motif_bits = []
            if pm:
                motif_bits.append(f'<span class="seq">1차: {pm}</span>')
            if sm:
                motif_bits.append(f'<span class="seq">2차: {sm}</span>')
            if tp:
                motif_bits.append(f'<span class="seq">🎯 {tp}</span>')
            st.markdown(" ".join(motif_bits), unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            sub_header("주인공")
            p = card.get("protagonist", {})
            antihero_badge = " 🎭 반동인물" if p.get("is_antihero") else ""
            st.markdown(f"**{p.get('name', '')}** ({p.get('age', '')}세, {p.get('role', '')}){antihero_badge}")
            st.markdown(f"- Goal: {p.get('goal', '')}")
            st.markdown(f"- Need: {p.get('need', '')}")
            st.markdown(f"- Fatal Flaw: {p.get('fatal_flaw', '')}")

            sub_header("빌런")
            v = card.get("villain", {})
            if v.get("name"):
                st.markdown(f"**{v.get('name', '')}** ({v.get('role', '')})")
                st.markdown(f"- Wants: {v.get('wants', '')}")
                st.markdown(f"- Justification: {v.get('justification', '')}")
                st.markdown(f"- Limits: {v.get('limits', '')}")
                st.markdown(f"- Win Rate: {v.get('win_rate', '')}")
            else:
                st.warning("빌런 미설정 (자동 보강 필요)")

        with col2:
            sub_header(f"상대역 ({len(card.get('love_interests', []))}명)")
            for i, li in enumerate(card.get("love_interests", []), 1):
                st.markdown(f"**{i}. {li.get('name', '')}** — {li.get('role', '')}")
                st.caption(f"매력: {li.get('appeal', '')}  |  갈등: {li.get('conflict', '')}")

            sub_header("시즌 질문")
            sq = card.get("season_questions", {})
            st.markdown(f"- 로맨스 축: {sq.get('romance', '')}")
            st.markdown(f"- 미스터리 축: {sq.get('mystery', '')}")

        sub_header("세계관 / 관계 구도")
        st.markdown(card.get("world", ""))
        st.markdown(card.get("relationships", ""))

        sub_header("시놉시스")
        st.markdown(card.get("synopsis", ""))


def render_arc_blocks(blocks, arc_label="Core Arc"):
    """아크 블록 리스트를 화면에 렌더링."""
    for block in blocks:
        block_no = block.get("block_no", "?")
        ep_range = block.get("ep_range", "")
        theme = block.get("theme", "")
        phase = block.get("phase", "")
        st.markdown(f"**[{arc_label}] 블록 {block_no}** ({ep_range}) · {phase} — {theme}")
        for ep in block.get("episodes", []):
            ep_num = ep.get("ep", "?")
            ep_title = ep.get("title", "")
            summary = ep.get("summary", "")
            cliff = ep.get("cliffhanger_type", "")
            plant = ep.get("plant_or_payoff", "")
            plant_tag = f" 🌱{plant}" if plant and plant != "없음" else ""
            st.markdown(
                f'<span class="seq">EP{ep_num}</span> **{ep_title}** — {summary} [{cliff}]{plant_tag}',
                unsafe_allow_html=True,
            )
        st.markdown("")

# ══════════════════════════════════════════════
# 메인 탭 3개
# ══════════════════════════════════════════════
main_tabs = st.tabs([
    "STEP 1  CONCEPT",
    "STEP 2  BUILD-UP",
    "STEP 3  WRITING",
])

# ══════════════════════════════════════════════════════════════
# STEP 1: CONCEPT
# ══════════════════════════════════════════════════════════════
with main_tabs[0]:
    section_header("컨셉 설계", "CONCEPT")

    sub_tabs_1 = st.tabs(["📄 기획서 업로드", "💡 아이디어 생성", "✏️ 직접 입력"])

    # ── 1-A: 기획서 업로드 ──
    with sub_tabs_1[0]:
        st.markdown("기획서 파일(DOCX/HWP/PDF/TXT)을 업로드하면 컨셉 카드가 자동으로 채워집니다.")

        uploaded = st.file_uploader(
            "기획서 업로드",
            type=["docx", "hwp", "pdf", "txt", "md"],
            label_visibility="collapsed",
        )

        if uploaded:
            if st.button("📖 기획서 파싱 → 컨셉 카드 생성", type="primary", key="parse_brief_btn"):
                with st.spinner("기획서 텍스트 추출 중..."):
                    brief_text = parse_brief(uploaded)
                st.session_state.brief_text = brief_text

                if len(brief_text) < 200:
                    st.error(f"추출된 텍스트가 너무 짧습니다 ({len(brief_text)}자). 파일을 확인해 주세요.")
                else:
                    st.success(f"✅ 텍스트 추출 완료 ({len(brief_text)}자)")
                    with st.spinner("컨셉 카드 생성 중..."):
                        raw = call_claude(
                            build_parse_brief_prompt(brief_text),
                            MAX_TOKENS_STRUCTURE,
                        )
                    card = safe_json(raw)
                    if card:
                        st.session_state.concept_card = card
                        st.success(f"✅ 컨셉 카드 생성 완료 — '{card.get('title','')}'")
                    else:
                        st.error("컨셉 카드 파싱 실패. 아래 응답을 확인하시고 다시 시도해 주세요.")
                        with st.expander("🔍 디버깅 — LLM 응답 원본"):
                            st.code(raw[:3000] if raw else "응답 없음", language="json")

    # ── 1-B: 아이디어 생성 ──
    with sub_tabs_1[1]:
        st.markdown("한 줄 아이디어를 입력하면 컨셉 카드가 자동 생성됩니다.")

        idea = st.text_area(
            "아이디어",
            height=100,
            placeholder="예: 모태솔로가 4번 이혼녀 몸으로 환생해서 전남편 4명과 얽히는 치정 로맨스",
        )
        genre_hint = st.selectbox("장르 (선택)", [""] + list(GENRE_RULES.keys()), key="idea_genre")

        if st.button("💡 아이디어 → 컨셉 카드 생성", type="primary", key="gen_concept_btn"):
            if not idea.strip():
                st.error("아이디어를 입력해 주세요.")
            else:
                with st.spinner("컨셉 카드 생성 중..."):
                    raw = call_claude(
                        build_generate_concept_prompt(idea, genre_hint),
                        MAX_TOKENS_STRUCTURE,
                    )
                card = safe_json(raw)
                if card:
                    st.session_state.concept_card = card
                    st.success(f"✅ 컨셉 카드 생성 완료 — '{card.get('title','')}'")
                else:
                    st.error("컨셉 카드 파싱 실패. 아래 응답을 확인하시고 다시 시도해 주세요.")
                    with st.expander("🔍 디버깅 — LLM 응답 원본"):
                        st.code(raw[:3000] if raw else "응답 없음", language="json")

    # ── 1-C: 직접 입력 ──
    with sub_tabs_1[2]:
        st.markdown("9칸 양식에 직접 입력합니다.")

        card = st.session_state.concept_card
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("가제", value=card.get("title", ""))
            genre = st.selectbox(
                "장르",
                list(GENRE_RULES.keys()),
                index=list(GENRE_RULES.keys()).index(card.get("genre")) if card.get("genre") in GENRE_RULES else 0,
            )
            logline = st.text_area("로그라인", height=80, value=card.get("logline", ""))
            synopsis = st.text_area("시놉시스", height=120, value=card.get("synopsis", ""))
            world = st.text_area("세계관/배경", height=80, value=card.get("world", ""))

        with col2:
            p = card.get("protagonist", {})
            st.markdown("**주인공**")
            p_name = st.text_input("이름", value=p.get("name", ""), key="pname")
            p_goal = st.text_input("Goal", value=p.get("goal", ""), key="pgoal")
            p_need = st.text_input("Need", value=p.get("need", ""), key="pneed")
            p_flaw = st.text_input("Fatal Flaw", value=p.get("fatal_flaw", ""), key="pflaw")

            sq = card.get("season_questions", {})
            romance_q = st.text_input("시즌 질문 — 로맨스 축", value=sq.get("romance", ""))
            mystery_q = st.text_input("시즌 질문 — 미스터리 축", value=sq.get("mystery", ""))

        valid_tags = list(WEB_NOVEL_FORMULAS.keys())
        raw_tags = card.get("formula_tags", [])
        safe_default_tags = [t for t in raw_tags if t in valid_tags]
        tags = st.multiselect(
            "웹소설 공식 태그",
            valid_tags,
            default=safe_default_tags,
        )

        # ── 서사 모티프 이중 구조 ──
        st.markdown("**서사 모티프 (고경은 2022 연구 기반)**")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            primary_opts = [""] + list(NARRATIVE_MOTIFS["primary"].keys())
            cur_primary = card.get("primary_motif", "")
            p_idx = primary_opts.index(cur_primary) if cur_primary in primary_opts else 0
            primary_motif = st.selectbox(
                "1차 모티프 (시공간 이동)",
                primary_opts,
                index=p_idx,
                help="회빙환 계열. 없으면 '일상' 선택",
                key="direct_primary_motif",
            )
        with col_m2:
            secondary_opts = [""] + list(NARRATIVE_MOTIFS["secondary"].keys())
            cur_secondary = card.get("secondary_motif", "")
            s_idx = secondary_opts.index(cur_secondary) if cur_secondary in secondary_opts else 0
            secondary_motif = st.selectbox(
                "2차 모티프 (소재 결합)",
                secondary_opts,
                index=s_idx,
                help="성장물/사이다물/시스템물 등 '~물' 분류",
                key="direct_secondary_motif",
            )

        # ── 타겟 독자 페르소나 (강종현 2024 + KOCCA 통계) ──
        st.markdown("**타겟 독자 페르소나 (강종현 2024 수용자 연구)**")
        persona_opts = [""] + list(READER_PERSONAS.keys())
        cur_persona = card.get("target_persona", "")
        pers_idx = persona_opts.index(cur_persona) if cur_persona in persona_opts else 0
        target_persona = st.selectbox(
            "타겟 독자층",
            persona_opts,
            index=pers_idx,
            help="독자의 소비 동기·선호 훅·동일시 필요도가 집필 프롬프트에 자동 주입됨",
            key="direct_target_persona",
        )
        if target_persona:
            pdat = READER_PERSONAS[target_persona]
            st.caption(
                f"소비 동기: {pdat['motivation']} · "
                f"선호 훅: {pdat['preferred_hooks']} · "
                f"동일시: {pdat['identification']}"
            )

        # ── ⭐ 작품 지향점 (v2.5 신규) ──
        st.markdown("**⭐ 작품 지향점 (작가 페르소나 + 수위 톤)**")
        tone_opts = [""] + list(NARRATIVE_TONE_PRESETS.keys())
        cur_tone = card.get("narrative_tone", "")
        tone_idx = tone_opts.index(cur_tone) if cur_tone in tone_opts else 0
        narrative_tone = st.selectbox(
            "작품 지향점",
            tone_opts,
            index=tone_idx,
            help="집필 시 작가 페르소나·수위 톤·서사 기능 체크가 자동 주입. '포르노 아닌 장르 픽션'의 상업 표준 적용.",
            key="direct_narrative_tone",
        )
        if narrative_tone:
            tdat = NARRATIVE_TONE_PRESETS[narrative_tone]
            st.caption(f"📖 {tdat['description']}")
            st.caption(f"🎬 참고작: {tdat['reference_works']}")
            if tdat.get("allowed_elements"):
                with st.expander("🔓 허용 소재 (장르 필수 요소)"):
                    for el in tdat['allowed_elements']:
                        st.markdown(f"- {el}")

        # ── 반동인물 주인공 체크 ──
        is_antihero = st.checkbox(
            "주인공이 반동인물적 성향 (실리적·계산적·도덕적으로 완벽하지 않음)",
            value=card.get("protagonist", {}).get("is_antihero", False),
            help="박자희 2024 연구 기반. 착하기만 한 주인공보다 실리 따지는 주인공을 선호하는 독자 경향",
            key="direct_is_antihero",
        )

        # ── 동일시 전략 (강종현 2024 기반) ──
        with st.expander("🎭 주인공 동일시 전략 (독자 몰입 장치)"):
            id_strategy = card.get("protagonist", {}).get("identification_strategy", {})
            naming_opts = ["실명 사용", "일반명사 통일", "애칭 중심"]
            cur_naming = id_strategy.get("naming_style", "실명 사용")
            if cur_naming not in naming_opts:
                cur_naming = "실명 사용"
            naming_style = st.selectbox(
                "호칭 처리 방식",
                naming_opts,
                index=naming_opts.index(cur_naming),
                help="'일반명사 통일'은 여주를 '그녀'로만 부르는 방식 — 독자 자기 투영 강화 (로판 기법)",
                key="direct_naming_style",
            )
            empathy_text = st.text_area(
                "공감 포인트 (독자가 공감할 감정/상황, 콤마로 구분)",
                value=", ".join(id_strategy.get("empathy_points", [])),
                height=60,
                placeholder="예: 직장 상사 스트레스, 가족 갈등, 외로움",
                key="direct_empathy_points",
            )
            inner_monologue_style = st.text_input(
                "내면 독백 스타일",
                value=id_strategy.get("inner_monologue_style", ""),
                placeholder="예: 냉소적 자기 관찰 / 체념적 짧은 사유",
                key="direct_inner_style",
            )

        if st.button("✅ 직접 입력 컨셉 카드 저장", key="save_direct"):
            empathy_list = [x.strip() for x in empathy_text.split(",") if x.strip()]
            st.session_state.concept_card = {
                "title": title, "genre": genre, "logline": logline,
                "formula_tags": tags,
                "primary_motif": primary_motif,
                "secondary_motif": secondary_motif,
                "target_persona": target_persona,
                "narrative_tone": narrative_tone,
                "protagonist": {
                    "name": p_name, "age": p.get("age", 0), "role": p.get("role", ""),
                    "goal": p_goal, "need": p_need, "fatal_flaw": p_flaw,
                    "is_antihero": is_antihero,
                    "identification_strategy": {
                        "naming_style": naming_style,
                        "empathy_points": empathy_list,
                        "inner_monologue_style": inner_monologue_style,
                    },
                },
                "love_interests": card.get("love_interests", []),
                "villain": card.get("villain", {}),
                "world": world, "relationships": card.get("relationships", ""),
                "season_questions": {"romance": romance_q, "mystery": mystery_q},
                "synopsis": synopsis,
            }
            st.success("✅ 컨셉 카드 저장 완료")

    # ── 컨셉 카드 표시 + 보강 ──
    if st.session_state.concept_card:
        st.divider()
        section_header("현재 컨셉 카드", "CURRENT CARD")
        render_concept_card(st.session_state.concept_card)

        st.divider()
        section_header("자동 보강", "AUTO-AUGMENT")
        st.markdown("빈 필드 또는 약한 필드를 엔진이 자동으로 보강합니다. 특히 빌런, Fatal Flaw, 미스터리 질문이 약하면 강화.")

        if st.button("🔧 컨셉 카드 보강 실행"):
            with st.spinner("보강 중..."):
                raw = call_claude(
                    build_augment_concept_prompt(
                        json.dumps(st.session_state.concept_card, ensure_ascii=False, indent=2)
                    ),
                    MAX_TOKENS_STRUCTURE,
                )
            augmented = safe_json(raw)
            if augmented:
                st.session_state.concept_card = augmented
                st.success("✅ 보강 완료")
                st.rerun()

        # ── 연재 설정 ──
        st.divider()
        section_header("연재 설정", "SERIAL CONFIG")

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            platform = st.selectbox(
                "플랫폼",
                list(PLATFORM_LENGTH.keys()),
                index=0,
                help="플랫폼별 표준 분량이 자동 설정됩니다",
            )
            lp = get_platform_length(platform)
            st.caption(f"표준: {lp['min']:,}~{lp['max']:,}자 (공백 포함)")
            core_eps = st.number_input("Core Arc 회차", min_value=20, max_value=100, value=50, step=10)
        with col_s2:
            max_extension = st.number_input("최대 Extension 회차", min_value=0, max_value=100, value=50, step=10)
            rating_mode = st.selectbox("수위 모드", ["듀얼(19+15)", "19금만", "15금만"])
        with col_s3:
            paywall_ep = st.number_input("과금 전환 회차", min_value=5, max_value=40, value=25, step=5)
            style_strength = st.selectbox("문체 강도", ["약", "중", "강"], index=1)
            st.session_state.style_strength = style_strength

        style_sample = st.text_area("문체 샘플 (선택)", height=80, value=st.session_state.style_dna,
                                    placeholder="작가 고유 문체 샘플 500자 이상")

        if st.button("✅ 연재 설정 저장 → STEP 2로", type="primary"):
            st.session_state.concept_card["serial_config"] = {
                "platform": platform,
                "core_eps": core_eps,
                "max_extension": max_extension,
                "target_length": lp["target"],
                "rating_mode": rating_mode,
                "paywall_ep": paywall_ep,
            }
            st.session_state.style_dna = style_sample
            st.success(f"✅ 연재 설정 저장 완료 ({platform} · {lp['min']:,}~{lp['max']:,}자). STEP 2 BUILD-UP 탭으로 이동하세요.")


# ══════════════════════════════════════════════════════════════
# STEP 2: BUILD-UP
# ══════════════════════════════════════════════════════════════
with main_tabs[1]:
    section_header("빌드업", "BUILD-UP")

    if not st.session_state.concept_card.get("title"):
        st.info("STEP 1에서 컨셉 카드를 먼저 완성해 주세요.")
    else:
        sub_tabs_2 = st.tabs([
            "2-1 Core Arc",
            "2-2 떡밥 맵",
            "2-3 캐릭터 바이블",
            "2-4 회차 플롯",
            "2-5 🆙 Extension",
        ])

        concept = st.session_state.concept_card
        config = concept.get("serial_config", {})
        core_eps = config.get("core_eps", 50)

        # ── 2-1 Core Arc ──
        with sub_tabs_2[0]:
            sub_header(f"Core Arc — {core_eps}화 완결형")
            st.markdown(f"**{concept['title']}** · {concept['genre']} · 25화 × 2청크 순차 생성")

            if st.button("🚀 Core Arc 생성 (2청크)", type="primary"):
                all_blocks, all_summaries = [], []
                prev_summary = ""
                total_chunks = max(1, core_eps // 25)
                progress = st.progress(0)
                status = st.empty()

                for chunk in range(1, total_chunks + 1):
                    start_ep = (chunk - 1) * 25 + 1
                    end_ep = min(chunk * 25, core_eps)
                    status.info(f"🔄 청크 {chunk}/{total_chunks} 생성 중... (EP{start_ep}~{end_ep})")

                    with st.spinner(f"청크 {chunk}/{total_chunks} (EP{start_ep}~{end_ep}) Claude API 호출 중... (1~2분 소요)"):
                        raw = call_claude(
                            build_core_arc_prompt(
                                concept, core_eps,
                                producer_note=st.session_state.producer_note,
                                chunk=chunk, total_chunks=total_chunks,
                                prev_summary=prev_summary,
                            ),
                            MAX_TOKENS_ARC,
                        )
                    result = safe_json(raw)
                    if not result:
                        st.error(f"청크 {chunk} 생성 실패.")
                        with st.expander(f"🔍 디버깅 — 청크 {chunk} LLM 응답 원본"):
                            st.code(raw[:3000] if raw else "응답 없음", language="json")
                        break

                    all_blocks.extend(result.get("blocks", []))
                    all_summaries.append(result.get("chunk_summary", ""))
                    prev_summary = result.get("chunk_summary", "")
                    # v2.4: 19금 관능 스케줄 추출 (첫 청크에만 있음)
                    if chunk == 1 and result.get("intimacy_schedule"):
                        st.session_state.intimacy_schedule = result.get("intimacy_schedule")
                    progress.progress(chunk / total_chunks)

                st.session_state.core_arc = all_blocks
                st.session_state.core_arc_summaries = all_summaries
                ep_count = sum(len(b.get('episodes', [])) for b in all_blocks)
                status.success(
                    f"✅ Core Arc 완성 — {len(all_blocks)}블록, {ep_count}회차"
                )
                # v2.4: 관능 스케줄 안내
                if st.session_state.get("intimacy_schedule"):
                    with st.expander(f"⭐ 19금 관능 축 스케줄 ({len(st.session_state.intimacy_schedule)}지점)"):
                        for item in st.session_state.intimacy_schedule:
                            st.markdown(
                                f"- **EP {item.get('ep_range','')}** · "
                                f"`{item.get('level','')}` — {item.get('description','')}"
                            )

            if st.session_state.core_arc:
                st.divider()
                render_arc_blocks(st.session_state.core_arc, "Core")

        # ── 2-2 떡밥 맵 ──
        with sub_tabs_2[1]:
            sub_header("떡밥 맵 (Plant & Payoff)")

            if not st.session_state.core_arc:
                st.info("Core Arc를 먼저 생성하세요.")
            else:
                if st.button("🌱 Core Arc 떡밥 맵 생성", type="primary"):
                    arc_text = json.dumps(st.session_state.core_arc, ensure_ascii=False, indent=2)
                    chars = json.dumps({
                        "protagonist": concept.get("protagonist", {}),
                        "love_interests": concept.get("love_interests", []),
                        "villain": concept.get("villain", {}),
                    }, ensure_ascii=False)

                    with st.spinner("떡밥 설계 중..."):
                        raw = call_claude(
                            build_plant_payoff_prompt(arc_text, chars, arc_type="core"),
                            MAX_TOKENS_STRUCTURE,
                        )
                    result = safe_json(raw)
                    if result:
                        st.session_state.plant_map_core = result
                        st.success(f"✅ 떡밥 {len(result.get('plants', []))}개 설계")
                    else:
                        st.error("떡밥 맵 생성 실패.")

                pm = st.session_state.plant_map_core
                if pm and "plants" in pm:
                    for p in pm["plants"]:
                        ptype = p.get("type", "")
                        color = {
                            "핵심": "🔴", "중기": "🟡", "단기": "🟢",
                            "미끼": "⚫", "Extension예비": "🟣",
                        }.get(ptype, "⚪")
                        hints = ", ".join([f"EP{h}" for h in p.get("hints", [])])
                        st.markdown(
                            f'{color} **{p["name"]}** ({ptype}) — '
                            f'심기 EP{p.get("plant_ep","?")} → 힌트 [{hints}] → '
                            f'회수 EP{p.get("payoff_ep","?")}'
                        )
                        st.caption(p.get("description", ""))

        # ── 2-3 캐릭터 바이블 ──
        with sub_tabs_2[2]:
            sub_header("캐릭터 바이블")

            if st.button("👥 캐릭터 바이블 생성", type="primary"):
                with st.spinner("캐릭터 바이블 생성 중..."):
                    raw = call_claude(
                        build_character_bible_prompt(
                            json.dumps(concept, ensure_ascii=False, indent=2)
                        ),
                        MAX_TOKENS_STRUCTURE,
                    )
                result = safe_json(raw)
                if result:
                    st.session_state.character_bible = result
                    st.success("✅ 캐릭터 바이블 완성")
                else:
                    st.error("생성 실패.")
                    with st.expander("🔍 디버깅 — LLM 응답 원본"):
                        st.code(raw[:3000] if raw else "응답 없음", language="json")

            cb = st.session_state.character_bible
            if cb:
                # ── 다운로드 + Raw JSON 토글 ──
                col_cb1, col_cb2 = st.columns([3, 1])
                with col_cb1:
                    st.caption("아래는 생성된 캐릭터 바이블 요약입니다. Raw JSON은 '원본 JSON 보기'에서.")
                with col_cb2:
                    cb_json_str = json.dumps(cb, ensure_ascii=False, indent=2)
                    st.download_button(
                        "⬇️ JSON",
                        data=cb_json_str.encode("utf-8"),
                        file_name=f"{concept.get('title','wn')}_character_bible.json",
                        mime="application/json",
                        key="dl_cb_json",
                    )

                # ── 카드 형태로 렌더링 ──
                def _render_character(char, role_label, badge_class="seq"):
                    """개별 캐릭터를 카드로 렌더링."""
                    if not isinstance(char, dict):
                        return
                    name = char.get("name", "(이름 없음)")
                    age = char.get("age", "")
                    occupation = char.get("occupation", "")
                    appearance = char.get("appearance", "")

                    header = f"**{name}**"
                    if age:
                        header += f" · {age}세"
                    if occupation:
                        header += f" · {occupation}"

                    st.markdown(
                        f'<span class="{badge_class}">{role_label}</span> {header}',
                        unsafe_allow_html=True,
                    )
                    if appearance:
                        st.caption(f"🎭 {appearance}")

                    # 말투 패턴
                    speech = char.get("speech_patterns", [])
                    if speech:
                        with st.expander(f"💬 말투 패턴 ({len(speech)}개)"):
                            for s in speech:
                                st.markdown(f'- "{s}"')

                    # 주요 필드를 2열로
                    col_a, col_b = st.columns(2)
                    with col_a:
                        bp = char.get("behavioral_patterns", "")
                        if bp:
                            st.markdown("**행동 패턴**")
                            st.markdown(f"_{bp}_")
                        sw = char.get("secret_wound", "")
                        if sw:
                            st.markdown("**상처/비밀**")
                            st.markdown(f"_{sw}_")
                    with col_b:
                        dg = char.get("desire_goal", "")
                        if dg:
                            st.markdown("**욕망/목표**")
                            st.markdown(f"_{dg}_")
                        ca = char.get("character_arc", "")
                        if ca:
                            st.markdown("**캐릭터 아크**")
                            st.markdown(f"_{ca}_")
                    st.divider()

                # 주인공
                if cb.get("protagonist"):
                    st.markdown("### 🎯 주인공")
                    _render_character(cb["protagonist"], "PROTAGONIST")

                # 상대역(들)
                love_interests = cb.get("love_interests", [])
                if love_interests:
                    st.markdown(f"### 💕 상대역 ({len(love_interests)}명)")
                    for i, li in enumerate(love_interests, 1):
                        _render_character(li, f"LI #{i}")

                # 빌런
                if cb.get("villain"):
                    st.markdown("### ⚔️ 빌런")
                    _render_character(cb["villain"], "VILLAIN")

                # 조연
                supporting = cb.get("supporting", [])
                if supporting:
                    st.markdown(f"### 🎭 조연 ({len(supporting)}명)")
                    for i, sup in enumerate(supporting, 1):
                        _render_character(sup, f"조연 #{i}")

                # Raw JSON은 접어두기
                with st.expander("📄 원본 JSON 보기 (개발자용)"):
                    st.json(cb)

        # ── 2-4 회차 플롯 ──
        with sub_tabs_2[3]:
            sub_header("회차별 플롯")

            if not st.session_state.core_arc:
                st.info("Core Arc를 먼저 생성하세요.")
            else:
                all_eps = get_all_episodes(st.session_state.core_arc)
                total_plot_eps = len(all_eps)

                plot_mode = st.radio(
                    "플롯 생성 방식",
                    ["🚀 전체 일괄 생성", "📋 개별 회차 생성/재생성"],
                    horizontal=True,
                    key="plot_mode_radio",
                )

                # ── 모드 A: 전체 일괄 생성 ──
                if plot_mode == "🚀 전체 일괄 생성":
                    done_count = len(st.session_state.episode_plots)
                    st.markdown(
                        f"**Core Arc {total_plot_eps}회차** · "
                        f"현재 완료: {done_count}/{total_plot_eps}회차"
                    )

                    col_bat1, col_bat2 = st.columns([2, 1])
                    with col_bat1:
                        skip_existing = st.checkbox(
                            "이미 생성된 회차는 건너뛰기",
                            value=True,
                            key="skip_done_plots",
                        )
                    with col_bat2:
                        pass

                    if st.button(
                        f"🚀 {total_plot_eps}회차 플롯 일괄 생성",
                        type="primary",
                        key="batch_plot_btn",
                    ):
                        progress_plot = st.progress(0)
                        status_plot = st.empty()
                        fail_count = 0

                        for idx, ep_data in enumerate(all_eps, 1):
                            ep_num = ep_data.get("ep", idx)

                            # 이미 생성된 회차 건너뛰기
                            if skip_existing and ep_num in st.session_state.episode_plots:
                                progress_plot.progress(idx / total_plot_eps)
                                continue

                            status_plot.info(f"📋 EP{ep_num} 플롯 설계 중... ({idx}/{total_plot_eps})")

                            target_block = None
                            for block in st.session_state.core_arc:
                                for ep in block.get("episodes", []):
                                    if ep.get("ep") == ep_num:
                                        target_block = block
                                        break
                            block_text = json.dumps(target_block, ensure_ascii=False) if target_block else ""
                            plant_rel = get_relevant_plants(st.session_state.plant_map_core, ep_num)
                            prev_sum = get_prev_summary(ep_num)

                            with st.spinner(f"EP{ep_num} 플롯 설계 중..."):
                                raw = call_claude(
                                    build_episode_plot_prompt(
                                        block_text, plant_rel, ep_num, prev_sum,
                                        st.session_state.producer_note,
                                        concept_dict=concept,
                                        total_eps=total_plot_eps,
                                        intimacy_schedule=concept.get("intimacy_schedule") or st.session_state.get("intimacy_schedule"),
                                    ),
                                    MAX_TOKENS_STRUCTURE,
                                )
                            result = safe_json(raw)
                            if result:
                                st.session_state.episode_plots[ep_num] = result
                            else:
                                fail_count += 1

                            progress_plot.progress(idx / total_plot_eps)

                        final_done = len(st.session_state.episode_plots)
                        if fail_count == 0:
                            status_plot.success(
                                f"✅ 플롯 일괄 생성 완료 — {final_done}/{total_plot_eps}회차"
                            )
                        else:
                            status_plot.warning(
                                f"⚠️ 완료: {final_done}/{total_plot_eps} · 실패: {fail_count}회차 "
                                "(개별 재생성 탭에서 실패한 회차만 다시 시도하세요)"
                            )

                    # ── 플롯 일괄 다운로드 ──
                    if st.session_state.episode_plots:
                        st.divider()
                        st.markdown("**📦 전체 플롯 다운로드**")
                        col_dl_p1, col_dl_p2 = st.columns(2)
                        with col_dl_p1:
                            plots_json = json.dumps(
                                {str(k): v for k, v in sorted(st.session_state.episode_plots.items())},
                                ensure_ascii=False,
                                indent=2,
                            )
                            st.download_button(
                                "⬇️ 전체 플롯 JSON",
                                data=plots_json.encode("utf-8"),
                                file_name=f"{concept.get('title','wn')}_플롯_전체_{datetime.now().strftime('%Y%m%d')}.json",
                                mime="application/json",
                                key="dl_all_plots_json",
                            )
                        with col_dl_p2:
                            # DOCX: 플롯 리스트를 컨셉 카드 기획서에 추가
                            plot_lines = []
                            for ep_num in sorted(st.session_state.episode_plots.keys()):
                                p = st.session_state.episode_plots[ep_num]
                                plot_lines.append(f"EP{ep_num:03d}. {p.get('title', '')}")
                                plot_lines.append(f"  유형: {p.get('title_type', '')}")
                                cliff = p.get("cliffhanger", {})
                                plot_lines.append(f"  클리프행어: [{cliff.get('type','')}] {cliff.get('content','')}")
                                plot_lines.append("")
                            plots_txt = "\n".join(plot_lines)
                            st.download_button(
                                "⬇️ 플롯 요약 TXT",
                                data=plots_txt.encode("utf-8"),
                                file_name=f"{concept.get('title','wn')}_플롯_요약_{datetime.now().strftime('%Y%m%d')}.txt",
                                mime="text/plain",
                                key="dl_all_plots_txt",
                            )

                    # ── 생성된 플롯 리스트 미리보기 ──
                    if st.session_state.episode_plots:
                        st.divider()
                        st.markdown(f"**📋 생성된 플롯 ({len(st.session_state.episode_plots)}/{total_plot_eps}회차)**")
                        for ep_num in sorted(st.session_state.episode_plots.keys()):
                            p = st.session_state.episode_plots[ep_num]
                            title_t = p.get("title_type", "")
                            cliff_t = p.get("cliffhanger", {}).get("type", "")
                            st.markdown(
                                f'<span class="seq">EP{ep_num}</span> '
                                f'**{p.get("title", "")}** '
                                f'<span class="seq">{title_t}</span> '
                                f'[{cliff_t}]',
                                unsafe_allow_html=True,
                            )

                # ── 모드 B: 개별 회차 생성/재생성 ──
                else:
                    ep_select = st.number_input(
                        "회차 번호",
                        min_value=1,
                        max_value=total_plot_eps,
                        value=1,
                        key="plot_ep_num",
                    )

                    exists = ep_select in st.session_state.episode_plots
                    btn_label = f"🔄 EP{ep_select} 재생성" if exists else f"📋 EP{ep_select} 플롯 설계"

                    if st.button(btn_label, type="primary"):
                        target_block = None
                        for block in st.session_state.core_arc:
                            for ep in block.get("episodes", []):
                                if ep.get("ep") == ep_select:
                                    target_block = block
                                    break
                        block_text = json.dumps(target_block, ensure_ascii=False) if target_block else ""
                        plant_rel = get_relevant_plants(st.session_state.plant_map_core, ep_select)
                        prev_sum = get_prev_summary(ep_select)

                        with st.spinner(f"EP{ep_select} 플롯 설계 중..."):
                            raw = call_claude(
                                build_episode_plot_prompt(
                                    block_text, plant_rel, ep_select, prev_sum,
                                    st.session_state.producer_note,
                                    concept_dict=concept,
                                    total_eps=total_plot_eps,
                                    intimacy_schedule=concept.get("intimacy_schedule") or st.session_state.get("intimacy_schedule"),
                                ),
                                MAX_TOKENS_STRUCTURE,
                            )
                        result = safe_json(raw)
                        if result:
                            st.session_state.episode_plots[ep_select] = result
                            st.success(f"✅ EP{ep_select} 플롯 완료")
                        else:
                            st.error(f"EP{ep_select} 플롯 생성 실패.")
                            with st.expander(f"🔍 디버깅 — EP{ep_select} 응답 원본"):
                                st.code(raw[:3000] if raw else "응답 없음", language="json")

                    if ep_select in st.session_state.episode_plots:
                        plot = st.session_state.episode_plots[ep_select]
                        title_type = plot.get("title_type", "")
                        title_badge = f' <span class="seq">{title_type}</span>' if title_type else ""
                        st.markdown(
                            f"### EP{ep_select}. {plot.get('title','')}{title_badge}",
                            unsafe_allow_html=True,
                        )
                        opening = plot.get("opening", {})
                        dev = plot.get("development", {})
                        cliff = plot.get("cliffhanger", {})

                        st.markdown("**도입**")
                        st.markdown(f"- 첫 문장: {opening.get('hook_line','')}")
                        st.markdown(f"- 리캡 방식: {opening.get('recap_method','')}")
                        st.markdown(f"- 독자 질문: {opening.get('question','')}")

                        st.markdown("**전개**")
                        for scene in dev.get("scenes", []):
                            st.markdown(
                                f"  씬 {scene.get('scene_no','')}: "
                                f"{scene.get('location','')} — {scene.get('conflict','')} → "
                                f"{scene.get('outcome','')}"
                            )
                        st.markdown(f"- 감정 곡선: {dev.get('emotion_arc','')}")

                        st.markdown("**클리프행어**")
                        st.markdown(f"- 유형: {cliff.get('type','')}")
                        st.markdown(f"- 내용: {cliff.get('content','')}")

        # ── 2-5 Extension ──
        with sub_tabs_2[4]:
            sub_header("🆙 Extension Arc — 인기 확장 모드")

            if not st.session_state.core_arc:
                st.info("Core Arc를 먼저 생성하세요.")
            else:
                st.markdown("""
                Core Arc가 독자 반응이 좋아 연장이 필요한 경우 사용합니다.
                현재 집필 완료 회차와 확장 모드를 선택하세요.
                """)

                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    current_ep = st.number_input(
                        "현재 집필 완료 회차",
                        min_value=1, max_value=core_eps, value=min(30, core_eps),
                    )
                    ext_mode = st.selectbox(
                        "확장 모드",
                        ["bridge", "late", "season"],
                        format_func=lambda x: {
                            "bridge": "Bridge Extension (중반 30~35화)",
                            "late": "Late Extension (후반 45화)",
                            "season": "Season Break (완결 후 시즌2)",
                        }[x],
                    )
                with col_e2:
                    ext_eps = st.number_input(
                        "Extension 분량",
                        min_value=15, max_value=100, value=50, step=5,
                    )
                    st.session_state.extension_eps = ext_eps
                    st.session_state.extension_mode = ext_mode

                reader_feedback = st.text_area(
                    "독자 반응 데이터 (선택)",
                    value=st.session_state.reader_feedback,
                    height=100,
                    placeholder=(
                        "예시:\n"
                        "- 유료 전환율: 23%\n"
                        "- 인기 캐릭터: 이준호 (전남편1)\n"
                        "- 댓글 반응: 김지훈의 정체가 궁금하다는 의견 많음\n"
                        "- 독자들이 가장 좋아한 장면: EP15 일기장 발견"
                    ),
                )
                st.session_state.reader_feedback = reader_feedback

                if st.button("🚀 Extension Arc 생성", type="primary"):
                    total_ext_chunks = max(1, ext_eps // 25)
                    all_ext_blocks = []
                    prev_summary = ""
                    core_arc_text = json.dumps(st.session_state.core_arc, ensure_ascii=False, indent=2)

                    progress = st.progress(0)
                    status = st.empty()

                    for chunk in range(1, total_ext_chunks + 1):
                        start_ep = core_eps + (chunk - 1) * 25 + 1
                        end_ep = core_eps + min(chunk * 25, ext_eps)
                        status.info(f"🔄 Extension 청크 {chunk}/{total_ext_chunks} (EP{start_ep}~{end_ep})")

                        with st.spinner(f"Extension 청크 {chunk}/{total_ext_chunks} (EP{start_ep}~{end_ep}) 생성 중... (1~2분 소요)"):
                            raw = call_claude(
                                build_extension_arc_prompt(
                                    concept, core_arc_text, current_ep, ext_eps,
                                    mode=ext_mode,
                                    reader_feedback=reader_feedback,
                                    producer_note=st.session_state.producer_note,
                                    chunk=chunk, total_chunks=total_ext_chunks,
                                    prev_summary=prev_summary,
                                ),
                                MAX_TOKENS_ARC,
                            )
                        result = safe_json(raw)
                        if not result:
                            st.error(f"청크 {chunk} 실패.")
                            with st.expander(f"🔍 디버깅 — Extension 청크 {chunk} 응답 원본"):
                                st.code(raw[:3000] if raw else "응답 없음", language="json")
                            break

                        all_ext_blocks.extend(result.get("blocks", []))
                        prev_summary = result.get("chunk_summary", "")
                        progress.progress(chunk / total_ext_chunks)

                        # Bridge 재설계 정보 표시 (첫 청크에만)
                        if chunk == 1:
                            bridge_eps = result.get("bridge_episodes", [])
                            reused = result.get("reused_plants", [])
                            new_plants = result.get("new_plants", [])
                            new_chars = result.get("new_characters", [])
                            if bridge_eps:
                                st.info(f"🌉 Bridge 회차: {bridge_eps}")
                            if reused:
                                st.info(f"♻️ 재활용 떡밥: {', '.join(reused)}")
                            if new_plants:
                                st.info(f"🌱 신규 떡밥: {', '.join(new_plants)}")
                            if new_chars:
                                names = [c.get('name', '') for c in new_chars]
                                st.info(f"👤 신규 캐릭터: {', '.join(names)}")

                    st.session_state.extension_arc = all_ext_blocks
                    status.success(
                        f"✅ Extension Arc 완성 — {len(all_ext_blocks)}블록, "
                        f"{sum(len(b.get('episodes', [])) for b in all_ext_blocks)}회차"
                    )

                if st.session_state.extension_arc:
                    st.divider()
                    render_arc_blocks(st.session_state.extension_arc, "Extension")


# ══════════════════════════════════════════════════════════════
# STEP 3: WRITING
# ══════════════════════════════════════════════════════════════
with main_tabs[2]:
    section_header("집필", "WRITING")

    concept = st.session_state.concept_card
    if not concept.get("title"):
        st.info("STEP 1 → STEP 2 순서로 먼저 진행하세요.")
    elif not st.session_state.core_arc:
        st.info("STEP 2에서 Core Arc를 먼저 생성하세요.")
    else:
        sub_tabs_3 = st.tabs([
            "3-1 19금 집필",
            "3-2 15금 변환",
            "3-3 품질 체크",
            "🔍 3-4 독자 시뮬레이터",
            "3-5 내보내기",
        ])

        # 전체 에피소드 리스트 (Core + Extension)
        all_eps = get_all_episodes(st.session_state.core_arc)
        if st.session_state.extension_arc:
            all_eps += get_all_episodes(st.session_state.extension_arc)
        total_eps = len(all_eps)

        config = concept.get("serial_config", {})
        rating_mode = config.get("rating_mode", "듀얼(19+15)")
        platform = config.get("platform", "카카오페이지")
        target_length = config.get("target_length", 5200)

        # ── 3-1 19금 집필 ──
        with sub_tabs_3[0]:
            sub_header("19금 원고 집필 (Opus)")

            ep_write = st.number_input(
                "집필할 회차",
                min_value=1, max_value=total_eps, value=1,
                key="ep_write_num",
            )

            if ep_write not in st.session_state.episode_plots:
                st.warning(f"EP{ep_write} 플롯이 없습니다. STEP 2 → 회차 플롯에서 먼저 설계하세요.")
            else:
                write_rating = "19" if "19" in rating_mode else "15"

                if st.button(f"✍️ EP{ep_write} 집필 시작 ({write_rating}금)", type="primary"):
                    plot_text = json.dumps(st.session_state.episode_plots[ep_write], ensure_ascii=False, indent=2)
                    chars = json.dumps(st.session_state.character_bible or {
                        "protagonist": concept.get("protagonist", {}),
                        "love_interests": concept.get("love_interests", []),
                        "villain": concept.get("villain", {}),
                    }, ensure_ascii=False)

                    prev_3 = get_prev_summary(ep_write, count=3)
                    # 떡밥 맵: Core 또는 Extension 선택
                    pm = st.session_state.plant_map_core
                    if ep_write > config.get("core_eps", 50) and st.session_state.plant_map_extension:
                        pm = st.session_state.plant_map_extension
                    plant_rel = get_relevant_plants(pm, ep_write)

                    with st.spinner(f"EP{ep_write} 집필 중 (Opus)..."):
                        result = call_claude_opus(
                            build_episode_write_prompt(
                                episode_plot=plot_text,
                                characters=chars,
                                style_dna=st.session_state.style_dna,
                                genre=concept.get("genre", ""),
                                rating=write_rating,
                                prev_3_episodes=prev_3,
                                plant_map_relevant=plant_rel,
                                formula_tags=concept.get("formula_tags", []),
                                producer_note=st.session_state.producer_note,
                                style_strength=st.session_state.style_strength,
                                target_length=target_length,
                                platform=platform,
                                primary_motif=concept.get("primary_motif", ""),
                                secondary_motif=concept.get("secondary_motif", ""),
                                target_persona=concept.get("target_persona", ""),
                                concept_dict=concept,
                                ep_number=ep_write,
                                total_eps=total_eps,
                                intimacy_schedule=concept.get("intimacy_schedule") or st.session_state.get("intimacy_schedule"),
                                narrative_tone=concept.get("narrative_tone", ""),
                            ),
                            MAX_TOKENS_EPISODE,
                            system=build_system_prompt(
                                narrative_tone=concept.get("narrative_tone", ""),
                                for_episode_write=True,
                            ),
                        )

                    if result:
                        st.session_state.episodes_19[ep_write] = result
                        summary_raw = call_claude(
                            build_episode_summary_prompt(result, ep_write),
                            MAX_TOKENS_ANALYSIS,
                        )
                        st.session_state.episode_summaries[ep_write] = summary_raw.strip()
                        st.success(f"✅ EP{ep_write} 집필 완료 ({len(result)}자)")

                if ep_write in st.session_state.episodes_19:
                    text = st.session_state.episodes_19[ep_write]
                    # 첫 줄에서 제목 추출
                    lines = text.strip().split("\n")
                    title_line = lines[0].strip() if lines else f"EP{ep_write}"

                    col_title, col_dl = st.columns([3, 1])
                    with col_title:
                        st.markdown(
                            f'<span class="rating-badge-19">19금</span> '
                            f'**{title_line}** · {len(text):,}자',
                            unsafe_allow_html=True,
                        )
                    with col_dl:
                        # 개별 DOCX 다운로드
                        plot_data = st.session_state.episode_plots.get(ep_write, {})
                        docx_bytes = build_episode_docx(
                            text, ep_write, concept, plot_data, "19", platform,
                        )
                        st.download_button(
                            "📄 DOCX",
                            data=docx_bytes,
                            file_name=f"EP{ep_write:03d}_19금.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"dlx19_{ep_write}",
                        )
                    st.text_area("원고", value=text, height=500, key=f"ep19_{ep_write}")

        # ── 3-2 15금 변환 ──
        with sub_tabs_3[1]:
            sub_header("15금 변환")

            if "15" not in rating_mode and "듀얼" not in rating_mode:
                st.info("수위 모드가 '19금만'으로 설정됨.")
            else:
                written = sorted(st.session_state.episodes_19.keys())
                if not written:
                    st.info("STEP 3-1에서 먼저 19금 집필하세요.")
                else:
                    ep_conv = st.selectbox("변환할 회차", written, key="ep_conv_select")

                    if st.button(f"🔄 EP{ep_conv} → 15금 변환", type="primary"):
                        text_19 = st.session_state.episodes_19[ep_conv]
                        with st.spinner(f"EP{ep_conv} 변환 중..."):
                            result = call_claude(
                                build_rating_convert_prompt(text_19),
                                MAX_TOKENS_EPISODE,
                            )
                        if result:
                            st.session_state.episodes_15[ep_conv] = result
                            st.success(f"✅ EP{ep_conv} 15금 변환 완료 ({len(result)}자)")

                    if ep_conv in st.session_state.episodes_19 and ep_conv in st.session_state.episodes_15:
                        col19, col15 = st.columns(2)
                        with col19:
                            text_19 = st.session_state.episodes_19[ep_conv]
                            title_19 = text_19.strip().split("\n")[0] if text_19.strip() else ""
                            st.markdown(
                                f'<span class="rating-badge-19">19금 원본</span> {title_19}',
                                unsafe_allow_html=True,
                            )
                            st.text_area("19금", value=text_19,
                                         height=400, key=f"cmp19_{ep_conv}")
                        with col15:
                            text_15 = st.session_state.episodes_15[ep_conv]
                            title_15 = text_15.strip().split("\n")[0] if text_15.strip() else ""
                            col_h1, col_h2 = st.columns([3, 1])
                            with col_h1:
                                st.markdown(
                                    f'<span class="rating-badge-15">15금 변환</span> {title_15}',
                                    unsafe_allow_html=True,
                                )
                            with col_h2:
                                plot_data = st.session_state.episode_plots.get(ep_conv, {})
                                docx_bytes_15 = build_episode_docx(
                                    text_15, ep_conv, concept, plot_data, "15", platform,
                                )
                                st.download_button(
                                    "📄 DOCX",
                                    data=docx_bytes_15,
                                    file_name=f"EP{ep_conv:03d}_15금.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key=f"dlx15_{ep_conv}",
                                )
                            st.text_area("15금", value=text_15,
                                         height=400, key=f"cmp15_{ep_conv}")

        # ── 3-3 품질 체크 ──
        with sub_tabs_3[2]:
            sub_header("품질 체크")

            all_written = sorted(set(list(st.session_state.episodes_19.keys()) +
                                     list(st.session_state.episodes_15.keys())))
            if not all_written:
                st.info("집필된 회차가 없습니다.")
            else:
                ep_check = st.selectbox("검사할 회차", all_written, key="ep_check_sel")
                check_rating = st.radio("검사 대상", ["19금", "15금"], horizontal=True, key="check_rt")

                if st.button(f"🔍 EP{ep_check} 품질 검사", type="primary"):
                    text = (st.session_state.episodes_19.get(ep_check, "") if check_rating == "19금"
                            else st.session_state.episodes_15.get(ep_check, ""))
                    if not text:
                        st.warning(f"EP{ep_check} {check_rating} 원고 없음.")
                    else:
                        chars = json.dumps(st.session_state.character_bible or {}, ensure_ascii=False)
                        plant_text = json.dumps(st.session_state.plant_map_core, ensure_ascii=False)
                        prev_sum = get_prev_summary(ep_check)
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

                            violations = result.get("ai_antipattern_violations", [])
                            if violations:
                                st.markdown("**AI Anti-Pattern 위반:**")
                                for v in violations:
                                    st.markdown(f"- {v.get('rule','')}: {v.get('suggestion','')}")
                            else:
                                st.markdown("✅ AI Anti-Pattern 위반 없음")

                            improvements = result.get("top_3_improvements", [])
                            if improvements:
                                st.markdown("**Top 3 개선:**")
                                for i, imp in enumerate(improvements, 1):
                                    st.markdown(f"{i}. {imp}")

        # ── 3-4 독자 시뮬레이터 (신규 — 강종현 2024 몰입 이론) ──
        with sub_tabs_3[3]:
            sub_header("독자 시뮬레이터 — 몰입 경험 피드백")
            st.caption(
                "강종현(2024) 몰입(Flow) 이론 기반. "
                "회차 원고를 실제 독자 페르소나 관점에서 읽고 몰입 진입/이탈/결제 의사를 시뮬레이션."
            )

            sim_written = sorted(set(
                list(st.session_state.episodes_19.keys()) +
                list(st.session_state.episodes_15.keys())
            ))
            if not sim_written:
                st.info("집필된 회차가 없습니다. STEP 3-1에서 먼저 집필하세요.")
            else:
                col_sim1, col_sim2 = st.columns([1, 1])
                with col_sim1:
                    sim_ep = st.selectbox(
                        "시뮬레이션할 회차",
                        sim_written,
                        key="sim_ep_select",
                    )
                with col_sim2:
                    sim_rating = st.radio(
                        "버전",
                        ["19금", "15금"],
                        horizontal=True,
                        key="sim_rating_select",
                    )

                # 타겟 페르소나 선택 (컨셉 카드 기본값 + 수동 추가 선택 가능)
                concept_persona = concept.get("target_persona", "")
                st.markdown("**시뮬레이션할 독자 페르소나 (복수 선택 가능)**")
                default_personas = [concept_persona] if concept_persona else []
                sim_personas = st.multiselect(
                    "독자층",
                    list(READER_PERSONAS.keys()),
                    default=default_personas,
                    help="여러 페르소나를 선택하면 각각의 관점에서 피드백을 받습니다",
                    key="sim_personas_select",
                )

                if st.button(
                    f"🔍 EP{sim_ep} ({sim_rating}) 독자 시뮬레이션 실행",
                    type="primary",
                    key="run_sim_btn",
                    disabled=not sim_personas,
                ):
                    text = (
                        st.session_state.episodes_19.get(sim_ep, "")
                        if sim_rating == "19금"
                        else st.session_state.episodes_15.get(sim_ep, "")
                    )
                    if not text:
                        st.error(f"EP{sim_ep} {sim_rating} 원고가 없습니다.")
                    else:
                        results_by_persona = {}
                        for pers in sim_personas:
                            with st.spinner(f"'{pers}' 독자 시뮬레이션 중..."):
                                raw = call_claude(
                                    build_reader_simulation_prompt(
                                        text, pers, genre=concept.get("genre", "")
                                    ),
                                    MAX_TOKENS_ANALYSIS,
                                )
                            result = safe_json(raw)
                            if result:
                                results_by_persona[pers] = result
                            else:
                                results_by_persona[pers] = {"_error": True, "_raw": raw}

                        st.session_state["last_sim_results"] = {
                            "ep": sim_ep,
                            "rating": sim_rating,
                            "results": results_by_persona,
                        }

                # 결과 표시
                last_sim = st.session_state.get("last_sim_results", {})
                if last_sim and last_sim.get("ep") == sim_ep and last_sim.get("rating") == sim_rating:
                    st.divider()
                    for pers, result in last_sim.get("results", {}).items():
                        st.markdown(f"### 🎯 {pers}")

                        if result.get("_error"):
                            st.error(f"{pers} 시뮬레이션 파싱 실패.")
                            with st.expander("디버깅 — 원본 응답"):
                                st.code(result.get("_raw", "")[:2000], language="json")
                            continue

                        # 총평
                        score = result.get("flow_score", 0)
                        color = "🟢" if score >= 8 else "🟡" if score >= 5 else "🔴"
                        verdict = result.get("honest_verdict", "")
                        st.markdown(f"{color} **몰입 점수: {score}/10** · _{verdict}_")

                        # 몰입 진입
                        flow_entry = result.get("flow_entry", {})
                        entry_icon = "✅" if flow_entry.get("success") else "❌"
                        st.markdown(
                            f"**{entry_icon} 몰입 진입:** "
                            f"{flow_entry.get('entry_point', '')} "
                            f"(명확도 {flow_entry.get('clarity_score', 0)}/10)"
                        )

                        # 동일시
                        ident = result.get("identification", {})
                        ident_icon = "✅" if ident.get("works") else "❌"
                        st.markdown(f"**{ident_icon} 동일시 작동:** {ident.get('evidence', '')}")

                        # 결제 의사
                        payment = result.get("payment_intent", {})
                        pay_icon = "💰" if payment.get("next_episode") else "🚫"
                        st.markdown(
                            f"**{pay_icon} 다음 회차 결제 의사:** "
                            f"{'Y' if payment.get('next_episode') else 'N'} — "
                            f"{payment.get('reason', '')}"
                        )

                        # 이탈 지점
                        dropouts = result.get("dropout_points", [])
                        if dropouts:
                            with st.expander(f"⚠️ 이탈 가능 지점 ({len(dropouts)}곳)"):
                                for d in dropouts:
                                    st.markdown(f"- **{d.get('location', '')}:** {d.get('reason', '')}")

                        # 댓글 유발 포인트
                        comments = result.get("comment_worthy", [])
                        if comments:
                            with st.expander(f"💬 댓글 유발 포인트 ({len(comments)}개)"):
                                for c in comments:
                                    st.markdown(f"- {c}")

                        st.divider()

        # ── 3-5 내보내기 ──
        with sub_tabs_3[4]:
            sub_header("내보내기")

            eps_19 = st.session_state.episodes_19
            eps_15 = st.session_state.episodes_15
            plots = st.session_state.episode_plots

            if not eps_19 and not eps_15:
                st.info("집필된 회차가 없습니다.")
            else:
                st.markdown(f"**19금:** {len(eps_19)}회차 · **15금:** {len(eps_15)}회차 · **플랫폼:** {platform}")

                # ── 3가지 다운로드 옵션 ──
                col_dl1, col_dl2, col_dl3 = st.columns(3)

                # 1. 기획서 DOCX
                with col_dl1:
                    st.markdown("**📘 기획서 DOCX**")
                    st.caption("투자/피칭용 · 컨셉+캐릭터+아크+떡밥")
                    proposal_bytes = build_proposal_docx(
                        concept,
                        character_bible=st.session_state.character_bible,
                        core_arc=st.session_state.core_arc,
                        plant_map=st.session_state.plant_map_core,
                    )
                    title = concept.get("title", "webnovel")
                    st.download_button(
                        "⬇️ 기획서 다운로드",
                        data=proposal_bytes,
                        file_name=f"{title}_기획서_{datetime.now().strftime('%Y%m%d')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="dl_proposal",
                    )

                # 2. 시즌 전체 DOCX (19금/15금 각각)
                with col_dl2:
                    st.markdown("**📚 시즌 전체 DOCX**")
                    st.caption("회차 통합 · 커버+목차+본문")
                    if eps_19:
                        season_19_bytes = build_season_docx(eps_19, concept, "19", platform)
                        st.download_button(
                            "⬇️ 19금 시즌 전체",
                            data=season_19_bytes,
                            file_name=f"{title}_시즌1_19금_{datetime.now().strftime('%Y%m%d')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="dl_season_19",
                        )
                    if eps_15:
                        season_15_bytes = build_season_docx(eps_15, concept, "15", platform)
                        st.download_button(
                            "⬇️ 15금 시즌 전체",
                            data=season_15_bytes,
                            file_name=f"{title}_시즌1_15금_{datetime.now().strftime('%Y%m%d')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="dl_season_15",
                        )

                # 3. 전체 ZIP
                with col_dl3:
                    st.markdown("**📦 전체 ZIP**")
                    st.caption("모든 회차 TXT+DOCX · 메타데이터")
                    if st.button("🗂️ ZIP 생성", type="primary", key="make_zip"):
                        buf = io.BytesIO()
                        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                            # 19금 TXT + DOCX
                            for ep_num in sorted(eps_19.keys()):
                                text = eps_19[ep_num]
                                zf.writestr(f"19금/TXT/EP{ep_num:03d}.txt", text)
                                plot_data = plots.get(ep_num, {})
                                ep_docx = build_episode_docx(
                                    text, ep_num, concept, plot_data, "19", platform,
                                )
                                zf.writestr(f"19금/DOCX/EP{ep_num:03d}.docx", ep_docx)
                            # 15금 TXT + DOCX
                            for ep_num in sorted(eps_15.keys()):
                                text = eps_15[ep_num]
                                zf.writestr(f"15금/TXT/EP{ep_num:03d}.txt", text)
                                plot_data = plots.get(ep_num, {})
                                ep_docx = build_episode_docx(
                                    text, ep_num, concept, plot_data, "15", platform,
                                )
                                zf.writestr(f"15금/DOCX/EP{ep_num:03d}.docx", ep_docx)

                            # 기획서 DOCX
                            zf.writestr(
                                f"{title}_기획서.docx",
                                build_proposal_docx(
                                    concept,
                                    character_bible=st.session_state.character_bible,
                                    core_arc=st.session_state.core_arc,
                                    plant_map=st.session_state.plant_map_core,
                                ),
                            )

                            # 시즌 전체 DOCX
                            if eps_19:
                                zf.writestr(
                                    f"{title}_시즌1_19금_전체.docx",
                                    build_season_docx(eps_19, concept, "19", platform),
                                )
                            if eps_15:
                                zf.writestr(
                                    f"{title}_시즌1_15금_전체.docx",
                                    build_season_docx(eps_15, concept, "15", platform),
                                )

                            # 메타데이터 JSON
                            zf.writestr("metadata/concept_card.json",
                                        json.dumps(concept, ensure_ascii=False, indent=2))
                            if st.session_state.core_arc:
                                zf.writestr("metadata/core_arc.json",
                                            json.dumps(st.session_state.core_arc, ensure_ascii=False, indent=2))
                            if st.session_state.extension_arc:
                                zf.writestr("metadata/extension_arc.json",
                                            json.dumps(st.session_state.extension_arc, ensure_ascii=False, indent=2))
                            if st.session_state.plant_map_core:
                                zf.writestr("metadata/plant_map_core.json",
                                            json.dumps(st.session_state.plant_map_core, ensure_ascii=False, indent=2))
                            if st.session_state.character_bible:
                                zf.writestr("metadata/character_bible.json",
                                            json.dumps(st.session_state.character_bible, ensure_ascii=False, indent=2))
                            if plots:
                                zf.writestr("metadata/episode_plots.json",
                                            json.dumps({str(k): v for k, v in plots.items()},
                                                       ensure_ascii=False, indent=2))

                        st.download_button(
                            f"⬇️ {title}_전체.zip",
                            data=buf.getvalue(),
                            file_name=f"{title}_{datetime.now().strftime('%Y%m%d')}.zip",
                            mime="application/zip",
                            key="dl_zip",
                        )

                # ── 개별 회차 다운로드 ──
                st.divider()
                sub_header("개별 회차 다운로드")

                col_ind1, col_ind2 = st.columns(2)
                with col_ind1:
                    st.markdown("**19금 회차별**")
                    for ep_num in sorted(eps_19.keys()):
                        text = eps_19[ep_num]
                        title_line = text.strip().split("\n")[0] if text.strip() else f"EP{ep_num}"
                        plot_data = plots.get(ep_num, {})
                        ep_docx_bytes = build_episode_docx(
                            text, ep_num, concept, plot_data, "19", platform,
                        )
                        st.download_button(
                            f"EP{ep_num:03d}. {title_line[:20]}",
                            data=ep_docx_bytes,
                            file_name=f"EP{ep_num:03d}_19금.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"dl_ind_19_{ep_num}",
                        )

                with col_ind2:
                    st.markdown("**15금 회차별**")
                    for ep_num in sorted(eps_15.keys()):
                        text = eps_15[ep_num]
                        title_line = text.strip().split("\n")[0] if text.strip() else f"EP{ep_num}"
                        plot_data = plots.get(ep_num, {})
                        ep_docx_bytes = build_episode_docx(
                            text, ep_num, concept, plot_data, "15", platform,
                        )
                        st.download_button(
                            f"EP{ep_num:03d}. {title_line[:20]}",
                            data=ep_docx_bytes,
                            file_name=f"EP{ep_num:03d}_15금.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"dl_ind_15_{ep_num}",
                        )

# ══════════════════════════════════════════════
# Footer
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown(
    '<p style="text-align:center;font-family:var(--body);font-size:0.7rem;color:var(--dim);">'
    '© 2026 BLUE JEANS PICTURES · Web Novel Engine v2.5'
    '</p>',
    unsafe_allow_html=True,
)
