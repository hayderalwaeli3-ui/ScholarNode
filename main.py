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
import time

# --- [كود رقم 1] - إعدادات النظام والمفاتيح ---
API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)
DB_CODES = "scholar_main_db.csv"

# --- وظائف السياسة المادية المحسنة ---
def calculate_costs(pages):
    attempts = pages
    iqd_cost = int((pages * 300) * 1.08)
    return attempts, iqd_cost

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

def deduct_attempt(amount):
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

# وظيفة محاكاة شريط التقدم لراحة المستخدم بصرياً
def show_progress():
    progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        progress_bar.progress(percent_complete + 1)
    return progress_bar

# --- بروتوكول الحماية المطلقة وتنسيق الألوان الذكي (CSS) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.stDeployButton {display:none;}
:root { --text-color: inherit; }
.main-header { background: #1e3a8a; color: #ffffff !important; padding: 20px; text-align: center; border-radius: 15px; border: 4px solid #facc15; margin-bottom: 25px; }
.payment-box { background: #1e3a8a; color: white !important; padding: 18px; border-radius: 12px; border: 3px solid #facc15; font-size: 0.95rem; line-height: 1.6; }
.price-table { width: 100%; border-collapse: collapse; margin: 10px 0; background: transparent; }
.price-table th { background: #ef4444; color: white !important; padding: 12px; border: 1px solid #ddd; }
.price-table td { border: 1px solid #ddd; padding: 10px; text-align: center; color: inherit !important; font-weight: bold; }
.cost-alert { background: rgba(255, 251, 230, 0.1); border-right: 5px solid #facc15; padding: 15px; color: inherit; font-weight: bold; border-radius: 5px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("### 🏦 معلومات الحساب والدعم")
    st.markdown(f'<div class="payment-box">👤 <b>الاسم:</b> HAYDER Z. JASIM<br>💳 <b>ماستر كارد الرافدين:</b><br> 8369719342<br>📞 <b>الدعم والتفعيل:</b> 07715632230</div>', unsafe_allow_html=True)
    if "auth" in st.session_state:
        st.write(f"🎟️ **الكود المفعل:** `{st.session_state.code}`")
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear()
            st.rerun()
    st.markdown("### 🏷️ جدول فئات الكروت")
    st.markdown("""<table class="price-table"><tr><th>الفئة (دينار)</th><th>محاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>50,000</td><td>333</td></tr><tr><td>100,000</td><td>666</td></tr></table>""", unsafe_allow_html=True)

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        in_c = st.text_input("أدخل كود التفعيل للدخول:", type="password")
        if st.button("دخول", use_container_width=True):
            if os.path.exists(DB_CODES):
                df = pd.read_csv(DB_CODES)
                match = df[(df['code'] == in_c.strip()) & (df['status'] == 'Active')]
                if not match.empty:
                    idx = match.index[0]
                    st.session_state.update({"auth": True, "user": "باحث مشترك", "credit": df.at[idx, 'remaining'], "code": in_c.strip()})
                    st.rerun()
                else: st.error("الكود غير صحيح")
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً بك دكتور {st.session_state.user}</h1><h2>الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF للمراجعة أو الترجمة", type=["pdf"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# 1. المستشار الذكي
with tabs[0]:
    st.subheader("🎓 مستشار بناء الخطط والبحوث الأكاديمية")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    c_prompt = st.chat_input("اطلب بناء خطة بحثية...")
    if c_prompt:
        is_research = any(word in c_prompt for word in ["بحث", "دراسة", "أطروحة"])
        cost_att = 10 if is_research else 1
        _, iqd_v = calculate_costs(cost_att)
        st.warning(f"⚠️ التكلفة: {cost_att} محاولة ({iqd_v} دينار).")
        if st.button("تأكيد وخصم"):
            if deduct_attempt(cost_att):
                p_bar = show_progress()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "خبير أكاديمي رصين."}] + st.session_state.chat_history + [{"role": "user", "content": c_prompt}])
                st.markdown(res.choices[0].message.content)
                st.session_state.chat_history.append({"role": "user", "content": c_prompt})
                st.session_state.chat_history.append({"role": "assistant", "content": res.choices[0].message.content})
                p_bar.empty()

if up:
    up.seek(0)
    doc_v = fitz.open(stream=up.read(), filetype="pdf")
    p_count = len(doc_v)
    att_req, iqd_req = calculate_costs(p_count)

    with tabs[1]:
        st.subheader("🌍 ترجمة أكاديمية كاملة")
        st.markdown(f'<div class="cost-alert">💰 التكلفة: {att_req} محاولة | {iqd_req} دينار</div>', unsafe_allow_html=True)
        if st.button("تأكيد الترجمة"):
            if deduct_attempt(att_req):
                p_bar = show_progress()
                all_text = "\n".join([p.get_text() for p in doc_v])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate to Arabic:\n{all_text}"}])
                st.download_button("📥 تحميل الترجمة", data=create_word_file(res.choices[0].message.content), file_name="trans.docx")
                p_bar.empty()

    with tabs[2]:
        st.subheader("🎓 مراجعة نقدية (جاهزة للنشر)")
        st.markdown(f'<div class="cost-alert">💰 التكلفة: {att_req} محاولة | {iqd_req} دينار</div>', unsafe_allow_html=True)
        if st.button("توليد التقرير"):
            if deduct_attempt(att_req):
                p_bar = show_progress()
                all_text = "\n".join([p.get_text() for p in doc_v])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Academic review for: {all_text}"}])
                st.download_button("📥 تحميل التقرير", data=create_word_file(res.choices[0].message.content), file_name="review.docx")
                p_bar.empty()

    with tabs[3]:
        st.subheader("📄 معاينة ومناقشة الملف")
        p_idx = st.number_input("الصفحة:", 1, p_count, 1)
        q_p = st.text_input("اسأل عن الصفحة:")
        if st.button("إرسال السؤال"):
            if deduct_attempt(1):
                p_bar = show_progress()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": f"Context: {doc_v[p_idx-1].get_text()}"}, {"role": "user", "content": q_p}])
                st.info(res.choices[0].message.content)
                p_bar.empty()
        pix = doc_v[p_idx-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)

st.markdown("<p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
