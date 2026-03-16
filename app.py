import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="حكايات الصغار", page_icon="🌙")
st.title("🌙 مؤلف قصص الأطفال الذكي")

with st.sidebar:
    st.header("⚙️ الإعدادات")
    api_key = st.text_input("أدخل مفتاح Gemini API", type="password")

user_input = st.text_area("عن ماذا تريد قصة اليوم؟")

if st.button("تأليف القصة ✨"):
    if api_key and user_input:
        try:
            genai.configure(api_key=api_key)
            # استخدام البحث التلقائي عن الموديل لتجنب أخطاء 404
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                model = genai.GenerativeModel(model_name=available_models[0])
                with st.spinner("جاري تأليف الحكاية..."):
                    response = model.generate_content(f"اكتب قصة تربوية للأطفال عن: {user_input} بالعربية")
                    st.success("تمت القصة!")
                    st.markdown("---")
                    st.write(response.text)
            else:
                st.error("لم يتم العثور على موديلات متاحة.")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
    else:
        st.warning("تأكد من وضع المفتاح ووصف القصة")
