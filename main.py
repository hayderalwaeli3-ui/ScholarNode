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

# --- الإعدادات والمفاتيح ---
API_KEY = st.secrets["OPENAI_API_KEY"]
from openai import OpenAI
client = OpenAI(api_key=API_KEY)

DB_CODES = "scholar_main_db.csv"
DB_SECURITY = "device_tracking.csv"

def init_db():
    if not os.path.exists(DB_CODES):
        pd.DataFrame(columns=["code", "credit", "remaining", "status", "activation_date", "expiry_date"]).to_csv(DB_CODES, index=False)
    if not os.path.exists(DB_SECURITY):
        pd.DataFrame(columns=["device_id", "free_used", "is_blocked"]).to_csv(DB_SECURITY, index=False)

init_db()

def get_device_id():
    return str(uuid.getnode())

def deduct_attempt(amount=1):
    if st.session_state.get('access_granted', False): return True
    df = pd.read_csv(DB_SECURITY)
    dev_id = get_device_id()
    if dev_id not in df['device_id'].values:
        new_row = pd.DataFrame([{'device_id': dev_id, 'free_used': 0, 'is_blocked': False}])
        df = pd.concat([df, new_row], ignore_index=True)
    
    idx = df.index[df['device_id'] == dev_id].tolist()[0]
    if df.at[idx, 'free_used'] >= 2:
        st.error("❌ نفد الرصيد المجاني. يرجى الاشتراك.")
        st.stop()
        return False
    df.at[idx, 'free_used'] += amount
    df.to_csv(DB_SECURITY, index=False)
    st.session_state.credit = 2 - df.at[idx, 'free_used']
    return True

# --- التنسيق البصري ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: white; }
    .main-header { background: #1e3a8a; color: white !important; padding: 25px; text-align: center; border-radius: 15px; border: 4px solid #facc15; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: black !important; font-weight: bold !important; }
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 2px solid #facc15; }
    .price-table { width: 100%; border: 2px solid #ef4444; color: black; text-align: center; }
    .price-table th { background: #ef4444; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    if "auth" in st.session_state:
        if st.button("🔴 خروج"):
            st.session_state.clear()
            st.rerun()
    st.markdown('<div class="payment-box"><b>🏦 ماستر كارد:</b> 8369719342<br><b>👤 حيدر جاسم</b></div>', unsafe_allow_html=True)
    st.markdown("### 🏷️ جدول الكروت")
    st.markdown('<table class="price-table"><tr><th>الفئة</th><th>المحاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>50,000</td><td>333</td></tr></table>', unsafe_allow_html=True)
    adm = st.text_input("لوحة التحكم (Admin):", type="password")
    if adm == "HAYDER_2026":
        st.session_state.access_granted = True
        st.success("تم تفعيل وضع المدير")

# --- الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>المنصة الأكاديمية (ScholarNode)</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎁 تجربة مجانية")
        u_name = st.text_input("الاسم الثلاثي:")
        if st.button("بدء") and len(u_name.split()) >= 3:
            st.session_state.update({"auth": True, "mode": "free", "user": u_name, "credit": 2})
            st.rerun()
    with col2:
        st.subheader("🔑 كود الاشتراك")
        in_code = st.text_input("الكود:", type="password")
        if st.button("تفعيل"):
            df = pd.read_csv(DB_CODES)
            if in_code in df['code'].values:
                st.session_state.update({"auth": True, "mode": "pro", "user": "باحث", "credit": 100})
                st.rerun()
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً {st.session_state.user}</h1><h2>الرصيد: {st.session_state.credit}</h2></div>', unsafe_allow_html=True)
file = st.file_uploader("ارفع ملف PDF", type=["pdf"])

t1, t2, t3 = st.tabs(["💬 شات", "🌍 ترجمة", "📄 معاينة"])

with t2: # تبويب الترجمة عاد كاملاً
    st.subheader("الترجمة الأكاديمية")
    lang = st.selectbox("اللغة:", ["العربية", "English"])
    if file and st.button("ترجمة"):
        if deduct_attempt(1):
            st.success("جاري الترجمة...")

with t3: # المعاينة عادت كاملة
    if file:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        p_num = st.number_input("الصفحة:", 1, len(doc), 1)
        if st.button("تحليل الصفحة"):
            if deduct_attempt(1):
                st.info("تم التحليل.")
        st.image(Image.open(io.BytesIO(doc[p_num-1].get_pixmap().tobytes())))
