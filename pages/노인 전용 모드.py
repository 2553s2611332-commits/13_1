import os
import streamlit as st
from google import genai

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="어르신 맞춤형 쉬운 키오스크",
    page_icon="🍔",
    layout="wide"
)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "senior_mode" not in st.session_state:
    st.session_state.senior_mode = True

if "cart" not in st.session_state:
    st.session_state.cart = []

# ---------------------------------------------------------
# CSS Injection (Streamlit >= 1.40.0 호환)
# ---------------------------------------------------------
if st.session_state.senior_mode:
    st.markdown(
        """
        <style>
        html, body, [class*="st-"] {
            font-size: 22px !important;
        }
        button {
            height: 3.2rem !important;
            font-size: 22px !important;
            font-weight: bold !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# Menu Data
# ---------------------------------------------------------
MENU_ITEMS = [
    {"id": 1, "category": "버거 (식사)", "name": "불고기버거", "price": 4500, "icon": "🍔", "desc": "달콤하고 부드러운 불고기 소스 버거"},
    {"id": 2, "category": "버거 (식사)", "name": "새우버거", "price": 5000, "icon": "🥪", "desc": "고소한 새우 살이 씹히는 버거"},
    {"id": 3, "category": "음료 (마실거리)", "name": "따뜻한 아메리카노", "price": 2000, "icon": "☕", "desc": "향이 좋고 따뜻한 커피"},
    {"id": 4, "category": "음료 (마실거리)", "name": "시원한 사이다", "price": 1800, "icon": "🥤", "desc": "톡 쏘는 청량한 톡톡 음료"},
    {"id": 5, "category": "간식 (사이드)", "name": "바삭한 감자튀김", "price": 2200, "icon": "🍟", "desc": "갓 튀겨낸 짭조름한 감자"},
    {"id": 6, "category": "간식 (사이드)", "name": "달콤한 아이스크림", "price": 1500, "icon": "🍦", "desc": "시원하고 부드러운 우유 아이스크림"}
]

# ---------------------------------------------------------
# Header Section
# ---------------------------------------------------------
col_head1, col_head2 = st.columns([3, 1])

with col_head1:
    if st.session_state.senior
