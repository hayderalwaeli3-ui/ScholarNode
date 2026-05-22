import streamlit as st

# 1. ضبط إعدادات الصفحة لتكون مغلقة افتراضياً ومنع الوميض
st.set_page_config(page_title="ScholarNode Academy", layout="wide", initial_sidebar_state="collapsed")

# 2. حجب القائمة الجانبية فورياً بالـ CSS قبل تحميل بقية الملف لحماية الخصوصية
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

# 3. استدعاء المكتبات (بدون أي تكرار)
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

# --- [بروتوكول الحماية المطلقة والاتصال الآمن] ---
API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)
DB_CODES = "scholar_main_db.csv"
DB_SECURITY = "device_tracking.csv"

# --- تهيئة قواعد البيانات التلقائية ---
def init_db():
    if not os.path.exists(DB_CODES):
        pd.DataFrame(columns=["code", "credit", "remaining", "status", "activation_date", "price_point"]).to_csv(DB_CODES, index=False)
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

# --- وظائف الخصم والحماية من الاختراق الحركي ---
def deduct_attempt(amount=1):
    if st.session_state.code == "HAYDER_2026":
        return True  # حساب المدير معفى من الخصم
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

# --- تنسيق الألوان الذكي المخصص للواجهات (CSS) ---
st.markdown("""
<style>
.main-header { background: #1e3a8a; color: #ffffff !important; padding: 20px; text-align: center; border-radius: 15px; border: 4px solid #facc15; margin-bottom: 25px; }
.payment-box { background: #1e3a8a; color: white !important; padding: 18px; border-radius: 12px; border: 3px solid #facc15; font-size: 0.9rem; line-height: 1.6; margin-bottom: 20px; }
.side-table { width: 100%; border-collapse: collapse; direction: rtl; text-align: center; font-size: 0.8rem; margin-top: 10px; }
.side-table th { background-color: #0ea5e9; color: white; padding: 6px; border: 1px solid #ddd; }
.side-table td { padding: 5px; border: 1px solid #ddd; background-color: white; color: black; font-weight: bold; }
.side-table tr:nth-child(even) td { background-color: #fee2e2; }
.admin-area { background: #f0f4f8; border: 2px solid #1e3a8a; padding: 15px; border-radius: 10px; margin-top: 10px; color: #1e3a8a; }
</style>
""", unsafe_allow_html=True)

