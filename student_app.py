
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
# 2. 세션 상태
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
# 3. 디자인 - Pretendard
# ==========================================

st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

/* 전체 폰트 */
html, body, p, button, textarea, input,
h1, h2, h3, label, span,
[data-testid="stAppViewContainer"],
[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"] {
    font-family: 'Pretendard', sans-serif !important;
}

/* 전체 배경 */
.stApp {
    background: linear-gradient(
        180deg,
        #fff8fc 0%,
        #f7faff 100%
    );
}

/* 화면 너비 */
.block-container {
    max-width: 700px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* 메인 제목 */
.main-title {
    text-align: center;
    font-size: 2.4rem;
    font-weight: 800;
    color: #594968;
    margin: 20px 0;
    letter-spacing: -0.7px;
}

/* 부제목 */
.subtitle {
    text-align: center;
    font-size: 1.15rem;
    font-weight: 600;
    color: #75677f;
    line-height: 1.9;
    margin-bottom: 25px;
}

/* 조별 제목 */
.group-title {
    text-align: center;
    font-size: 2.1rem;
    font-weight: 800;
    color: #594968;
    margin: 30px 0 12px;
    letter-spacing: -0.5px;
}

/* 평가 질문 */
.question {
    text-align: center;
    color: #615568;
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 28px;
}

/* 평가 기준 안내 */
.guide-box {
    background: #fff2f8;
    border: 2px dashed #efc2d9;
    padding: 24px;
    border-radius: 22px;
    line-height: 2.4;
    color: #62536c;
    margin: 25px 0;
    font-size: 1.08rem;
    font-weight: 600;
}

/* 버튼 공통 */
div.stButton > button {
    font-family: 'Pretendard', sans-serif !important;
    width: 100%;
    border-radius: 18px;
    font-weight: 800 !important;
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
    min-height: 65px;
    font-size: 19px !important;
}

/* 신호등 버튼 공통 */
.st-key-green_btn button,
.st-key-yellow_btn button,
.st-key-red_btn button {
    height: 95px !important;
    min-height: 95px !important;
    font-size: 23px !important;
    font-weight: 800 !important;
    border-radius: 22px !important;
    white-space: normal !important;
}

/* 가능 */
.st-key-green_btn button {
    background: #baf3cb !important;
    color: #275c3e !important;
    border: 3px solid #9be5b0 !important;
}

/* 제한 */
.st-key-yellow_btn button {
    background: #ffedac !important;
    color: #73591c !important;
    border: 3px solid #ffdc83 !important;
}

/* 금지 */
.st-key-red_btn button {
    background: #ffc6cb !important;
    color: #783747 !important;
    border: 3px solid #ffa9b2 !important;
}

/* 다음 및 처음 버튼 */
.st-key-next_button button,
.st-key-home_button button {
    background: #ded8ff !important;
    color: #51467d !important;
    border: 2px solid #c8c0f6 !important;
    min-height: 65px;
    font-size: 19px !important;
}

/* 비활성화 */
.st-key-next_button button:disabled {
    background: #f0edf5 !important;
    color: #aaa3b5 !important;
    border: 2px solid #e7e1ec !important;
    opacity: 1 !important;
}

/* 입력창 제목 */
.stTextArea label,
[data-testid="stWidgetLabel"] {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: #5d506b !important;
}

/* 이유 입력창 */
.stTextArea textarea {
    font-family: 'Pretendard', sans-serif !important;
    background: #ffffff !important;
    border: 2px solid #e7d9ed !important;
    border-radius: 18px !important;
    color: #51475a !important;
    font-size: 17px !important;
    font-weight: 500 !important;
    line-height: 1.7 !important;
    padding: 15px !important;
}

.stTextArea textarea:focus {
    border-color: #c8b6e8 !important;
    box-shadow: 0 0 0 2px #eee5fb !important;
}

/* 평가 선택 안내 */
.info-box {
    background: #f2f0ff;
    border: 2px solid #ddd5fa;
    color: #5c5178;
    padding: 19px;
    border-radius: 18px;
    text-align: center;
    line-height: 1.9;
    margin: 23px 0;
    font-size: 1.12rem;
    font-weight: 600;
}

.info-box b {
    font-weight: 800;
}

/* 완료 화면 */
.result-card {
    background: #fff2f8;
    border: 2px solid #f3d2e4;
    padding: 20px;
    border-radius: 18px;
    margin: 15px 0;
    color: #62536c;
    line-height: 1.9;
    font-size: 1.05rem;
    font-weight: 500;
    overflow-wrap: anywhere;
}

.result-card b {
    font-weight: 800;
}

/* 안내 문구 */
.small-note {
    text-align: center;
    color: #82758d;
    font-size: 15px;
    font-weight: 600;
    line-height: 1.9;
    margin-top: 17px;
}

/* 진행 표시 */
div[data-testid="stProgress"] {
    margin-top: 20px;
    font-weight: 600;
}

/* 모바일 화면 */
@media (max-width: 500px) {
    .main-title {
        font-size: 1.9rem;
    }

    .group-title {
        font-size: 1.8rem;
    }

    .question {
        font-size: 1.05rem;
    }

    .guide-box {
        padding: 18px;
        font-size: 0.95rem;
    }

    .st-key-green_btn button,
    .st-key-yellow_btn button,
    .st-key-red_btn button {
        height: 85px !important;
        min-height: 85px !important;
        font-size: 17px !important;
        padding: 5px !important;
    }

    .info-box {
        font-size: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. Google Sheets 일괄 전송
# ==========================================

def send_all_evaluations(results):
    """네 조의 평가를 한 번에 전송"""

    payload = {
        "action": "save_all",
        "participant_id": st.session_state.participant_id,
        "results": results
    }

    response = requests.post(
        st.secrets["apps_script_url"],
        json=payload,
        timeout=(4, 15),
        allow_redirects=True
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(
            data.get("message", "저장에 실패했습니다.")
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

    st.session_state.participant_id = uuid.uuid4().hex

    for i in range(1, TOTAL_GROUPS + 1):
        st.session_state.pop(
            f"reason_{i}", None
        )


def select_answer(answer):
    """신호등 선택"""

    st.session_state.selected = answer
    st.session_state.save_error = ""


def save_and_next():
    """1~3조 임시 저장, 4조에서 일괄 제출"""

    group = st.session_state.current_group
    answer = st.session_state.selected

    reason = st.session_state.get(
        f"reason_{group}", ""
    ).strip()

    if answer not in CRITERIA or not reason:
        st.session_state.save_error = (
            "평가를 선택하고 이유를 작성해 주세요."
        )
        return False

    current_result = {
        "group": group,
        "answer": answer,
        "reason": reason
    }

    # 1~3조: 임시 저장 후 즉시 이동
    if group < TOTAL_GROUPS:

        st.session_state.results.append(
            current_result
        )

        st.session_state.current_group += 1
        st.session_state.selected = None
        st.session_state.save_error = ""

        return True

    # 4조: 네 개의 평가를 한 번에 전송
    all_results = (
        st.session_state.results + [current_result]
    )

    if len(all_results) != TOTAL_GROUPS:
        st.session_state.save_error = (
            "평가 결과를 확인해 주세요."
        )
        return False

    try:
        send_all_evaluations(all_results)

    except Exception:
        st.session_state.save_error = (
            "평가 결과를 전송하지 못했어요. "
            "잠시 후 다시 제출해 주세요."
        )
        return False

    # 전송 성공
    st.session_state.results = all_results
    st.session_state.selected = None
    st.session_state.save_error = ""
    st.session_state.page = "complete"

    return True


def go_home():
    """시작 화면 이동"""

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

    # 신호등 선택 버튼
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

    # 선택한 평가 강조
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

    # 평가 이유 작성
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

    # 평가 버튼과 이유 모두 필수
    can_next = (
        st.session_state.selected is not None
        and bool(reason.strip())
    )

    st.write("")

    if group < TOTAL_GROUPS:
        next_text = f"다음 : {group + 1}조 평가하기 →"
    else:
        next_text = "💌 모든 평가 제출하기"

    if st.button(
        next_text,
        key="next_button",
        use_container_width=True,
        disabled=not can_next
    ):

        # 마지막 조에서만 Google Sheets 전송
        if group == TOTAL_GROUPS:

            with st.spinner(
                "🌷 모든 평가 결과를 제출하고 있어요..."
            ):
                success = save_and_next()

        else:
            success = save_and_next()

        if success:
            st.rerun()

    # 오류 메시지
    if st.session_state.save_error:
        st.error(st.session_state.save_error)

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
