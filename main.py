import streamlit as st
import pandas as pd
import os
import time
import random
import string
import io
from datetime import datetime, timedelta
import requests

# محاولة استيراد المكتبات
try:
    import fitz
except ImportError:
    fitz = None
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# --- إعدادات الصفحة ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide", initial_sidebar_state="expanded")

# --- تنسيق CSS ---
st.markdown("""
    <style>
    .welcome-header { background-color: #1e3d59 !important; border: 2px solid #ffc13b !important; padding: 20px; border-radius: 12px; margin-bottom: 25px; text-align: center; }
    .payment-card { border: 2px dashed #1e3d59; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- قاعدة البيانات ---
DB_CODES = "scholarnode_database.csv"
def init_db():
    if not os.path.exists(DB_CODES):
        df = pd.DataFrame(columns=["code", "credit", "remaining", "plan_type", "activation_date", "expiry_date", "status"])
        df.to_csv(DB_CODES, index=False)
init_db()

PLANS = {
    "1000": {"attempts": 10, "days": 4},
    "5000": {"attempts": 60, "days": 20},
    "10000": {"attempts": 130, "days": 30},
    "20000": {"attempts": 270, "days": 60},
    "50000": {"attempts": 690, "days": 150}
}

# --- إعداد الذكاء الاصطناعي ---
openai_key = st.secrets.get("OPENAI_API_KEY", "").strip()
gemini_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if gemini_key and genai:
    genai.configure(api_key=gemini_key)

client = None
if openai_key:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
    except:
        client = None

# --- [المحرك الذكي] Gemini أولاً، OpenAI احتياط---
def generate_academic_text(prompt):
    # محاولة Gemini (الأساسي)
    if gemini_key and genai:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(prompt)
            return res.text
        except:
            pass # فشل Gemini -> انتقل للبديل
    
    # محاولة OpenAI (احتياطي)
    if client and openai_key:
        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content
        except Exception as e:
            return f"عذراً، فشل الاتصال بالمحرك: {str(e)}"
    return "لا توجد مفاتيح اتصال فعالة."

# --- الدوال الوظيفية ---
def extract_file_content(uploaded_file):
    if uploaded_file is None: return "", 0
    uploaded_file.seek(0)
    text = ""
    try:
        if uploaded_file.name.lower().endswith('.pdf') and fitz:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page in doc: text += page.get_text()
        elif uploaded_file.name.lower().endswith('.docx'):
            from docx import Document
            doc = Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs])
    except:
        text = "خطأ في قراءة الملف."
    return text, 1

def deduct_attempts(amount):
    if st.session_state.get('user_code') == "HAYDER_2026$$$": return True
    try:
        df = pd.read_csv(DB_CODES)
        idx = df.index[df['code'] == st.session_state.user_code].tolist()
        if idx and df.at[idx[0], 'remaining'] >= amount:
            df.at[idx[0], 'remaining'] = int(df.at[idx[0], 'remaining'] - amount)
            df.to_csv(DB_CODES, index=False)
            st.session_state.user_credit = df.at[idx[0], 'remaining']
            return True
    except: return False
    return False

# --- الواجهات ---
def render_user_services():
    st.markdown("### ✨ الخدمات الأكاديمية")
    uploaded_file = st.file_uploader("📂 ارفع مستندك هنا", type=["pdf", "docx", "png", "jpg"], key="main_upload_unique")
    
    tabs = st.tabs(["🔍 معاينة", "🎓 مراجعة", "🌍 ترجمة", "⚖️ قانونية", "🎨 رسم", "✨ تحسين", "👨‍🏫 مستشار"])
    
    with tabs[0]: # معاينة
        if uploaded_file:
            query = st.text_input("💬 سؤالك:", key="query_chat_unique")
            if st.button("🚀 تنفيذ", key="btn_chat_unique"):
                if deduct_attempts(1):
                    text, _ = extract_file_content(uploaded_file)
                    st.write(generate_academic_text(f"{text}\n\nالسؤال: {query}"))
    
    with tabs[6]: # مستشار
        adv = st.text_area("🧠 اسأل المستشار:", key="adv_unique")
        if st.button("إرسال", key="btn_adv_unique"):
            if deduct_attempts(1):
                st.write(generate_academic_text(adv))

# --- نظام الدخول ---
if "authenticated" not in st.session_state:
    st.subheader("🔐 تسجيل الدخول")
    c = st.text_input("كود:", type="password", key="pass_unique")
    if st.button("دخول", key="login_btn_unique"):
        if c == "HAYDER_2026$$$":
            st.session_state.update({"authenticated": True, "user_code": "ADMIN", "is_admin": True})
            st.rerun()
        else:
            st.error("كود غير صحيح")
else:
    if st.session_state.is_admin:
        tabs = st.tabs(["الخدمات", "الإدارة"])
        with tabs[0]: render_user_services()
        with tabs[1]: st.write("قسم الإدارة متاح.")
    else:
        render_user_services()
