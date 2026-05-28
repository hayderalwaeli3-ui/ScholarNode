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
st.set_page_config(page_title="ScholarNode", layout="wide", initial_sidebar_state="expanded")

# 2. إعداد محرك Gemini المحدث
def get_gemini_response(prompt):
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_level="HIGH")),
        )
        return response.text
    except Exception as e:
        return f"⚠️ خطأ تقني: {str(e)}"

# 3. إدارة البيانات المالية (السياسة المالية)
DB_CODES = "scholarnode_secured_db.csv"
def init_db():
    if not os.path.exists(DB_CODES):
        df = pd.DataFrame(columns=["code", "credit", "remaining", "plan_type", "activation_date", "expiry_date", "status"])
        df.to_csv(DB_CODES, index=False)
init_db()

# فئات الاشتراكات
PLANS = {
    1000: {"attempts": 20, "days": 3}, 5000: {"attempts": 100, "days": 20},
    10000: {"attempts": 200, "days": 30}, 20000: {"attempts": 400, "days": 60},
    30000: {"attempts": 600, "days": 90}, 40000: {"attempts": 800, "days": 120},
    50000: {"attempts": 1000, "days": 150}, 100000: {"attempts": 2000, "days": 300}
}

# 4. التنسيقات (CSS)
st.markdown("""
<style>
    .welcome-header-box { background-color: #1e40af; border: 4px solid #eab308; padding: 22px; text-align: center; border-radius: 14px; margin-bottom: 30px; color: white; }
    .payment-box-luxury { border: 2px solid #1e40af; background-color: #f0f9ff; padding: 18px; border-radius: 12px; }
    .styled-table { width: 100%; border-collapse: collapse; }
    .styled-table th { background-color: #bae6fd; color: #1e3a8a; padding: 10px; }
    .styled-table td { background-color: #fef08a; color: #1e3a8a; padding: 10px; border-bottom: 1px solid #fde047; }
</style>
""", unsafe_allow_html=True)

# 5. منطق الدخول (تم تنقيحه)
if "authenticated" not in st.session_state:
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
                # [منطق التحقق من CSV هنا]
                st.session_state.update({"authenticated": True, "user_code": code, "is_admin": False, "user_credit": 100}) # مثال
                st.rerun()
    with col2:
        st.markdown('<div class="payment-box-luxury"><b>معلومات الدفع:</b><br>ماستر كارد الرافدين: 8369719342<br>HAYDER Z. JASIM</div>', unsafe_allow_html=True)
    st.stop()

# 6. الواجهة بعد الدخول (التبويبات)
st.sidebar.markdown(f"**الكود:** {st.session_state.user_code}")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.clear()
    st.rerun()

tabs = st.tabs(["📄 معاينة", "🎓 مراجعة", "🌍 ترجمة", "⚖️ قانونية", "🎨 صور", "🔍 توضيح", "🎙️ صوت", "💬 مستشار"])

with tabs[7]: # مثال المستشار
    query = st.text_area("اطرح سؤالك الأكاديمي:")
    if st.button("إرسال"):
        with st.spinner("جاري المعالجة..."):
            st.markdown(get_gemini_response(query))

# 7. لوحة الإدارة
if st.session_state.get("is_admin"):
    st.markdown("---")
    st.subheader("🛠️ لوحة الإدارة")
    # [هنا تضع منطق توليد الكودات]
