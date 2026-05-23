import streamlit as st
import streamlit.components.v1 as components
import uuid
from datetime import datetime, timedelta
import math
from openai import OpenAI

# مكتبات معالجة وقراءة نصوص الملفات المرفوعة حقيقياً
import pypdf       # لقراءة ملفات PDF (pip install pypdf)
import docx        # لقراءة ملفات Word (pip install python-docx)

# ==========================================
# 1. إعدادات الصفحة والتهيئة المبدئية والوضع المظلم
# ==========================================
st.set_page_config(
    page_title="ScholarNode Academy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استدعاء العميل وربطه بمفتاحك السري بشكل آمن تماماً عبر الـ Secrets الخاصة بالرابط
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

# تأمين حقل إدخال الكود لمنع الفقدان أثناء الـ Rerun
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

# دالة ذكية لاستخراج النصوص الفعلية من الملفات المرفوعة لإرسالها للـ API
def extract_text_from_file(file):
    try:
        if file.name.endswith('.pdf'):
            pdf_reader = pypdf.PdfReader(file)
            text = ""
            for page in pdf_reader.pages[:10]: # قراءة أول 10 صفحات كحد أقصى لسرعة الاستجابة وحفظ الرصيد
                text += page.extract_text() or ""
            return text if text.strip() else "تحذير: لم نتمكن من قراءة نص رقمي داخل ملف الـ PDF."
        elif file.name.endswith('.docx') or file.name.endswith('.doc'):
            doc = docx.Document(file)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            return f"[ملف مرفوع: {file.name}] - يحتوي على بيانات ثنائية أو صورية."
    except Exception as e:
        return f"فشل استخراج النص من الملف بسبب: {str(e)}"

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

# دالة تصيير الجدول الآمنة والمستقلة
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
        st.write("أدخل كود التفعيل الخاص بك للولوج مباشرة إلى خدمات الذكاء الاصطناعي الأكاديمي.")
        
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
# 3. واجهة المستخدم بعد تسجيل الدخول (التكامل الحقيقي مع الـ API)
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
        
        st.warning(f"⚠️ تنبيه: ينتهي اشتراكك الحالي ذو الفئة ({user_info['tier']:,} د.ع) والمخصص لصلاحية {user_info['days']} يوم بتاريخ {formatted_exp_date}. يرجى التجديد قبل الموعد تجنباً لتعطيل الخدمة.")
        
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

    st.markdown("### 📁 مركز رفع ومعالجة المستندات والبحوث")
    uploaded_file = st.file_uploader("شريط التحميل الموحد (يدعم PDF, Word, وصور بجميع أنواعها)", type=["pdf", "docx", "doc", "png", "jpg", "jpeg"], accept_multiple_files=False, key="main_file_uploader")
    
    # حلقة الوصل ومخزن النص المستخرج لجميع التبويبات بالأسفل
    if 'extracted_content' not in st.session_state:
        st.session_state['extracted_content'] = ""

    if uploaded_file is not None:
        try:
            with st.spinner("⏳ جاري معالجة وقراءة محتوى الملف (نصوص وصور) ذكياً..."):
                # استدعاء خوارزمية المعالجة الأساسية للملف
                file_text = extract_text_from_file(uploaded_file)
                if file_text:
                    st.session_state['extracted_content'] = file_text
                    st.success(f"✔️ تم استقبال ملف ({uploaded_file.name}) ومعالجته بنجاح! التبويبات بالأسفل جاهزة للعمل الآن.")
                else:
                    st.warning("⚠️ تم رفع الملف، لكن لم يتم العثور على نصوص قابلة للاستخراج التلقائي.")
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء معالجة الملف داخلياً: {str(e)}")
    else:
        # إذا لم يتم رفع ملف، نضمن أن المتغير فارغ ولا يسبب انهيار للتبويبات
        st.session_state['extracted_content'] = ""
            
    st.markdown("---")
    st.markdown("### 🛠️ التبويبات والخدمات الأكاديمية المتطورة")

    tabs = st.tabs([
        "📖 معاينة ومناقشة المستند", 
        "🔍 المراجعة الأكاديمية والنقد", 
        "📝 الترجمة الأكاديمية الاحترافية", 
        "⚖️ الترجمة القانونية للمستندات", 
        "🎨 توليد الصور والمخططات", 
        "🎬 إنشاء فيديو قصير", 
        "🖼️ توضيح وتحسين الصور", 
        "🎙️ توليد الصوت الذكي", 
        "🤖 المستشار الذكي المفتوح"
    ])

    # ---- التبويب 1: معاينة ومناقشة المستند الحقيقي ----
    with tabs[0]:
        st.header("📖 معاينة ومناقشة المستند")
        if uploaded_file is None:
            st.info("💡 يرجى رفع مستند من شريط التحميل بالأعلى لتفعيل خدمات المعاينة والنقاش الحقيقي.")
        else:
            user_query = st.text_input("اسأل الذكاء الاصطناعي عن أي جزئية في الملف المرفوع:", placeholder="اكتب سؤالك هنا...")
            if st.button("تحليل ومناقشة الملف عبر GPT", key="tab1_btn"):
                if not user_query.strip():
                    st.warning("⚠️ يرجى كتابة سؤالك أولاً.")
                elif user_info['attempts'] < 1:
                    st.error("❌ رصيدك غير كافٍ لإجراء هذه العملية.")
                else:
                    simulate_processing()
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "أنت مساعد أكاديمي تجيب على أسئلة المستخدم بناءً على محتوى الملف المرفق بدقة علمية بالغة وبنفس لغة السؤال."},
                                {"role": "user", "content": f"محتوى الملف:\n{extracted_content}\n\nسؤال المستخدم:\n{user_query}"}
                            ]
                        )
                        if not st.session_state['is_admin']:
                            st.session_state['active_codes'][current_code]['attempts'] -= 1
                        st.markdown("### 🟢 الإجابة والتحليل الحقيقي للنص:")
                        st.write(response.choices[0].message.content)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ حدث خطأ أثناء الاتصال بالسيرفر: {e}")

    # ---- التبويب 2: المراجعة الأكاديمية والنقدية الحقيقية ----
    with tabs[1]:
        st.header("🔍 المراجعة الأكاديمية والنقدية الاحترافية")
        if uploaded_file is None:
            st.info("💡 يرجى رفع ملف البحث أو الأطروحة من الأعلى للبدء بالمراجعة والنقد.")
        else:
            st.markdown("💰 التكلفة الإجمالية للاجراء: **5 محاولات** لنقد المنهجية والمضمون العلمي بالكامل.")
            if st.button("البدء بالمراجعة والنقد الأكاديمي الشامل", key="tab2_btn"):
                if user_info['attempts'] < 5:
                    st.error("❌ رصيدك الحالي غير كافٍ. العملية تتطلب خصم 5 محاولات.")
                else:
                    simulate_processing()
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "أنت بروفيسور محكم للأبحاث العلمية. قم بتقديم نقد منهجي، أكاديمي، وبنيوي مفصل للنص المرفق واقترح نقاط التحسين باللغة العربية."},
                                {"role": "user", "content": extracted_content}
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
        if uploaded_file is None:
            st.info("💡 يرجى رفع الملف المُراد ترجمته أكاديمياً عبر شريط الرفع الموحد.")
        else:
            st.markdown("💰 التكلفة الإجمالية للترجمة الاحترافية: **3 محاولات**.")
            target_lang_tab3 = st.selectbox("اختر اللغة المستهدفة للترجمة الفورية:", ["العربية", "English"], key="tab3_lang")
            
            if st.button("تنفيذ الترجمة الأكاديمية الفائقة", key="tab3_btn"):
                if user_info['attempts'] < 3:
                    st.error("❌ رصيدك غير كافٍ. يتطلب الإجراء 3 محاولات.")
                else:
                    simulate_processing()
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": f"ترجم النص التالي ترجمة أكاديمية احترافية دقيقة مع الحفاظ على المصطلحات العلمية الرصينة والسياق الأكاديمي إلى لغة: {target_lang_tab3}."},
                                {"role": "user", "content": extracted_content[:4000]}
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
        if uploaded_file is None:
            st.info("💡 يرجى رفع الوثائق الشخصية، الشهادات، أو العقود عبر شريط التحميل بالأعلى.")
        else:
            legal_entity = st.text_input("اذكر الجهة الرسمية أو الدولية التي سيقدم لها الملف القانوني:")
            if st.button("بدء صياغة الترجمة القانونية المعتمدة", key="tab4_btn"):
                if user_info['attempts'] < 5:
                    st.error("❌ رصيدك الحالي منخفض لإنجاز الصياغة القانونية المحكمة (تتطلب 5 محاولات).")
                else:
                    simulate_processing()
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": f"أنت مترجم قانوني محلف ومجاز. صغ وترجم النص التالي بلغة قانونية رسمية صارمة ومطابقة للمعايير لتناسب التقديم إلى: {legal_entity}."},
                                {"role": "user", "content": extracted_content[:4000]}
                            ]
                        )
                        if not st.session_state['is_admin']:
                            st.session_state['active_codes'][current_code]['attempts'] -= 5
                        st.markdown("### 🟢 وثيقة صياغة الترجمة القانونية:")
                        st.write(response.choices[0].message.content)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ خطأ في السيرفر القانوني: {e}")

    # ---- التبويب 5: توليد الصور والمخططات الهندسية والأكاديمية عبر DALL-E 3 ----
    with tabs[4]:
        st.header("🎨 توليد الصور والمخططات والأشكال التوضيحية")
        image_prompt = st.text_area("أدخل الوصف التفصيلي للصورة، المخطط، الجدول، أو الشعار المطلوب بدقة:")
        st.markdown("💰 التكلفة: **5 محاولات** لتوليد صور ومخططات بدقة فائقة رقمياً.")
        
        if st.button("توليد الصورة الذكية والمخطط", key="tab5_btn"):
            if not image_prompt.strip():
                st.warning("⚠️ يرجى كتابة وصف أو محتوى لتوليده كشكل توضيحي.")
            elif user_info['attempts'] < 5:
                st.error(f"❌ رصيدك غير كافٍ للتوليد. العملية تتطلب خصم 5 محاولات.")
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
                    st.success("🟢 تم بناء وتوليد المخطط البياني/الصورة الفعليّة بنجاح!")
                    st.image(response.data[0].url, caption="المخطط المولد الفعلي القادم من السيرفر")
                except Exception as e:
                    st.error(f"❌ خطأ في سيرفر توليد الصور: {e}")

    # ---- التبويب 6: إنشاء فيديو قصير ----
    with tabs[5]:
        st.header("🎬 إنشاء وإنتاج فيديو قصير ذكي")
        st.info("حزم توليد الفيديو المباشر للمطورين (Sora API) لا تزال قيد الإطلاق المحدود من قبل OpenAI. تم إبقاء واجهة توليد الفيديو في وضعها التفاعلي المحاكي لتأمين جودة تجربة الاستخدام لطلابك عند توفر التحديث عالمياً.")

    # ---- التبويب 7: توضيح وتحسين الصورة بدقة عالية ----
    with tabs[6]:
        st.header("🖼️ معالجة وتوضيح الصور بدقة عالية (AI Upscaling)")
        st.info("ميزة رفع الجودة وتوضيح البيكسل (Upscaling) معمارياً تتطلب خوادم رسومية محلية لمعالجة الصور الثنائية، الواجهة مهيأة ومرتبطة بقواعد البيانات وجاهزة لإجراء عمليات المحاكاة والتخصيص.")

    # ---- التبويب 8: توليد الصوت الطبيعي الحقيقي عبر الـ API ----
    with tabs[7]:
        st.header("🎙️ توليد وتحويل النصوص إلى أصوات احترافية طبيعية (TTS)")
        audio_text = st.text_area("اكتب أو الصق النص الأكاديمي المراد توليده صوتياً هنا:")
        audio_voice = st.selectbox("اختر نوع خامة الصوت الفعليّة:", ["onyx", "nova"])
        st.markdown("💰 التكلفة الثابتة للإجراء: **5 محاولات** لتخليق كليب صوتي احترافي.")
        
        if st.button("توليد وتحويل المحتوى إلى ملف صوتي مسموع", key="tab8_btn"):
            if not audio_text.strip():
                st.warning("⚠️ يرجى كتابة نص أولاً.")
            elif user_info['attempts'] < 5:
                st.error(f"❌ رصيدك غير كافٍ. العملية تتطلب خصم 5 محاولات.")
            else:
                simulate_processing()
                try:
                    response = client.audio.speech.create(
                        model="tts-1",
                        voice=audio_voice,
                        input=audio_text
                    )
                    # حفظ الصوت في ملف مؤقت لعرضه مباشرة داخل مشغل الصوت الخاص بـ Streamlit
                    with open("temp_output.mp3", "wb") as f:
                        f.write(response.content)
                        
                    if not st.session_state['is_admin']:
                        st.session_state['active_codes'][current_code]['attempts'] -= 5
                    st.success("🟢 تم تحويل النص إلى صوت بشري طبيعي حقيقي بنجاح!")
                    st.audio("temp_output.mp3")
                except Exception as e:
                    st.error(f"❌ حدث خطأ في معالجة الصوت: {e}")

    # ---- التبويب 9: المستشار الذكي المفتوح الحقيقي ----
    with tabs[8]:
        st.header("🤖 المستشار الذكي الأكاديمي المفتوح")
        advisor_query = st.text_area("اطرح سؤالك أو استشارتك العلمية هنا بشكل مفصل:")
        
        if st.button("إرسال الاستشارة إلى المستشار الذكي", key="tab9_btn"):
            if not advisor_query.strip():
                st.warning("⚠️ يرجى كتابة استفسارك أولاً.")
            else:
                simulate_processing()
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "أنت مستشار أكاديمي وبروفيسور خبير تقدم إرشادات علمية دقيقة وموثوقة لمساعدة الباحثين في كتابة الأبحاث وصياغة المناهج بأسلوب رصين وفلسفة علمية محكمة."},
                            {"role": "user", "content": advisor_query}
                        ]
                    )
                    # احتساب مرن ومؤتمت لتكلفة استهلاك الكلمات والردود
                    total_words = len(advisor_query.split()) + len(response.choices[0].message.content.split())
                    calculated_advisor_cost = math.ceil(total_words / 600)
                    
                    if user_info['attempts'] < calculated_advisor_cost:
                        st.error("❌ رصيدك الحالي منخفض لإنجاز صياغة الاستشارة المقدرة.")
                    else:
                        if not st.session_state['is_admin']:
                            st.session_state['active_codes'][current_code]['attempts'] -= calculated_advisor_cost
                        st.write("---")
                        st.markdown("### 🟢 رد وتوجيه المستشار الأكاديمي المباشر:")
                        st.write(response.choices[0].message.content)
                        st.caption(f"*تم توليد المحتوى حقيقياً واقتطاع {calculated_advisor_cost} محاولات من الرصيد.*")
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
        selected_tier = st.selectbox("اختر فئة كارت الاشتراك المراد إنشاؤه وصناعته:", list(CARDS_DATA.keys()), format_func=lambda x: f"{x:,} دينار عراقي")
        tier_info = CARDS_DATA[selected_tier]
        
        if st.button("توليد وإصدار كود التفعيل المعتمد الآن"):
            generated_key = f"SCHOLAR-{selected_tier // 1000}K-{str(uuid.uuid4())[:8].upper()}"
            st.session_state['active_codes'][generated_key] = {
                "attempts": tier_info['attempts'],
                "days": tier_info['days'],
                "tier": selected_tier,
                "created_at": datetime.now().strftime("%Y-%m-%d")
            }
            st.success(f"🎉 تم توليد وإصدار كود الاشتراك بنجاح لـ فئة {selected_tier:,} د.ع!")
            st.text_input("📋 كود التفعيل المولد (انسخه الآن وصدره للمستخدم):", value=generated_key)

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
