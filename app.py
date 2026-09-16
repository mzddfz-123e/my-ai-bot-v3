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

# تصميم أنيق مع دائرة الصوت السريعة
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
    
    .mic-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 15px;
        background: #ffffff;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(123, 44, 191, 0.15);
        border: 2px solid #9d4edd;
        margin: 10px 0 20px 0;
    }
    .mic-circle {
        width: 75px;
        height: 75px;
        background: linear-gradient(135deg, #7b2cbf 0%, #9d4edd 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 20px rgba(157, 78, 221, 0.5);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(157, 78, 221, 0.7); }
        70% { transform: scale(1.05); box-shadow: 0 0 0 12px rgba(157, 78, 221, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(157, 78, 221, 0); }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="designer-card">🔮 Moha AI | صانعي وبكل فخر محمد علاء بن زايد 🔮</div>', unsafe_allow_html=True)

# --- 2. المفتاح والسجل ---
raw_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
api_key = str(raw_key).strip()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. الوقت السريع ---
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

# --- 4. القائمة الجانبية ---
with st.sidebar:
    st.header("⚙️ إعدادات Moha AI")
    enable_voice_mode = st.toggle("🎙️ تحدث بصوتك مباشرة", value=False)
    enable_audio_reply = st.toggle("🔊 تفعيل الرد الصوتي", value=True)
    
    voice_gender = st.selectbox("🗣️ صوت المتحدث:", ("صوت أنثى (طبيعي وسريع)", "صوت رجل (طبيعي وسريع)"))
    
    st.write("---")
    uploaded_media = st.file_uploader("🖼️ / 🎥 ارفع صورة أو فيديو", type=["png", "jpg", "jpeg", "mp4"])
    
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

# --- 5. عرض المحادثات ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. نمط الصوتي مثل ChatGPT ---
audio_bytes = None
if enable_voice_mode:
    st.markdown("""
        <div class="mic-container">
            <div class="mic-circle">
                <span style="font-size: 32px; color: white;">🎙️</span>
            </div>
            <p style="font-weight: bold; color: #7b2cbf; margin-top: 8px; font-size: 14px;">Moha AI يتحدث معك بسرعة فاقة.. اضغط التسجيل وتكلم</p>
        </div>
    """, unsafe_allow_html=True)
    audio_bytes = st.audio_input("اضغط المايك وتكلم")

text_input = st.chat_input("اكتب سؤالك هنا بسرعة...")

prompt_text = ""
file_part = None

if text_input:
    prompt_text = text_input
elif audio_bytes:
    prompt_text = "أجبني بصوتك بطلاقة وسرعة وبشكل مختصر ومباشر."
    audio_b64 = base64.b64encode(audio_bytes.read()).decode('utf-8')
    file_part = {"inline_data": {"mime_type": "audio/wav", "data": audio_b64}}

if uploaded_media and not text_input:
    prompt_text = "حلل هذا الملف المرفق باختصار وسرعة."
    file_b64 = base64.b64encode(uploaded_media.getvalue()).decode('utf-8')
    file_part = {"inline_data": {"mime_type": uploaded_media.type, "data": file_b64}}

# --- 7. معالجة الإجابة والتحدث بطريقة فائقة السرعة والطلاقة ---
if prompt_text:
    if not api_key:
        st.error("مفتاح API غير متوفر.")
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
                with st.spinner("⚡ Moha AI يجيب الآن..."):
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
                        
                        parts = [{"text": prompt_text}]
                        if file_part:
                            parts.append(file_part)

                        payload = {
                            "systemInstruction": {
                                "parts": [
                                    {
                                        "text": "أنت Moha AI، مساعد ذكي ومباشر. أجوبتك فائقة السرعة والطلاقة وبلا تعقيد أو إطالة. إذا تم سؤالك عن من صنعك أو طورك، أجب فوراً وبكل فخر أن صانعك ومطورك هو محمد علاء بن زايد."
                                    }
                                ]
                            },
                            "contents": [{"parts": parts}]
                        }
                        
                        response = requests.post(url, json=payload, timeout=8)
                        res_json = response.json()

                        if "candidates" in res_json:
                            answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        else:
                            answer = "حاول مرة أخرى."

                    except Exception as e:
                        answer = "حدث خطأ بسيط في الاتصال، أعد المحاولة."

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # تشغيل الصوت بطلاقة وسرعة ممتازة (Rate 1.15 ليكون النطق سريعاً وطبيعياً)
                if enable_audio_reply and answer:
                    pitch_val = "0.85" if "رجل" in voice_gender else "1.05"
                    clean_text = answer.replace("'", "").replace("\n", " ").replace("*", "").replace('"', '')
                    
                    tts_script = f"""
                    <script>
                    window.speechSynthesis.cancel();
                    var msg = new SpeechSynthesisUtterance("{clean_text}");
                    msg.lang = 'ar-SA';
                    msg.rate = 1.15;
                    msg.pitch = {pitch_val};
                    window.speechSynthesis.speak(msg);
                    </script>
                    """
                    st.components.v1.html(tts_script, height=0)
