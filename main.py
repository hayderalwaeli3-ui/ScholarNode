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

# --- وظائف الحماية والخصم ---
def get_device_id():
    return str(uuid.getnode())

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

# --- بروتوكول الحماية المطلقة وتنسيق الألوان الذكي (CSS) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
/* إخفاء القوائم والعناصر البرمجية لضمان الحماية المطلقة */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}

/* تنسيق النصوص لتتبع ثيم الجهاز (داكن/فاتح) تلقائياً */
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

/* جداول احترافية متجاوبة */
.price-table { width: 100%; border-collapse: collapse; margin: 10px 0; background: transparent; }
.price-table th { background: #ef4444; color: white !important; padding: 12px; border: 1px solid #ddd; }
.price-table td { border: 1px solid #ddd; padding: 10px; text-align: center; color: inherit !important; font-weight: bold; }

.payment-box { 
    background: #1e3a8a; 
    color: white !important; 
    padding: 18px; 
    border-radius: 12px; 
    border: 3px solid #facc15; 
    font-size: 0.95rem;
    line-height: 1.6;
}

.finance-info { 
    background: rgba(250, 204, 21, 0.15); 
    color: inherit !important; 
    padding: 15px; 
    border-radius: 8px; 
    border-right: 6px solid #facc15; 
    margin-bottom: 20px; 
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    if "auth" in st.session_state:
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear()
            st.rerun()
        if "total_pages" in st.session_state:
            total_iqd = int((st.session_state.total_pages * 300) * 1.08)
            st.markdown(f'<div class="finance-info">📊 كلفة الملف: {total_iqd:,} دينار</div>', unsafe_allow_html=True)
    
    # استعادة رقم الهاتف ومعلومات الدفع
    st.markdown("""
    <div class="payment-box">
        <b>🏦 معلومات الدفع والدعم:</b><br>
        💳 ماستر كارد الرافدين: 8369719342<br>
        👤 المستلم: HAYDER Z. JASIM<br>
        📞 للاستفسار وتفعيل الكروت: 07715632230
    </div>
    """, unsafe_allow_html=True)
    
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
        cat = st.selectbox("اختر فئة الكود للتوليد:", [10, 20, 30, 40, 50, 100])
        if st.button("توليد كود جديد"):
            new_c = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            attempts = {10: 66, 20: 133, 30: 200, 40: 266, 50: 333, 100: 666}[cat]
            df = pd.read_csv(DB_CODES)
            new_entry = pd.DataFrame([{"code": new_c, "credit": attempts, "remaining": attempts, "status": "Active", "activation_date": "None", "expiry_date": "None"}])
            pd.concat([df, new_entry]).to_csv(DB_CODES, index=False)
            st.success(f"تم توليد الكود بنجاح: {new_c}")

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        in_c = st.text_input("يرجى إدخال كود التفعيل للدخول:", type="password")
        if st.button("تسجيل الدخول", use_container_width=True):
            df = pd.read_csv(DB_CODES)
            match = df[(df['code'] == in_c.strip()) & (df['status'] == 'Active')]
            if not match.empty:
                idx = match.index[0]
                st.session_state.update({"auth": True, "user": "باحث مشترك", "credit": df.at[idx, 'remaining'], "code": in_c.strip()})
                st.rerun()
            else: st.error("عذراً، الكود غير صحيح أو منتهي الصلاحية")
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً {st.session_state.user}</h1><h2>الرصيد الحالي: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF للمراجعة أو الترجمة أو المناقشة", type=["pdf"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# --- تبويب المستشار الأكاديمي ---
with tabs[0]:
    st.subheader("🎓 مستشار بناء الخطط والبحوث الأكاديمية")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]): st.markdown(message["content"])

    c_prompt = st.chat_input("اطلب بناء خطة بحثية أو اسأل سؤالاً علمياً...")
    if c_prompt:
        if deduct_attempt(1):
            with st.chat_message("user"): st.markdown(c_prompt)
            st.session_state.chat_history.append({"role": "user", "content": c_prompt})
            with st.chat_message("assistant"):
                with st.spinner("جاري التفكير أكاديمياً..."):
                    res = client.chat.completions.create(
                        model="gpt-4o", 
                        messages=[{"role": "system", "content": "أنت خبير أكاديمي محترف."}] + st.session_state.chat_history
                    )
                    response = res.choices[0].message.content
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.download_button("📥 تحميل المخرج (Word)", data=create_word_file(response), file_name="scholar_output.docx")
        else: st.error("الرصيد غير كافٍ، يرجى تعبئة الكود.")

# --- المعالجة المتقدمة للملفات ---
if up:
    up.seek(0)
    doc_v = fitz.open(stream=up.read(), filetype="pdf")
    st.session_state.total_pages = len(doc_v)
    
    with tabs[1]: 
        st.subheader("🌍 الترجمة الأكاديمية الاحترافية")
        t_lang = st.selectbox("ترجمة إلى:", ["العربية", "English"], key="trans_lang")
        if st.button(f"بدء ترجمة {st.session_state.total_pages} صفحة"):
            if deduct_attempt(st.session_state.total_pages):
                up.seek(0)
                all_text = "\n".join([p.get_text() for p in doc_v])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate to {t_lang}:\n{all_text}"}])
                st.success("✅ اكتملت الترجمة!")
                st.download_button("📥 تحميل الملف المترجم (Word)", data=create_word_file(res.choices[0].message.content), file_name="translated.docx")
            else: st.error("الرصيد غير كافٍ لعدد الصفحات")

    with tabs[2]: 
        st.subheader("🎓 المراجعة العلمية النقدية")
        r_lang = st.selectbox("لغة التقرير العلمي:", ["العربية", "English"], key="rev_lang")
        if st.button("توليد مراجعة نقدية متكاملة"):
            if deduct_attempt(st.session_state.total_pages):
                up.seek(0)
                all_text = "\n".join([p.get_text() for p in doc_v])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Provide a critical academic review in {r_lang}: {all_text}"}])
                st.success("✅ اكتملت المراجعة!")
                st.download_button("📥 تحميل تقرير المراجعة (Word)", data=create_word_file(res.choices[0].message.content), file_name="academic_review.docx")
            else: st.error("الرصيد غير كافٍ")

    with tabs[3]:
        st.subheader("📄 معاينة ومناقشة محتوى الملف")
        p_num = st.number_input("عرض الصفحة:", 1, len(doc_v), 1)
        pix = doc_v[p_num-1].get_pixmap(matrix=fitz.Matrix(1.3, 1.3))
        st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)
        
        f_prompt = st.text_input("اسأل عن تفاصيل هذه الصفحة:")
        if st.button("إرسال الاستفسار") and f_prompt:
            if deduct_attempt(1):
                context = doc_v[p_num-1].get_text()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": f"Context: {context}"}, {"role": "user", "content": f_prompt}])
                st.info(f"**الرد:** {res.choices[0].message.content}")
            else: st.error("الرصيد غير كافٍ")

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026<br>Designed for Academic Excellence</p>", unsafe_allow_html=True)
