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
# CSS FIXES - NO OVERLAY BLOCKING SCROLL
# ==========================================
st.markdown(
    """
    <style>
    /* Prevent pull-to-refresh - works on both html and body */
    html {
        overscroll-behavior-y: none !important;
        height: 100%;
        overflow: auto;
    }
    
    body {
        overscroll-behavior-y: none !important;
        overflow-x: hidden;
        /* Allow normal scrolling but prevent bounce refresh */
        touch-action: pan-y pinch-zoom;
        min-height: 100%;
    }
    
    /* Prevent scroll anchoring jumps */
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
    
    /* Prevent zoom on mobile inputs */
    input, textarea, select {
        font-size: 16px !important;
    }
    
    /* Smooth scrolling */
    .stApp {
        scroll-behavior: smooth;
    }
    
    /* Button touch optimization */
    button, .stButton {
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
    }
    
    /* Audio player optimization */
    audio {
        width: 100%;
        max-width: 100%;
    }
    
    /* Floating action button style for Start Over */
    .floating-btn-container {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        display: flex;
        gap: 10px;
        background: rgba(255, 255, 255, 0.95);
        padding: 10px 20px;
        border-radius: 50px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Hide Streamlit default elements that cause issues */
    .stDeployButton, .stSpinner {
        display: none !important;
    }
    </style>
    
    <!-- CRITICAL: Prevent pull-to-refresh with JavaScript -->
    <script>
    (function() {
        let startY = 0;
        
        // Prevent pull-to-refresh by blocking touchstart at top of page
        document.addEventListener('touchstart', function(e) {
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchmove', function(e) {
            let currentY = e.touches[0].clientY;
            let isAtTop = (window.scrollY || document.documentElement.scrollTop) <= 0;
            
            // If pulling down at top of page, prevent default
            if (isAtTop && currentY > startY) {
                e.preventDefault();
            }
        }, { passive: false });
        
        // Restore scroll position after rerun
        if (window.scrollY > 0) {
            setTimeout(function() {
                window.scrollTo(0, window.scrollY);
            }, 100);
        }
    })();
    </script>
    """,
    unsafe_allow_html=True
)

# ==========================================
# LANGUAGE SELECTION
# ==========================================
language = st.sidebar.selectbox(
    "اختر اللغة / Select Language", 
    ["العربية", "English"],
    index=0 if st.session_state.language == "العربية" else 1
)

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
    start_over_text = "🔄 بدء جديد"
    prompt_prefix = "اكتب قصة قصيرة وممتعة للأطفال عن: "
    loading_msg = "جاري تأليف قصتك السحرية..."
    audio_label = "🔊 استمع للقصة"
    error_api = "يرجى توفير مفتاح API للبدء!"
    error_topic = "يرجى إدخال موضوع!"
    error_generate = "عذراً، لم نتمكن من توليد القصة. الخطأ: "
    
    st.markdown('<div class="arabic-text">', unsafe_allow_html=True)
    
else:
    title = "🪄 Smart Tales"
    input_label = "What should today's story be about?"
    button_text = "✨ Generate Story"
    clear_button_text = "🗑️ Clear Story"
    start_over_text = "🔄 Start Over"
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
# INPUT FORM
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
    genai.configure(api_key=api_key, transport="rest")
    
    model_names_to_try = [
        'gemini-2.5-flash',
        'gemini-3.5-flash'
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
# DISPLAY STORY
# ==========================================
if st.session_state.story_text:
    st.markdown("---")
    
    # Story content with proper text wrapping
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
    
    # ==========================================
    # FLOATING START OVER BUTTON (Always visible)
    # ==========================================
    st.markdown("---")
    st.markdown(
        """
        <style>
        .floating-action-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 15px 25px;
            font-size: 1.1em;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .floating-action-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(0,0,0,0.4);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Use columns for the start over button at bottom
    _, _, right_col = st.columns([1, 1, 1])
    with right_col:
        if st.button(start_over_text, key="start_over_btn", use_container_width=True):
            st.session_state.story_text = None
            st.session_state.audio_data = None
            st.session_state.last_topic = ""
            st.rerun()

if language == "العربية":
    st.markdown('</div>', unsafe_allow_html=True)
