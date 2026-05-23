import streamlit as st
import streamlit.components.v1 as components
import uuid
from datetime import datetime, timedelta
import math
from openai import OpenAI

# مكتبات معالجة وقراءة نصوص الملفات المرفوعة حقيقياً
import pypdf       # لقراءة ملفات PDF
import docx        # لقراءة ملفات Word

# ==========================================
# 1. إعدادات الصفحة والتهيئة المبدئية
# ==========================================
st.set_page_config(
    page_title="ScholarNode Academy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استدعاء العميل وربطه بمفتاحك السري
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

CUSTOM_CSS = """
<style>
    .header-box {
        background-color: #0056b3;
        border: 3px solid #ffcc00;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-bottom: 25px;
    }
    .header-box h1 {
        color: #000000 !important;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        margin: 0;
    }
    .footer {
        text-align: center;
        padding: 20px;
        font-size: 0.9em;
        color: #888888;
        border-top: 1px solid #ddd;
        margin-top: 50px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# قاعدة بيانات الـ Session State
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
        status_text.text(f"جاري المعالجة الذكية عبر سيرفرات OpenAI... {percent_complete}%")
    status_text.empty()
    progress_bar.empty()

def render_cards_table():
    html_table = """
    <style>
        .styled-table { width: 100%; border-collapse: collapse; font-size: 14px; text-align: center; direction: rtl; }
        .styled-table th { background-color: #e6f2ff; color: #003366; padding: 10px; border: 1px solid #ffe680; }
        .styled-table td { padding: 10px; border: 1px solid #ffe680; }
    </style>
    <table class="styled-table">
        <thead><tr><th>فئة الكارت (دينار عراقي)</th><th>رصيد المحاولات</th><th>الصلاحية</th></tr></thead>
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

# ==========================================
# 2. الواجهة الرئيسية (قبل تسجيل الدخول)
# ==========================================
if not st.session_state['logged_in'] and not st.session_state['is_admin']:
    st.markdown('<div class="header-box"><h1>منصة التعليم الأكاديمية (ScholarNode)</h1></div>', unsafe_allow_html=True)
    col_main, col_payment = st.columns([5, 3], gap="large")
    
    with col_main:
        st.subheader("🔒 الدخول الآمن للمنصة")
        show_code = st.checkbox("👁️ إظهار الكود المدخل")
        input_code = st.text_input("ادخل كود التفعيل", type="default" if show_code else "password", value=st.session_state['typed_code'], key="login_input_field")
        st.session_state['typed_code'] = input_code

        if st.button("دخول المنصة", use_container_width=True):
            cleaned_code = st.session_state['typed_code'].strip()
            if cleaned_code == st.session_state['admin_password']:
                st.session_state['is_admin'] = True
                st.rerun()
            elif cleaned_code in st.session_state['active_codes']:
                if st.session_state['active_codes'][cleaned_code]['attempts'] <= 0:
                    st.error("❌ عذراً، هذا الكود انتهى رصيده.")
                else:
                    st.session_state['logged_in'] = True
                    st.session_state['current_user_code'] = cleaned_code
                    st.rerun()
            else:
                st.error("⚠️ الكود غير صحيح.")

        st.write("---")
        render_cards_table()

    with col_payment:
        st.markdown("""
        <div style="background-color: rgba(255, 230, 128, 0.15); border-right: 5px solid #ffcc00; padding: 20px; border-radius: 5px;">
            <h4 style="color: #0056b3; margin-top:0;">💳 معلومات الدفع والاشتراك</h4>
            <b>حساب الماستر كارد الرافدين:</b><br><code>8369719342</code><br><br>
            <b>الاسم:</b><br><code>HAYDER Z. JASIM</code><br><br>
            <b>الدعم الفني:</b><br><code>07879974395</code>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 3. واجهة المستخدم بعد تسجيل الدخول
# ==========================================
elif st.session_state['logged_in'] or (st.session_state['is_admin'] and st.session_state['admin_view_as_user']):
    current_code = st.session_state['current_user_code'] if st.session_state['logged_in'] else "ADMIN-PREVIEW"
    user_info = st.session_state['active_codes'].get(current_code, {"attempts": 999, "days": 30, "tier": 10000, "created_at": datetime.now().strftime("%Y-%m-%d")})
    
    st.markdown(f'<div style="background-color: #e6f2ff; border-left: 5px solid #0056b3; padding: 15px; border-radius: 5px; margin-bottom: 20px;"><h3>👋 مرحباً بك في ScholarNode</h3><p>الكود النشط: <b>{current_code}</b> | المتبقي: <b>{user_info["attempts"]} محاولة</b></p></div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 📋 معلومات الاشتراك")
        st.info(f"**المحاولات المتبقية:** {user_info['attempts']}")
        if st.session_state['is_admin']:
            if st.button("🔙 العودة إلى لوحة الإدارة"):
                st.session_state['admin_view_as_user'] = False
                st.rerun()
        else:
            st.button("🚪 تسجيل الخروج", on_click=logout)

    # دالات قراءة الملفات الآمنة
    def read_pdf(file):
        try:
            pdf_reader = pypdf.PdfReader(file)
            return "".join([page.extract_text() or "" for page in pdf_reader.pages[:15]])
        except: return ""

    def read_docx(file):
        try:
            doc = docx.Document(file)
            return "\n".join([p.text for p in doc.paragraphs])
        except: return ""

    tabs = st.tabs([
        "📖 معاينة ومناقشة المستند", "🔍 المراجعة الأكاديمية والنقد", 
        "📝 الترجمة الأكاديمية الاحترافية", "⚖️ الترجمة القانونية للمستندات", 
        "🎨 توليد الصور والمخططات", "🎬 إنشاء فيديو قصير", 
        "🖼️ توضيح وتحسين الصور", "🎙️ توليد الصوت الذكي", "🤖 المستشار الذكي المفتوح"
    ])

    # ---- التبويب 1 ----
    with tabs[0]:
        st.header("📖 معاينة ومناقشة المستند")
        # صندوق رفع موحد وصريح لمنع التعارض الجذري وبدون كتابة صيغ مكررة في التسمية
        uploaded_file1 = st.file_uploader("قم بسحب وإفلات ملف البحث هنا (PDF أو DOCX)", type=["pdf", "docx"], key="file_tab1")
        active_text1 = ""
        if uploaded_file1:
            active_text1 = read_pdf(uploaded_file1) if uploaded_file1.name.endswith('.pdf') else read_docx(uploaded_file1)
            if active_text1: st.success("✔️ تم تحميل وقراءة الملف بنجاح.")
            
        user_query = st.text_input("اسأل عن أي جزئية في الملف:", key="q_t1")
        if st.button("تحليل ومناقشة الملف", key="b_t1"):
            if active_text1 and user_query.strip():
                simulate_processing()
                try:
                    res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": "مساعد أكاديمي."}, {"role": "user", "content": f"{active_text1}\n\nالسؤال:\n{user_query}"}])
                    if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= 1
                    st.write(res.choices[0].message.content)
                except Exception as e: st.error(f"خطأ: {e}")

    # ---- التبويب 2 ----
    with tabs[1]:
        st.header("🔍 المراجعة الأكاديمية والنقدية")
        uploaded_file2 = st.file_uploader("قم برفع المستند للنقد العلمي (PDF أو DOCX)", type=["pdf", "docx"], key="file_tab2")
        active_text2 = ""
        if uploaded_file2:
            active_text2 = read_pdf(uploaded_file2) if uploaded_file2.name.endswith('.pdf') else read_docx(uploaded_file2)
        if st.button("البدء بالنقد الأكاديمي", key="b_t2") and active_text2:
            simulate_processing()
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": "بروفيسور محكم لأبحاث علمية."}, {"role": "user", "content": active_text2}])
            if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= 5
            st.write(res.choices[0].message.content)

    # ---- التبويب 3 ----
    with tabs[2]:
        st.header("📝 الترجمة الأكاديمية الاحترافية")
        uploaded_file3 = st.file_uploader("رفع ملف الترجمة الأكاديمية (PDF أو DOCX)", type=["pdf", "docx"], key="file_tab3")
        target_lang = st.selectbox("اختر اللغة:", ["العربية", "English"], key="lang_t3")
        active_text3 = ""
        if uploaded_file3:
            active_text3 = read_pdf(uploaded_file3) if uploaded_file3.name.endswith('.pdf') else read_docx(uploaded_file3)
        if st.button("تنفيذ الترجمة الأكاديمية", key="b_t3") and active_text3:
            simulate_processing()
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": f"مترجم أكاديمي إلى {target_lang}."}, {"role": "user", "content": active_text3[:4000]}])
            if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= 3
            st.write(res.choices[0].message.content)

    # ---- التبويب 4 ----
    with tabs[3]:
        st.header("⚖️ ترجمة المستندات ترجمة قانونية")
        uploaded_file4 = st.file_uploader("رفع الوثيقة الرسمية (PDF أو DOCX)", type=["pdf", "docx"], key="file_tab4")
        legal_entity = st.text_input("الجهة الموجه لها:", key="ent_t4")
        active_text4 = ""
        if uploaded_file4:
            active_text4 = read_pdf(uploaded_file4) if uploaded_file4.name.endswith('.pdf') else read_docx(uploaded_file4)
        if st.button("بدء الترجمة القانونية", key="b_t4") and active_text4:
            simulate_processing()
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": f"مترجم قانوني محلف موجه إلى {legal_entity}."}, {"role": "user", "content": active_text4[:4000]}])
            if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= 5
            st.write(res.choices[0].message.content)

    # ---- التبويب 5 ----
    with tabs[4]:
        st.header("🎨 توليد الصور والمخططات")
        image_prompt = st.text_area("أدخل الوصف:", key="p_t5")
        if st.button("توليد المخطط", key="b_t5") and image_prompt.strip():
            simulate_processing()
            try:
                res = client.images.generate(model="dall-e-3", prompt=image_prompt, n=1, size="1024x1024")
                if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= 5
                st.image(res.data[0].url)
            except Exception as e: st.error(f"خطأ: {e}")

    # ---- التبويب 6 ----
    with tabs[5]:
        st.header("🎬 إنشاء فيديو قصير")
        st.info("واجهة الفيديو تعمل في وضعها المحاكي حالياً لحين إطلاق Sora API بشكل عام.")

    # ---- التبويب 7 ----
    with tabs[6]:
        st.header("🖼️ معالجة وتوضيح الصور")
        img_file7 = st.file_uploader("تحميل صورة المخطط", type=["png", "jpg", "jpeg"], key="img_tab7")
        if img_file7: st.image(img_file7, caption="تم التقاط الصورة وهي جاهزة للمعالجة.")

    # ---- التبويب 8 ----
    with tabs[7]:
        st.header("🎙️ توليد الصوت الذكي (TTS)")
        audio_text = st.text_area("اكتب النص:", key="txt_t8")
        audio_voice = st.selectbox("خامة الصوت:", ["onyx", "nova"], key="v_t8")
        if st.button("توليد الصوت", key="b_t8") and audio_text.strip():
            simulate_processing()
            try:
                res = client.audio.speech.create(model="tts-1", voice=audio_voice, input=audio_text)
                with open("temp_output.mp3", "wb") as f: f.write(res.content)
                if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= 5
                st.audio("temp_output.mp3")
            except Exception as e: st.error(f"خطأ: {e}")

    # ---- التبويب 9 ----
    with tabs[8]:
        st.header("🤖 المستشار الذكي المفتوح")
        st.caption("💬 واجهة حرة ومباشرة.")
        advisor_query = st.text_area("اطرح سؤالك الأكاديمي:", key="q_t9")
        if st.button("إرسال الاستشارة", key="b_t9") and advisor_query.strip():
            simulate_processing()
            try:
                res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": "بروفيسور ومستشار أكاديمي خبير."}, {"role": "user", "content": advisor_query}])
                words = len(advisor_query.split()) + len(res.choices[0].message.content.split())
                cost = math.ceil(words / 600)
                if not st.session_state['is_admin']: st.session_state['active_codes'][current_code]['attempts'] -= cost
                st.write(res.choices[0].message.content)
                st.rerun()
            except Exception as e: st.error(f"خطأ: {e}")

# ==========================================
# 4. لوحة الإدارة
# ==========================================
elif st.session_state['is_admin'] and not st.session_state['admin_view_as_user']:
    st.markdown('<div style="background-color: #ffe680; padding: 15px; border-radius: 5px; margin-bottom: 25px;"><h2 style="text-align:center;margin:0;">🛠️ لوحة تحكم الإدارة العليا</h2></div>', unsafe_allow_html=True)
    admin_tabs = st.tabs(["🔑 توليد الكودات", "📊 مراجعة الكودات", "👁️ واجهة العميل"])

    with admin_tabs[0]:
        selected_tier = st.selectbox("اختر فئة كارت الاشتراك:", list(CARDS_DATA.keys()))
        if st.button("توليد وإصدار كود التفعيل"):
            gen_key = f"SCHOLAR-{selected_tier // 1000}K-{str(uuid.uuid4())[:8].upper()}"
            st.session_state['active_codes'][gen_key] = {"attempts": CARDS_DATA[selected_tier]['attempts'], "days": CARDS_DATA[selected_tier]['days'], "tier": selected_tier, "created_at": datetime.now().strftime("%Y-%m-%d")}
            st.success(f"🎉 تم التوليد بنجاح!")
            st.text_input("كود التفعيل:", value=gen_key)

    with admin_tabs[1]:
        if st.session_state['active_codes']:
            st.table([{"الكود": k, "الفئة": f"{v['tier']:,} د.ع", "المحاولات": v['attempts'], "الأيام": v['days']} for k, v in st.session_state['active_codes'].items()])

    with admin_tabs[2]:
        if st.button("🚀 الانتقال لطور محاكاة المشترك"):
            st.session_state['admin_view_as_user'] = True
            st.rerun()
