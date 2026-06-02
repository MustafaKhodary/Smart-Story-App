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
if 'show_dialog' not in st.session_state:
    st.session_state.show_dialog = False

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="حكايات ذكية - Smart Tales", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CSS FIXES
# ==========================================
st.markdown(
    """
    <style>
    html, body {
        overscroll-behavior-y: none !important;
        overflow-x: hidden;
        touch-action: pan-y;
    }
    
    * {
        overflow-anchor: none !important;
    }
    
    .arabic-text {
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: bidi-override !important;
        word-wrap: break-word;
        white-space: normal;
        font-family: 'Segoe UI', 'Tahoma', 'Geneva', 'Verdana', sans-serif;
        line-height: 1.8;
    }
    
    input, textarea, select {
        font-size: 16px !important;
    }
    
    .stApp {
        overflow-y: auto;
        overscroll-behavior-y: none;
    }
    
    button, .stButton {
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
    }
    
    iframe, audio {
        pointer-events: auto;
        touch-action: none;
    }
    
    /* DIALOG STYLES */
    .dialog-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .dialog-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 30px;
        max-width: 90%;
        width: 380px;
        text-align: center;
        color: white;
        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    }
    
    .dialog-title {
        font-size: 1.8em;
        margin-bottom: 15px;
        font-weight: bold;
    }
    
    .dialog-text {
        font-size: 1.2em;
        margin-bottom: 25px;
        line-height: 1.6;
    }
    </style>
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
    prompt_prefix = "اكتب قصة قصيرة وممتعة للأطفال عن: "
    loading_msg = "جاري تأليف قصتك السحرية..."
    audio_label = "🔊 استمع للقصة"
    error_api = "يرجى توفير مفتاح API للبدء!"
    error_topic = "يرجى إدخال موضوع!"
    error_generate = "عذراً، لم نتمكن من توليد القصة. الخطأ: "
    
    dialog_title = "⚠️ هل تريد البدء من جديد؟"
    dialog_text = "ستفقد قصتك الحالية إذا واصلت!"
    dialog_yes = "✅ نعم، ابدأ جديد"
    dialog_no = "❌ لا، أبقَ هنا"
    
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
    
    dialog_title = "⚠️ Start Over?"
    dialog_text = "You'll lose your current story if you continue!"
    dialog_yes = "✅ Yes, Start New"
    dialog_no = "❌ No, Stay Here"

st.title(title)

# ==========================================
# DIALOG DISPLAY (When activated)
# ==========================================
if st.session_state.story_text and st.session_state.show_dialog:
    # Visual overlay
    st.markdown(
        f"""
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                    background: rgba(0,0,0,0.85); z-index: 9999; display: flex; 
                    justify-content: center; align-items: center; backdrop-filter: blur(8px);">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 25px; padding: 40px 30px; max-width: 90%; 
                        width: 400px; text-align: center; color: white; 
                        box-shadow: 0 25px 80px rgba(0,0,0,0.5);">
                <div style="font-size: 2em; margin-bottom: 10px;">🤔</div>
                <div style="font-size: 1.6em; margin-bottom: 15px; font-weight: bold;">{dialog_title}</div>
                <div style="font-size: 1.2em; margin-bottom: 30px; opacity: 0.9;">{dialog_text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Buttons (must be Streamlit native for interaction)
    c1, c2 = st.columns(2)
    with c1:
        if st.button(dialog_yes, key="dlg_yes", use_container_width=True):
            st.session_state.story_text = None
            st.session_state.audio_data = None
            st.session_state.last_topic = ""
            st.session_state.show_dialog = False
            st.rerun()
    with c2:
        if st.button(dialog_no, key="dlg_no", use_container_width=True):
            st.session_state.show_dialog = False
            st.rerun()
    
    st.stop()

# ==========================================
# SCROLL DETECTOR (JavaScript + Hidden Button)
# ==========================================
if st.session_state.story_text and not st.session_state.show_dialog:
    # Inject JavaScript to detect scroll and trigger hidden button
    scroll_detector_js = """
    <script>
    (function() {
        let lastScroll = 0;
        let triggered = false;
        
        function checkScroll() {
            if (triggered) return;
            let current = window.scrollY || document.documentElement.scrollTop;
            
            // Detect downward scroll past threshold
            if (current > lastScroll && current > 200) {
                triggered = true;
                // Find and click the hidden Streamlit button
                let buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.textContent.includes('🔄 SCROLL DETECTED')) {
                        btn.click();
                        break;
                    }
                }
            }
            lastScroll = current;
        }
        
        window.addEventListener('scroll', checkScroll, { passive: true });
        // Also check on touch end for mobile
        document.addEventListener('touchend', checkScroll, { passive: true });
    })();
    </script>
    """
    st.markdown(scroll_detector_js, unsafe_allow_html=True)
    
    # Hidden button that JavaScript will click
    if st.button("🔄 SCROLL DETECTED - HIDDEN", key="scroll_trigger", help="Auto-triggered on scroll"):
        st.session_state.show_dialog = True
        st.rerun()

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
                st.session_state.show_dialog = False
                st.rerun()
            else:
                st.error(f"{error_generate} {error}")

# ==========================================
# DISPLAY STORY
# ==========================================
if st.session_state.story_text:
    st.markdown("---")
    
    if language == "العربية":
        st.markdown(
            f'<div class="arabic-text" style="font-size: 1.2em; padding: 20px;">{st.session_state.story_text}</div>',
            unsafe_allow_html=True
        )
    else:
        st.write(st.session_state.story_text)
    
    if st.session_state.audio_data:
        st.markdown(f"### {audio_label}")
        st.audio(io.BytesIO(st.session_state.audio_data), format='audio/mp3')

if language == "العربية":
    st.markdown('</div>', unsafe_allow_html=True)
