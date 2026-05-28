import streamlit as st
import pandas as pd
import time
from google import genai
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="ScholarNode Academy", layout="wide")

# تهيئة الجلسة لضمان عدم وجود أخطاء AttributeError
if "user_data" not in st.session_state:
    st.session_state.user_data = {"name": "Courage", "credit": 187, "expiry": "27-06-2026", "plan": "10000"}

# دالة المعالجة بـ Gemini
def process_with_gemini(task, content):
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(model="gemini-2.0-flash", contents=f"{task}: {content}")
        return response.text
    except:
        return "⚠️ عذراً، حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى."

# --- الواجهة الجانبية (الشريط الجانبي) ---
with st.sidebar:
    st.markdown("### 🛠️ إدارة الحساب الحالي")
    st.info(f"💳 الكود النشط حالياً: SN-10K-KXRB9POB")
    st.metric("الرصيد المتبقي", f"{st.session_state.user_data['credit']} محاولة")
    st.warning(f"📅 تاريخ انتهاء الصلاحية: {st.session_state.user_data['expiry']}")
    st.caption(f"IQD نوع الباقة: {st.session_state.user_data['plan']}")
    if st.button("تسجيل الخروج"):
        st.session_state.clear()
        st.rerun()

# --- الواجهة الرئيسية (الترحاب + التحميل) ---
st.markdown("""
<style>
    .welcome-banner { background-color: #2563eb; color: white; padding: 20px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="welcome-banner"><h2>✨ مرحباً دكتور {st.session_state.user_data["name"]}</h2><p>لديك رصيد محاولات يبلغ حالياً: {st.session_state.user_data["credit"]} محاولة جاهزة للاستخدام الأكاديمي.</p></div>', unsafe_allow_html=True)

st.write("📂 ارفع مستند البحث أو الوثيقة أو الصورة هنا:")
uploaded_file = st.file_uploader("Upload", type=["pdf", "docx", "png", "jpg"])

# --- التبويبات الكاملة (حسب طلبك) ---
tabs = st.tabs([
    "📄 معاينة ومناقشة المستند", 
    "🎓 المراجعة الأكاديمية والنقدية", 
    "🌍 الترجمة الأكاديمية الاحترافية", 
    "⚖️ ترجمة المستندات القانونية",
    "🎨 صياغة المخططات الهيكلية", 
    "🔍 توضيح الصورة بدقة", 
    "🎙️ توليد الصوت الطبيعي", 
    "💬 المستشار الذكي"
])

# تنفيذ تبويب "صياغة المخططات" كمثال للالتزام بالتفاصيل
with tabs[4]:
    st.subheader("🎨 صياغة وهندسة المخططات الهيكلية والأكاديمية")
    user_input = st.text_area("ادخل عناصر المخطط العلمي أو الهيكلي المطلوب توصيفه وتدقيقه لغوياً:")
    if st.button("ابدأ هندسة وتدقيق المخطط"):
        if st.session_state.user_data["credit"] >= 5:
            with st.spinner("جاري المعالجة..."):
                result = process_with_gemini("صمم مخططاً هيكلياً لـ:", user_input)
                st.write(result)
                st.session_state.user_data["credit"] -= 5 # خصم المحاولات
        else:
            st.error("رصيدك غير كافي!")

st.markdown("---")
st.markdown("<center>ScholarNode Academy © 2026</center>", unsafe_allow_html=True)
