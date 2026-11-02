import uuid
from html import escape

import requests
import streamlit as st

st.set_page_config(page_title="AI 신호등 평가", page_icon="🚦", layout="centered")

CLASSES = {"A": {"label": "205", "groups": 4}, "B": {"label": "206", "groups": 5}}
CRITERIA = {
    "가능": "인공지능 서비스를 바로 사용할 의사가 있어요.",
    "제한": "조건 또는 보완이 이루어진다면 사용할 의사가 있어요.",
    "금지": "인공지능 서비스를 사용할 의사가 없어요.",
}
EMOJI = {"가능": "🟢", "제한": "🟡", "금지": "🔴"}

for key, default in {
    "page": "home", "selected_class": "A", "class_picker": "A", "current_group": 1,
    "selected": None, "results": [], "participant_id": None, "save_error": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Jua&display=swap');
html, body, p, button, textarea, input, label, span,
[data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"] {font-family:'Gowun Dodum',sans-serif !important;}
.stApp {background:linear-gradient(180deg,#fff8fc 0%,#f7faff 100%);}
.block-container {max-width:700px;padding-top:2rem;padding-bottom:3rem;}
.main-title {font-family:'Jua',sans-serif!important;text-align:center;font-size:2.6rem;color:#594968;margin:20px 0;}
.group-title {font-family:'Jua',sans-serif!important;text-align:center;font-size:2.3rem;color:#594968;margin:30px 0 12px;}
.subtitle {text-align:center;font-size:1.15rem;color:#75677f;line-height:1.9;margin-bottom:25px;}
.question {text-align:center;color:#615568;font-size:1.2rem;margin-bottom:28px;}
.guide-box {background:#fff2f8;border:2px dashed #efc2d9;padding:24px;border-radius:22px;line-height:2.4;color:#62536c;margin:25px 0;font-size:1.08rem;}
div.stButton>button {font-family:'Gowun Dodum',sans-serif!important;width:100%;border-radius:18px;transition:all .15s ease;}
div.stButton>button:hover:not(:disabled) {transform:translateY(-2px);box-shadow:0 5px 15px rgba(0,0,0,.08);}
.st-key-start_button button {background:#ffd8e8!important;color:#754f67!important;border:2px solid #f4bbd4!important;min-height:65px;}
.st-key-start_button button p {font-size:22px!important;font-weight:700!important;color:#754f67!important;}
.st-key-green_btn button,.st-key-yellow_btn button,.st-key-red_btn button {height:95px!important;min-height:95px!important;border-radius:22px!important;white-space:normal!important;}
.st-key-green_btn button p,.st-key-yellow_btn button p,.st-key-red_btn button p {font-family:'Gowun Dodum',sans-serif!important;font-size:30px!important;font-weight:700!important;line-height:1.3!important;}
.st-key-green_btn button {background-color:#baf3cb!important;color:#275c3e!important;border:3px solid #9be5b0!important;}
.st-key-yellow_btn button {background-color:#ffedac!important;color:#73591c!important;border:3px solid #ffdc83!important;}
.st-key-red_btn button {background-color:#ffc6cb!important;color:#783747!important;border:3px solid #ffa9b2!important;}
.st-key-green_btn button p {color:#275c3e!important;}
.st-key-yellow_btn button p {color:#73591c!important;}
.st-key-red_btn button p {color:#783747!important;}
.st-key-next_button button,.st-key-home_button button {background:#ded8ff!important;color:#51467d!important;border:2px solid #c8c0f6!important;min-height:65px;}
.st-key-next_button button p,.st-key-home_button button p {font-size:22px!important;font-weight:700!important;color:#51467d!important;}
.st-key-next_button button:disabled {background:#f0edf5!important;color:#aaa3b5!important;border:2px solid #e7e1ec!important;opacity:1!important;}
.st-key-next_button button:disabled p {color:#aaa3b5!important;}
.stTextArea label,[data-testid="stWidgetLabel"] {font-size:1.1rem!important;color:#5d506b!important;}
.stTextArea textarea {font-family:'Gowun Dodum',sans-serif!important;background:white!important;border:2px solid #e7d9ed!important;border-radius:18px!important;color:#51475a!important;font-size:17px!important;line-height:1.7!important;padding:15px!important;}
.stTextArea textarea:focus {border-color:#c8b6e8!important;box-shadow:0 0 0 2px #eee5fb!important;}
.info-box {background:#f2f0ff;border:2px solid #ddd5fa;color:#5c5178;padding:19px;border-radius:18px;text-align:center;line-height:1.9;margin:23px 0;font-size:1.12rem;}
.result-card {background:#fff2f8;border:2px solid #f3d2e4;padding:20px;border-radius:18px;margin:15px 0;color:#62536c;line-height:1.9;font-size:1.05rem;overflow-wrap:anywhere;}
.small-note {text-align:center;color:#82758d;font-size:15px;line-height:1.9;margin-top:17px;}
@media(max-width:500px){.main-title{font-size:2.1rem}.group-title{font-size:1.9rem}.question{font-size:1.05rem}.guide-box{padding:18px;font-size:.95rem}.st-key-green_btn button,.st-key-yellow_btn button,.st-key-red_btn button{height:85px!important;min-height:85px!important}.st-key-green_btn button p,.st-key-yellow_btn button p,.st-key-red_btn button p{font-size:23px!important}.st-key-start_button button p,.st-key-next_button button p,.st-key-home_button button p{font-size:19px!important}.info-box{font-size:1rem}}
</style>
""", unsafe_allow_html=True)


def reset_evaluation():
    # 홈에서 선택한 분반을 평가 시작 시 확정합니다.
    st.session_state.selected_class = st.session_state.class_picker
    st.session_state.page = "evaluation"
    st.session_state.current_group = 1
    st.session_state.selected = None
    st.session_state.results = []
    st.session_state.participant_id = uuid.uuid4().hex
    st.session_state.save_error = ""
    for i in range(1, 6):
        st.session_state.pop(f"reason_{i}", None)


def go_home():
    st.session_state.page = "home"
    st.session_state.current_group = 1
    st.session_state.selected = None
    st.session_state.results = []
    st.session_state.save_error = ""


def select_answer(answer):
    st.session_state.selected = answer
    st.session_state.save_error = ""


def save_all(results):
    payload = {
        "action": "save_all",
        "class_id": st.session_state.selected_class,
        "participant_id": st.session_state.participant_id,
        "results": results,
    }
    response = requests.post(
        st.secrets["apps_script_url"], json=payload,
        timeout=(4, 15), allow_redirects=True,
    )
    response.raise_for_status()
    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(result.get("message", "저장 실패"))


def save_and_next():
    group = st.session_state.current_group
    answer = st.session_state.selected
    reason = st.session_state.get(f"reason_{group}", "").strip()
    total = CLASSES[st.session_state.selected_class]["groups"]
    if answer not in CRITERIA or not reason:
        st.session_state.save_error = "평가를 선택하고 이유를 작성해 주세요."
        return False
    current = {"group": group, "answer": answer, "reason": reason}
    if group < total:
        st.session_state.results.append(current)
        st.session_state.current_group += 1
        st.session_state.selected = None
        st.session_state.save_error = ""
        return True
    all_results = st.session_state.results + [current]
    if len(all_results) != total:
        st.session_state.save_error = "평가 결과를 확인해 주세요."
        return False
    try:
        save_all(all_results)
    except Exception:
        st.session_state.save_error = "평가 결과를 전송하지 못했어요. 다시 제출해 주세요."
        return False
    st.session_state.results = all_results
    st.session_state.page = "complete"
    st.session_state.selected = None
    st.session_state.save_error = ""
    return True


def title(text):
    st.markdown(f'<div class="main-title">{text}</div>', unsafe_allow_html=True)


if st.session_state.page == "home":
    title("🚦 AI 신호등 평가")
    st.markdown('<div class="subtitle">우리의 인공지능 서비스,<br>사용해도 괜찮을까요? 🌷</div>', unsafe_allow_html=True)
    st.markdown('<div class="guide-box">🟢 <b>가능</b> : 바로 사용할 의사가 있어요.<br>🟡 <b>제한</b> : 조건이나 보완이 이루어진다면 사용할 의사가 있어요.<br>🔴 <b>금지</b> : 사용할 의사가 없어요.</div>', unsafe_allow_html=True)
    selected_class = st.radio(
        "🌼 자신의 분반을 선택해 주세요.", options=list(CLASSES),
        format_func=lambda c: f'{CLASSES[c]["label"]} ({CLASSES[c]["groups"]}개 조)',
        horizontal=True, key="class_picker",
    )
    st.markdown(
        '평가를 선택하고 이유를 작성해야 다음으로 넘어갈 수 있어요.</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.button("🌷 평가 시작하기", key="start_button", use_container_width=True, on_click=reset_evaluation)

elif st.session_state.page == "evaluation":
    group = st.session_state.current_group
    class_id = st.session_state.selected_class
    total = CLASSES[class_id]["groups"]
    title("🚦 AI 신호등 평가")
    st.progress((group - 1) / total, text=f'{CLASSES[class_id]["label"]} · 평가 진행 : {group} / {total}')
    st.markdown(f'<div class="group-title">🌼 {group}조 평가하기</div>', unsafe_allow_html=True)
    st.markdown('<div class="question">이 인공지능 서비스를 사용하시겠습니까?</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        st.button("🟢 가능", key="green_btn", use_container_width=True, on_click=select_answer, args=("가능",))
    with col2:
        st.button("🟡 제한", key="yellow_btn", use_container_width=True, on_click=select_answer, args=("제한",))
    with col3:
        st.button("🔴 금지", key="red_btn", use_container_width=True, on_click=select_answer, args=("금지",))
    selected = st.session_state.selected
    if selected:
        button_key = {"가능": "green_btn", "제한": "yellow_btn", "금지": "red_btn"}[selected]
        st.markdown(f'<style>.st-key-{button_key} button {{outline:4px solid #82718d!important;outline-offset:3px!important;}}</style>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box"><b>{EMOJI[selected]} 선택한 평가 : {selected}</b><br>{CRITERIA[selected]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">🍀 세 가지 신호등 중 하나를 선택해 주세요!</div>', unsafe_allow_html=True)
    reason = st.text_area(
        "📝 그렇게 평가한 이유를 작성해 주세요.",
        placeholder="예) 개인정보 보호를 위한 대책이 부족해서 바로 사용하기 어려울 것 같아요.",
        max_chars=100, height=145, key=f"reason_{group}",
    )
    can_next = selected is not None and bool(reason.strip())
    next_text = f"다음 : {group + 1}조 평가하기 →" if group < total else "💌 모든 평가 제출하기"
    if st.button(next_text, key="next_button", use_container_width=True, disabled=not can_next):
        if group == total:
            with st.spinner("🌷 모든 평가 결과를 제출하고 있어요..."):
                success = save_and_next()
        else:
            success = save_and_next()
        if success:
            st.rerun()
    if st.session_state.save_error:
        st.error(st.session_state.save_error)
    if not can_next:
        st.markdown('<div class="small-note">🌸 평가 선택과 이유 작성을 완료하면<br>다음 조로 넘어갈 수 있어요.</div>', unsafe_allow_html=True)

elif st.session_state.page == "complete":
    title("🎉 평가 완료!")
    class_id = st.session_state.selected_class
    st.markdown(f'<div class="subtitle">{CLASSES[class_id]["label"]}의 모든 평가를 완료했어요!<br>신중하게 평가해 주셔서 고마워요. 💗</div>', unsafe_allow_html=True)
    st.subheader("📋 나의 평가 결과")
    for item in st.session_state.results:
        reason = escape(item["reason"]).replace("\n", "<br>")
        st.markdown(
            f'<div class="result-card"><b>{item["group"]}조 : {EMOJI[item["answer"]]} {item["answer"]}</b>'
            f'<div style="margin-top:10px;">{reason}</div></div>', unsafe_allow_html=True,
        )
    st.markdown('<div class="small-note">평가 결과가 제출되었어요.<br>결과를 확인한 뒤 화면을 닫아 주세요.</div>', unsafe_allow_html=True)
    st.button("🏠 처음으로 돌아가기", key="home_button", use_container_width=True, on_click=go_home)
