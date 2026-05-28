import streamlit as st

# 1. ضبط إعدادات الصفحة (مرة واحدة فقط في أعلى الملف لمنع الانهيار واللون الأحمر)
st.set_page_config(page_title="ScholarNode Academy", layout="wide", initial_sidebar_state="expanded")

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

# 3. استدعاء المكتبات
import pandas as pd
import os
import io
import uuid
import random
import string
from datetime import datetime
import fitz  # PyMuPDF
from PIL import Image
try:
    import docx
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
from openai import OpenAI
import time

# --- بروتوكول الحماية والربط الذكي بسيرفر OpenAI ---
if "OPENAI_API_KEY" in st.secrets:
    API_KEY = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=API_KEY)
else:
    st.error("❌ خطأ: مفتاح OPENAI_API_KEY غير معرف في الـ Secrets الخاص بـ Streamlit.")

DB_CODES = "scholar_main_db.csv"
DB_SECURITY = "device_tracking.csv"

# --- تهيئة قواعد البيانات الثابتة ---
def init_db():
    if not os.path.exists(DB_CODES):
        pd.DataFrame(columns=["code", "credit", "remaining", "status", "activation_date", "expiry_date", "price_point"]).to_csv(DB_CODES, index=False)
    if not os.path.exists(DB_SECURITY):
        pd.DataFrame(columns=["device_id", "free_used", "is_blocked"]).to_csv(DB_SECURITY, index=False)

init_db()

# --- وظيفة إنشاء ملف Word بتنسيق أكاديمي رصين من الكود المستقر ---
def create_word_file(text):
    if not HAS_DOCX:
        return io.BytesIO(text.encode('utf-8'))
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

# --- وظائف الخصم والحماية من الكود المستقر ---
def deduct_attempt(amount=1):
    if st.session_state.get('code') == "HAYDER_2026":
        return True
    try:
        df = pd.read_csv(DB_CODES)
        idx_list = df.index[df['code'] == st.session_state.code].tolist()
        if idx_list:
            idx = idx_list[0]
            if df.at[idx, 'remaining'] >= amount:
                df.at[idx, 'remaining'] -= amount
                df.to_csv(DB_CODES, index=False)
                st.session_state.credit = df.at[idx, 'remaining']
                return True
    except Exception:
        pass
    return False

# تنبيه محاكاة التحميل الذكي
def simulate_processing():
    progress_bar = st.progress(0)
    status_text = st.empty()
    for percent_complete in range(0, 101, 25):
        time.sleep(0.05)
        progress_bar.progress(percent_complete)
        status_text.text(f"جاري المعالجة الأكاديمية عبر سيرفرات المعالجة الفعّالة... {percent_complete}%")
    status_text.empty()
    progress_bar.empty()

