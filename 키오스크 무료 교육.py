
import streamlit as st

st.set_page_config(
    page_title="키오스크 무료 교육",
    page_icon="🖥️",
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
        background-color: #FFFDF6;
    }
    .block-container {
        max-width: 850px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    html, body, [class*="css"] {
        font-size: 21px !important;
    }
    h1 {
        font-size: 2.1rem !important;
        color: #17365D !important;
    }
    h2 {
        font-size: 1.65rem !important;
        color: #17365D !important;
    }
    h3 {
        font-size: 1.35rem !important;
    }
    p, li, label {
        font-size: 1.05rem !important;
        line-height: 1.7 !important;
    }
    div.stButton > button {
        min-height: 58px;
        width: 100%;
        border-radius: 12px;
        border: 2px solid #24476B;
        font-size: 1.05rem !important;
        font-weight: 700;
        padding: 0.6rem;
    }
    div.stButton > button:focus {
        outline: 3px solid #F0B429;
        outline-offset: 3px;
    }
    [data-testid="stAlert"] {
        font-size: 1.05rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 교육용 메뉴 데이터
# -----------------------------
MENUS = {
    "햄버거": [
        {"name": "불고기 버거", "price": 4500, "emoji": "🍔"},
        {"name": "치즈 버거", "price": 4000, "emoji": "🍔"},
        {"name": "감자튀김", "price": 2000, "emoji": "🍟"},
        {"name": "콜라", "price": 1500, "emoji": "🥤"},
    ],
    "카페": [
        {"name": "아메리카노", "price": 2500, "emoji": "☕"},
        {"name": "카페라떼", "price": 3500, "emoji": "🥛"},
        {"name": "아이스티", "price": 3000, "emoji": "🧋"},
        {"name": "케이크", "price": 4000, "emoji": "🍰"},
    ],
    "분식": [
        {"name": "떡볶이", "price": 4000, "emoji": "🍲"},
        {"name": "김밥", "price": 3500, "emoji": "🍙"},
        {"name": "라면", "price": 4000, "emoji": "🍜"},
        {"name": "어묵", "price": 2000, "emoji": "🍢"},
    ],
}

STEPS = {
    "home": "1단계: 매장 선택",
    "menu": "2단계: 음식 선택",
    "cart": "3단계: 주문 확인",
    "payment": "4단계: 결제 방법 선택",
    "done": "5단계: 주문 완료",
}


def reset_app():
    """교육 과정을 처음부터 다시 시작합니다."""
    st.session_state.stage = "home"
    st.session_state.store = ""
    st.session_state.cart = {}
    st.session_state.payment = ""


def money(amount):
    return f"{amount:,}원"


def get_total():
    total = 0
    store = st.session_state.get("store", "")
    cart = st.session_state.get("cart", {})

    if store not in MENUS:
        return 0

    prices = {item["name"]: item["price"] for item in MENUS[store]}
    for name, quantity in cart.items():
        if name in prices and isinstance(quantity, int) and quantity > 0:
            total += prices[name] * quantity

    return total


# -----------------------------
# 세션 초기화 및 상태 검사
# -----------------------------
if "stage" not in st.session_state:
    reset_app()

if st.session_state.stage not in STEPS:
    reset_app()

if not isinstance(st.session_state.get("cart"), dict):
    st.session_state.cart = {}

# -----------------------------
# 공통 화면
# -----------------------------
st.title("🖥️ 키오스크 무료 교육")
st.markdown(
    "천천히 따라 해 보세요. "
    "실제 돈이 결제되지 않는 **안전한 연습 화면**입니다."
)

current_stage = st.session_state.stage
st.progress(
    (list(STEPS).index(current_stage) + 1) / len(STEPS),
    text=STEPS[current_stage],
)

with st.expander("📖 키오스크가 무엇인가요?"):
    st.write(
        "키오스크는 사람이 직접 화면을 눌러 "
        "음식이나 음료를 주문하는 기계입니다."
    )
    st.write(
        "화면의 글씨를 읽고 원하는 버튼을 누르면 됩니다. "
        "잘못 눌러도 당황하지 말고 이전 단계로 돌아가면 됩니다."
    )

st.divider()

# -----------------------------
# 1단계: 매장 선택
# -----------------------------
if current_stage == "home":
    st.header("1. 어디에서 주문해 볼까요?")
    st.info("원하는 매장의 큰 버튼을 눌러 주세요.")

    columns = st.columns(1)
    for store in MENUS:
        if st.button(
            f"🏪 {store}에서 주문하기",
            key=f"store_{store}",
        ):
            st.session_state.store = store
            st.session_state.cart = {}
            st.session_state.payment = ""
            st.session_state.stage = "menu"
            st.rerun()

# -----------------------------
# 2단계: 음식 선택
# -----------------------------
elif current_stage == "menu":
    store = st.session_state.store

    if store not in MENUS:
        st.warning("매장을 다시 선택해 주세요.")
        if st.button("매장 선택으로 돌아가기"):
            reset_app()
            st.rerun()
    else:
        st.header(f"2. {store} 메뉴 고르기")
        st.write("먹고 싶은 음식의 '담기' 버튼을 눌러 보세요.")
        st.caption("연습이므로 여러 개를 선택해도 괜찮습니다.")

        for item in MENUS[store]:
            with st.container(border=True):
                left, right = st.columns([3, 2])
                with left:
                    st.subheader(f"{item['emoji']} {item['name']}")
                    st.write(money(item["price"]))
                    quantity = st.session_state.cart.get(
                        item["name"], 0
                    )
                    if quantity:
                        st.write(f"현재 담은 수량: {quantity}개")
                with right:
                    if st.button(
                        f"{item['name']} 담기",
                        key=f"add_{item['name']}",
                    ):
                        current = st.session_state.cart.get(
                            item["name"], 0
                        )
                        st.session_state.cart[item["name"]] = current + 1
                        st.rerun()

        st.divider()
        st.subheader(f"현재 합계: {money(get_total())}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ 매장 다시 선택"):
                st.session_state.stage = "home"
                st.rerun()
        with col2:
            if st.button("주문 확인하기 ➡️"):
                if not st.session_state.cart:
                    st.warning("먼저 음식 하나를 담아 주세요.")
                else:
                    st.session_state.stage = "cart"
                    st.rerun()

# -----------------------------
# 3단계: 장바구니 확인
# -----------------------------
elif current_stage == "cart":
    st.header("3. 주문 내용을 확인해요")
    st.write("선택한 음식과 수량이 맞는지 확인하세요.")

    store = st.session_state.store
    cart = st.session_state.cart

    if store not in MENUS or not cart:
        st.warning("담긴 음식이 없습니다. 메뉴를 선택해 주세요.")
        if st.button("메뉴 선택하기"):
            st.session_state.stage = "menu"
            st.rerun()
    else:
        prices = {
            item["name"]: item["price"] for item in MENUS[store]
        }

        for name in list(cart.keys()):
            quantity = cart.get(name, 0)
            if name not in prices or not isinstance(quantity, int) or quantity < 1:
                st.session_state.cart.pop(name, None)

        if not st.session_state.cart:
            st.warning("주문할 음식을 다시 선택해 주세요.")
            if st.button("메뉴로 돌아가기"):
                st.session_state.stage = "menu"
                st.rerun()
        else:
            for name, quantity in st.session_state.cart.items():
                col1, col2, col3 = st.columns([3, 1, 2])
                with col1:
                    st.write(f"**{name}**")
                with col2:
                    st.write(f"{quantity}개")
                with col3:
                    st.write(money(prices[name] * quantity))

                minus_col, plus_col = st.columns(2)
                with minus_col:
                    if st.button(
                        f"{name} 1개 빼기",
                        key=f"minus_{name}",
                    ):
                        if quantity <= 1:
                            st.session_state.cart.pop(name, None)
                        else:
                            st.session_state.cart[name] = quantity - 1
                        st.rerun()
                with plus_col:
                    if st.button(
                        f"{name} 1개 더하기",
                        key=f"plus_{name}",
                    ):
                        st.session_state.cart[name] = quantity + 1
                        st.rerun()

            st.divider()
            st.header(f"총금액: {money(get_total())}")
            st.info(
                "실제 키오스크에서도 결제하기 전에 "
                "음식과 금액을 꼭 확인하세요."
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ 음식 더 고르기"):
                    st.session_state.stage = "menu"
                    st.rerun()
            with col2:
                if st.button("결제 방법 선택 ➡️"):
                    st.session_state.stage = "payment"
                    st.rerun()

# -----------------------------
# 4단계: 가상 결제 선택
# -----------------------------
elif current_stage == "payment":
    st.header("4. 결제 방법을 골라요")
    st.write("실제 결제가 아닙니다. 원하는 방법을 눌러 연습하세요.")

    if not st.session_state.cart or not st.session_state.store:
        st.warning("먼저 음식을 선택해 주세요.")
        if st.button("메뉴로 돌아가기"):
            st.session_state.stage = "menu"
            st.rerun()
    else:
        st.subheader(f"결제할 금액: {money(get_total())}")
        st.write("실제 매장에서는 화면 안내에 따라 결제합니다.")

        if st.button("💳 카드로 결제하는 연습"):
            st.session_state.payment = "카드"
            st.session_state.stage = "done"
            st.rerun()

        if st.button("💵 현금 결제 안내 연습"):
            st.session_state.payment = "현금"
            st.session_state.stage = "done"
            st.rerun()

        if st.button("⬅️ 주문 내용 다시 확인"):
            st.session_state.stage = "cart"
            st.rerun()

# -----------------------------
# 5단계: 주문 완료
# -----------------------------
elif current_stage == "done":
    st.header("🎉 주문 연습을 마쳤어요!")
    st.success("잘하셨습니다. 키오스크 주문 과정을 끝까지 연습했어요.")

    st.subheader("연습한 주문 내역")
    for name, quantity in st.session_state.cart.items():
        st.write(f"- {name} × {quantity}개")

    st.subheader(f"연습한 총금액: {money(get_total())}")
    st.write(f"선택한 결제 방법: {st.session_state.payment}")
    st.info(
        "이 화면은 교육용입니다. 실제 주문이나 결제는 발생하지 않습니다."
    )

    st.markdown("### 오늘 배운 순서")
    st.markdown(
        """
        1. 매장을 선택했어요
        2. 원하는 음식을 골랐어요
        3. 주문 내용과 금액을 확인했어요
        4. 결제 방법을 선택했어요
        5. 주문 완료 화면을 확인했어요
        """
    )

    if st.button("🔄 처음부터 다시 연습하기"):
        reset_app()
        st.rerun()

# -----------------------------
# 공통 하단 안내
# -----------------------------
st.divider()
st.caption(
    "키오스크 무료 교육 | 교육용 가상 주문 | 실제 결제 기능 없음"
)

if st.session_state.stage != "home":
    if st.button("🏠 처음 화면으로 돌아가기", key="global_home"):
        reset_app()
        st.rerun()

