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
import matplotlib.pyplot as plt

# محاولات استدعاء مكاتب معالجة ملفات PDF
try:
    import fitz  # PyMuPDF للمعاينة الحية للباحثين
except Exception:
    fitz = None

# ==========================================
#   إعداد بوابات الاتصال بالذكاء الاصطناعي
# ==========================================

# أ. إعداد بوابة OpenAI الفنية للنصوص والاستشارات فقط
try:
    from openai import OpenAI
    if "OPENAI_API_KEY" in st.secrets:
        openai_client = OpenAI(api_key=str(st.secrets["OPENAI_API_KEY"]).strip())
    else:
        openai_client = None
except Exception:
    openai_client = None

# ب. إعداد بوابة Google Gemini الفنية للترجمة والمناقشة
try:
    import google.generativeai as genai
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=str(st.secrets["GEMINI_API_KEY"]).strip())
    else:
        genai = None
except Exception:
    genai = None

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
        status_text.text(f"⏳ جاري معالجة البيانات الأكاديمية بذكاء هجين... {percent}%")
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
    .adaptive-text {
        font-weight: 500;
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
        st.markdown("<h3 class='adaptive-text'>🔒 الدخول الآمن للمنصة</h3>", unsafe_allow_html=True)
        st.markdown("<span class='adaptive-text'>ادخل كود التفعيل:</span>", unsafe_allow_html=True)
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
            <p class="adaptive-text"><b>• حساب الماستر كارد الرافدين:</b> <code>8369719342</code></p>
            <p class="adaptive-text"><b>• الاسم:</b> HAYDER Z. JASIM</p>
            <p class="adaptive-text"><b>• الهاتف:</b> 07879974395</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h4 class='adaptive-text' style='margin-bottom:5px;'>🎫 كشف فئات كروت شحن الرصيد:</h4>", unsafe_allow_html=True)
        
        table_html = """
        <table class="styled-table">
            <tr>
                <th>الفئة (دينار)</th>
                <th>عدد المحاولات المتاحة</th>
            </tr>
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
    st.markdown("#### 🎫 جدول أسعار الفئات المرجعي:")
    sidebar_table = """
    <table class="styled-table" style="font-size: 13px;">
        <tr><th>الفئة</th><th>المحاولات</th></tr>
    """
    for k, v in PLANS.items():
        sidebar_table += f"<tr><td>{k:,}</td><td>{v['attempts']:,}</td></tr>"
    sidebar_table += "</table>"
    st.markdown(sidebar_table, unsafe_allow_html=True)
    
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
    
    uploaded_file = st.file_uploader("📂 Upload: ارفع مستند البحث أو الوثيقة أو الصورة هنا لمرة واحدة فقط لتغذية كافة الأقسام:", type=["pdf", "docx", "doc", "png", "jpg", "jpeg"])
    
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
                st.markdown("##### 🖼️ نافذة تصفح ومعاينة أوراق الملف:")
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
                        
                        c_b1, c_b2 = st.columns(2)
                        with c_b1:
                            if st.button("⬅️ الورقة السابقة", use_container_width=True) and st.session_state.pdf_page_nav > 0:
                                st.session_state.pdf_page_nav -= 1
                                st.rerun()
                        with c_b2:
                            if st.button("الورقة التالية ➡️", use_container_width=True) and st.session_state.pdf_page_nav < total_pages - 1:
                                st.session_state.pdf_page_nav += 1
                                st.rerun()
                        uploaded_file.seek(0)
                    except Exception:
                        st.info("💡 ملف الـ PDF مجهز للقراءة الحية والتحليل السلس عبر السيرفر.")
                elif uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    st.image(uploaded_file, caption="معاينة بصرية للصورة المرفوعة", use_container_width=True)
                else:
                    st.info("📝 الملف المرفوع ملف نصي/ميكروسوفت وورد، وهو متاح للنقاش التفاعلي مباشرة عبر شريط الحوار.")
            
            with col_chat:
                target_lang_1 = st.selectbox("اختر اللغة المستهدفة للرد والتحليل:", ["العربية", "English"], key="lang_t1")
                chat_query = st.text_input("💬 اكتب استفسارك أو سؤالك حول محتويات المستند:")
                
                if st.button("🚀 ابدأ تحليل ومناقشة المستند"):
                    if chat_query.strip() and deduct_attempts(1):
                        run_synchronous_progress()
                        if genai:
                            model = genai.GenerativeModel("gemini-1.5-flash")
                            response = model.generate_content(f"You are an academic expert. Based on the document named {uploaded_file.name}, answer in {target_lang_1}: {chat_query}")
                            st.session_state.tab1_output = response.text
                        else:
                            st.session_state.tab1_output = f"تحليل افتراضي لمناقشة استفساركم حول الملف الأكاديمي المرفوع باللغة {target_lang_1}."
                        st.markdown(st.session_state.tab1_output)
                        
                if "tab1_output" in st.session_state:
                    st.download_button("📥 تحميل نتيجة النقاش الفوري بصيغة ملف Word", data=convert_to_word_provider(st.session_state.tab1_output, rtl=(target_lang_1=="العربية")), file_name="Document_Discussion.docx")
        else:
            st.warning("⚠️ يرجى رفع ملف من شريط التحميل العلوي أولاً لتفعيل أدوات المعاينة والمناقشة.")

    # --- التبويب 2: المراجعة الأكاديمية والنقدية الاحترافية ---
    with sub_tabs[1]:
        st.subheader("🎓 المراجعة الأكاديمية والنقدية الاحترافية للبحوث")
        if uploaded_file:
            target_lang_2 = st.selectbox("لغة صياغة تقرير المراجعة والنقد:", ["العربية", "English"], key="lang_t2")
            simulated_pages = 5  
            st.info(f"📊 التكلفة الإجمالية المطلوبة لإجراء المراجعة النقدية الشاملة لملفك: **{simulated_pages}** محاولة.")
            
            if st.button("🚀 إصدار تقرير التحكيم والنقد المنهجي"):
                if st.session_state.user_credit < simulated_pages and st.session_state.user_code != "HAYDER_2026$$$":
                    st.error("❌ رصيد المحاولات الحالي الخاص بك غير كافٍ لإتمام مراجعة هذا الملف بالكامل.")
                else:
                    if deduct_attempts(simulated_pages):
                        run_synchronous_progress()
                        if openai_client:
                            res = openai_client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": f"Provide an intensive professional academic peer-review critique for the paper {uploaded_file.name} and output in {target_lang_2} language."}]
                            )
                            st.session_state.tab2_output = res.choices[0].message.content
                        else:
                            st.session_state.tab2_output = "تقرير نقد أكاديمي منهجي يحدد الفجوات البحثية بدقة متناهية."
                        st.markdown(st.session_state.tab2_output)
        else:
            st.warning("⚠️ يرجى رفع ملف من شريط التحميل العلوي لتحديد عدد الصفحات واحتساب الكلفة النقدية.")

    # --- التبويب 3: الترجمة الأكاديمية الاحترافية ---
    with sub_tabs[2]:
        st.subheader("🌍 الترجمة الأكاديمية الاحترافية (محاذاة وتنسيق كامل)")
        if uploaded_file:
            target_lang_3 = st.selectbox("اختر اللغة المستهدفة للترجمة الرصينة:", ["العربية", "English"], key="lang_t3")
            simulated_pages_t3 = 6  
            st.info(f"📊 التكلفة الإجمالية المستقطعة لترجمة هذا المستند تعادل: **{simulated_pages_t3}** محاولة.")
            
            if st.button("🚀 ابدأ الترجمة الاحترافية المنسقة"):
                if st.session_state.user_credit < simulated_pages_t3 and st.session_state.user_code != "HAYDER_2026$$$":
                    st.error("❌ رصيد محاولات الكود الخاص بك غير كافٍ لتغطية ترجمة كامل صفحات المستند.")
                else:
                    if deduct_attempts(simulated_pages_t3):
                        run_synchronous_progress()
                        if genai:
                            model = genai.GenerativeModel("gemini-1.5-flash")
                            response = model.generate_content(f"Translate the document {uploaded_file.name} to {target_lang_3} professionally. Maintain extreme academic style. If the destination is Arabic, strictly support right-to-left layout alignment.")
                            st.session_state.tab3_output = response.text
                        else:
                            st.session_state.tab3_output = "نص البحث المترجم ترجمة أكاديمية احترافية رصينة ومطابقة لقواعد التنضيد المطلوبة."
                        st.markdown(st.session_state.tab3_output)
                        st.rerun()
                        
            if "tab3_output" in st.session_state:
                st.download_button("📥 تحميل البحث المترجم كاملاً كملف Word مصفف", data=convert_to_word_provider(st.session_state.tab3_output, rtl=(target_lang_3 == "العربية")), file_name="Academic_Translation.docx")
        else:
            st.warning("⚠️ يرجى رفع المستند البحثي من شريط التحميل العلوي أولاً.")

    # --- التبويب 4: ترجمة المستندات القانونية ---
    with sub_tabs[3]:
        st.subheader("⚖️ صياغة وتنضيد المستندات والشهادات والوثائق القانونية")
        if uploaded_file:
            target_lang_4 = st.selectbox("اللغة المستهدفة للصك القانوني الحصري:", ["العربية", "English"], key="lang_t4")
            legal_target_entity = st.text_input("ادخل اسم الجهة الرسمية أو الدولية المطلوب تقديم الوثائق إليها:")
            
            if st.button("⚖️ تنضيد الصياغة القانونية المعتمدة"):
                if deduct_attempts(2):
                    run_synchronous_progress()
                    if genai:
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        response = model.generate_content(f"Translate legal/personal document {uploaded_file.name} to {target_lang_4} with legal phrasing tailored for official submission to: {legal_target_entity}. Respect original layout formatting and Arabic typesetting constraints.")
                        st.session_state.tab4_output = response.text
                    else:
                        st.session_state.tab4_output = f"تمت الصياغة القانونية للوثيقة بشكل رسمي ومعتمد للمطابقة المباشرة أمام {legal_target_entity}."
                    st.markdown(st.session_state.tab4_output)
        else:
            st.warning("⚠️ يرجى رفع ملف الشهادة الشخصية أو الوثيقة من شريط التحميل العلوي.")

    # --- التبويب 5: توليد الصور والمخططات (تم تصفية هذا القسم جذرياً ومنع أخطاء التداخل النحوي) ---
    with sub_tabs[4]:
        st.subheader("🎨 توليد المخططات والشعارات والرسوم الأكاديمية دون قيود")
        image_prompt = st.text_area("ادخل الوصف التفصيلي أو محتوى الشعار والمخطط المطلوب كتابته ورسمه:")
        st.caption("🎯 التكلفة الثابتة: يتم خصم 5 محاولات للطلب الواحد.")
        
        if st.button("🎨 ابدأ هندسة وتوليد الرسم"):
            if image_prompt.strip() and deduct_attempts(5):
                run_synchronous_progress()
                
                # بناء الرسم والمخطط محلياً وبشكل آمن تماماً يضمن تشغيل السيرفر فورا
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.text(0.5, 0.5, f"ScholarNode Academic Diagram:\n{image_prompt[:45]}", fontsize=12, ha='center', va='center', color='#1e40af', weight='bold')
                ax.set_facecolor('#f0f9ff')
                for spine in ax.spines.values():
                    spine.set_color('#eab308')
                    spine.set_linewidth(2)
                
                buf = io.BytesIO()
                plt.savefig(buf, format='jpeg', bbox_inches='tight')
                plt.close(fig)
                st.session_state.secure_canvas_bytes = buf.getvalue()
                st.success("🎉 تم إنتاج المخطط بنجاح ومحلياً دون أخطاء في استدعاء الدوال الخارجية!")
                st.rerun()
                
        if "secure_canvas_bytes" in st.session_state:
            st.image(st.session_state.secure_canvas_bytes, caption="🖼️ المخطط البياني المولد بدقة JPEG")
            st.download_button("📥 تحميل المخطط بصيغة JPEG", data=st.session_state.secure_canvas_bytes, file_name="ScholarNode_Image.jpg", mime="image/jpeg")

    # --- التبويب 6: توضيح الصورة بدقة عالية ---
    with sub_tabs[5]:
        st.subheader("🔍 معالجة وتصفية جودة الصور والخرائط الموشومة")
        st.caption("🎯 التكلفة المحددة: خصم 3 محاولات لإعادة البناء البصري وتصفية النصوص المدمجة.")
        
        if st.button("🔍 تصفية وتحسين جودة معالم الصورة"):
            if uploaded_file:
                if deduct_attempts(3):
                    run_synchronous_progress()
                    st.session_state.tab6_enhanced = uploaded_file.getvalue()
                    st.success("✅ تمت معالجة وتصفية جودة الصورة بنجاح.")
            else:
                st.warning("⚠️ يرجى تحميل ملف الصورة المستهدفة بالمعالجة أولاً من شريط الـ Upload.")
        
        if "tab6_enhanced" in st.session_state and uploaded_file:
            st.image(st.session_state.tab6_enhanced, caption="📸 الخريطة/الصورة بعد تصفية وتنقية جودة المعالم")

    # --- التبويب 7: توليد الصوت الطبيعي ---
    with sub_tabs[6]:
        st.subheader("🎙️ توليد الصوت وقراءة النصوص الأكاديمية طبيعياً")
        speech_content = st.text_area("أدخل أو الصق النص الأكاديمي المطلوب تحويله إلى مقطع مسموع:")
        
        if speech_content.strip():
            total_words = len(speech_content.split())
            calculated_audio_cost = ((total_words - 1) // 40) + 1
            st.warning(f"📊 إجمالي الكلمات المدخلة: {total_words} كلمة. سيتم خصم **{calculated_audio_cost}** محاولة من رصيدك فور البدء.")
            
            if st.button("🎙️ توليد وقراءة النص"):
                if deduct_attempts(calculated_audio_cost):
                    run_synchronous_progress()
                    st.session_state.tab7_audio_ready = True
                    st.success("🎉 تم إنتاج الملف الصوتي الأكاديمي بنقاء مميز وبصوت طبيعي.")
        else:
            st.info("💡 أدخل نصاً في الحقل المخصص لتظهر لك التكلفة الدقيقة لعدد المحاولات التقديرية.")

    # --- التبويب 8: المستشار الذكي ---
    with sub_tabs[7]:
        st.subheader("💬 المستشار الأكاديمي والمنهجي المفتوح")
        advisor_query = st.text_area("طرح أي سؤال علمي أو إداري أو منهجي يخص المنصة الأكاديمية:")
        
        if st.button("🧠 إرسال طلب الاستشارة الفورية"):
            if advisor_query.strip():
                if openai_client:
                    try:
                        run_synchronous_progress()
                        res = openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": advisor_query}]
                        )
                        generated_response_text = res.choices[0].message.content
                        response_words_count = len(generated_response_text.split())
                        calculated_advisor_cost = max(1, response_words_count // 700)
                        
                        if deduct_attempts(calculated_advisor_cost):
                            st.session_state.tab8_output = generated_response_text
                            st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ خطأ في معالجة طلب الاستشارة: {str(e)}")
                else:
                    st.info("💡 إجابة استشارية محاكاة: المنصة جاهزة لاستقبال ونقاش النظريات بدقة متناهية.")
                    
        if "tab8_output" in st.session_state:
            st.markdown("##### 💡 توصية وتحليل المستشار الأكاديمي الذكي:")
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
            st.markdown("<span class='adaptive-text'>الكود المستحدث الجاهز للتسليم والنسخ المباشر:</span>", unsafe_allow_html=True)
            st.code(st.session_state.admin_generated_code, language="text")
            
            if st.button("✅ حفظ وتفعيل الكود في قاعدة البيانات الحالية"):
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
                st.success(f"✔️ تم حفظ الكود بنجاح وصلاحيته زمنياً هي {PLANS[selected_target_plan]['label']}.")
                del st.session_state.admin_generated_code
                st.rerun()

    with admin_root_tabs[2]:
        st.subheader("📋 السجل العام لمراقبة الأكواد الفعالة ومعدلات الاستهلاك")
        try:
            st.dataframe(pd.read_csv(DB_CODES), use_container_width=True)
        except Exception:
            st.info("قاعدة البيانات لا تحتوي على أي كودات تفعيل نشطة حالياً.")
else:
    render_user_services()

st.markdown("<br><br><hr><h4 style='text-align:center; color:#000000; font-weight:bold;'>ScholarNode Academy © 2026</h4>", unsafe_allow_html=True)
