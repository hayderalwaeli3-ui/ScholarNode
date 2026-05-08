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

# --- وظيفة إنشاء ملف Word ---
def create_word_file(text):
    doc = Document()
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- وظيفة جلب معرف الجهاز ---
def get_device_id():
    return str(uuid.getnode())

# --- دالة الخصم والقفل الصارم ---
def deduct_attempt(amount=1):
    # إذا كان المستخدم مديراً، لا نخصم
    if st.session_state.get('access_granted', False):
        return True
    
    # للمشتركين (Pro)
    if st.session_state.get('mode') == 'pro':
        df = pd.read_csv(DB_CODES)
        code = st.session_state.get('code')
        idx = df.index[df['code'] == code].tolist()[0]
        if df.at[idx, 'remaining'] >= amount:
            df.at[idx, 'remaining'] -= amount
            df.to_csv(DB_CODES, index=False)
            st.session_state.credit = df.at[idx, 'remaining']
            return True
        return False
    
    # للمستخدمين المجانيين (Free)
    else:
        df = pd.read_csv(DB_SECURITY)
        dev_id = get_device_id()
        mask = df['device_id'] == dev_id
        if not mask.any():
            new_row = pd.DataFrame([{'device_id': dev_id, 'free_used': 0, 'is_blocked': False}])
            df = pd.concat([df, new_row], ignore_index=True)
            mask = df['device_id'] == dev_id
        
        idx = df.index[mask].tolist()[0]
        # قفل الأمان: إذا وصل للمحاولتين، نوقف الموقع فوراً
        if df.at[idx, 'free_used'] >= 2:
            st.error("❌ نفد رصيدك المجاني. يرجى تفعيل كود الاشتراك.")
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
    .stApp { background-color: #ffffff !important; }
    .main-header { background: #1e3a8a; color: white !important; padding: 30px; text-align: center; border-radius: 15px; border: 5px solid #facc15; margin-bottom: 25px; }
    h1, h2, h3, p, span, label { color: #000000 !important; font-weight: bold !important; }
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 3px solid #facc15; }
    </style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    if "auth" in st.session_state:
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear()
            st.rerun()
    st.markdown('<h2 style="color:#1e3a8a; text-align:center;">💳 معلومات الدفع</h2>', unsafe_allow_html=True)
    st.markdown('<div class="payment-box"><b>🏦 ماستر كارد الرافدين:</b><br>8369719342<br><br><b>👤 الاسم:</b><br>HAYDER Z. JASIM</div>', unsafe_allow_html=True)

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>المنصة الأكاديمية (ScholarNode)</h1></div>', unsafe_allow_html=True)
    df_sec = pd.read_csv(DB_SECURITY)
    dev_id = get_device_id()
    used = df_sec[df_sec['device_id'] == dev_id]['free_used'].values[0] if dev_id in df_sec['device_id'].values else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎁 الدخول المجاني")
        if used >= 2: st.error("المحاولات المجانية نفدت.")
        else:
            u_name = st.text_input("الاسم الثلاثي:", key="free_name")
            if st.button("بدء التجربة") and len(u_name.split()) >= 3:
                st.session_state.update({"auth": True, "mode": "free", "user": u_name, "credit": 2 - used})
                st.rerun()
    with col2:
        st.subheader("🔑 تفعيل الاشتراك")
        in_code = st.text_input("كود الكارت:", type="password")
        if st.button("تفعيل الحساب"):
            df = pd.read_csv(DB_CODES)
            match = df[(df['code'] == in_code.strip()) & (df['status'] == 'Active')]
            if not match.empty:
                st.session_state.update({"auth": True, "mode": "pro", "user": "باحث مشترك", "credit": match.iloc[0]['remaining'], "code": in_code.strip()})
                st.rerun()
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً Courage</h1><h2 style="color:#facc15 !important;">الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 ارفع ملفك هنا (PDF)", type=["pdf"])
if uploaded_file:
    doc_bytes = uploaded_file.read()
    doc_temp = fitz.open(stream=doc_bytes, filetype="pdf")
    st.session_state.total_pages = len(doc_temp)

tabs = st.tabs(["💬 الشات الأكاديمي", "🌍 الترجمة", "🎓 المراجعة", "📄 المعاينة والتحليل"])

with tabs[0]:
    prompt = st.chat_input("اسأل أي شيء...")
    if prompt:
        if deduct_attempt(1):
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
            st.info(res.choices[0].message.content)

with tabs[1]:
    if uploaded_file and st.button("بدء ترجمة أول صفحة"):
        if deduct_attempt(1):
            doc = fitz.open(stream=doc_bytes, filetype="pdf")
            text = doc[0].get_text()
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate this to Arabic: {text[:2000]}"}])
            st.write(res.choices[0].message.content)

with tabs[3]:
    if uploaded_file:
        doc = fitz.open(stream=doc_bytes, filetype="pdf")
        p_num = st.number_input("رقم الصفحة:", 1, len(doc), 1)
        if st.button("حلل الصفحة"):
            if deduct_attempt(1):
                txt = doc[p_num-1].get_text()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"حلل: {txt[:2000]}"}])
                st.success(res.choices[0].message.content)
        pix = doc[p_num-1].get_pixmap()
        st.image(Image.open(io.BytesIO(pix.tobytes())))

st.markdown("<hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
