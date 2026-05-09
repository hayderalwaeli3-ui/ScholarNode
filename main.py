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

# --- [كود رقم 5] - الإعدادات السيادية المستندة للأصل (بروتوكول الحماية المطلقة) ---
API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)
DB_CODES = "scholar_main_db.csv"

# --- وظائف النظام المستقرة ---
def create_word_file(text):
    doc = Document()
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in p.runs:
        run.font.size = Pt(13)
        run.font.name = 'Arial'
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
    progress_text = "جاري التحليل والمعالجة الأكاديمية... يرجى الانتظار"
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(95):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    return my_bar

# --- تنسيق الواجهة (CSS) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.stDeployButton {display:none;}
.main-header { background: #1e3a8a; color: #ffffff !important; padding: 20px; text-align: center; border-radius: 15px; border: 4px solid #facc15; margin-bottom: 25px; }
.payment-box { background: #1e3a8a; color: white !important; padding: 18px; border-radius: 12px; border: 3px solid #facc15; font-size: 0.95rem; line-height: 1.6; }
.price-table { width: 100%; border-collapse: collapse; margin: 10px 0; background: transparent; }
.price-table th { background: #ef4444; color: white !important; padding: 12px; border: 1px solid #ddd; }
.price-table td { border: 1px solid #ddd; padding: 10px; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية (HAYDER Z. JASIM) ---
with st.sidebar:
    st.markdown("### 🏦 معلومات الحساب والدعم")
    st.markdown(f'<div class="payment-box">👤 <b>الاسم:</b> HAYDER Z. JASIM<br>💳 <b>ماستر كارد الرافدين:</b><br> 8369719342<br>📞 <b>الدعم والتفعيل:</b> 07879974395</div>', unsafe_allow_html=True)
    if "auth" in st.session_state:
        st.write(f"🎟️ **الكود:** `{st.session_state.code}`")
        if st.button("🔴 تسجيل الخروج"): st.session_state.clear(); st.rerun()
    st.markdown("### 🏷️ جدول فئات الكروت")
    st.markdown("""<table class="price-table"><tr><th>الفئة (دينار)</th><th>محاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>20,000</td><td>133</td></tr><tr><td>40,000</td><td>266</td></tr><tr><td>50,000</td><td>333</td></tr><tr><td>100,000</td><td>666</td></tr></table>""", unsafe_allow_html=True)

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        in_c = st.text_input("أدخل كود التفعيل:", type="password")
        if st.button("دخول النظام"):
            if os.path.exists(DB_CODES):
                df = pd.read_csv(DB_CODES); match = df[(df['code'] == in_c.strip()) & (df['status'] == 'Active')]
                if not match.empty:
                    st.session_state.update({"auth": True, "credit": df.at[match.index[0], 'remaining'], "code": in_c.strip()})
                    st.rerun()
                else: st.error("الكود غير صحيح")
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً بك دكتور Courage</h1><h2>الرصيد المتوفر: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)

# حقل الرفع السيادي في الأعلى
up = st.file_uploader("📂 ارفع ملف البحث (PDF, DOCX, XLSX, PPTX)", type=["pdf", "docx", "xlsx", "pptx"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# 1. المستشار الذكي (بدون رفع ملف + نظام شيكاغو + السياسة المالية)
with tabs[0]:
    st.subheader("🎓 مستشار البحوث والمقالات الرصينة")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    c_prompt = st.chat_input("اكتب موضوع البحث العلمي التفصيلي هنا...")
    
    if c_prompt:
        m_bar = run_progress_sync()
        sys_msg = "أنت بروفيسور خبير. اكتب بحوثاً تفصيلية طويلة مع دمج المصادر الرصينة بنظام شيكاغو (Chicago Style). تجنب الملخصات."
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_msg}] + st.session_state.chat_history + [{"role": "user", "content": c_prompt}])
        answer = res.choices[0].message.content
        
        # السياسة المالية: 700 كلمة = 33 محاولة
        word_count = len(answer.split())
        cost = math.ceil((word_count / 700) * 33)
        if cost < 1: cost = 1
        
        if deduct_attempt(cost):
            m_bar.progress(100, text=f"تم التوليد! الاستهلاك: {cost} محاولة لـ {word_count} كلمة")
            st.markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.download_button("📥 تحميل البحث (Word)", data=create_word_file(answer), file_name="Academic_Research.docx")
            time.sleep(1); m_bar.empty()
        else:
            st.error("رصيدك غير كافٍ")
            m_bar.empty()
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

# منطق المعاينة والتبويبات المرتبطة بالملف
if up:
    # وظيفة المعاينة البصرية (مستوحاة من كود 1)
    if up.type == "application/pdf":
        up.seek(0)
        doc_v = fitz.open(stream=up.read(), filetype="pdf")
        p_count = len(doc_v)
    else:
        p_count = 1 # صيغ أخرى

    with tabs[1]:
        st.subheader("🌍 ترجمة أكاديمية")
        if st.button("بدء الترجمة"):
            if deduct_attempt(10):
                m_bar = run_progress_sync()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": "Translate this content."}])
                m_bar.progress(100, text="تمت الترجمة!")
                st.download_button("📥 تحميل (Word)", data=create_word_file(res.choices[0].message.content), file_name="translated.docx")
                time.sleep(1); m_bar.empty()

    with tabs[2]:
        st.subheader("🎓 مراجعة نقدية")
        if st.button("توليد تقرير المراجعة"):
            if deduct_attempt(10):
                m_bar = run_progress_sync()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "Critical review."}])
                m_bar.progress(100, text="اكتمل التقرير!")
                st.markdown(res.choices[0].message.content)
                st.download_button("📥 تحميل (Word)", data=create_word_file(res.choices[0].message.content), file_name="review.docx")
                time.sleep(1); m_bar.empty()

    with tabs[3]:
        st.subheader("📄 معاينة ومناقشة الملف")
        if up.type == "application/pdf":
            p_idx = st.number_input("عرض الصفحة:", 1, p_count, 1)
            q_p = st.text_input("اسأل حول هذه الصفحة:")
            if st.button("إرسال"):
                if deduct_attempt(1):
                    m_bar = run_progress_sync()
                    res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": q_p}])
                    st.info(res.choices[0].message.content)
                    m_bar.progress(100, text="تم الرد!")
                    time.sleep(1); m_bar.empty()
            # عرض الصفحة (الميزة المستعادة من كود 1)
            pix = doc_v[p_idx-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)
        else:
            st.info(f"تم رفع ملف بصيغة ({up.name})، المعاينة البصرية متاحة لملفات PDF فقط، ولكن يمكنك مناقشة المحتوى هنا.")
            q_gen = st.text_input("اسأل حول محتوى الملف:")
            if st.button("إرسال السؤال"):
                if deduct_attempt(1):
                    res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": q_gen}])
                    st.info(res.choices[0].message.content)

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
