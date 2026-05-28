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

# 2. إعداد محرك Gemini
def get_gemini_response(prompt):
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text
    except Exception as e:
        return f"⚠️ خطأ: {str(e)}"

# 3. قاعدة البيانات
DB_FILE = "scholarnode_secured_db.csv"
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["code", "credit", "remaining", "plan_type", "expiry_date", "status"])
    df.to_csv(DB_FILE, index=False)

# 4. التنسيقات (الواجهة الأنيقة)
st.markdown("""
<style>
    .welcome-header-box { background-color: #1e40af; border: 4px solid #eab308; padding: 22px; text-align: center; border-radius: 14px; color: #000; }
    .payment-box-luxury { border: 2px solid #1e40af; background-color: #f8fafc; padding: 18px; border-radius: 12px; }
    .styled-table { width: 100%; border-collapse: collapse; background-color: #fef08a; }
    .styled-table th { background-color: #bae6fd; color: #1e3a8a; padding: 10px; }
    .styled-table td { padding: 10px; border: 1px solid #fde047; color: #1e3a8a; }
</style>
""", unsafe_allow_html=True)

# 5. منطق الدخول
if "authenticated" not in st.session_state:
    st.markdown('<div class="welcome-header-box"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🔒 الدخول الآمن للمنصة")
        code = st.text_input("ادخل كود التفعيل:", type="password")
        if st.button("دخول المنصة"):
            if code == "HAYDER_2026$$$":
                st.session_state.update({"auth": True, "admin": True, "code": code})
                st.rerun()
            else:
                # [منطق التحقق من ملف CSV هنا]
                st.error("الكود غير صحيح")
    with col2:
        st.markdown('<div class="payment-box-luxury"><b>💳 معلومات الدفع:</b><br>رافدين: 8369719342<br>HAYDER Z. JASIM<br>هاتف: 07879974395</div>', unsafe_allow_html=True)
        # جدول الكروت
        st.markdown("<table class='styled-table'><tr><th>الفئة</th><th>المحاولات</th></tr><tr><td>1000</td><td>20</td></tr><tr><td>5000</td><td>100</td></tr></table>", unsafe_allow_html=True)
    st.stop()

# 6. لوحة الإدارة (توليد الكودات)
if st.session_state.get("admin"):
    admin_tabs = st.tabs(["الواجهة", "🔑 توليد الكودات", "الكودات المفعلة"])
    with admin_tabs[1]:
        st.subheader("توليد كودات التفعيل")
        if st.button("توليد كود جديد"):
            new_code = "SN-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            st.code(new_code)
            # هنا يتم حفظ الكود في ملف CSV
            st.success("تم توليد الكود!")

st.markdown("<center>ScholarNode Academy © 2026</center>", unsafe_allow_html=True)
