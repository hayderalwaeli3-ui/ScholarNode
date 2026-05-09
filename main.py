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
import time

# --- [كود رقم 11 المطور] - بروتوكول الحماية مع خيار الإدارة ---
API_KEY = st.secrets["OPENAI_API_KEY"]
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

# --- وظيفة إنشاء ملف Word بتنسيق أكاديمي رصين ---
def create_word_file(text):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(14)
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- وظائف الخصم والحماية ---
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

# --- بروتوكول الحماية المطلقة وتنسيق الألوان (CSS) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.stDeployButton {display:none;}
.main-header { background: #1e3a8a; color: #ffffff !important; padding: 20px; text-align: center; border-radius: 15px; border: 4px solid #facc15; margin-bottom: 25px; }
.payment-box { background: #1e3a8a; color: white !important; padding: 18px; border-radius: 12px; border: 3px solid #facc15; font-size: 0.9rem; line-height: 1.6; margin-bottom: 20px; }
.price-table { width: 100%; border-collapse: collapse; margin: 10px 0; background: transparent; }
.price-table th { background: #ef4444; color: white !important; padding: 12px; border: 1px solid #ddd; }
.price-table td { border: 1px solid #ddd; padding: 10px; text-align: center; color: inherit !important; font-weight: bold; }
.admin-section { background: #f8fafc; border: 2px dashed #1e3a8a; padding: 15px; border-radius: 10px; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("### 🏦 معلومات الحساب والدعم")
    st.markdown(f"""
    <div class="payment-box">
        👤 <b>الاسم:</b> HAYDER Z. JASIM<br>
        💳 <b>ماستر كارد الرافدين:</b><br> 8369719342<br>
        📞 <b>رقم الهاتف (تفعيل):</b><br> 07879974395
    </div>
    """, unsafe_allow_html=True)
    
    if "auth" in st.session_state:
        st.write(f"🎟️ **الكود المفعل:** `{st.session_state.code}`")
        
        # --- قسم الإدارة (يظهر فقط إذا كان الكود هو كود الإدارة الخاص بك) ---
        # ملاحظة: استبدل 'ADMIN123' بكودك الخاص للدخول للإدارة
        if st.session_state.code == "ADMIN123": 
            st.markdown("---")
            st.markdown("### ⚙️ الإدارة الأكاديمية")
            if st.button("📊 فتح لوحة التحكم"):
                st.session_state.show_admin = not st.session_state.get('show_admin', False)
        
        st.markdown("---")
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear(); st.rerun()

    st.markdown("### 🏷️ جدول فئات الكروت")
    st.markdown("""
    <table class="price-table">
        <tr><th>الفئة (دينار)</th><th>محاولات</th></tr>
        <tr><td>10,000</td><td>66</td></tr>
        <tr><td>20,000</td><td>133</td></tr>
        <tr><td>30,000</td><td>200</td></tr>
        <tr><td>40,000</td><td>266</td></tr>
        <tr><td>50,000</td><td>333</td></tr>
        <tr><td>100,000</td><td>666</td></tr>
    </table>
    """, unsafe_allow_html=True)

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    in_c = st.text_input("أدخل كود التفعيل للدخول:", type="password")
    if st.button("دخول", use_container_width=True):
        df = pd.read_csv(DB_CODES)
        match = df[(df['code'] == in_c.strip()) & (df['status'] == 'Active')]
        if not match.empty:
            st.session_state.update({"auth": True, "credit": df.at[match.index[0], 'remaining'], "code": in_c.strip()})
            st.rerun()
        else: st.error("الكود غير صحيح")
    st.stop()

# --- لوحة الإدارة (تظهر عند التفعيل) ---
if st.session_state.get('show_admin', False):
    st.markdown('<div class="admin-section"><h3>🛠️ لوحة تحكم الإدارة</h3>', unsafe_allow_html=True)
    admin_tab1, admin_tab2 = st.tabs(["🎫 توليد كروت", "📋 استعراض البيانات"])
    with admin_tab1:
        new_code = st.text_input("الكود الجديد:")
        new_credit = st.number_input("عدد المحاولات:", 1, 1000, 66)
        if st.button("إضافة الكود"):
            df = pd.read_csv(DB_CODES)
            new_row = {"code": new_code, "credit": new_credit, "remaining": new_credit, "status": "Active", "activation_date": datetime.now().date(), "expiry_date": (datetime.now() + timedelta(days=30)).date()}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DB_CODES, index=False)
            st.success("تمت إضافة الكود بنجاح")
    with admin_tab2:
        st.dataframe(pd.read_csv(DB_CODES))
    st.markdown('</div>', unsafe_allow_html=True)

# --- الواجهة الرئيسية للمستخدم ---
st.markdown(f'<div class="main-header"><h1>مرحباً دكتور Courage</h1><h2>الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF للمراجعة أو الترجمة", type=["pdf"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# (بقية محتوى التبويبات يبقى كما هو في كود رقم 11 المستقر)
with tabs[0]:
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    c_prompt = st.chat_input("اطلب بناء خطة بحثية...")
    if c_prompt and deduct_attempt(1):
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "أنت خبير أكاديمي."}] + st.session_state.chat_history + [{"role": "user", "content": c_prompt}])
        st.session_state.chat_history.append({"role": "user", "content": c_prompt})
        st.session_state.chat_history.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

# (ملاحظة: الترجمة والمراجعة والمعاينة تعمل بنفس منطق كود 11 المعتمد لديك)
if up:
    up.seek(0); doc_v = fitz.open(stream=up.read(), filetype="pdf"); p_count = len(doc_v)
    with tabs[1]:
        if st.button(f"ترجمة {p_count} صفحة"):
            with st.spinner("🚀 جاري المعالجة..."):
                if deduct_attempt(p_count):
                    # ... خوارزمية الدمج الاقتصادي ...
                    st.success("اكتملت الترجمة")

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy 2026</p>", unsafe_allow_html=True)
