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

# --- إدارة قاعدة البيانات ---
DB_CODES = "scholarnode_database.csv"
if not os.path.exists(DB_CODES):
    df = pd.DataFrame(columns=["code", "credit", "remaining", "plan_type", "activation_date", "expiry_date", "status"])
    df.to_csv(DB_CODES, index=False)

PLANS = {
    "1000": {"attempts": 10, "days": 4},
    "5000": {"attempts": 60, "days": 20},
    "10000": {"attempts": 130, "days": 30},
    "20000": {"attempts": 270, "days": 60},
    "50000": {"attempts": 690, "days": 150}
}

# --- إعداد المحركات الخلفية ---
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
        pass

# --- المحرك الذكي الصامت ---
def generate_academic_text(prompt):
    # محاولة Gemini أولاً (التوفير)
    if gemini_key and genai:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            return model.generate_content(prompt).text
        except:
            pass 
    
    # محاولة OpenAI كبديل
    if client and openai_key:
        try:
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
            return res.choices[0].message.content
        except:
            pass
            
    return "عذراً، تعذر الاتصال بخدمات الذكاء الاصطناعي حالياً."

# --- دوال المعالجة ---
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
    except:
        return False
    return False

# --- واجهة الخدمة الموحدة ---
def render_user_services():
    st.markdown("### ✨ الخدمات الأكاديمية")
    uploaded_file = st.file_uploader("📂 ارفع مستندك للتحليل", type=["pdf", "docx", "png", "jpg"], key="main_file_uploader")
    
    tabs = st.tabs(["🔍 معاينة", "🎓 مراجعة", "🌍 ترجمة", "⚖️ قانونية", "🎨 رسوم", "✨ تحسين", "👨‍🏫 مستشار"])
    
    with tabs[0]: # معاينة
        if uploaded_file:
            st.info("الملف جاهز للمعالجة.")
            chat_query = st.text_input("سؤالك عن الملف:", key="chat_q")
            if st.button("🚀 تنفيذ", key="btn_chat"):
                if deduct_attempts(1):
                    text, _ = extract_file_content(uploaded_file)
                    st.write(generate_academic_text(f"{text}\n\nسؤال: {chat_query}"))
    
    with tabs[6]: # مستشار
        adv_input = st.text_area("استشارتك:", key="adv_in")
        if st.button("🧠 إرسال", key="btn_adv"):
            if deduct_attempts(1):
                st.write(generate_academic_text(adv_input))

# --- نظام الدخول ---
if "authenticated" not in st.session_state:
    st.title("ScholarNode Academy")
    code = st.text_input("كود التفعيل:", type="password")
    if st.button("دخول"):
        if code == "HAYDER_2026$$$":
            st.session_state.update({"authenticated": True, "user_code": code, "is_admin": True})
            st.rerun()
        # (أضف منطق التحقق من الملف هنا)
else:
    if st.session_state.get("is_admin"):
        admin_tabs = st.tabs(["خدمات", "توليد كودات", "الجدول"])
        with admin_tabs[0]: render_user_services()
        with admin_tabs[1]: st.write("قسم توليد الكودات...")
    else:
        render_user_services()
