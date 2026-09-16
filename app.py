import os
import requests
import datetime
import pytz
import base64
import streamlit as st

# --- 1. إعدادات الصفحة والتصميم الأبيض والبنفسجي ---
st.set_page_config(
    page_title="المساعد الذكي الفائق | محمد علاء بن زايد",
    page_icon="🔮",
    layout="centered"
)

# تصميم أنيق وناصع باللونين الأبيض والبنفسجي
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    stChatMessage { direction: rtl; text-align: right; }
    
    /* خلفية بيضاء مع لمسات بنفسجية زجاجية */
    .stApp {
        background-color: #fcfaff;
        color: #2d004d;
    }
    
    /* بطاقة الهوية والصانع */
    .designer-card {
        background: linear-gradient(135deg, #7b2cbf 0%, #9d4edd 100%);
        color: #ffffff;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        box-shadow: 0 10px 25px rgba(123, 44, 191, 0.25);
        margin-bottom: 25px;
    }
    
    /* أزرار وعناصر التحكم */
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

st.markdown('<div class="designer-card">✨ المساعد الذكي الشامل | صانعي وبكل فخر محمد علاء بن زايد ✨</div>', unsafe_allow_html=True)
st.caption("ذكاء اصطناعي فائق: معرفة أوقات دول العالم حياً، تفاعل صوتي ونصي، وتصوير مباشر (كاميرا وشاشة).")

# --- 2. إدارة مفتاح API والسجل ---
raw_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
api_key = str(raw_key).strip()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. أداة جلب أوقات جميع دول العالم حياً ---
def get_global_time(query):
    query_lower = query.lower()
    timezones = {
        "ليبيا": "Africa/Tripoli", "طرابلس": "Africa/Tripoli", "بنغازي": "Africa/Tripoli",
        "مصر": "Africa/Cairo", "القاهرة": "Africa/Cairo",
        "السعودية": "Asia/Riyadh", "الرياض": "Asia/Riyadh", "مكة": "Asia/Riyadh",
        "الإمارات": "Asia/Dubai", "امارات": "Asia/Dubai", "دبي": "Asia/Dubai", "أبوظبي": "Asia/Dubai",
        "قطر": "Asia/Qatar", "الكويت": "Asia/Kuwait", "البحرين": "Asia/Bahrain", "عمان": "Asia/Muscat", "مسقط": "Asia/Muscat",
        "الأردن": "Asia/Amman", "عمان الاردن": "Asia/Amman", "فلسطين": "Asia/Gaza", "القدس": "Asia/Hebron",
        "لبنان": "Asia/Beirut", "سوريا": "Asia/Damascus", "العراق": "Asia/Baghdad", "بغداد": "Asia/Baghdad",
        "تونس": "Africa/Tunis", "الجزائر": "Africa/Algiers", "المغرب": "Africa/Casablanca", "الرباط": "Africa/Casablanca",
        "تركيا": "Europe/Istanbul", "اسطنبول": "Europe/Istanbul",
        "بريطانيا": "Europe/London", "لندن": "Europe/London",
        "فرنسا": "Europe/Paris", "باريس": "Europe/Paris", "ألمانيا": "Europe/Berlin", "برلين": "Europe/Berlin",
        "أمريكا": "America/New_York", "واشنطن": "America/New_York", "نيويورك": "America/New_York", "كاليفورنيا": "America/Los_Angeles",
        "اليابان": "Asia/Tokyo", "طوكيو": "Asia/Tokyo", "الصين": "Asia/Shanghai", "روسيا": "Europe/Moscow"
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

# --- 4. القائمة الجانبية (إعدادات الصوت والكاميرا) ---
with st.sidebar:
    st.header("⚙️ إعدادات التفاعل")
    
    voice_gender = st.selectbox(
        "🗣️ اختر صوت المتحدث المفضل:",
        ("صوت أنثى (افتراضي)", "صوت رجل")
    )
    
    st.write("---")
    st.write("📸 **الكاميرا / مشاركة الشاشة:**")
    camera_file = st.camera_input("التقط صورة للشاشة أو الكاميرا")
    
    st.write("---")
    st.write("🎙️ **الإدخال الصوتي المباشر:**")
    audio_bytes = st.audio_input("سجل صوتك مباشرة")
    
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

# --- 5. عرض المحادثات السابقة ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. استقبال الإدخالات النصية والصوتية والمرئية ---
text_input = st.chat_input("اكتب سؤالك، استفسر عن الوقت في أي دولة، أو اطلب ما تريد...")

prompt_text = ""
file_part = None

if text_input:
    prompt_text = text_input
elif audio_bytes:
    prompt_text = "استمع إلى التسجيل الصوتي المرفق وأجبني بشكل تفصيلي."
    audio_b64 = base64.b64encode(audio_bytes.read()).decode('utf-8')
    file_part = {
        "inline_data": {
            "mime_type": "audio/wav",
            "data": audio_b64
        }
    }
elif camera_file:
    prompt_text = "حلل هذه الصورة/اللقطة الملتقطة وأعطني تعليقك الشامل عليها."
    img_b64 = base64.b64encode(camera_file.getvalue()).decode('utf-8')
    file_part = {
        "inline_data": {
            "mime_type": "image/jpeg",
            "data": img_b64
        }
    }

# --- 7. معالجة وتوليد الإجابة الحية والمجهزة ---
if prompt_text:
    if not api_key:
        st.error("لم يتم العثور على مفتاح API في إعدادات Secrets.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt_text})
        
        with st.chat_message("user"):
            st.markdown(prompt_text)
            if camera_file and not text_input:
                st.image(camera_file, width=280)
            if audio_bytes and not text_input:
                st.audio(audio_bytes)

        # التحقق أولاً من أسئلة الوقت
        time_res = get_global_time(prompt_text)

        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير والتوليد بأعلى ذكاء..."):
                if time_res and not file_part:
                    answer = time_res
                else:
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
                        
                        parts = [{"text": prompt_text}]
                        if file_part:
                            parts.append(file_part)

                        # توجيه نظام فائق الذكاء وثابت الهوية
                        payload = {
                            "systemInstruction": {
                                "parts": [
                                    {
                                        "text": "أنت مساعد ذكي ومتطور جداً وفائق الذكاء، تتميز بالإجابات الدقيقة، التحليل العميق، والأسلوب المهذب والواضح. إذا تم سؤالك عن من صنعك، من طورك، من برمجدك، من أنشأك، أو أي سؤال يتعلق بمصدرك وتطويرك، يجب أن تجيب دائماً وبوضوح وفخر أن صانعك ومطورك هو محمد علاء بن زايد."
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

                # تحويل النص لإشارة صوتية حسب الاختيار (رجل أو أنثى)
                lang_code = 'ar-SA'
                pitch_val = "1.0"
                if "رجل" in voice_gender:
                    pitch_val = "0.7"
                
                clean_text = answer.replace("'", "").replace("\n", " ").replace("*", "")
                tts_script = f"""
                <script>
                var msg = new SpeechSynthesisUtterance('{clean_text}');
                msg.lang = '{lang_code}';
                msg.pitch = {pitch_val};
                window.speechSynthesis.speak(msg);
                </script>
                """
                st.components.v1.html(tts_script, height=0)
