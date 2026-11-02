
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

# 분반 설정
# label만 변경하면 화면에 표시되는 이름이 바뀜
CLASSES = {
    "A": {
        "label": "205",
        "groups": 4
    },
    "B": {
        "label": "206",
        "groups": 5
    }
}

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

# 시작 화면에서 선택한 분반
if "selected_class" not in st.session_state:
    st.session_state.selected_class = None

# 실제 평가에 사용할 분반
if "active_class" not in st.session_state:
    st.session_state.active_class = None

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
# 3. 디자인
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Jua&display=swap');

/* 기본 글씨체 */
html, body, p, button, textarea, input,
h1, h2, h3, label, span,
[data-testid="stAppViewContainer"],
[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"] {
    font-family: 'Gowun Dodum', sans-serif !important;
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
    font-family: 'Jua', sans-serif !important;
    text-align: center;
    font-size: 2.6rem;
    color: #594968;
    margin: 20px 0;
}

/* 조별 제목 */
.group-title {
    font-family: 'Jua', sans-serif !important;
    text-align: center;
    font-size: 2.3rem;
    color: #594968;
    margin: 30px 0 12px;
}

/* 부제목 */
.subtitle {
    text-align: center;
    font-size: 1.15rem;
    color: #75677f;
    line-height: 1.9;
    margin-bottom: 25px;
}

/* 평가 질문 */
.question {
    text-align: center;
    color: #615568;
    font-size: 1.2rem;
    margin-bottom: 28px;
}

/* 평가 기준 */
.guide-box {
    background: #fff2f8;
    border: 2px dashed #efc2d9;
    padding: 24px;
    border-radius: 22px;
    line-height: 2.4;
    color: #62536c;
    margin: 25px 0;
    font-size: 1.08rem;
}

/* 버튼 공통 */
div.stButton > button {
    font-family: 'Gowun Dodum', sans-serif !important;
    width: 100%;
    border-radius: 18px;
    font-weight: 700 !important;
    transition: all 0.15s ease;
}

div.stButton > button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
}

/* ========================================
   분반 선택 버튼
======================================== */

.st-key-class_a_btn button,
.st-key-class_b_btn button {
    height: 110px !important;
    min-height: 110px !important;
    border-radius: 24px !important;
}

/* 분반 버튼 내부 글씨 */
.st-key-class_a_btn button p,
.st-key-class_b_btn button p {
    font-family: 'Gowun Dodum', sans-serif !important;
    font-size: 27px !important;
    font-weight: 700 !important;
    line-height: 1.4 !important;
}

/* A분반: 하늘색 */
.st-key-class_a_btn button {
    background-color: #dcecfb !important;
    color: #4d6684 !important;
    border: 3px solid #bad4f2 !important;
}

.st-key-class_a_btn button p {
    color: #4d6684 !important;
}

/* B분반: 분홍색 */
.st-key-class_b_btn button {
    background-color: #fbe0ec !important;
    color: #855c75 !important;
    border: 3px solid #f1bbd3 !important;
}

.st-key-class_b_btn button p {
    color: #855c75 !important;
}

/* 선택된 분반 버튼 강조 */
.st-key-class_a_btn.selected button,
.st-key-class_b_btn.selected button {
    outline: 4px solid #9b83bf !important;
    outline-offset: 2px !important;
    box-shadow: 0 5px 15px rgba(120, 90, 150, 0.15);
}

/* 선택한 분반 안내 */
.class-info {
    background: #f2f0ff;
    border: 2px solid #ddd5fa;
    color: #5c5178;
    padding: 18px;
    border-radius: 18px;
    text-align: center;
    font-size: 1.12rem;
    line-height: 1.8;
    margin: 20px 0;
}

/* ========================================
   시작 버튼
======================================== */

.st-key-start_button button {
    background-color: #ffd8e8 !important;
    color: #754f67 !important;
    border: 2px solid #f4bbd4 !important;
    min-height: 65px;
}

.st-key-start_button button p {
    font-size: 22px !important;
    font-weight: 700 !important;
}

