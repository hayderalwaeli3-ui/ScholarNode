import streamlit as st
import pandas as pd
import os
import io
import uuid
import random
import string
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

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
        if df.at[idx, 'free_used'] < 2:
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

# --- التنسيق البصري (CSS) المستخلص من ملف الوورد ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    .main-header { background: #1e3a8a; color: white !important; padding: 30px; text-align: center; border-radius: 15px; border: 5px solid #facc15; margin-bottom: 25px; }
    h1, h2, h3, p, label { color: black !important; font-weight: bold !important; }
    .rtl-box { direction: rtl; text-align: right; background: #f8fafc; padding: 20px; border-radius: 10px; border-right: 6px solid #1e3a8a; color: black; }
    .price-table { width: 100%; border: 2px solid #ef4444; text-align: center; color: black; border-collapse: collapse; }
    .price-table th { background: #ef4444; color: white; padding: 10px; }
    .price-table td { border: 1px solid #ef4444; padding: 8px; }
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 3px solid #facc15; }
    </style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    if "auth" in st.session_state:
        if st.button("🔴 خروج من الحساب"):
            st.session_state.clear()
            st.rerun()
    st.write("---")
    st.markdown('<h2 style="color:#1e3a8a; text-align:center;">💳 معلومات الدفع</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="payment-box"><b>🏦 ماستر كارد الرافدين:</b><br>8369719342<br><br><b>👤 الاسم:</b><br>HAYDER Z. JASIM<br><br><b>📞 الهاتف:</b><br>07879974395</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏷️ جدول الكروت")
    st.markdown('<table class="price-table"><tr><th>الفئة</th><th>المحاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>20,000</td><td>133</td></tr><tr><td>30,000</td><td>200</td></tr><tr><td>40,000</td><td>266</td></tr><tr><td>50,000</td><td>333</td></tr><tr><td>100,000</td><td>666</td></tr></table>', unsafe_allow_html=True)

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>المنصة الأكاديمية (ScholarNode)</h1></div>', unsafe_allow_html=True)
    status, used = check_security()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎁 تجربة مجانية")
        if status == "blocked" or used >= 2:
            st.error("❌ انتهت المحاولات المجانية نهائياً لهذا الجهاز.")
        else:
            u_name = st.text_input("الاسم الثلاثي:")
            if st.button("بدء") and len(u_name.split()) >= 3:
                st.session_state.update({"auth": True, "mode": "free", "user": u_name, "credit": 2 - used})
                st.rerun()
    with col2:
        st.subheader("🔑 كود الاشتراك")
        in_c = st.text_input("الكود:", type="password")
        if st.button("تفعيل"):
            df = pd.read_csv(DB_CODES)
            if in_c in df['code'].values:
                st.session_state.update({"auth": True, "mode": "pro", "user": "باحث", "credit": 100, "code": in_c})
                st.rerun()
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً دكتور {st.session_state.user}</h1><h2>الرصيد المتبقي: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
file = st.file_uploader("ارفع ملف PDF الأكاديمي", type=["pdf"])

if file:
    doc_raw = file.read()
    t1, t2, t3, t4 = st.tabs(["💬 الشات الأكاديمي", "🌍 الترجمة الاحترافية", "🎓 المراجعة العلمية", "📄 المعاينة والتحليل"])

    with t1: # الشات
        prompt = st.chat_input("اسأل عن أي جزء في الملف...")
        if prompt:
            if deduct_attempt(1):
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
                st.markdown(f'<div class="rtl-box">{res.choices[0].message.content}</div>', unsafe_allow_html=True)

    with t2: # الترجمة
        if st.button("ابدأ الترجمة الفورية"):
            if deduct_attempt(1):
                st.success("تمت الترجمة بنجاح.")
                st.markdown('<div class="rtl-box">يظهر النص المترجم هنا من اليمين لليسان...</div>', unsafe_allow_html=True)
                st.download_button("📥 تحميل الترجمة (Word)", create_word_file("نص مترجم بتنسيق عربي"), "translated.docx")

    with t3: # المراجعة
        if st.button("ابدأ المراجعة الأكاديمية"):
            if deduct_attempt(1):
                st.success("تمت المراجعة العلمية.")
                st.download_button("📥 تحميل المراجعة (Word)", create_word_file("نتائج المراجعة الأكاديمية"), "review.docx")

    with t4: # المعاينة
        doc = fitz.open(stream=doc_raw, filetype="pdf")
        col_l, col_r = st.columns([1, 2])
        with col_l:
            p_num = st.number_input("رقم الصفحة:", 1, len(doc), 1)
            task = st.text_area("المهمة (مثلاً: لخص هذه الصفحة):")
            if st.button("معالجة الصفحة"):
                if deduct_attempt(1):
                    st.success("تمت المعالجة.")
        with col_r:
            pix = doc[p_num-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            st.image(Image.open(io.BytesIO(pix.tobytes())), caption=f"معاينة الصفحة {p_num}")

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
