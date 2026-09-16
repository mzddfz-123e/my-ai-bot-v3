import os
import requests
import datetime
import pytz
import base64
import streamlit as st

# --- 1. إعدادات الصفحة والتصميم العالي الجودة ---
st.set_page_config(
    page_title="المساعد الذكي الشامل | محمد علاء بن زايد",
    page_icon="⚡",
    layout="centered"
)

# تصميم زجاجي عصري (Glassmorphism Deep Dark)
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    stChatMessage { direction: rtl; text-align: right; }
    
    /* خلفية الصفحة زجاجية وفخمة */
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: #ffffff;
    }
    
    /* بطاقة الهوية والصانع */
    .designer-card {
        background: linear-gradient(135deg, #7b2cbf 0%, #3a0ca3 100%);
        color: #ffffff;
        padding: 18px;
        border-radius: 20px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 25px;
    }
    
    /* تحسين الأزرار وحقول الإدخال */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #4cc9f0, #4361ee);
        color: white;
        font-size: 16px;
        font-weight: bold;
        border: none;
        padding: 10px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="designer-card">⚡ المساعد الذكي | صانعي وبكل فخر محمد علاء بن زايد ⚡</div>', unsafe_allow_html=True)
st.caption("ذكاء اصطناعي شامل: إدخال صوتي، تحليل مقاطع فيديو وصور، معرفة الأوقات، وفتح التطبيقات.")

# --- 2. إدارة مفتاح API والسجل ---
raw_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
api_key = str(raw_key).strip()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. أدوات الوقت والتطبيقات ---
def get_country_time(query):
    """البحث عن التوقيت المحلي للدول"""
    query_lower = query.lower()
    timezones = {
        "ليبيا": "Africa/Tripoli", "طرابلس": "Africa/Tripoli",
        "مصر": "Africa/Cairo", "القاهرة": "Africa/Cairo",
        "السعودية": "Asia/Riyadh", "الرياض": "Asia/Riyadh",
        "الامارات": "Asia/Dubai", "دبي": "Asia/Dubai",
        "قطر": "Asia/Qatar", "الكويت": "Asia/Kuwait", 
        "تونس": "Africa/Tunis", "الجزائر": "Africa/Algiers", 
        "المغرب": "Africa/Casablanca", "تركيا": "Europe/Istanbul",
        "لندن": "Europe/London", "بريطانيا": "Europe/London",
        "أمريكا": "America/New_York", "نيويورك": "America/New_York"
    }
    for country, zone in timezones.items():
        if country in query_lower:
            tz = pytz.timezone(zone)
            now = datetime.datetime.now(tz)
            return f"🕒 الوقت الحالي في {country} هو: {now.strftime('%I:%M %p - بتاريخ %Y-%m-%d')}"
    
    if "الوقت" in query_lower or "الساعة" in query_lower:
        tz = pytz.timezone("Africa/Tripoli")
        now = datetime.datetime.now(tz)
        return f"🕒 الوقت الحالي (توقيت ليبيا): {now.strftime('%I:%M %p - بتاريخ %Y-%m-%d')}"
        
    return None

def check_app_redirect(query):
    """روابط فتح التطبيقات"""
    query_lower = query.lower()
    if "واتس" in query_lower or "whatsapp" in query_lower:
        return "[اضغط هنا لفتح تطبيق واتساب](https://wa.me/)"
    elif "يوتيوب" in query_lower or "youtube" in query_lower:
        return "[اضغط هنا لفتح تطبيق يوتيوب](https://youtube.com)"
    elif "جوجل" in query_lower or "google" in query_lower:
        return "[اضغط هنا لفتح محرك البحث جوجل](https://google.com)"
    return None

# --- 4. القائمة الجانبية (رفع وسائط + إدخال صوتي) ---
with st.sidebar:
    st.header("⚙️ أدوات المساعد الذكي")
    
    uploaded_file = st.file_uploader("📷 / 🎥 ارفع صورة أو فيديو للتحليل والتعديل", type=["png", "jpg", "jpeg", "mp4", "mov", "avi"])
    
    st.write("🎙️ **التحدث الصوتي المباشر:**")
    audio_bytes = st.audio_input("اضغط للتحدث بصوتك")
    
    enable_audio_reply = st.checkbox("🔊 تفعيل الإجابة الصوتية تلقائياً", value=True)
    
    if st.button("🗑️ مسح السجل / محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# --- 5. عرض محادثات السجل ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("اكتب سؤالك، اطلب الوقت، فتح تطبيق، أو استفسر عن فيديو/صورة...")

# --- 6. معالجة الطلبات ---
prompt_text = ""
file_part = None

if audio_bytes:
    prompt_text = "استمع إلى هذا المقطع الصوتي وأجبني عنه بالتفصيل."
    audio_b64 = base64.b64encode(audio_bytes.read()).decode('utf-8')
    file_part = {
        "inline_data": {
            "mime_type": "audio/wav",
            "data": audio_b64
        }
    }
elif user_input:
    prompt_text = user_input

if uploaded_file:
    if not prompt_text:
        prompt_text = "حلل هذا الملف (صورة/فيديو) واشرح لي محتواه أو أعطني نصائح لتعديله."
    
    file_b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    file_part = {
        "inline_data": {
            "mime_type": uploaded_file.type,
            "data": file_b64
        }
    }

if prompt_text:
    if not api_key:
        st.error("لم يتم العثور على مفتاح API في إعدادات Secrets.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt_text})
        
        with st.chat_message("user"):
            st.markdown(prompt_text)
            if uploaded_file:
                if "image" in uploaded_file.type:
                    st.image(uploaded_file, width=300)
                elif "video" in uploaded_file.type:
                    st.video(uploaded_file)
            if audio_bytes:
                st.audio(audio_bytes)

        # التحقق أولاً من الوقت أو التطبيقات
        time_res = get_country_time(prompt_text)
        app_res = check_app_redirect(prompt_text)
        
        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير وتوليد الإجابة..."):
                if time_res and not uploaded_file and not audio_bytes:
                    answer = time_res
                elif app_res and not uploaded_file and not audio_bytes:
                    answer = f"تفضل: {app_res}"
                else:
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                        
                        parts = [{"text": prompt_text}]
                        if file_part:
                            parts.append(file_part)

                        payload = {
                            "systemInstruction": {
                                "parts": [
                                    {
                                        "text": "أنت مساعد ذكي ومتطور جداً. إذا تم سؤالك عن من صنعك، من طورك، من برمجدك، أو من أنشأك، يجب أن تجيب دائماً وبوضوح وفخر أن صانعك ومطورك هو محمد علاء بن زايد."
                                    }
                                ]
                            },
                            "contents": [{"parts": parts}]
                        }
                        
                        response = requests.post(url, json=payload)
                        res_json = response.json()

                        if "candidates" in res_json:
                            answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        else:
                            answer = f"حدث خطأ في الاستجابة: {res_json.get('error', {}).get('message', res_json)}"

                    except Exception as e:
                        answer = f"حدث خطأ أثناء الاتصال: {e}"

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # التشغيل الصوتي للإجابة
                if enable_audio_reply and answer:
                    clean_text = answer.replace("'", "").replace("\n", " ")
                    tts_script = f"""
                    <script>
                    var msg = new SpeechSynthesisUtterance('{clean_text}');
                    msg.lang = 'ar-SA';
                    window.speechSynthesis.speak(msg);
                    </script>
                    """
                    st.components.v1.html(tts_script, height=0)
