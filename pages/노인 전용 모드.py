import os
import streamlit as st
from google import genai

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="어르신 맞춤형 쉬운 키오스크",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# State Management Initialization
# ---------------------------------------------------------
if "senior_mode" not in st.session_state:
    st.session_state.senior_mode = True  # 기본값을 어르신 모드로 설정

if "cart" not in st.session_state:
    st.session_state.cart = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# CSS Styling (Senior Mode / Standard Mode)
# ---------------------------------------------------------
senior_css = """
<style>
    /* 어르신 모드: 큰 글씨, 명확한 고대비 스타일 */
    html, body, [class*="css"] {
        font-size: 24px !important;
    }
    .stButton>button {
        font-size: 26px !important;
        font-weight: bold !important;
        height: 3.5rem !important;
        border-radius: 12px !important;
        background-color: #0056b3 !important;
        color: white !important;
        border: 2px solid #003366 !important;
        margin-bottom: 10px;
    }
    .stButton>button:hover {
        background-color: #003366 !important;
        color: #ffff00 !important;
    }
    .cart-box {
        background-color: #fffde7;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #fbc02d;
        margin-top: 15px;
    }
    .menu-card {
        border: 2px solid #cccccc;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        background-color: #f9f9f9;
        margin-bottom: 15px;
    }
</style>
"""

standard_css = """
<style>
    /* 일반 모드 스타일 */
    html, body, [class*="css"] {
        font-size: 16px;
    }
</style>
"""

if st.session_state.senior_mode:
    st.markdown(senior_css, unsafe_allow_html=True)
else:
    st.markdown(standard_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# Menu Data Definition
# ---------------------------------------------------------
MENU_ITEMS = [
    {
        "id": 1,
        "category": "버거 (밥/빵)",
        "name": "불고기버거",
        "price": 4500,
        "desc": "달콤한 불고기 소스가 들어간 대표 버거",
        "icon": "🍔"
    },
    {
        "id": 2,
        "category": "버거 (밥/빵)",
        "name": "새우버거",
        "price": 5000,
        "desc": "고소한 새우살이 씹히는 부드러운 버거",
        "icon": "🥪"
    },
    {
        "id": 3,
        "category": "음료 (마실 거리)",
        "name": "따뜻한 아메리카노",
        "price": 2000,
        "desc": "향이 좋고 따뜻한 원두커피",
        "icon": "☕"
    },
    {
        "id": 4,
        "category": "음료 (마실 거리)",
        "name": "시원한 사이다",
        "price": 1800,
        "desc": "톡 쏘는 청량한 톡톡 음료",
        "icon": "🥤"
    },
    {
        "id": 5,
        "category": "사이드 (간식)",
        "name": "바삭한 감자튀김",
        "price": 2200,
        "desc": "갓 튀겨낸 짭조름한 샛노란 감자",
        "icon": "🍟"
    },
    {
        "id": 6,
        "category": "사이드 (간식)",
        "name": "부드러운 아이스크림",
        "price": 1500,
        "desc": "시원하고 달콤한 우유 아이스크림",
        "icon": "🍦"
    }
]

# ---------------------------------------------------------
# Header & Mode Switch
# ---------------------------------------------------------
col_title, col_toggle = st.columns([3, 1])

with col_title:
    if st.session_state.senior_mode:
        st.title("👵 어르신 전용 쉬운 주문 매장")
        st.subheader("글씨가 크고 주문하기 가장 쉬운 화면입니다.")
    else:
        st.title("🍔 스마트 키오스크 (일반 모드)")

with col_toggle:
    st.write("---")
    senior_toggle = st.toggle(
        "👵 어르신 전용 모드",
        value=st.session_state.senior_mode,
        key="mode_switch"
    )
    if senior_toggle != st.session_state.senior_mode:
        st.session_state.senior_mode = senior_toggle
        st.rerun()

st.divider()

# ---------------------------------------------------------
# Sidebar: AI Assistant (Gemini 2.5 Flash-Lite)
# ---------------------------------------------------------
with st.sidebar:
    st.header("🤖 AI 키오스크 도우미")
    st.info("메뉴 선택이 어렵거나 도움이 필요하시면 아래에 물어보세요!")
    
    # Secret Key 가져오기
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    
    user_query = st.text_input(
        "질문하기 (예: '매운 거 못 먹는데 뭐 먹을까요?')" if not st.session_state.senior_mode else "💡 궁금한 점을 적고 질문하기 버튼을 누르세요:"
    )
    
    if st.button("질문하기 🗣️", use_container_width=True):
        if not api_key:
            st.error("API 키가 설정되지 않았습니다. Secrets에 GEMINI_API_KEY를 등록해 주세요.")
        elif not user_query.strip():
            st.warning("질문 내용을 입력해 주세요.")
        else:
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                당신은 패스트푸드점 키오스크 사용을 돕는 친절한 어
