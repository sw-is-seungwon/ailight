import streamlit as st

# ==========================================
# 기본 설정
# ==========================================
st.set_page_config(
    page_title="AI 신호등 평가",
    page_icon="🚦",
    layout="centered"
)

TOTAL_GROUPS = 4

CRITERIA = {
    "가능": "인공지능 서비스를 바로 사용할 의사가 있어요.",
    "제한": "조건 또는 보완이 이루어진다면 사용할 의사가 있어요.",
    "금지": "사용할 의사가 없어요."
}

# ==========================================
# CSS 스타일
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

html, body, [class*="css"] {
    font-family: 'Gowun Dodum', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #fffafc 0%, #f8fbff 100%);
}

.block-container {
    max-width: 760px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

.main-card {
    background: #ffffff;
    border: 2px solid #f6ddea;
    border-radius: 28px;
    padding: 28px 24px;
    box-shadow: 0 10px 30px rgba(236, 214, 226, 0.35);
    margin-bottom: 20px;
}

.title-main {
    text-align: center;
    font-size: 2.2rem;
    font-weight: 700;
    color: #5c4b5f;
    margin-bottom: 0.3rem;
}

.subtitle-main {
    text-align: center;
    color: #857187;
    font-size: 1.05rem;
    line-height: 1.7;
    margin-bottom: 1.2rem;
}

.guide-box {
    background: #fff5fa;
    border: 2px dashed #f3bfd6;
    border-radius: 22px;
    padding: 18px 20px;
    color: #6c5a6f;
    line-height: 2;
    margin: 16px 0 20px 0;
    font-size: 1rem;
}

.small-note {
    text-align: center;
    color: #97879a;
    font-size: 0.92rem;
    margin-top: 8px;
    line-height: 1.6;
}

.section-title {
    text-align: center;
    color: #66556a;
    font-size: 1.6rem;
    font-weight: 700;
    margin-top: 0.2rem;
    margin-bottom: 0.6rem;
}

.question-text {
    text-align: center;
    color: #7b6b7f;
    font-size: 1.05rem;
    margin-bottom: 1.2rem;
}

.result-box {
    background: #f9fbff;
    border: 2px solid #dbeafe;
    border-radius: 18px;
    padding: 16px;
    color: #5f6680;
    line-height: 1.7;
}

.complete-box {
    background: #fff8fd;
    border: 2px solid #f4cce0;
    border-radius: 22px;
    padding: 16px;
    margin-top: 14px;
}

div.stButton > button {
    width: 100%;
    min-height: 56px;
    border-radius: 18px;
    font-size: 17px;
    font-weight: 700;
    border: none;
    transition: all 0.15s ease-in-out;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(0,0,0,0.08);
}

/* 시작 버튼 */
div.st-key-start_button button {
    background: #ffd6e7;
    color: #6a4a5e;
    border: 2px solid #f6bad2;
}

/* 교사용 버튼 */
div.st-key-teacher_button button {
    background: #e8eefc;
    color: #687394;
    border: 2px solid #d7e2fb;
}

/* 가능 / 제한 / 금지 */
div.st-key-green_btn button {
    background: #c9f7d6;
    color: #336247;
    border: 2px solid #aeeac0;
}

div.st-key-yellow_btn button {
    background: #fff0b8;
    color: #7a6220;
    border: 2px solid #ffe08a;
}

div.st-key-red_btn button {
    background: #ffc9c9;
    color: #7b4040;
    border: 2px solid #ffadad;
}

/* 다음 버튼 */
div.st-key-next_button button,
div.st-key-home_button button {
    background: #d9d6ff;
    color: #564f8b;
    border: 2px solid #c7c2ff;
}

/* disabled 버튼도 귀엽게 */
div.stButton > button:disabled {
    background: #f3f1f7 !important;
    color: #b0a8b8 !important;
    border: 2px solid #ece7f3 !important;
    opacity: 1 !important;
    cursor: not-allowed;
    box-shadow: none !important;
    transform: none !important;
}

.stTextArea textarea {
    border-radius: 16px !important;
    border: 2px solid #eadff0 !important;
    background: #fffdfd !important;
    color: #5d5663 !important;
    font-size: 1rem !important;
}

.stTextArea textarea:focus {
    border: 2px solid #d9c8f3 !important;
    box-shadow: 0 0 0 0.1rem rgba(217, 200, 243, 0.35) !important;
}

div[data-testid="stProgressBar"] > div > div {
    background-color: #f6c7dd !important;
}

hr {
    border: none;
    height: 1px;
    background: #f0e5ee;
    margin: 18px 0;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 세션 상태 초기화
# ==========================================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "current_group" not in st.session_state:
    st.session_state.current_group = 1

if "selected" not in st.session_state:
    st.session_state.selected = None

if "results" not in st.session_state:
    st.session_state.results = []

# ==========================================
# 함수
# ==========================================
def start_evaluation():
    st.session_state.page = "evaluation"
    st.session_state.current_group = 1
    st.session_state.selected = None
    st.session_state.results = []

def select_answer(answer):
    st.session_state.selected = answer

def save_and_next():
    group = st.session_state.current_group
    answer = st.session_state.selected
    reason = st.session_state.get(f"reason_{group}", "").strip()

    if answer is None or reason == "":
        return

    st.session_state.results.append({
        "group": group,
        "answer": answer,
        "reason": reason
    })

    st.session_state.selected = None

    if group < TOTAL_GROUPS:
        st.session_state.current_group += 1
    else:
        st.session_state.page = "complete"

# ==========================================
# 시작 화면
# ==========================================
if st.session_state.page == "home":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    st.markdown('<div class="title-main">🚦 AI 신호등 평가</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle-main">우리의 인공지능 서비스,<br>사용해도 괜찮을까요?</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="guide-box">
        🟢 <b>가능</b> : 인공지능 서비스를 바로 사용할 의사가 있어요.<br>
        🟡 <b>제한</b> : 조건 또는 보완이 이루어진다면 사용할 의사가 있어요.<br>
        🔴 <b>금지</b> : 인공지능 서비스를 사용할 의사가 없어요.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="small-note">1조부터 4조까지 순서대로 평가해 주세요.<br>평가를 선택하고 이유를 작성해야 다음 조로 넘어갈 수 있어요.</div>',
        unsafe_allow_html=True
    )

    st.write("")
    if st.button("🌷 평가 시작하기", key="start_button", use_container_width=True):
        start_evaluation()
        st.rerun()

    st.write("")
    st.button(
        "🧸 교사용 결과 확인 (준비 중)",
        key="teacher_button",
        disabled=True,
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 평가 화면
# ==========================================
elif st.session_state.page == "evaluation":
    group = st.session_state.current_group
    selected = st.session_state.selected

    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    st.markdown('<div class="title-main">🚦 AI 신호등 평가</div>', unsafe_allow_html=True)
    st.progress((group - 1) / TOTAL_GROUPS, text=f"평가 진행 : {group} / {TOTAL_GROUPS}")

    st.markdown(f'<div class="section-title">{group}조 평가하기</div>', unsafe_allow_html=True)
    st.markdown('<div class="question-text">이 인공지능 서비스를 사용하시겠습니까?</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="small")

    with col1:
        st.button(
            "🟢 가능",
            key="green_btn",
            use_container_width=True,
            on_click=select_answer,
            args=("가능",)
        )

    with col2:
        st.button(
            "🟡 제한",
            key="yellow_btn",
            use_container_width=True,
            on_click=select_answer,
            args=("제한",)
        )

    with col3:
        st.button(
            "🔴 금지",
            key="red_btn",
            use_container_width=True,
            on_click=select_answer,
            args=("금지",)
        )

    st.write("")

    if selected is not None:
        emoji_map = {"가능": "🟢", "제한": "🟡", "금지": "🔴"}
        st.markdown(
            f"""
            <div class="result-box">
                <b>{emoji_map[selected]} 선택한 평가 : {selected}</b><br>
                {CRITERIA[selected]}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("세 가지 버튼 중 하나를 먼저 선택해 주세요.")

    st.write("")

    reason = st.text_area(
        "📝 그렇게 평가한 이유를 작성해 주세요. (100자 이내)",
        placeholder="예) 개인정보 보호 대책이 충분하지 않아서 바로 사용하기는 어려워요.",
        max_chars=100,
        height=140,
        key=f"reason_{group}"
    )

    can_next = (selected is not None) and (len(reason.strip()) > 0)

    if group < TOTAL_GROUPS:
        next_text = f"다음 : {group + 1}조 평가하기 →"
    else:
        next_text = "💌 모든 평가 제출하기"

    st.write("")
    st.button(
        next_text,
        key="next_button",
        type="secondary",
        disabled=not can_next,
        use_container_width=True,
        on_click=save_and_next
    )

    if not can_next:
        st.markdown(
            '<div class="small-note">평가 선택과 이유 작성을 완료해야 다음 단계로 이동할 수 있어요.</div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 완료 화면
# ==========================================
elif st.session_state.page == "complete":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    st.markdown('<div class="title-main">🎉 평가 완료!</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle-main">1조부터 4조까지 모든 평가를 완료했어요.<br>신중하게 평가해 주셔서 고마워요!</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-title">📋 나의 평가 결과</div>', unsafe_allow_html=True)

    emoji_map = {"가능": "🟢", "제한": "🟡", "금지": "🔴"}

    for result in st.session_state.results:
        st.markdown(
            f"""
            <div class="complete-box">
                <b>{result["group"]}조 : {emoji_map[result["answer"]]} {result["answer"]}</b><br>
                <div style="margin-top:8px; color:#6b6470;">{result["reason"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    st.caption("현재 버전은 결과가 서버에 저장되지 않고, 접속한 화면에서만 임시로 유지됩니다.")

    st.write("")
    if st.button("🏠 처음으로 돌아가기", key="home_button", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.current_group = 1
        st.session_state.selected = None
        st.session_state.results = []
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
