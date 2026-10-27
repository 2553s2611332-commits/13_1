import os
import streamlit as st

# Google SDK 호환성 예외 처리
AI_AVAILABLE = True
try:
    import google.generativeai as genai
    SDK_TYPE = "generativeai"
except ImportError:
    try:
        from google import genai
        SDK_TYPE = "genai"
    except ImportError:
        AI_AVAILABLE = False

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
# CSS Injection for Senior Mode
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
    if st.session_state.senior_mode:
        st.title("👵 어르신 전용 쉬운 주문 매장")
        st.write("글씨가 크고 주문하기 가장 쉬운 화면입니다.")
    else:
        st.title("🍔 일반 스마트 키오스크")

with col_head2:
    toggle_val = st.toggle("👵 노인전용모드", value=st.session_state.senior_mode)
    if toggle_val != st.session_state.senior_mode:
        st.session_state.senior_mode = toggle_val
        st.rerun()

st.divider()

# ---------------------------------------------------------
# Sidebar: AI Assistant (gemini-2.5-flash-lite)
# ---------------------------------------------------------
with st.sidebar:
    st.header("🤖 AI 키오스크 도우미")
    st.write("메뉴 선택이 어렵다면 도우미에게 물어보세요!")
    
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    user_q = st.text_input("질문 입력 (예: 매운 거 못 먹는데 추천해줘)")
    
    if st.button("도우미에게 물어보기 🗣️", use_container_width=True):
        if not AI_AVAILABLE:
            st.error("AI 라이브러리 설치 중입니다. 잠시 후 다시 시도해주세요.")
        elif not api_key:
            st.error("Secrets에 GEMINI_API_KEY가 설정되지 않았습니다.")
        elif not user_q.strip():
            st.warning("질문 내용을 입력해 주세요.")
        else:
            try:
                prompt_text = (
                    "당신은 어르신을 돕는 친절한 패스트푸드 점원입니다. "
                    "쉬운 한국어와 존댓말로 2문장 이내로 친절히 안내해주세요.\n"
                    f"현재 메뉴: 불고기버거(4500원), 새우버거(5000원), 따뜻한 아메리카노(2000원), "
                    f"시원한 사이다(1800원), 바삭한 감자튀김(2200원), 달콤한 아이스크림(1500원)\n"
                    f"사용자 질문: {user_q}"
                )
                
                with st.spinner("생각하는 중..."):
                    if SDK_TYPE == "generativeai":
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-2.5-flash-lite")
                        res = model.generate_content(prompt_text)
                        ans_text = res.text
                    else:
                        client = genai.Client(api_key=api_key)
                        res = client.models.generate_content(
                            model="gemini-2.5-flash-lite",
                            contents=prompt_text
                        )
                        ans_text = res.text
                        
                    st.success("도우미 답변:")
                    st.write(ans_text)
            except Exception as e:
                st.error(f"AI 연결 중 오류 발생: {e}")

# ---------------------------------------------------------
# Main Ordering Interface
# ---------------------------------------------------------
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("1. 원하시는 음식 종류를 선택하세요")
    categories = list(dict.fromkeys(item["category"] for item in MENU_ITEMS))
    selected_cat = st.radio("카테고리 선택", categories, horizontal=True)
    
    st.subheader("2. 드시고 싶은 음식을 클릭하세요")
    items_to_show = [i for i in MENU_ITEMS if i["category"] == selected_cat]
    
    grid_cols = st.columns(2)
    for index, item in enumerate(items_to_show):
        with grid_cols[index % 2]:
            st.info(f"### {item['icon']} {item['name']}\n\n**가격: {item['price']:,}원**\n\n{item['desc']}")
            if st.button(f"➕ {item['name']} 담기", key=f"btn_{item['id']}", use_container_width=True):
                st.session_state.cart.append(item)
                st.toast(f"'{item['name']}'을(를) 담았습니다!", icon="✅")

with right_col:
    st.subheader("🛒 선택한 메뉴 목록")
    
    if not st.session_state.cart:
        st.warning("아직 선택한 음식이 없습니다.")
    else:
        total = 0
        for idx, cart_item in enumerate(st.session_state.cart):
            st.write(f"**{idx + 1}. {cart_item['name']}** ({cart_item['price']:,}원)")
            total += cart_item["price"]
            
        st.divider()
        st.markdown(f"### **총 합계: {total:,}원**")
        
        btn_pay, btn_clear = st.columns(2)
        with btn_pay:
            if st.button("💳 결제하기", use_container_width=True):
                st.balloons()
                st.success("🎉 주문이 완료되었습니다!")
                st.session_state.cart = []
        with btn_clear:
            if st.button("🗑️ 전체 취소", use_container_width=True):
                st.session_state.cart = []
                st.rerun()
