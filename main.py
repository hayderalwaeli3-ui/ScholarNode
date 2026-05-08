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

# --- وظيفة إنشاء ملف Word بتنسيق عربي ---
def create_word_file(text):
    doc = Document()
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- وظائف الحماية والخصم ---
def get_device_id():
    return str(uuid.getnode())

def deduct_attempt(amount=1):
    if st.session_state.get('access_granted', False):
        return True
    
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
    else:
        df = pd.read_csv(DB_SECURITY)
        dev_id = get_device_id()
        mask = df['device_id'] == dev_id
        if not mask.any():
            new_row = pd.DataFrame([{'device_id': dev_id, 'free_used': 0, 'is_blocked': False}])
            df = pd.concat([df, new_row], ignore_index=True)
            mask = df['device_id'] == dev_id
        
        idx = df.index[mask].tolist()[0]
        if df.at[idx, 'free_used'] >= 2:
            st.error("❌ نفد رصيدك المجاني. يرجى الحصول على كود وصول للمتابعة.")
            st.stop()
            return False
        
        df.at[idx, 'free_used'] += amount
        df.to_csv(DB_SECURITY, index=False)
        st.session_state.credit = 2 - df.at[idx, 'free_used']
        return True

# --- التنسيق البصري (CSS) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    .main-header { background: #1e3a8a; color: white !important; padding: 30px; text-align: center; border-radius: 15px; border: 5px solid #facc15; margin-bottom: 25px; }
    h1, h2, h3, p, span, label { color: #000000 !important; font-weight: bold !important; }
    .price-table { width: 100%; border-collapse: collapse; background: #ffffff; border: 2px solid #ef4444; }
    .price-table th { background: #ef4444; color: white !important; padding: 10px; }
    .price-table td { border: 1px solid #ef4444; padding: 8px; text-align: center; color: #000000 !important; }
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 3px solid #facc15; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    if "auth" in st.session_state:
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear()
            st.rerun()
    
    st.markdown('<h2 style="color:#1e3a8a; text-align:center;">💳 معلومات الدفع</h2>', unsafe_allow_html=True)
    st.markdown('<div class="payment-box"><b>🏦 ماستر كارد الرافدين:</b><br>8369719342<br><br><b>👤 الاسم:</b><br>HAYDER Z. JASIM<br><br><b>📞 الهاتف:</b><br>07879974395</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏷️ جدول الكروت")
    st.markdown('<table class="price-table"><tr><th>الفئة</th><th>المحاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>50,000</td><td>333</td></tr></table>', unsafe_allow_html=True)

    st.write("---")
    adm = st.text_input("لوحة التحكم (Admin):", type="password")
    if adm == "HAYDER_2026":
        cat = st.selectbox("توليد فئة:", [10, 20, 30, 40, 50, 100])
        if st.button("توليد كود الاشتراك"):
            new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            attempts = {10: 66, 20: 133, 30: 200, 40: 266, 50: 333, 100: 666}[cat]
            df = pd.read_csv(DB_CODES)
            new_entry = pd.DataFrame([{"code": new_code, "credit": attempts, "remaining": attempts, "status": "Active", "activation_date": "None", "expiry_date": "None"}])
            pd.concat([df, new_entry]).to_csv(DB_CODES, index=False)
            st.success(f"الكود: {new_code}")

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
st.markdown(f'<div class="main-header"><h1>مرحباً Courage</h1><h2 style="color:#facc15 !important;">الرصيد المتبقي: {st.session_state.credit} محاولة</h2></div>', unsafe_
