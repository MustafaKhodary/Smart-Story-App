import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
# Page Configuration
st.set_page_config(page_title="حكايات ذكية - Smart Tales", layout="centered")
# Language Selection
language = st.sidebar.selectbox("اختر اللغة / Select Language", ["العربية", "English"])

# Localization Settings
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
# --- API Key Management ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("أدخل مفتاح Gemini API يدوياً" if language == "العربية" else "Enter Gemini API Key manually", type="password")
# User Input
user_topic = st.text_input(input_label)
if st.button(button_text):
    if user_topic:
        if not api_key:
            st.error("يرجى توفير مفتاح API للبدء!" if language == "العربية" else "Please provide an API Key!")
        else:
            with st.spinner(loading_msg):
                try:
                    # Configure the API
                    genai.configure(api_key=api_key)
                    # FIX: Using 'gemini-1.5-flash-latest' or 'gemini-2.0-flash' which are more stable
                    # Based on the error, 'gemini-1.5-flash' might have been deprecated or requires a specific version
                    model_name = 'gemini-1.5-flash-latest' 
                    model = genai.GenerativeModel(model_name)
                    
                    full_prompt = f"{prompt_prefix} {user_topic}"
                    response = model.generate_content(full_prompt)
                    if response.text:
                        story_text = response.text
                        # Display Story
                        st.markdown("---")
                        st.write(story_text)
                        # Text-to-Speech
                        st.markdown(f"### {audio_label}")
                        lang_code = 'ar' if language == "العربية" else 'en'
                        tts = gTTS(text=story_text, lang=lang_code)
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        st.audio(audio_fp, format='audio/mp3')
                    else:
                        st.error("لم يتم توليد أي محتوى. يرجى المحاولة مرة أخرى." if language == "العربية" else "No content generated. Please try again.")
                except Exception as e:
                    # Enhanced error message for the user
                    error_msg = str(e)
                    if "404" in error_msg:
                        st.error(f"Error: Model not found. Please check if '{model_name}' is available for your API key or try 'gemini-1.5-flash'.")
                    else:
                        st.error(f"Error: {e}")
    else:
        st.warning("يرجى إدخال عنوان!" if language == "العربية" else "Please enter a topic!")
