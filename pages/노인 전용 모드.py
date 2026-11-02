import streamlit as st
import os

# Streamlit 페이지 기본 설정 (와이드 레이아웃)
st.set_page_config(
    page_title="어르신 전용 쉬운 키오스크",
    page_icon="👵",
    layout="wide"
)

# -------------------------------------------------------------------
# 어르신 전용 대형 글씨 및 가독성 향상 CSS 스타일링
# -------------------------------------------------------------------
st.markdown("""
<style>
    /* 전체 글꼴 크기 확대 및 굵게 설정 */
    html, body, [class*="css"] {
        font-size: 24px !important;
        font-family: 'Malgun Gothic', 'Nanum Gothic', sans-serif;
    }
    
    /* 버튼 스타일: 대형 크기, 직관적인 색상, 명확한 테두리 */
    .stButton > button {
        width: 100%;
        height: 90px !important;
        font-size: 28px !important;
        font-weight: bold !important;
        border-radius: 16px !important;
        border: 3px solid #222222 !important;
        background-color: #F8F9FA !important;
        color: #111111 !important;
        margin-bottom: 10px;
    }
    
    /* 강조 버튼 (주문 완료, 다음 단계 등) */
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #FF5722 !important;
        color: #FFFFFF !important;
        border: 3px solid #BF360C !important;
    }

    /* 카드/상자 형태의 메뉴 안내 */
    .menu-card {
        background-color: #FFFFFF;
        border: 3px solid #CCCCCC;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
    }
    .menu-title {
        font-size: 30px !important;
        font-weight: bold;
        color: #111111;
    }
    .menu-price {
        font-size: 26px !important;
        color: #D32F2F;
        font-weight: bold;
    }

    /* 큰 설명 텍스트 */
    .big-instruction {
        font-size: 32px !important;
        font-weight: bold;
        color: #1A237E;
        background-color: #E8EAF6;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        border: 2px solid #3F51B5;
    }
</style>
""", unsafe_allow_kw=True)

# -------------------------------------------------------------------
# 세션 상태 초기화 (주문 데이터 및 진행 단계 관리)
# -------------------------------------------------------------------
if 'step' not in st.session_state:
    st.session_state.step = 1  # 1: 장소선택, 2: 메뉴선택, 3: 결제, 4: 완료
if 'place' not in st.session_state:
    st.session_state.place = ""
if 'cart' not in st.session_state:
    st.session_state.cart = {}  # {메뉴명: {"price": 가격, "qty": 수량}}

# -------------------------------------------------------------------
# 메뉴 데이터 (쉬운 한글 이름 표기)
# -------------------------------------------------------------------
MENU_ITEMS = {
    "☕ 마실 것 (음료)": [
        {"name": "따뜻한 원두커피", "price": 2000, "desc": "쓴맛이 나고 향이 좋은 따뜻한 커피", "icon": "☕"},
        {"name": "시원한 원두커피", "price": 2500, "desc": "얼음이 들어간 시원한 커피", "icon": "🧊"},
        {"name": "달콤한 꿀배차", "price": 3000, "desc": "목에 좋은 달달하고 따뜻한 배차", "icon": "🍵"},
        {"name": "고소한 우유", "price": 1500, "desc": "신선하고 신선한 영양 우유", "icon": "🥛"}
    ],
    "🍞 먹을 것 (빵/식사)": [
        {"name": "부드러운 식빵 구이", "price": 3000, "desc": "노릇하게 구운 식빵 2조각", "icon": "🍞"},
        {"name": "불고기 빵 (버거)", "price": 4500, "desc": "달콤한 불고기가 들어간 빵", "icon": "🍔"},
        {"name": "고소한 계란 빵", "price": 2500, "desc": "영양 가득한 계란이 쏙 들어간 빵", "icon": "🧁"},
        {"name": "감자 튀김", "price": 2000, "desc": "바삭하고 짭짤한 감자 튀김", "icon": "🍟"}
    ]
}

# -------------------------------------------------------------------
# Gemini AI 도우미 함수 (선택 사항)
# -------------------------------------------------------------------
def ask_gemini_ai(user_prompt):
    """Gemini 2.5 Flash Lite 모델을 이용한 어르신 전용 추천 답변 생성"""
    try:
        from google import genai
        
        api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "AI 도우미 설정이 되어있지 않습니다. 아래 버튼을 직접 눌러 메뉴를 선택해주세요."
            
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"당신은 친절한 패스트푸드점 직원입니다. 어르신께서 '{user_prompt}'라고 하셨습니다. 극히 쉬운 우리말 표현으로, 존댓말을 사용하여 메뉴 1~2개를 따뜻하게 추천해주세요. 영어나 어려운 말은 절대 쓰지 마세요.",
        )
        return response.text
    except Exception as e:
        return "AI 도우미 연결에 실패했습니다. 아래 메뉴판에서 직접 눌러 주문해주세요."

# -------------------------------------------------------------------
# 화면 구성 (단계별 레이아웃)
# -------------------------------------------------------------------

# 헤더 영역
st.title("👵 어르신 전용 쉬운 주문기 (키오스크)")
st.divider()

# STEP 1: 어디서 드실지 선택
if st.session_state.step == 1:
    st.markdown("<div class='big-instruction'>1단계: 어디서 드시는지 눌러주세요</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏪 가게 안에서 먹기\n(매장 식사)", use_container_width=True):
            st.session_state.place = "가게 안에서 먹기"
            st.session_state.step = 2
            st.rerun()
            
    with col2:
        if st.button("🛍️ 싸서 가져가기\n(포장 주문)", use_container_width=True):
            st.session_state.place = "싸서 가져가기"
            st.session_state.step = 2
            st.rerun()

