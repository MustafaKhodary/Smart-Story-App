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
                    
                    # Based on diagnostic results, these are the correct model names for your key:
                    # We'll try the most advanced ones first.
                    model_names_to_try = [
                        'gemini-2.5-flash',      # Newest stable
                        'gemini-2.0-flash',      # High performance
                        'gemini-flash-latest',   # Reliable alias
                        'gemini-1.5-flash'       # Legacy (if still active)
                    ]
                    
                    model = None
                    story_text = None
                    last_error = ""
                    
                    for name in model_names_to_try:
                        try:
                            # Attempt to initialize and generate content
                            model = genai.GenerativeModel(name)
                            full_prompt = f"{prompt_prefix} {user_topic}"
                            response = model.generate_content(full_prompt)
                            
                            if response and response.text:
                                story_text = response.text
                                break # Success!
                        except Exception as e:
                            last_error = str(e)
                            continue # Try next model
                    
                    if story_text:
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
                        st.error(f"Error: Could not generate story. Last error: {last_error}")
                        st.info("Please ensure your API key has access to the latest Gemini models.")
               
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.warning("يرجى إدخال عنوان!" if language == "العربية" else "Please enter a topic!")
