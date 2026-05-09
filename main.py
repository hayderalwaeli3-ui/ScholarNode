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
from openai import OpenAI

# --- إعدادات النظام والمفاتيح ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
DB_CODES = "scholar_main_db.csv"

# --- تهيئة قواعد البيانات ---
if not os.path.exists(DB_CODES):
    pd.DataFrame(columns=["code", "credit", "remaining", "status", "activation_date", "expiry_date"]).to_csv(DB_CODES, index=False)

# --- وظيفة إنشاء ملف Word بتنسيق عربي ---
def create_word_file(text):
    doc = Document()
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- وظائف الخصم للمشتركين فقط ---
def deduct_attempt(amount=1):
    if "code" in st.session_state:
        df = pd.read_csv(DB_CODES)
        matches = df.index[df['code'] == st.session_state.code].tolist()
        if matches:
            idx = matches[0]
            if df.at[idx, 'remaining'] >= amount:
                df.at[idx, 'remaining'] -= amount
                df.to_csv(DB_CODES, index=False)
                st.session_state.credit = df.at[idx, 'remaining']
                return True
    return False

# --- التنسيق البصري (CSS) الاحترافي ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #ffffff !important; }
    .main-header { background: #1e3a8a; color: #ffffff !important; padding: 30px; text-align: center; border-radius: 15px; border: 5px solid #facc15; margin-bottom: 25px; }
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 3px solid #facc15; margin-bottom: 20px; }
    .finance-info { background: #fffbe6; color: #856404; padding: 15px; border-radius: 8px; border-right: 5px solid #facc15; margin-bottom: 20px; font-weight: bold; }
    .price-table { width: 100%; border-collapse: collapse; border: 2px solid #ef4444; }
    .price-table th { background: #ef4444; color: white !important; padding: 10px; }
    .price-table td { border: 1px solid #ef4444; padding: 8px; text-align: center; color: black !important; }
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    if "auth" in st.session_state:
        if st.button(" 🔴  تسجيل الخروج"):
            st.session_state.clear()
            st.rerun()
        st.write("---")
        if "total_pages" in st.session_state:
            base_cost = st.session_state.total_pages * 300
            total_iqd = int(base_cost + (base_cost * 0.08))
            st.markdown(f'<div class="finance-info">📊 تفاصيل الكلفة:<br>📄 الصفحات: {st.session_state.total_pages}<br>💰 المبلغ: {total_iqd} دينار</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="payment-box"><b>🏦 ماستر كارد الرافدين:</b><br>8369719342<br><br><b>👤 HAYDER Z. JASIM</b></div>', unsafe_allow_html=True)
    st.markdown("### 🏷️ جدول الكروت")
    st.markdown('<table class="price-table"><tr><th>الفئة</th><th>المحاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>100,000</td><td>666</td></tr></table>', unsafe_allow_html=True)

    # لوحة الإدارة (Admin)
    st.write("---")
    adm = st.text_input("لوحة التحكم (Admin):", type="password")
    if adm == "HAYDER_2026":
        cat = st.selectbox("الفئة:", [10, 20, 30, 40, 50, 100])
        if st.button("توليد كود"):
            new_c = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            st.success(f"الكود الجديد: {new_c}")

# --- بوابة الدخول (تم حذف التجربة المجانية) ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>🔐 يرجى إدخال كود الاشتراك للتفعيل</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        in_code = st.text_input("كود الكارت:", type="password")
        if st.button("تفعيل الحساب والدخول", use_container_width=True):
            df = pd.read_csv(DB_CODES)
            match = df[(df['code'] == in_code.strip()) & (df['status'] == 'Active')]
            if not match.empty:
                idx = match.index[0]
                st.session_state.update({"auth": True, "user": "باحث مشترك", "credit": df.at[idx, 'remaining'], "code": in_code.strip()})
                st.rerun()
            else: st.error("الكود غير صحيح أو منتهي.")
    st.stop()

# --- الواجهة الرئيسية للمشتركين ---
st.markdown(f'<div class="main-header"><h1>مرحباً بك دكتور</h1><h2>الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("📂 ارفع ملفك (PDF)", type=["pdf"])

if uploaded_file:
    doc_temp = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.session_state.total_pages = len(doc_temp)
    tabs = st.tabs(["💬 الشات", "🌍 الترجمة", "🎓 المراجعة", "📄 المعاينة"])
    
    with tabs[1]: # الترجمة
        if st.button(f"بدء الترجمة ({st.session_state.total_pages} صفحة)"):
            if deduct_attempt(st.session_state.total_pages):
                all_text = "\n".join([page.get_text() for page in doc_temp])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate to Arabic:\n{all_text[:10000]}"}])
                st.write(res.choices[0].message.content)
                st.download_button("📥 تحميل ملف Word", create_word_file(res.choices[0].message.content), "translated.docx")
