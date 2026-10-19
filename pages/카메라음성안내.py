

import base64
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="쉬운 키오스크 음성도우미",
    page_icon="🔊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# 기본 설정
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F4F8FC;
    }
    .block-container {
        max-width: 850px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3, p, label, li {
        color: #183153;
    }
    h1 {
        font-size: 2.1rem !important;
        font-weight: 800 !important;
    }
    h2 {
        font-size: 1.55rem !important;
    }
    p, li, label {
        font-size: 1.15rem;
        line-height: 1.7;
    }
    div.stButton > button {
        width: 100%;
        min-height: 58px;
        border-radius: 14px;
        font-size: 1.15rem;
        font-weight: 700;
        border: 2px solid #B8CDE5;
    }
    div[data-testid="stRadio"] label {
        font-size: 1.15rem;
        padding: 5px 0;
    }
    .guide-card {
        background: #FFFFFF;
        border: 2px solid #D5E3F3;
        border-radius: 18px;
        padding: 22px;
        margin: 12px 0;
    }
    .guide-number {
        font-size: 1rem;
        color: #365D89;
        font-weight: 700;
    }
    .guide-text {
        font-size: 1.55rem;
        color: #17365D;
        font-weight: 800;
        line-height: 1.7;
    }
    .notice {
        background: #FFF4D6;
        border-radius: 12px;
        padding: 14px;
        color: #553F08;
        font-size: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

STEPS = {
    "1. 메뉴 고르기": {
        "title": "원하는 메뉴를 골라 보세요.",
        "guide": (
            "화면에 있는 메뉴 사진이나 이름을 살펴보세요. "
            "원하는 메뉴를 손가락으로 한 번 눌러 주세요. "
            "잘 모르겠다면 직원에게 도움을 요청하셔도 됩니다."
        ),
        "tip": "먹고 싶은 음식이나 음료를 먼저 찾아보세요.",
    },
    "2. 수량과 옵션 선택": {
        "title": "수량과 옵션을 확인해 주세요.",
        "guide": (
            "몇 개를 주문할지 확인해 주세요. "
            "크기나 추가 메뉴를 고르는 화면이라면 원하는 항목을 선택하세요. "
            "선택하지 않아도 되는 항목인지 잘 모르겠다면 서두르지 마세요."
        ),
        "tip": "화면에 표시된 가격과 선택 항목을 확인하세요.",
    },
    "3. 장바구니 확인": {
        "title": "주문할 음식과 가격을 확인하세요.",
        "guide": (
            "지금까지 고른 메뉴와 수량, 총금액을 확인해 주세요. "
            "잘못 선택한 항목이 있다면 수정하세요. "
            "모두 맞으면 주문하기 또는 결제하기 버튼을 찾아 눌러 주세요."
        ),
        "tip": "결제하기 전에 메뉴와 총금액을 꼭 확인하세요.",
    },
    "4. 결제하기": {
        "title": "결제 방법을 선택해 주세요.",
        "guide": (
            "화면에서 카드 결제나 다른 결제 방법을 확인하세요. "
            "안내에 따라 진행하고, 카드나 현금은 기기가 안내하는 위치에 넣어 주세요. "
            "카드 비밀번호 등 민감한 정보는 다른 사람에게 알려주지 마세요."
        ),
        "tip": "기기마다 카드 투입 위치와 결제 순서가 다를 수 있습니다.",
    },
    "5. 주문 완료 확인": {
        "title": "주문이 완료되었는지 확인하세요.",
        "guide": (
            "주문 완료 메시지나 영수증, 대기번호가 표시되었는지 확인하세요. "
            "번호표가 나왔다면 잘 보관해 주세요. "
            "주문 완료 여부가 불분명하다면 결제를 반복하지 말고 직원에게 확인하세요."
        ),
        "tip": "영수증이나 대기번호를 확인하면 주문을 찾기 쉽습니다.",
    },
}

# -----------------------------
# 세션 상태 초기화
# -----------------------------
if "step_index" not in st.session_state:
    st.session_state.step_index = 0

if "font_scale" not in st.session_state:
    st.session_state.font_scale = "큰 글씨"

if "camera_image" not in st.session_state:
    st.session_state.camera_image = None

# -----------------------------
# 상단 소개
# -----------------------------
st.title("🔊 쉬운 키오스크 음성도우미")
st.markdown(
    "어려운 키오스크 화면도 천천히! "
    "큰 글씨와 한국어 음성으로 한 단계씩 안내해 드립니다."
)

st.info(
    "사용 방법: 카메라로 화면을 촬영하고, "
    "현재 진행 중인 단계를 선택한 다음 안내를 들어 보세요."
)

# -----------------------------
# 글씨 크기 조절
# -----------------------------
st.subheader("👓 글씨 크기")

st.session_state.font_scale = st.radio(
    "안내 글씨 크기를 선택하세요.",
    ["보통 글씨", "큰 글씨", "아주 큰 글씨"],
    index=["보통 글씨", "큰 글씨", "아주 큰 글씨"].index(
        st.session_state.font_scale
    ),
    horizontal=True,
    label_visibility="collapsed",
)

font_sizes = {
    "보통 글씨": "1.15rem",
    "큰 글씨": "1.45rem",
    "아주 큰 글씨": "1.75rem",
}
current_font = font_sizes[st.session_state.font_scale]

st.markdown(
    f"""
    <style>
    .guide-text {{
        font-size: {current_font} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 카메라
# -----------------------------
st.subheader("📷 키오스크 화면 비추기")
st.write(
    "아래 버튼을 눌러 키오스크 화면을 촬영할 수 있습니다. "
    "카메라 권한 요청이 나오면 허용해 주세요."
)

try:
    photo = st.camera_input(
        "키오스크 화면 촬영",
        key="kiosk_camera",
    )

    if photo is not None:
        st.session_state.camera_image = photo
        st.success("사진을 촬영했습니다.")
        st.image(
            photo,
            caption="촬영한 키오스크 화면",
            use_container_width=True,
        )

except Exception as exc:
    st.warning(
        "카메라를 사용할 수 없습니다. "
        "브라우저의 카메라 권한과 기기 설정을 확인해 주세요."
    )
    st.caption(f"오류 정보: {type(exc).__name__}")

st.markdown(
    """
    <div class="notice">
    안내: 이 버전은 촬영한 화면을 미리 보여 줍니다.
    사진 속 글자나 버튼을 자동으로 판독하지는 않습니다.
    아래에서 현재 상황을 선택하면 해당 단계의 안내를 제공합니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 단계 선택
# -----------------------------
st.subheader("🧭 지금 어떤 단계인가요?")

step_names = list(STEPS.keys())

selected_step = st.radio(
    "현재 상황을 선택하세요.",
    step_names,
    index=st.session_state.step_index,
    key="step_selector",
)

st.session_state.step_index = step_names.index(selected_step)
current_step = STEPS[selected_step]

st.markdown(
    f"""
    <div class="guide-card">
        <div class="guide-number">{selected_step}</div>
        <div class="guide-text">{current_step["title"]}</div>
        <p>{current_step["tip"]}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 음성안내
# 브라우저 내장 한국어 음성 합성 사용
# -----------------------------
st.subheader("🗣️ 음성으로 안내 듣기")
st.write("아래 음성안내 창의 버튼을 눌러 설명을 들어 보세요.")

speech_text = (
    current_step["title"]
    + " "
    + current_step["guide"]
    + " "
    + current_step["tip"]
)

speech_json = json.dumps(speech_text, ensure_ascii=False)

speech_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
body {
    font-family: sans-serif;
    margin: 0;
    padding: 8px;
    background: #F4F8FC;
}
button {
    width: 100%;
    min-height: 64px;
    margin: 5px 0;
    padding: 12px;
    border: 2px solid #1D4E89;
    border-radius: 14px;
    background: #1D4E89;
    color: white;
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;
}
button.secondary {
    background: white;
    color: #1D4E89;
}
#status {
    color: #183153;
    font-size: 16px;
    padding: 8px 2px;
}
</style>
</head>
<body>
<button id="speak">🔊 안내 듣기</button>
<button class="secondary" id="slow">🐢 천천히 듣기</button>
<button class="secondary" id="stop">■ 음성 멈추기</button>
<div id="status" role="status" aria-live="polite">
버튼을 누르면 한국어 안내가 시작됩니다.
</div>
<script>
const message = __SPEECH_TEXT__;
const statusBox = document.getElementById("status");

function speak(rate) {
    if (!("speechSynthesis" in window)) {
        statusBox.textContent =
            "이 브라우저는 음성 안내를 지원하지 않습니다.";
        return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(message);
    utterance.lang = "ko-KR";
    utterance.rate = rate;
    utterance.pitch = 1;
    utterance.onstart = () => {
        statusBox.textContent = "음성 안내를 재생하고 있습니다.";
    };
    utterance.onend = () => {
        statusBox.textContent = "안내가 끝났습니다.";
    };
    utterance.onerror = () => {
        statusBox.textContent =
            "음성을 재생하지 못했습니다. 다시 눌러 주세요.";
    };

    window.speechSynthesis.speak(utterance);
}

document.getElementById("speak").addEventListener(
    "click", () => speak(0.95)
);
document.getElementById("slow").addEventListener(
    "click", () => speak(0.70)
);
document.getElementById("stop").addEventListener("click", () => {
    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
    }
    statusBox.textContent = "음성 안내를 멈췄습니다.";
});
</script>
</body>
</html>
""".replace("__SPEECH_TEXT__", speech_json)

components.html(speech_html, height=250, scrolling=False)

# -----------------------------
# 단계 이동
# -----------------------------
st.subheader("➡️ 다음 단계로 이동")

col1, col2 = st.columns(2)

with col1:
    if st.button("⬅️ 이전 단계"):
        if st.session_state.step_index > 0:
            st.session_state.step_index -= 1
            st.rerun()
        else:
            st.info("첫 번째 단계입니다.")

with col2:
    if st.button("다음 단계 ➡️"):
        if st.session_state.step_index < len(step_names) - 1:
            st.session_state.step_index += 1
            st.rerun()
        else:
            st.success("마지막 단계입니다. 주문이 완료되었는지 확인하세요.")

if st.button("🏠 처음부터 다시 시작"):
    st.session_state.step_index = 0
    st.rerun()

# -----------------------------
# 도움말
# -----------------------------
with st.expander("❓ 사용이 어려우신가요?"):
    st.markdown(
        """
        1. 카메라 권한을 허용해 주세요.
        2. 현재 키오스크 진행 상황을 선택하세요.
        3. '안내 듣기' 또는 '천천히 듣기'를 누르세요.
        4. 안내를 이해하기 어려우면 직원에게 도움을 요청하세요.

        **개인정보 보호:** 카드번호, 비밀번호, 개인정보가
        보이는 화면은 촬영하지 마세요.

        **참고:** 이 앱은 실제 키오스크를 직접 조작하거나
        결제를 수행하지 않습니다.
        """
    )

st.divider()
st.caption(
    "쉬운 키오스크 음성도우미 · 어르신의 편리하고 안전한 이용을 돕습니다."
)
