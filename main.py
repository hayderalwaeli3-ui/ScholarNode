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

# --- [كود رقم سبعة] - بروتوكول الحماية المطلقة ---
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
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in p.runs:
        run.font.size = Pt(14)
        run.font.name = 'Arial'
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

# --- وظيفة شريط النسبة المئوية المتزامن (تعديل رقم 2) ---
def run_progress_synced(text="جاري المعالجة..."):
    placeholder = st.empty()
    for p in range(1, 96): # يصل لـ 95% وينتظر اكتمال العملية الفعلية
        time.sleep(0.01)
        placeholder.progress(p, text=f"{text} {p}%")
    return placeholder

# --- بروتوكول الحماية المطلقة وتنسيق الألوان الذكي (CSS) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.stDeployButton {display:none;}
:root { --text-color: inherit; }
.main-header { background: #1e3a8a; color: #ffffff !important; padding: 20px; text-align: center; border-radius: 15px; border: 4px solid #facc15; margin-bottom: 25px; }
.price-table { width: 100%; border-collapse: collapse; margin: 10px 0; background: transparent; }
.price-table th { background: #ef4444; color: white !important; padding: 12px; border: 1px solid #ddd; }
.price-table td { border: 1px solid #ddd; padding: 10px; text-align: center; color: inherit !important; font-weight: bold; }
.payment-box { background: #1e3a8a; color: white !important; padding: 18px; border-radius: 12px; border: 3px solid #facc15; font-size: 0.9rem; line-height: 1.6; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("### 🏦 معلومات الحساب والدعم")
    st.markdown(f"""
    <div class="payment-box">
        👤 <b>الاسم:</b> HAYDER Z. JASIM<br>
        💳 <b>ماستر كارد الرافدين:</b><br> 8369719342<br>
        📞 <b>رقم الهاتف (تفعيل):</b><br> 0 7 8 7 9 9 7 4 3 9 5
    </div>
    """, unsafe_allow_html=True) # تم تحديث الرقم (تعديل رقم 1)
    
    if "auth" in st.session_state:
        st.write(f"🎟️ **الكود المفعل:** `{st.session_state.code}`")
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear(); st.rerun()

    st.markdown("### 🏷️ جدول فئات الكروت")
    st.markdown("""<table class="price-table"><tr><th>الفئة (دينار)</th><th>محاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>20,000</td><td>133</td></tr><tr><td>50,000</td><td>333</td></tr><tr><td>100,000</td><td>666</td></tr></table>""", unsafe_allow_html=True)

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

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً بك في ScholarNode</h1><h2>الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF للمراجعة أو الترجمة", type=["pdf"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# 1. تبويب المستشار (تعديل رقم 4: إضافة تحميل ملف ثابت)
with tabs[0]:
    st.subheader("🎓 مستشار بناء الخطط والبحوث")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    if "last_advisor_doc" not in st.session_state: st.session_state.last_advisor_doc = None

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    
    c_prompt = st.chat_input("اطلب بناء خطة بحثية رصينة...")
    if c_prompt:
        if deduct_attempt(1):
            prog = run_progress_synced("جاري إعداد البحث الأكاديمي...")
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "أنت خبير أكاديمي محترف. قدم بحوثاً رصينة مع توثيق أكاديمي."}] + st.session_state.chat_history + [{"role": "user", "content": c_prompt}])
            response = res.choices[0].message.content
            st.session_state.chat_history.append({"role": "user", "content": c_prompt})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.session_state.last_advisor_doc = response
            prog.progress(100, text="✅ تمت العملية بنجاح!")
            time.sleep(0.5); prog.empty()
            st.rerun()

    if st.session_state.last_advisor_doc:
        st.download_button("📥 تحميل البحث الحالي (Word)", data=create_word_file(st.session_state.last_advisor_doc), file_name="Academic_Research.docx", key="advisor_dl_fixed")

# التبويبات الأخرى مع ضمان ثبات الملفات (تعديل رقم 3)
if up:
    up.seek(0); doc_v = fitz.open(stream=up.read(), filetype="pdf"); p_count = len(doc_v)
    
    with tabs[1]:
        st.subheader("🌍 ترجمة الملف بالكامل")
        t_lang = st.selectbox("اللغة المستهدفة:", ["العربية", "English"], key="t_lang")
        if st.button(f"بدء ترجمة {p_count} صفحة"):
            if deduct_attempt(p_count):
                prog = run_progress_synced("جاري الترجمة الأكاديمية...")
                all_text = "\n".join([p.get_text() for p in doc_v])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate this fully to {t_lang}:\n{all_text}"}])
                st.session_state.translation_result = res.choices[0].message.content
                prog.progress(100, text="✅ اكتملت الترجمة!")
                time.sleep(0.5); prog.empty()
        
        if "translation_result" in st.session_state:
            st.download_button("📥 تحميل الملف المترجم", data=create_word_file(st.session_state.translation_result), file_name="translated.docx", key="trans_dl_fixed")

    with tabs[2]:
        st.subheader("🎓 مراجعة نقدية أكاديمية")
        r_lang = st.selectbox("لغة التقرير:", ["العربية", "English"], key="r_lang")
        if st.button("توليد تقرير المراجعة"):
            if deduct_attempt(p_count):
                prog = run_progress_synced("جاري تحليل الملف نقدياً...")
                all_text = "\n".join([p.get_text() for p in doc_v])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Provide a human-like academic review in {r_lang}: {all_text}"}])
                st.session_state.review_result = res.choices[0].message.content
                prog.progress(100, text="✅ تم توليد المراجعة!")
                time.sleep(0.5); prog.empty()

        if "review_result" in st.session_state:
            st.markdown(st.session_state.review_result)
            st.download_button("📥 تحميل تقرير المراجعة", data=create_word_file(st.session_state.review_result), file_name="review.docx", key="rev_dl_fixed")

    with tabs[3]:
        p_num = st.number_input("الصفحة رقم:", 1, p_count, 1)
        f_prompt = st.text_input("اسأل المستشار عن محتوى هذه الصفحة:")
        if st.button("إرسال") and f_prompt:
            if deduct_attempt(1):
                prog = run_progress_synced("جاري استخراج الإجابة...")
                context = doc_v[p_num-1].get_text()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": f"Context: {context}"}, {"role": "user", "content": f_prompt}])
                st.info(f"**المستشار:** {res.choices[0].message.content}")
                prog.empty()
        pix = doc_v[p_num-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026 | كود رقم سبعة</p>", unsafe_allow_html=True)
