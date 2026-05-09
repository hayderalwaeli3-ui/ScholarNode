import streamlit as st
import pandas as pd
import os
import io
import uuid
import random
import string
from datetime import datetime
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from openai import OpenAI

# --- إعدادات النظام والمفاتيح (حماية مطلقة) ---
API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)
DB_CODES = "scholar_main_db.csv"

def init_db():
    if not os.path.exists(DB_CODES):
        pd.DataFrame(columns=["code", "credit", "remaining", "status"]).to_csv(DB_CODES, index=False)

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

# --- التنسيق البصري المتجاوب (Responsive Design) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #ffffff !important; }
    .main-header { 
        background: #1e3a8a; color: #ffffff !important; padding: 25px; 
        text-align: center; border-radius: 15px; border: 4px solid #facc15; margin-bottom: 20px; 
    }
    @media (max-width: 640px) {
        .main-header h1 { font-size: 22px !important; }
        .main-header h2 { font-size: 16px !important; }
        .stButton button { width: 100% !important; }
    }
    h1, h2, h3, p, span, label { color: #000000 !important; font-weight: bold !important; }
    .price-table { width: 100%; border-collapse: collapse; background: #ffffff; border: 2px solid #ef4444; margin-top: 10px; }
    .price-table th { background: #ef4444; color: white !important; padding: 8px; }
    .price-table td { border: 1px solid #ef4444; padding: 6px; text-align: center; color: #000000 !important; }
    .payment-box { background: #1e3a8a; color: white !important; padding: 15px; border-radius: 10px; border: 2px solid #facc15; }
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية (إدارة الكروت والأسعار) ---
with st.sidebar:
    if "auth" in st.session_state:
        st.write(f"🎫 الكود الحالي: `{st.session_state.code}`")
        if st.button("🔴 تسجيل الخروج"):
            st.session_state.clear()
            st.rerun()
    
    st.markdown('<div class="payment-box"><b>🏦 ماستر كارد الرافدين:</b><br>8369719342<br>👤 HAYDER Z. JASIM</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏷️ فئات الشحن")
    st.markdown("""<table class="price-table">
    <tr><th>الفئة (دينار)</th><th>المحاولات</th></tr>
    <tr><td>10,000</td><td>66</td></tr>
    <tr><td>20,000</td><td>133</td></tr>
    <tr><td>50,000</td><td>333</td></tr>
    <tr><td>100,000</td><td>666</td></tr>
    </table>""", unsafe_allow_html=True)

    st.write("---")
    adm = st.text_input("لوحة التحكم (Admin):", type="password")
    if adm == "HAYDER_2026":
        st.subheader("🛠️ توليد الكروت")
        cat = st.selectbox("اختر الفئة:", [10, 20, 30, 40, 50, 100])
        if st.button("توليد الكود الجديد"):
            new_c = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            att_map = {10: 66, 20: 133, 30: 200, 40: 266, 50: 333, 100: 666}
            attempts = att_map[cat]
            df = pd.read_csv(DB_CODES)
            new_entry = pd.DataFrame([{"code": new_c, "credit": attempts, "remaining": attempts, "status": "Active"}])
            pd.concat([df, new_entry]).to_csv(DB_CODES, index=False)
            st.success(f"تم التوليد: {new_c}")
            st.code(new_c)

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        in_c = st.text_input("أدخل كود التفعيل الخاص بك:", type="password")
        if st.button("دخول للمنصة", use_container_width=True):
            df = pd.read_csv(DB_CODES)
            match = df[df['code'] == in_c.strip()]
            if not match.empty:
                idx = match.index[0]
                st.session_state.update({"auth": True, "credit": df.at[idx, 'remaining'], "code": in_c.strip()})
                st.rerun()
            else: st.error("عذراً، الكود غير صحيح أو منتهي.")
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>ScholarNode Academy</h1><h2>الرصيد المتبقي: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF للبدء بالعمل", type=["pdf"])

tabs = st.tabs(["💬 المستشار الأكاديمي", "🌍 الترجمة", "🎓 المراجعة النقدية", "📄 المعاينة"])

# 1. تبويب المستشار (بناء الخطط)
with tabs[0]:
    st.subheader("🎓 مستشار بناء الخطط والبحوث")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                st.download_button("📥 تحميل كملف Word", data=create_word_file(msg["content"]), file_name="scholar_output.docx", key=str(uuid.uuid4()))

    prompt = st.chat_input("اطلب خطة بحثية مفصلة أو استشارة علمية...")
    if prompt:
        if deduct_attempt(1):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("assistant"):
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "أنت خبير أكاديمي برتبة بروفيسور، تقدم خطط بحثية مفصلة ورصينة."}] + st.session_state.chat_history
                )
                ans = res.choices[0].message.content
                st.markdown(ans)
                st.session_state.chat_history.append({"role": "assistant", "content": ans})
                st.rerun()
        else: st.error("رصيدك غير كافٍ، يرجى التعبئة.")

# 2. تبويب الترجمة
with tabs[1]:
    if up:
        t_lang = st.selectbox("ترجمة إلى:", ["العربية", "English"])
        if st.button("بدء الترجمة الكاملة"):
            up.seek(0)
            doc = fitz.open(stream=up.read(), filetype="pdf")
            if deduct_attempt(len(doc)):
                all_text = "\n".join([page.get_text() for page in doc])
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate to {t_lang}:\n{all_text}"}])
                txt = res.choices[0].message.content
                st.success("اكتملت الترجمة")
                st.download_button("📥 تحميل الترجمة (Word)", data=create_word_file(txt), file_name="translated.docx")
            else: st.error("الرصيد لا يكفي لعدد الصفحات")

# 3. تبويب المراجعة النقدية (بشخصية المراجع البشري)
with tabs[2]:
    if up:
        if st.button("توليد مراجعة علمية تفصيلية"):
            up.seek(0)
            doc = fitz.open(stream=up.read(), filetype="pdf")
            if deduct_attempt(len(doc)):
                all_text = "\n".join([page.get_text() for page in doc])
                rev_prompt = f"أنت مراجع أكاديمي بشري. حافظ على العناوين الأصلية للنص وقدم مراجعة نقدية رصينة تحت كل عنوان بأسلوبك الخاص. النص: {all_text}"
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": rev_prompt}])
                txt = res.choices[0].message.content
                st.write(txt)
                st.download_button("📥 تحميل المراجعة (Word)", data=create_word_file(txt), file_name="review.docx")

# 4. تبويب المعاينة (متوافق مع الموبايل)
with tabs[3]:
    if up:
        up.seek(0)
        doc = fitz.open(stream=up.read(), filetype="pdf")
        p_num = st.number_input("عرض صفحة:", 1, len(doc), 1)
        pix = doc[p_num-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)
        
        q = st.text_input("ناقش المستشار في هذه الصفحة:")
        if st.button("إرسال السؤال") and q:
            if deduct_attempt(1):
                context = doc[p_num-1].get_text()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": f"Context: {context}"}, {"role": "user", "content": q}])
                st.info(res.choices[0].message.content)

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
