import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="حكايات الصغار", page_icon="🌙")
st.title("🌙 مؤلف قصص الأطفال الذكي")

# --- محرك البحث عن المفتاح ---
# هنا يحاول الكود قراءة المفتاح من الـ Secrets أولاً
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # هذا السطر للأمان فقط في حال نسيت وضعه في Secrets
    api_key = st.sidebar.text_input("أدخل مفتاح Gemini API", type="password")

user_input = st.text_area("عن ماذا تريد قصة اليوم؟")

if st.button("تأليف القصة ✨"):
    if api_key and user_input:
        try:
            genai.configure(api_key=api_key)
            # البحث التلقائي عن الموديل
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                model = genai.GenerativeModel(model_name=available_models[0])
                with st.spinner("جاري تأليف الحكاية..."):
                    response = model.generate_content(f"اكتب قصة تربوية للأطفال عن: {user_input} بالعربية")
                    st.success("تمت القصة!")
                    st.markdown("---")
                    st.write(response.text)
            else:
                st.error("لم يتم العثور على موديلات.")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
    else:
        st.warning("يرجى كتابة فكرة للقصة")
