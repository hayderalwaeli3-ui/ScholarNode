import streamlit as st
import pandas as pd
import os
import time
import random
import string
import io
from datetime import datetime, timedelta
import requests

# محاولة استيراد مكتبات قراءة الملفات والمعاينة
try:
    import fitz  # PyMuPDF لقراءة ومعاينة الـ PDF
except ImportError:
    fitz = None

# محاولة استيراد محرك قوقل الاحتياطي
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# --- 1. إعدادات وتصميم الصفحة ---
st.set_page_config(
    page_title="ScholarNode Academy",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .welcome-header { background-color: #1e3d59 !important; border: 2px solid #ffc13b !important; padding: 20px; border-radius: 12px; margin-bottom: 25px; text-align: center; }
    .payment-card { border: 2px dashed #1e3d59; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات المحلية للكودات ---
DB_CODES = "scholarnode_database.csv"

def init_db():
    if not os.path.exists(DB_CODES):
        df = pd.DataFrame(columns=["code", "credit", "remaining", "plan_type", "activation_date", "expiry_date", "status"])
        df.to_csv(DB_CODES, index=False)

init_db()

# --- 3. جدول الباقات والأسعار ---
PLANS = {
    "1000": {"attempts": 10, "days": 4},
    "5000": {"attempts": 60, "days": 20},
    "10000": {"attempts": 130, "days": 30},
    "20000": {"attempts": 270, "days": 60},
    "30000": {"attempts": 410, "days": 90},
    "40000": {"attempts": 550, "days": 120},
    "50000": {"attempts": 690, "days": 150},
    "100000": {"attempts": 1500, "days": 300}
}
table_data = [{"الفئة (دينار)": f"{int(k):,}", "المحاولات المتاحة": f"{v['attempts']} محاولة"} for k, v in PLANS.items()]

# --- 4. إعداد بوابات الذكاء الاصطناعي (تم تحديثها لتكون Gemini أولاً) ---
openai_key = st.secrets.get("OPENAI_API_KEY", "").strip()
gemini_key = st.secrets.get("GEMINI_API_KEY", "").strip()

# تهيئة OpenAI
client = None
if openai_key:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
    except:
        client = None

# تهيئة Gemini
if gemini_key and genai:
    genai.configure(api_key=gemini_key)

# دالة التوليد (Gemini أولاً، ثم OpenAI)
def generate_academic_text(prompt):
    # محاولة Gemini (الأساسي)
    if gemini_key and genai:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            res = model.generate_content(prompt)
            return res.text
        except:
            pass # في حال فشل Gemini، نمر لـ OpenAI
    
    # محاولة OpenAI (الاحتياطي)
    if client and openai_key:
        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content
        except Exception as e:
            return f"عذراً، تعذر الوصول لكلا المحركين. الخطأ: {str(e)}"
    
    return "🚨 لا تتوفر اتصالات نشطة بمفاتيح الذكاء الاصطناعي حالياً."

# --- 5. دوال قراءة ومعالجة المستندات وحساب الصفحات ---
def extract_file_content(uploaded_file):
    if uploaded_file is None:
        return "", 0
    
    uploaded_file.seek(0)
    file_name = uploaded_file.name
    text = ""
    pages = 1
    
    try:
        if file_name.lower().endswith('.pdf'):
            if fitz:
                file_bytes = uploaded_file.read()
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                pages = len(doc)
                for page in doc:
                    text += page.get_text()
            else:
                text = "مكتبة المعالجة غائبة بالسيرفر حالياً."
        elif file_name.lower().endswith('.docx'):
            from docx import Document
            doc = Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs])
            pages = max(1, len(text) // 1500)
    except Exception as e:
        text = f"خطأ معالجة داخلي: {e}"
    
    uploaded_file.seek(0)
    return text, pages

# --- 6. نظام خصم الرصيد ---
def deduct_attempts(amount):
    if st.session_state.get('user_code') == "HAYDER_2026$$$":
        return True
    try:
        df = pd.read_csv(DB_CODES)
        idx = df.index[df['code'] == st.session_state.user_code].tolist()
        if idx:
            current_rem = df.at[idx[0], 'remaining']
            if current_rem >= amount:
                df.at[idx[0], 'remaining'] = int(current_rem - amount)
                df.to_csv(DB_CODES, index=False)
                st.session_state.user_credit = df.at[idx[0], 'remaining']
                return True
        return False
    except:
        return False

# --- 7. دوال مساعدة ---
def run_progress_bar():
    p_bar = st.progress(0)
    status = st.empty()
    for percent in range(0, 101, 25):
        time.sleep(0.04)
        p_bar.progress(percent)
        status.text(f"⏳ جاري معالجة البيانات الأكاديمية... {percent}%")
    status.empty()
    p_bar.empty()

def convert_word_provider(text, rtl=False):
    bio = io.BytesIO()
    try:
        from docx import Document
        doc = Document()
        p = doc.add_paragraph()
        p.add_run(text)
        doc.save(bio)
    except:
        bio.write(text.encode('utf-8'))
    bio.seek(0)
    return bio

# --- 8. الشاشات الرئيسية ---
if "authenticated" not in st.session_state:
    st.markdown('<div class="welcome-header"><h1 style="color:white; margin:0;">ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    col_main, col_info = st.columns([2, 1])
    
    with col_main:
        st.subheader("🔐 تسجيل الدخول الآمن")
        input_key = st.text_input("أدخل كود تفعيل الحساب الخاص بك:", type="password")
        if st.button("تفعيل الدخول للمنصة", use_container_width=True):
            cleaned_key = input_key.strip()
            if cleaned_key == "HAYDER_2026$$$":
                st.session_state.update({"authenticated": True, "user_code": "HAYDER_2026$$$", "user_credit": "الإدارة العليا", "is_admin": True, "expiry_info": "مفتوح للأبد"})
                st.rerun()
            elif cleaned_key:
                df = pd.read_csv(DB_CODES)
                record = df[df['code'] == cleaned_key]
                if not record.empty:
                    rem = int(record.iloc[0]['remaining'])
                    exp_str = record.iloc[0]['expiry_date']
                    if rem <= 0:
                        st.error("❌ نفدت جميع محاولات هذا الكود.")
                    else:
                        st.session_state.update({"authenticated": True, "user_code": cleaned_key, "user_credit": rem, "is_admin": False, "expiry_info": exp_str})
                        st.rerun()
                else:
                    st.error("❌ الكود غير مسجل بنظامنا.")
                    
    with col_info:
        st.markdown('<div class="payment-card"><b>💳 حسابات الدفع الرسمية:</b><br>• ماستر كارد: 8369719342<br>• باسم: HAYDER Z. JASIM<br>• هاتف: 07879974395</div>', unsafe_allow_html=True)
        st.markdown("📊 **باقات النظام المتاحة:**")
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

else:
    with st.sidebar:
        st.markdown("### 👤 حالة الحساب الحالي")
        st.info(f"الكود: {st.session_state.user_code}\n\nالرصيد: {st.session_state.user_credit} محاولة")
        if not st.session_state.is_admin:
            st.warning(f"تاريخ انتهاء الصلاحية: {st.session_state.expiry_info}")
        if st.button("🚪 تسجيل الخروج الآمن"):
            st.session_state.clear()
            st.rerun()
        st.markdown("---")
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

    def render_user_services():
        st.markdown("### ✨ الخدمات الأكاديمية المتطورة")
        uploaded_file = st.file_uploader("📂 ارفع مستندك هنا", type=["pdf", "docx", "png", "jpg", "jpeg"])
        sub_tabs = st.tabs(["🔍 معاينة ومناقشة المستند", "🎓 المراجعة الأكاديمية والنقدية", "🌍 الترجمة الأكاديمية", "⚖️ الترجمة القانونية", "🎨 صناعة الصور", "✨ تحسين الصور", "👨‍🏫 المستشار الذكي"])
        
        with sub_tabs[0]:
            if uploaded_file:
                query = st.text_input("💬 سؤالك حول الملف:")
                if st.button("🚀 تنفيذ التحليل"):
                    if deduct_attempts(1):
                        run_progress_bar()
                        text, _ = extract_file_content(uploaded_file)
                        st.write(generate_academic_text(f"Context: {text}\nQuestion: {query}"))
            else: st.warning("يرجى رفع ملف.")
        
        with sub_tabs[6]:
            adv = st.text_area("🧠 اسأل المستشار:")
            if st.button("إرسال الاستشارة"):
                if deduct_attempts(1):
                    run_progress_bar()
                    st.write(generate_academic_text(adv))
        # (بقية التبويبات تعمل بنفس المنطق...)

    if st.session_state.is_admin:
        st.title("👨‍💼 لوحة تحكم الإدارة العليا")
        t1, t2 = st.tabs(["الخدمات", "الإدارة"])
        with t1: render_user_services()
        with t2: st.write("قسم الإدارة...")
    else:
        render_user_services()
