

import json
import os
import urllib.error
import urllib.request

import streamlit as st

st.set_page_config(
    page_title="키오스크 교사",
    page_icon="☕",
    layout="centered",
)

st.markdown("""
<style>
.stApp {
    background-color: #FFFDF7;
    color: #222222;
}
h1, h2, h3 {
    color: #174D3A !important;
}
p, label, .stMarkdown {
    font-size: 19px;
    line-height: 1.7;
}
div.stButton > button {
    width: 100%;
    min-height: 60px;
    border-radius: 14px;
    border: 2px solid #285C4D;
    background: white;
    color: #174D3A;
    font-size: 19px;
    font-weight: bold;
    white-space: normal;
}
div.stButton > button:hover {
    background: #E5F3E9;
    color: #174D3A;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------
# 세션 상태
# ------------------------------
def initialize():
    defaults = {
        "page": "home",
        "step": 0,
        "menu": "아메리카노",
        "temperature": "따뜻하게",
        "order_type": "매장에서 먹기",
        "payment": "카드",
        "question": "",
        "answer": "",
        "history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize()


def reset_practice():
    st.session_state.step = 0
    st.session_state.menu = "아메리카노"
    st.session_state.temperature = "따뜻하게"
    st.session_state.order_type = "매장에서 먹기"
    st.session_state.payment = "카드"
    st.session_state.page = "practice"


def header():
    st.title("☕ 키오스크 교사")
    st.caption("어르신을 위한 친절한 키오스크 연습 선생님")
    st.divider()


# ------------------------------
# AI 선생님
# ------------------------------
def get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return str(key).strip()
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "").strip()


def ask_teacher(question):
    api_key = get_api_key()

    if not api_key:
        return (
            "안녕하세요! 선생님이에요. 😊\n\n"
            "AI 연결 설정이 없어 기본 안내를 드릴게요.\n\n"
            "1. 화면의 글씨를 천천히 읽어 보세요.\n"
            "2. 원하는 메뉴 버튼을 한 번 누르세요.\n"
            "3. 다음 화면에서 안내하는 순서대로 진행하세요.\n"
            "4. 잘못 눌렀다면 이전 단계로 돌아가세요.\n\n"
            "손이 불편하거나 어려운 화면이 나오면 "
            "직원에게 도움을 요청하셔도 괜찮아요."
        )

    system_prompt = (
        "당신은 키오스크 사용이 어려운 어르신을 가르치는 "
        "친절한 한국어 선생님입니다. 쉬운 단어와 짧은 문장으로 "
        "설명하세요. 한 번에 1~3단계씩 안내하세요. "
        "실수해도 괜찮다고 안심시켜 주세요. "
        "실제 결제나 개인정보 입력을 요구하지 마세요."
    )

    contents = []
    for item in st.session_state.history[-6:]:
        contents.append({
            "role": item["role"],
            "parts": [{"text": item["text"]}],
        })

    contents.append({
        "role": "user",
        "parts": [{"text": question}],
    })

    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 700,
        },
    }

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash-lite:generateContent"
        f"?key={api_key}"
    )

    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            data = json.loads(response.read().decode("utf-8"))

        candidates = data.get("candidates", [])
        if not candidates:
            return "답변을 만들지 못했어요. 질문을 다시 입력해 주세요."

        parts = candidates[0].get("content", {}).get("parts", [])
        answer = "\n".join(
            p["text"] for p in parts
            if isinstance(p, dict) and p.get("text")
        ).strip()

        if not answer:
            return "답변이 비어 있어요. 다시 질문해 주세요."

        st.session_state.history.extend([
            {"role": "user", "text": question},
            {"role": "model", "text": answer},
        ])
        return answer

    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            return "질문이 많아 잠시 기다려야 해요. 조금 뒤 다시 시도해 주세요."
        if exc.code in (400, 403):
            return "API 키 또는 Gemini API 설정을 확인해 주세요."
        return f"AI 서비스 오류가 발생했어요 (HTTP {exc.code})."

    except (urllib.error.URLError, TimeoutError):
        return "인터넷 연결을 확인하고 다시 시도해 주세요."

    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return "답변을 읽는 중 문제가 생겼어요. 다시 시도해 주세요."

    except Exception:
        return "예상하지 못한 오류가 발생했어요. 기본 연습 기능을 이용해 주세요."


# ------------------------------
# 홈
# ------------------------------
def home():
    header()
    st.header("어서 오세요, 어르신! 🌷")
    st.write(
        "키오스크 사용이 어려우신가요?\n\n"
        "괜찮아요. 실제 돈을 내지 않고 천천히 연습할 수 있어요."
    )
    st.success("실수해도 괜찮습니다. 언제든 다시 시작할 수 있어요.")

    if st.button("① 키오스크가 어려운 이유 알아보기"):
        st.session_state.page = "difficulty"
        st.rerun()

    if st.button("② 키오스크 사용법 연습하기"):
        reset_practice()
        st.rerun()

    if st.button("③ AI 선생님에게 질문하기"):
        st.session_state.page = "teacher"
        st.rerun()

    st.divider()
    st.subheader("기억해 주세요")
    st.write("• 서두르지 않아도 됩니다.")
    st.write("• 화면의 글씨를 먼저 읽어 보세요.")
    st.write("• 어려우면 직원에게 도움을 요청하세요.")


# ------------------------------
# 어려움 안내
# ------------------------------
def difficulty():
    header()
    st.header("키오스크가 왜 어려울까요?")

    st.subheader("🔎 글씨가 너무 작아요")
    st.write("화면을 천천히 살펴보세요. 가능하다면 글씨 확대 기능을 이용하세요.")

    st.subheader("🔎 어떤 버튼을 눌러야 할지 모르겠어요")
    st.write("화면 위쪽부터 읽고 한 번에 하나씩 선택하세요.")

    st.subheader("🔎 잘못 누를까 봐 걱정돼요")
    st.write("주문을 확정하기 전에 메뉴와 금액을 확인하세요.")

    st.subheader("🔎 손이 불편해서 누르기 어려워요")
    st.write("무리하지 마세요. 직원에게 도움을 요청해도 괜찮습니다.")

    st.info("실제 키오스크는 기계마다 화면과 버튼이 다를 수 있어요.")

    if st.button("주문 연습 시작하기"):
        reset_practice()
        st.rerun()

    if st.button("홈으로 돌아가기"):
        st.session_state.page = "home"
        st.rerun()


# ------------------------------
# 주문 연습
# ------------------------------
def practice():
    header()

    steps = [
        "음료 고르기",
        "음료 온도 선택하기",
        "매장 또는 포장 선택하기",
        "주문 내용 확인하기",
        "가상 결제 연습하기",
    ]

    step = max(0, min(st.session_state.step, 4))
    st.session_state.step = step

    st.progress((step + 1) / len(steps))
    st.caption(f"{step + 1}단계 / {len(steps)}단계")
    st.header(steps[step])

    if step == 0:
        st.info("원하는 음료의 큰 버튼을 눌러 보세요.")

        menus = [
            ("☕ 아메리카노", "아메리카노"),
            ("🥛 카페라테", "카페라테"),
            ("🍵 녹차", "녹차"),
            ("🍊 오렌지 주스", "오렌지 주스"),
        ]

        for label, value in menus:
            if st.button(label, key="menu_" + value):
                st.session_state.menu = value
                st.session_state.step = 1
                st.rerun()

    elif step == 1:
        st.write(f"선택한 음료: **{st.session_state.menu}**")
        st.radio(
            "어떤 음료로 드실까요?",
            ["따뜻하게", "차갑게"],
            key="temperature",
        )

        if st.button("다음 단계로"):
            st.session_state.step = 2
            st.rerun()

    elif step == 2:
        st.radio(
            "어디에서 드실 건가요?",
            ["매장에서 먹기", "포장하기"],
            key="order_type",
        )

        if st.button("선택 완료"):
            st.session_state.step = 3
            st.rerun()

    elif step == 3:
        prices = {
            "아메리카노": 3000,
            "카페라테": 4000,
            "녹차": 3500,
            "오렌지 주스": 4000,
        }
        price = prices.get(st.session_state.menu, 3000)

        st.subheader("주문 내용을 확인하세요.")
        st.write(f"음료: {st.session_state.menu}")
        st.write(f"온도: {st.session_state.temperature}")
        st.write(f"주문 방법: {st.session_state.order_type}")
        st.metric("연습용 가격", f"{price:,}원")
        st.info("실제 주문이나 결제는 발생하지 않습니다.")

        if st.button("주문 내용이 맞아요"):
            st.session_state.step = 4
            st.rerun()

    elif step == 4:
        st.info("연습용 결제입니다. 실제 돈은 결제되지 않습니다.")

        st.radio(
            "결제 방법을 골라 보세요.",
            ["카드", "간편결제", "직원에게 도움 요청"],
            key="payment",
        )

        if st.button("가상 결제 연습 완료"):
            st.session_state.page = "complete"
            st.rerun()

    st.divider()
    left, right = st.columns(2)

    with left:
        if step > 0 and st.button("← 이전 단계"):
            st.session_state.step -= 1
            st.rerun()

    with right:
        if st.button("처음부터 다시"):
            reset_practice()
            st.rerun()

    if st.button("AI 선생님에게 도움받기"):
        st.session_state.page = "teacher"
        st.rerun()

    if st.button("홈으로 돌아가기"):
        st.session_state.page = "home"
        st.rerun()


# ------------------------------
# 연습 완료
# ------------------------------
def complete():
    header()
    st.balloons()
    st.header("🎉 참 잘하셨어요!")
    st.success("키오스크 주문 연습을 모두 마쳤습니다.")

    st.write("오늘 배운 순서를 기억해 보세요.")
    st.write("1. 음료 고르기")
    st.write("2. 온도 선택하기")
    st.write("3. 매장 또는 포장 선택하기")
    st.write("4. 주문 내용 확인하기")
    st.write("5. 결제 방법 확인하기")

    st.warning("실제 키오스크에서는 결제 전에 금액을 꼭 확인하세요.")

    if st.button("한 번 더 연습하기"):
        reset_practice()
        st.rerun()

    if st.button("AI 선생님과 대화하기"):
        st.session_state.page = "teacher"
        st.rerun()

    if st.button("홈으로 돌아가기"):
        st.session_state.page = "home"
        st.rerun()


# ------------------------------
# AI 선생님과 대화
# ------------------------------
def teacher():
    header()
    st.header("👩‍🏫 AI 선생님")

    st.write(
        "궁금한 점을 편하게 질문해 주세요. "
        "선생님이 쉬운 말로 설명해 드릴게요."
    )

    examples = [
        "노인들이 키오스크를 어려워하는 이유를 알려 주세요.",
        "키오스크 쉽게 쓰는 법을 알려 주세요.",
        "카드 결제는 어떻게 하나요?",
        "잘못 눌렀을 때 어떻게 해야 하나요?",
        "손이 불편하면 어떻게 도움받나요?",
    ]

    for i, example in enumerate(examples):
        if st.button(example, key=f"example_{i}"):
            st.session_state.question = example
            st.session_state.answer = ""
            st.rerun()

    with st.form("question_form", clear_on_submit=True):
        question = st.text_area(
            "선생님께 질문하기",
            placeholder="여기에 질문을 적어 주세요.",
            max_chars=1000,
        )
        submitted = st.form_submit_button("질문하기")

    if submitted and question.strip():
        st.session_state.question = question.strip()
        st.session_state.answer = ""

    if st.session_state.question:
        st.markdown("### 내 질문")
        st.write(st.session_state.question)

        if not st.session_state.answer:
            with st.spinner("선생님이 답변을 준비하고 있어요..."):
                st.session_state.answer = ask_teacher(
                    st.session_state.question
                )

        st.markdown("### 선생님의 답변")
        st.markdown(st.session_state.answer)

        if st.button("다른 질문하기"):
            st.session_state.question = ""
            st.session_state.answer = ""
            st.rerun()

    st.divider()

    if st.button("키오스크 연습으로 돌아가기"):
        st.session_state.page = "practice"
        st.rerun()

    if st.button("홈으로 돌아가기"):
        st.session_state.page = "home"
        st.rerun()


# ------------------------------
# 실행
# ------------------------------
def main():
    pages = {
        "home": home,
        "difficulty": difficulty,
        "practice": practice,
        "complete": complete,
        "teacher": teacher,
    }

    try:
        pages.get(st.session_state.page, home)()
    except Exception:
        st.error(
            "화면에서 문제가 발생했어요. "
            "홈으로 돌아가 다시 시도해 주세요."
        )
        if st.button("홈으로 돌아가기", key="error_home"):
            st.session_state.page = "home"
            st.rerun()


if __name__ == "__main__":
    main()
