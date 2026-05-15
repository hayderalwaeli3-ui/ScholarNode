import streamlit as st

# 1. ضبط إعدادات الصفحة لتكون مغلقة افتراضياً ومنع الوميض
st.set_page_config(page_title="ScholarNode", layout="wide", initial_sidebar_state="collapsed")

# 2. حجب القائمة الجانبية فورياً بالـ CSS قبل تحميل بقية الملف
st.markdown("""
    <style>
        /* إخفاء كلي وشامل لكل شيء فوق المحتوى */
        header, [data-testid="stHeader"], .stAppHeader, 
        [data-testid="stToolbar"], #MainMenu, button[kind="header"] {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
        }
        
        /* إخفاء القطة والنقاط الثلاث بأسمائها البرمجية الجديدة */
        .st-emotion-cache-zq5wmm, .st-emotion-cache-18ni7ve, 
        .st-emotion-cache-yf7105, .st-emotion-cache-1647ite {
            display: none !important;
        }

        /* رفع المحتوى للأعلى وتغطية مكان الشريط تماماً */
        .main .block-container {
            padding-top: 0rem !important;
            margin-top: -70px !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. بقية المكتبات
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
    # 1. معلومات الحساب والدعم (ثابتة)
    st.markdown("### 🏦 معلومات الحساب والدعم")
    st.markdown(f"""
    <div class="payment-box">
        👤 <b>الاسم:</b> HAYDER Z. JASIM<br>
        💳 <b>ماستر كارد الرافدين:</b><br> 8369719342<br>
        📞 <b>رقم الهاتف (تفعيل):</b><br> 07879974395
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # 2. جدول فئات الاشتراك والمحاولات (الجديد)
    st.markdown("### 🎫 فئات كروت الاشتراك")
    subscription_plans = [
        {"الفئة": "1,000 دينار", "المحاولات": "10 محاولات"},
        {"الفئة": "5,000 دينار", "المحاولات": "50 محاولة"},
        {"الفئة": "10,000 دينار", "المحاولات": "100 محاولة"},
        {"الفئة": "20,000 دينار", "المحاولات": "200 محاولة"},
        {"الفئة": "30,000 دينار", "المحاولات": "300 محاولة"},
        {"الفئة": "40,000 دينار", "المحاولات": "400 محاولة"},
        {"الفئة": "50,000 دينار", "المحاولات": "500 محاولة"},
        {"الفئة": "100,000 دينار", "المحاولات": "1000 محاولة"}
    ]
    st.table(subscription_plans)
    
    st.markdown("---")

    # 3. نظام التحقق والتعرف على الكود المفعل
    if "auth" in st.session_state:
        st.write(f"🎟️ **الكود المفعل:** `{st.session_state.code}`")
        
        # --- [إضافة خيار الإدارة] ---
        if st.session_state.code == "HAYDER_2026":
            st.markdown("""
                <style>
                [data-testid="stSidebar"], .stSidebar { 
                    display: block !important; 
                    visibility: visible !important; 
                    width: auto !important; 
                }
                header, .stAppHeader { 
                    display: block !important; 
                    visibility: visible !important; 
                    height: auto !important; 
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### ⚙️ الإدارة")
            if st.button("🛠️ لوحة التحكم في الكروت"):
                st.session_state.admin_view = not st.session_state.get('admin_view', False)
    # --- [بوابة الدخول والمعلومات] ---
if "auth" not in st.session_state:
    # 1. إخفاء القائمة الجانبية وتنسيق العنوان
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            .stDeployButton { display:none !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)

# 1. القائمة الجانبية (تظهر فقط قبل تسجيل الدخول)
    with st.sidebar:
        st.markdown(f"""
        <div style="background-color: #f0f9ff; color: #1e3a8a; padding: 15px; border-radius: 12px; border: 2px solid #ef4444; direction: rtl; text-align: right;">
            <h3 style="color: #ef4444; margin-top: 0; font-size: 1.1rem;">🏦 معلومات الدفع</h3>
            <p style="margin: 5px 0;"><b>👤 الاسم:</b> HAYDER Z. JASIM</p>
            <p style="margin: 5px 0;"><b>💳 ماستر كارد:</b> 8369719342</p>
            <p style="margin: 5px 0;"><b>📞 تفعيل:</b> 07879974395</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <style>
            .side-table { width: 100%; border-collapse: collapse; direction: rtl; text-align: center; font-size: 0.8rem; margin-top: 10px; }
            .side-table th { background-color: #0ea5e9; color: white; padding: 6px; border: 1px solid #ddd; }
            .side-table td { padding: 5px; border: 1px solid #ddd; background-color: white; color: black; }
            .side-table tr:nth-child(even) td { background-color: #fee2e2; }
        </style>
        <table class="side-table">
            <tr><th>الفئة (د.ع)</th><th>المحاولات</th></tr>
            <tr><td>1,000</td><td>10 محاولات</td></tr>
            <tr><td>5,000</td><td>50 محاولة</td></tr>
            <tr><td>10,000</td><td>100 محاولة</td></tr>
            <tr><td>20,000</td><td>200 محاولة</td></tr>
            <tr><td>30,000</td><td>300 محاولة</td></tr>
            <tr><td>40,000</td><td>400 محاولة</td></tr>
            <tr><td>50,000</td><td>500 محاولة</td></tr>
            <tr><td>100,000</td><td>1000 محاولة</td></tr>
        </table>
        """, unsafe_allow_html=True)
        st.markdown("---")

    # 2. واجهة الدخول الرئيسية (في وسط الصفحة)
    st.markdown('<div style="text-align: center;"><h3>🔑 بوابة الدخول الآمن</h3></div>', unsafe_allow_html=True)
    
    # تعريف خانة إدخال الكود "مرة واحدة فقط"
    in_c = st.text_input("أدخل كود التفعيل للدخول:", type="password", key="main_login_input")

    if st.button("دخول المنصة", use_container_width=True):
        input_cleaned = in_c.strip()
        
        # خوارزمية التحقق الأساسية (دكتور Courage)
        if input_cleaned == "HAYDER_2026":
            st.session_state.update({
                "auth": True, 
                "is_admin": True, 
                "credit": 9999, 
                "code": "HAYDER_2026"
            })
            # كسر حماية السلايد بار للمدير
            st.markdown("<style>[data-testid='stSidebar'], .stSidebar { display: block !important; visibility: visible !important; }</style>", unsafe_allow_html=True)
            st.rerun()
        
        # هنا يمكنك إضافة خوارزمية التحقق من الأكواد الأخرى (Database)
     # ... (نهاية كود التحقق من الطلاب)
        else:
            st.error("الكود غير صحيح")
            
    # --- التعديل الجوهري هنا ---
    if "auth" not in st.session_state:
        st.stop()  # يتوقف الكود هنا فقط إذا لم يسجل المستخدم دخوله

# --- [ النقطة رقم 3: إعادة الصلاحيات للمدير ] ---
if st.session_state.get("code") == "HAYDER_2026":
    st.markdown("""
        <style>
            [data-testid="stSidebar"], .stSidebar { 
                display: block !important; 
                visibility: visible !important; 
                width: auto !important; 
            }
            header, .stAppHeader { 
                display: block !important; 
                visibility: visible !important; 
            }
        </style>
    """, unsafe_allow_html=True)

# --- محتوى المنصة الرئيسي (الذي سيظهر الآن) ---
st.markdown(f'<div class="main-header"><h1>مرحباً دكتور Courage</h1><h2>الرصيد المتاح: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)

# هنا تكمل بقية الأسطر الخاصة بالـ tabs و file_uploader كما هي في كودك

# ثم يكمل بقية الكود (مثلاً st.title("ScholarNode") أو الترحيب)
    
# --- قسم لوحة الإدارة (السياسة المالية الجديدة: 100 محاولة لكل 10 آلاف) ---
if st.session_state.get('admin_view', False):
    st.markdown('<div class="admin-area"><h3>🛠️ إدارة اشتراكات ScholarNode</h3>', unsafe_allow_html=True)
    admin_tab1, admin_tab2 = st.tabs(["🎫 إصدار كروت جديدة", "📋 كشف الأكواد"])

    with admin_tab1:
        st.info("💡 السياسة الحالية: 1,000=10 | 5,000=50 | 10,000=100 محاولة")

        # 1. اختيار قيمة الكارت
        card_value = st.selectbox("💰 اختر قيمة الكارت (دينار عراقي):",
                                 [1000, 5000, 10000, 20000, 30000, 40000, 50000, 100000],
                                 format_func=lambda x: f"{x:,} دينار")

        # 2. الحسبة الآلية للمحاولات
        if card_value == 1000:
            auto_credit = 10
        elif card_value == 5000:
            auto_credit = 50
        else:
            auto_credit = int(card_value / 100)

        # 3. رسم الواجهة
        col_gen1, col_gen2 = st.columns([2, 1])
        
        if "generated_code" not in st.session_state:
            st.session_state.generated_code = ""
            
        with col_gen2:
            if st.button("🔄 توليد كود عشوائي"):
                import random, string
                random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                st.session_state.generated_code = f"SN-{random_suffix}"
        
        with col_gen1:
            c_new = st.text_input("🔑 كود التفعيل:", value=st.session_state.generated_code)
            
        c_credit = st.number_input("🎟️ الرصيد الممنوح (محاولات):", min_value=1, value=auto_credit)
        
        if st.button("✅ تفعيل وحفظ الكود في قاعدة البيانات"):
            if c_new:
                df = pd.read_csv(DB_CODES)
                new_entry = pd.DataFrame([{
                    "code": c_new.strip(), 
                    "credit": c_credit, 
                    "remaining": c_credit, 
                    "status": "Active", 
                    "activation_date": datetime.now().strftime('%Y-%m-%d'),
                    "price_point": f"{card_value:,} IQD"
                }])
                pd.concat([df, new_entry], ignore_index=True).to_csv(DB_CODES, index=False)
                st.success(f"✔️ تم بنجاح! كود بقيمة {card_value:,} د.ع برصيد {c_credit} محاولة.")
                st.session_state.generated_code = "" 
            else:
                st.error("⚠️ يرجى توليد الكود أولاً")

    with admin_tab2:
        st.dataframe(pd.read_csv(DB_CODES), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
# --- الواجهة الرئيسية للمنصة ---
st.markdown(f'<div class="main-header"><h1>مرحباً دكتور Courage</h1><h2>الرصيد المتاح: {st.session_state.credit} محاولة</h2></div>', unsafe_allow_html=True)
up = st.file_uploader("📂 ارفع ملف PDF للمراجعة أو الترجمة", type=["pdf"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية", "📄 معاينة الملف"])

# 1. تبويب المستشار الذكي (مع إضافة ميزة تحميل الخطة كملف وورد)
with tabs[0]:
    st.subheader("🎓 مستشار بناء الخطط والبحوث")
    if "chat_history" not in st.session_state: 
        st.session_state.chat_history = []
    
    # عرض التاريخ
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]): 
            st.markdown(message["content"])
    
    # إدخال السؤال
    c_prompt = st.chat_input("اطلب بناء خطة بحثية أو مقال رصين...")
    
    if c_prompt:
        if deduct_attempt(1):
            with st.spinner("✍️ جاري صياغة الخطة الأكاديمية..."):
                res = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[{"role": "system", "content": "أنت خبير أكاديمي محترف في كتابة الخطط البحثية والمقالات."}] + st.session_state.chat_history + [{"role": "user", "content": c_prompt}]
                )
                response = res.choices[0].message.content
                st.session_state.chat_history.append({"role": "user", "content": c_prompt})
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                # حفظ آخر إجابة لتوليد ملف الوورد
                st.session_state.last_plan = response
                st.rerun()

    # --- إضافة زر تحميل الملف هنا ---
    if "last_plan" in st.session_state:
        st.markdown("---")
        st.success("✅ الخطة جاهزة للتحميل")
        # استخدام دالة create_word_file الموجودة مسبقاً في كودك رقم 11
        word_file = create_word_file(st.session_state.last_plan)
        st.download_button(
            label="📥 تحميل الخطة كملف Word",
            data=word_file,
            file_name=f"Research_Plan_{datetime.now().strftime('%Y%m%d')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
# --- 2. كتلة المعالجة الأكاديمية الشاملة (ترجمة + مراجعة + معاينة) ---
if up:
    # تهيئة الملف واستخراج عدد الصفحات بشكل آمن
    up.seek(0)
    doc_v = fitz.open(stream=up.read(), filetype="pdf")
    p_count = len(doc_v)
    
    # تبويب الترجمة (المطور والاقتصادي)
    with tabs[1]:
        st.subheader("🌍 مترجم ScholarNode الشامل (ترجمة احترافية)")
        t_lang = st.selectbox("اللغة المستهدفة للترجمة:", ["العربية", "English"], key="t_lang_new")
        
        if st.button(f"🚀 بدء ترجمة {p_count} صفحة"):
            if st.session_state.get('credit', 0) >= p_count:
                with st.spinner("جاري الترجمة الشاملة..."):
                    if deduct_attempt(p_count):
                        full_translation = ""
                        prog_bar = st.progress(0)
                        for i in range(p_count):
                            page_text = doc_v[i].get_text()
                            if page_text.strip():
                                res = client.chat.completions.create(
                                    model="gpt-4o-mini",
                                    messages=[{"role": "system", "content": f"Translate to {t_lang}"}, 
                                              {"role": "user", "content": page_text}]
                                )
                                full_translation += f"\n--- صفحة {i+1} ---\n" + res.choices[0].message.content + "\n"
                            prog_bar.progress((i + 1) / p_count)
                        st.session_state.translation_result = full_translation
                        st.success("✅ اكتملت الترجمة!")
            else:
                st.error(f"عذراً، رصيدك الحالي ({st.session_state.get('credit', 0)}) لا يكفي لترجمة {p_count} صفحة.")
        
        if "translation_result" in st.session_state:
            st.download_button(
                label="📥 تحميل الكتاب المترجم (Word)",
                data=create_word_file(st.session_state.translation_result),
                file_name="ScholarNode_Translated.docx"
            )

    # تبويب المراجعة النقدية
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
                        percent = int((min(i + 10, p_count) / p_count) * 100)
                        prog_placeholder.progress(percent, text=f"جاري التحليل النقدي...")
                    st.session_state.review_result = full_review
                    prog_placeholder.empty()
        
        if "review_result" in st.session_state:
            st.markdown(st.session_state.review_result)
            st.download_button("📥 تحميل تقرير المراجعة", data=create_word_file(st.session_state.review_result), file_name="Academic_Review.docx")

    # تبويب معاينة ومناقشة الملف (تم نقله داخل شرط وجود الملف)
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

else:
    # رسالة تظهر للمستخدم عند عدم رفع ملف لتجنب الأخطاء البرمجية
    with tabs[1]: st.info("📂 يرجى رفع ملف PDF من الأعلى لتفعيل خدمة الترجمة.")
    with tabs[2]: st.info("📂 يرجى رفع ملف PDF من الأعلى لتفعيل خدمة المراجعة النقدية.")
    with tabs[3]: st.info("📂 يرجى رفع ملف PDF من الأعلى لمعاينة الصفحات.")

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy 2026</p>", unsafe_allow_html=True)
