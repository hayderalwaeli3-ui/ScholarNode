import streamlit as st
import pandas as pd
import os
import io
import uuid
import random
import string
from datetime import datetime, timedelta
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

# --- إعدادات النظام والمفاتيح ---
API_KEY = st.secrets["OPENAI_API_KEY"]
from openai import OpenAI
client = OpenAI(api_key=API_KEY)

DB_CODES = "scholar_main_db.csv"
DB_SECURITY = "device_tracking.csv"

# --- تهيئة قواعد البيانات ---
def init_db():
    if not os.path.exists(DB_CODES):
        pd.DataFrame(columns=["code", "credit", "remaining", "status", "activation_date", "expiry_date"]).to_csv(DB_CODES, index=False)
    if not os.path.exists(DB_SECURITY):
        pd.DataFrame(columns=["device_id", "free_used", "is_blocked"]).to_csv(DB_SECURITY, index=False)

init_db()

# --- وظائف الحماية والتحكم ---
def get_device_id():
    return str(uuid.getnode())

def check_security():
    dev_id = get_device_id()
    df = pd.read_csv(DB_SECURITY)
    user_row = df[df['device_id'] == dev_id]
    if not user_row.empty:
        if user_row.iloc[0]['is_blocked'] or user_row.iloc[0]['free_used'] >= 2:
            return "blocked", user_row.iloc[0]['free_used']
        return "exists", user_row.iloc[0]['free_used']
    return "new", 0

def deduct_attempt(amount=1):
    if st.session_state.mode == "pro":
        df = pd.read_csv(DB_CODES)
        idx_list = df.index[df['code'] == st.session_state.code].tolist()
        if idx_list:
            idx = idx_list[0]
            if df.at[idx, 'remaining'] >= amount:
                df.at[idx, 'remaining'] -= amount
                df.to_csv(DB_CODES, index=False)
                st.session_state.credit = df.at[idx, 'remaining']
                return True
        return False
    else:
        # إصلاح الـ IndexError هنا
        df = pd.read_csv(DB_SECURITY)
        dev_id = get_device_id()
        if dev_id not in df['device_id'].values:
            new_dev = pd.DataFrame([{"device_id": dev_id, "free_used": 0, "is_blocked": False}])
            df = pd.concat([df, new_dev], ignore_index=True)
        
        idx = df.index[df['device_id'] == dev_id].tolist()[0]
        if df.at[idx, 'free_used'] + amount <= 2:
            df.at[idx, 'free_used'] += amount
            if df.at[idx, 'free_used'] >= 2:
                df.at[idx, 'is_blocked'] = True
            df.to_csv(DB_SECURITY, index=False)
            st.session_state.credit = 2 - df.at[idx, 'free_used']
            return True
        else:
            st.error("❌ انتهت المحاولات المجانية نهائياً لهذا الجهاز.")
            st.stop()
            return False

def create_word_file(text):
    doc = Document()
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- التنسيق البصري (CSS المسترجع) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    .main-header { background: #1e3a8a; color: #ffffff !important; padding: 30px; text-align: center; border-radius: 15px; border: 5px solid #facc15; margin-bottom: 25px; }
    h1, h2, h3, p, span, label { color: #000000 !important; font-weight: bold !important; }
    .price-table { width: 100%; border-collapse: collapse; border: 2px solid #ef4444; }
    .price-table th { background: #ef4444; color: white !important; padding: 10px; }
    .price-table td { border: 1px solid #ef4444; padding: 8px; text-align: center; color: #000000 !important; }
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 3px solid #facc15; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    if "auth" in st.session_state:
        if st.button(" 🔴 تسجيل الخروج"):
            st.session_state.clear()
            st.rerun()
    st.write("---")
    st.markdown('<h2 style="color:#1e3a8a; text-align:center;"> 💳 معلومات الدفع</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="payment-box"><b> 🏦 ماستر كارد الرافدين:</b><br>8369719342<br><br><b> 👤 الاسم:</b><br>HAYDER Z. JASIM<br><br><b> 📞 الهاتف:</b><br>07879974395</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏷️ جدول الكروت")
    st.markdown('<table class="price-table"><tr><th>الفئة (دينار)</th><th>المحاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>50,000</td><td>333</td></tr><tr><td>100,000</td><td>666</td></tr></table>', unsafe_allow_html=True)

    adm = st.text_input("لوحة التحكم (Admin):", type="password")
    if adm == "HAYDER_2026":
        cat = st.selectbox("توليد فئة:", [10, 50, 100])
        if st.button("توليد كود الاشتراك"):
            new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            attempts = {10: 66, 50: 333, 100: 666}[cat]
            df = pd.read_csv(DB_CODES)
            new_entry = pd.DataFrame([{"code": new_code, "credit": attempts, "remaining": attempts, "status": "Active", "activation_date": "None", "expiry_date": "None"}])
            pd.concat([df, new_entry]).to_csv(DB_CODES, index=False)
            st.success(f"الكود: {new_code}")

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>المنصة الأكاديمية (ScholarNode)</h1></div>', unsafe_allow_html=True)
    status, used = check_security()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(" 🎁 الدخول المجاني")
        if status == "blocked" or used >= 2: 
            st.error("❌ انتهت المحاولة المجانية.")
        else:
            u_name = st.text_input("الاسم الثلاثي:", key="free_name")
            if st.button("بدء التجربة") and len(u_name.split()) >= 3:
                st.session_state.update({"auth": True, "mode": "free", "user": u_name, "credit": 2 - used})
                st.rerun()
    with col2:
        st.subheader(" 🔑 تفعيل الاشتراك")
        in_code = st.text_input("كود الكارت:", type="password")
        if st.button("تفعيل الحساب"):
            df = pd.read_csv(DB_CODES)
            match = df[(df['code'] == in_code.strip()) & (df['status'] == 'Active')]
            if not match.empty:
                st.session_state.update({"auth": True, "mode": "pro", "user": "باحث مشترك", "credit": match.iloc[0]['remaining'], "code": in_code.strip()})
                st.rerun()
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً {st.session_state.user}</h1><h2 style="color:#facc15 !important;">الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(" 📂 ارفع ملف PDF", type=["pdf"])

if uploaded_file:
    doc_bytes = uploaded_file.read()
    doc_temp = fitz.open(stream=doc_bytes, filetype="pdf")
    st.session_state.total_pages = len(doc_temp)
    
    tabs = st.tabs([" 💬 الشات", " 🌍 الترجمة", " 🎓 المراجعة", " 📄 المعاينة"])

    with tabs[1]: # الترجمة
        target_lang = st.selectbox("إلى:", ["العربية", "English"])
        if st.button(f"بدء الترجمة"):
            if deduct_attempt(st.session_state.total_pages):
                st.success("تمت الترجمة.")
                st.download_button("📥 تحميل Word", create_word_file("نص مترجم"), "trans.docx")

    with tabs[2]: # المراجعة
        if st.button(f"بدء المراجعة"):
            if deduct_attempt(st.session_state.total_pages):
                st.success("تمت المراجعة.")
                st.download_button("📥 تحميل Word", create_word_file("نص مراجع"), "review.docx")

    with tabs[3]: # المعاينة
        doc = fitz.open(stream=doc_bytes, filetype="pdf")
        p_num = st.number_input("الصفحة:", 1, len(doc), 1)
        task = st.text_area("المهمة:")
        if st.button("معالجة الصفحة"):
            if deduct_attempt(1):
                st.success("تمت المعالجة بنجاح.")

st.markdown("<br><hr><p style='text-align:center; color:black;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
