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

# --- [كود رقم 11 المعتمد] - نسخة دكتور Courage الكاملة مع الإدارة ---
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
.admin-view-box { background: #f8fafc; border: 2px dashed #1e3a8a; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
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
        st.write(f"🎟️ **الكود:** `{st.session_state.code}`")
        
        # --- خيار الإدارة للأستاذ هايدر فقط ---
        # إذا دخلت بكود ADMIN123 أو أي كود تحدده أنت للإدارة
        if st.session_state.code == "ADMIN123":
            st.markdown("---")
            if st.button("🛠️ لوحة إدارة الأكواد"):
                st.session_state.admin_active = not st.session_state.get('admin_active', False)
        
        st.markdown("---")
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear(); st.rerun()

    st.markdown("### 🏷️ فئات الشحن")
    st.markdown("""
    <table class="price-table">
        <tr><th>الفئة</th><th>محاولات</th></tr>
        <tr><td>10,000</td><td>66</td></tr>
        <tr><td>100,000</td><td>666</td></tr>
    </table>
    """, unsafe_allow_html=True)

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    in_c = st.text_input("أدخل كود التفعيل للدخول:", type="password")
    if st.button("دخول", use_container_width=True):
        # ميزة الطوارئ: إذا كتبت ADMIN123 ولم يكن موجوداً في الملف، سيفتح لك الإدارة فوراً
        if in_c.strip() == "ADMIN123":
            st.session_state.update({"auth": True, "credit": 9999, "code": "ADMIN123"})
            st.rerun()
            
        df = pd.read_csv(DB_CODES)
        match = df[(df['code'] == in_c.strip()) & (df['status'] == 'Active')]
        if not match.empty:
            st.session_state.update({"auth": True, "credit": df.at[match.index[0], 'remaining'], "code": in_c.strip()})
            st.rerun()
        else: st.error("الكود غير صحيح")
    st.stop()

# --- لوحة التحكم (تظهر عند تفعيلها من الجانب) ---
if st.session_state.get('admin_active', False):
    st.markdown('<div class="admin-view-box">', unsafe_allow_html=True)
    st.subheader("🛠️ لوحة توليد الأكواد")
    c1, c2 = st.columns(2)
    with c1:
        new_c = st.text_input("الكود الجديد المراد إنشاؤه:")
        new_r = st.number_input("عدد المحاولات لهذا الكود:", 1, 1000, 66)
        if st.button("تفعيل وحفظ الكود"):
            df = pd.read_csv(DB_CODES)
            new_row = {"code": new_c, "credit": new_r, "remaining": new_r, "status": "Active", "activation_date": datetime.now().date(), "expiry_date": (datetime.now()+timedelta(days=30)).date()}
            pd.concat([df, pd.DataFrame([new_row])], ignore_index=True).to_csv(DB_CODES, index=False)
            st.success("تم الحفظ!")
    with c2:
        st.write("الأكواد الحالية:")
        st.dataframe(pd.read_csv(DB_CODES))
    st.markdown('</div>', unsafe_allow_html=True)

# --- الواجهة الرئيسية للمنصة ---
st.markdown(f'<div class="main-header"><h1>مرحباً بك دكتور Courage</h1><h2>الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF للمراجعة أو الترجمة", type=["pdf"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# 1. تبويب المستشار
with tabs[0]:
    st.subheader("🎓 مستشار بناء الخطط والبحوث")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    cp = st.chat_input("اسأل المستشار...")
    if cp and deduct_attempt(1):
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "أنت خبير أكاديمي."}] + st.session_state.chat_history + [{"role": "user", "content": cp}])
        st.session_state.chat_history.append({"role": "user", "content": cp})
        st.session_state.chat_history.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

# 2. الترجمة والمراجعة والمعاينة (الخوارزميات الكاملة)
if up:
    up.seek(0); doc_v = fitz.open(stream=up.read(), filetype="pdf"); p_count = len(doc_v)
    
    with tabs[1]:
        st.subheader("🌍 ترجمة الملف بالكامل")
        t_lang = st.selectbox("اللغة:", ["العربية", "English"])
        if st.button(f"بدء ترجمة {p_count} صفحة"):
            with st.spinner("🚀 جاري المعالجة..."):
                if deduct_attempt(p_count):
                    full_t = ""
                    for i in range(0, p_count, 10):
                        batch = "\n".join([doc_v[j].get_text() for j in range(i, min(i+10, p_count))])
                        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Translate to {t_lang}: {batch}"}])
                        full_t += res.choices[0].message.content + "\n\n"
                    st.session_state.translation_result = full_t
                    st.success("اكتملت الترجمة")
        
        if "translation_result" in st.session_state:
            st.download_button("📥 تحميل المترجم", data=create_word_file(st.session_state.translation_result), file_name="Translated.docx")

    with tabs[2]:
        st.subheader("🎓 مراجعة نقدية")
        if st.button("توليد تقرير المراجعة"):
            if deduct_attempt(p_count):
                full_rev = ""
                for i in range(0, p_count, 10):
                    batch = "\n".join([doc_v[j].get_text() for j in range(i, min(i+10, p_count))])
                    res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Academic review for: {batch}"}])
                    full_rev += res.choices[0].message.content + "\n"
                st.session_state.review_result = full_rev
        if "review_result" in st.session_state:
            st.markdown(st.session_state.review_result)

    with tabs[3]:
        p_num = st.number_input("عرض صفحة:", 1, p_count, 1)
        pix = doc_v[p_num-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy 2026</p>", unsafe_allow_html=True)
