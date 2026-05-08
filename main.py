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
from docx.shared import Pt
from openai import OpenAI

# --- 1. الإعدادات والمفاتيح ---
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

DB_CODES = "scholar_main_db.csv"
DB_SECURITY = "device_tracking.csv"

def init_db():
    if not os.path.exists(DB_CODES):
        pd.DataFrame(columns=["code", "credit", "remaining", "status"]).to_csv(DB_CODES, index=False)
    if not os.path.exists(DB_SECURITY):
        pd.DataFrame(columns=["device_id", "free_used", "is_blocked"]).to_csv(DB_SECURITY, index=False)

init_db()

# --- 2. وظيفة إنشاء ملف Word (حل مشكلة الملف الذي لا يفتح) ---
def create_word_file(text_content):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(12)
    for line in text_content.split('\n'):
        if line.strip():
            p = doc.add_paragraph(line)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT  # دعم العربية
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. محرك الترجمة الذكي (يمنع التعليق) ---
def translate_in_chunks(full_text):
    chunks = [full_text[i:i+2000] for i in range(0, len(full_text), 2000)]
    translated_text = ""
    progress = st.progress(0)
    for i, chunk in enumerate(chunks):
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "مترجم أكاديمي محترف من الإنجليزية للعربية."},
                      {"role": "user", "content": chunk}]
        )
        translated_text += res.choices[0].message.content + "\n"
        progress.progress((i + 1) / len(chunks))
    return translated_text

# --- 4. وظائف الحماية والخصم (إصلاح IndexError) ---
def get_device_id():
    if 'device_id' not in st.session_state:
        st.session_state.device_id = str(uuid.getnode())
    return st.session_state.device_id

def deduct_attempt(amount=1):
    if st.session_state.get("mode") == "pro":
        df = pd.read_csv(DB_CODES)
        matches = df.index[df['code'] == st.session_state.code].tolist()
        if matches:
            idx = matches[0]
            if df.at[idx, 'remaining'] >= amount:
                df.at[idx, 'remaining'] -= amount
                df.to_csv(DB_CODES, index=False)
                st.session_state.credit = df.at[idx, 'remaining']
                return True
    else:
        df = pd.read_csv(DB_SECURITY)
        dev_id = get_device_id()
        if dev_id not in df['device_id'].values:
            df = pd.concat([df, pd.DataFrame([{"device_id": dev_id, "free_used": 0, "is_blocked": False}])], ignore_index=True)
        idx = df.index[df['device_id'] == dev_id].tolist()[0]
        if df.at[idx, 'free_used'] + amount <= 2:
            df.at[idx, 'free_used'] += amount
            if df.at[idx, 'free_used'] >= 2: df.at[idx, 'is_blocked'] = True
            df.to_csv(DB_SECURITY, index=False)
            st.session_state.credit = 2 - df.at[idx, 'free_used']
            return True
    return False

# --- 5. الهوية البصرية (استعادة كافة الألوان والكروت) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
    <style>
    .main-header { background: #1e3a8a; color: white; padding: 20px; text-align: center; border-radius: 15px; border: 4px solid #facc15; }
    .payment-box { background: #1e3a8a; color: white; padding: 15px; border-radius: 10px; border: 2px solid #facc15; }
    .price-table { width: 100%; border: 2px solid #ef4444; border-collapse: collapse; }
    .price-table th { background: #ef4444; color: white; padding: 8px; }
    .price-table td { border: 1px solid #ef4444; text-align: center; font-weight: bold; padding: 5px; color: black; }
    </style>
""", unsafe_allow_html=True)

# --- 6. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    if "auth" in st.session_state:
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear()
            st.rerun()
    st.markdown('<div class="payment-box"><b>🏦 ماستر كارد الرافدين:</b><br>8369719342<br><b>👤 HAYDER Z. JASIM</b><br><b>📞 07879974395</b></div>', unsafe_allow_html=True)
    st.markdown("### 🏷️ باقات الاشتراك")
    st.markdown('<table class="price-table"><tr><th>الفئة</th><th>المحاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr style="background:#fff9c4;"><td>20,000</td><td>133</td></tr><tr><td>30,000</td><td>200</td></tr><tr style="background:#fff9c4;"><td>40,000</td><td>266</td></tr><tr><td>50,000</td><td>333</td></tr><tr style="background:#ffcdd2;"><td>100,000</td><td>666</td></tr></table>', unsafe_allow_html=True)
    
    adm = st.text_input("لوحة التحكم:", type="password")
    if adm == "HAYDER_2026":
        cat = st.selectbox("الفئة:", [10, 20, 30, 40, 50, 100])
        if st.button("توليد كود"):
            nc = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            att = {10: 66, 20: 133, 30: 200, 40: 266, 50: 333, 100: 666}[cat]
            df = pd.read_csv(DB_CODES)
            df = pd.concat([df, pd.DataFrame([{"code": nc, "credit": att, "remaining": att, "status": "Active"}])])
            df.to_csv(DB_CODES, index=False)
            st.success(f"الكود: {nc}")

# --- 7. بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎁 تجربة مجانية")
        name = st.text_input("الاسم الثلاثي:")
        if st.button("دخول") and len(name.split()) >= 3:
            st.session_state.update({"auth": True, "mode": "free", "user": name, "credit": 2})
            st.rerun()
    with c2:
        st.subheader("🔑 تفعيل كود")
        code_in = st.text_input("الكود:", type="password")
        if st.button("تفعيل"):
            df_c = pd.read_csv(DB_CODES)
            if code_in in df_c['code'].values:
                r = df_c[df_c['code'] == code_in]['remaining'].values[0]
                st.session_state.update({"auth": True, "mode": "pro", "user": "باحث مشترك", "credit": r, "code": code_in})
                st.rerun()
    st.stop()

# --- 8. الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً دكتور {st.session_state.user}</h1><h2>رصيدك: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
file = st.file_uploader("📂 ارفع ملف PDF", type=["pdf"])

if file:
    doc_bytes = file.read()
    tabs = st.tabs(["💬 الشات", "🌍 الترجمة", "🎓 المراجعة", "📄 المعاينة"])
    
    with tabs[1]: # الترجمة الشاملة
        if st.button("بدء الترجمة الأكاديمية"):
            if deduct_attempt(1):
                pdf = fitz.open(stream=doc_bytes, filetype="pdf")
                full_raw = "".join([p.get_text() for p in pdf])
                final_text = translate_in_chunks(full_raw)
                st.success("✅ تمت الترجمة بنجاح")
                st.download_button("📥 تحميل Word", create_word_file(final_text), "ScholarNode_Translation.docx")
