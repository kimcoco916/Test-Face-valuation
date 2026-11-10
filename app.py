from html import escape

import streamlit as st

from face_reader import FaceReadError, Reading, get_api_key, read_face
from styles import inject_css
from utils import ImageError, image_hash, preprocess, to_data_url

DISCLAIMER = (
    "본 서비스는 재미를 위한 것이며, 관상 결과는 과학적 근거가 없습니다. "
    "업로드한 사진은 저장되지 않습니다."
)

FEATURES = [
    ("forehead", "이마", "🌅"),
    ("eyebrows", "눈썹", "〰️"),
    ("eyes", "눈", "👁️"),
    ("nose", "코", "👃"),
    ("mouth", "입", "👄"),
    ("ears", "귀", "👂"),
    ("chin", "턱", "🙂"),
]
FORTUNES = [
    ("wealth", "재물운", "💰"),
    ("love", "애정운", "💗"),
    ("career", "직업운", "💼"),
    ("health", "건강운", "🍀"),
]

# Korean color names the model is likely to return -> swatch color
COLOR_SWATCHES = {
    "금": "#D4AF37", "골드": "#D4AF37", "황금": "#D4AF37",
    "은": "#C0C0C0", "실버": "#C0C0C0",
    "빨": "#D63A3A", "붉": "#D63A3A", "레드": "#D63A3A", "적": "#D63A3A",
    "주황": "#F08C2E", "오렌지": "#F08C2E",
    "노랑": "#F2D22E", "노란": "#F2D22E", "옐로": "#F2D22E",
    "초록": "#3FA45B", "녹": "#3FA45B", "그린": "#3FA45B", "연두": "#9BD45B",
    "하늘": "#7EC8F0", "파랑": "#2F6FD6", "파란": "#2F6FD6", "블루": "#2F6FD6", "청": "#2F6FD6",
    "남": "#22307A", "네이비": "#22307A",
    "보라": "#8A4FD1", "퍼플": "#8A4FD1", "자주": "#9B2D6F",
    "분홍": "#F29AC0", "핑크": "#F29AC0",
    "흰": "#FFFFFF", "하양": "#FFFFFF", "화이트": "#FFFFFF", "백": "#FFFFFF",
    "검": "#111111", "블랙": "#111111", "흑": "#111111",
    "회": "#8A8A8A", "그레이": "#8A8A8A",
    "갈": "#8B5A2B", "브라운": "#8B5A2B", "베이지": "#E3D3B0",
    "민트": "#8FE3CF", "청록": "#1E9C96",
}


def swatch_for(color_name: str) -> str | None:
    # Longest names first so e.g. "청록" isn't caught by "청"
    for key, hex_code in sorted(COLOR_SWATCHES.items(), key=lambda kv: -len(kv[0])):
        if key in color_name:
            return hex_code
    return None


def section_title(text: str) -> None:
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def reading_to_text(data: dict) -> str:
    lines = ["🔮 AI 관상가 결과", "", f"[총평] {data.get('summary', '')}", "", "[부위별 관상]"]
    for key, label, _ in FEATURES:
        lines.append(f"- {label}: {data['features'].get(key, '-')}")
    lines += ["", "[운세]"]
    for key, label, _ in FORTUNES:
        score = data["scores"].get(key)
        score_text = f" ({score}점)" if score is not None else ""
        lines.append(f"- {label}{score_text}: {data['fortune'].get(key, '-')}")
    lucky = data["lucky"]
    lines += [
        "",
        f"[성격 키워드] {', '.join(data['personality'])}",
        f"[조언] {data.get('advice', '')}",
        f"[행운의 색] {lucky.get('color', '-')}  [행운의 숫자] {lucky.get('number', '-')}",
        "",
        f"※ {DISCLAIMER}",
    ]
    return "\n".join(lines)


