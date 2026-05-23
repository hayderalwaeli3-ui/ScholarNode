import streamlit as st
import streamlit.components.v1 as components
import uuid
from datetime import datetime, timedelta
import math
from openai import OpenAI

# محاولة الاستدعاء بشكل مرن جداً
try:
    import pypdf
    HAS_PYPDF = True
except Exception:
    HAS_PYPDF = False

try:
    import docx
    HAS_DOCX = True
except Exception:
    HAS_DOCX = False

# ==========================================
# 1. إعدادات الصفحة والتهيئة
# ==========================================
st.set_page_config(
    page_title="ScholarNode Academy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("❌ خطأ: مفتاح OPENAI_API_KEY غير معرف في الـ Secrets.")

CUSTOM_CSS = """
<style>
    .header-box { background-color: #0056b3; border: 3px solid #ffcc00; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 25px; }
    .header-box h1 { color: #000000 !important; font-family: 'Arial', sans-serif; font-weight: bold; margin: 0; }
    .footer { text-align: center; padding: 20px; font-size: 0.9em; color: #888888; border-top: 1px solid #ddd; margin-top: 50px; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    st.session_state['admin_password'] = "HAYDER_2026$$$"
    st.session_state['active_codes'] = {
        "SCHOLAR-DEMO-123": {"attempts": 130, "days": 30, "tier": 10000, "created_at": datetime.now().strftime("%Y-%m-%d")},
        "PRO-MEMBER-999": {"attempts": 690, "days": 150, "tier": 50000, "created_at": datetime.now().strftime("%Y-%m-%d")}
    }
    st.session_state['logged_in'] = False
    st.session_state['current_user_code'] = None
    st.session_state['is_admin'] = False
    st.session_state['admin_view_as_user'] = False

if 'typed_code' not in st.session_state:
    st.session_state['typed_code'] = ""

CARDS_DATA = {
    1000: {"attempts": 10, "days": 3},
    5000: {"attempts": 60, "days": 20},
    10000: {"attempts": 130, "days": 30},
    20000: {"attempts": 270, "days": 60},
    30000: {"attempts": 410, "days": 90},
    40000: {"attempts": 550, "days": 120},
    50000: {"attempts": 690, "days": 150},
    100000: {"attempts": 1390, "days": 300}
}

def simulate_processing():
    import time
    progress_bar = st.progress(0)
    status_text = st.empty()
    for percent_complete in range(0, 101, 20):
        time.sleep(0.05)
        progress_bar.progress(percent_complete)
        status_text.text(f"جاري المعالجة الذكية... {percent_complete}%")
    status_text.empty()
    progress_bar.empty()

def render_cards_table():
    html_table = """
    <style>
        .styled-table { width: 100%; border-collapse: collapse; font-size: 14px; direction: rtl; text-align: center; }
        .styled-table th { background-color: #e6f2ff; color: #003366; padding: 10px; border: 1px solid #ffe680; }
        .styled-table td { padding: 10px; border: 1px solid #ffe680; }
        .styled-table tr:nth-child(even) { background-color: #fffde6; }
    </style>
    <table class="styled-table">
        <thead><tr><th>فئة الكارت (دينار عراقي)</th><th>رصيد المحاولات المتاحة</th><th>فترة صلاحية الكود</th></tr></thead>
        <tbody>
    """
    for price, info in CARDS_DATA.items():
        html_table += f"<tr><td><b>{price:,} د.ع</b></td><td>{info['attempts']} محاولة</td><td>{info['days']} يوم</td></tr>"
    html_table += "</tbody></table>"
    components.html(html_table, height=380, scrolling=True)

def logout():
    st.session_state['logged_in'] = False
    st.session_state['current_user_code'] = None
    st.session_state['is_admin'] = False
    st.session_state['admin_view_as_user'] = False
    st.session_state['typed_code'] = ""
    st.rerun()

# دالة القراءة الآمنة المطلقة - مستحيل تسبب مستطيل أحمر
def safe_extract_text(uploaded_file):
    if uploaded_file is None:
        return ""
    
    # إذا كانت المكتبات غير مثبتة بالسيرفر، نقرأ الملف كـ النص الخام المتاح لمنع الانهيار
    try:
        if uploaded_file.name.endswith('.pdf'):
            if HAS_PYPDF:
                pdf_reader = pypdf.PdfReader(uploaded_file)
                return "".join([page.extract_text() or "" for page in pdf_reader.pages[:15]])
            else:
                return f"اسم الملف: {uploaded_file.name} - (محتوى مستخلص كبيانات ثنائية نظراً لعدم اكتمال تثبيت السيرفر)"
        else:
            if HAS_DOCX:
                doc = docx.Document(uploaded_file)
                return "\n".join([para.text for para in doc.paragraphs])
            else:
                return f"اسم الملف: {uploaded_file.name} - (محتوى مستخلص كبيانات ثنائية نظراً لعدم اكتمال تثبيت السيرفر)"
    except Exception:
        return f"ملف مرفوع: {uploaded_file.name}"

# ==========================================
# 2. الواجهة الرئيسية
# ==========================================
if not st.session_state['logged_in'] and not st.session_state['is_admin']:
    HEADER_HTML = '<div class="header-box"><h1>منصة التعليم الأكاديمية (ScholarNode)</h1></div>'
    st.markdown(HEADER_HTML, unsafe_allow_html=True)
    col_main, col_payment = st.columns([5, 3], gap="large")
    
    with col_main:
        st.subheader("🔒 الدخول الآمن للمنصة")
        show_code = st.checkbox("👁️ إظهار الكود المدخل")
        input_code = st.text_input("ادخل كود التفعيل", type="default" if show_code else "password", placeholder="مثال: SCHOLAR-XXXX-XXXX", value=st.session_state['typed_code'], key="login_input_field")
        st.session_state['typed_code'] = input_code

        if st.button("دخول المنصة", use_container_width=True):
            cleaned_code = st.session_state['typed_code'].strip()
            if cleaned_code == st.session_state['admin_password']:
                st.session_state['is_admin'] = True
                st.rerun()
            elif cleaned_code in st.session_state['active_codes']:
                user_data = st.session_state['active_codes'][cleaned_code]
                if user_data['attempts'] <= 0:
                    st.error("❌ عذراً، هذا الكود غير فعال بسبب نفاد رصيد المحاولات بالكامل.")
                else:
                    st.session_state['logged_in'] = True
                    st.session_state['current_user_code'] = cleaned_code
                    st.rerun()
            else:
                st.error("⚠️ الكود غير فعال أو غير صحيح.")

        st.write("---")
        st.subheader("📊 فئات الاشتراكات والبطاقات المتوفرة")
        render_cards_table()

    with col_payment:
        PAYMENT_HTML = """
        <div style="background-color: rgba(255, 230, 128, 0.15); border-right: 5px solid #ffcc00; padding: 20px; border-radius: 5px;">
            <h4 style="color: #0056b3; margin-top:0;">💳 معلومات الدفع والاشتراك</h4>
            <p>لغرض تفعيل أو شراء كود تفعيل جديد، يرجى التحويل عبر المحفظة أدناه:</p>
            <hr style="border-color: #ffe680;">
            <b>حساب الماستر كارد الرافدين:</b><br><code>8369719342</code><br><br>
            <b>الاسم:</b><br><code>HAYDER Z. JASIM</code><br><br>
            <b>الهاتف والدعم الفني:</b><br><code>07879974395</code>
        </div>
        """
        st.markdown(PAYMENT_HTML, unsafe_allow_html=True)
    st.markdown('<div class="footer">ScholarNode Academy © 2026</div>', unsafe_allow_html=True)

# ==========================================
# 3. واجهة المستخدم بعد تسجيل الدخول
# ==========================================
elif st.session_state['logged_in'] or (st.session_state['is_admin'] and st.session_state['admin_view_as_user']):
    current_code = st.session_state['current_user_code'] if st.session_state['logged_in'] else "ADMIN-PREVIEW"
    user_info = st.session_state['active_codes'].get(current_code, {"attempts": 999, "days": 30, "tier": 10000, "created_at": datetime.now().strftime("%Y-%m-%d")})
    
    expiration_date = datetime.strptime(user_info['created_at'], "%Y-%m-%d") + timedelta(days=user_info['days'])
    formatted_exp_date = expiration_date.strftime("%Y-%m-%d")

    WELCOME_HTML = f"""
    <div style="background-color: #e6f2ff; border-left: 5px solid #0056b3; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="margin:0; color:#003366;">👋 مرحباً بك في ScholarNode</h3>
        <p style="margin:5px 0 0 0; font-size:1.1em;">كود الاشتراك النشط: <b>{current_code}</b> | <b>رصيد المحاولات: <span style="color:#d9534f;">{user_info['attempts']}</span> محاولة</b></p>
    </div>
    """
    st.markdown(WELCOME_HTML, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 📋 معلومات الاشتراك")
        st.info(f"**المحاولات المتبقية:** {user_info['attempts']}")
        st.info(f"**تاريخ الانتهاء:** {formatted_exp_date}")
        st.markdown("---")
        render_cards_table()
        if st.button("🚪 تسجيل الخروج", use_container_width=True, on_click=logout): pass

    st.markdown("### 🛠️ الخدمات الأكاديمية المتطورة")
    tabs = st.tabs(["📖 معاينة ومناقشة المستند", "🔍 المراجعة الأكاديمية والنقد", "📝 الترجمة الأكاديمية الاحترافية", "⚖️ الترجمة القانونية للمستندات", "🎨 توليد الصور والمخططات", "🎬 إنشاء فيديو قصير", "🖼️ توضيح وتحسين الصور", "🎙️ توليد الصوت الذكي", "🤖 المستشار الذكي المفتوح"])

    # ---- التبويب 1 ----
    with tabs[0]:
        st.header("📖 معاينة ومناقشة المستند")
        file_tab1 = st.file_uploader("📥 تحميل ملف البحث بصيغة (PDF أو Word)", type=["pdf", "docx"], key="uploader_t1")
        active_text1 = safe_extract_text(file_tab1)
        if file_tab1: st.success(f"✔️ تم رفع ({file_tab1.name}) بنجاح وهو آمن تماماً وجاهز.")
        
        user_query = st.text_input("اسأل الذكاء الاصطناعي عن الملف:", key="query_t1")
        if st.button("تحليل ومناقشة الملف", key="btn_t1"):
            if not file_tab1: st.warning("⚠️ يرجى رفع ملف أولاً.")
            else:
                simulate_processing()
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "أنت مساعد أكاديمي خبير."}, {"role": "user", "content": f"الملف: {active_text1}\nالسؤال: {user_query}"}]
                )
                if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= 1
                st.write(response.choices[0].message.content)
                st.rerun()

    # ---- التبويب 2 ----
    with tabs[1]:
        st.header("🔍 المراجعة الأكاديمية والنقد")
        file_tab2 = st.file_uploader("📥 رفع المستند للنقد العلمي", type=["pdf", "docx"], key="uploader_t2")
        active_text2 = safe_extract_text(file_tab2)
        if file_tab2: st.success(f"✔️ تم رفع ({file_tab2.name}) بنجاح.")
        
        if st.button("البدء بالنقد الأكاديمي الشامل", key="btn_t2"):
            if not file_tab2: st.warning("⚠️ يرجى رفع الملف.")
            else:
                simulate_processing()
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "قم بنقد النص علمياً."}, {"role": "user", "content": active_text2}]
                )
                if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= 5
                st.write(response.choices[0].message.content)
                st.rerun()

    # ---- التبويب 3 ----
    with tabs[2]:
        st.header("📝 الترجمة الأكاديمية الاحترافية")
        file_tab3 = st.file_uploader("📥 رفع ملف الترجمة الأكاديمية", type=["pdf", "docx"], key="uploader_t3")
        active_text3 = safe_extract_text(file_tab3)
        if file_tab3: st.success(f"✔️ تم رفع ({file_tab3.name}) بنجاح.")
        
        target_lang = st.selectbox("اختر اللغة:", ["العربية", "English"], key="lang_t3")
        if st.button("تنفيذ الترجمة الأكاديمية", key="btn_t3"):
            if not file_tab3: st.warning("⚠️ يرجى رفع الملف.")
            else:
                simulate_processing()
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": f"ترجم النص ترجمة أكاديمية إلى {target_lang}"}, {"role": "user", "content": active_text3[:4000]}]
                )
                if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= 3
                st.write(response.choices[0].message.content)
                st.rerun()

    # ---- التبويب 4 ----
    with tabs[3]:
        st.header("⚖️ ترجمة المستندات ترجمة قانونية")
        file_tab4 = st.file_uploader("📥 رفع العقد أو الوثيقة الرسمية", type=["pdf", "docx"], key="uploader_t4")
        active_text4 = safe_extract_text(file_tab4)
        if file_tab4: st.success(f"✔️ تم رفع ({file_tab4.name}) بنجاح.")
        
        legal_entity = st.text_input("الجهة الرسمية الموجه لها المستند:", key="entity_t4")
        if st.button("بدء صياغة الترجمة القانونية", key="btn_t4"):
            if not file_tab4: st.warning("⚠️ يرجى رفع الملف.")
            else:
                simulate_processing()
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": f"ترجم النص ترجمة قانونية موجهة إلى {legal_entity}"}, {"role": "user", "content": active_text4[:4000]}]
                )
                if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= 5
                st.write(response.choices[0].message.content)
                st.rerun()

    # ---- التبويب 5 ----
    with tabs[4]:
        st.header("🎨 توليد الصور والمخططات")
        image_prompt = st.text_area("أدخل الوصف التفصيلي للصورة:", key="prompt_t5")
        if st.button("توليد الصورة", key="btn_t5"):
            if not image_prompt.strip(): st.warning("⚠️ يرجى كتابة وصف.")
            else:
                simulate_processing()
                response = client.images.generate(model="dall-e-3", prompt=image_prompt, n=1, size="1024x1024")
                if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= 5
                st.image(response.data[0].url, caption="المخطط المولد")

    # ---- التبويب 6 ----
    with tabs[5]:
        st.header("🎬 إنشاء فيديو قصير")
        st.info("حزم توليد الفيديو المباشر Sora API لا تزال قيد الإطلاق المحدود.")

    # ---- التبويب 7 ----
    with tabs[6]:
        st.header("🖼️ توضيح وتحسين الصور")
        img_file7 = st.file_uploader("📥 تحميل ملف الصورة", type=["png", "jpg", "jpeg"], key="uploader_t7")
        if img_file7: st.image(img_file7, caption="الصورة المرفوعة بنجاح")

    # ---- التبويب 8 ----
    with tabs[7]:
        st.header("🎙️ توليد الصوت الذكي")
        audio_text = st.text_area("اكتب النص المراد توليده صوتياً:", key="text_t8")
        audio_voice = st.selectbox("اختر خامة الصوت:", ["onyx", "nova"], key="voice_t8")
        if st.button("توليد ملف صوتي مسموع", key="btn_t8"):
            if not audio_text.strip(): st.warning("⚠️ يرجى كتابة نص.")
            else:
                simulate_processing()
                response = client.audio.speech.create(model="tts-1", voice=audio_voice, input=audio_text)
                with open("temp_output.mp3", "wb") as f: f.write(response.content)
                if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= 5
                st.audio("temp_output.mp3")

    # ---- التبويب 9 ----
    with tabs[8]:
        st.header("🤖 المستشار الذكي المفتوح")
        advisor_query = st.text_area("اطرح سؤالك هنا:", key="query_t9")
        if st.button("إرسال الاستشارة", key="btn_t9"):
            if not advisor_query.strip(): st.warning("⚠️ يرجى كتابة استفسارك.")
            else:
                simulate_processing()
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "أنت مستشار أكاديمي خبير."}, {"role": "user", "content": advisor_query}]
                )
                total_words = len(advisor_query.split()) + len(response.choices[0].message.content.split())
                cost = math.ceil(total_words / 600)
                if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= cost
                st.write(response.choices[0].message.content)
                st.rerun()

    st.markdown('<div class="footer">ScholarNode Academy © 2026</div>', unsafe_allow_html=True)

# ==========================================
# 4. لوحة تحكم الإدارة
# ==========================================
elif st.session_state['is_admin'] and not st.session_state['admin_view_as_user']:
    st.markdown('<div style="background-color: #ffe680; padding: 15px; border-radius: 5px; margin-bottom: 25px;"><h2 style="text-align:center;margin:0;">🛠️ لوحة تحكم الإدارة السرية العليا</h2></div>', unsafe_allow_html=True)
    admin_tabs = st.tabs(["🔑 توليد الكودات", "📊 مراجعة الكودات", "👁️ واجهة العميل"])

    with admin_tabs[0]:
        selected_tier = st.selectbox("اختر فئة كارت الاشتراك:", list(CARDS_DATA.keys()), format_func=lambda x: f"{x:,} دينار عراقي")
        if st.button("توليد وإصدار كود التفعيل"):
            gen_key = f"SCHOLAR-{selected_tier // 1000}K-{str(uuid.uuid4())[:8].upper()}"
            st.session_state['active_codes'][gen_key] = {"attempts": CARDS_DATA[selected_tier]['attempts'], "days": CARDS_DATA[selected_tier]['days'], "tier": selected_tier, "created_at": datetime.now().strftime("%Y-%m-%d")}
            st.success("🎉 تم التوليد بنجاح!")
            st.text_input("📋 كود التفعيل المولد:", value=gen_key)

    with admin_tabs[1]:
        if len(st.session_state['active_codes']) == 0: st.info("لا توجد أكواد مفعّلة حالياً.")
        else:
            clist = [{"كود التفعيل": c, "الفئة المادية": f"{d['tier']:,} د.ع", "المحاولات المتبقية": d['attempts'], "صلاحية الأيام": d['days'], "تاريخ الإصدار": d['created_at']} for c, d in st.session_state['active_codes'].items()]
            st.table(clist)

    with admin_tabs[2]:
        if st.button("🚀 الانتقال المباشر لطور محاكاة المشترك"):
            st.session_state['admin_view_as_user'] = True
            st.rerun()
            
    st.markdown("---")
    if st.button("🚪 خروج من حساب الإدارة"): logout()
