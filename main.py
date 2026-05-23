import streamlit as st
import streamlit.components.v1 as components
import uuid
from datetime import datetime, timedelta
import math
from openai import OpenAI

# محاولة استدعاء مكتبات القراءة بشكل آمن تماماً لا يسبب انهيار أداة الرفع
try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

# ==========================================
# 1. إعدادات الصفحة والتهيئة المبدئية والوضع المظلم
# ==========================================
st.set_page_config(
    page_title="ScholarNode Academy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استدعاء العميل وربطه بمفتاحك السري بشكل آمن تماماً عبر الـ Secrets
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("❌ خطأ: مفتاح OPENAI_API_KEY غير معرف في الـ Secrets الخاصة بـ Streamlit.")

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

# قاعدة بيانات ثابتة ومستقرة بداخل الـ Session State
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
        status_text.text(f"جاري المعالجة الذكية عبر سيرفرات OpenAI الفعّالة... {percent_complete}%")
    status_text.empty()
    progress_bar.empty()

def render_cards_table():
    html_table = """
    <style>
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            font-family: sans-serif;
            border-radius: 5px;
            overflow: hidden;
            direction: rtl;
            text-align: center;
        }
        .styled-table th {
            background-color: #e6f2ff;
            color: #003366;
            padding: 10px;
            border: 1px solid #ffe680;
        }
        .styled-table td {
            padding: 10px;
            border: 1px solid #ffe680;
        }
        .styled-table tr:nth-child(even) {
            background-color: #fffde6;
        }
    </style>
    <table class="styled-table">
        <thead>
            <tr>
                <th>فئة الكارت (دينار عراقي)</th>
                <th>رصيد المحاولات المتاحة</th>
                <th>فترة صلاحية الكود</th>
            </tr>
        </thead>
        <tbody>
    """
    for price, info in CARDS_DATA.items():
        html_table += f"""
            <tr>
                <td><b>{price:,} د.ع</b></td>
                <td>{info['attempts']} محاولة</td>
                <td>{info['days']} يوم</td>
            </tr>
        """
    html_table += "</tbody></table>"
    components.html(html_table, height=380, scrolling=True)

def logout():
    st.session_state['logged_in'] = False
    st.session_state['current_user_code'] = None
    st.session_state['is_admin'] = False
    st.session_state['admin_view_as_user'] = False
    st.session_state['typed_code'] = ""
    st.rerun()

# دالة مركزية موحدة ومحمية لقراءة الملفات في كافة التبويبات تمنع الانهيار
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        if uploaded_file.name.endswith('.pdf'):
            if not HAS_PYPDF:
                return "ERROR_NOT_INSTALLED"
            pdf_reader = pypdf.PdfReader(uploaded_file)
            return "".join([page.extract_text() or "" for page in pdf_reader.pages[:15]])
        else:
            if not HAS_DOCX:
                return "ERROR_NOT_INSTALLED"
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
    except Exception:
        return "ERROR_READING"

# ==========================================
# 2. الواجهة الرئيسية (قبل تسجيل الدخول)
# ==========================================
if not st.session_state['logged_in'] and not st.session_state['is_admin']:
    
    HEADER_HTML = """
    <div class="header-box">
        <h1>منصة التعليم الأكاديمية (ScholarNode)</h1>
    </div>
    """
    st.markdown(HEADER_HTML, unsafe_allow_html=True)
    
    col_main, col_payment = st.columns([5, 3], gap="large")
    
    with col_main:
        st.subheader("🔒 الدخول الآمن للمنصة")
        show_code = st.checkbox("👁️ إظهار الكود المدخل")
        
        input_code = st.text_input(
            "ادخل كود التفعيل", 
            type="default" if show_code else "password", 
            placeholder="مثال: SCHOLAR-XXXX-XXXX",
            value=st.session_state['typed_code'],
            key="login_input_field"
        )
        st.session_state['typed_code'] = input_code

        if st.button("دخول المنصة", use_container_width=True):
            cleaned_code = st.session_state['typed_code'].strip()
            
            if cleaned_code == st.session_state['admin_password']:
                st.session_state['is_admin'] = True
                st.success("تم الدخول بصفتك مديراً للنظام بنجاح.")
                st.rerun()
            
            elif cleaned_code in st.session_state['active_codes']:
                user_data = st.session_state['active_codes'][cleaned_code]
                if user_data['attempts'] <= 0:
                    st.error("❌ عذراً، هذا الكود غير فعال بسبب نفاد رصيد المحاولات بالكامل.")
                else:
                    st.session_state['logged_in'] = True
                    st.session_state['current_user_code'] = cleaned_code
                    st.success("تم الدخول الآمن بنجاح!")
                    st.rerun()
            else:
                st.error(f"⚠️ الكود غير فعال أو غير صحيح. تأكد من تطابق الكود المكتوب تماماً.")

        st.write("---")
        st.subheader("📊 فئات الاشتراكات والبطاقات المتوفرة")
        render_cards_table()

    with col_payment:
        PAYMENT_HTML = """
        <div style="background-color: rgba(255, 230, 128, 0.15); border-right: 5px solid #ffcc00; padding: 20px; border-radius: 5px;">
            <h4 style="color: #0056b3; margin-top:0;">💳 معلومات الدفع والاشتراك</h4>
            <p>لغرض تفعيل أو شراء كود تفعيل جديد، يرجى التحويل عبر المحفظة أدناه:</p>
            <hr style="border-color: #ffe680;">
            <b>حساب الماستر كارد الرافدين:</b><br>
            <code style="font-size:1.2em; color:#d9534f;">8369719342</code><br><br>
            <b>الاسم:</b><br>
            <code>HAYDER Z. JASIM</code><br><br>
            <b>الهاتف والدعم الفني:</b><br>
            <code>07879974395</code>
        </div>
        """
        st.markdown(PAYMENT_HTML, unsafe_allow_html=True)

    st.markdown('<div class="footer">ScholarNode Academy © 2026</div>', unsafe_allow_html=True)

# ==========================================
# 3. واجهة المستخدم بعد تسجيل الدخول
# ==========================================
elif st.session_state['logged_in'] or (st.session_state['is_admin'] and st.session_state['admin_view_as_user']):
    
    current_code = st.session_state['current_user_code'] if st.session_state['logged_in'] else "ADMIN-PREVIEW"
    if current_code in st.session_state['active_codes']:
        user_info = st.session_state['active_codes'][current_code]
    else:
        user_info = {"attempts": 999, "days": 30, "tier": 10000, "created_at": datetime.now().strftime("%Y-%m-%d")}
        
    creation_date = datetime.strptime(user_info['created_at'], "%Y-%m-%d")
    expiration_date = creation_date + timedelta(days=user_info['days'])
    formatted_exp_date = expiration_date.strftime("%Y-%m-%d")

    WELCOME_HTML = f"""
    <div style="background-color: #e6f2ff; border-left: 5px solid #0056b3; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="margin:0; color:#003366;">👋 مرحباً بك في ScholarNode</h3>
        <p style="margin:5px 0 0 0; font-size:1.1em;">كود الاشتراك النشط: <b>{current_code}</b> | <b>لديك رصيد محاولات يبلغ: <span style="color:#d9534f; font-size:1.2em;">{user_info['attempts']}</span> محاولة</b></p>
    </div>
    """
    st.markdown(WELCOME_HTML, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 📋 معلومات الاشتراك")
        st.info(f"**المحاولات المتبقية:** {user_info['attempts']} محاولة")
        st.info(f"**تاريخ انتهاء الصلاحية:** {formatted_exp_date}")
        st.warning(f"⚠️ تنبيه: ينتهي اشتراكك الحالي بتاريخ {formatted_exp_date}. يرجى التجديد قبل الموعد تجنباً لتعطيل الخدمة.")
        st.markdown("---")
        st.markdown("### 📊 جدول الكروت المعتمد")
        render_cards_table()
        st.markdown("---")
        
        if st.session_state['is_admin']:
            if st.button("🔙 العودة إلى لوحة الإدارة", use_container_width=True):
                st.session_state['admin_view_as_user'] = False
                st.rerun()
        else:
            if st.button("🚪 تسجيل الخروج", use_container_width=True, on_click=logout):
                st.success("تم تسجيل الخروج.")

    st.markdown("### 🛠️ الخدمات الأكاديمية المتطورة")

    tabs = st.tabs([
        "📖 معاينة ومناقشة المستند", 
        "🔍 المراجعة الأكاديمية والنقد", 
        "📝 الترجمة الأكاديمية الاحترافية", 
        "⚖️ الترجمة القانونية للمستندات", 
        "🎨 توليد الصور والمخططات", 
        "🎬 إنشاء فيديو قصير", 
        "🖼️ توضيح وتحسين الصور", 
        "🖼️ توليد الصوت الذكي", 
        "🤖 المستشار الذكي المفتوح"
    ])

    # ---- التبويب 1: معاينة ومناقشة المستند ----
    with tabs[0]:
        st.header("📖 معاينة ومناقشة المستند")
        file_tab1 = st.file_uploader("📥 تحميل ملف البحث بصيغة (PDF أو Word)", type=["pdf", "docx"], key="secure_uploader_t1")
        
        active_text1 = ""
        if file_tab1 is not None:
            res = extract_text_from_file(file_tab1)
            if res == "ERROR_NOT_INSTALLED":
                st.error("⚠️ حزم القراءة غير مثبتة بالسيرفر بعد.")
            elif res == "ERROR_READING":
                st.error("⚠️ خطأ في بنية الملف، يرجى إعادة رفعه.")
            else:
                active_text1 = res
                st.success(f"✔️ تم قراءة الملف ({file_tab1.name}) بنجاح وهو جاهز للتحليل!")

        user_query = st.text_input("اسأل الذكاء الاصطناعي عن أي جزئية في الملف المرفوع:", placeholder="اكتب سؤالك هنا...", key="query_t1")
        if st.button("تحليل ومناقشة الملف عبر GPT", key="btn_t1"):
            if not active_text1:
                st.warning("⚠️ يرجى رفع ملف أولاً والتأكد من صحته.")
            elif user_query.strip() == "":
                st.warning("⚠️ يرجى كتابة سؤالك أولاً.")
            elif user_info['attempts'] < 1:
                st.error("❌ رصيدك غير كافٍ.")
            else:
                simulate_processing()
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "أنت مساعد أكاديمي تجيب على أسئلة المستخدم بناءً على محتوى الملف المرفق بدقة علمية بالغة وبنفس لغة السؤال."},
                            {"role": "user", "content": f"محتوى الملف:\n{active_text1}\n\nسؤال المستخدم:\n{user_query}"}
                        ]
                    )
                    if not st.session_state['is_admin']:
                        st.session_state['active_codes'][current_code]['attempts'] -= 1
                    st.markdown("### 🟢 الإجابة والتحليل الحقيقي للنص:")
                    st.write(response.choices[0].message.content)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء الاتصال بالسيرفر: {e}")

    # ---- التبويب 2: المراجعة الأكاديمية والنقدية ----
    with tabs[1]:
        st.header("🔍 المراجعة الأكاديمية والنقدية الاحترافية")
        file_tab2 = st.file_uploader("📥 رفع المستند للنقد العلمي (PDF أو Word)", type=["pdf", "docx"], key="secure_uploader_t2")
            
        active_text2 = ""
        if file_tab2 is not None:
            res = extract_text_from_file(file_tab2)
            if "ERROR" not in res:
                active_text2 = res
                st.success(f"✔️ تم قراءة ({file_tab2.name}) بنجاح للنقد.")
            else:
                st.error("⚠️ فشل قراءة الملف.")
            
        st.markdown("💰 التكلفة الإجمالية للاجراء: **5 محاولات**.")
        if st.button("البدء بالمراجعة والنقد الأكاديمي الشامل", key="btn_t2"):
            if not active_text2:
                st.warning("⚠️ يرجى رفع الملف أولاً.")
            elif user_info['attempts'] < 5:
                st.error("❌ رصيدك الحالي غير كافٍ.")
            else:
                simulate_processing()
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "أنت بروفيسور محكم للأبحاث العلمية. قم بتقديم نقد منهجي، أكاديمي، وبنيوي مفصل للنص المرفق واقترح نقاط التحسين باللغة العربية."},
                            {"role": "user", "content": active_text2}
                        ]
                    )
                    if not st.session_state['is_admin']:
                        st.session_state['active_codes'][current_code]['attempts'] -= 5
                    st.markdown("### 🟢 تقرير النقد والمراجعة الأكاديمية المولد:")
                    st.write(response.choices[0].message.content)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ حدث خطأ: {e}")

    # ---- التبويب 3: الترجمة الأكاديمية الاحترافية ----
    with tabs[2]:
        st.header("📝 الترجمة الأكاديمية الاحترافية")
        file_tab3 = st.file_uploader("📥 رفع ملف الترجمة الأكاديمية (PDF أو Word)", type=["pdf", "docx"], key="secure_uploader_t3")
            
        active_text3 = ""
        if file_tab3 is not None:
            res = extract_text_from_file(file_tab3)
            if "ERROR" not in res:
                active_text3 = res
                st.success(f"✔️ تم قراءة ({file_tab3.name}) بنجاح للترجمة الأكاديمية.")
            else:
                st.error("⚠️ فشل قراءة الملف.")
            
        st.markdown("💰 التكلفة: **3 محاولات**.")
        target_lang_tab3 = st.selectbox("اختر اللغة المستهدفة:", ["العربية", "English"], key="lang_t3")
        if st.button("تنفيذ الترجمة الأكاديمية الفائقة", key="btn_t3"):
            if not active_text3:
                st.warning("⚠️ يرجى رفع المستند المراد ترجمته.")
            elif user_info['attempts'] < 3:
                st.error("❌ رصيدك غير كافٍ.")
            else:
                simulate_processing()
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": f"ترجم النص التالي ترجمة أكاديمية احترافية دقيقة مع الحفاظ على المصطلحات العلمية الرصينة والسياق الأكاديمي إلى لغة: {target_lang_tab3}."},
                            {"role": "user", "content": active_text3[:4000]}
                        ]
                    )
                    if not st.session_state['is_admin']:
                        st.session_state['active_codes'][current_code]['attempts'] -= 3
                    st.markdown("### 🟢 النص المترجم أكاديمياً:")
                    st.write(response.choices[0].message.content)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء الترجمة: {e}")

    # ---- التبويب 4: ترجمة المستندات ترجمة قانونية ----
    with tabs[3]:
        st.header("⚖️ ترجمة المستندات ترجمة قانونية")
        file_tab4 = st.file_uploader("📥 رفع العقد أو الوثيقة الرسمية (PDF أو Word)", type=["pdf", "docx"], key="secure_uploader_t4")
            
        active_text4 = ""
        if file_tab4 is not None:
            res = extract_text_from_file(file_tab4)
            if "ERROR" not in res:
                active_text4 = res
                st.success(f"✔️ تم قراءة ({file_tab4.name}) بنجاح للترجمة القانونية.")
            else:
                st.error("⚠️ فشل قراءة الملف.")
            
        legal_entity = st.text_input("اذكر الجهة الرسمية الموجه لها المستند:", key="entity_t4")
        if st.button("بدء صياغة الترجمة القانونية المعتمدة", key="btn_t4"):
            if not active_text4:
                st.warning("⚠️ يرجى رفع الملف القانوني أولاً.")
            elif user_info['attempts'] < 5:
                st.error("❌ رصيدك الحالي منخفض (تتطلب 5 محاولات).")
            else:
                simulate_processing()
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": f"أنت مترجم قانوني محلف ومجاز. صغ وترجم النص التالي بلغة قانونية رسمية صارمة ومطابقة للمعايير لتناسب التخدم إلى: {legal_entity}."},
                            {"role": "user", "content": active_text4[:4000]}
                        ]
                    )
                    if not st.session_state['is_admin']:
                        st.session_state['active_codes'][current_code]['attempts'] -= 5
                    st.markdown("### 🟢 وثيقة صياغة الترجمة القانونية:")
                    st.write(response.choices[0].message.content)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ في السيرفر القانوني: {e}")

    # ---- التبويب 5: توليد الصور والمخططات ----
    with tabs[4]:
        st.header("🎨 توليد الصور والمخططات والأشكال التوضيحية")
        image_prompt = st.text_area("أدخل الوصف التفصيلي للصورة أو المخطط المطلوب بدقة:", key="prompt_t5")
        st.markdown("💰 التكلفة: **5 محاولات**.")
        
        if st.button("توليد الصورة الذكية والمخطط", key="btn_t5"):
            if not image_prompt.strip():
                st.warning("⚠️ يرجى كتابة وصف أولاً.")
            elif user_info['attempts'] < 5:
                st.error(f"❌ رصيدك غير كافٍ.")
            else:
                simulate_processing()
                try:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=image_prompt,
                        n=1,
                        size="1024x1024"
                    )
                    if not st.session_state['is_admin']:
                        st.session_state['active_codes'][current_code]['attempts'] -= 5
                    st.success("🟢 تم بناء وتوليد المخطط البياني بنجاح!")
                    st.image(response.data[0].url, caption="المخطط المولد")
                except Exception as e:
                    st.error(f"❌ خطأ في سيرفر توليد الصور: {e}")

    # ---- التبويب 6: إنشاء فيديو قصير ----
    with tabs[5]:
        st.header("🎬 إنشاء وإنتاج فيديو قصير ذكي")
        st.info("حزم توليد الفيديو المباشر للمطورين (Sora API) لا تزال قيد الإطلاق المحدود من قبل OpenAI.")

    # ---- التبويب 7: توضيح وتحسين الصورة ----
    with tabs[6]:
        st.header("🖼️ معالجة وتوضيح الصور بدقة عالية (AI Upscaling)")
        img_file7 = st.file_uploader("📥 تحميل ملف المخطط أو الصورة المراد معالجتها وتكبيرها", type=["png", "jpg", "jpeg"], key="unique_image_uploader_tab7")
        if img_file7 is not None:
            st.image(img_file7, caption="الصورة المرفوعة بنجاح")
            st.success("🟢 تم التقاط البيانات الصورية وهي جاهزة لعمليات التحسين الفني الفوري.")

    # ---- التبويب 8: توليد الصوت الطبيعي الحقيقي ----
    with tabs[7]:
        st.header("🎙️ توليد وتحويل النصوص إلى أصوات احترافية طبيعية (TTS)")
        audio_text = st.text_area("اكتب أو الصق النص الأكاديمي المراد توليده صوتياً هنا:", key="text_t8")
        audio_voice = st.selectbox("اختر نوع خامة الصوت الفعليّة:", ["onyx", "nova"], key="voice_t8")
        st.markdown("💰 التكلفة الثابتة للإجراء: **5 محاولات**.")
        
        if st.button("توليد وتحويل المحتوى إلى ملف صوتي مسموع", key="btn_t8"):
            if not audio_text.strip():
                st.warning("⚠️ يرجى كتابة نص أولاً.")
            elif user_info['attempts'] < 5:
                st.error(f"❌ رصيدك غير كافٍ.")
            else:
                simulate_processing()
                try:
                    response = client.audio.speech.create(
                        model="tts-1",
                        voice=audio_voice,
                        input=audio_text
                    )
                    with open("temp_output.mp3", "wb") as f:
                        f.write(response.content)
                        
                    if not st.session_state['is_admin']:
                        st.session_state['active_codes'][current_code]['attempts'] -= 5
                    st.success("🟢 تم تحويل النص إلى صوت بشرى طبيعي حقيقي بنجاح!")
                    st.audio("temp_output.mp3")
                except Exception as e:
                    st.error(f"❌ حدث خطأ في معالجة الصوت: {e}")

    # ---- التبويب 9: المستشار الذكي المفتوح الحقيقي ----
    with tabs[8]:
        st.header("🤖 المستشار الذكي الأكاديمي المفتوح")
        advisor_query = st.text_area("اطرح سؤالك أو استشارتك العلمية هنا بشكل مفصل:", key="query_t9")
        
        if st.button("إرسال الاستشارة إلى المستشار الذكي", key="btn_t9"):
            if not advisor_query.strip():
                st.warning("⚠️ يرجى كتابة استفسارك أولاً.")
            else:
                simulate_processing()
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "أنت مستشار أكاديمي وبروفيسور خبير تقدم إرشادات علمية دقيقة وموثوقة."},
                            {"role": "user", "content": advisor_query}
                        ]
                    )
                    total_words = len(advisor_query.split()) + len(response.choices[0].message.content.split())
                    calculated_advisor_cost = math.ceil(total_words / 600)
                    
                    if user_info['attempts'] < calculated_advisor_cost:
                        st.error("❌ رصيدك الحالي منخفض لإنجاز صياغة الاستشارة.")
                    else:
                        if not st.session_state['is_admin']:
                            st.session_state['active_codes'][current_code]['attempts'] -= calculated_advisor_cost
                        st.write("---")
                        st.markdown("### 🟢 رد وتوجيه المستشار الأكاديمي المباشر:")
                        st.write(response.choices[0].message.content)
                        st.caption(f"*تم اقتطاع {calculated_advisor_cost} محاولات من الرصيد.*")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ في نظام معالجة الاستشارات: {e}")

    st.markdown('<div class="footer">ScholarNode Academy © 2026</div>', unsafe_allow_html=True)

