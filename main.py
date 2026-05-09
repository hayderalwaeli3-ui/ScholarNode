import streamlit as st
import pandas as pd
import os
import io
import random
import string
from datetime import datetime, timedelta
import fitz  # PyMuPDF
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from openai import OpenAI

# --- إعدادات النظام ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
DB_CODES = "scholar_main_db.csv"

if not os.path.exists(DB_CODES):
    pd.DataFrame(columns=["code", "credit", "remaining", "status", "activation_date", "expiry_date"]).to_csv(DB_CODES, index=False)

def create_word_file(text):
    doc = Document()
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

def deduct_attempt(amount=1):
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

# --- التنسيق البصري ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""<style>
    .main-header { background: #1e3a8a; color: white !important; padding: 30px; text-align: center; border-radius: 15px; border: 5px solid #facc15; margin-bottom: 25px; }
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 3px solid #facc15; }
    .price-table { width: 100%; border-collapse: collapse; border: 2px solid #ef4444; background: white; }
    .price-table th { background: #ef4444; color: white; padding: 10px; }
    .price-table td { border: 1px solid #ef4444; padding: 8px; text-align: center; color: black; }
</style>""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    if "auth" in st.session_state:
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear()
            st.rerun()
    
    st.markdown('<div class="payment-box"><b>🏦 ماستر كارد الرافدين:</b><br>8369719342<br>👤 HAYDER Z. JASIM</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏷️ جدول الكروت")
    st.markdown("""<table class="price-table">
        <tr><th>الفئة (دينار)</th><th>المحاولات</th></tr>
        <tr><td>10,000</td><td>66</td></tr>
        <tr><td>20,000</td><td>133</td></tr>
        <tr><td>30,000</td><td>200</td></tr>
        <tr><td>40,000</td><td>266</td></tr>
        <tr><td>50,000</td><td>333</td></tr>
        <tr><td>100,000</td><td>666</td></tr>
    </table>""", unsafe_allow_html=True)

    st.write("---")
    adm_key = st.text_input("لوحة التحكم (Admin):", type="password")
    if adm_key == "HAYDER_2026":
        st.success("تم الدخول كمسؤول")
        cat = st.selectbox("توليد فئة:", [10, 20, 30, 40, 50, 100])
        if st.button("توليد كود الاشتراك"):
            new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            attempts = {10: 66, 20: 133, 30: 200, 40: 266, 50: 333, 100: 666}[cat]
            df = pd.read_csv(DB_CODES)
            new_entry = pd.DataFrame([{"code": new_code, "credit": attempts, "remaining": attempts, "status": "Active", "activation_date": "None", "expiry_date": "None"}])
            pd.concat([df, new_entry]).to_csv(DB_CODES, index=False)
            st.code(f"الكود: {new_code}")

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>🔐 أدخل كود الاشتراك</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        u_code = st.text_input("كود الكارت:", type="password")
        if st.button("دخول", use_container_width=True):
            df = pd.read_csv(DB_CODES)
            match = df[(df['code'] == u_code.strip()) & (df['status'] == 'Active')]
            if not match.empty:
                idx = match.index[0]
                st.session_state.update({"auth": True, "credit": df.at[idx, 'remaining'], "code": u_code.strip()})
                st.rerun()
            else: st.error("الكود غير صحيح")
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً دكتور</h1><h2>الرصيد: {st.session_state.credit}</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF", type=["pdf"])
if up:
    st.success("تم رفع الملف بنجاح") # تم تصحيح الخطأ هنا
