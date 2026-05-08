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

# --- 1. إعدادات النظام والمفاتيح ---
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

DB_CODES = "scholar_main_db.csv"
DB_SECURITY = "device_tracking.csv"

# --- 2. تهيئة قواعد البيانات ---
def init_db():
    if not os.path.exists(DB_CODES):
        pd.DataFrame(columns=["code", "credit", "remaining", "status", "activation_date", "expiry_date"]).to_csv(DB_CODES, index=False)
    if not os.path.exists(DB_SECURITY):
        pd.DataFrame(columns=["device_id", "free_used", "is_blocked"]).to_csv(DB_SECURITY, index=False)

init_db()

# --- 3. وظيفة إنشاء ملف Word احترافي (عربي) ---
def create_word_file(content_text):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(12)
    
    # تقسيم النص لفقرات وضبط المحاذاة لليمين
    for line in content_text.split('\n'):
        if line.strip():
            p = doc.add_paragraph(line)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 4. وظائف الحماية والخصم (إصلاح الأخطاء السابقة) ---
def get_device_id():
    return str(uuid.getnode())

def deduct_attempt(amount=1):
    if st.session_state.get("mode") == "pro":
        df = pd.read_csv(DB_CODES)
        # التأكد من وجود الكود لتجنب IndexError
        matching_rows = df.index[df['code'] == st.session_state.code].tolist()
        if not matching_rows: return False
        
        idx = matching_rows[0]
        if df.at[idx, 'remaining'] >= amount:
            df.at[idx, 'remaining'] -= amount
            df.to_csv(DB_CODES, index=False)
            st.session_state.credit = df.at[idx, 'remaining']
            return True
    else:
        df = pd.read_csv(DB_SECURITY)
        dev_id = get_device_id()
        # التأكد من وجود الجهاز في قاعدة البيانات
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

# --- 5. التنسيق البصري CSS (هوية ScholarNode) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    .main-header { background: #1e3a8a; color: white !important; padding: 25px; text-align: center; border-radius: 15px; border: 4px solid #facc15; margin-bottom: 20px; }
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 2px solid #facc15; margin-bottom: 10px; }
    .price-table { width: 100%; border-collapse: collapse; border: 2px solid #ef4444; }
    .price-table th { background: #ef4444; color: white !important; padding: 8px; }
    .price-table td { border: 1px solid #ef4444; padding: 5px; text-align: center; color: black !important; font-weight: bold; }
    .price-table tr:nth-child(even) { background-color: #fff9c4; }
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
    st.markdown('<table class="price-table"><tr><th>الفئة</th><th>المحاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>20,000</td><td>133</td></tr><tr><td>30,000</td><td>200</td></tr><tr><td>40,000</td><td>266</td></tr><tr><td>50,000</td><td>333</td></tr><tr><td>100,000</td><td>666</td></tr></table>', unsafe_allow_html=True)
    
    st.write("---")
    adm_pass = st.text_input("لوحة التحكم (Admin):", type="password")
    if adm_pass == "HAYDER_2026":
        cat = st.selectbox("توليد فئة:", [10, 20, 30, 40, 50, 100])
        if st.button("إنشاء كود جديد"):
            new_c = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            att = {10: 66, 20: 133, 30: 200, 40: 266, 50: 333, 100: 666}[cat]
            df = pd.read_csv(DB_CODES)
            df = pd.concat([df, pd.DataFrame([{"code": new_c, "credit": att, "remaining": att, "status": "Active"}])])
            df.to_csv(DB_CODES, index=False)
            st.success(f"تم التوليد: {new_c}")

# --- 7. بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>المنصة الأكاديمية (ScholarNode)</h1></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎁 الدخول المجاني")
        u_name = st.text_input("الاسم الثلاثي:")
        if st.button("بدء التجربة"):
            if len(u_name.split()) >= 3:
                st.session_state.update({"auth": True, "mode": "free", "user": u_name, "credit": 2})
                st.rerun()
            else: st.warning("يرجى إدخال الاسم الثلاثي.")
    with c2:
        st.subheader("🔑 تفعيل الاشتراك")
        code_in = st.text_input("كود الكارت:", type="password")
        if st.button("دخول"):
            df_c = pd.read_csv(DB_CODES)
            if code_in in df_c['code'].values:
                rem = df_c[df_c['code'] == code_in]['remaining'].values[0]
                st.session_state.update({"auth": True, "mode": "pro", "user": "باحث مشترك", "credit": rem, "code": code_in})
                st.rerun()
            else: st.error("الكود غير صحيح.")
    st.stop()

# --- 8. الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً دكتور {st.session_state.user}</h1><h2>الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up_file = st.file_uploader("📂 ارفع ملف PDF", type=["pdf"])

if up_file:
    tabs = st.tabs(["💬 الشات الأكاديمي", "🌍 الترجمة الاحترافية", "🎓 المراجعة العلمية", "📄 المعاينة"])
    
    with tabs[1]: # الترجمة
        if st.button("بدء الترجمة الفورية"):
            if deduct_attempt(1):
                with st.spinner("جاري الترجمة..."):
                    # هنا نضع كود استدعاء OpenAI الفعلي
                    text_out = "نموذج ترجمة أكاديمية احترافية...\nنص مترجم من ملفك الأصلي."
                    st.success("✅ اكتملت المهمة")
                    st.download_button("📥 تحميل ملف Word", create_word_file(text_out), "ScholarNode_Translated.docx")
            else: st.error("عذراً، نفد الرصيد.")

    with tabs[3]: # المعاينة والتحليل
        doc = fitz.open(stream=up_file.read(), filetype="pdf")
        col_a, col_b = st.columns([1, 2])
        with col_a:
            p_num = st.number_input("الصفحة:", 1, len(doc), 1)
            if st.button("تحليل هذه الصفحة"):
                if deduct_attempt(1): st.info("جاري تحليل الصفحة...")
        with col_b:
            pix = doc[p_num-1].get_pixmap()
            st.image(Image.open(io.BytesIO(pix.tobytes())))

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
