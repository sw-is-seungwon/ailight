
import streamlit as st
import requests
import uuid
from html import escape

# ==========================================
# 1. 기본 설정
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
    "금지": "인공지능 서비스를 사용할 의사가 없어요."
}

EMOJI = {
    "가능": "🟢",
    "제한": "🟡",
    "금지": "🔴"
}

# ==========================================
# 2. 세션 상태 초기화
# ==========================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "current_group" not in st.session_state:
    st.session_state.current_group = 1

if "selected" not in st.session_state:
    st.session_state.selected = None

if "results" not in st.session_state:
    st.session_state.results = []

if "participant_id" not in st.session_state:
    st.session_state.participant_id = uuid.uuid4().hex

if "save_error" not in st.session_state:
    st.session_state.save_error = ""

# ==========================================
# 3. 파스텔톤 디자인
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

html, body, p, button, textarea,
div[data-testid="stAppViewContainer"],
div[data-testid="stWidgetLabel"],
div[data-testid="stMarkdownContainer"] {
    font-family: 'Gowun Dodum', sans-serif !important;
}

.stApp {
    background: linear-gradient(
        180deg,
        #fff8fc 0%,
        #f7faff 100%
    );
}

.block-container {
    max-width: 700px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* 제목 */
.main-title {
    text-align: center;
    font-size: 2.3rem;
    font-weight: bold;
    color: #65536d;
    margin: 15px 0;
}

.subtitle {
    text-align: center;
    font-size: 1.1rem;
    color: #85758e;
    line-height: 1.9;
    margin-bottom: 25px;
}

.group-title {
    text-align: center;
    font-size: 2rem;
    font-weight: bold;
    color: #65536d;
    margin: 25px 0 10px;
}

.question {
    text-align: center;
    color: #87778f;
    font-size: 1.1rem;
    margin-bottom: 25px;
}

/* 시작 화면의 안내 */
.guide-box {
    background: #fff2f8;
    border: 2px dashed #efc2d9;
    padding: 24px;
    border-radius: 22px;
    line-height: 2.3;
    color: #67586e;
    margin: 25px 0;
}

/* 모든 버튼의 기본 디자인 */
div.stButton > button {
    font-family: 'Gowun Dodum', sans-serif !important;
    width: 100%;
    border-radius: 18px;
    font-weight: bold;
    transition: all 0.15s ease;
}

div.stButton > button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
}

/* 시작 버튼 */
.st-key-start_button button {
    background: #ffd8e8 !important;
    color: #754f67 !important;
    border: 2px solid #f4bbd4 !important;
    min-height: 60px;
    font-size: 19px;
}

/* 신호등 버튼 크기 */
.st-key-green_btn button,
.st-key-yellow_btn button,
.st-key-red_btn button {
    height: 95px !important;
    min-height: 95px !important;
    font-size: 23px !important;
    border-radius: 22px !important;
    white-space: normal !important;
}

/* 가능 - 파스텔 민트 */
.st-key-green_btn button {
    background: #baf3cb !important;
    color: #316747 !important;
    border: 3px solid #9be5b0 !important;
}

/* 제한 - 파스텔 노랑 */
.st-key-yellow_btn button {
    background: #ffedac !important;
    color: #806123 !important;
    border: 3px solid #ffdc83 !important;
}

/* 금지 - 파스텔 분홍 */
.st-key-red_btn button {
    background: #ffc6cb !important;
    color: #873f49 !important;
    border: 3px solid #ffa9b2 !important;
}

/* 다음 및 처음 버튼 */
.st-key-next_button button,
.st-key-home_button button {
    background: #ded8ff !important;
    color: #5c548b !important;
    border: 2px solid #c8c0f6 !important;
    min-height: 60px;
    font-size: 19px;
}

/* 다음 버튼 비활성화 */
.st-key-next_button button:disabled {
    background: #f0edf5 !important;
    color: #aaa3b5 !important;
    border: 2px solid #e7e1ec !important;
    opacity: 1 !important;
}

/* 이유 작성 칸 */
.stTextArea textarea {
    font-family: 'Gowun Dodum', sans-serif !important;
    background: #ffffff !important;
    border: 2px solid #e7d9ed !important;
    border-radius: 18px !important;
    color: #554b60 !important;
    font-size: 17px !important;
}