# --- [بوابة الدخول الصارمة - قبل تسجيل الدخول] ---
if "auth" not in st.session_state:
    # فتح السلايد بار حصرياً لإظهار فئات الاشتراك والتحصيل المالي في صفحة الدخول
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: block !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("""
        <div style="background-color: #f0f9ff; color: #1e3a8a; padding: 15px; border-radius: 12px; border: 2px solid #ef4444; direction: rtl; text-align: right;">
            <h3 style="color: #ef4444; margin-top: 0; font-size: 1.1rem;">🏦 معلومات الدفع وتفعيل الكروت</h3>
            <p style="margin: 5px 0;"><b>👤 الاسم:</b> HAYDER Z. JASIM</p>
            <p style="margin: 5px 0;"><b>💳 ماستر كارد:</b> 8369719342</p>
            <p style="margin: 5px 0;"><b>📞 رقم تفعيل الكروت:</b> 07879974395</p>
        </div>
        """, unsafe_allow_html=True)

        # جدول فئات الاشتراك الملون (سمائي وأحمر)
        st.markdown("""
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

    # كتل واجهة الدخول الوسطى
    st.markdown('<div style="text-align: center; margin-top: 20px;"><h3>🔑 بوابة الدخول الآمن للمنصة</h3></div>', unsafe_allow_html=True)
    in_c = st.text_input("أدخل كود التفعيل المستلم للاتصال بالخادم:", type="password", key="main_login_input")

    if st.button("دخول المنصة", use_container_width=True):
        input_cleaned = in_c.strip()
        if input_cleaned == "HAYDER_2026":
            st.session_state.update({"auth": True, "is_admin": True, "credit": "∞ (حساب الإدارة)", "code": "HAYDER_2026"})
            st.rerun()
        else:
            df = pd.read_csv(DB_CODES)
            if input_cleaned in df['code'].values:
                rem = df[df['code'] == input_cleaned]['remaining'].values[0]
                if rem > 0:
                    st.session_state.update({"auth": True, "is_admin": False, "credit": rem, "code": input_cleaned})
                    st.rerun()
                else:
                    st.error("⚠️ هذا الكود مستهلك بالكامل، يرجى شحن الرصيد.")
            else:
                st.error("❌ الكود غير صحيح، يرجى التحقق أو التواصل مع الدعم لتفعيل كارت جديد.")
                
    st.stop()  # الحماية القاطعة: تمنع بايثون من استعراض أي سطر بالأسفل قبل النجاح في الدخول

# --- [محتوى المنصة المحمي - يظهر فقط بعد الدخول] ---

# تخصيص السلايد بار بعد تسجيل الدخول (إخفاء الأشرطة لمنع العبث لغير الإدارة)
if not st.session_state.get('is_admin', False):
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    # فتح لوحة الإدارة للمدير بسلايد بار مرئي ومتحكم به
    st.markdown("""
        <style>
            [data-testid="stSidebar"], .stSidebar { display: block !important; visibility: visible !important; }
        </style>
    """, unsafe_allow_html=True)
    with st.sidebar:
        st.write(f"⚙️ **حساب الإدارة نشط**")
        st.write(f"🎟️ **كود المرور المستخدم:** `{st.session_state.code}`")
        if st.button("🚪 تسجيل الخروج الآمن"):
            st.session_state.clear()
            st.rerun()

# رسالة ترحيبية أساسية موحدة (تظهر مرة واحدة في أعلى المنصة)
st.markdown(f'<div class="main-header"><h1>مرحباً دكتور Courage</h1><h2>الرصيد المتاح: {st.session_state.credit}</h2></div>', unsafe_allow_html=True)

# لوحة الإدارة الحصرية للمدير لإنشاء وإصدار الأكواد والكروت
if st.session_state.get('is_admin', False):
    st.markdown('<div class="admin-area"><h3>🛠️ لوحة تحكم الاشتراكات والكروت الصادرة</h3>', unsafe_allow_html=True)
    admin_tab1, admin_tab2 = st.tabs(["🎫 إصدار كروت جديدة", "📋 كشف الأكواد المفعّلة"])
    
    with admin_tab1:
        st.info("💡 السياسة المعتمدة: 1,000=10 | 5,000=50 | 10,000=100 محاولة نقدية.")
        card_value = st.selectbox("💰 اختر فئة الكارت المراد إنشاؤه (دينار عراقي):", 
                                 [1000, 5000, 10000, 20000, 30000, 40000, 50000, 100000],
                                 format_func=lambda x: f"{x:,} دينار")
        
        if card_value == 1000:
            auto_credit = 10
        elif card_value == 5000:
            auto_credit = 50
        else:
            auto_credit = int(card_value / 100)

        col_gen1, col_gen2 = st.columns([2, 1])
        
        if "generated_code" not in st.session_state:
            st.session_state.generated_code = ""
            
        with col_gen2:
            if st.button("🔄 توليد كود عشوائي"):
                random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                st.session_state.generated_code = f"SN-{random_suffix}"
        
        with col_gen1:
            c_new = st.text_input("🔑 الكود المقترح الصادر للمشترك:", value=st.session_state.generated_code)
            
        c_credit = st.number_input("🎟️ الرصيد المرتبط بالكود (محاولات):", min_value=1, value=auto_credit)
        
        if st.button("✅ حفظ وتفعيل الكارت في النظام"):
            if c_new:
                df = pd.read_csv(DB_CODES)
                if c_new.strip() in df['code'].values:
                    st.error("⚠️ هذا الكود موجود مسبقاً في النظام! يرجى توليد كود آخر.")
                else:
                    new_entry = pd.DataFrame([{
                        "code": c_new.strip(), 
                        "credit": c_credit, 
                        "remaining": c_credit, 
                        "status": "Active", 
                        "activation_date": datetime.now().strftime('%Y-%m-%d'),
                        "price_point": f"{card_value:,} IQD"
                    }])
                    pd.concat([df, new_entry], ignore_index=True).to_csv(DB_CODES, index=False)
                    st.success(f"✔️ تم الحفظ والنشاط! الكود {c_new.strip()} جاهز بقيمة {card_value:,} د.ع ورصيد {c_credit} محاولة.")
                    st.session_state.generated_code = ""
            else:
                st.error("⚠️ يرجى الضغط على زر التوليد لصياغة الكود أولاً.")

    with admin_tab2:
        st.dataframe(pd.read_csv(DB_CODES), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- الواجهة البرمجية الأساسية للمنصة ومستندات المراجعة ---
up = st.file_uploader("📂 ارفع مستند أو كتاب بصيغة PDF للمراجعة، الترجمة، أو الفحص", type=["pdf"])

tabs = st.tabs(["💬 المستشار الذكي", "🌍 الترجمة الأكاديمية", "🎓 المراجعة العلمية النقدية", "📄 معاينة ومناقشة المستند"])

# 1. تبويب المستشار الذكي وبناء الخطط
with tabs[0]:
    st.subheader("🎓 مستشار بناء الخطط والمقالات الأكاديمية")
    if "chat_history" not in st.session_state: 
        st.session_state.chat_history = []
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]): 
            st.markdown(message["content"])
    
    c_prompt = st.chat_input("اطلب بناء هيكلية بحث، خطة رسالة، أو مقال علمي رصين...")
    
    if c_prompt:
        if deduct_attempt(1):
            with st.spinner("✍️ جاري معالجة وتوليد المادة العلمية..."):
                res = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[{"role": "system", "content": "أنت بروفيسور أكاديمي ومستشار بحثي محترف في صياغة الخطط والمقالات والبحوث الرصينة المستندة لأصول المعرفة."}] + st.session_state.chat_history + [{"role": "user", "content": c_prompt}]
                )
                response = res.choices[0].message.content
                st.session_state.chat_history.append({"role": "user", "content": c_prompt})
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.session_state.last_plan = response
                st.rerun()
        else:
            st.error("⚠️ نفد الرصيد المتاح في هذا الكود لتنفيذ المحاولة.")

    if "last_plan" in st.session_state:
        st.markdown("---")
        st.success("✅ صياغة المادة جاهزة للتحميل والتصدير")
        word_file = create_word_file(st.session_state.last_plan)
        st.download_button(
            label="📥 تحميل الخطة المصاغة كملف Word مٌنسق",
            data=word_file,
            file_name=f"ScholarNode_Output_{datetime.now().strftime('%Y%m%d')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# 2. كتلة المعالجة والتحليل للملفات (ترجمة + مراجعة نقدية + معاينة تفاعلية)
if up:
    up.seek(0)
    doc_v = fitz.open(stream=up.read(), filetype="pdf")
    p_count = len(doc_v)
    
    # تبويب الترجمة المتقدمة
    with tabs[1]:
        st.subheader("🌍 مترجم ومصوب الحقول الأكاديمية الاحترافي")
        t_lang = st.selectbox("اختر اللغة المراد الترجمة إليها:", ["العربية", "English"], key="t_lang_new")
        
        if st.button(f"🚀 معالجة وترجمة {p_count} صفحة بالكامل"):
            current_credit = st.session_state.get('credit', 0)
            if st.session_state.code == "HAYDER_2026" or (isinstance(current_credit, (int, float)) and current_credit >= p_count):
                with st.spinner("جاري قراءة الصفحات وترجمتها أكاديمياً..."):
                    if deduct_attempt(p_count):
                        full_translation = ""
                        prog_bar = st.progress(0)
                        for i in range(p_count):
                            page_text = doc_v[i].get_text()
                            if page_text.strip():
                                res = client.chat.completions.create(
                                    model="gpt-4o-mini",
                                    messages=[{"role": "system", "content": f"You are a professional academic translator. Translate the following text into professional {t_lang}, maintaining rigid scientific context and terminology."}, 
                                              {"role": "user", "content": page_text}]
                                )
                                full_translation += f"\n--- صفحة {i+1} ---\n" + res.choices[0].message.content + "\n"
                            prog_bar.progress((i + 1) / p_count)
                        st.session_state.translation_result = full_translation
                        st.success("✅ تمت معالجة وتدقيق المستند بنجاح!")
                        st.rerun()
            else:
                st.error(f"⚠️ رصيدك المتبقي ({current_credit}) لا يغطي تكلفة ترجمة المستند المكون من ({p_count}) صفحة.")
        
        if "translation_result" in st.session_state:
            st.download_button(
                label="📥 تحميل النص المترجم كملف Word",
                data=create_word_file(st.session_state.translation_result),
                file_name="ScholarNode_Translated_Doc.docx"
            )

    # تبويب المراجعة النقدية العلمية
    with tabs[2]:
        st.subheader("🎓 الفحص النقدي والتقييم المنهجي للملف")
        review_lang = st.selectbox("لغة التقرير النقدي النهائي:", ["العربية", "English"], key="rev_lang")
        if st.button("توليد التقرير الأكاديمي التفصيلي"):
            current_credit = st.session_state.get('credit', 0)
            if st.session_state.code == "HAYDER_2026" or (isinstance(current_credit, (int, float)) and current_credit >= p_count):
                with st.spinner("🔍 جاري الفحص البنيوي والمنهجي للنص..."):
                    if deduct_attempt(p_count):
                        prog_placeholder = st.empty()
                        full_review = ""
                        for i in range(0, p_count, 10):
                            chunk = "\n".join([doc_v[j].get_text() for j in range(i, min(i+10, p_count))])
                            res = client.chat.completions.create(
                                model="gpt-4o-mini", 
                                messages=[{"role": "system", "content": f"Provide an intensive academic peer-review report in {review_lang}. Critique methodology, coherence, literature placement, and clarity."},
                                          {"role": "user", "content": chunk}]
                            )
                            full_review += res.choices[0].message.content + "\n"
                            percent = int((min(i + 10, p_count) / p_count) * 100)
                            prog_placeholder.progress(percent, text=f"جاري مراجعة وتحليل بنية الصفحات...")
                        st.session_state.review_result = full_review
                        prog_placeholder.empty()
                        st.success("✅ تم الانتهاء من التقييم النقدي العلمي للمستند!")
                        st.rerun()
            else:
                st.error(f"⚠️ رصيد كودك لا يغطي تكلفة الفحص المنهجي لـ {p_count} صفحة.")
        
        if "review_result" in st.session_state:
            st.markdown(st.session_state.review_result)
            st.download_button("📥 تحميل التقرير البنيوي (Word)", data=create_word_file(st.session_state.review_result), file_name="ScholarNode_Review_Report.docx")

    # تبويب معاينة ومناقشة صفحات المستند
    with tabs[3]:
        st.subheader("📄 فحص ومعاينة صفحات المستند وتدقيقها تفاعلياً")
        p_num = st.number_input("تصفح واختيار رقم الصفحة للمناقشة:", 1, p_count, 1)
        st.markdown("---")
        user_query = st.text_input("💬 اسأل المستشار الذكي عن أي جزئية أو فرضية في هذه الصفحة:")
        
        if st.button("إرسال التساؤل المنهجي"):
            if user_query:
                with st.spinner("⌛ جاري استخراج النص وتطبيقه على الخوارزمية..."):
                    if deduct_attempt(1):
                        page_content = doc_v[p_num-1].get_text()
                        res = client.chat.completions.create(
                            model="gpt-4o", 
                            messages=[
                                {"role": "system", "content": "أنت بروفيسور فاحص ومناقش للرسائل الأكاديمية. أجب بدقة شديدة معتمداً ومقيداً بالنص المرفق فقط لحماية الأمان العلمي."},
                                {"role": "user", "content": f"محتوى الصفحة المستخرجة:\n{page_content}\n\nسؤال الباحث للتحليل والمناقشة: {user_query}"}
                            ]
                        )
                        st.info(f"💡 **تحليل وتقييم المستشار:**\n\n{res.choices[0].message.content}")
                        st.rerun()
        
        st.markdown("---")
        pix = doc_v[p_num-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)

else:
    # حماية ضد أخطاء استدعاء المتغيرات غير الموجودة قبل رفع الملف
    with tabs[1]: st.info("📂 يرجى رفع ملف الـ PDF من الأعلى لتفعيل محرك الترجمة الفورية.")
    with tabs[2]: st.info("📂 يرجى رفع ملف الـ PDF من الأعلى لتفعيل فحص الهيكل النقدي.")
    with tabs[3]: st.info("📂 يرجى رفع ملف الـ PDF من الأعلى لاستعراض ومناقشة محتوى الصفحات.")

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
