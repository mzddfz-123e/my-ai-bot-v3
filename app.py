import os
import requests
import datetime
import pytz
import base64
import streamlit as st

# --- 1. إعدادات الصفحة والتصميم (Moha AI) ---
st.set_page_config(
    page_title="Moha AI | محمد علاء بن زايد",
    page_icon="🔮",
    layout="centered"
)

# تصميم بنفسجي وأبيض أنيق + تصميم دائرة المايك التفاعلية
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    stChatMessage { direction: rtl; text-align: right; }
    
    .stApp {
        background-color: #fcfaff;
        color: #2d004d;
    }
    
    /* بطاقة التعريف الفاخرة */
    .designer-card {
        background: linear-gradient(135deg, #7b2cbf 0%, #9d4edd 100%);
        color: #ffffff;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        box-shadow: 0 10px 25px rgba(123, 44, 191, 0.25);
        margin-bottom: 25px;
    }
    
    /* تصميم زر ودائرة المايك على طريقة ChatGPT */
    .mic-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
        background: #ffffff;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(123, 44, 191, 0.15);
        border: 2px solid #9d4edd;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .mic-circle {
        width: 85px;
        height: 85px;
        background: linear-gradient(135deg, #7b2cbf 0%, #9d4edd 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 20px rgba(157, 78, 221, 0.5);
        animation: pulse 2s infinite;
        margin-bottom: 10px;
    }
    @keyframes pulse {
        0% { transform: scale(0.98); box-shadow: 0 0 0 0 rgba(157, 78, 221, 0.7); }
        70% { transform: scale(1.05); box-shadow: 0 0 0 15px rgba(157, 78, 221, 0); }
        100% { transform: scale(0.98); box-shadow: 0 0 0 0 rgba(157, 78, 221, 0); }
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #7b2cbf, #5a189a);
        color: white;
        font-size: 16px;
        font-weight: bold;
        border: none;
        padding: 12px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #5a189a, #3c096c);
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="designer-card">🔮 Moha AI | صانعي وبكل فخر محمد علاء بن زايد 🔮</div>', unsafe_allow_html=True)

# --- 2. إدارة مفتاح API والسجل ---
raw_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
api_key = str(raw_key).strip()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. أداة أوقات العالم السريعة ---
def get_global_time(query):
    query_lower = query.lower()
    timezones = {
        "ليبيا": "Africa/Tripoli", "طرابلس": "Africa/Tripoli", "بنغازي": "Africa/Tripoli",
        "مصر": "Africa/Cairo", "القاهرة": "Africa/Cairo",
        "السعودية": "Asia/Riyadh", "الرياض": "Asia/Riyadh", "مكة": "Asia/Riyadh",
        "الإمارات": "Asia/Dubai", "دبي": "Asia/Dubai",
        "قطر": "Asia/Qatar", "الكويت": "Asia/Kuwait", "البحرين": "Asia/Bahrain", "عمان": "Asia/Muscat",
        "الأردن": "Asia/Amman", "فلسطين": "Asia/Gaza", "لبنان": "Asia/Beirut", "العراق": "Asia/Baghdad",
        "تونس": "Africa/Tunis", "الجزائر": "Africa/Algiers", "المغرب": "Africa/Casablanca",
        "تركيا": "Europe/Istanbul", "بريطانيا": "Europe/London", "لندن": "Europe/London",
        "فرنسا": "Europe/Paris", "ألمانيا": "Europe/Berlin", "أمريكا": "America/New_York", "نيويورك": "America/New_York"
    }
    
    for country, zone in timezones.items():
        if country in query_lower:
            tz = pytz.timezone(zone)
            now = datetime.datetime.now(tz)
            return f"🕒 الوقت الحالي في **{country}** هو: **{now.strftime('%I:%M:%S %p')}** (بتاريخ: {now.strftime('%Y-%m-%d')})"
    
    if "الوقت" in query_lower or "الساعة" in query_lower:
        tz = pytz.timezone("Africa/Tripoli")
        now = datetime.datetime.now(tz)
        return f"🕒 الوقت الحالي بتوقيت ليبيا: **{now.strftime('%I:%M:%S %p')}** (بتاريخ: {now.strftime('%Y-%m-%d')})"
        
    return None

# --- 4. القائمة الجانبية (رفع وسائط وإعدادات الصوت) ---
with st.sidebar:
    st.header("⚙️ خيارات Moha AI")
    
    enable_voice_mode = st.toggle("🎙️ تحدث بصوتك مع Moha AI", value=False)
    enable_audio_reply = st.toggle("🔊 تفعيل الرد الصوتي تلقائياً", value=True)
    
    voice_gender = st.selectbox(
        "🗣️ اختر صوت المتحدث:",
        ("صوت أنثى (افتراضي)", "صوت رجل")
    )
    
    st.write("---")
    uploaded_media = st.file_uploader("🖼️ / 🎥 ارفع صورة أو فيديو للتحليل", type=["png", "jpg", "jpeg", "mp4", "mov", "avi"])
    
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

# --- 5. عرض المحادثات ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. نمط التحدث الصوتي على طريقة ChatGPT عند التفعيل ---
audio_bytes = None
if enable_voice_mode:
    st.markdown("""
        <div class="mic-container">
            <div class="mic-circle">
                <span style="font-size: 38px;">🎙️</span>
            </div>
            <p style="font-weight: bold; color: #7b2cbf; margin-top: 5px;">Moha AI يستمع إليك الآن... اضغط المايك وتحدث</p>
        </div>
    """, unsafe_allow_html=True)
    audio_bytes = st.audio_input("اضغط وتسجل هنا لتكلم Moha AI مباشرة")

text_input = st.chat_input("اكتب سؤالك هنا...")

prompt_text = ""
file_part = None

if text_input:
    prompt_text = text_input
elif audio_bytes:
    prompt_text = "استمع إلى هذا المقطع الصوتي وأجبني بصوتك وتفصيل الإجابة."
    audio_b64 = base64.b64encode(audio_bytes.read()).decode('utf-8')
    file_part = {"inline_data": {"mime_type": "audio/wav", "data": audio_b64}}

if uploaded_media and not text_input:
    prompt_text = "حلل هذا الملف المرفق (صورة أو فيديو) وأعطني تفاصيل كاملة عنه."
    file_b64 = base64.b64encode(uploaded_media.getvalue()).decode('utf-8')
    file_part = {"inline_data": {"mime_type": uploaded_media.type, "data": file_b64}}

# --- 7. معالجة وتوليد الإجابة ---
if prompt_text:
    if not api_key:
        st.error("لم يتم العثور على مفتاح API في إعدادات Secrets.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt_text})
        
        with st.chat_message("user"):
            st.markdown(prompt_text)
            if uploaded_media and not text_input:
                if "image" in uploaded_media.type:
                    st.image(uploaded_media, width=300)
                elif "video" in uploaded_media.type:
                    st.video(uploaded_media)

        time_res = get_global_time(prompt_text)

        with st.chat_message("assistant"):
            if time_res and not file_part:
                answer = time_res
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                with st.spinner("Moha AI يجيب فوراً..."):
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
                        
                        parts = [{"text": prompt_text}]
                        if file_part:
                            parts.append(file_part)

                        payload = {
                            "systemInstruction": {
                                "parts": [
                                    {
                                        "text": "أنت Moha AI، مساعد ذكي ومبتكر وسريع جداً. إذا تم سؤالك عن من صنعك، من طورك، من برمجدك، أو من أنشأك، يجب أن تجيب دائماً وبوضوح وفخر أن صانعك ومطورك هو محمد علاء بن زايد."
                                    }
                                ]
                            },
                            "contents": [{"parts": parts}]
                        }
                        
                        response = requests.post(url, json=payload, timeout=12)
                        res_json = response.json()

                        if "candidates" in res_json:
                            answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        else:
                            answer = "حدث خطأ أثناء معالجة الطلب، يرجى إعادة المحاولة."

                    except Exception as e:
                        answer = f"حدث خطأ في الاتصال: {e}"

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # تشغيل الرد الصوتي تلقائياً
                if enable_audio_reply and answer:
                    pitch_val = "0.7" if "رجل" in voice_gender else "1.0"
                    clean_text = answer.replace("'", "").replace("\n", " ").replace("*", "")
                    tts_script = f"""
                    <script>
                    var msg = new SpeechSynthesisUtterance('{clean_text}');
                    msg.lang = 'ar-SA';
                    msg.pitch = {pitch_val};
                    window.speechSynthesis.speak(msg);
                    </script>
                    """
                    st.components.v1.html(tts_script, height=0)