.stTextArea textarea:focus {
    border-color: #c8b6e8 !important;
    box-shadow: 0 0 0 2px #eee5fb !important;
}

/* 선택 안내 */
.info-box {
    background: #f2f0ff;
    border: 2px solid #ddd5fa;
    color: #635a7e;
    padding: 18px;
    border-radius: 16px;
    text-align: center;
    line-height: 1.8;
    margin: 20px 0;
}

/* 완료 화면 결과 */
.result-card {
    background: #fff2f8;
    border: 2px solid #f3d2e4;
    padding: 20px;
    border-radius: 18px;
    margin: 15px 0;
    color: #67586d;
    line-height: 1.8;
    overflow-wrap: anywhere;
}

.small-note {
    text-align: center;
    color: #998c9e;
    font-size: 14px;
    line-height: 1.8;
    margin-top: 15px;
}

div[data-testid="stProgress"] {
    margin-top: 20px;
}

/* 스마트폰 화면 */
@media (max-width: 500px) {
    .main-title {
        font-size: 1.8rem;
    }

    .group-title {
        font-size: 1.6rem;
    }

    .st-key-green_btn button,
    .st-key-yellow_btn button,
    .st-key-red_btn button {
        font-size: 17px !important;
        height: 85px !important;
        min-height: 85px !important;
        padding: 5px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. Google Sheets 전송
# ==========================================

def send_evaluation(group, answer, reason):
    """Apps Script를 통해 평가 결과 저장"""

    payload = {
        "action": "save",
        "participant_id": st.session_state.participant_id,
        "group": group,
        "answer": answer,
        "reason": reason
    }

    response = requests.post(
        st.secrets["apps_script_url"],
        json=payload,
        timeout=(4, 12),
        allow_redirects=True
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(
            result.get("message", "저장 실패")
        )

# ==========================================
# 5. 기능 함수
# ==========================================

def start_evaluation():
    """평가 시작"""

    st.session_state.page = "evaluation"
    st.session_state.current_group = 1
    st.session_state.selected = None
    st.session_state.results = []
    st.session_state.save_error = ""

    # 학생별 임의 참여 ID
    st.session_state.participant_id = uuid.uuid4().hex

    # 이전 평가 이유 초기화
    for i in range(1, TOTAL_GROUPS + 1):
        st.session_state.pop(
            f"reason_{i}", None
        )


def select_answer(answer):
    """평가 버튼은 선택만 변경"""

    st.session_state.selected = answer
    st.session_state.save_error = ""


def save_and_next():
    """Google Sheets 저장 후 다음 조로 이동"""

    group = st.session_state.current_group
    answer = st.session_state.selected

    reason = st.session_state.get(
        f"reason_{group}", ""
    ).strip()

    # 선택과 이유가 모두 있어야 저장
    if answer not in CRITERIA or not reason:
        st.session_state.save_error = (
            "평가를 선택하고 이유를 작성해 주세요."
        )
        return False

    # Google Sheets로 전송
    try:
        send_evaluation(group, answer, reason)

    except Exception:
        st.session_state.save_error = (
            "평가 결과를 저장하지 못했어요. "
            "잠시 후 다시 시도해 주세요."
        )
        return False

    # 저장 성공
    st.session_state.save_error = ""

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

    return True


def go_home():
    """시작 화면으로 이동"""

    st.session_state.page = "home"
    st.session_state.current_group = 1
    st.session_state.selected = None
    st.session_state.results = []
    st.session_state.save_error = ""


def title(text):
    st.markdown(
        f'<div class="main-title">{text}</div>',
        unsafe_allow_html=True
    )

# ==========================================
# 6. 시작 화면
# ==========================================

if st.session_state.page == "home":

    title("🚦 AI 신호등 평가")

    st.markdown("""
    <div class="subtitle">
        우리의 인공지능 서비스,<br>
        사용해도 괜찮을까요? 🌷
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="guide-box">
        🟢 <b>가능</b> : 바로 사용할 의사가 있어요.<br>
        🟡 <b>제한</b> : 조건이나 보완이 이루어진다면 사용할 의사가 있어요.<br>
        🔴 <b>금지</b> : 사용할 의사가 없어요.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="small-note">
        1조부터 4조까지 차례대로 평가해 주세요.<br>
        평가를 선택하고 이유를 작성해야 다음으로 넘어갈 수 있어요.
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # 학생용에는 교사용 버튼 없음
    st.button(
        "🌷 평가 시작하기",
        key="start_button",
        use_container_width=True,
        on_click=start_evaluation
    )

# ==========================================
# 7. 평가 화면
# ==========================================

elif st.session_state.page == "evaluation":

    group = st.session_state.current_group

    title("🚦 AI 신호등 평가")

    st.progress(
        (group - 1) / TOTAL_GROUPS,
        text=f"평가 진행 : {group} / {TOTAL_GROUPS}"
    )

    st.markdown(
        f'<div class="group-title">🌼 {group}조 평가하기</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="question">
        이 인공지능 서비스를 사용하시겠습니까?
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------
    # 신호등 버튼
    # --------------------------------------

    col1, col2, col3 = st.columns(
        3, gap="small"
    )

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

    # --------------------------------------
    # 현재 선택한 평가 표시
    # --------------------------------------

    selected = st.session_state.selected

    if selected is not None:

        button_key = {
            "가능": "green_btn",
            "제한": "yellow_btn",
            "금지": "red_btn"
        }[selected]

        st.markdown(
            f"""
            <style>
            .st-key-{button_key} button {{
                outline: 4px solid #82718d !important;
                outline-offset: 3px !important;
                box-shadow: 0 5px 15px
                    rgba(90,70,110,0.15);
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="info-box">
                <b>{EMOJI[selected]} 선택한 평가 : {selected}</b><br>
                {CRITERIA[selected]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.markdown("""
        <div class="info-box">
            🍀 세 가지 신호등 중 하나를 선택해 주세요!
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # --------------------------------------
    # 평가 이유 작성
    # --------------------------------------

    reason = st.text_area(
        "📝 그렇게 평가한 이유를 작성해 주세요.",
        placeholder=(
            "예) 개인정보 보호를 위한 대책이 부족해서 "
            "바로 사용하기 어려울 것 같아요."
        ),
        max_chars=100,
        height=145,
        key=f"reason_{group}"
    )

    # 이유를 먼저 작성하거나
    # 버튼을 먼저 선택해도 정상 동작
    can_next = (
        st.session_state.selected is not None
        and bool(reason.strip())
    )

    st.write("")

    if group < TOTAL_GROUPS:
        next_text = f"다음 : {group + 1}조 평가하기 →"
    else:
        next_text = "💌 모든 평가 제출하기"

    # --------------------------------------
    # 다음 조 버튼 (수정)
    # --------------------------------------

    if st.button(
        next_text,
        key="next_button",
        use_container_width=True,
        disabled=not can_next
    ):

        with st.spinner(
            "🌷 평가 결과를 저장하고 있어요..."
        ):
            success = save_and_next()

        # 저장 성공 시에만 화면 전환
        if success:
            st.rerun()

    # 저장 실패 시 메시지 표시
    if st.session_state.save_error:
        st.error(
            st.session_state.save_error
        )

    if not can_next:
        st.markdown("""
        <div class="small-note">
            🌸 평가 선택과 이유 작성을 완료하면<br>
            다음 조로 넘어갈 수 있어요.
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 8. 평가 완료 화면
# ==========================================

elif st.session_state.page == "complete":

    title("🎉 평가 완료!")

    st.markdown("""
    <div class="subtitle">
        1조부터 4조까지 모든 평가를 완료했어요!<br>
        신중하게 평가해 주셔서 고마워요. 💗
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📋 나의 평가 결과")

    for result in st.session_state.results:

        group = result["group"]
        answer = result["answer"]

        reason = escape(
            result["reason"]
        ).replace("\n", "<br>")

        st.markdown(
            f"""
            <div class="result-card">
                <b>{group}조 : {EMOJI[answer]} {answer}</b>
                <div style="margin-top:10px;">
                    {reason}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("""
    <div class="small-note">
        평가 결과가 제출되었어요.<br>
        결과를 확인한 뒤 화면을 닫아 주세요.
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.button(
        "🏠 처음으로 돌아가기",
        key="home_button",
        use_container_width=True,
        on_click=go_home
    )