# تنسيق الألوان الذكي (CSS) المتوافق مع الهيكل القديم
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.stDeployButton {display:none;}
.main-header { background: #1e3a8a; color: #ffffff !important; padding: 20px; text-align: center; border-radius: 15px; border: 4px solid #facc15; margin-bottom: 25px; }
.payment-box { background: #1e3a8a; color: white !important; padding: 18px; border-radius: 12px; border: 3px solid #facc15; font-size: 0.9rem; line-height: 1.6; margin-bottom: 20px; }
.admin-area { background: #f0f4f8; border: 2px solid #1e3a8a; padding: 15px; border-radius: 10px; margin-top: 10px; color: #1e3a8a; }
</style>
""", unsafe_allow_html=True)

# تفعيل السلايد بار لجدول فئات الاشتراكات والمحاولات المعتمد لديك
with st.sidebar:
    st.markdown("### 🏦 معلومات الحساب والدعم")
    st.markdown("""
    <div class="payment-box">
        👤 <b>الاسم:</b> HAYDER Z. JASIM<br>
        💳 <b>ماستر كارد الرافدين:</b><br> 8369719342<br>
        📞 <b>رقم الهاتف (تفعيل):</b><br> 07879974395
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
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

    if "auth" in st.session_state:
        st.write(f"🎟️ **الكود المفعل:** `{st.session_state.code}`")
        if st.session_state.code == "HAYDER_2026":
            st.markdown("""
                <style>
                [data-testid="stSidebar"], .stSidebar { display: block !important; visibility: visible !important; width: auto !important; }
                header, .stAppHeader { display: block !important; visibility: visible !important; height: auto !important; }
                </style>
            """, unsafe_allow_html=True)
            st.markdown("### ⚙️ الإدارة")
            if st.button("🚪 تسجيل الخروج من الإدارة"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

# --- [1. بوابة الدخول والمعلومات - تظهر فقط قبل تسجيل الدخول] ---
if "auth" not in st.session_state:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: block !important; }
            .stDeployButton { display:none !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header"><h1>ScholarNode Academy</h1></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center;"><h3>🔑 بوابة الدخول الآمن للمنصة</h3></div>', unsafe_allow_html=True)
    
    in_c = st.text_input("أدخل كود التفعيل للدخول:", type="password", key="main_login_input")

    if st.button("دخول المنصة", use_container_width=True):
        input_cleaned = in_c.strip()
        if input_cleaned == "HAYDER_2026":
            st.session_state.update({"auth": True, "is_admin": True, "credit": 9999, "code": "HAYDER_2026"})
            st.rerun()
        else:
            try:
                df = pd.read_csv(DB_CODES)
                idx_list = df.index[df['code'] == input_cleaned].tolist()
                if idx_list:
                    idx = idx_list[0]
                    rem = df.at[idx, 'remaining']
                    if rem > 0:
                        st.session_state.update({"auth": True, "is_admin": False, "credit": rem, "code": input_cleaned})
                        st.rerun()
                    else:
                        st.error("❌ عذراً، رصيد هذا الكود نفد بالكامل.")
                else:
                    st.error("⚠️ الكود غير صحيح أو غير فعال.")
            except Exception:
                st.error("⚠️ خطأ في الاتصال بقاعدة البيانات.")
                
    st.stop()

# --- [2. محتوى المنصة - يظهر فقط بعد الدخول] ---

# لوحة الإدارة للمدير (HAYDER_2026)
if st.session_state.get('is_admin', False):
    st.markdown('<div class="admin-area"><h3>🛠️ إدارة اشتراكات ScholarNode العليا</h3>', unsafe_allow_html=True)
    admin_tab1, admin_tab2 = st.tabs(["🎫 إصدار كروت جديدة", "📋 كشف وفحص الأكواد المفعّلة"])
    
    with admin_tab1:
        st.info("💡 السياسة الحالية: 1,000=10 | 5,000=50 | 10,000=100 محاولة")
        card_value = st.selectbox("💰 اختر قيمة الكارت (دينار عراقي):", 
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
                st.session_state.generated_code = f"SN-{card_value // 1000}K-{random_suffix}"
        
        with col_gen1:
            c_new = st.text_input("🔑 كود التفعيل المولد:", value=st.session_state.generated_code)
            
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
                st.success(f"✔️ تم بنجاح! كود {c_new} جاهز للتسليم والعمل فوراً.")
                st.session_state.generated_code = "" 
            else:
                st.error("⚠️ يرجى توليد الكود أولاً")

    with admin_tab2:
        st.dataframe(pd.read_csv(DB_CODES), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- أداة الرفع الاستراتيجية المستقلة تماماً والمحمية ---
st.markdown("### 📂 مستودع رفع المستندات الموحد")
up = st.file_uploader("ارفع ملف البحث العلمي بصيغة (PDF فقط حالياً) لتفعيل التبويبات المتقدمة بالأسفل:", type=["pdf"])

# التبويبات الرئيسية المجمعة للمنصة
tabs = st.tabs([
    "💬 المستشار الأكاديمي المفتوح", 
    "🌍 الترجمة الأكاديمية الاحترافية", 
    "⚖️ الترجمة القانونية والصياغة",
    "🎓 المراجعة العلمية والنقد", 
    "🎨 توليد الصور والمخططات",
    "🎙️ توليد الصوت الطبيعي الذكي",
    "📄 معاينة ومناقشة الملف"
])

# 1. تبويب المستشار الذكي وبناء الخطط
with tabs[0]:
    st.subheader("🎓 مستشار بناء الخطط والبحوث والاستشارات العلمية")
    if "chat_history" not in st.session_state: 
        st.session_state.chat_history = []
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]): 
            st.markdown(message["content"])
    
    c_prompt = st.chat_input("اطلب بناء خطة بحثية، تحديد فجوة معرفية، أو استشارة أكاديمية...")
    
    if c_prompt:
        if deduct_attempt(1):
            simulate_processing()
            res = client.chat.completions.create(
                model="gpt-4o", 
                messages=[{"role": "system", "content": "أنت بروفيسور خبير ومستشار أكاديمي تقدم إرشادات صائبة وتصيغ خطط بحثية ممتازة بدقة علمية عالية."}] + st.session_state.chat_history + [{"role": "user", "content": c_prompt}]
            )
            response = res.choices[0].message.content
            st.session_state.chat_history.append({"role": "user", "content": c_prompt})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.session_state.last_plan = response
            st.rerun()

    if "last_plan" in st.session_state:
        st.markdown("---")
        st.success("✅ المخرجات الأكاديمية جاهزة للتحميل والتصدير:")
        st.download_button(
            label="📥 تحميل المخرجات كملف Word مجهز للتعديل",
            data=create_word_file(st.session_state.last_plan),
            file_name=f"ScholarNode_Output.docx"
        )

# كتلة المعالجة الحصرية للملف المرفوع
if up:
    try:
        up.seek(0)
        file_bytes = up.read()
        doc_v = fitz.open(stream=file_bytes, filetype="pdf")
        p_count = len(doc_v)
        
        # 2. تبويب الترجمة الأكاديمية الاحترافية
        with tabs[1]:
            st.subheader("🌍 مترجم ScholarNode الشامل (صياغة ومصطلحات أكاديمية)")
            t_lang = st.selectbox("اختر اللغة المستهدفة للترجمة:", ["العربية", "English"], key="t_lang_new")
            
            if st.button(f"🚀 بدء ترجمة {p_count} صفحة بالكامل"):
                if st.session_state.get('credit', 0) >= p_count or st.session_state.get('code') == "HAYDER_2026":
                    simulate_processing()
                    if deduct_attempt(p_count):
                        full_translation = ""
                        prog_bar = st.progress(0)
                        for i in range(p_count):
                            page_text = doc_v[i].get_text()
                            if page_text.strip():
                                res = client.chat.completions.create(
                                    model="gpt-4o-mini",
                                    messages=[{"role": "system", "content": f"Translate this scientific text professionally to {t_lang}, preserving all academic terms accurately."}, 
                                              {"role": "user", "content": page_text}]
                                )
                                full_translation += f"\n--- صفحة {i+1} ---\n" + res.choices[0].message.content + "\n"
                            prog_bar.progress((i + 1) / p_count)
                        st.session_state.translation_result = full_translation
                        st.success("✅ اكتملت عملية الترجمة الأكاديمية بنجاح!")
                        st.rerun()
                else:
                    st.error(f"عذراً، رصيدك الحالي لا يكفي لترجمة {p_count} صفحة بالكامل.")
            
            if "translation_result" in st.session_state:
                st.download_button(
                    label="📥 تحميل الكتاب أو المستند المترجم (Word)",
                    data=create_word_file(st.session_state.translation_result),
                    file_name="ScholarNode_Translated_Doc.docx"
                )

        # 3. تبويب الترجمة القانونية للمستندات
        with tabs[2]:
            st.subheader("⚖️ صياغة وترجمة المستندات ترجمة قانونية رسمية")
            legal_entity = st.text_input("اذكر الجهة الرسمية الموجه لها المستند (مثال: محكمة، جامعة، وزارة):", key="entity_t4")
            
            if st.button("🚀 بدء الصياغة القانونية المعتمدة (تكلفة ثابتة: 5 محاولات)"):
                if st.session_state.get('credit', 0) >= 5 or st.session_state.get('code') == "HAYDER_2026":
                    simulate_processing()
                    if deduct_attempt(5):
                        chunk = "\n".join([doc_v[j].get_text() for j in range(min(5, p_count))])
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "system", "content": f"أنت مترجم قانوني محلف ومجاز. صغ وترجم النص التالي بلغة قانونية رسمية صارمة ومطابقة للمعايير لتناسب التقديم إلى: {legal_entity}."},
                                      {"role": "user", "content": chunk}]
                        )
                        st.session_state.legal_result = res.choices[0].message.content
                        st.success("✅ تم الانتهاء من صياغة الوثيقة القانونية!")
                        st.rerun()
                else:
                    st.error("❌ رصيدك الحالي منخفض لإجراء الصياغة القانونية.")

            if "legal_result" in st.session_state:
                st.markdown(st.session_state.legal_result)
                st.download_button("📥 تحميل المستند القانوني (Word)", data=create_word_file(st.session_state.legal_result), file_name="Legal_Translation.docx")

        # 4. تبويب المراجعة العلمية والنقد
        with tabs[3]:
            st.subheader("🎓 مراجعة نقدية أكاديمية ومنهجية شاملة للبحث")
            review_lang = st.selectbox("اختر لغة تقرير النقد الأكاديمي:", ["العربية", "English"], key="rev_lang")
            
            if st.button("توليد تقرير النقد المنهجي"):
                simulate_processing()
                if deduct_attempt(max(1, int(p_count/2))):
                    full_review = ""
                    for i in range(0, p_count, 10):
                        chunk = "\n".join([doc_v[j].get_text() for j in range(i, min(i+10, p_count))])
                        res = client.chat.completions.create(
                            model="gpt-4o-mini", 
                            messages=[{"role": "system", "content": f"Provide a strict academic review and structural critique in {review_lang} highlighting methodology flaws and enhancement points."},
                                      {"role": "user", "content": chunk}]
                        )
                        full_review += res.choices[0].message.content + "\n"
                    st.session_state.review_result = full_review
                    st.success("✅ تم إنتاج تقرير التحكيم العلمي المنهجي!")
                    st.rerun()
            
            if "review_result" in st.session_state:
                st.markdown(st.session_state.review_result)
                st.download_button("📥 تحميل تقرير المراجعة والنقد (Word)", data=create_word_file(st.session_state.review_result), file_name="Academic_Critique_Report.docx")

        # 7. تبويب معاينة ومناقشة الملف
        with tabs[6]:
            st.subheader("📄 معاينة ومناقشة صفحات المستند المرفوع")
            p_num = st.number_input("عرض وعزل الصفحة رقم:", 1, p_count, 1)
            st.markdown("---")
            user_query = st.text_input("💬 اسأل الذكاء الاصطناعي عن محتوى هذه الصفحة تحديداً:")
            
            if st.button("إرسال السؤال ومناقشة النص"):
                if user_query:
                    simulate_processing()
                    if deduct_attempt(1):
                        page_content = doc_v[p_num-1].get_text()
                        res = client.chat.completions.create(
                            model="gpt-4o", 
                            messages=[
                                {"role": "system", "content": "أنت مساعد أكاديمي خبير ومحكم أبحاث. أجب بناءً على النص المستخلص من الصفحة المرفقة بدقة بالغة وبنفس لغة السؤال."},
                                {"role": "user", "content": f"النص المستخرج من الصفحة:\n{page_content}\n\nسؤال الباحث المستفسر:\n{user_query}"}
                            ]
                        )
                        st.info(f"**إجابة المستشار الأكاديمي الفورية:**\n\n{res.choices[0].message.content}")
            
            st.markdown("---")
            pix = doc_v[p_num-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            st.image(Image.open(io.BytesIO(pix.tobytes())), use_container_width=True)
            
    except Exception as e:
        st.error(f"⚠️ حدث خطأ أثناء معالجة الملف: {e}. يرجى التحقق من سلامة ملف الـ PDF.")

else:
    with tabs[1]: st.info("📂 يرجى سحب وإفلات أو رفع ملف PDF من الأعلى لتفعيل خدمة الترجمة الأكاديمية الشاملة.")
    with tabs[2]: st.info("📂 يرجى سحب وإفلات أو رفع ملف PDF من الأعلى لتفعيل خدمة الصياغة والترجمة القانونية.")
    with tabs[3]: st.info("📂 يرجى سحب وإفلات أو رفع ملف PDF من الأعلى لتفعيل خدمة التحكيم والنقد العلمي الشامل.")
    with tabs[6]: st.info("📂 يرجى سحب وإفلات أو رفع ملف PDF من الأعلى لمعاينة ومناقشة الصفحات صورياً ونصياً.")

# 5. تبويب توليد الصور والمخططات (مستقل)
with tabs[4]:
    st.subheader("🎨 توليد الصور والمخططات التوضيحية للأبحاث")
    image_prompt = st.text_area("أدخل الوصف الأكاديمي التفصيلي الدقيق للمخطط أو الشكل المطلوب بيانه:", key="img_prompt_t5")
    if st.button("بدء توليد الشكل التوضيحي (التكلفة: 5 محاولات)"):
        if not image_prompt.strip():
            st.warning("⚠️ يرجى كتابة وصف المخطط أولاً.")
        elif st.session_state.get('credit', 0) < 5 and st.session_state.get('code') != "HAYDER_2026":
            st.error("❌ الرصيد المتاح غير كافٍ لتوليد الصور.")
        else:
            simulate_processing()
            try:
                response = client.images.generate(model="dall-e-3", prompt=image_prompt, n=1, size="1024x1024")
                if deduct_attempt(5):
                    st.success("🎉 تم بناء المخطط البياني بنجاح!")
                    st.image(response.data[0].url, caption="المخطط المولد بواسطة المنصة")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ حدث عائق أثناء توليد الصورة: {e}")

# 6. تبويب توليد الصوت الاحترافي (مستقل)
with tabs[5]:
    st.subheader("🎙️ تحويل النصوص الأكاديمية إلى ملفات صوتية طبيعية (TTS)")
    audio_text = st.text_area("اكتب أو الصق النص المراد قراءته وتحويله إلى محتوى مسموع وبشري:", key="audio_text_t8")
    audio_voice = st.selectbox("اختر طبقة وخامة الصوت المفضلة:", ["onyx", "nova"], key="voice_t8")
    
    if st.button("تحويل المحتوى وتوليد الصوت (التكلفة: 5 محاولات)"):
        if not audio_text.strip():
            st.warning("⚠️ يرجى إدخل النص أولاً.")
        elif st.session_state.get('credit', 0) < 5 and st.session_state.get('code') != "HAYDER_2026":
            st.error("❌ رصيدك غير كافٍ لإنجاز توليد الصوت.")
        else:
            simulate_processing()
            try:
                response = client.audio.speech.create(model="tts-1", voice=audio_voice, input=audio_text)
                with open("temp_output.mp3", "wb") as f:
                    f.write(response.content)
                if deduct_attempt(5):
                    st.success("🟢 تم تحويل المحتوى إلى صوت حقيقي بنجاح!")
                    st.audio("temp_output.mp3")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ في معالجة نظام الصوتيات: {e}")

st.markdown("<br><hr><p style='text-align:center;'>ScholarNode Academy 2026</p>", unsafe_allow_html=True)