def render_reading(reading: Reading) -> None:
    if reading.status == "no_face":
        st.warning("얼굴이 잘 보이는 1인 사진을 올려주세요.")
        return
    if reading.status == "refused":
        st.info(f"이 사진은 관상 분석을 할 수 없어요. 다른 사진으로 시도해 주세요.\n\n> {reading.text}")
        return
    if reading.status == "raw":
        st.info("결과를 정리된 형태로 보여드리지 못했어요. 받은 내용을 그대로 보여드릴게요.")
        st.markdown(reading.text)
        return

    data = reading.data

    # Summary
    st.markdown(
        f"""<div class="card summary-card">
              <div class="label">✨ 총 평 ✨</div>
              <div class="text">{escape(str(data.get("summary", "")))}</div>
            </div>""",
        unsafe_allow_html=True,
    )

    # Features
    section_title("부위별 관상")
    tabs = st.tabs([f"{icon} {label}" for _, label, icon in FEATURES])
    for tab, (key, _, _) in zip(tabs, FEATURES):
        tab.write(data["features"].get(key) or "해석이 없어요.")

    # Fortune grid
    section_title("운세")
    cards = []
    for key, label, icon in FORTUNES:
        score = data["scores"].get(key)
        score_html = f'{score}<small>점</small>' if score is not None else ""
        bar_html = f'<div class="bar"><span style="width:{score}%"></span></div>' if score is not None else ""
        text = escape(str(data["fortune"].get(key, "-")))
        cards.append(
            f"""<div class="card">
                  <div class="fortune-head">
                    <span class="fortune-name">{icon} {label}</span>
                    <span class="fortune-score">{score_html}</span>
                  </div>
                  {bar_html}
                  <div class="fortune-text">{text}</div>
                </div>"""
        )
    st.markdown(f'<div class="grid-2">{"".join(cards)}</div>', unsafe_allow_html=True)

    # Personality
    if data["personality"]:
        section_title("성격 키워드")
        pills = "".join(f'<span class="pill">#{escape(str(kw))}</span>' for kw in data["personality"])
        st.markdown(f'<div class="pills">{pills}</div>', unsafe_allow_html=True)

    # Advice & lucky items
    section_title("조언과 행운")
    lucky = data["lucky"]
    color_name = str(lucky.get("color", "-"))
    swatch = swatch_for(color_name)
    swatch_html = f'<span class="swatch" style="background:{swatch}"></span>' if swatch else ""
    st.markdown(
        f"""<div class="grid-3">
              <div class="card lucky-card">
                <div class="label">💬 한마디 조언</div>
                <div class="value advice">{escape(str(data.get("advice", "-")))}</div>
              </div>
              <div class="card lucky-card">
                <div class="label">🎨 행운의 색</div>
                <div class="value">{swatch_html}{escape(color_name)}</div>
              </div>
              <div class="card lucky-card">
                <div class="label">🔢 행운의 숫자</div>
                <div class="value">{escape(str(lucky.get("number", "-")))}</div>
              </div>
            </div>""",
        unsafe_allow_html=True,
    )

    st.write("")
    st.download_button(
        "📥 결과 다운로드",
        data=reading_to_text(data),
        file_name="관상_결과.txt",
        mime="text/plain",
        width="stretch",
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🔮 AI 관상가")
        st.write("얼굴 사진 한 장으로 전통 관상학 관점의 풀이를 재미로 들려드려요.")

        st.markdown("### 사용 방법")
        st.markdown(
            "1. 사진을 올리거나 카메라로 촬영해요\n"
            "2. **🔍 관상 보기** 버튼을 눌러요\n"
            "3. 부위별 관상과 운세를 확인해요"
        )

        st.markdown("### 좋은 사진 팁")
        st.markdown(
            "- 정면을 바라본 사진\n"
            "- 밝은 조명, 선명한 화질\n"
            "- 한 사람만 나온 사진\n"
            "- 모자·선글라스는 벗고"
        )

        st.markdown("---")
        st.caption(f"※ {DISCLAIMER}")


# ---------------------------------------------------------------- page
st.set_page_config(page_title="AI 관상가", page_icon="🔮", layout="centered")
inject_css()
st.session_state.setdefault("readings", {})
render_sidebar()

st.markdown(
    """<div class="hero">
         <h1>🔮 AI 관상가</h1>
         <p>사진 한 장으로 보는 나의 관상</p>
         <div class="line"></div>
       </div>""",
    unsafe_allow_html=True,
)

api_key = get_api_key()
if not api_key:
    st.warning("API 키가 설정되지 않았습니다. `.env` 또는 Streamlit Secrets에 OPENAI_API_KEY를 등록해 주세요.")

source = st.radio(
    "사진 입력 방법",
    ["📁 사진 업로드", "📷 카메라 촬영"],
    horizontal=True,
    label_visibility="collapsed",
)

col_input, col_preview = st.columns([3, 2], gap="large")
with col_input:
    if source == "📁 사진 업로드":
        image_file = st.file_uploader(
            "얼굴 사진을 올려주세요",
            type=["jpg", "jpeg", "png", "webp"],
            help="JPG, PNG, WEBP 형식의 10MB 이하 사진만 올릴 수 있어요.",
        )
        # Streamlit's own size/type rejection messages are English-only, so state the rules in Korean up front.
        st.caption("📌 JPG · PNG · WEBP, 10MB 이하 사진만 올릴 수 있어요. 조건에 맞지 않는 파일은 빨간 Error 문구와 함께 거부돼요.")
    else:
        image_file = st.camera_input("정면을 바라보고 촬영해 주세요")

processed = None
if image_file is not None:
    raw_bytes = image_file.getvalue()
    try:
        processed = preprocess(raw_bytes)
    except ImageError as e:
        st.error(str(e))

if processed is not None:
    if source == "📁 사진 업로드":
        with col_preview:
            st.image(processed, caption="업로드한 사진", width="stretch")

    key = image_hash(raw_bytes)
    cached = st.session_state["readings"].get(key)

    clicked = st.button(
        "✅ 분석 완료" if cached is not None else "🔍 관상 보기",
        type="primary",
        disabled=not api_key or cached is not None,
        width="stretch",
    )
    if clicked and cached is None:
        with st.spinner("관상을 살피는 중입니다... 🔮"):
            try:
                cached = read_face(to_data_url(processed))
            except FaceReadError as e:
                st.error(str(e))
        # Unparsed output may be a one-off glitch: show it, but let the user retry.
        if cached is not None and cached.status != "raw":
            st.session_state["readings"][key] = cached
            st.rerun()  # redraw so the button switches to "분석 완료"

    if cached is not None:
        render_reading(cached)

st.markdown(f'<div class="footer">※ {DISCLAIMER}</div>', unsafe_allow_html=True)
