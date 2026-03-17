import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# إعداد الصفحة
st.set_page_config(page_title="حكايات ذكية - Smart Tales", layout="centered")

# اختيار اللغة
language = st.sidebar.selectbox("اختر اللغة / Select Language", ["العربية", "English"])

# تخصيص الإعدادات بناءً على اللغة
if language == "العربية":
    title = "🪄 حكايات ذكية"
    input_label = "ماذا تريد أن تكون قصة اليوم؟"
    button_text = "تأليف القصة"
    prompt_prefix = "اكتب قصة قصيرة وممتعة للأطفال عن: "
    loading_msg = "جاري تأليف قصتك السحرية..."
    audio_label = "استمع للقصة 🔊"
    st.markdown('<style>body{direction: rtl; text-align: right;}</style>', unsafe_allow_html=True)
else:
    title = "🪄 Smart Tales"
    input_label = "What should today's story be about?"
    button_text = "Generate Story"
    prompt_prefix = "Write a short, engaging children's story about: "
    loading_msg = "Crafting your magic story..."
    audio_label = "Listen to the story 🔊"
    st.markdown('<style>body{direction: ltr; text-align: left;}</style>', unsafe_allow_html=True)

st.title(title)

# --- نظام جلب مفتاح API الذكي ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("أدخل مفتاح Gemini API يدوياً", type="password")

# مدخلات المستخدم
user_topic = st.text_input(input_label)

if st.button(button_text):
    if user_topic:
        if not api_key: # إذا لم يتوفر مفتاح في السكرت ولا في الشريط الجانبي
            st.error("يرجى توفير مفتاح API للبدء!" if language == "العربية" else "Please provide an API Key!")
        else:
            with st.spinner(loading_msg):
                try:
                    # التعديل الهام هنا: نستخدم المتغير api_key الذي عرفناه بالأعلى
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    full_prompt = f"{prompt_prefix} {user_topic}"
                    response = model.generate_content(full_prompt)
                    story_text = response.text
                    
                    # عرض القصة
                    st.markdown("---")
                    st.write(story_text)
                    
                    # إضافة الصوت
                    st.markdown(f"### {audio_label}")
                    lang_code = 'ar' if language == "العربية" else 'en'
                    tts = gTTS(text=story_text, lang=lang_code)
                    
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format='audio/mp3')
                    
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.warning("يرجى إدخال عنوان!" if language == "العربية" else "Please enter a topic!")
