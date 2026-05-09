import streamlit as st
import pandas as pd
import os
import io
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from openai import OpenAI
import time

# --- [كود رقم 3] - إعدادات النظام (بروتوكول الحماية المطلقة الصارم) ---
API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)
DB_CODES = "scholar_main_db.csv"

# --- وظائف المعالجة الذكية ---
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
    progress_text = "جاري البحث والتحليل الأكاديمي... يرجى الانتظار"
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(95):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    return my_bar

# --- الحماية البرمجية وتنسيق الواجهة (CSS) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.stDeployButton {display:none;}
.main-header { background: #1e3a8a; color: #ffffff !important; padding: 20px; text-align: center; border-radius: 15px; border: 4px solid #facc15; margin-bottom: 25px; }
.payment-box { background: #1e3a8a; color: white !important; padding: 18px; border-radius: 12px; border: 3px solid #facc15; font-size: 0.95rem; line-height: 1.6; }
.price-table { width: 100%; border-collapse: collapse; margin: 10px 0; background: transparent; }
.price-table th { background: #ef4444; color: white !important; padding: 12px; border: 1px solid #ddd; }
.price-table td { border: 1px solid #ddd; padding: 10px; text-align: center; color: inherit !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية (Sidebar) ---
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

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# 1. المستشار الذكي (إخفاء الرفع + توثيق شيكاغو)
with tabs[0]:
    st.subheader("🎓 مستشار البحوث والمقالات الرصينة")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    
    c_prompt = st.chat_input("اطلب موضوع البحث العلمي هنا...")
    
    if c_prompt:
        cost = 10 if any(w in c_prompt for w in ["بحث", "دراسة", "مقالة"]) else 1
        if deduct_attempt(cost):
            m_bar = run_progress_sync()
            # نظام توثيق شيكاغو وتفصيل أكاديمي صارم
            sys_msg = """أنت بروفيسور أكاديمي متخصص. اكتب بحوثاً تفصيلية شاملة مع دمج الهوامش والمصادر الأجنبية الرصينة داخل الفقرات وفي النهاية.
            يجب أن يكون التوثيق بالكامل وفق نظام شيكاغو (Chicago Style). تجنب الاختصار والملخصات."""
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_msg}] + st.session_state.chat_history + [{"role": "user", "content": c_prompt}])
            answer = res.choices[0].message.content
            m_bar.progress(100, text="اكتملت الصياغة الأكاديمية!")
            st.markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.download_button("📥 تحميل البحث (Word)", data=create_word_file(answer), file_name="Academic_Research_Chicago.docx")
            time.sleep(1); m_bar.empty()
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

# رفع الملف للتبويبات الأخرى فقط
up = st.file_uploader("📂 ارفع ملف البحث للترجمة أو المراجعة العلمية (PDF, Word, Excel, PPT)", type=["pdf", "docx", "xlsx", "pptx"])

if up:
    with tabs[1]:
        st.subheader("🌍 ترجمة أكاديمية")
        t_lang = st.selectbox("لغة الترجمة:", ["العربية", "English"], key="t_lang")
        if st.button("بدء الترجمة"):
            if deduct_attempt(10):
                m_bar = run_progress_sync()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate strictly to {t_lang}."}])
                m_bar.progress(100, text="تمت الترجمة!")
                st.download_button("📥 تحميل الملف (Word)", data=create_word_file(res.choices[0].message.content), file_name="translated.docx")
                time.sleep(1); m_bar.empty()

    with tabs[2]:
        st.subheader("🎓 مراجعة علمية نقدية")
        r_lang = st.selectbox("لغة التقرير:", ["العربية", "English"], key="r_lang")
        if st.button("توليد التقرير"):
            if deduct_attempt(10):
                m_bar = run_progress_sync()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": f"Critical review in {r_lang}."}])
                m_bar.progress(100, text="اكتمل التقرير!")
                st.markdown(res.choices[0].message.content)
                st.download_button("📥 تحميل (Word)", data=create_word_file(res.choices[0].message.content), file_name="review.docx")
                time.sleep(1); m_bar.empty()

    with tabs[3]:
        st.subheader("📄 معاينة ومناقشة")
        q_p = st.text_input("اسأل حول محتوى الملف:")
        if st.button("إرسال"):
            if deduct_attempt(1):
                m_bar = run_progress_sync()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": q_p}])
                m_bar.progress(100, text="تم الرد!")
                st.info(res.choices[0].message.content)
                st.download_button("📥 تحميل الإجابة (Word)", data=create_word_file(res.choices[0].message.content), file_name="response.docx")
                time.sleep(1); m_bar.empty()

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
