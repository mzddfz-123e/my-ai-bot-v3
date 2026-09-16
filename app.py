import os
import requests
import datetime
import pytz
import base64
import streamlit as st

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="Moha AI | محمد علاء بن زايد",
    page_icon="🔮",
    layout="centered"
)

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    stChatMessage { direction: rtl; text-align: right; }
    
    .stApp {
        background-color: #fcfaff;
        color: #2d004d;
    }
    
    .designer-card {
        background: linear-gradient(135deg, #7b2cbf 0%, #9d4edd 100%);
        color: #ffffff;
        padding: 18px;
        border-radius: 20px;
        text-align: center;
        font-size: 23px;
        font-weight: bold;
        box-shadow: 0 8px 20px rgba(123, 44, 191, 0.2);
        margin-bottom: 20px;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #7b2cbf, #5a189a);
        color: white;
        font-size: 15px;
        font-weight: bold;
        border: none;
        padding: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="designer-card">🔮 Moha AI | صانعي وبكل فخر محمد علاء بن زايد 🔮</div>', unsafe_allow_html=True)

# --- 2. إدارة السجل والمحفوظات ومفتاح API ---
raw_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
api_key = str(raw_key).strip()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = {}

# --- 3. أداة الوقت السريع ---
def get_global_time(query):
    query_lower = query.lower()
    timezones = {
        "ليبيا": "Africa/Tripoli", "طرابلس": "Africa/Tripoli", "بنغازي": "Africa/Tripoli",
        "مصر": "Africa/Cairo", "القاهرة": "Africa/Cairo",
        "السعودية": "Asia/Riyadh", "الرياض": "Asia/Riyadh", "مكة": "Asia/Riyadh",
        "الإمارات": "Asia/Dubai", "دبي": "Asia/Dubai", "قطر": "Asia/Qatar", "الكويت": "Asia/Kuwait",
        "تونس": "Africa/Tunis", "الجزائر": "Africa/Algiers", "المغرب": "Africa/Casablanca",
        "تركيا": "Europe/Istanbul", "بريطانيا": "Europe/London", "فرنسا": "Europe/Paris", "أمريكا": "America/New_York"
    }
    for country, zone in timezones.items():
        if country in query_lower:
            tz = pytz.timezone(zone)
            now = datetime.datetime.now(tz)
            return f"🕒 الوقت الآن في **{country}**: **{now.strftime('%I:%M:%S %p')}**"
    if "الوقت" in query_lower or "الساعة" in query_lower:
        tz = pytz.timezone("Africa/Tripoli")
        now = datetime.datetime.now(tz)
        return f"🕒 الوقت الحالي: **{now.strftime('%I:%M:%S %p')}**"
    return None

# --- 4. القائمة الجانبية (حفظ المحادثات والخيارات) ---
with st.sidebar:
    st.header("⚙️ خيارات Moha AI")
    enable_audio_reply = st.toggle("🔊 تفعيل الرد الصوتي", value=False)
    voice_gender = st.selectbox("🗣️ صوت المتحدث:", ("صوت أنثى (طبيعي وسريع)", "صوت رجل (طبيعي وسريع)"))
    
    st.write("---")
    st.header("💾 حفظ المحادثة")
    chat_title_input = st.text_input("اسم المحادثة:", placeholder="مثال: محادثة الراب / أفكار صور")
    if st.button("💾 حفظ المحادثة الحالية"):
        if st.session_state.messages:
            title = chat_title_input.strip() if chat_title_input.strip() else f"محادثة {datetime.datetime.now().strftime('%H:%M - %d/%m')}"
            st.session_state.saved_chats[title] = list(st.session_state.messages)
            st.success(f"تم حفظ: {title}")
        else:
            st.warning("المحادثة فارغة لحفظها!")

    st.write("---")
    st.header("📂 محادثاتي المحفوظة")
    if st.session_state.saved_chats:
        selected_chat = st.selectbox("اختر محادثة لاسترجاعها:", list(st.session_state.saved_chats.keys()))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📖 فتح"):
                st.session_state.messages = list(st.session_state.saved_chats[selected_chat])
                st.rerun()
        with col2:
            if st.button("❌ حذف"):
                del st.session_state.saved_chats[selected_chat]
                st.rerun()
    else:
        st.info("لا توجد محادثات محفوظة بعد.")

    st.write("---")
    uploaded_media = st.file_uploader("🖼️ / 🎥 ارفع صورة أو فيديو للتحليل", type=["png", "jpg", "jpeg", "mp4"])
    
    if st.button("🗑️ بدء محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# --- 5. عرض المحادثات الحالية ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. استقبال وتوليد الطلبات ---
text_input = st.chat_input("اكتب سؤالك، اطلب أغنية، صمم صورة، أو تحدث بالإنجليزية...")

prompt_text = ""
file_part = None

if text_input:
    prompt_text = text_input

if uploaded_media and not text_input:
    prompt_text = "حلل هذا الملف المرفق باختصار وسرعة."
    file_b64 = base64.b64encode(uploaded_media.getvalue()).decode('utf-8')
    file_part = {"inline_data": {"mime_type": uploaded_media.type, "data": file_b64}}

if prompt_text:
    if not api_key:
        st.error("لم يتم العثور على مفتاح API في إعدادات Secrets.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt_text})
        
        with st.chat_message("user"):
            st.markdown(prompt_text)

        time_res = get_global_time(prompt_text)

        with st.chat_message("assistant"):
            if time_res and not file_part:
                answer = time_res
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                with st.spinner("⚡ Moha AI يجيب بسرعة..."):
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
                        
                        parts = [{"text": prompt_text}]
                        if file_part:
                            parts.append(file_part)

                        system_instruction_text = (
                            "You are Moha AI, an exceptionally smart, fast, and helpful AI assistant created and developed by Mohamed Alaa Bin Zayed. "
                            "When speaking or answering in English, use flawless, modern, natural, and grammatically accurate English. "
                            "If asked to write songs or rap lyrics, create highly creative lyrics. "
                            "If asked to generate or design images, provide rich, highly detailed prompts in both English and Arabic. "
                            "If asked who created, developed, or built you, answer clearly and proudly in any language that your developer and creator is Mohamed Alaa Bin Zayed."
                        )

                        payload = {
                            "systemInstruction": {
                                "parts": [{"text": system_instruction_text}]
                            },
                            "contents": [{"parts": parts}]
                        }
                        
                        response = requests.post(url, json=payload, timeout=6)
                        res_json = response.json()

                        if "candidates" in res_json:
                            answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        else:
                            answer = "حدث خطأ بسيط، يرجى إعادة المحاولة."

                    except Exception as e:
                        answer = "حدث خطأ في الاتصال، حاول مرة أخرى."

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                if enable_audio_reply and answer:
                    pitch_val = "0.85" if "رجل" in voice_gender else "1.05"
                    clean_text = answer.replace("'", "").replace("\n", " ").replace("*", "").replace('"', '')
                    
                    tts_script = f"""
                    <script>
                    window.speechSynthesis.cancel();
                    var msg = new SpeechSynthesisUtterance("{clean_text}");
                    msg.lang = 'ar-SA';
                    msg.rate = 1.25;
                    msg.pitch = {pitch_val};
                    window.speechSynthesis.speak(msg);
                    </script>
                    """
                    st.components.v1.html(tts_script, height=0)