/* ========================================
   신호등 버튼
======================================== */

.st-key-green_btn button,
.st-key-yellow_btn button,
.st-key-red_btn button {
    height: 95px !important;
    min-height: 95px !important;
    border-radius: 22px !important;
    white-space: normal !important;
}

/* 버튼 내부 글씨 30px */
.st-key-green_btn button p,
.st-key-yellow_btn button p,
.st-key-red_btn button p {
    font-family: 'Gowun Dodum', sans-serif !important;
    font-size: 30px !important;
    font-weight: 700 !important;
    line-height: 1.3 !important;
}

/* 가능 */
.st-key-green_btn button {
    background-color: #baf3cb !important;
    color: #275c3e !important;
    border: 3px solid #9be5b0 !important;
}

.st-key-green_btn button p {
    color: #275c3e !important;
}

/* 제한 */
.st-key-yellow_btn button {
    background-color: #ffedac !important;
    color: #73591c !important;
    border: 3px solid #ffdc83 !important;
}

.st-key-yellow_btn button p {
    color: #73591c !important;
}

/* 금지 */
.st-key-red_btn button {
    background-color: #ffc6cb !important;
    color: #783747 !important;
    border: 3px solid #ffa9b2 !important;
}

.st-key-red_btn button p {
    color: #783747 !important;
}

/* 선택한 신호등 버튼 강조 */
.st-key-green_btn.selected button,
.st-key-yellow_btn.selected button,
.st-key-red_btn.selected button {
    outline: 4px solid #82718d !important;
    outline-offset: 3px !important;
    box-shadow: 0 5px 15px rgba(90, 70, 110, 0.15);
}

/* ========================================
   다음 버튼
======================================== */

.st-key-next_button button,
.st-key-home_button button {
    background-color: #ded8ff !important;
    color: #51467d !important;
    border: 2px solid #c8c0f6 !important;
    min-height: 65px;
}

.st-key-next_button button p,
.st-key-home_button button p {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #51467d !important;
}

/* 비활성화 버튼 */
.st-key-next_button button:disabled,
.st-key-start_button button:disabled {
    background-color: #f0edf5 !important;
    color: #aaa3b5 !important;
    border: 2px solid #e7e1ec !important;
    opacity: 1 !important;
}

.st-key-next_button button:disabled p,
.st-key-start_button button:disabled p {
    color: #aaa3b5 !important;
}

/* ========================================
   입력창
======================================== */

.stTextArea label,
[data-testid="stWidgetLabel"] {
    font-size: 1.1rem !important;
    color: #5d506b !important;
}

.stTextArea textarea {
    font-family: 'Gowun Dodum', sans-serif !important;
    background: #ffffff !important;
    border: 2px solid #e7d9ed !important;
    border-radius: 18px !important;
    color: #51475a !important;
    font-size: 17px !important;
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
}

/* 평가 완료 결과 */
.result-card {
    background: #fff2f8;
    border: 2px solid #f3d2e4;
    padding: 20px;
    border-radius: 18px;
    margin: 15px 0;
    color: #62536c;
    line-height: 1.9;
    font-size: 1.05rem;
    overflow-wrap: anywhere;
}

/* 작은 안내 */
.small-note {
    text-align: center;
    color: #82758d;
    font-size: 15px;
    line-height: 1.9;
    margin-top: 17px;
}

