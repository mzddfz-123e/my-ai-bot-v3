import os
import requests
import datetime
import pytz
import base64
import streamlit as st

# --- 1. إعدادات الصفحة والتصميم العالي الجودة ---
st.set_page_config(
    page_title="المساعد الذكي الشامل",
    page_icon="⚡",
    layout="centered"
)

# تصميم زجاجي وعصري
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    stChatMessage { direction: rtl; text-align: right; }
    
    /* بطاقة الهوية والصانع */
    .designer-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 25px;
    }
    
    /* تحسين زر الإرسال والحقول */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #2a5298;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="designer-card">⚡ المساعد الذكي | صانعي وبكل فخر محمد علاء بن زايد ⚡</div>', unsafe_allow_html=True)
st.caption("ذكاء اصطناعي متطور للإجابة عن الأسئلتك، تحليل الصور، معرفة الأوقات، وفتح التطبيقات.")

# --- 2. إدارة مفتاح API والسجل ---
raw_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
api_key = str(raw_key).strip()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. أدوات مساعدة (وقت الدول والتطبيقات) ---
def get_country_time(query):
    """البحث عن التوقيت المحلي للدول"""
    query_lower = query.lower()
    timezones = {
        "مصر": "Africa/Cairo", "السعودية": "Asia/Riyadh", "الامارات": "Asia/Dubai",
        "قطر": "Asia/Qatar", "الكويت": "Asia/Kuwait", "تونس": "Africa/Tunis",
        "الجزائر": "Africa/Algiers", "المغرب": "Africa/Casablanca", "تركيا": "Europe/Istanbul",
        "لندن": "Europe/London", "أمريكا": "America/New_York", "نيويورك": "America/New_York"
    }
    for country, zone in timezones.items():
        if country in query_lower:
            tz = pytz.timezone(zone)
            now = datetime.datetime.now(tz)
            return f"الوقت الحالي في {country} هو: {now.strftime('%I:%M %p (%Y-%m-%d)')}"
    return None

def check_app_redirect(query):
    """إنشاء روابط لفتح التطبيقات"""
    query_lower = query.lower()
    if "واتس" in query_lower or "whatsapp" in query_lower:
        return "[اضغط هنا لفتح واتساب مباشرة](https://wa.me/)"
    elif "يوتيوب" in query_lower or "youtube" in query_lower:
        return "[اضغط هنا لفتح يوتيوب](https://youtube.com)"
    elif "جوجل" in query_lower or "google" in query_lower:
        return "[اضغط هنا لفتح محرك البحث جوجل](https://google.com)"
    return None

# --- 4. القائمة الجانبية (رفع الصور والخيار الصوتي) ---
with st.sidebar:
    st.header("⚙️ أدوات المساعد")
    uploaded_image = st.file_uploader("📷 ارفع صورة للتحليل", type=["png", "jpg", "jpeg"])
    enable_audio = st.checkbox("🔊 تفعيل الرد الصوتي", value=False)
    
    if st.button("مسح السجل / محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# --- 5. عرض المحادثات ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("اكتب سؤالك، اطلب فتح تطبيق، أو استفسر عن الوقت...")

# --- 6. معالجة الإرسال والذكاء الاصطناعي ---
if user_input or uploaded_image:
    if not api_key:
        st.error("لم يتم العثور على مفتاح API في إعدادات Secrets.")
    else:
        prompt_text = user_input if user_input else "اشرح لي هذه الصورة بالتفصيل."
        st.session_state.messages.append({"role": "user", "content": prompt_text})
        
        with st.chat_message("user"):
            st.markdown(prompt_text)
            if uploaded_image:
                st.image(uploaded_image, width=250)

        # التحقق أولاً من أدوات الوقت والتطبيقات
        time_response = get_country_time(prompt_text)
        app_response = check_app_redirect(prompt_text)
        
        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير وتوليد الاستجابة..."):
                if time_response:
                    answer = time_response
                elif app_response:
                    answer = f"تفضل: {app_response}"
                else:
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
                        
                        parts = [{"text": prompt_text}]
                        
                        # معالجة الصورة إذا تم رفعها
                        if uploaded_image:
                            img_bytes = uploaded_image.getvalue()
                            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                            parts.append({
                                "inline_data": {
                                    "mime_type": uploaded_image.type,
                                    "data": img_base64
                                }
                            })

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

                # دعم الرد الصوتي باستخدام المتصفح
                if enable_audio:
                    clean_text = answer.replace("'", "").replace("\n", " ")
                    tts_script = f"""
                    <script>
                    var msg = new SpeechSynthesisUtterance('{clean_text}');
                    msg.lang = 'ar-SA';
                    window.speechSynthesis.speak(msg);
                    </script>
                    """
                    st.components.v1.html(tts_script, height=0)
