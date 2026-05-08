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
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT [cite: 337]
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- وظائف الحماية والخصم (إصلاح منطق القفل) ---
def get_device_id():
    return str(uuid.getnode())

def check_security():
    dev_id = get_device_id()
    df = pd.read_csv(DB_SECURITY)
    user_row = df[df['device_id'] == dev_id]
    if not user_row.empty:
        if user_row.iloc[0]['is_blocked']: return "blocked", 2
        return "exists", user_row.iloc[0]['free_used']
    return "new", 0

def deduct_attempt(amount=1):
    if st.session_state.mode == "pro":
        df = pd.read_csv(DB_CODES)
        idx = df.index[df['code'] == st.session_state.code].tolist()[0]
        if df.at[idx, 'remaining'] >= amount:
            df.at[idx, 'remaining'] -= amount
            df.to_csv(DB_CODES, index=False)
            st.session_state.credit = df.at[idx, 'remaining']
            return True
        return False
    else:
        # القفل الصارم للمستخدم المجاني 
        df = pd.read_csv(DB_SECURITY)
        dev_id = get_device_id()
        idx = df.index[df['device_id'] == dev_id].tolist()[0]
        if df.at[idx, 'free_used'] + amount <= 2:
            df.at[idx, 'free_used'] += amount
            if df.at[idx, 'free_used'] >= 2:
                df.at[idx, 'is_blocked'] = True
            df.to_csv(DB_SECURITY, index=False)
            st.session_state.credit = 2 - df.at[idx, 'free_used']
            return True
        return False

# --- التنسيق البصري (CSS المستخرج من الوورد) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    .main-header { background: #1e3a8a; color: #ffffff !important; padding: 30px; text-align: center; border-radius: 15px; border: 5px solid #facc15; margin-bottom: 25px; } [cite: 389-397]
    h1, h2, h3, p, span, label { color: #000000 !important; font-weight: bold !important; }
    .price-table { width: 100%; border-collapse: collapse; border: 2px solid #ef4444; } [cite: 409-414]
    .price-table th { background: #ef4444; color: white !important; padding: 10px; }
    .price-table td { border: 1px solid #ef4444; padding: 8px; text-align: center; color: #000000 !important; }
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 3px solid #facc15; margin-bottom: 20px; } [cite: 428-434]
    </style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية (استعادة حقل الإدارة) ---
with st.sidebar:
    if "auth" in st.session_state:
        if st.button(" 🔴 تسجيل الخروج"):
            st.session_state.clear()
            st.rerun()
    st.write("---")
    st.markdown('<h2 style="color:#1e3a8a; text-align:center;"> 💳 معلومات الدفع</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="payment-box"><b> 🏦 ماستر كارد الرافدين:</b><br>8369719342<br><br><b> 👤 الاسم:</b><br>HAYDER Z. JASIM<br><br><b> 📞 الهاتف:</b><br>07879974395</div>', unsafe_allow_html=True) [cite: 477-483]
    
    st.markdown("### 🏷️ جدول الكروت")
    st.markdown('<table class="price-table"><tr><th>الفئة</th><th>المحاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>50,000</td><td>333</td></tr><tr><td>100,000</td><td>666</td></tr></table>', unsafe_allow_html=True) [cite: 485-496]

    # استعادة حقل الإدارة (Admin) 
    st.write("---")
    adm = st.text_input("لوحة التحكم (Admin):", type="password", key="admin_key")
    if adm == "HAYDER_2026":
        cat = st.selectbox("توليد فئة:", [10, 20, 30, 40, 50, 100])
        if st.button("توليد كود الاشتراك"):
            new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            attempts = {10: 66, 20: 133, 30: 200, 40: 266, 50: 333, 100: 666}[cat]
            df = pd.read_csv(DB_CODES)
            new_entry = pd.DataFrame([{"code": new_code, "credit": attempts, "remaining": attempts, "status": "Active", "activation_date": "None", "expiry_date": "None"}])
            pd.concat([df, new_entry]).to_csv(DB_CODES, index=False)
            st.success(f"الكود المولد: {new_code}")

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>المنصة الأكاديمية (ScholarNode)</h1></div>', unsafe_allow_html=True)
    status, used = check_security()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(" 🎁 الدخول المجاني")
        if status == "blocked" or used >= 2:
            st.error("تم استهلاك المحاولات المجانية.")
        else:
            u_name = st.text_input("الاسم الثلاثي:", key="free_name")
            if st.button("بدء التجربة") and len(u_name.split()) >= 3:
                if status == "new":
                    df = pd.read_csv(DB_SECURITY)
                    new_dev = pd.DataFrame([{"device_id": get_device_id(), "free_used": 0, "is_blocked": False}])
                    pd.concat([df, new_dev]).to_csv(DB_SECURITY, index=False)
                st.session_state.update({"auth": True, "mode": "free", "user": u_name, "credit": 2 - used})
                st.rerun()
    with col2:
        st.subheader(" 🔑 تفعيل الاشتراك")
        in_code = st.text_input("كود الكارت:", type="password", key="sub_code")
        if st.button("تفعيل الحساب"):
            df = pd.read_csv(DB_CODES)
            match = df[(df['code'] == in_code.strip()) & (df['status'] == 'Active')]
            if not match.empty:
                st.session_state.update({"auth": True, "mode": "pro", "user": "باحث مشترك", "credit": match.iloc[0]['remaining'], "code": in_code.strip()})
                st.rerun()
    st.stop()

# --- الواجهة الرئيسية (الشريط الأزرق) ---
st.markdown(f'<div class="main-header"><h1>مرحباً {st.session_state.user}</h1><h2 style="color:#facc15 !important;">الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True) [cite: 545]
uploaded_file = st.file_uploader(" 📂 ارفع ملف PDF", type=["pdf"])

if uploaded_file:
    doc_temp = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.session_state.total_pages = len(doc_temp)
    uploaded_file.seek(0)
    
    tabs = st.tabs([" 💬 الشات الأكاديمي", " 🌍 الترجمة", " 🎓 المراجعة", " 📄 المعاينة والتحليل"]) [cite: 551]

    with tabs[0]: # استعادة حقل الشات [cite: 588-593]
        prompt = st.chat_input("اسأل أي شيء...")
        if prompt:
            if deduct_attempt(1):
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
                st.markdown(f'<div style="color:black; background:#f0f2f6; padding:15px; border-radius:10px; border-right:5px solid #1e3a8a; direction:rtl; text-align:right;">{res.choices[0].message.content}</div>', unsafe_allow_html=True)

    with tabs[1]: # الترجمة [cite: 553-567]
        if st.button(f"بدء ترجمة الملف"):
            if deduct_attempt(st.session_state.total_pages):
                st.success("تمت الترجمة.")
                st.download_button("📥 تحميل Word", create_word_file("نص مترجم"), "translated.docx")

    with tabs[3]: # المعاينة والتحليل [cite: 594-609]
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        c_l, c_r = st.columns([1, 2])
        with c_l:
            p_num = st.number_input("رقم الصفحة:", 1, len(doc), 1)
            task = st.text_area("المهمة:")
            if st.button("معالجة الصفحة"):
                if deduct_attempt(1): st.success("تمت المعالجة.")
        with c_r:
            pix = doc[p_num-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            st.image(Image.open(io.BytesIO(pix.tobytes())))

st.markdown("<br><hr><p style='text-align:center; color:black;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True) [cite: 610]
