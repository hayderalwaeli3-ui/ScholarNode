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

# --- 1. إعدادات النظام والمفاتيح [cite: 319-324] ---
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

DB_CODES = "scholar_main_db.csv"
DB_SECURITY = "device_tracking.csv"

def init_db():
    if not os.path.exists(DB_CODES):
        pd.DataFrame(columns=["code", "credit", "remaining", "status", "activation_date", "expiry_date"]).to_csv(DB_CODES, index=False)
    if not os.path.exists(DB_SECURITY):
        pd.DataFrame(columns=["device_id", "free_used", "is_blocked"]).to_csv(DB_SECURITY, index=False)

init_db()

# --- 2. وظيفة إنشاء ملف Word (الإصلاح الجذري للملف المعطوب)  ---
def create_word_file(content_text, filename="document.docx"):
    doc = Document()
    # إعدادات الخط والاتجاه للعربية
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(12)
    
    # إضافة المحتوى
    paragraphs = content_text.split('\n')
    for para in paragraphs:
        if para.strip():
            p = doc.add_paragraph(para)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT  # محاذاة لليمين
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. وظائف الحماية والخصم [cite: 344-381] ---
def get_device_id():
    return str(uuid.getnode())

def deduct_attempt(amount=1):
    if st.session_state.get("mode") == "pro":
        df = pd.read_csv(DB_CODES)
        idx_list = df.index[df['code'] == st.session_state.code].tolist()
        if idx_list:
            idx = idx_list[0]
            if df.at[idx, 'remaining'] >= amount:
                df.at[idx, 'remaining'] -= amount
                df.to_csv(DB_CODES, index=False)
                st.session_state.credit = df.at[idx, 'remaining']
                return True
    else:
        df = pd.read_csv(DB_SECURITY)
        dev_id = get_device_id()
        if dev_id not in df['device_id'].values:
            new_dev = pd.DataFrame([{"device_id": dev_id, "free_used": 0, "is_blocked": False}])
            df = pd.concat([df, new_dev], ignore_index=True)
        
        idx = df.index[df['device_id'] == dev_id].tolist()[0]
        if df.at[idx, 'free_used'] + amount <= 2:
            df.at[idx, 'free_used'] += amount
            df.to_csv(DB_SECURITY, index=False)
            st.session_state.credit = 2 - df.at[idx, 'free_used']
            return True
    return False

# --- 4. التنسيق البصري [cite: 385-451] ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    .main-header { background: #1e3a8a; color: white !important; padding: 25px; text-align: center; border-radius: 15px; border: 4px solid #facc15; }
    .rtl-box { direction: rtl; text-align: right; background: #f8fafc; padding: 20px; border-radius: 10px; border-right: 6px solid #1e3a8a; color: black; }
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 2px solid #facc15; }
    </style>
""", unsafe_allow_html=True)

# --- 5. بوابة الدخول [cite: 511-541] ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎁 الدخول المجاني")
        u_name = st.text_input("الاسم الثلاثي:")
        if st.button("بدء التجربة") and len(u_name.split()) >= 3:
            st.session_state.update({"auth": True, "mode": "free", "user": u_name, "credit": 2})
            st.rerun()
    with col2:
        st.subheader("🔑 تفعيل الاشتراك")
        code = st.text_input("كود الكارت:", type="password")
        if st.button("تفعيل"):
            df = pd.read_csv(DB_CODES)
            if code in df['code'].values:
                rem = df[df['code'] == code]['remaining'].values[0]
                st.session_state.update({"auth": True, "mode": "pro", "user": "باحث مشترك", "credit": rem, "code": code})
                st.rerun()
    st.stop()

# --- 6. الواجهة الرئيسية [cite: 543-610] ---
st.markdown(f'<div class="main-header"><h1>مرحباً دكتور {st.session_state.user}</h1><h2>الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("📂 ارفع ملف PDF للترجمة أو المراجعة", type=["pdf"])

if uploaded_file:
    doc_data = uploaded_file.read()
    pdf_doc = fitz.open(stream=doc_data, filetype="pdf")
    num_pages = len(pdf_doc)
    
    tabs = st.tabs(["💬 الشات", "🌍 الترجمة", "🎓 المراجعة"])
    
    with tabs[1]: # الترجمة
        if st.button(f"ابدأ الترجمة الفورية ({num_pages} صفحة)"):
            if deduct_attempt(num_pages):
                full_text = ""
                for page in pdf_doc:
                    full_text += page.get_text()
                
                # إرسال النص للذكاء الاصطناعي للترجمة
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "You are a professional academic translator."},
                              {"role": "user", "content": f"Translate the following text to Arabic accurately:\n\n{full_text[:15000]}"}]
                )
                translated_result = response.choices[0].message.content
                
                st.success("✅ تمت الترجمة بنجاح!")
                st.markdown(f'<div class="rtl-box">{translated_result[:1000]}...</div>', unsafe_allow_html=True)
                
                # توليد الملف المصلح للتحميل
                word_file = create_word_file(translated_result)
                st.download_button(
                    label="📥 تحميل الملف المترجم (Word)",
                    data=word_file,
                    file_name="Translated_Research.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.error("❌ رصيدك لا يكفي لترجمة هذا العدد من الصفحات.")
