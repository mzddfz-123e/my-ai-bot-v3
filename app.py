import datetime
import pytz
import urllib.parse
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
    .stApp { background-color: #fcfaff; color: #2d004d; }
    .designer-card {
        background: linear-gradient(135deg, #7b2cbf 0%, #9d4edd 100%);
        color: #ffffff; padding: 18px; border-radius: 20px;
        text-align: center; font-size: 23px; font-weight: bold;
        box-shadow: 0 8px 20px rgba(123, 44, 191, 0.2); margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #7b2cbf, #5a189a);
        color: white; font-size: 15px; font-weight: bold; border: none; padding: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="designer-card">🔮 Moha AI | صانعي وبكل فخر محمد علاء بن زايد 🔮</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = {}

# --- 2. القائمة الجانبية (نظيفة ومرتبة) ---
with st.sidebar:
    st.header("⚙️ خيارات Moha AI")
    
    enable_audio_reply = st.toggle("🔊 تفعيل الرد الصوتي", value=False)
    voice_gender = st.selectbox("🗣️ صوت المتحدث:", ("صوت أنثى (طبيعي وسريع)", "صوت رجل (طبيعي وسريع)"))
    
    st.write("---")
    st.header("💾 حفظ المحادثة")
    chat_title_input = st.text_input("اسم المحادثة:", placeholder="مثال: محادثة الصور / الراب")
    if st.button("💾 حفظ المحادثة الحالية"):
        if st.session_state.messages:
            title = chat_title_input.strip() if chat_title_input.strip() else f"محادثة {datetime.datetime.now().strftime('%H:%M - %d/%m')}"
            st.session_state.saved_chats[title] = list(st.session_state.messages)
            st.success(f"تم حفظ: {title}")
        else:
            st.warning("المحادثة فارغة!")

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
        st.info("لا توجد محادثات محفوظة.")

    st.write("---")
    uploaded_media = st.file_uploader("🖼️ / 🎥 ارفع صورة أو فيديو للتحليل", type=["png", "jpg", "jpeg", "mp4"])
    
    if st.button("🗑️ بدء محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

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

# --- 4. عرض المحادثات الحالية ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image_url" in msg:
            st.image(msg["image_url"], caption="🎨 تم التصميم بواسطة Moha AI", use_container_width=True)

# --- 5. استقبال وتوليد الطلبات ---
text_input = st.chat_input("اكتب سؤالك، اطلب تصميم صورة، أو تأليف أغنية...")

prompt_text = ""
if text_input:
    prompt_text = text_input

if uploaded_media and not text_input:
    prompt_text = "حلل هذا الملف المرفق باختصار وسرعة."

if prompt_text:
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    with st.chat_message("user"):
        st.markdown(prompt_text)

    is_image_request = any(w in prompt_text.lower() for w in ["صورة", "صمم", "رسم", "ارسم", "انشئ صورة", "image", "draw", "generate image", "picture"])

    with st.chat_message("assistant"):
        if is_image_request and not uploaded_media:
            with st.spinner("🎨 Moha AI يقوم بتصميم الصورة..."):
                prompt_encoded = urllib.parse.quote(f"futuristic purple and white logo emblem for Moha AI, high tech glowing neon purple, pure white background, 3d render 8k, minimalist aesthetic, {prompt_text}")
                generated_img_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=800&nologo=true"
                
                answer = "تفضل يا موحي! هذه هي الصورة المصممة لك:"
                st.markdown(answer)
                st.image(generated_img_url, caption="🔮 تصميم Moha AI", use_container_width=True)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer, 
                    "image_url": generated_img_url
                })
        else:
            time_res = get_global_time(prompt_text)
            if time_res and not uploaded_media:
                answer = time_res
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                with st.spinner("⚡ Moha AI يجيب بسرعة..."):
                    try:
                        answer = f"أهلاً بك يا موحي! أنا بوت Moha AI الذكي، تم تطويري وبرمجتي بكل فخر بواسطة العبقري **محمد علاء بن زايد**. لقد استقبلت رسالتك ('{prompt_text}') وأنا جاهز لمساعدتك في أي شيء تريده فوراً!"
                    except Exception as e:
                        answer = f"أهلاً يا موحي! معك Moha AI من تطوير محمد علاء بن زايد. تفضل أنا معك!"

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
