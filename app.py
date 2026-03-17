import streamlit as st
import google.generativeai as genai

# إعداد واجهة المستخدم
st.set_page_config(page_title="حكايات ذكية - Smart Tales", layout="centered")

# إضافة اختيار اللغة في الشريط الجانبي
language = st.sidebar.selectbox("اختر اللغة / Select Language", ["العربية", "English"])

# تخصيص النصوص بناءً على اللغة المختارة
if language == "العربية":
    title = "🪄 حكايات ذكية"
    input_label = "ماذا تريد أن تكون قصة اليوم؟"
    button_text = "تأليف القصة"
    prompt_prefix = "اكتب قصة قصيرة وممتعة للأطفال عن: "
    loading_msg = "جاري تأليف قصتك السحرية..."
    st.markdown("""<style> .stApp { direction: rtl; text-align: right; } </style>""", unsafe_check_html=True)
else:
    title = "🪄 Smart Tales"
    input_label = "What should today's story be about?"
    button_text = "Generate Story"
    prompt_prefix = "Write a short, engaging children's story about: "
    loading_msg = "Crafting your magic story..."
    st.markdown("""<style> .stApp { direction: ltr; text-align: left; } </style>""", unsafe_check_html=True)

st.title(title)

# مدخلات المستخدم
user_topic = st.text_input(input_label)

if st.button(button_text):
    if user_topic:
        with st.spinner(loading_msg):
            try:
                # إعداد Gemini (تأكد من وضع المفتاح الخاص بك هنا)
                # genai.configure(api_key="YOUR_API_KEY")
                model = genai.GenerativeModel('gemini-pro')
                
                # إرسال الطلب بناءً على اللغة
                full_prompt = f"{prompt_prefix} {user_topic}"
                response = model.generate_content(full_prompt)
                
                # عرض القصة
                st.markdown("---")
                st.write(response.text)
                
            except Exception as e:
                st.error("حدث خطأ ما، يرجى المحاولة لاحقاً." if language == "العربية" else "Something went wrong, please try again.")
    else:
        st.warning("يرجى إدخال عنوان أو فكرة!" if language == "العربية" else "Please enter a topic or idea!")
