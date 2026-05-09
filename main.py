import streamlit as st
import pandas as pd
import os
import io
import math
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from openai import OpenAI
import time

# --- [العودة لكود رقم 2] - مع التعديلات السيادية (بروتوكول الحماية المطلقة) ---
API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)
DB_CODES = "scholar_main_db.csv"

# --- وظائف السياسة المادية والمعالجة ---
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

def deduct_attempt(amount):
    if not os.path.exists(DB_CODES): return False
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

def run_progress_sync():
    # إصلاح الشريط لضمان عدم بقائه عالقاً وظهور النسبة المئوية
    placeholder = st.empty()
    progress_text = "جاري التحليل الأكاديمي... "
    for percent in range(1, 101):
        time.sleep(0.01)
        placeholder.progress(percent, text=f"{progress_text} {percent}%")
    time.sleep(0.5)
    placeholder.empty() # حذف الشريط فور الانتهاء

# --- تنسيق الواجهة (CSS كود رقم 2 الأصلي) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.main-header { background: #1e3a8a; color: #ffffff !important; padding: 20px; text-align: center; border-radius: 15px; border: 4px solid #facc15; margin-bottom: 25px; }
.payment-box { background: #1e3a8a; color: white !important; padding: 18px; border-radius: 12px; border: 3px solid #facc15; font-size: 0.95rem; }
.price-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
.price-table th { background: #ef4444; color: white !important; padding: 10px; border: 1px solid #ddd; }
.price-table td { border: 1px solid #ddd; padding: 8px; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية (كود رقم 2) ---
with st.sidebar:
    st.markdown("### 🏦 معلومات الحساب والدعم")
    st.markdown(f'<div class="payment-box">👤 <b>الاسم:</b> HAYDER Z. JASIM<br>💳 8369719342<br>📞 07879974395</div>', unsafe_allow_html=True)
    if "auth" in st.session_state:
        st.write(f"🎟️ **الكود:** `{st.session_state.code}`")
        if st.button("🔴 تسجيل الخروج"): st.session_state.clear(); st.rerun()
    st.markdown("### 🏷️ جدول فئات الكروت")
    st.markdown("""<table class="price-table"><tr><th>الفئة</th><th>محاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>20,000</td><td>133</td></tr><tr><td>50,000</td><td>333</td></tr><tr><td>100,000</td><td>666</td></tr></table>""", unsafe_allow_html=True)

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    in_c = st.text_input("أدخل كود التفعيل:", type="password")
    if st.button("دخول النظام"):
        if os.path.exists(DB_CODES):
            df = pd.read_csv(DB_CODES); match = df[(df['code'] == in_c.strip()) & (df['status'] == 'Active')]
            if not match.empty:
                st.session_state.update({"auth": True, "credit": df.at[match.index[0], 'remaining'], "code": in_c.strip()})
                st.rerun()
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً بك دكتور Courage</h1><h2>الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)

# تفعيل رفع ملفات الأوفيس والـ PDF في الأعلى
up = st.file_uploader("📂 ارفع ملف البحث (PDF, DOCX, XLSX, PPTX)", type=["pdf", "docx", "xlsx", "pptx"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# 1. المستشار الذكي (700 كلمة = 33 محاولة)
with tabs[0]:
    st.subheader("🎓 مستشار البحوث والمقالات الرصينة")
    c_prompt = st.chat_input("اطلب موضوع البحث هنا...")
    if c_prompt:
        sys_msg = "أنت بروفيسور أكاديمي. اكتب بحوثاً تفصيلية جداً بنظام شيكاغو (Chicago Style)."
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": c_prompt}])
        answer = res.choices[0].message.content
        cost = math.ceil((len(answer.split()) / 700) * 33) # السياسة المالية المطلوبة
        if deduct_attempt(cost):
            run_progress_sync()
            st.markdown(answer)
            st.download_button("📥 تحميل البحث (Word)", data=create_word_file(answer), file_name="Research.docx", key="dw_smart_final")
        else: st.error("رصيدك لا يكفي")

# 2. الترجمة (خيار اللغة + ثبات زر التحميل)
with tabs[1]:
    st.subheader("🌍 ترجمة أكاديمية احترافية")
    t_lang = st.selectbox("لغة الترجمة:", ["العربية", "English"], key="trans_lang")
    if st.button("بدء الترجمة"):
        if up and deduct_attempt(10):
            run_progress_sync()
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate to {t_lang}."}])
            trans_res = res.choices[0].message.content
            st.success("تمت الترجمة!")
            st.download_button("📥 تحميل المترجم (Word)", data=create_word_file(trans_res), file_name=f"translated_{t_lang}.docx", key="dw_trans_final")
        elif not up: st.warning("ارفع ملفاً أولاً")

# 3. المراجعة (بدء فوري + اختيار لغة)
with tabs[2]:
    st.subheader("🎓 مراجعة نقدية علمية")
    r_lang = st.selectbox("لغة التقرير:", ["العربية", "English"], key="rev_lang")
    if st.button("توليد تقرير المراجعة"):
        if up and deduct_attempt(10):
            run_progress_sync()
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": f"Review in {r_lang}."}])
            rev_res = res.choices[0].message.content
            st.markdown(rev_res)
            st.download_button("📥 تحميل المراجعة (Word)", data=create_word_file(rev_res), file_name="Review.docx", key="dw_rev_final")
        elif not up: st.warning("ارفع ملفاً أولاً")

# 4. المعاينة (دعم PDF والأوفيس)
with tabs[3]:
    if up:
        if up.type == "application/pdf":
            up.seek(0); doc_v = fitz.open(stream=up.read(), filetype="pdf")
            p_idx = st.number_input("الصفحة:", 1, len(doc_v), 1)
            pix = doc_v[p_idx-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)
        else:
            st.info(f"تم رفع الملف {up.name} بنجاح. المعاينة الصورية للـ PDF فقط.")
    else: st.info("يرجى رفع ملف للمعاينة.")

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
