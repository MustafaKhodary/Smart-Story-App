import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'story_text' not in st.session_state:
    st.session_state.story_text = None
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'last_topic' not in st.session_state:
    st.session_state.last_topic = ""
if 'language' not in st.session_state:
    st.session_state.language = "العربية"

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="حكايات ذكية - Smart Tales", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CRITICAL CSS FIXES: Scroll + Arabic + Touch
# ==========================================
st.markdown(
    """
    <style>
    /* Prevent pull-to-refresh and overscroll bounce */
    html, body {
        overscroll-behavior-y: none !important;
        overflow-x: hidden;
        touch-action: pan-y;
    }
    
    /* Prevent scroll anchoring from jumping */
    * {
        overflow-anchor: none !important;
    }
    
    /* Fix Arabic text rendering */
    .arabic-text {
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: bidi-override !important;
        word-wrap: break-word;
        white-space: normal;
        font-family: 'Segoe UI', 'Tahoma', 'Geneva', 'Verdana', sans-serif;
        line-height: 1.8;
    }
    
    /* Ensure input fields don't trigger zoom on mobile */
    input, textarea, select {
        font-size: 16px !important;
    }
    
    /* Fix Streamlit's default container behavior */
    .stApp {
        overflow-y: auto;
        overscroll-behavior-y: none;
    }
    
    /* Prevent button focus from causing layout jumps */
    button, .stButton {
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
    }
    
    /* Prevent iframe and audio player from causing reruns */
    iframe, audio {
        pointer-events: auto;
        touch-action: none;
    }
    </style>
    
    <!-- JavaScript to prevent scroll-triggered reruns -->
    <script>
    // Prevent passive touch events from triggering Streamlit rerun
    document.addEventListener('touchmove', function(e) {
        e.preventDefault = false;
    }, { passive: true });
    
    // Prevent scroll position from causing state issues
    if ('scrollRestoration' in history) {
        history.scrollRestoration = 'manual';
    }
    </script>
    """,
    unsafe_allow_html=True
)

# ==========================================
# LANGUAGE SELECTION (with session state)
# ==========================================
language = st.sidebar.selectbox(
    "اختر اللغة / Select Language", 
    ["العربية", "English"],
    index=0 if st.session_state.language == "العربية" else 1
)

# Update session state if language changed
if language != st.session_state.language:
    st.session_state.language = language
    st.session_state.story_text = None
    st.session_state.audio_data = None
    st.rerun()

# ==========================================
# LOCALIZATION
# ==========================================
if language == "العربية":
    title = "🪄 حكايات ذكية"
    input_label = "ماذا تريد أن تكون قصة اليوم؟"
    button_text = "✨ تأليف القصة"
    clear_button_text = "🗑️ مسح القصة"
    prompt_prefix = "اكتب قصة قصيرة وممتعة للأطفال عن: "
    loading_msg = "جاري تأليف قصتك السحرية..."
    audio_label = "🔊 استمع للقصة"
    error_api = "يرجى توفير مفتاح API للبدء!"
    error_topic = "يرجى إدخال موضوع!"
    error_generate = "عذراً، لم نتمكن من توليد القصة. الخطأ: "
    
    # Apply RTL direction safely
    st.markdown('<div class="arabic-text">', unsafe_allow_html=True)
    
else:
    title = "🪄 Smart Tales"
    input_label = "What should today's story be about?"
    button_text = "✨ Generate Story"
    clear_button_text = "🗑️ Clear Story"
    prompt_prefix = "Write a short, engaging children's story about: "
    loading_msg = "Crafting your magic story..."
    audio_label = "🔊 Listen to the story"
    error_api = "Please provide an API Key!"
    error_topic = "Please enter a topic!"
    error_generate = "Sorry, couldn't generate the story. Error: "

st.title(title)

# ==========================================
# API KEY MANAGEMENT
# ==========================================
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input(
        "أدخل مفتاح Gemini API يدوياً" if language == "العربية" else "Enter Gemini API Key manually", 
        type="password"
    )

# ==========================================
# INPUT FORM (Prevents rerun on input changes)
# ==========================================
with st.form(key="story_form", clear_on_submit=False):
    user_topic = st.text_input(
        input_label, 
        value=st.session_state.last_topic,
        key="topic_input"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        generate_submitted = st.form_submit_button(
            button_text, 
            use_container_width=True
        )
    
    with col2:
        clear_submitted = st.form_submit_button(
            clear_button_text, 
            use_container_width=True
        )

# ==========================================
# CLEAR BUTTON HANDLER
# ==========================================
if clear_submitted:
    st.session_state.story_text = None
    st.session_state.audio_data = None
    st.session_state.last_topic = ""
    st.rerun()

# ==========================================
# GENERATION LOGIC
# ==========================================
def generate_story(topic, api_key, lang):
    """Generate story and return text + audio"""
    genai.configure(api_key=api_key)
    
    model_names_to_try = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-flash-latest',
        'gemini-1.5-flash'
    ]
    
    story_text = None
    last_error = ""
    
    for name in model_names_to_try:
        try:
            model = genai.GenerativeModel(name)
            full_prompt = f"{prompt_prefix} {topic}"
            response = model.generate_content(full_prompt)
            
            if response and response.text:
                story_text = response.text
                break
        except Exception as e:
            last_error = str(e)
            continue
    
    if not story_text:
        return None, None, last_error
    
    # Generate audio
    lang_code = 'ar' if lang == "العربية" else 'en'
    try:
        tts = gTTS(text=story_text, lang=lang_code)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_data = audio_fp.getvalue()
    except Exception as e:
        audio_data = None
    
    return story_text, audio_data, None

# ==========================================
# GENERATE BUTTON HANDLER
# ==========================================
if generate_submitted:
    if not user_topic:
        st.warning(error_topic)
    elif not api_key:
        st.error(error_api)
    else:
        with st.spinner(loading_msg):
            story, audio, error = generate_story(user_topic, api_key, language)
            
            if story:
                st.session_state.story_text = story
                st.session_state.audio_data = audio
                st.session_state.last_topic = user_topic
                st.rerun()
            else:
                st.error(f"{error_generate} {error}")

# ==========================================
# DISPLAY STORY (ISOLATED FROM INPUT - Won't lose on scroll)
# ==========================================
if st.session_state.story_text:
    st.markdown("---")
    
    # Wrap Arabic text in a div with proper class
    if language == "العربية":
        st.markdown(
            f'<div class="arabic-text" style="font-size: 1.2em; padding: 20px;">{st.session_state.story_text}</div>',
            unsafe_allow_html=True
        )
    else:
        st.write(st.session_state.story_text)
    
    # Audio player
    if st.session_state.audio_data:
        st.markdown(f"### {audio_label}")
        st.audio(io.BytesIO(st.session_state.audio_data), format='audio/mp3')

# Close Arabic div if needed
if language == "العربية":
    st.markdown('</div>', unsafe_allow_html=True)
