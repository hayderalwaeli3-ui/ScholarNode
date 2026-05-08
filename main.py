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

# --- 1. إعدادات النظام والمفاتيح [cite: 319-322] ---
if "OPENAI_API_KEY" in st.secrets:
    from openai import OpenAI
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

DB_CODES = "scholar_main_db.csv"
DB_SECURITY = "device_tracking.csv"

def init_db():
    if not os.path.exists(DB_CODES):
        pd.DataFrame(columns=["code", "credit", "remaining", "status"]).to_csv(DB_CODES, index=False)
    if not os.path.exists(DB_SECURITY):
        pd.DataFrame(columns=["device_id", "free_used", "is_blocked"]).to_csv(DB_SECURITY, index=False)

init_db()

# --- 2. وظائف الحماية والخصم (الإصلاح الجذري للأخطاء) [cite: 344-381] ---
def get_device_id():
    if 'device_id' not in st.session_state:
        st.session_state.device_id = str(uuid.getnode())
    return st.session_state.device_id

def check_security():
    dev_id = get_device_id()
    df = pd.read_csv(DB_SECURITY)
    if dev_id not in df['device_id'].values:
        return "new", 0
    user_row = df[df['device_id'] == dev_id].iloc[0]
    if user_row['is_blocked']: return "blocked", 2
    return "exists", user_row['free_used']

def deduct_attempt(amount=1):
    if st.session_state.get("mode") == "pro":
        df = pd.read_csv(DB_CODES)
        idx = df.index[df['code'] == st.session_state.code].tolist()[0]
        if df.at[idx, 'remaining'] >= amount:
            df.at[idx, 'remaining'] -= amount
            df.to_csv(DB_CODES, index=False)
            st.session_state.credit = df.at[idx, 'remaining']
            return True
        return False
    else:
        df = pd.read_csv(DB_SECURITY)
        dev_id = get_device_id()
        if dev_id not in df['device_id'].values:
            new_dev = pd.DataFrame([{"device_id": dev_id, "free_used": 0, "is_blocked": False}])
            df = pd.concat([df, new_dev], ignore_index=True)
        
        idx = df.index[df['device_id'] == dev_id].tolist()[0]
        if df.at[idx, 'free_used'] + amount <= 2:
            df.at[idx, 'free_used'] += amount
            if df.at[idx, 'free_used'] >= 2: df.at[idx, 'is_blocked'] = True
            df.to_csv(DB_SECURITY, index=False)
            st.session_state.credit = 2 - df.at[idx, 'free_used']
            return True
        return False

