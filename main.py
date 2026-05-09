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

# --- [كود رقم 11] - بروتوكول الحماية المطلقة (نسخة المعالجة الفورية المحدثة بالإدارة) ---
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
.admin-area { background: #f0f4f8; border: 2px solid #1e3a8a; padding: 15px; border-radius: 10px; margin-top: 10px; color: #1e3a8a; }
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
        st.write(f"🎟️ **الكود المفعل:** `{st.session_state.code}`")
        
        # --- [إضافة خيار الإدارة] ---
        st.markdown("---")
        st.markdown("### ⚙️ الإدارة")
        # ملاحظة: يمكنك تغيير ADMIN123 إلى كودك الخاص للدخول
        if st.session_state.code == "HAYDER_2026":
            if st.button("🛠️ لوحة التحكم في الكروت"):
                st.session_state.admin_view = not st.session_state.get('admin_view', False)
        
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear(); st.rerun()

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

# --- قسم لوحة الإدارة (يظهر فقط عند الضغط على زر الإدارة) ---
if st.session_state.get('admin_view', False):
    st.markdown('<div class="admin-area"><h3>🛠️ لوحة تحكم الإدارة الأكاديمية</h3>', unsafe_allow_html=True)
    admin_tab1, admin_tab2 = st.tabs(["🎫 إضافة كود جديد", "📋 كشوفات الأكواد"])
    with admin_tab1:
        c_new = st.text_input("الكود الجديد:")
        c_credit = st.number_input("الرصيد (محاولات):", min_value=1, value=66)
        if st.button("تفعيل وحفظ الكود"):
            df = pd.read_csv(DB_CODES)
            new_data = pd.DataFrame([{"code": c_new, "credit": c_credit, "remaining": c_credit, "status": "Active", "activation_date": datetime.now(), "expiry_date": (datetime.now() + timedelta(days=30))}])
            pd.concat([df, new_data], ignore_index=True).to_csv(DB_CODES, index=False)
            st.success("تم الحفظ بنجاح")
    with admin_tab2:
        st.dataframe(pd.read_csv(DB_CODES))
    st.markdown('</div>', unsafe_allow_html=True)

# --- الواجهة الرئيسية للمنصة ---
st.markdown(f'<div class="main-header"><h1>مرحباً دكتور Courage</h1><h2>الرصيد المتاح: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
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
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "أنت خبير أكاديمي محترف."}] + st.session_state.chat_history + [{"role": "user", "content": c_prompt}])
            response = res.choices[0].message.content
            st.session_state.chat_history.append({"role": "user", "content": c_prompt})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

# 2. الترجمة والمراجعة والمعاينة (بنفس الخوارزميات الاقتصادية)
if up:
    up.seek(0); doc_v = fitz.open(stream=up.read(), filetype="pdf"); p_count = len(doc_v)
    
    with tabs[1]:
        st.subheader("🌍 ترجمة الملف بالكامل")
        t_lang = st.selectbox("اللغة المستهدفة للترجمة:", ["العربية", "English"], key="t_lang")
        if st.button(f"بدء ترجمة {p_count} صفحة"):
            with st.spinner("🚀 جاري تحضير المحرك وبدء المعالجة..."):
                if deduct_attempt(p_count):
                    full_translation = ""
                    prog_placeholder = st.empty()
                    for i in range(0, p_count, 10):
                        batch_text = "\n".join([doc_v[j].get_text() for j in range(i, min(i+10, p_count))])
                        if batch_text.strip():
                            res = client.chat.completions.create(
                                model="gpt-4o-mini", 
                                messages=[{"role": "user", "content": f"Translate to {t_lang}: {batch_text}"}]
                            )
                            full_translation += res.choices[0].message.content + "\n\n"
                        percent = int((min(i + 10, p_count) / p_count) * 100)
                        prog_placeholder.progress(percent, text=f"تمت ترجمة {min(i+10, p_count)} صفحة")
                    st.session_state.translation_result = full_translation
                    prog_placeholder.success("✅ تمت الترجمة بنجاح!")
                else:
                    st.error("عذراً، رصيدك لا يكفي.")
        
        if "translation_result" in st.session_state:
            st.download_button("📥 تحميل الملف المترجم", data=create_word_file(st.session_state.translation_result), file_name="Translated_Book.docx")

    with tabs[2]:
        st.subheader("🎓 مراجعة نقدية أكاديمية")
        review_lang = st.selectbox("اختر لغة النقد الأكاديمي:", ["العربية", "English"], key="rev_lang")
        if st.button("توليد تقرير المراجعة الشامل"):
            with st.spinner("🔍 جاري تحليل النص أكاديمياً..."):
                if deduct_attempt(p_count):
                    prog_placeholder = st.empty()
                    full_review = ""
                    for i in range(0, p_count, 10):
                        chunk = "\n".join([doc_v[j].get_text() for j in range(i, min(i+10, p_count))])
                        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Provide an academic review in {review_lang} for: {chunk}"}])
                        full_review += res.choices[0].message.content + "\n"
                        percent = int(((i + 10) / p_count) * 100)
                        prog_placeholder.progress(min(percent, 100), text=f"جاري التحليل النقدي...")
                    st.session_state.review_result = full_review
                    prog_placeholder.empty()
        
        if "review_result" in st.session_state:
            st.markdown(st.session_state.review_result)
            st.download_button("📥 تحميل تقرير المراجعة", data=create_word_file(st.session_state.review_result), file_name="Academic_Review.docx")

    with tabs[3]:
        st.subheader("📄 معاينة ومناقشة الملف")
        p_num = st.number_input("عرض الصفحة رقم:", 1, p_count, 1)
        st.markdown("---")
        user_query = st.text_input("💬 اسأل المستشار عن محتوى هذه الصفحة:")
        if st.button("إرسال السؤال"):
            if user_query:
                with st.spinner("⌛ جاري استخراج الإجابة..."):
                    if deduct_attempt(1):
                        page_content = doc_v[p_num-1].get_text()
                        res = client.chat.completions.create(
                            model="gpt-4o", 
                            messages=[
                                {"role": "system", "content": "أنت مساعد أكاديمي خبير. أجب بناءً على النص المرفق فقط."},
                                {"role": "user", "content": f"النص: {page_content}\n\nالسؤال: {user_query}"}
                            ]
                        )
                        st.info(f"**إجابة المستشار:**\n\n{res.choices[0].message.content}")
        
        st.markdown("---")
        pix = doc_v[p_num-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy 2026</p>", unsafe_allow_html=True)
