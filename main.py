import streamlit as st
import pandas as pd
import os
import io
import uuid
import random
import string
from datetime import datetime
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from openai import OpenAI
import time

# --- إعدادات النظام والمفاتيح (حماية مطلقة) ---
API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)
DB_CODES = "scholar_main_db.csv"

def init_db():
    if not os.path.exists(DB_CODES):
        pd.DataFrame(columns=["code", "credit", "remaining", "status"]).to_csv(DB_CODES, index=False)

init_db()

# --- وظيفة إنشاء ملف Word ---
def create_word_file(text):
    doc = Document()
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in p.runs:
        run.font.size = Pt(14)
        run.font.name = 'Arial'
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- وظيفة خصم الرصيد ---
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

# --- التنسيق البصري المتجاوب (للهواتف والحاسوب) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")

# إضافة كود CSS لجعل الواجهة تتكيف مع الموبايل
st.markdown("""
<style>
    /* جعل الحاويات مرنة */
    .stApp { background-color: #ffffff !important; }
    
    /* تنسيق الهيدر ليكون متجاوباً */
    .main-header { 
        background: #1e3a8a; 
        color: #ffffff !important; 
        padding: 20px; 
        text-align: center; 
        border-radius: 15px; 
        border: 4px solid #facc15; 
        margin-bottom: 20px;
    }
    
    /* تصغير الخطوط في الموبايل */
    @media (max-width: 640px) {
        .main-header h1 { font-size: 24px !important; }
        .main-header h2 { font-size: 18px !important; }
        .stButton button { width: 100% !important; }
        .price-table { font-size: 12px !important; }
    }

    h1, h2, h3, p, span, label { color: #000000 !important; font-weight: bold !important; }
    
    /* جداول الأسعار */
    .price-table { width: 100%; border-collapse: collapse; background: #ffffff; border: 2px solid #ef4444; }
    .price-table th { background: #ef4444; color: white !important; padding: 10px; }
    .price-table td { border: 1px solid #ef4444; padding: 8px; text-align: center; color: #000000 !important; }
    
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 3px solid #facc15; }
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    if "auth" in st.session_state:
        if st.button("🔴 خروج"):
            st.session_state.clear()
            st.rerun()
    
    st.markdown('<div class="payment-box"><b>🏦 ماستر كارد:</b><br>8369719342<br>👤 HAYDER Z. JASIM</div>', unsafe_allow_html=True)
    st.markdown("### 🏷️ الأسعار")
    st.markdown("""<table class="price-table"><tr><th>الفئة</th><th>رصيد</th></tr><tr><td>10k</td><td>66</td></tr><tr><td>20k</td><td>133</td></tr><tr><td>50k</td><td>333</td></tr></table>""", unsafe_allow_html=True)

    # لوحة تحكم الأدمن
    st.write("---")
    adm = st.text_input("Admin:", type="password")
    if adm == "HAYDER_2026":
        cat = st.selectbox("الفئة:", [10, 20, 30, 40, 50, 100])
        if st.button("توليد كود"):
            new_c = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            attempts = {10: 66, 20: 133, 30: 200, 40: 266, 50: 333, 100: 666}[cat]
            df = pd.read_csv(DB_CODES)
            new_entry = pd.DataFrame([{"code": new_c, "credit": attempts, "remaining": attempts, "status": "Active"}])
            pd.concat([df, new_entry]).to_csv(DB_CODES, index=False)
            st.success(f"الكود: {new_c}")

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    in_c = st.text_input("أدخل كود التفعيل:", type="password")
    if st.button("دخول", use_container_width=True):
        df = pd.read_csv(DB_CODES)
        match = df[df['code'] == in_c.strip()]
        if not match.empty:
            st.session_state.update({"auth": True, "code": in_c.strip(), "credit": match.iloc[0]['remaining']})
            st.rerun()
        else: st.error("الكود غير صحيح")
    st.stop()

# --- الواجهة الرئيسية (متجاوبة) ---
st.markdown(f'<div class="main-header"><h1>ScholarNode</h1><h2>الرصيد: {st.session_state.credit}</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف البحث (PDF)", type=["pdf"])

tabs = st.tabs(["💬 المستشار", "🌍 الترجمة", "🎓 المراجعة", "📄 المعاينة"])

# تبويب المستشار الأكاديمي
with tabs[0]:
    st.subheader("🎓 المستشار الأكاديمي")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    prompt = st.chat_input("اطلب بناء خطة بحثية...")
    if prompt:
        if deduct_attempt(1):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "أنت بروفيسور أكاديمي خبير."}] + st.session_state.chat_history)
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            st.rerun()

# تبويب المعاينة (المعدل ليتناسب مع الهاتف)
with tabs[3]:
    if up:
        up.seek(0)
        doc = fitz.open(stream=up.read(), filetype="pdf")
        p_n = st.number_input("الصفحة:", 1, len(doc), 1)
        pix = doc[p_n-1].get_pixmap(matrix=fitz.Matrix(1.2, 1.2)) # تصغير المصفوفة قليلاً لتناسب الموبايل
        st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)
        
        f_q = st.text_input("اسأل عن محتوى الملف:")
        if st.button("تحليل المحتوى") and f_q:
            if deduct_attempt(1):
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f_q}])
                st.info(res.choices[0].message.content)
                st.download_button("📥 تحميل الإجابة (Word)", data=create_word_file(res.choices[0].message.content), file_name="analysis.docx")

# الترجمة والمراجعة (مع تفعيل شخصية المراجع البشري والعناوين الأصلية)
if up:
    with tabs[1]:
        if st.button("بدء الترجمة الأكاديمية الكاملة"):
            if deduct_attempt(10): # خصم تقديري أو حسب الصفحات
                st.success("جاري الترجمة...")
                # (نفس منطق الترجمة السابق)

    with tabs[2]:
        if st.button("توليد مراجعة علمية (شخصية مراجع)"):
            if deduct_attempt(5):
                st.info("المراجع يقوم بفحص النص الآن...")
                # (نفس منطق المراجعة السابق)

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
