import streamlit as st
import pandas as pd
import os
import random
import string
import time
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# 1. إعداد الصفحة
st.set_page_config(page_title="ScholarNode Academy", layout="wide")

# محرك Gemini المدمج (للاتصال الذكي)
def get_gemini_response(prompt):
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ خطأ في الاتصال: {str(e)}"

# إدارة قاعدة البيانات والسياسة المالية
DB_FILE = "scholarnode_data.csv"
def init_db():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["code", "remaining", "expiry_date", "plan_type"])
        df.to_csv(DB_FILE, index=False)
init_db()

# تنسيق CSS الأنيق
st.markdown("""
<style>
    .welcome-box { background-color: #1e40af; border: 4px solid #eab308; padding: 20px; border-radius: 15px; text-align: center; color: #000; }
    .payment-box { border: 2px solid #1e40af; padding: 15px; border-radius: 10px; background-color: #f8fafc; }
    .stTable { background-color: #fef08a; }
</style>
""", unsafe_allow_html=True)

# منطق الدخول
if "authenticated" not in st.session_state:
    st.markdown('<div class="welcome-box"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🔒 الدخول الآمن للمنصة")
        code = st.text_input("ادخل كود التفعيل:")
        if st.button("دخول المنصة"):
            if code == "HAYDER_2026$$$":
                st.session_state.update({"auth": True, "admin": True, "code": code})
                st.rerun()
            else:
                # [إضافة منطق التحقق من CSV هنا]
                st.error("كود غير صالح")
    
    with col2:
        st.markdown('<div class="payment-box"><b>معلومات الدفع:</b><br>الرافدين: 8369719342<br>HAYDER Z. JASIM</div>', unsafe_allow_html=True)
    st.stop()

# الواجهة بعد الدخول
st.sidebar.markdown(f"**الكود:** {st.session_state.code}")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.clear()
    st.rerun()

# التبويبات (مثال للتبويب الأول)
tabs = st.tabs(["📄 معاينة", "🎓 مراجعة", "🌍 ترجمة", "⚖️ قانونية", "🎨 صور", "🔍 توضيح", "🎙️ صوت", "💬 مستشار"])

with tabs[0]:
    st.subheader("📄 معاينة ومناقشة المستند")
    uploaded_file = st.file_uploader("Upload", type=["pdf", "docx", "jpg", "png"])
    if uploaded_file and st.button("بدء المعالجة"):
        with st.spinner("جاري المعالجة..."):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.02)
                progress.progress(i+1)
            st.markdown(get_gemini_response("تحليل المستند المرفوع..."))

# لوحة الإدارة
if st.session_state.get("admin"):
    st.sidebar.markdown("---")
    st.subheader("🛠️ لوحة الإدارة")
    admin_tabs = st.tabs(["الواجهة", "توليد كودات", "الكودات المفعلة"])
    # [إضافة منطق توليد الأكواد]

st.markdown("<center>ScholarNode Academy © 2026</center>", unsafe_allow_html=True)
