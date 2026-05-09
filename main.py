import streamlit as st
import pandas as pd
import os
import io
import math
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from openai import OpenAI
import time

# --- [كود رقم 6] - بروتوكول الحماية المطلقة والشاملة ---
API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)
DB_CODES = "scholar_main_db.csv"

# --- وظائف السياسة المادية والمعالجة الذكية ---
def create_word_file(text_content):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(13)
    p = doc.add_paragraph(text_content)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
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

def run_progress_with_percent():
    p_bar = st.progress(0, text="جاري المعالجة الأكاديمية... 0%")
    for p in range(1, 101):
        time.sleep(0.01)
        p_bar.progress(p, text=f"جاري المعالجة الأكاديمية... {p}%")
    return p_bar

# --- تنسيق الواجهة (CSS) ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.stDeployButton {display:none;}
.main-header { background: #1e3a8a; color: white !important; padding: 20px; text-align: center; border-radius: 15px; border: 4px solid #facc15; }
.payment-box { background: #1e3a8a; color: white; padding: 15px; border-radius: 10px; border: 2px solid #facc15; }
.price-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
.price-table th { background: #ef4444; color: white; padding: 10px; }
.price-table td { border: 1px solid #ddd; padding: 8px; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    st.markdown("### 🏦 الحساب والدعم")
    st.markdown(f'<div class="payment-box">👤 <b>الاسم:</b> HAYDER Z. JASIM<br>💳 <b>الماستر:</b> 8369719342<br>📞 <b>الدعم:</b> 07879974395</div>', unsafe_allow_html=True)
    if "auth" in st.session_state:
        st.write(f"🎟️ الكود: `{st.session_state.code}`")
        if st.button("🔴 خروج"): st.session_state.clear(); st.rerun()
    st.markdown("### 🏷️ جدول الكروت")
    st.markdown("""<table class="price-table"><tr><th>الفئة</th><th>محاولات</th></tr><tr><td>10k</td><td>66</td></tr><tr><td>20k</td><td>133</td></tr><tr><td>50k</td><td>333</td></tr><tr><td>100k</td><td>666</td></tr></table>""", unsafe_allow_html=True)

# --- بوابة الدخول ---
if "auth" not in st.session_state:
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    in_c = st.text_input("أدخل كود التفعيل:", type="password")
    if st.button("دخول النظام"):
        if os.path.exists(DB_CODES):
            df = pd.read_csv(DB_CODES); match = df[df['code'] == in_c.strip()]
            if not match.empty:
                st.session_state.update({"auth": True, "credit": df.at[match.index[0], 'remaining'], "code": in_c.strip()})
                st.rerun()
    st.stop()

# --- الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>مرحباً بك دكتور Courage</h1><h2>الرصيد: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)

# 1. دعم كافة ملفات المايكروسوفت أوفيس في الأعلى
up = st.file_uploader("📂 ارفع ملف البحث (PDF, DOCX, XLSX, PPTX)", type=["pdf", "docx", "xlsx", "pptx"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# 2. المستشار الذكي (السياسة المالية: 700 كلمة = 33 محاولة)
with tabs[0]:
    st.subheader("🎓 مستشار البحوث الرصينة")
    c_p = st.chat_input("اطلب موضوع البحث التفصيلي هنا...")
    if c_p:
        sys_msg = "أنت بروفيسور خبير. اكتب بحثاً تفصيلياً طويلاً جداً مع توثيق شيكاغو (Chicago Style). اسهب في التفاصيل والمصادر."
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": c_p}])
        ans = res.choices[0].message.content
        
        # تطبيق السياسة المالية (700 كلمة = 33 محاولة)
        word_count = len(ans.split())
        cost = math.ceil((word_count / 700) * 33)
        if cost < 1: cost = 1
        
        if deduct_attempt(cost):
            run_progress_with_percent()
            st.markdown(ans)
            st.download_button("📥 تحميل المخرج (Word)", data=create_word_file(ans), file_name="Research_Output.docx")
        else: st.error("عذراً، رصيدك لا يكفي لتوليد هذا البحث.")

# 3. الترجمة الأكاديمية (مع قائمة اللغة)
with tabs[1]:
    st.subheader("🌍 الترجمة الأكاديمية")
    t_lang = st.selectbox("ترجم هذا الملف إلى:", ["العربية", "English"], key="t_lang_box")
    if st.button("بدء الترجمة"):
        if up and deduct_attempt(10):
            run_progress_with_percent()
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Translate strictly to {t_lang}."}])
            translated = res.choices[0].message.content
            st.download_button("📥 تحميل المترجم (Word)", data=create_word_file(translated), file_name=f"Translated_{t_lang}.docx")
        elif not up: st.warning("يرجى رفع ملف أولاً")

# 4. المراجعة العلمية (مع قائمة اللغة)
with tabs[2]:
    st.subheader("🎓 مراجعة نقدية علمية")
    r_lang = st.selectbox("لغة التقرير:", ["العربية", "English"], key="r_lang_box")
    if st.button("توليد التقرير"):
        if up and deduct_attempt(10):
            run_progress_with_percent()
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": f"Extensive academic review in {r_lang}."}])
            review = res.choices[0].message.content
            st.markdown(review)
            st.download_button("📥 تحميل المراجعة (Word)", data=create_word_file(review), file_name="Academic_Review.docx")
        elif not up: st.warning("يرجى رفع ملف أولاً")

# 5. معاينة الملف (دعم PDF + ملفات Office)
with tabs[3]:
    if up:
        st.write(f"📄 **اسم الملف:** {up.name}")
        if up.type == "application/pdf":
            up.seek(0); doc_v = fitz.open(stream=up.read(), filetype="pdf")
            p_idx = st.number_input("الصفحة:", 1, len(doc_v), 1)
            pix = doc_v[p_idx-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)
        elif up.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(up)
            text = "\n".join([p.text for p in doc.paragraphs[:20]]) # معاينة أول 20 فقرة
            st.text_area("معاينة نصية لملف الوورد:", text, height=300)
        elif up.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(up)
            st.dataframe(df.head(20)) # معاينة أول 20 سطر
        else:
            st.success("تم رفع الملف بنجاح وهو جاهز للمعالجة الأكاديمية.")
    else: st.info("يرجى رفع ملف (PDF أو Office) للمعاينة.")

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
