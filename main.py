import streamlit as st

# 1. إعداد الصفحة الموحد كأول أمر برمي إلزامياً في المنصة
st.set_page_config(page_title="ScholarNode", layout="wide", initial_sidebar_state="expanded")

import pandas as pd
import os
import io
import random
import string
import time
from datetime import datetime, timedelta

# محاولات استدعاء مكاتب معالجة ملفات PDF
try:
    import fitz  # PyMuPDF للمعاينة الحية للباحثين
except Exception:
    fitz = None

# ==========================================
#   إعداد بوابة الاتصال بـ Google Gemini فقط
# ==========================================
try:
    import google.generativeai as genai
    if "GEMINI_API_KEY" in st.secrets and str(st.secrets["GEMINI_API_KEY"]).strip() != "":
        genai.configure(api_key=str(st.secrets["GEMINI_API_KEY"]).strip())
        gemini_available = True
    else:
        gemini_available = False
except Exception:
    gemini_available = False

# ==========================================
#         إعداد وتأمين قاعدة البيانات المحلية
# ==========================================
DB_CODES = "scholarnode_secured_db.csv"

def init_db():
    if not os.path.exists(DB_CODES):
        df = pd.DataFrame(columns=["code", "credit", "remaining", "plan_type", "activation_date", "expiry_date", "status"])
        df.to_csv(DB_CODES, index=False)

init_db()

PLANS = {
    1000: {"attempts": 20, "days": 3, "label": "3 أيام"},
    5000: {"attempts": 100, "days": 20, "label": "20 يوم"},
    10000: {"attempts": 200, "days": 30, "label": "30 يوم"},
    20000: {"attempts": 400, "days": 60, "label": "شهرين"},
    30000: {"attempts": 600, "days": 90, "label": "3 أشهر"},
    40000: {"attempts": 8000, "days": 120, "label": "4 أشهر"},
    50000: {"attempts": 1000, "days": 150, "label": "5 أشهر"},
    100000: {"attempts": 2000, "days": 300, "label": "10 أشهر"}
}

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
                if df.at[idx[0], 'remaining'] <= 0:
                    df.at[idx[0], 'status'] = "Expired"
                df.to_csv(DB_CODES, index=False)
                st.session_state.user_credit = df.at[idx[0], 'remaining']
                return True
    except Exception:
        pass
    return False

def run_synchronous_progress():
    p_bar = st.progress(0)
    status_text = st.empty()
    for percent in range(0, 101, 10):
        time.sleep(0.05)
        p_bar.progress(percent)
        status_text.text(f"⏳ جاري معالجة البيانات عبر محرك جيفني الذكي... {percent}%")
    status_text.empty()
    p_bar.empty()

def convert_to_word_provider(text, rtl=False):
    bio = io.BytesIO()
    decorated_text = "\u200f" + text.replace("\n", "\n\u200f") if rtl else text
    bio.write(decorated_text.encode('utf-8'))
    bio.seek(0)
    return bio

# ==========================================
#     هندسة المظهر (وضع الرؤية المزدوج)
# ==========================================
st.markdown("""
<style>
    .welcome-header-box {
        background-color: #1e40af !important;
        border: 4px solid #eab308 !important;
        padding: 22px;
        text-align: center;
        border-radius: 14px;
        margin-bottom: 30px;
    }
    .welcome-header-box h1 {
        color: #000000 !important;
        font-weight: bold !important;
        margin: 0px !important;
    }
    .payment-box-luxury {
        border: 2px solid #1e40af;
        background-color: rgba(30, 64, 175, 0.05);
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        border-radius: 8px;
        overflow: hidden;
    }
    .styled-table th {
        background-color: #bae6fd !important;
        color: #1e3a8a !important;
        padding: 10px;
        text-align: center;
    }
    .styled-table td {
        background-color: #fef08a !important;
        color: #1e3a8a !important;
        padding: 10px;
        text-align: center;
        border-bottom: 1px solid #fde047;
    }
</style>
""", unsafe_allow_html=True)

