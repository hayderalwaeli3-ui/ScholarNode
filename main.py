import streamlit as st
import pandas as pd
import os
import io
import random
import string
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from openai import OpenAI
import time

# --- [كود رقم 1] - إعدادات النظام والمفاتيح (بروتوكول الحماية المطلقة) ---
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

def run_progress_bar():
    progress_text = "جاري المعالجة الأكاديمية... يرجى الانتظار"
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(0.4)
    st.success("✅ اكتملت العملية بنجاح!")
    my_bar.empty()

# --- تنسيق الألوان الذكي والحماية المطلقة (CSS) ---
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
    st.markdown(f"""
    <div class="payment-box">
        👤 <b>الاسم:</b> HAYDER Z. JASIM<br>
        💳 <b>ماستر كارد الرافدين:</b><br> 8369719342<br>
        📞 <b>الدعم والتفعيل:</b> 07879974395
    </div>
    """, unsafe_allow_html=True)
    
    if "auth" in st.session_state:
        st.write(f"🎟️ **الكود:** `{st.session_state.code}`")
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear(); st.rerun()

    st.markdown("### 🏷️ جدول فئات الكروت")
    st.markdown("""<table class="price-table"><tr><th>الفئة (دينار)</th><th>محاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>20,000</td><td>133</td></tr><tr><td>30,000</td><td>200</td></tr><tr><td>40,000</td><td>266</td></tr><tr><td>50,000</td><td>333</td></tr><tr><td>100,000</td><td>666</td></tr></table>""", unsafe_allow_html=True)

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
                    idx = match.index[0]
                    st.session_state.update({"auth": True, "user": "باحث مشترك", "credit": df.at[idx, 'remaining'], "code": in_c.strip()})
                    st.rerun()
                else: st.error("الكود غير صحيح")
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً بك دكتور Courage</h1><h2>الرصيد المتوفر: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF للبدء", type=["pdf"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# 1. المستشار الذكي
with tabs[0]:
    st.subheader("🎓 مستشار البحوث والمقالات الرصينة")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    c_prompt = st.chat_input("اطلب موضوع البحث أو المقالة هنا...")
    if c_prompt:
        cost = 10 if any(w in c_prompt for w in ["بحث", "دراسة", "مقالة"]) else 1
        if st.button(f"تأكيد وخصم {cost} محاولة"):
            if deduct_attempt(cost):
                run_progress_bar()
                sys_msg = "أنت بروفيسور أكاديمي محترف. اكتب بحوثاً تفصيلية مع دمج مصادر أجنبية داخل الفقرات وفي النهاية باللغة العربية حصراً إلا إذا طلب المستخدم لغة أخرى."
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_msg}] + st.session_state.chat_history + [{"role": "user", "content": c_prompt}])
                answer = res.choices[0].message.content
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "user", "content": c_prompt})
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.download_button("📥 تحميل المخرج (Word)", data=create_word_file(answer), file_name="scholar_output.docx")

if up:
    up.seek(0); doc_v = fitz.open(stream=up.read(), filetype="pdf"); p_count = len(doc_v)
    att_req, iqd_req = calculate_costs(p_count)

    with tabs[1]:
        st.subheader("🌍 ترجمة أكاديمية احترافية")
        t_lang = st.selectbox("لغة الترجمة المستهدفة:", ["العربية", "English"], key="t_lang")
        st.info(f"💰 التكلفة: {att_req} محاولة")
        if st.button("بدء الترجمة"):
            if deduct_attempt(att_req):
                run_progress_bar()
                all_text = "\n".join([p.get_text() for p in doc_v])
                # إجبار النموذج على اللغة المختارة
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate the following text strictly into {t_lang}. Do not use any other language:\n\n{all_text}"}])
                st.download_button("📥 تحميل الملف المترجم (Word)", data=create_word_file(res.choices[0].message.content), file_name=f"translated_{t_lang}.docx")

    with tabs[2]:
        st.subheader("🎓 مراجعة نقدية جاهزة للنشر")
        r_lang = st.selectbox("لغة التقرير المطلوبة:", ["العربية", "English"], key="r_lang")
        st.info(f"💰 التكلفة: {att_req} محاولة")
        if st.button("توليد تقرير المراجعة"):
            if deduct_attempt(att_req):
                run_progress_bar()
                all_text = "\n".join([p.get_text() for p in doc_v])
                # تعديل جوهري لضمان الالتزام باللغة المختارة
                sys_rev = f"You are an academic reviewer. Write a critical, publisher-ready review. You MUST write the entire report in {r_lang} only. Maintain original headings."
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_rev}, {"role": "user", "content": all_text}])
                answer = res.choices[0].message.content
                st.markdown(answer)
                st.download_button("📥 تحميل تقرير المراجعة (Word)", data=create_word_file(answer), file_name=f"review_{r_lang}.docx")

    with tabs[3]:
        st.subheader("📄 معاينة ومناقشة الملف")
        p_idx = st.number_input("الصفحة:", 1, p_count, 1)
        q_p = st.text_input("اسأل عن هذه الصفحة:")
        if st.button("إرسال السؤال"):
            if deduct_attempt(1):
                run_progress_bar()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": f"Context: {doc_v[p_idx-1].get_text()}"}, {"role": "user", "content": q_p}])
                st.info(res.choices[0].message.content)
                st.download_button("📥 تحميل الإجابة (Word)", data=create_word_file(res.choices[0].message.content), file_name="response.docx")
        pix = doc_v[p_idx-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
