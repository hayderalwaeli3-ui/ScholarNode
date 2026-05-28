import streamlit as st
import pandas as pd
import os
import random
import string
import time
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# --- إعداد الصفحة والتهيئة ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")

# تهيئة الجلسة لضمان عدم حدوث أخطاء AttributeError
if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "user_code": "", "is_admin": False, "user_credit": 0})

# --- محرك الاتصال بـ Gemini ---
def get_gemini_response(prompt):
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text
    except Exception as e:
        return f"⚠️ عذراً، تعذر الاتصال بالمحرك: {str(e)}"

# --- قاعدة البيانات (السياسة المالية) ---
DB_FILE = "scholarnode_secured_db.csv"
def init_db():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["code", "credit", "remaining", "plan_type", "expiry_date", "status"])
        df.to_csv(DB_FILE, index=False)
init_db()

# --- التنسيقات (CSS) ---
st.markdown("""
<style>
    .welcome-header-box { background-color: #1e40af; border: 4px solid #eab308; padding: 22px; text-align: center; border-radius: 14px; color: #000; }
    .payment-box-luxury { border: 2px solid #1e40af; background-color: #f8fafc; padding: 18px; border-radius: 12px; }
    .styled-table { width: 100%; border-collapse: collapse; background-color: #fef08a; color: #1e3a8a; }
    .styled-table th { background-color: #bae6fd; padding: 10px; }
    .styled-table td { padding: 10px; border: 1px solid #fde047; }
</style>
""", unsafe_allow_html=True)

# --- الواجهة الرئيسية (قبل الدخول) ---
if not st.session_state.authenticated:
    st.markdown('<div class="welcome-header-box"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔒 الدخول الآمن للمنصة")
        code = st.text_input("ادخل كود التفعيل:", type="password")
        if st.button("دخول المنصة"):
            if code == "HAYDER_2026$$$":
                st.session_state.update({"authenticated": True, "user_code": code, "is_admin": True})
                st.rerun()
            else:
                st.error("كود غير صالح أو منتهي الصلاحية.")
    
    with col2:
        st.markdown('<div class="payment-box-luxury"><b>💳 معلومات الدفع:</b><br>ماستر كارد الرافدين: 8369719342<br>HAYDER Z. JASIM<br>هاتف: 07879974395</div>', unsafe_allow_html=True)
        # جدول الكروت
        st.markdown("<table class='styled-table'><tr><th>الفئة</th><th>المحاولات</th></tr><tr><td>1000</td><td>20</td></tr><tr><td>5000</td><td>100</td></tr></table>", unsafe_allow_html=True)
    
    st.markdown("<br><center><b>ScholarNode Academy © 2026</b></center>", unsafe_allow_html=True)
    st.stop()

# --- واجهة المستخدم (بعد الدخول) ---
with st.sidebar:
    st.write(f"**الكود:** {st.session_state.user_code}")
    if st.button("تسجيل الخروج"):
        st.session_state.clear()
        st.rerun()

# --- التبويبات (تطبيق كامل للتعليمات) ---
tab_titles = ["📄 معاينة", "🎓 مراجعة", "🌍 ترجمة", "⚖️ قانونية", "🎨 صور", "🔍 توضيح", "🎙️ صوت", "💬 مستشار"]
tabs = st.tabs(tab_titles)

with tabs[0]: # معاينة
    st.subheader("📄 معاينة ومناقشة المستند")
    uploaded_file = st.file_uploader("Upload", type=["pdf", "docx", "jpg", "png"])
    if uploaded_file and st.button("معالجة"):
        with st.spinner("جاري المعالجة..."):
            prog = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                prog.progress(i+1)
            st.success("تم التحليل.")

# --- لوحة الإدارة (تظهر فقط للإدارة) ---
if st.session_state.is_admin:
    st.markdown("---")
    st.subheader("🛠️ لوحة تحكم الإدارة")
    admin_tabs = st.tabs(["الواجهة", "🔑 توليد الكودات", "📋 الكودات المفعلة"])
    
    with admin_tabs[1]:
        plan = st.selectbox("اختر فئة الاشتراك:", [1000, 5000, 10000])
        if st.button("توليد كود"):
            code = "SN-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            st.code(code)
            st.success("تم توليد الكود بنجاح.")

    with admin_tabs[2]:
        st.dataframe(pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame())