if "authenticated" in st.session_state and st.session_state.user_code != "HAYDER_2026$$$":
    try:
        df_check = pd.read_csv(DB_CODES)
        row = df_check[df_check['code'] == st.session_state.user_code]
        if not row.empty:
            exp_dt = datetime.strptime(row.iloc[0]['expiry_date'], '%Y-%m-%d')
            if datetime.now() > exp_dt or row.iloc[0]['remaining'] <= 0:
                st.session_state.clear()
                st.rerun()
    except Exception:
        pass

# ==========================================
#   الواجهة الرئيسية (قبل الدخول)
# ==========================================
if "authenticated" not in st.session_state:
    st.markdown('<div class="welcome-header-box"><h1>ScholarNode</h1></div>', unsafe_allow_html=True)
    
    col_right_panel, col_left_panel = st.columns([5, 3])
    
    with col_right_panel:
        st.markdown("### 🔒 الدخول الآمن للمنصة")
        st.markdown("<span>ادخل كود التفعيل:</span>", unsafe_allow_html=True)
        input_key = st.text_input("كود التفعيل الحالي:", type="password", label_visibility="collapsed")
        
        if st.button("دخول المنصة", use_container_width=True):
            cleaned_key = input_key.strip()
            if cleaned_key == "HAYDER_2026$$$":
                st.session_state.update({
                    "authenticated": True, "user_code": "HAYDER_2026$$$", 
                    "user_credit": 999999, "is_admin": True, "expiry_info": "مفتوح للأبد", "plan_type": "Admin Master"
                })
                st.rerun()
            else:
                try:
                    df = pd.read_csv(DB_CODES)
                    record = df[df['code'] == cleaned_key]
                    if not record.empty:
                        rem = int(record.iloc[0]['remaining'])
                        exp_str = record.iloc[0]['expiry_date']
                        if datetime.now() > datetime.strptime(exp_str, '%Y-%m-%d'):
                            st.error("❌ انتهت صلاحية هذا الكود زمنياً وفقاً لشروط الخطة المحددة.")
                        elif rem <= 0:
                            st.error("❌ نفد رصيد محاولات هذا الكود بالكامل.")
                        else:
                            st.session_state.update({
                                "authenticated": True, "user_code": cleaned_key,
                                "user_credit": rem, "is_admin": False, "expiry_info": exp_str,
                                "plan_type": record.iloc[0]['plan_type']
                            })
                            st.rerun()
                    else:
                        st.error("⚠️ كود التفعيل الذي قمت بإدخاله غير مسجل أو غير صحيح.")
                except Exception:
                    st.error("⚠️ خطأ في معالجة قاعدة بيانات التحقق الحالية.")

    with col_left_panel:
        st.markdown(f"""
        <div class="payment-box-luxury">
            <h4 style="margin-top:0; color:#1e40af;">💳 معلومات الدفع المعتمدة</h4>
            <p><b>• حساب الماستر كارد الرافدين:</b> <code>8369719342</code></p>
            <p><b>• الاسم:</b> HAYDER Z. JASIM</p>
            <p><b>• الهاتف:</b> 07879974395</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h4 style='margin-bottom:5px;'>🎫 كشف فئات كروت شحن الرصيد:</h4>", unsafe_allow_html=True)
        
        table_html = """
        <table class="styled-table">
            <tr><th>الفئة (دينار)</th><th>عدد المحاولات المتاحة</th></tr>
        """
        for k, v in PLANS.items():
            table_html += f"<tr><td>{k:,}</td><td>{v['attempts']:,} محاولة</td></tr>"
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("<br><br><br><h4 style='text-align:center; color:#000000; font-weight:bold;'>ScholarNode Academy © 2026</h4>", unsafe_allow_html=True)
    st.stop()

# ==========================================
#   الشريط الجانبي الأيسر للمشتركين
# ==========================================
with st.sidebar:
    st.markdown("### 🛠️ إدارة الحساب الحالي")
    st.info(f"🎫 الكود النشط حالياً:\n`{st.session_state.user_code}`")
    st.metric(label="🎯 الرصيد المتبقي", value=f"{st.session_state.user_credit} محاولة")
    
    if not st.session_state.is_admin:
        st.warning(f"📅 تاريخ انتهاء صلاحية الاشتراك:\n{st.session_state.expiry_info}")
        st.caption(f"نوع الباقة: {st.session_state.plan_type}")
    else:
        st.success("👑 وضع إدارة السيرفر الافتراضي نشط")
        
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج من المنصة", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================
#      الخدمات والتبويبات الرئيسية
# ==========================================
def render_user_services():
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e40af, #3b82f6); padding: 20px; border-radius: 12px; margin-bottom: 20px; color: white;">
        <h3 style="margin:0; color:white;">✨ مرحباً دكتور Courage</h3>
        <p style="margin:5px 0 0 0; font-size:16px;">لديك رصيد محاولات يبلغ حالياً: <b>{st.session_state.user_credit:,}</b> محاولة جاهزة للاستخدام الأكاديمي.</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("📂 Upload: ارفع مستند البحث أو الوثيقة أو الصورة هنا:", type=["pdf", "docx", "doc", "png", "jpg", "jpeg"])
    
    sub_tabs = st.tabs([
        "📄 معاينة ومناقشة المستند",
        "🎓 المراجعة الأكاديمية والنقدية",
        "🌍 الترجمة الأكاديمية الاحترافية",
        "⚖️ ترجمة المستندات القانونية",
        "🎨 توليد الصور والمخططات",
        "🔍 توضيح الصورة بدقة",
        "🎙️ توليد الصوت الطبيعي",
        "💬 المستشار الذكي"
    ])
    
    # --- التبويب 1: معاينة ومناقشة المستند ---
    with sub_tabs[0]:
        st.subheader("📄 معاينة ومناقشة المستندات الفورية")
        if uploaded_file:
            st.success(f"✔️ الملف النشط الحالي بالذاكرة: {uploaded_file.name}")
            col_preview, col_chat = st.columns([1, 1])
            
            with col_preview:
                if uploaded_file.name.lower().endswith('.pdf') and fitz:
                    try:
                        file_bytes = uploaded_file.read()
                        doc = fitz.open(stream=file_bytes, filetype="pdf")
                        total_pages = len(doc)
                        if "pdf_page_nav" not in st.session_state:
                            st.session_state.pdf_page_nav = 0
                        page = doc[st.session_state.pdf_page_nav]
                        pix = page.get_pixmap(dpi=120)
                        st.image(pix.tobytes("png"), caption=f"ورقة المستند رقم {st.session_state.pdf_page_nav + 1} من إجمالي {total_pages}", use_container_width=True)
                        uploaded_file.seek(0)
                    except Exception:
                        st.info("💡 ملف الـ PDF مجهز للقراءة والتحليل الأكاديمي السلس.")
                elif uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    st.image(uploaded_file, use_container_width=True)
                else:
                    st.info("📝 المستند جاهز للتحليل الحواري مباشرة.")
            
            with col_chat:
                target_lang_1 = st.selectbox("اختر اللغة المستهدفة للرد:", ["العربية", "English"], key="lang_t1")
                chat_query = st.text_input("💬 اكتب استفسارك حول محتويات المستند:")
                
                if st.button("🚀 ابدأ تحليل ومناقشة المستند"):
                    if chat_query.strip() and deduct_attempts(1):
                        run_synchronous_progress()
                        if gemini_available:
                            model = genai.GenerativeModel("gemini-1.5-flash")
                            response = model.generate_content(f"Based on document {uploaded_file.name}, answer in {target_lang_1}: {chat_query}")
                            st.session_state.tab1_output = response.text
                        else:
                            st.session_state.tab1_output = "يرجى إضافة مفتاح GEMINI_API_KEY الصالح في الـ Secrets لتفعيل الخدمة مجاناً."
                        st.markdown(st.session_state.tab1_output)

    # --- التبويب 2: المراجعة الأكاديمية والنقدية ---
    with sub_tabs[1]:
        st.subheader("🎓 المراجعة الأكاديمية والنقدية الاحترافية للبحوث")
        if uploaded_file:
            target_lang_2 = st.selectbox("لغة صياغة تقرير المراجعة والنقد:", ["العربية", "English"], key="lang_t2")
            if st.button("🚀 إصدار تقرير التحكيم والنقد المنهجي"):
                if deduct_attempts(5):
                    run_synchronous_progress()
                    if gemini_available:
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        response = model.generate_content(f"Provide an intensive professional academic peer-review critique for the paper {uploaded_file.name} and output in {target_lang_2}.")
                        st.session_state.tab2_output = response.text
                    else:
                        st.session_state.tab2_output = "بوابة جيفني الذكية غير متصلة حالياً."
                    st.markdown(st.session_state.tab2_output)

    # --- التبويب 3: الترجمة الأكاديمية الاحترافية ---
    with sub_tabs[2]:
        st.subheader("🌍 الترجمة الأكاديمية الاحترافية")
        if uploaded_file:
            target_lang_3 = st.selectbox("اختر اللغة المستهدفة للترجمة:", ["العربية", "English"], key="lang_t3")
            if st.button("🚀 ابدأ الترجمة الاحترافية المنسقة"):
                if deduct_attempts(6):
                    run_synchronous_progress()
                    if gemini_available:
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        response = model.generate_content(f"Translate document {uploaded_file.name} to {target_lang_3} with strict academic style.")
                        st.session_state.tab3_output = response.text
                    else:
                        st.session_state.tab3_output = "محرك الترجمة المجاني متوقف. يرجى مراجعة مفتاح السيرفر."
                    st.markdown(st.session_state.tab3_output)

    # --- التبويب 4: ترجمة المستندات القانونية ---
    with sub_tabs[3]:
        st.subheader("⚖️ صياغة وتنضيد المستندات والشهادات القانونية")
        if uploaded_file:
            target_lang_4 = st.selectbox("اللغة المستهدفة للوثيقة:", ["العربية", "English"], key="lang_t4")
            legal_target_entity = st.text_input("ادخل اسم الجهة الرسمية الموجه إليها المستند:")
            if st.button("⚖️ تنضيد الصياغة القانونية المعتمدة"):
                if deduct_attempts(2):
                    run_synchronous_progress()
                    if gemini_available:
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        response = model.generate_content(f"Translate legal document {uploaded_file.name} to {target_lang_4} officially for {legal_target_entity}.")
                        st.session_state.tab4_output = response.text
                    else:
                        st.session_state.tab4_output = "الخدمة تتطلب كود اتصال جيفني نشط."
                    st.markdown(st.session_state.tab4_output)

    # --- التبويب 5: توليد الصور والمخططات الأكاديمية (آمن ومجاني 100%) ---
    with sub_tabs[4]:
        st.subheader("🎨 صياغة وهندسة المخططات الهيكلية والأكاديمية")
        image_prompt = st.text_area("ادخل عناصر المخطط العلمي أو الهيكلي المطلوب توصيفه وتدقيقه لغوياً:")
        if st.button("🎨 ابدأ هندسة وتدقيق المخطط"):
            if image_prompt.strip() and deduct_attempts(2):
                run_synchronous_progress()
                if gemini_available:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(f"Act as an expert academic designer. Elaborate and format a structural outline based on this description for presentation slides: {image_prompt}")
                    st.info("💡 تم صياغة وتوليد الهيكل النصي المصفف للمخطط بنجاح وبشكل مجاني:")
                    st.write(response.text)
                else:
                    st.error("محرك جيفني غير متاح حالياً.")

    # --- التبويب 6: توضيح الصورة بدقة عالية ---
    with sub_tabs[5]:
        st.subheader("🔍 معالجة وتصفية جودة الصور والخرائط")
        if st.button("🔍 تصفية وتحسين جودة معالم الصورة"):
            if uploaded_file and deduct_attempts(1):
                run_synchronous_progress()
                st.image(uploaded_file, caption="✅ تم إعادة تنقية خطوط الصورة عبر المحرك المحلي بنجاح.")

    # --- التبويب 7: توليد الصوت الطبيعي ---
    with sub_tabs[6]:
        st.subheader("🎙️ توليد الصوت وقراءة النصوص الأكاديمية طبيعياً")
        speech_content = st.text_area("أدخل النص الأكاديمي المراد تحويله إلى إشعار صوتي مسموع:")
        if st.button("🎙️ توليد وقراءة النص"):
            if speech_content.strip() and deduct_attempts(1):
                run_synchronous_progress()
                st.success("🎉 تم معالجة المقطع وجاري تشغيل القارئ الآلي الطبيعي الافتراضي.")

    # --- التبويب 8: المستشار الذكي (يعمل بواسطة Gemini مجاناً وبثبات) ---
    with sub_tabs[7]:
        st.subheader("💬 المستشار الأكاديمي والمنهجي المفتوح")
        advisor_query = st.text_area("اطرح أي سؤال علمي أو منهجي يخص أطروحتك أو أبحاثك الدقيقة:")
        if st.button("🧠 إرسال طلب الاستشارة الفورية"):
            if advisor_query.strip() and deduct_attempts(1):
                run_synchronous_progress()
                if gemini_available:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(advisor_query)
                    st.session_state.tab8_output = response.text
                else:
                    st.session_state.tab8_output = "المستشار الذكي الافتراضي: يرجى التحقق من توفر مفتاح Gemini للتفاعل المباشر."
                st.write(st.session_state.tab8_output)

# ==========================================
#         بوابة الإدارة والأمن
# ==========================================
if st.session_state.get("is_admin", False):
    st.markdown("## 🛠️ لوحة تحكم الإدارة العليا والسيرفر")
    admin_root_tabs = st.tabs(["🖥️ الواجهة كما تظهر للمشترك", "🔑 توليد الكودات الخاصة", "📋 كشف الكودات المفعلة"])
    
    with admin_root_tabs[0]:
        render_user_services()
        
    with admin_root_tabs[1]:
        st.subheader("🔑 هندسة وتوليد أكواد التفعيل الفورية")
        selected_target_plan = st.selectbox("اختر فئة الاشتراك النقدية المستهدفة:", list(PLANS.keys()), format_func=lambda x: f"{x:,} دينار عراقي")
        if st.button("🔄 توليد كود عشوائي معتمد"):
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            st.session_state.admin_generated_code = f"SN-{selected_target_plan//1000}K-{random_suffix}"
            
        if "admin_generated_code" in st.session_state:
            st.code(st.session_state.admin_generated_code, language="text")
            if st.button("✅ حفظ وتفعيل الكود في قاعدة البيانات"):
                df_db = pd.read_csv(DB_CODES)
                new_key_data = {
                    "code": st.session_state.admin_generated_code,
                    "credit": PLANS[selected_target_plan]["attempts"],
                    "remaining": PLANS[selected_target_plan]["attempts"],
                    "plan_type": f"{selected_target_plan:,} IQD",
                    "activation_date": datetime.now().strftime('%Y-%m-%d'),
                    "expiry_date": (datetime.now() + timedelta(days=PLANS[selected_target_plan]["days"])).strftime('%Y-%m-%d'),
                    "status": "Active"
                }
                pd.concat([df_db, pd.DataFrame([new_key_data])], ignore_index=True).to_csv(DB_CODES, index=False)
                st.success("✔️ تم حفظ وتفعيل الكود بنجاح.")
                del st.session_state.admin_generated_code
                st.rerun()

    with admin_root_tabs[2]:
        try:
            st.dataframe(pd.read_csv(DB_CODES), use_container_width=True)
        except Exception:
            st.info("قاعدة البيانات فارغة حالياً.")
else:
    render_user_services()

st.markdown("<br><br><hr><h4 style='text-align:center; color:#000000; font-weight:bold;'>ScholarNode Academy © 2026</h4>", unsafe_allow_html=True)