# STEP 2: 메뉴 선택
elif st.session_state.step == 2:
    st.markdown(f"<div class='big-instruction'>2단계: 원하시는 음식을 눌러서 담으세요<br><small style='font-size:20px; color:#555;'>(선택한 장소: {st.session_state.place})</small></div>", unsafe_allow_html=True)
    
    # AI 안내말 도우미 접기/펴기
    with st.expander("🤖 무엇을 먹을지 고민되시나요? (AI 도우미에게 물어보기)", expanded=False):
        user_input = st.text_input("예: 목이 마른데 달콤한 차 있어?", placeholder="궁금하신 점을 여기에 적어보세요.")
        if st.button("도우미에게 물어보기"):
            if user_input:
                with st.spinner("도우미가 생각 중입니다..."):
                    ai_reply = ask_gemini_ai(user_input)
                    st.info(ai_reply)
            else:
                st.warning("궁금하신 점을 입력해주세요.")

    # 메인 메뉴 목록과 장바구니 화면 분할 (2:1 비율)
    col_menu, col_cart = st.columns([2, 1])
    
    with col_menu:
        # 카테고리 탭 (마실 것 / 먹을 것)
        tabs = st.tabs(list(MENU_ITEMS.keys()))
        
        for idx, (category, items) in enumerate(MENU_ITEMS.items()):
            with tabs[idx]:
                grid_col1, grid_col2 = st.columns(2)
                for i, item in enumerate(items):
                    target_col = grid_col1 if i % 2 == 0 else grid_col2
                    with target_col:
                        st.markdown(f"""
                        <div class='menu-card'>
                            <div style='font-size:48px;'>{item['icon']}</div>
                            <div class='menu-title'>{item['name']}</div>
                            <div class='menu-price'>{item['price']:,}원</div>
                            <div style='font-size:18px; color:#666;'>{item['desc']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"➕ {item['name']} 담기", key=f"add_{item['name']}"):
                            if item['name'] in st.session_state.cart:
                                st.session_state.cart[item['name']]['qty'] += 1
                            else:
                                st.session_state.cart[item['name']] = {"price": item['price'], "qty": 1}
                            st.rerun()

    with col_cart:
        st.markdown("### 🛒 담은 음식 목록")
        total_price = 0
        
        if not st.session_state.cart:
            st.info("왼쪽에서 드시고 싶은 음식의 [담기] 버튼을 눌러주세요.")
        else:
            for item_name, data in list(st.session_state.cart.items()):
                item_total = data['price'] * data['qty']
                total_price += item_total
                
                st.markdown(f"**{item_name}**")
                st.write(f"가격: {data['price']:,}원 × {data['qty']}개 = **{item_total:,}원**")
                
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1:
                    if st.button("➖ 1개 빼기", key=f"minus_{item_name}"):
                        st.session_state.cart[item_name]['qty'] -= 1
                        if st.session_state.cart[item_name]['qty'] <= 0:
                            del st.session_state.cart[item_name]
                        st.rerun()
                with c2:
                    if st.button("➕ 1개 더", key=f"plus_{item_name}"):
                        st.session_state.cart[item_name]['qty'] += 1
                        st.rerun()
                with c3:
                    if st.button("❌ 전체 삭제", key=f"del_{item_name}"):
                        del st.session_state.cart[item_name]
                        st.rerun()
                st.divider()
            
            st.markdown(f"## 💰 총 금액: **{total_price:,}원**")
            
            st.write("")
            if st.button("👉 주문하러 가기 (결제)", type="primary", use_container_width=True):
                st.session_state.step = 3
                st.rerun()

    st.divider()
    if st.button("⬅️ 처음 단계(장소 선택)로 돌아가기"):
        st.session_state.step = 1
        st.rerun()

# STEP 3: 주문 확인 및 결제 선택
elif st.session_state.step == 3:
    st.markdown("<div class='big-instruction'>3단계: 주문하신 내용을 확인하시고 결제 방법을 눌러주세요</div>", unsafe_allow_html=True)
    
    st.markdown(f"### 📍 드시는 곳: **{st.session_state.place}**")
    st.markdown("### 📋 선택하신 메뉴:")
    
    total_price = 0
    for name, data in st.session_state.cart.items():
        subtotal = data['price'] * data['qty']
        total_price += subtotal
        st.write(f"- **{name}** : {data['qty']}개 ({subtotal:,}원)")
        
    st.markdown(f"## 💵 내실 금액: **{total_price:,}원**")
    st.divider()
    
    st.markdown("### 💳 결제 방법을 선택해주세요")
    col_pay1, col_pay2 = st.columns(2)
    
    with col_pay1:
        if st.button("💳 카드 넣어서 계산하기", type="primary", use_container_width=True):
            st.session_state.step = 4
            st.rerun()
            
    with col_pay2:
        if st.button("💵 현금 (카운터 직원에게 내기)", use_container_width=True):
            st.session_state.step = 4
            st.rerun()
            
    st.write("")
    if st.button("⬅️ 메뉴 다시 고르기"):
        st.session_state.step = 2
        st.rerun()

# STEP 4: 주문 완료
elif st.session_state.step == 4:
    st.balloons()
    st.markdown("<div class='big-instruction' style='background-color:#E8F5E9; border-color:#2E7D32;'>🎉 주문이 정상적으로 완료되었습니다!</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; padding: 30px;'>
        <h1 style='font-size: 80px; color: #D32F2F;'>주문 번호: 105번</h1>
        <p style='font-size: 28px;'>영수증을 챙기시고, 영수증의 번호(105번)가 화면에 나오면 음식을 가져가세요.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    if st.button("🔄 처음으로 돌아가서 새 주문하기", type="primary", use_container_width=True):
        st.session_state.step = 1
        st.session_state.cart = {}
        st.session_state.place = ""
        st.rerun()