# ==========================================
# 4. لوحة تحكم الإدارة السرية (HAYDER_2026$$$)
# ==========================================
elif st.session_state['is_admin'] and not st.session_state['admin_view_as_user']:
    
    ADMIN_HEADER_HTML = """
    <div style="background-color: #ffe680; border: 2px solid #ffcc00; padding: 15px; border-radius: 5px; margin-bottom: 25px;">
        <h2 style="color: #000000; margin:0; text-align:center;">🛠️ لوحة تحكم الإدارة السرية العليا | ScholarNode</h2>
    </div>
    """
    st.markdown(ADMIN_HEADER_HTML, unsafe_allow_html=True)

    admin_tabs = st.tabs([
        "🔑 توليد الكودات الخاصة ببطاقات الاشتراك",
        "📊 مراجعة وفحص كافة الكودات النشطة بالسيرفر",
        "👁️ واجهة العميل"
    ])

    with admin_tabs[0]:
        st.subheader("🔑 نظام توليد كروت التفعيل الذكي")
        selected_tier = st.selectbox("اختر فئة كارت الاشتراك المراد إنشاؤه:", list(CARDS_DATA.keys()), format_func=lambda x: f"{x:,} دينار عراقي")
        tier_info = CARDS_DATA[selected_tier]
        
        if st.button("توليد وإصدار كود التفعيل المعتمد الآن"):
            generated_key = f"SCHOLAR-{selected_tier // 1000}K-{str(uuid.uuid4())[:8].upper()}"
            st.session_state['active_codes'][generated_key] = {
                "attempts": tier_info['attempts'],
                "days": tier_info['days'],
                "tier": selected_tier,
                "created_at": datetime.now().strftime("%Y-%m-%d")
            }
            st.success(f"🎉 تم توليد وإصدار كود الاشتراك بنجاح!")
            st.text_input("📋 كود التفعيل المولد:", value=generated_key)

    with admin_tabs[1]:
        st.subheader("📊 كودات التفعيل النشطة وحالة استهلاك السيرفر")
        if len(st.session_state['active_codes']) == 0:
            st.info("لا توجد أكواد مفعّلة حالياً بالسيرفر.")
        else:
            codes_list = []
            for code, data in st.session_state['active_codes'].items():
                codes_list.append({
                    "كود التفعيل": code,
                    "الفئة المادية": f"{data['tier']:,} د.ع",
                    "المحاولات المتبقية": data['attempts'],
                    "صلاحية الأيام": data['days'],
                    "تاريخ الإصدار": data['created_at']
                })
            st.table(codes_list)

    with admin_tabs[2]:
        st.subheader("معاينة تجريبية حية لنظام العميل")
        if st.button("🚀 الانتقال المباشر لطور محاكاة المشترك"):
            st.session_state['admin_view_as_user'] = True
            st.rerun()
            
    st.markdown("---")
    if st.button("🚪 خروج من حساب الإدارة العليا"):
        logout()
