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

# --- إعدادات النظام والمفاتيح ---
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

# --- وظيفة شريط النسبة المئوية للانجاز (تعديل رقم 3) ---
def run_progress_with_percent(text="جاري المعالجة..."):
    placeholder = st.empty()
    for p in range(1, 101):
        time.sleep(0.01)
        placeholder.progress(p, text=f"{text} {p}%")
    time.sleep(0.5)
    placeholder.empty()

# --- بروتوكول الحماية المطلقة وتنسيق الألوان الذكي (CSS) ---
st.set_page_config(
    page_title="ScholarNode Academy", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* إخفاء العناصر البرمجية لضمان الحماية المطلقة */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}

/* تنسيق النصوص لتتبع ثيم الجهاز تلقائياً لضمان الوضوح */
:root { --text-color: inherit; }

.main-header { 
    background: #1e3a8a; 
    color: #ffffff !important; 
    padding: 20px; 
    text-align: center; 
    border-radius: 15px; 
    border: 4px solid #facc15; 
    margin-bottom: 25px; 
}

.price-table { width: 100%; border-collapse: collapse; margin: 10px 0; background: transparent; }
.price-table th { background: #ef4444; color: white !important; padding: 12px; border: 1px solid #ddd; }
.price-table td { border: 1px solid #ddd; padding: 10px; text-align: center; color: inherit !important; font-weight: bold; }

.payment-box { 
    background: #1e3a8a; 
    color: white !important; 
    padding: 18px; 
    border-radius: 12px; 
    border: 3px solid #facc15; 
    font-size: 0.9rem;
    line-height: 1.6;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("### 🏦 معلومات الحساب والدعم")
    st.markdown(f"""
    <div class="payment-box">
        👤 <b>الاسم:</b> HAYDER Z. JASIM<br>
        💳 <b>ماستر كارد الرافدين:</b><br> 8369719342<br>
        📞 <b>رقم الهاتف (تفعيل):</b><br> 07879973495
    </div>
    """, unsafe_allow_html=True) # تم تعديل الرقم (تعديل رقم 1)
    
    if "auth" in st.session_state:
        st.write(f"🎟️ **الكود المفعل:** `{st.session_state.code}`")
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear()
            st.rerun()

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

    st.write("---")
    adm = st.text_input("لوحة التحكم (Admin):", type="password")
    if adm == "HAYDER_2026":
        cat = st.selectbox("اختر فئة الكود:", [10, 20, 30, 40, 50, 100])
        if st.button("توليد كود جديد"):
            new_c = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            attempts = {10: 66, 20: 133, 30: 200, 40: 266, 50: 333, 100: 666}[cat]
            df = pd.read_csv(DB_CODES)
            new_entry = pd.DataFrame([{"code": new_c, "credit": attempts, "remaining": attempts, "status": "Active"}])
            pd.concat([df, new_entry]).to_csv(DB_CODES, index=False)
            st.success(f"تم توليد الكود: {new_c}")

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        in_c = st.text_input("أدخل كود التفعيل للدخول:", type="password")
        if st.button("دخول", use_container_width=True):
            df = pd.read_csv(DB_CODES)
            match = df[(df['code'] == in_c.strip()) & (df['status'] == 'Active')]
            if not match.empty:
                st.session_state.update({"auth": True, "user": "باحث مشترك", "credit": df.at[match.index[0], 'remaining'], "code": in_c.strip()})
                st.rerun()
            else: st.error("الكود غير صحيح")
    st.stop()

# --- الواجهة الرئيسية بعد الدخول ---
st.markdown(f'<div class="main-header"><h1>مرحباً بك في ScholarNode</h1><h2>الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF للمراجعة أو الترجمة", type=["pdf"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# 1. تبويب المستشار
with tabs[0]:
    st.subheader("🎓 مستشار بناء الخطط والبحوث")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    c_prompt = st.chat_input("اطلب بناء خطة بحثية...")
    if c_prompt:
        if deduct_attempt(1):
            run_progress_with_percent("جاري إعداد الرد...") # إضافة الشريط
            with st.chat_message("user"): st.markdown(c_prompt)
            st.session_state.chat_history.append({"role": "user", "content": c_prompt})
            with st.chat_message("assistant"):
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "أنت خبير أكاديمي."}] + st.session_state.chat_history)
                response = res.choices[0].message.content
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.download_button("📥 تحميل المخرج (Word)", data=create_word_file(response), file_name="output.docx", key=f"dl_{uuid.uuid4()}")
        else: st.error("الرصيد غير كافٍ")

# وظائف التبويبات الأخرى
if up:
    up.seek(0)
    doc_v = fitz.open(stream=up.read(), filetype="pdf")
    st.session_state.total_pages = len(doc_v)
    
    with tabs[1]:
        st.subheader("🌍 ترجمة الملف بالكامل")
        t_lang = st.selectbox("اللغة المستهدفة:", ["العربية", "English"], key="t_lang")
        if st.button(f"بدء ترجمة {st.session_state.total_pages} صفحة"):
            if deduct_attempt(st.session_state.total_pages):
                run_progress_with_percent("جاري ترجمة كامل الملف...") # إضافة الشريط
                up.seek(0)
                all_text = "\n".join([p.get_text() for p in doc_v])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate this fully to {t_lang}:\n{all_text}"}])
                st.success("✅ تمت الترجمة بنجاح!")
                st.download_button("📥 تحميل الملف المترجم", data=create_word_file(res.choices[0].message.content), file_name="translated.docx")
            else: st.error("رصيدك لا يكفي لعدد الصفحات")

    with tabs[2]:
        st.subheader("🎓 مراجعة نقدية أكاديمية")
        r_lang = st.selectbox("لغة التقرير:", ["العربية", "English"], key="r_lang")
        if st.button("توليد تقرير المراجعة"):
            if deduct_attempt(st.session_state.total_pages):
                run_progress_with_percent("جاري تحليل الملف نقدياً...") # إضافة الشريط
                up.seek(0)
                all_text = "\n".join([p.get_text() for p in doc_v])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Provide a human-like academic review in {r_lang}: {all_text}"}])
                st.success("✅ تم توليد المراجعة!")
                st.download_button("📥 تحميل تقرير المراجعة", data=create_word_file(res.choices[0].message.content), file_name="review.docx")
            else: st.error("الرصيد غير كافٍ")

    with tabs[3]:
        st.subheader("📄 معاينة ومناقشة الصفحات")
        # تعديل رقم 2: رفع مربع الحوار للأعلى
        p_num = st.number_input("الصفحة رقم:", 1, len(doc_v), 1)
        f_prompt = st.text_input("اسأل المستشار عن محتوى هذه الصفحة:")
        if st.button("إرسال") and f_prompt:
            if deduct_attempt(1):
                run_progress_sync_simple = st.progress(0, text="جاري استخراج الإجابة...")
                for i in range(100):
                    time.sleep(0.005)
                    run_progress_sync_simple.progress(i + 1)
                context = doc_v[p_num-1].get_text()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": f"Context: {context}"}, {"role": "user", "content": f_prompt}])
                st.info(f"**المستشار:** {res.choices[0].message.content}")
                run_progress_sync_simple.empty()
            else: st.error("الرصيد غير كافٍ")
        
        # وضع الصورة في الأسفل بعد مربع الحوار
        pix = doc_v[p_num-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)
else:
    with tabs[1]: st.info("يرجى رفع ملف PDF لتفعيل خيار الترجمة.")
    with tabs[2]: st.info("يرجى رفع ملف PDF لتفعيل خيار المراجعة الأكاديمية.")
    with tabs[3]: st.info("يرجى رفع ملف PDF لتتمكن من معاينته ومناقشته.")

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
