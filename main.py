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
    # إضافة النص مع ضبط الاتجاه والمحاذاة
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    # تحويل الملف إلى Bytes ليتمكن المستخدم من تحميله
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- وظائف الحماية والخصم ---
def get_device_id():
    return str(uuid.getnode())

def check_security():
    dev_id = get_device_id()
    df = pd.read_csv(DB_SECURITY)
    user_row = df[df['device_id'] == dev_id]
    if not user_row.empty:
        if user_row.iloc[0]['is_blocked']: return "blocked", 0
        return "exists", user_row.iloc[0]['free_used']
    return "new", 0

def deduct_attempt(amount=1):
    if st.session_state.get('access_granted', False):
        return True
    
    df = pd.read_csv(DB_SECURITY)
    dev_id = get_device_id()
    
    # التحقق من وجود الجهاز
    mask = df['device_id'] == dev_id
    if not mask.any():
        new_row = pd.DataFrame([{'device_id': dev_id, 'free_used': 0}])
        df = pd.concat([df, new_row], ignore_index=True)
        mask = df['device_id'] == dev_id
    
    idx = df.index[mask].tolist()[0]
    
    if df.at[idx, 'free_used'] + amount <= 2:
        df.at[idx, 'free_used'] += amount
        df.to_csv(DB_SECURITY, index=False)
        st.session_state.credit = 2 - df.at[idx, 'free_used']
        return True
    return False
