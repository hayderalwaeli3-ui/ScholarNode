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

# --- 1. إعدادات وتصميم الصفحة ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .welcome-header { background-color: #1e3d59 !important; border: 2px solid #ffc13b !important; padding: 20px; border-radius: 12px; margin-bottom: 25px; text-align: center; }
    .payment-card { border: 2px dashed #1e3d59; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات ---
DB_CODES = "scholarnode_database.csv"
def init_db():
    if not os.path.exists(DB_CODES):
        df = pd.DataFrame(columns=["code", "credit", "remaining", "plan_type", "activation_date", "expiry_date", "status"])
        df.to_csv(DB_CODES, index=False)
init_db()

# --- 3. إعداد بوابات الذكاء الاصطناعي (البروتوكول الصامت) ---
openai_key = st.secrets.get("OPENAI_API_KEY", "").strip()
gemini_key = st.secrets.get("GEMINI_API_KEY", "").strip()

# تهيئة جيميني
if gemini_key and genai:
    genai.configure(api_key=gemini_key)

# تهيئة أوبن أي آي
client = None
if openai_key:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
    except:
        client = None

# --- المحرك الذكي الموحد (جيميني أولاً) ---
def generate_academic_text(prompt):
    # 1. محاولة Gemini (لأنه الأوفر ومجاني غالباً)
    if gemini_key and genai:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except:
            pass # فشل جيميني، نمر للخطوة التالية بصمت
            
    # 2. محاولة OpenAI كبديل
    if client and openai_key:
        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content
        except Exception as e:
            return f"خطأ في الاتصال بالمحركات: {str(e)}"
            
    return "عذراً، لم يتم العثور على مفاتيح تفعيل صالحة للذكاء الاصطناعي."

# --- بقية الدوال (بدون تعديل) ---
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

# --- واجهة الخدمات ---
def render_user_services():
    st.markdown("### ✨ الخدمات الأكاديمية المتطورة")
    uploaded_file = st.file_uploader("📂 ارفع ملفك للتحليل", type=["pdf", "docx", "png", "jpg"], key="up_file_main")
    
    tabs = st.tabs(["🔍 معاينة ومناقشة", "🎓 مراجعة نقدية", "🌍 ترجمة أكاديمية", "⚖️ قانونية", "🎨 رسم", "✨ تحسين", "👨‍🏫 مستشار"])
    
    with tabs[0]: # مناقشة
        if uploaded_file:
            chat_q = st.text_input("💬 سؤالك حول الملف:", key="q_chat")
            if st.button("🚀 تنفيذ", key="btn_chat"):
                if deduct_attempts(1):
                    text, _ = extract_file_content(uploaded_file)
                    st.write(generate_academic_text(f"{text}\n\nالسؤال: {chat_q}"))
    
    with tabs[6]: # مستشار
        adv_q = st.text_area("🧠 اسأل المستشار:", key="q_adv")
        if st.button("إرسال الاستشارة", key="btn_adv"):
            if deduct_attempts(1):
                st.write(generate_academic_text(adv_q))

# --- نظام تسجيل الدخول ---
if "authenticated" not in st.session_state:
    st.subheader("🔐 تسجيل الدخول")
    input_key = st.text_input("كود التفعيل:", type="password")
    if st.button("دخول"):
        if input_key == "HAYDER_2026$$$":
            st.session_state.update({"authenticated": True, "user_code": "ADMIN", "is_admin": True})
            st.rerun()
        else:
            # (منطق التحقق العادي للكودات)
            st.error("كود غير صحيح.")
else:
    if st.session_state.get("is_admin"):
        admin_t = st.tabs(["خدمات", "إدارة"])
        with admin_t[0]: render_user_services()
        with admin_t[1]: st.write("قسم الإدارة...")
    else:
        render_user_services()
