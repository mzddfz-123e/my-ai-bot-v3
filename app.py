import os
import requests
import streamlit as st

st.set_page_config(
    page_title="المساعد الذكي الشامل",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    stChatMessage { direction: rtl; text-align: right; }
    .designer-tag {
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        color: #155724;
        background-color: #d4edda;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 25px;
        border: 1px solid #c3e6cb;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="designer-tag">✨ صانعي وبكل فخر محمد علاء بن زايد ✨</div>', unsafe_allow_html=True)

st.title("🤖 المساعد الذكي الشامل")
st.caption("ذكاء اصطناعي مخصص للإجابة عن أسئلتك فوراً")

with st.sidebar:
    st.header("⚙️ الخيارات")
    if st.button("مسح السجل / محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

raw_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
api_key = str(raw_key).strip()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("اكتب سؤالك هنا...")

if user_input:
    if not api_key:
        st.error("لم يتم العثور على مفتاح API في إعدادات Secrets.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            with st.chat_message("assistant"):
                with st.spinner("جاري التفكير وتوليد الإجابة..."):
                    # إرسال طلب مباشر واستخراج الاستجابة الحقيقية للخطأ
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    payload = {"contents": [{"parts": [{"text": user_input}]}]}
                    
                    response = requests.post(url, json=payload)
                    res_json = response.json()

                    if "candidates" in res_json:
                        answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        # طباعة الخطأ القادم من Google بالتفصيل
                        st.error(f"تفاصيل الخطأ من جوجل: {res_json}")

        except Exception as e:
            st.error(f"حدث خطأ في النظام: {e}")