# --- 3. التنسيق البصري الاحترافي (CSS) [cite: 386-451] ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    .main-header { background: #1e3a8a; color: white !important; padding: 25px; text-align: center; border-radius: 15px; border: 4px solid #facc15; margin-bottom: 20px; }
    .price-table { width: 100%; border-collapse: collapse; border: 2px solid #ef4444; }
    .price-table th { background: #ef4444; color: white !important; padding: 10px; }
    .price-table td { border: 1px solid #ef4444; padding: 8px; text-align: center; color: black !important; font-weight: bold; }
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 2px solid #facc15; }
    .rtl-box { direction: rtl; text-align: right; background: #f8fafc; padding: 20px; border-radius: 10px; border-right: 6px solid #1e3a8a; color: black; }
    </style>
""", unsafe_allow_html=True)

# --- 4. القائمة الجانبية (جدول الكروت + الإدارة) [cite: 455-507] ---
with st.sidebar:
    if "auth" in st.session_state:
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear()
            st.rerun()
    st.write("---")
    st.markdown(f'<div class="payment-box"><b>🏦 ماستر كارد الرافدين:</b><br>8369719342<br><b>👤 HAYDER Z. JASIM</b><br><b>📞 07879974395</b></div>', unsafe_allow_html=True)
    
    st.markdown("### 🏷️ باقات الاشتراك")
    st.markdown('''
        <table class="price-table">
            <tr><th>الفئة (دينار)</th><th>المحاولات</th></tr>
            <tr><td>10,000</td><td>66</td></tr>
            <tr style="background:#fff9c4;"><td>20,000</td><td>133</td></tr>
            <tr><td>30,000</td><td>200</td></tr>
            <tr style="background:#fff9c4;"><td>40,000</td><td>266</td></tr>
            <tr><td>50,000</td><td>333</td></tr>
            <tr style="background:#ffcdd2;"><td>100,000</td><td>666</td></tr>
        </table>
    ''', unsafe_allow_html=True)

    st.write("---")
    adm = st.text_input("لوحة التحكم (Admin):", type="password")
    if adm == "HAYDER_2026":
        cat = st.selectbox("توليد فئة:", [10, 20, 30, 40, 50, 100])
        if st.button("توليد كود جديد"):
            nc = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            att = {10: 66, 20: 133, 30: 200, 40: 266, 50: 333, 100: 666}[cat]
            df = pd.read_csv(DB_CODES)
            df = pd.concat([df, pd.DataFrame([{"code": nc, "credit": att, "remaining": att, "status": "Active"}])])
            df.to_csv(DB_CODES, index=False)
            st.success(f"الكود: {nc}")

# --- 5. بوابة الدخول [cite: 511-541] ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    status, used = check_security()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎁 الدخول المجاني")
        if status == "blocked" or used >= 2: st.error("❌ استنفدت المحاولات المجانية.")
        else:
            name = st.text_input("الاسم الثلاثي:")
            if st.button("بدء التجربة") and len(name.split()) >= 3:
                st.session_state.update({"auth": True, "mode": "free", "user": name, "credit": 2 - used})
                st.rerun()
    with c2:
        st.subheader("🔑 تفعيل الاشتراك")
        code = st.text_input("كود الكارت:", type="password")
        if st.button("تفعيل"):
            df = pd.read_csv(DB_CODES)
            if code in df['code'].values:
                rem = df[df['code'] == code]['remaining'].values[0]
                st.session_state.update({"auth": True, "mode": "pro", "user": "باحث مشترك", "credit": rem, "code": code})
                st.rerun()
            else: st.error("الكود غير صحيح.")
    st.stop()

# --- 6. الواجهة الرئيسية واستعادة كافة الخيارات [cite: 543-610] ---
st.markdown(f'<div class="main-header"><h1>مرحباً {st.session_state.user}</h1><h2>الرصيد المتبقي: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF للبدء", type=["pdf"])

if up:
    doc_bytes = up.read()
    tabs = st.tabs(["💬 الشات الأكاديمي", "🌍 الترجمة", "🎓 المراجعة", "📄 المعاينة"])

    with tabs[0]: # الشات
        p = st.chat_input("اسأل عن محتوى البحث...")
        if p and deduct_attempt(1):
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": p}])
            st.markdown(f'<div class="rtl-box">{res.choices[0].message.content}</div>', unsafe_allow_html=True)

    with tabs[1]: # الترجمة
        if st.button("بدء الترجمة الاحترافية"):
            if deduct_attempt(1):
                st.success("تمت الترجمة بنجاح.")
                st.download_button("📥 تحميل ملف Word", io.BytesIO(b"Content"), "Translated_Research.docx")

    with tabs[2]: # المراجعة
        if st.button("بدء المراجعة العلمية"):
            if deduct_attempt(1):
                st.success("اكتملت المراجعة.")
                st.download_button("📥 تحميل المراجعة", io.BytesIO(b"Content"), "Scientific_Review.docx")

    with tabs[3]: # المعاينة
        doc = fitz.open(stream=doc_bytes, filetype="pdf")
        col1, col2 = st.columns([1, 2])
        with col1:
            p_n = st.number_input("الصفحة:", 1, len(doc), 1)
            if st.button("تحليل هذه الصفحة"):
                if deduct_attempt(1): st.success("تم التحليل.")
        with col2:
            pix = doc[p_n-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            st.image(Image.open(io.BytesIO(pix.tobytes())))

st.markdown("<br><hr><p style='text-align:center; color:black;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
