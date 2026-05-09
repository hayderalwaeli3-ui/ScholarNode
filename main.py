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

# --- التنسيق البصري (CSS) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #ffffff !important; }
.main-header { background: #1e3a8a; color: #ffffff !important; padding: 30px; text-align: center; border-radius: 15px; border: 5px solid #facc15; margin-bottom: 25px; }
h1, h2, h3, p, span, label { color: #000000 !important; font-weight: bold !important; }
.price-table { width: 100%; border-collapse: collapse; background: #ffffff; border: 2px solid #ef4444; }
.price-table th { background: #ef4444; color: white !important; padding: 10px; }
.price-table td { border: 1px solid #ef4444; padding: 8px; text-align: center; color: #000000 !important; }
.payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 3px solid #facc15; }
.finance-info { background: #fffbe6; color: #856404; padding: 15px; border-radius: 8px; border-right: 5px solid #facc15; margin-bottom: 20px; }
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
            st.markdown(f'<div class="finance-info">📊 كلفة الملف: {total_iqd} دينار</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="payment-box"><b>🏦 ماستر كارد الرافدين:</b><br>8369719342<br>👤 HAYDER Z. JASIM</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏷️ جدول الكروت")
    st.markdown("""<table class="price-table"><tr><th>الفئة</th><th>محاولات</th></tr><tr><td>10,000</td><td>66</td></tr><tr><td>20,000</td><td>133</td></tr><tr><td>30,000</td><td>200</td></tr><tr><td>40,000</td><td>266</td></tr><tr><td>50,000</td><td>333</td></tr><tr><td>100,000</td><td>666</td></tr></table>""", unsafe_allow_html=True)

    st.write("---")
    adm = st.text_input("لوحة التحكم (Admin):", type="password")
    if adm == "HAYDER_2026":
        cat = st.selectbox("الفئة:", [10, 20, 30, 40, 50, 100])
        if st.button("توليد الكود"):
            new_c = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            attempts = {10: 66, 20: 133, 30: 200, 40: 266, 50: 333, 100: 666}[cat]
            df = pd.read_csv(DB_CODES)
            new_entry = pd.DataFrame([{"code": new_c, "credit": attempts, "remaining": attempts, "status": "Active", "activation_date": "None", "expiry_date": "None"}])
            pd.concat([df, new_entry]).to_csv(DB_CODES, index=False)
            st.success(f"الكود المولد: {new_c}")

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        in_c = st.text_input("كود التفعيل:", type="password")
        if st.button("دخول", use_container_width=True):
            df = pd.read_csv(DB_CODES)
            match = df[(df['code'] == in_c.strip()) & (df['status'] == 'Active')]
            if not match.empty:
                idx = match.index[0]
                st.session_state.update({"auth": True, "user": "باحث مشترك", "credit": df.at[idx, 'remaining'], "code": in_c.strip()})
                st.rerun()
            else: st.error("الكود غير صحيح")
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً {st.session_state.user}</h1><h2>الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF لغرض المراجعة أو الترجمة", type=["pdf"])

tabs = st.tabs(["💬 المستشار الأكاديمي", "🌍 الترجمة", "🎓 المراجعة النقدية", "📄 المعاينة"])

# --- تبويب المستشار الأكاديمي ---
with tabs[0]:
    st.subheader("🎓 مستشار بناء الخطط والبحوث الأكاديمية")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    c_prompt = st.chat_input("اطلب بناء خطة بحثية أو اسأل سؤالاً علمياً...", key="main_chat")
    if c_prompt:
        if deduct_attempt(1):
            with st.chat_message("user"):
                st.markdown(c_prompt)
            st.session_state.chat_history.append({"role": "user", "content": c_prompt})
            
            with st.chat_message("assistant"):
                res = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[{"role": "system", "content": "أنت خبير أكاديمي متخصص في كتابة الخطط والبحوث."}] + st.session_state.chat_history
                )
                response = res.choices[0].message.content
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.download_button("📥 تحميل المخرج كملف Word", data=create_word_file(response), file_name="academic_output.docx", key=str(uuid.uuid4()))
        else: st.error("رصيدك غير كافٍ")

# --- باقي التبويبات ---
if up:
    up.seek(0)
    doc_v = fitz.open(stream=up.read(), filetype="pdf")
    st.session_state.total_pages = len(doc_v)
    
    with tabs[1]: 
        st.subheader("🌍 الترجمة الأكاديمية الكاملة")
        t_lang = st.selectbox("اللغة:", ["العربية", "English"], key="trans_lang")
        if st.button(f"بدء معالجة {st.session_state.total_pages} صفحة", key="tr_btn"):
            if deduct_attempt(st.session_state.total_pages):
                up.seek(0)
                doc = fitz.open(stream=up.read(), filetype="pdf")
                all_text = "\n".join([p.get_text() for p in doc])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate this fully to {t_lang}:\n{all_text}"}])
                final_txt = res.choices[0].message.content
                st.success("✅ اكتملت الترجمة!")
                st.download_button("📥 تحميل ملف Word المترجم", data=create_word_file(final_txt), file_name="translated_document.docx")
            else: st.error("رصيدك غير كافٍ")

    with tabs[2]: 
        st.subheader("🎓 المراجعة العلمية بشخصية مراجع بشري")
        r_lang = st.selectbox("لغة تقرير المراجعة النهائية:", ["العربية", "English"], key="rev_lang")
        if st.button("توليد مراجعة أكاديمية متكاملة", key="rev_btn"):
            if deduct_attempt(st.session_state.total_pages):
                up.seek(0)
                doc = fitz.open(stream=up.read(), filetype="pdf")
                all_text = "\n".join([p.get_text() for p in doc])
                review_prompt = f"أنت مراجع أكاديمي بشري خبير. حافظ على العناوين الأصلية للنص التالي وقدم مراجعة نقدية تحت كل عنوان بأسلوبك الخاص باللغة {r_lang}. النص: {all_text}"
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": review_prompt}])
                final_txt = res.choices[0].message.content
                st.success("✅ اكتملت المراجعة!")
                st.download_button("📥 تحميل المراجعة العلمية (Word)", data=create_word_file(final_txt), file_name="academic_human_review.docx")
            else: st.error("رصيدك غير كافٍ")

    with tabs[3]:
        st.subheader("📄 معاينة ومناقشة الملف")
        col_view, col_chat = st.columns([1, 1])
        
        with col_view:
            up.seek(0)
            doc = fitz.open(stream=up.read(), filetype="pdf")
            p_num = st.number_input("عرض الصفحة رقم:", 1, len(doc), 1)
            pix = doc[p_num-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            st.image(Image.open(io.BytesIO(pix.tobytes())), caption=f"الصفحة {p_num}")
            
        with col_chat:
            st.write("💬 **اسأل المستشار عن محتوى هذا الملف:**")
            if "file_chat_history" not in st.session_state:
                st.session_state.file_chat_history = []
            
            for msg in st.session_state.file_chat_history:
                st.info(f"**{msg['role']}:** {msg['content']}")
            
            f_prompt = st.text_input("ماذا تريد أن تعرف عن هذا الملف؟", key="file_query_input")
            if st.button("إرسال الاستفسار") and f_prompt:
                if deduct_attempt(1):
                    up.seek(0)
                    doc = fitz.open(stream=up.read(), filetype="pdf")
                    context_text = doc[p_num-1].get_text()
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": f"أنت مراجع أكاديمي. أجب بناءً على هذا النص: {context_text}"}, {"role": "user", "content": f_prompt}]
                    )
                    ans = res.choices[0].message.content
                    st.session_state.file_chat_history.append({"role": "الباحث", "content": f_prompt})
                    st.session_state.file_chat_history.append({"role": "المستشار", "content": ans})
                    st.rerun()
                else: st.error("رصيدك غير كافٍ")

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
