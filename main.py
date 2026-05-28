import streamlit as st
import pandas as pd
import os
import random
import string
import time
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# --- إعدادات الصفحة الأساسية ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")

# --- بروتوكول الحماية والتهيئة (Session State) ---
def init_session():
    defaults = {"auth": False, "user_code": "", "is_admin": False, "credit": 0}
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

# --- محرك Gemini الموحد ---
def get_gemini_response(prompt):
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text
    except Exception as e:
        return f"⚠️ خطأ تقني: {str(e)}"

# --- التصميم والألوان (CSS) ---
st.markdown("""
<style>
    .welcome-header { background-color: #1e40af; border: 4px solid #eab308; padding: 20px; text-align: center; border-radius: 15px; color: #000; }
    .payment-box { border: 2px solid #1e40af; padding: 15px; border-radius: 10px; background-color: #f8fafc; }
    .styled-table { width: 100%; border-collapse: collapse; background-color: #fef08a; color: #1e3a8a; }
    .styled-table th { background-color: #bae6fd; padding: 10px; text-align: center; }
    .styled-table td { padding: 10px; border: 1px solid #fde047; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- واجهة الدخول (أولاً) ---
if not st.session_state.auth:
    st.markdown('<div class="welcome-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🔒 الدخول الامن للمنصة")
        code = st.text_input("ادخل كود التفعيل:")
        if st.button("دخول المنصة"):
            if code == "HAYDER_2026$$$":
                st.session_state.update({"auth": True, "user_code": code, "is_admin": True})
                st.rerun()
            else:
                # هنا سيتم الربط بقاعدة البيانات (CSV) لاحقاً
                st.error("كود غير صحيح")
    with col2:
        st.markdown('<div class="payment-box"><b>معلومات الدفع:</b><br>ماستر كارد الرافدين: 8369719342<br>HAYDER Z. JASIM<br>هاتف: 07879974395</div>', unsafe_allow_html=True)
        st.markdown("<table class='styled-table'><tr><th>الفئة</th><th>المحاولات</th></tr><tr><td>1000</td><td>20</td></tr><tr><td>5000</td><td>100</td></tr><tr><td>10000</td><td>200</td></tr></table>", unsafe_allow_html=True)
    st.markdown("<br><center><b>ScholarNode Academy © 2026</b></center>", unsafe_allow_html=True)
    st.stop()

# --- واجهة المستخدم (بعد الدخول) ---
st.sidebar.markdown(f"**🎟️ الكود:** {st.session_state.user_code}")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.clear()
    st.rerun()

# --- تبويبات المنصة ---
tabs = st.tabs(["📄 معاينة", "🎓 مراجعة", "🌍 ترجمة", "⚖️ قانونية", "🎨 صور", "🔍 توضيح", "🎙️ صوت", "💬 مستشار"])

with tabs[0]: # مثال: تبويب المعاينة
    st.subheader("📄 معاينة ومناقشة المستند")
    file = st.file_uploader("Upload", type=["pdf", "docx", "png", "jpg"])
    if file and st.button("معالجة"):
        with st.spinner("جاري المعالجة..."):
            bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                bar.progress(i+1)
            st.markdown(get_gemini_response("قم بتحليل الملف."))

# --- حساب الإدارة (يظهر فقط للإدارة) ---
if st.session_state.is_admin:
    st.markdown("---")
    st.subheader("🛠️ لوحة تحكم الإدارة")
    admin_tabs = st.tabs(["الواجهة", "🔑 توليد الكودات", "📋 الكودات المفعلة"])
    with admin_tabs[1]:
        plan = st.selectbox("اختر الفئة:", [1000, 5000, 10000])
        if st.button("توليد كود"):
            new_code = "SN-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            st.code(new_code)
            st.success("تم توليد الكود!")
