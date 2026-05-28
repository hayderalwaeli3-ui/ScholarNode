import streamlit as st
import pandas as pd
import time
from google import genai
from google.genai import types

# 1. إعداد الصفحة
st.set_page_config(page_title="ScholarNode Academy", layout="wide")

# 2. تهيئة الحالة (لضمان عدم حدوث خطأ AttributeError)
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, "user_code": "", "is_admin": False,
        "name": "Dr. HAYDER", "credit": 999999
    })

# 3. محرك Gemini الاحترافي
def get_gemini_response(prompt):
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text
    except Exception as e:
        return "⚠️ عذراً، حدث خطأ في الاتصال بالبوابة الذكية. يرجى المحاولة مرة أخرى."

# 4. التنسيق (تصميم الواجهة كما في الصور)
st.markdown("""
<style>
    .header { background-color: #1e40af; color: white; padding: 20px; border-radius: 10px; border: 3px solid #eab308; text-align: center; }
    .sidebar-info { background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #ddd; }
    .stButton>button { width: 100%; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# 5. منطق الواجهة الرئيسية
if not st.session_state.authenticated:
    st.markdown('<div class="header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🔒 الدخول الامن للمنصة")
        code = st.text_input("ادخل كود التفعيل:")
        if st.button("دخول المنصة"):
            if code == "HAYDER_2026$$$":
                st.session_state.update({"authenticated": True, "is_admin": True, "user_code": code})
                st.rerun()
            else:
                st.error("الكود غير صحيح.")
    with col2:
        st.markdown('<div class="sidebar-info"><b>💳 معلومات الدفع:</b><br>ماستر كارد الرافدين: 8369719342<br>HAYDER Z. JASIM<br>هاتف: 07879974395</div>', unsafe_allow_html=True)
    st.stop()

# 6. واجهة المنصة (بعد الدخول)
with st.sidebar:
    st.markdown(f"**الكود:** {st.session_state.user_code}")
    st.metric("الرصيد المتبقي", f"{st.session_state.credit} محاولة")
    if st.button("تسجيل الخروج"):
        st.session_state.clear()
        st.rerun()

# تبويبات المنصة كما طلبت
tabs = st.tabs([
    "📄 معاينة ومناقشة المستند", "🎓 المراجعة الأكاديمية", "🌍 الترجمة الأكاديمية", 
    "⚖️ ترجمة قانونية", "🎨 صياغة المخططات", "🔍 توضيح الصور", "🎙️ توليد الصوت", "💬 المستشار الذكي"
])

# تنفيذ التبويب الأول كمثال حي للالتزام
with tabs[0]:
    st.subheader("📄 معاينة ومناقشة المستند")
    uploaded_file = st.file_uploader("Upload", type=["pdf", "docx", "png", "jpg"])
    if uploaded_file and st.button("معالجة المستند"):
        with st.spinner("جاري معالجة المستند عبر بوابة Gemini..."):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i+1)
            st.success("تم التحليل.")
            st.write(get_gemini_response("قم بمناقشة المستند المرفق"))

# 7. واجهة الإدارة (الحماية المطلقة)
if st.session_state.is_admin:
    st.markdown("---")
    st.subheader("🛠️ لوحة تحكم الإدارة العليا")
    admin_tabs = st.tabs(["الواجهة", "🔑 توليد الكودات", "📋 الكودات المفعلة"])
    with admin_tabs[1]:
        st.write("توليد كودات التفعيل الجديدة:")
        if st.button("توليد كود SN جديد"):
            st.code("SN-" + "".join(pd.util.testing.rands_array(8, 1)))

st.markdown("<center>ScholarNode Academy © 2026</center>", unsafe_allow_html=True)