# ==========================================
# التنسيق البصري (CSS)
# ==========================================
st.set_page_config(page_title="ScholarNode Academy", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #ffffff !important; }}
    .main-header {{ 
        background: #1e3a8a; 
        color: #ffffff !important; 
        padding: 30px; 
        text-align: center; 
        border-radius: 15px; 
        border: 5px solid #facc15; 
        margin-bottom: 25px; 
    }}
    input[type="text"], input[type="password"], textarea {{
        color: #000000 !important; 
        background-color: #ffffff !important; 
        font-weight: bold !important; 
        font-size: 16px !important;
        border: 2px solid #1e3a8a !important;
    }}
    h1, h2, h3, p, span, label {{ 
        color: #000000 !important; 
        font-weight: bold !important; 
    }}
    .price-table {{ 
        width: 100%; 
        border-collapse: collapse; 
        background: #ffffff;
        border: 2px solid #ef4444;
    }}
    .price-table th {{ 
        background: #ef4444; 
        color: white !important; 
        padding: 10px; 
    }}
    .price-table td {{ 
        border: 1px solid #ef4444; 
        padding: 8px; 
        text-align: center; 
        color: #000000 !important;
    }}
    .price-table tr:nth-child(odd) td {{ background: #fff1f2; }}
    .price-table tr:nth-child(even) td {{ background: #facc15; }}
    .payment-box {{
        background: #1e3a8a;
        color: white !important;
        padding: 15px;
        border-radius: 10px;
        border: 3px solid #facc15;
        margin-bottom: 20px;
    }}
    .logout-btn button {{
        background-color: #ef4444 !important;
        color: white !important;
        font-weight: bold !important;
    }}
    .finance-info {{
        background: #fffbe6;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        border-right: 5px solid #facc15;
        margin-bottom: 20px;
        font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# القائمة الجانبية
# ==========================================
with st.sidebar:
    if "auth" in st.session_state:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🔴 تسجيل الخروج"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("---")

    if "total_pages" in st.session_state:
        # الحسبة: السعر 300 والرسوم 8%
        base_cost = st.session_state.total_pages * 300
        hidden_fee = base_cost * 0.08
        total_iqd = int(base_cost + hidden_fee)
        # إظهار المبلغ الصافي فقط للمشترك
        st.markdown(f"""
        <div class="finance-info">
            📊 تفاصيل كلفة الملف:<br>
            📄 عدد الصفحات: {st.session_state.total_pages}<br>
            💰 المبلغ الكلي: {total_iqd} دينار
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<h2 style="color:#1e3a8a; text-align:center;">💳 معلومات الدفع</h2>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="payment-box">
        <b>🏦 ماستر كارد الرافدين:</b><br>8369719342<br><br>
        <b>👤 الاسم:</b><br>HAYDER Z. JASIM<br><br>
        <b>📞 الهاتف:</b><br><span style="font-size:18px;">07879974395</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🏷️ جدول الكروت")
    st.markdown("""
    <table class="price-table">
        <tr><th>الفئة (دينار)</th><th>المحاولات</th></tr>
        <tr><td>10,000</td><td>66</td></tr>
        <tr><td>20,000</td><td>133</td></tr>
        <tr><td>30,000</td><td>200</td></tr>
        <tr><td>40,000</td><td>266</td></tr>
        <tr><td>50,000</td><td>333</td></tr>
        <tr><td>100,000</td><td>666</td></tr>
    </table>
    """, unsafe_allow_html=True)
    
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
            st.success(f"الكود: {new_code}")

# ==========================================
# بوابة الدخول
# ==========================================
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>المنصة الأكاديمية (ScholarNode)</h1></div>', unsafe_allow_html=True)
    status, used = check_security()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎁 الدخول المجاني")
        if used >= 2: st.error("تم استهلاك المحاولات المجانية.")
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
        st.subheader("🔑 تفعيل الاشتراك")
        in_code = st.text_input("كود الكارت:", type="password", key="sub_code")
        if st.button("تفعيل الحساب"):
            df = pd.read_csv(DB_CODES)
            match = df[(df['code'] == in_code.strip()) & (df['status'] == 'Active')]
            if not match.empty:
                idx = match.index[0]
                if df.at[idx, 'activation_date'] == "None":
                    df.at[idx, 'activation_date'] = datetime.now().strftime("%Y-%m-%d")
                    df.at[idx, 'expiry_date'] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                    df.to_csv(DB_CODES, index=False)
                st.session_state.update({"auth": True, "mode": "pro", "user": "باحث مشترك", "credit": df.at[idx, 'remaining'], "code": in_code.strip()})
                st.rerun()
    st.stop()

# ==========================================
# الواجهة الرئيسية
# ==========================================
st.markdown(f'<div class="main-header"><h1>مرحباً {st.session_state.user}</h1><h2 style="color:#facc15 !important;">الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 ارفع ملفك هنا (PDF)", type=["pdf"])

if uploaded_file:
    doc_temp = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.session_state.total_pages = len(doc_temp)
    uploaded_file.seek(0)

tabs = st.tabs(["💬 الشات الأكاديمي", "🌍 الترجمة", "🎓 المراجعة", "📄 المعاينة والتحليل"])

# تبويب الترجمة
with tabs[1]:
    st.subheader("🌍 خدمة الترجمة الأكاديمية")
    if uploaded_file:
        target_lang = st.selectbox("ترجمة إلى:", ["العربية", "English"], key="lang_select")
        if st.button(f"بدء ترجمة الملف ({st.session_state.total_pages} صفحة)"):
            if deduct_attempt(st.session_state.total_pages):
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                all_text = "\n".join([page.get_text() for page in doc])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate to {target_lang}:\n{all_text[:12000]}"}])
                translated_text = res.choices[0].message.content
                st.success("تمت الترجمة:")
                st.write(translated_text)
                
                # زر تحميل ملف Word
                word_io = create_word_file(translated_text)
                st.download_button(label="📥 تحميل الترجمة كملف Word", data=word_io, file_name="translated_document.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            else: st.error("رصيدك غير كافٍ.")
    else: st.info("يرجى رفع ملف PDF أولاً.")

# تبويب المراجعة
with tabs[2]:
    st.subheader("🎓 خدمة المراجعة الأكاديمية")
    if uploaded_file:
        if st.button(f"بدء المراجعة ({st.session_state.total_pages} صفحة)"):
            if deduct_attempt(st.session_state.total_pages):
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                all_text = "\n".join([page.get_text() for page in doc])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Review this academic text:\n{all_text[:12000]}"}])
                reviewed_text = res.choices[0].message.content
                st.success("تمت المراجعة:")
                st.write(reviewed_text)
                
                # زر تحميل ملف Word
                word_io = create_word_file(reviewed_text)
                st.download_button(label="📥 تحميل المراجعة كملف Word", data=word_io, file_name="reviewed_document.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            else: st.error("رصيدك غير كافٍ.")
    else: st.info("يرجى رفع ملف PDF أولاً.")

# (بقية التبويبات تبقى كما هي في الكود الأصلي)
with tabs[0]:
    prompt = st.chat_input("اسأل أي شيء...")
    if prompt:
        if deduct_attempt(1):
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
            st.markdown(f'<div style="color:black; background:#f0f2f6; padding:15px; border-radius:10px; border-right:5px solid #1e3a8a;">{res.choices[0].message.content}</div>', unsafe_allow_html=True)

with tabs[3]:
    if uploaded_file:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        c_left, c_right = st.columns([1, 2])
        with c_left:
            page_num = st.number_input("رقم الصفحة:", 1, len(doc), 1)
            user_task = st.text_area("المهمة:", key="page_task")
            if st.button("معالجة الصفحة"):
                if deduct_attempt(1):
                    page_text = doc[page_num-1].get_text()
                    ai_res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"نص: {page_text}\nمهمة: {user_task}"}])
                    st.success(ai_res.choices[0].message.content)
        with c_right:
            page = doc[page_num-1]
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            st.image(Image.open(io.BytesIO(pix.tobytes())), caption=f"معاينة الصفحة {page_num}")

st.markdown("<br><hr><p style='text-align:center; color:black;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
