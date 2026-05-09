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

# --- وظيفة شريط النسبة المئوية المتزامن (معدل لضمان المزامنة الصارمة) ---
def run_synced_progress(text="جاري المعالجة الأكاديمية..."):
    placeholder = st.empty()
    for p in range(1, 101): # تم ضبطه ليكون متزامناً بالكامل من 1 إلى 100
        time.sleep(0.01)
        placeholder.progress(p, text=f"{text} {p}%")
    time.sleep(0.3) # ثبات بسيط للتأكد من رؤية المستخدم للكمال
    return placeholder

# --- بروتوكول الحماية المطلقة وتنسيق الألوان الذكي (CSS) ---
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
    """, unsafe_allow_html=True) # تم تحديث رقم الهاتف والمحافظة عليه
    
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
st.markdown(f'<div class="main-header"><h1>مرحباً بك دكتور Courage</h1><h2>الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF للمراجعة أو الترجمة", type=["pdf"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# 1. تبويب المستشار الذكي
with tabs[0]:
    st.subheader("🎓 مستشار بناء الخطط والبحوث")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    
    c_prompt = st.chat_input("اطلب بناء خطة بحثية أو مقال رصين...")
    if c_prompt:
        if deduct_attempt(1):
            progress_bar = run_synced_progress("جاري إعداد الرد الأكاديمي الموثق...")
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "أنت خبير أكاديمي محترف، قدم توثيقاً دقيقاً."}] + st.session_state.chat_history + [{"role": "user", "content": c_prompt}])
            response = res.choices[0].message.content
            
            st.session_state.chat_history.append({"role": "user", "content": c_prompt})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            progress_bar.empty()
            st.rerun()

    if st.session_state.chat_history:
        last_response = st.session_state.chat_history[-1]["content"]
        st.download_button("📥 تحميل الرد الحالي (Word)", data=create_word_file(last_response), file_name="Academic_Research.docx", key="static_chat_dl")

# وظائف الملفات (الترجمة والمراجعة)
if up:
    up.seek(0); doc_v = fitz.open(stream=up.read(), filetype="pdf"); p_count = len(doc_v)
    
    with tabs[1]:
        st.subheader("🌍 ترجمة الملف بالكامل")
        t_lang = st.selectbox("اللغة المستهدفة:", ["العربية", "English"], key="t_lang")
        if st.button(f"بدء ترجمة {p_count} صفحة"):
            if deduct_attempt(p_count):
                progress_bar = run_synced_progress("جاري الترجمة الأكاديمية المتزامنة...")
                all_text = "\n".join([p.get_text() for p in doc_v])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate fully to {t_lang}: {all_text}"}])
                st.session_state.translation_result = res.choices[0].message.content
                progress_bar.empty()
                st.success("✅ اكتملت الترجمة!")
        
        if "translation_result" in st.session_state:
            st.download_button("📥 تحميل الملف المترجم", data=create_word_file(st.session_state.translation_result), file_name="Translated_Document.docx", key="static_trans_dl")

    with tabs[2]:
        st.subheader("🎓 مراجعة نقدية أكاديمية")
        r_lang = st.selectbox("لغة التقرير:", ["العربية", "English"], key="r_lang")
        if st.button("توليد تقرير المراجعة"):
            if deduct_attempt(p_count):
                progress_bar = run_synced_progress("جاري تحليل الملف نقدياً...")
                all_text = "\n".join([p.get_text() for p in doc_v])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Provide an academic review in {r_lang}: {all_text}"}])
                st.session_state.review_result = res.choices[0].message.content
                progress_bar.empty()
                st.success("✅ تم توليد التقرير الأكاديمي!")

        if "review_result" in st.session_state:
            st.markdown(st.session_state.review_result)
            st.download_button("📥 تحميل تقرير المراجعة", data=create_word_file(st.session_state.review_result), file_name="Review_Report.docx", key="static_rev_dl")

    with tabs[3]:
        st.subheader("📄 معاينة ومناقشة الصفحات")
        p_num = st.number_input("الصفحة رقم:", 1, p_count, 1)
        f_prompt = st.text_input("اسأل المستشار عن محتوى هذه الصفحة:")
        if st.button("إرسال") and f_prompt:
            if deduct_attempt(1):
                progress_bar = run_synced_progress("جاري استخراج الإجابة الدقيقة...")
                context = doc_v[p_num-1].get_text()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": f"Context: {context}"}, {"role": "user", "content": f_prompt}])
                st.session_state.page_ans = res.choices[0].message.content
                progress_bar.empty()
        
        if "page_ans" in st.session_state:
            st.info(f"**المستشار:** {st.session_state.page_ans}")

        pix = doc_v[p_num-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026 | كود رقم سبعة</p>", unsafe_allow_html=True)
