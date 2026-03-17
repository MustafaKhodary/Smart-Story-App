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
    # تحسين طريقة الـ CSS لتجنب الخطأ
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

# مدخلات المستخدم
user_topic = st.text_input(input_label)

if st.button(button_text):
    if user_topic:
        with st.spinner(loading_msg):
            try:
                # إعداد Gemini (تأكد من إعداد المفتاح في Secrets على Streamlit Cloud)
                # genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                model = genai.GenerativeModel('gemini-pro')
                
                full_prompt = f"{prompt_prefix} {user_topic}"
                response = model.generate_content(full_prompt)
                story_text = response.text
                
                # عرض القصة
                st.markdown("---")
                st.write(story_text)
                
                # إضافة الصوت (مجاناً)
                st.markdown(f"### {audio_label}")
                lang_code = 'ar' if language == "العربية" else 'en'
                tts = gTTS(text=story_text, lang=lang_code)
                
                # حفظ الصوت في الذاكرة المؤقتة
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp, format='audio/mp3')
                
            except Exception as e:
                st.error("حدث خطأ! تأكد من إعداد مفتاح API." if language == "العربية" else "Error! Make sure API Key is set.")
    else:
        st.warning("يرجى إدخال عنوان!" if language == "العربية" else "Please enter a topic!")
