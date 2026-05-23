import streamlit as st
import uuid
from datetime import datetime, timedelta
import math

# ==========================================
# 1. إعدادات الصفحة والتهيئة المبدئية والوضع المظلم
# ==========================================
st.set_page_config(
    page_title="ScholarNode Academy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# دعم التنسيق المتزن والألوان المتوافقة مع الوضعين المظلم والمضيء
st.markdown("""
<style>
    /* علامة الترحيب بالرأس طبقاً للمواصفات */
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
    /* تنسيق الجداول لتناسب اللون الأزرق والأصفر الفاتح */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 0.95em;
        border-radius: 5px;
        overflow: hidden;
    }
    .styled-table th {
        background-color: #e6f2ff;
        color: #003366;
        text-align: center;
        padding: 10px;
        border: 1px solid #ffe680;
    }
    .styled-table td {
        padding: 10px;
        text-align: center;
        border: 1px solid #ffe680;
    }
    .styled-table tr:nth-child(even) {
        background-color: #fffde6;
    }
    /* الفوتر أسفل الصفحة */
    .footer {
        text-align: center;
        padding: 20px;
        font-size: 0.9em;
        color: #888888;
        border-top: 1px solid #ddd;
        margin-top: 50px;
    }
</style>
""", unsafe_scale=True)

# قاعدة بيانات وهمية محاكاة بداخل الـ Session State للحفاظ على الأمان والعمليات التشاركية
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    # الكود السري للإدارة للوصول المباشر
    st.session_state['admin_password'] = "HAYDER_2026$$$"
    # قاعدة بيانات الكروت الصالحة (الكود: {المحاولات، الصلاحية بالأيام، الفئة، تاريخ الإنشاء})
    st.session_state['active_codes'] = {
        "SCHOLAR-DEMO-123": {"attempts": 130, "days": 30, "tier": 10000, "created_at": datetime.now().strftime("%Y-%m-%d")},
        "PRO-MEMBER-999": {"attempts": 690, "days": 150, "tier": 50000, "created_at": datetime.now().strftime("%Y-%m-%d")}
    }
    # حالة جلسة تسجيل الدخول الحالية
    st.session_state['logged_in'] = False
    st.session_state['current_user_code'] = None
    st.session_state['is_admin'] = False
    st.session_state['admin_view_as_user'] = False

# بيانات الكروت والسياسة التراكمية والصلاحيات المحددة
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

# دالة مساعدة لمحاكاة شريط معالجة متزامن من 0% إلى 100%
def simulate_processing():
    import time
    progress_bar = st.progress(0)
    status_text = st.empty()
    for percent_complete in range(0, 101, 10):
        time.sleep(0.05)  # معالجة سريعة للمحاكاة
        progress_bar.progress(percent_complete)
        status_text.text(f"جاري المعالجة الذكية عبر GPT-4o-mini... {percent_complete}%")
    status_text.empty()
    progress_bar.empty()

# دالة لعرض جدول الكروت الموحد بالألوان المطلوبة
def render_cards_table():
    html_table = """
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
    st.markdown(html_table, unsafe_allow_html=True)

# دالة تسجيل الخروج
def logout():
    st.session_state['logged_in'] = False
    st.session_state['current_user_code'] = None
    st.session_state['is_admin'] = False
    st.session_state['admin_view_as_user'] = False
    st.rerun()


# ==========================================
# 2. الواجهة الرئيسية (قبل تسجيل الدخول)
# ==========================================
if not st.session_state['logged_in'] and not st.session_state['is_admin']:
    
    # 1. علامة الترحيب العلوية بالألوان المحددة
    st.markdown("""
    <div class="header-box">
        <h1>منصة التعليم الأكاديمية (ScholarNode)</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # تقسيم الواجهة إلى قسمين الرئيسي والمعلومات الجانبية للدفع
    col_main, col_payment = st.columns([5, 3], gap="large")
    
    with col_main:
        st.subheader("🔒 الدخول الآمن للمنصة")
        st.write("أدخل كود التفعيل الخاص بك للولوج مباشرة إلى خدمات الذكاء الاصطناعي الأكاديمي.")
        
        # حقل إدخال الكود مع ميزة إخفاء وإظهار العين
        show_code = st.checkbox("👁️ إظهار الكود المدخل")
        input_code = st.text_input(
            "ادخل كود التفعيل", 
            type="default" if show_code else "password", 
            placeholder="مثال: SCHOLAR-XXXX-XXXX",
            label_visibility="collapsed"
        )
        
        if st.button("دخول المنصة", use_container_width=True):
            cleaned_code = input_code.strip()
            
            # فحص الولوج السري لحساب الإدارة
            if cleaned_code == st.session_state['admin_password']:
                st.session_state['is_admin'] = True
                st.success("تم الدخول بصفتك مديراً للنظام بنجاح.")
                st.rerun()
            
            # فحص أكواد المستخدمين وإجراءات الأمان
            elif cleaned_code in st.session_state['active_codes']:
                user_data = st.session_state['active_codes'][cleaned_code]
                
                # التحقق من نفاد المحاولات أو انتهاء الصلاحية
                if user_data['attempts'] <= 0:
                    st.error("❌ عذراً، هذا الكود غير فعال بسبب نفاد رصيد المحاولات بالكامل.")
                else:
                    st.session_state['logged_in'] = True
                    st.session_state['current_user_code'] = cleaned_code
                    st.success("تم الدخول الآمن بنجاح!")
                    st.rerun()
            else:
                st.error("⚠️ الكود غير فعال أو غير صحيح. يرجى التأكد من كود التفعيل الخاص بك أو تجديد الاشتراك.")

        st.write("---")
        st.subheader("📊 فئات الاشتراكات والبطاقات المتوفرة")
        render_cards_table()

    with col_payment:
        # 3. تخصيص معلومات الدفع في جهة اليسار
        st.markdown("""
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
        """, unsafe_allow_html=True)

    # 6. عبارة الحقوق أسفل الصفحة
    st.markdown('<div class="footer">ScholarNode Academy © 2026</div>', unsafe_allow_html=True)


# ==========================================
# 3. واجهة المستخدم بعد تسجيل الدخول (أو معاينة المسؤول)
# ==========================================
elif st.session_state['logged_in'] or (st.session_state['is_admin'] and st.session_state['admin_view_as_user']):
    
    # تحديد الكود النشط لإدارة العمليات الحالية
    current_code = st.session_state['current_user_code'] if st.session_state['logged_in'] else "ADMIN-PREVIEW"
    
    # جلب بيانات المشترك أو توفير بيانات تجريبية للمعاينة الإدارية
    if current_code in st.session_state['active_codes']:
        user_info = st.session_state['active_codes'][current_code]
    else:
        user_info = {"attempts": 999, "days": 30, "tier": 10000, "created_at": datetime.now().strftime("%Y-%m-%d")}
        
    # الحساب التلقائي لتاريخ الانتهاء بناءً على نوع الاشتراك وصلاحيته
    creation_date = datetime.strptime(user_info['created_at'], "%Y-%m-%d")
    expiration_date = creation_date + timedelta(days=user_info['days'])
    formatted_exp_date = expiration_date.strftime("%Y-%m-%d")

    # 1. عبارة الترحيب العلوية المخصصة للمشترك مع الرصيد الحالي
    st.markdown(f"""
    <div style="background-color: #e6f2ff; border-left: 5px solid #0056b3; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="margin:0; color:#003366;">👋 مرحباً بك في ScholarNode</h3>
        <p style="margin:5px 0 0 0; font-size:1.1em;">كود الاشتراك النشط: <b>{current_code}</b> | <b>لديك رصيد محاولات يبلغ: <span style="color:#d9534f; font-size:1.2em;">{user_info['attempts']}</span> محاولة</b></p>
    </div>
    """, unsafe_allow_html=True)

    # هيكلة الصفحة: شريط جانبي لبيانات الحساب + مساحة العمل الرئيسية للتبويبات
    with st.sidebar:
        st.markdown("### 📋 معلومات الاشتراك")
        st.info(f"**المحاولات المتبقية:** {user_info['attempts']} محاولة")
        st.info(f"**تاريخ انتهاء الصلاحية:** {formatted_exp_date}")
        
        # رسالة تنبيه للمشترك عن موعد انتهاء الاشتراك وحسب الصلاحية
        st.warning(f"⚠️ تنبيه: ينتهي اشتراكك الحالي ذو الفئة ({user_info['tier']:,} د.ع) والمخصص لصلاحية {user_info['days']} يوم بتاريخ {formatted_exp_date}. يرجى التجديد قبل الموعد تجنباً لتعطيل الخدمة.")
        
        st.markdown("---")
        st.markdown("### 📊 جدول الكروت المعتمد")
        render_cards_table()
        st.markdown("---")
        
        # زر تسجيل الخروج أو العودة للإدارة
        if st.session_state['is_admin']:
            if st.button("🔙 العودة إلى لوحة الإدارة", use_container_width=True):
                st.session_state['admin_view_as_user'] = False
                st.rerun()
        else:
            if st.button("🚪 تسجيل الخروج", use_container_width=True, on_click=logout):
                st.success("تم تسجيل الخروج.")

    # 2. شريط رفع الملفات الموحد (يصل حتى حجم 600 ميجابايت) لكافة الأنواع
    st.markdown("### 📁 مركز رفع ومعالجة المستندات والبحوث")
    uploaded_file = st.file_uploader(
        "شريط التحميل الموحد (يدعم PDF, Word, Excel, والصور بجميع أنواعها حتى 600 ميجابايت)", 
        type=["pdf", "docx", "doc", "xlsx", "xls", "png", "jpg", "jpeg"],
        help="الحد الأقصى للملف المرفوع هو 600 ميجابايت"
    )

    if uploaded_file is not None:
        st.success(f"✔️ تم استقبال الملف: {uploaded_file.name} بنجاح وجاهز للمعالجة عبر خدمات التبويبات بالأسفل.")

    st.markdown("---")
    st.markdown("### 🛠️ التبويبات والخدمات الأكاديمية المتطورة")

    # 3. إعداد التبويبات البرمجية الأساسية كاملة
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

    # ---- التبويب 1: معاينة ومناقشة المستند ----
    with tabs[0]:
        st.header("📖 معاينة ومناقشة المستند")
        if uploaded_file is None:
            st.info("💡 يرجى رفع مستند من شريط التحميل بالأعلى لتفعيل خدمات المعاينة والنقاش.")
        else:
            col_preview, col_chat = st.columns([1, 1])
            with col_preview:
                st.subheader("📄 تصفح المستند المرفوع")
                st.markdown(f"🖼️ *محاكاة عرض الصفحة الأولى للمستند: ({uploaded_file.name})*")
                st.image("https://via.placeholder.com/400x550.png?text=ScholarNode+Document+Preview", use_container_width=True)
            with col_chat:
                st.subheader("💬 شريط الحوار ومناقشة المحتوى")
                target_lang = st.selectbox("اختر اللغة المستهدفة للحوار للنقاش:", ["العربية", "English", "Кыргызча"], key="tab1_lang")
                user_query = st.text_input("اسأل الذكاء الاصطناعي عن أي جزئية في الملف:", placeholder="اكتب سؤالك هنا...")
                
                if st.button("تحليل ومناقشة", key="tab1_btn"):
                    if user_info['attempts'] < 1:
                        st.error("❌ رصيدك غير كافٍ لإجراء هذه العملية. يتطلب الإجراء محاولة واحدة على الأقل.")
                    else:
                        simulate_processing()
                        # حسم محاولة واحدة للنقاش المستقل
                        if st.session_state['logged_in']:
                            st.session_state['active_codes'][current_code]['attempts'] -= 1
                        st.success("🟢 رد الذكاء الاصطناعي (GPT-4o-mini): تم تحليل النص استناداً للمستند المرفوع بدقة بالغة باللغة المحددة.")
                        st.download_button("📥 تحميل النقاش والتقرير المولد بصيغة Word (.docx)", data="محتوى افتراضي للتقرير", file_name="Document_Discussion_Report.docx")
                        st.rerun()

    # ---- التبويب 2: المراجعة الأكاديمية والنقدية الاحترافية ----
    with tabs[1]:
        st.header("🔍 المراجعة الأكاديمية والنقدية الاحترافية")
        if uploaded_file is None:
            st.info("💡 يرجى رفع ملف البحث أو الأطروحة من الأعلى للبدء بالمراجعة والنقد.")
        else:
            st.write("يقوم النظام بفحص هيكلية الملف وحساب تكلفة النقد العلمي.")
            # محاكاة حساب الصفحات لغرض تطبيق السياسة المالية الصارمة لحماية رصيد الأستاذ
            simulated_pages = 8 
            st.info(f"📊 عدد صفحات الملف الحالي المستكشفة: **{simulated_pages} صفحات**")
            st.markdown(f"💰 التكلفة الإجمالية المخصومة للاجراء: **{simulated_pages} محاولات** (بمعدل 1 محاولة لكل صفحة).")
            
            target_lang_tab2 = st.selectbox("اختر اللغة المستهدفة لتقرير النقد الأكاديمي:", ["العربية", "English"], key="tab2_lang")
            
            if st.button("البدء بالمراجعة والنقد الأكاديمي الشامل", key="tab2_btn"):
                if user_info['attempts'] < simulated_pages:
                    st.error(f"❌ رصيدك الحالي ({user_info['attempts']}) غير كافٍ لإتمام مراجعة الملف. العملية تتطلب خصم {simulated_pages} محاولات.")
                else:
                    simulate_processing()
                    if st.session_state['logged_in']:
                        st.session_state['active_codes'][current_code]['attempts'] -= simulated_pages
                    st.success(f"🟢 تم الانتهاء من المراجعة المنهجية والنقد الأكاديمي الرصين للـ {simulated_pages} صفحات بنجاح، وتم خصم التكلفة من رصيدك.")
                    st.rerun()

    # ---- التبويب 3: الترجمة الأكاديمية الاحترافية ----
    with tabs[2]:
        st.header("📝 الترجمة الأكاديمية الاحترافية")
        if uploaded_file is None:
            st.info("💡 يرجى رفع الملف المُراد ترجمته أكاديمياً عبر شريط الرفع الموحد.")
        else:
            simulated_pages_t3 = 5
            st.info(f"📊 عدد صفحات الملف المستهدفة بالترجمة: **{simulated_pages_t3} صفحات**")
            st.markdown(f"💰 التكلفة الإجمالية للترجمة الاحترافية: **{simulated_pages_t3} محاولات** (1 محاولة لكل صفحة).")
            
            target_lang_tab3 = st.selectbox("اختر اللغة المستهدفة للترجمة الفورية:", ["العربية (يمين إلى يسار RTL)", "English"], key="tab3_lang")
            
            if st.button("تنفيذ الترجمة الأكاديمية الفائقة", key="tab3_btn"):
                if user_info['attempts'] < simulated_pages_t3:
                    st.error(f"❌ رصيدك غير كافٍ. يتطلب الإجراء {simulated_pages_t3} محاولات، بينما تمتلك حالياً {user_info['attempts']} محاولة فقط.")
                else:
                    simulate_processing()
                    if st.session_state['logged_in']:
                        st.session_state['active_codes'][current_code]['attempts'] -= simulated_pages_t3
                    st.success("🟢 تمت الترجمة الأكاديمية الاحترافية جداً ومراعاة المصطلحات والمفاهيم بدقة تامة.")
                    
                    # التأكيد البرمجي على التنسيق الموجه من اليمين إلى اليسار في حال اختيار اللغة العربية
                    if "العربية" in target_lang_tab3:
                        st.info("ℹ️ تم تطبيق نظام المحاذاة والتنسيق العربي الصارم (RTL) من اليمين إلى اليسار على ملف الـ Word المتولد.")
                    
                    st.download_button("📥 تحميل ملف الترجمة المتكامل بصيغة Word المنسقة", data="محتوى مترجم منسق", file_name="Academic_Translated_Document.docx")
                    st.rerun()

    # ---- التبويب 4: ترجمة المستندات ترجمة قانونية ----
    with tabs[3]:
        st.header("⚖️ ترجمة المستندات ترجمة قانونية")
        if uploaded_file is None:
            st.info("💡 يرجى رفع الوثائق الشخصية، الشهادات، أو العقود عبر شريط التحميل بالأعلى.")
        else:
            st.write(f"الملف الحالي المستهدف بالصياغة القانونية: `{uploaded_file.name}`")
            legal_entity = st.text_input("اذكر الجهة الرسمية أو الدولية التي سيقدم لها الملف القانوني (لتخصيص الصياغة):")
            target_lang_tab4 = st.selectbox("اختر لغة الترجمة القانونية المعتمدة:", ["English", "العربية", "Français"], key="tab4_lang")
            
            if st.button("بدء صياغة الترجمة القانونية المعتمدة", key="tab4_btn"):
                if user_info['attempts'] < 5:  # تكلفة تقديرية مرجعية للوثيقة القانونية المحكمة
                    st.error("❌ رصيدك الحالي منخفض لإنجاز الصياغة القانونية المحكمة والمراجعة اللغوية الاستشارية.")
                else:
                    simulate_processing()
                    if st.session_state['logged_in']:
                        st.session_state['active_codes'][current_code]['attempts'] -= 5
                    st.success(f"🟢 تم صياغة الترجمة القانونية الاحترافية والاعتمادية وتوثيقها لتتوافق تماماً مع متطلبات الجهة المحددة: ({legal_entity}).")
                    st.download_button("📥 تحميل الوثيقة القانونية المترجمة المعتمدة (.docx)", data="نص قانوني مترجم", file_name="Certified_Legal_Translation.docx")
                    st.rerun()

    # ---- التبويب 5: توليد الصور والمخططات الهندسية والأكاديمية ----
    with tabs[4]:
        st.header("🎨 توليد الصور والمخططات والأشكال التوضيحية")
        st.write("توليد كافة أنواع الرسوم والبيانات اللوجستية والمخططات البيانية دون قيود فنية، مع حظر وإغلاق تام لأي محتوى غير أخلاقي.")
        
        image_prompt = st.text_area("أدخل الوصف التفصيلي للصورة، المخطط، الجدول، أو الشعار المطلوب بدقة:")
        st.markdown("💰 تكلفة التوليد الثابتة للعملية: **5 محاولات** تفصم عند إتمام البناء بنجاح.")
        
        if st.button("توليد الصورة الذكية والمخطط", key="tab5_btn"):
            if not image_prompt.strip():
                st.warning("⚠️ يرجى كتابة وصف أو محتوى لتوليده كشكل توضيحي.")
            elif any(word in image_prompt.lower() for word in ["bad_word_1", "غير_اخلاقي"]): # فحص أمان أولي برمجياً
                st.error("❌ تم رفض الطلب وأرشفته! يمنع النظام ويقيد كلياً توليد أي محتوى غير أخلاقي أو مخالف لمعايير الأكاديمية.")
            elif user_info['attempts'] < 5:
                st.error(f"❌ رصيدك غير كافٍ للتوليد. العملية تتطلب خصم 5 محاولات، رصيدك الحالي هو: {user_info['attempts']}.")
            else:
                simulate_processing()
                if st.session_state['logged_in']:
                    st.session_state['active_codes'][current_code]['attempts'] -= 5
                
                st.success("🟢 تم بناء وتوليد المخطط البياني/الصورة بدقة ووضوح فائقين، مع تطبيق دمج الكلمات باللغة العربية بوضوح تام ودون أي تشويه رقمي للأحرف.")
                # عرض الصورة الوهمية مع توفير خيار التحميل بصيغة JPEG المطلوبة حصرًا
                st.image("https://via.placeholder.com/800x450.png?text=Generated+Academic+Chart+With+Arabic+Text", caption="المخطط المولد بدقة رقمية عالية")
                st.download_button("📥 تحميل الصورة المعتمدة فوراً بصيغة JPEG", data="بيانات_صورة_افتراضية", file_name="ScholarNode_Generated_Image.jpeg", mime="image/jpeg")
                st.rerun()

    # ---- التبويب 6: إنشاء فيديو قصير (Shorts / Reels) ----
    with tabs[5]:
        st.header("🎬 إنشاء وإنتاج فيديو قصير ذكي")
        st.write("بناء وتصميم الفيديوهات القصيرة التعليمية والتعريفية التلقائية بالكامل استناداً لبياناتك.")
        video_duration_min = st.number_input("حدد مدة الفيديو المطلوبة (بالدقائق):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
        
        calculated_video_cost = math.ceil(video_duration_min * 25)
        st.markdown(f"💰 التكلفة المقدرة لإنتاج الفيديو بناءً على المدة: **{calculated_video_cost} محاولة** (بمعدل 25 محاولة لكل 1 دقيقة زمنية).")
        
        video_topic = st.text_input("موضوع الفيديو أو السكريبت الأساسي المراد تحويله إلى سيناريو مرئي ومسموع:")
        
        if st.button("توليد ومعالجة وإنتاج الفيديو القصير", key="tab6_btn"):
            if user_info['attempts'] < calculated_video_cost:
                st.error(f"❌ رصيدك الحالي لا يكفي لإتمام عملية إنتاج وتوليد الفيديو القصير. التكلفة المطلوبة هي {calculated_video_cost} محاولة.")
            else:
                simulate_processing()
                if st.session_state['logged_in']:
                    st.session_state['active_codes'][current_code]['attempts'] -= calculated_video_cost
                st.success(f"🟢 تم الانتهاء من كتابة السكريبت، وتوليد الصوت، ودمج المشاهد المرئية، وتصدير الفيديو بنجاح لفترة {video_duration_min} دقيقة!")
                
                # توفير زر تحميل بصيغة Mp4 للعمل على جميع المشغلات دون مشاكل توافقية
                st.video("https://www.w3schools.com/html/mov_bbb.mp4") # فيديو تجريبي للمحاكاة والتأكد
                st.download_button("📥 تحميل ملف الفيديو النهائي بصيغة MP4 العالمية القياسية", data="بيانات_فيديو", file_name="ScholarNode_Short_Video.mp4", mime="video/mp4")
                st.rerun()

    # ---- التبويب 7: توضيح وتحسين الصورة بدقة عالية ----
    with tabs[6]:
        st.header("🖼️ معالجة وتوضيح الصور بدقة عالية (AI Upscaling)")
        st.write("تبويب مخصص لرفع جودة الأشكال، المخططات الضعيفة، المخطوطات والوثائق القديمة لتبدو فائقة الجودة.")
        
        uploaded_img = st.file_uploader("ارفع الصورة المُراد تحسين دقتها ووضوحها هنا:", type=["png", "jpg", "jpeg"], key="tab7_upload")
        st.markdown("💰 تكلفة تحسين الصورة الثابتة: **3 محاولات** فقط تفصم عند إتمام التحسين المعملي لملامح الأبعاد.")
        
        if uploaded_img is not None:
            st.image(uploaded_img, caption="الصورة الأصلية قبل المعالجة", width=300)
            if st.button("تحسين جودة الصورة ومعالجتها فوراً", key="tab7_btn"):
                if user_info['attempts'] < 3:
                    st.error("❌ لا تملك رصيد كافٍ لإجراء تحسين الصورة الرقمية الذكية (تتطلب 3 محاولات).")
                else:
                    simulate_processing()
                    if st.session_state['logged_in']:
                        st.session_state['active_codes'][current_code]['attempts'] -= 3
                    st.success("🟢 تمت معالجة وتوضيح الصورة وإعادة بنائها بجودة ودقة فوتوغرافية متطابقة وثابتة الأبعاد.")
                    st.image("https://via.placeholder.com/800x450.png?text=Enhanced+High+Resolution+Image+Result", caption="الصورة النهائية بعد رفع دقتها للوضوح العالي")
                    st.download_button("📥 تحميل الصورة المحسنة بدقة فائقة", data="بيانات_صورة", file_name="Enhanced_Image.png")
                    st.rerun()

    # ---- التبويب 8: توليد وتحويل النصوص إلى أصوات طبيعية احترافية ----
    with tabs[7]:
        st.header("🎙️ توليد وتحويل النصوص إلى أصوات احترافية")
        st.write("قم بتحويل أي فقرات نصية أو بحوث كاملة إلى ملفات صوتية مسموعة بخامات صوتية طبيعية ومحاكية للبشر.")
        
        audio_text = st.text_area("اكتب أو الصق النص الأكاديمي المراد توليده صوتياً هنا:")
        
        # خوارزمية الاحتساب المالي الصارمة بناءً على رغبتك (كل 40 كلمة = 1 محاولة)
        words_count = len(audio_text.split()) if audio_text.strip() else 0
        calculated_audio_cost = math.ceil(words_count / 40) if words_count > 0 else 0
        
        st.info(f"📊 عدد الكلمات المكتوبة حالياً في الحقل: **{words_count} كلمة**.")
        st.markdown(f"💰 سياسة حسم التكلفة التلقائية للتبويب: **{calculated_audio_cost} محاولة** مخصومة (حيث تحتسب كل 40 كلمة بمحاولة كاملة، وبمجرد الدخول في الكلمة 41 تحتسب محاولتين تلقائياً صعوداً).")
        
        audio_voice = st.selectbox("اختر خامة ونوع الصوت المطلوب:", ["Onyx (رجالي وقور)", "Nova (نسائي نقي)", "Shimmer (احترافي قياسي)"])
        
        if st.button("توليد وتحويل المحتوى إلى ملف صوتي مسموع", key="tab8_btn"):
            if words_count == 0:
                st.warning("⚠️ يرجى كتابة نص أولاً ليقوم محرك الصوت بمعالجته وتحويله.")
            elif user_info['attempts'] < calculated_audio_cost:
                st.error(f"❌ رصيدك غير كافٍ. العملية تتطلب خصم {calculated_audio_cost} محاولات بناءً على طول النص الحالي.")
            else:
                simulate_processing()
                if st.session_state['logged_in']:
                    st.session_state['active_codes'][current_code]['attempts'] -= calculated_audio_cost
                st.success(f"🟢 تم تحويل النص إلى صوت احترافي بنجاح بنسق وخامة ({audio_voice}) وتم حسم {calculated_audio_cost} محاولة من حسابك.")
                st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
                st.download_button("📥 تحميل الملف الصوتي النهائي بصيغة MP3 الخفيفة والمرنة", data="بيانات_صوت", file_name="ScholarNode_Speech_Audio.mp3", mime="audio/mp3")
                st.rerun()

    # ---- التبويب 9: المستشار الذكي المفتوح (مقيد الاستهلاك التلقائي) ----
    with tabs[8]:
        st.header("🤖 المستشار الذكي الأكاديمي المفتوح")
        st.write("تبويب وبوابة استشارية عامة ومفتوحة للإجابة ونقاش كافة المسائل الفكرية والأبحاث بدون أي شروط مسبقة.")
        
        advisor_query = st.text_area("اطرح سؤالك أو استشارتك العلمية هنا بشكل مفصل:", height=150)
        
        if st.button("إرسال الاستشارة إلى المستشار الذكي", key="tab9_btn"):
            if not advisor_query.strip():
                st.warning("⚠️ يرجى كتابة استفسارك أولاً.")
            else:
                simulate_processing()
                # سياسة الحساب التلقائي الصارمة لحماية رصيد السيرفر دون إظهار العداد اللفظي للمستخدم
                simulated_response_text = "هذا رد أكاديمي استشاري مفصل ومبني على المعايير العلمية الدقيقة لنموذج GPT-4o-mini لمعالجة الأبحاث..."
                total_words = len(advisor_query.split()) + len(simulated_response_text.split())
                calculated_advisor_cost = math.ceil(total_words / 600)  # كل 600 كلمة مستهلكة (سؤال + جواب) = 1 محاولة
                
                if user_info['attempts'] < calculated_advisor_cost:
                    st.error("❌ رصيدك الحالي منخفض جداً لإتمام صياغة الاستشارة الشاملة عبر المستشار الذكي.")
                else:
                    if st.session_state['logged_in']:
                        st.session_state['active_codes'][current_code]['attempts'] -= calculated_advisor_cost
                    st.write("---")
                    st.markdown("### 🟢 رد وتوجيه المستشار الأكاديمي:")
                    st.write(simulated_response_text + " (تم معالجة وضبط الفروق المعرفية بدقة فائقة).")
                    st.caption(f"*تم توليد المحتوى بنجاح واقتطاع المحاولات المستهلكة تلقائياً من الكود بنجاح وفق السياسة المالية الآمنة.*")
                    st.rerun()

    # 6. عبارة الحقوق أسفل الصفحة بعد تسجيل الدخول
    st.markdown('<div class="footer">ScholarNode Academy © 2026</div>', unsafe_allow_html=True)


# ==========================================
# 4. لوحة تحكم الإدارة السرية (HAYDER_2026$$$)
# ==========================================
elif st.session_state['is_admin'] and not st.session_state['admin_view_as_user']:
    
    st.markdown("""
    <div style="background-color: #ffe680; border: 2px solid #ffcc00; padding: 15px; border-radius: 5px; margin-bottom: 25px;">
        <h2 style="color: #000000; margin:0; text-align:center;">🛠️ لوحة تحكم الإدارة السرية العليا | ScholarNode</h2>
    </div>
    """, unsafe_allow_html=True)

    # تقسيم لوحة الإدارة إلى ثلاثة تبويبات تنظيمية طبقاً لطلبك
    admin_tabs = st.tabs([
        "👁️ الواجهة كما تظهر للمشترك بعد تسجيل الدخول", 
        "🔑 توليد الكودات الخاصة ببطاقات الاشتراك",
        "📊 مراجعة وفحص كافة الكودات النشطة بالسيرفر"
    ])

    # ---- تبويب الإدارة 1: الانتقال لمعاينة واجهة المشترك ----
    with admin_tabs[0]:
        st.subheader("معاينة تجريبية حية لنظام العميل")
        st.write("عند الضغط على الزر أدناه، ستفتح لك واجهة المنصة المتكاملة والتبويبات التسعة تماماً كما يراها الطالب الباحث لمراجعة الأداء واختبار التنسيق.")
        if st.button("🚀 الانتقال المباشر لطور محاكاة المشترك"):
            st.session_state['admin_view_as_user'] = True
            st.rerun()

    # ---- تبويب الإدارة 2: توليد الأكواد وحفظها مع زر النسخ ----
    with admin_tabs[1]:
        st.subheader("🔑 نظام توليد كروت التفعيل الذكي")
        st.write("قم باختيار فئة الكارت المراد إصداره بالدينار العراقي، وسيقوم النظام تلقائياً بتطبيق السياسة المالية التراكمية وربط الصلاحية الزمنية المناسبة لها.")
        
        selected_tier = st.selectbox("اختر فئة كارت الاشتراك المراد إنشاؤه وصناعته:", list(CARDS_DATA.keys()), format_func=lambda x: f"{x:,} دينار عراقي")
        
        # عرض معلومات الفئة المختارة للتأكيد قبل الإنشاء
        tier_info = CARDS_DATA[selected_tier]
        st.write(f"ℹ️ الكارت الناتج سيمنح رصيد: **{tier_info['attempts']} محاولة** | صالح للاستخدام لمدة: **{tier_info['days']} يوم**.")
        
        if st.button("توليد وإصدار كود التفعيل المعتمد الآن"):
            # إنشاء كود فريد آمن ومقاوم للتخمين والاختراق
            generated_key = f"SCHOLAR-{selected_tier // 1000}K-{str(uuid.uuid4())[:8].upper()}"
            
            # حفظ وإدراج الكود فوراً في قاعدة بيانات السيرفر النشطة لمنع تكرار الكود المنهي وضمان الاستخدام لمرة واحدة
            st.session_state['active_codes'][generated_key] = {
                "attempts": tier_info['attempts'],
                "days": tier_info['days'],
                "tier": selected_tier,
                "created_at": datetime.now().strftime("%Y-%m-%d")
            }
            st.success(f"🎉 تم توليد وإصدار كود الاشتراك بنجاح لـ فئة {selected_tier:,} د.ع!")
            
            # حقل نصي مخصص ومزود بجانبه خيار وجهاز النسخ الفوري المباشر بضغطة واحدة
            st.text_input("📋 كود التفعيل المولد جاهز للنسخ الآن:", value=generated_key, readonly=True)
            st.caption("يمكنك نسخ الكود مباشرة من الحقل وإرساله للطالب المشترك لبدء الاستخدام من أي جهاز.")

    # ---- تبويب الإدارة 3: مراجعة كافة الأكواد النشطة بالفهرس ----
    with admin_tabs[2]:
        st.subheader("📊 كودات التفعيل النشطة وحالة استهلاك السيرفر")
        st.write("جدول شامل يستعرض الأكواد الموزعة والمحاولات المتبقية لكل باحث لضمان المراقبة اللوجستية:")
        
        if len(st.session_state['active_codes']) == 0:
            st.info("لا توجد أكواد مفعّلة حالياً بالسيرفر.")
        else:
            # بناء جدول بيانات ديناميكي للإدارة للمراقبة الشاملة للأمان
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
            
    st.markdown("---")
    if st.button("🚪 خروج من حساب الإدارة العيا"):
        logout()