/* 모바일 */
@media (max-width: 500px) {

    .main-title {
        font-size: 2.1rem;
    }

    .group-title {
        font-size: 1.9rem;
    }

    .question {
        font-size: 1.05rem;
    }

    .guide-box {
        padding: 18px;
        font-size: 0.95rem;
    }

    .st-key-class_a_btn button,
    .st-key-class_b_btn button {
        height: 95px !important;
        min-height: 95px !important;
    }

    .st-key-class_a_btn button p,
    .st-key-class_b_btn button p {
        font-size: 20px !important;
    }

    .st-key-green_btn button,
    .st-key-yellow_btn button,
    .st-key-red_btn button {
        height: 85px !important;
        min-height: 85px !important;
        padding: 5px !important;
    }

    .st-key-green_btn button p,
    .st-key-yellow_btn button p,
    .st-key-red_btn button p {
        font-size: 22px !important;
    }

    .info-box {
        font-size: 1rem;
    }

    .st-key-start_button button p,
    .st-key-next_button button p,
    .st-key-home_button button p {
        font-size: 19px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 기능 함수
# ==========================================

def choose_class(class_id):
    """시작 화면에서 분반 선택"""

    st.session_state.selected_class = class_id


def start_evaluation():
    """선택된 분반으로 평가 시작"""

    class_id = st.session_state.selected_class

    if class_id not in CLASSES:
        return

    # 선택한 분반을 실제 평가 분반으로 확정
    st.session_state.active_class = class_id

    st.session_state.page = "evaluation"
    st.session_state.current_group = 1
    st.session_state.selected = None
    st.session_state.results = []
    st.session_state.save_error = ""

    st.session_state.participant_id = uuid.uuid4().hex

    # 기존 입력값 초기화
    for i in range(1, 6):
        st.session_state.pop(
            f"reason_{i}", None
        )


def select_answer(answer):
    """신호등 선택"""

    st.session_state.selected = answer
    st.session_state.save_error = ""


def send_all_evaluations(results):
    """선택한 분반의 평가 결과 일괄 전송"""

    class_id = st.session_state.active_class

    payload = {
        "action": "save_all",
        "class_id": class_id,
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
            data.get(
                "message",
                "평가 결과 저장에 실패했습니다."
            )
        )


def save_and_next():
    """다음 조로 이동하거나 최종 제출"""

    class_id = st.session_state.active_class

    if class_id not in CLASSES:
        st.session_state.save_error = (
            "분반 정보가 올바르지 않습니다."
        )
        return False

    total_groups = CLASSES[class_id]["groups"]

    group = st.session_state.current_group
    answer = st.session_state.selected

    reason = st.session_state.get(
        f"reason_{group}", ""
    ).strip()

    # 입력 확인
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

    # 마지막 조 이전에는 임시 저장
    if group < total_groups:

        st.session_state.results.append(
            current_result
        )

        st.session_state.current_group += 1
        st.session_state.selected = None
        st.session_state.save_error = ""

        return True

    # 마지막 조에서 한 번에 전송
    all_results = (
        st.session_state.results + [current_result]
    )

    if len(all_results) != total_groups:
        st.session_state.save_error = (
            "평가 결과를 확인해 주세요."
        )
        return False

    try:
        send_all_evaluations(all_results)

    except Exception:
        st.session_state.save_error = (
            "평가 결과를 전송하지 못했어요. "
            "다시 제출해 주세요."
        )
        return False

    # 저장 성공
    st.session_state.results = all_results
    st.session_state.selected = None
    st.session_state.save_error = ""
    st.session_state.page = "complete"

    return True


def go_home():
    """처음으로 돌아가기"""

    st.session_state.page = "home"
    st.session_state.selected_class = None
    st.session_state.active_class = None
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
# 5. 시작 화면
# ==========================================

if st.session_state.page == "home":

    title("🚦 AI 신호등 평가")

    st.markdown("""
    <div class="subtitle">
        우리의 인공지능 서비스,<br>
        사용해도 괜찮을까요? 🌷
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------
    # 분반 선택
    # --------------------------------------

    st.markdown(
        '<div class="group-title">'
        '🌼 분반 선택하기'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="question">
        자신이 속한 분반을 선택해 주세요.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:

        st.button(
            f"🌼 {CLASSES['A']['label']}",
            key="class_a_btn",
            use_container_width=True,
            on_click=choose_class,
            args=("A",)
        )

    with col2:

        st.button(
            f"🌸 {CLASSES['B']['label']}",
            key="class_b_btn",
            use_container_width=True,
            on_click=choose_class,
            args=("B",)
        )

    # 선택한 버튼 강조
    selected_class = st.session_state.selected_class

    if selected_class in CLASSES:

        button_key = (
            "class_a_btn"
            if selected_class == "A"
            else "class_b_btn"
        )

        st.markdown(
            f"""
            <style>
            .st-key-{button_key} button {{
                outline: 4px solid #9b83bf !important;
                outline-offset: 2px !important;
                box-shadow: 0 5px 15px
                    rgba(120, 90, 150, 0.15);
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

        label = CLASSES[selected_class]["label"]
        total = CLASSES[selected_class]["groups"]

        st.markdown(
            f"""
            <div class="class-info">
                💜 <b>{label} 선택 완료!</b><br>
                1조부터 {total}조까지 평가합니다.
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown("""
        <div class="class-info">
            🌷 평가할 분반을 선택해 주세요.
        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------
    # 신호등 평가 안내
    # --------------------------------------

    st.markdown("""
    <div class="guide-box">
        🟢 <b>가능</b> : 바로 사용할 의사가 있어요.<br>
        🟡 <b>제한</b> : 조건이나 보완이 이루어진다면 사용할 의사가 있어요.<br>
        🔴 <b>금지</b> : 사용할 의사가 없어요.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="small-note">
        평가를 선택하고 이유를 작성해야<br>
        다음 조로 넘어갈 수 있어요.
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.button(
        "🌷 평가 시작하기",
        key="start_button",
        use_container_width=True,
        disabled=selected_class not in CLASSES,
        on_click=start_evaluation
    )

# ==========================================
# 6. 평가 화면
# ==========================================

elif st.session_state.page == "evaluation":

    class_id = st.session_state.active_class

    # 잘못된 분반 정보인 경우 시작 화면으로
    if class_id not in CLASSES:
        go_home()
        st.rerun()

    total_groups = CLASSES[class_id]["groups"]
    class_label = CLASSES[class_id]["label"]
    group = st.session_state.current_group

    title("🚦 AI 신호등 평가")

    # 분반 정보 표시
    st.markdown(
        f"""
        <div class="class-info">
            💜 {class_label} · 총 {total_groups}개 조
        </div>
        """,
        unsafe_allow_html=True
    )

    # 진행 상황
    st.progress(
        (group - 1) / total_groups,
        text=f"평가 진행 : {group} / {total_groups}"
    )

    st.markdown(
        f"""
        <div class="group-title">
            🌼 {group}조 평가하기
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="question">
        이 인공지능 서비스를 사용하시겠습니까?
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------
    # 신호등 선택
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

    selected = st.session_state.selected

    # 선택한 버튼 강조
    if selected in CRITERIA:

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
                    rgba(90, 70, 110, 0.15);
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="info-box">
                <b>
                    {EMOJI[selected]}
                    선택한 평가 : {selected}
                </b><br>
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
    # 평가 이유
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

    can_next = (
        selected in CRITERIA
        and bool(reason.strip())
    )

    st.write("")

    # --------------------------------------
    # 다음 조 이동 또는 최종 제출
    # --------------------------------------

    if group < total_groups:
        next_text = (
            f"다음 : {group + 1}조 평가하기 →"
        )
    else:
        next_text = "💌 모든 평가 제출하기"

    if st.button(
        next_text,
        key="next_button",
        use_container_width=True,
        disabled=not can_next
    ):

        if group == total_groups:

            with st.spinner(
                "🌷 모든 평가 결과를 제출하고 있어요..."
            ):
                success = save_and_next()

        else:
            success = save_and_next()

        if success:
            st.rerun()

    # 오류 안내
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
# 7. 평가 완료 화면
# ==========================================

elif st.session_state.page == "complete":

    class_id = st.session_state.active_class

    title("🎉 평가 완료!")

    if class_id in CLASSES:

        label = CLASSES[class_id]["label"]

        st.markdown(
            f"""
            <div class="class-info">
                💜 {label} 평가 완료
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("""
    <div class="subtitle">
        모든 평가 결과가 제출되었어요!<br>
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
                <b>
                    {group}조 :
                    {EMOJI[answer]} {answer}
                </b>
                <div style="margin-top:10px;">
                    {reason}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("""
    <div class="small-note">
        평가 결과가 Google Sheets에 저장되었어요.<br>
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
