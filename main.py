import streamlit as st
import pandas as pd
import os
import random
import string
import time
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# 1. إعداد الصفحة - يجب أن يكون أول أمر
st.set_page_config(page_title="ScholarNode", layout="wide")

# 2. تهيئة الجلسة لمنع خطأ AttributeError
if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "user_code": "", "is_admin": False})

# 3. محرك Gemini الحديث
def get_gemini_response(prompt):
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ خطأ في المعالجة: {str(e)}"

# 4. التنسيقات (CSS)
st.markdown("""
<style>
    .welcome-header-box { background-color: #1e40af; border: 4px solid #eab308; padding: 22px; text-align: center; border-radius: 14px; margin-bottom: 30px; color: #000; }
    .payment-box-luxury { border: 2px solid #1e40af; background-color: #f8fafc; padding: 18px; border-radius: 12px; }
    .styled-table { width: 100%; border-collapse: collapse; background-color: #fef08a; color: #1e3a8a; }
    .styled-table th { background-color: #bae6fd; padding: 10px; }
    .styled-table td { padding: 10px; border-bottom: 1px solid #fde047; }
</style>
""", unsafe_allow_html=True)

# 5. منطق الدخول الآمن
if not st.session_state.authenticated:
    st.markdown('<div class="welcome-header-box"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🔒 الدخول الآمن للمنصة")
        input_code = st.text_input("ادخل كود التفعيل:", type="password")
        if st.button("دخول المنصة"):
            if input_code == "HAYDER_2026$$$":
                st.session_state.update({"authenticated": True, "user_code": input_code, "is_admin": True})
                st.rerun()
            else:
                # هنا يتم التحقق من قاعدة البيانات لاحقاً
                st.error("كود غير صحيح")
    with col2:
        st.markdown('<div class="payment-box-luxury"><b>معلومات الدفع:</b><br>ماستر كارد الرافدين: 8369719342<br>HAYDER Z. JASIM<br>هاتف: 07879974395</div>', unsafe_allow_html=True)
    st.stop()

# 6. الواجهة بعد الدخول
st.sidebar.markdown(f"**🎫 الكود الحالي:** `{st.session_state.user_code}`")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.clear()
    st.rerun()

# 7. التبويبات والخدمات
tabs = st.tabs(["📄 معاينة", "🎓 مراجعة", "🌍 ترجمة", "⚖️ قانونية", "🎨 صور", "🔍 توضيح", "🎙️ صوت", "💬 مستشار"])

with tabs[0]:
    st.subheader("📄 معاينة ومناقشة المستند")
    # منطق التبويب هنا
    if st.button("بدء التحليل"):
        st.markdown(get_gemini_response("قم بتحليل المستند."))

st.markdown("<center>ScholarNode Academy © 2026</center>", unsafe_allow_html=True)
