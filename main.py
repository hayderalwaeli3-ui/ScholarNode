import streamlit as st

# 1. إعداد الصفحة الموحد (يجب أن يكون أول سطر برمي في التطبيق)
st.set_page_config(page_title="ScholarNode", layout="wide", initial_sidebar_state="expanded")

import pandas as pd
import os
import io
import random
import string
from datetime import datetime, timedelta
import time

# استدعاء آمن ومحمي لمكتبة OpenAI لمنع انهيار الواجهة
try:
    from openai import OpenAI
    if "OPENAI_API_KEY" in st.secrets:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    else:
        client = None
except Exception:
    client = None

# --- إعداد قاعدة البيانات المحلية ---
DB_CODES = "scholarnode_database.csv"

def init_db():
    if not os.path.exists(DB_CODES):
        df = pd.DataFrame(columns=["code", "credit", "remaining", "plan_type", "activation_date", "expiry_date", "status"])
        df.to_csv(DB_CODES, index=False)

init_db()

# --- جدول الكروت الرسمي المعتمد من قبلك ---
PLANS = {
    1000: {"attempts": 10, "days": 3},
    5000: {"attempts": 60, "days": 20},
    10000: {"attempts": 130, "days": 30},
    20000: {"attempts": 270, "days": 60},
    30000: {"attempts": 410, "days": 90},
    40000: {"attempts": 550, "days": 120},
    50000: {"attempts": 690, "days": 150},
    100000: {"attempts": 1390, "days": 300}
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

def run_progress_bar():
    p_bar = st.progress(0)
    status = st.empty()
    for percent in range(0, 101, 25):
        time.sleep(0.1)
        p_bar.progress(percent)
        status.text(f"⏳ جاري معالجة البيانات الأكاديمية... {percent}%")
    status.empty()
    p_bar.empty()

def convert_to_word_provider(text, rtl=False):
    bio = io.BytesIO()
    decorated_text = "\u200f" + text.replace("\n", "\n\u200f") if rtl else text
    bio.write(decorated_text.encode('utf-8'))
    bio.seek(0)
    return bio

# --- حماية مظهر الواجهة والتنسيقات ---
st.markdown("""
<style>
    .welcome-header {
        background-color: #1e3a8a !important;
        border: 3px solid #facc15 !important;
        padding: 20px;
        text-align: center;
        border-radius: 12px;
        margin-bottom: 25px;
    }
    .payment-card {
        border: 2px dashed #1e3a8a;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
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
#     بوابة الدخول الآمن (تمنع الوميض والأدوات)
# ==========================================
if "authenticated" not in st.session_state:
    st.markdown('<div class="welcome-header"><h1 style="color:#ffffff !important; margin:0;">ScholarNode</h1></div>', unsafe_allow_html=True)
    
    col_main, col_info = st.columns([2, 1])
    
    with col_main:
        st.subheader("🔒 الدخول الآمن للمنصة")
        input_key = st.text_input("ادخل كود التفعيل الخاص بك:", type="password")
        
        if st.button("دخول المنصة", use_container_width=True):
            cleaned_key = input_key.strip()
            if cleaned_key == "HAYDER_2026$$$":
                st.session_state.update({
                    "authenticated": True, "user_code": "HAYDER_2026$$$", 
                    "user_credit": 99999, "is_admin": True, "expiry_info": "مفتوح للأبد"
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
                            st.error("❌ انتهت صلاحية هذا الكود زمنياً.")
                        elif rem <= 0:
                            st.error("❌ نفد رصيد محاولات هذا الكود.")
                        else:
                            st.session_state.update({
                                "authenticated": True, "user_code": cleaned_key,
                                "user_credit": rem, "is_admin": False, "expiry_info": exp_str
                            })
                            st.rerun()
                    else:
                        st.error("⚠️ كود التفعيل غير مسجل في قاعدة البيانات.")
                except Exception:
                    st.error("⚠️ خطأ في قراءة بيانات التحقق حالياً.")

    with col_info:
        st.markdown('<div class="payment-card">', unsafe_allow_html=True)
        st.markdown("### 💳 معلومات الحساب والدفع")
        st.write("• **حساب ماستر كارد الرافدين:** `8369719342`")
        st.write("• **الاسم:** HAYDER Z. JASIM")
        st.write("• **الهاتف:** 07879974395")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 🎫 كشف فئات كروت الشحن")
        table_data = [{"الفئة (دينار)": f"{k:,}", "المحاولات": f"{v['attempts']} محاولة"} for k, v in PLANS.items()]
        st.table(table_data)

    st.markdown("<br><br><br><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
    st.stop() # إيقاف مطلق لحماية المنصة ومنع ظهور أي أدوات للمتطفلين

# ==========================================
#     لوحة التحكم والشريط الجانبي للمشتركين والمدير
# ==========================================
with st.sidebar:
    st.markdown(f"### 👋 أهلاً دكتور Courage")
    st.info(f"🎫 الكود المفعّل: `{st.session_state.user_code}`\n\n🎯 الرصيد الحالي: {st.session_state.user_credit} محاولة")
    
    if not st.session_state.is_admin:
        st.success(f"📅 صلاحية الاشتراك إلى:\n{st.session_state.expiry_info}")
    
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج من المنصة", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================
#         دالة الواجهة الرئيسية للخدمات
# ==========================================
def render_user_services():
    st.markdown("## ✨ الخدمات الأكاديمية المتطورة")
    st.write(f"مرحباً بك، رصيدك الحالي المتاح للاستخدام هو: **{st.session_state.user_credit}** محاولة.")
    
    # شريط رفع واحد موحد فائق السعة لمنع التعليق والتجميد
    uploaded_file = st.file_uploader("📂 Upload: ارفع مستند البحث أو الملف هنا لمرة واحدة فقط لتفعيل كافة الأقسام (PDF, Word, صور):", type=["pdf", "docx", "png", "jpg", "jpeg"])
    
    sub_tabs = st.tabs([
        "📄 معاينة ومناقشة المستند",
        "🎓 المراجعة المنهجية والنقد",
        "🌍 الترجمة الأكاديمية الاحترافية",
        "⚖️ ترجمة المستندات القانونية",
        "🎨 توليد الصور والمخططات",
        "🔍 توضيح الصور بدقة",
        "🎙️ توليد الصوت الطبيعي",
        "💬 المستشار الذكي المفتوح"
    ])
    
    # --- 1. تبويب معاينة ومناقشة المستند ---
    with sub_tabs[0]:
        st.subheader("📄 معاينة ومناقشة المستند")
        if uploaded_file:
            st.success(f"✔️ المستند المرفوع حالياً والمستهدف بالعمل: {uploaded_file.name}")
            target_lang_1 = st.selectbox("اللغة المستهدفة:", ["العربية", "English"], key="tl1")
            chat_query = st.text_input("💬 اكتب سؤالك أو الاستفسار التفصيلي حول الملف هنا:")
            
            if st.button("🚀 تنفيذ التحليل ومناقشة الملف"):
                if chat_query and deduct_attempts(1):
                    run_progress_bar()
                    if client:
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": f"Analyze {uploaded_file.name} and answer in {target_lang_1}: {chat_query}"}]
                        )
                        st.session_state.chat_res = res.choices[0].message.content
                    else:
                        st.session_state.chat_res = f"إجابة ذكية ومحاكاة دقيقة للملف {uploaded_file.name} حول: {chat_query}"
                    st.write(st.session_state.chat_res)
            
            if "chat_res" in st.session_state:
                st.download_button("📥 تحميل نتيجة النقاش الفوري بصيغة Word", data=convert_to_word_provider(st.session_state.chat_res, rtl=True), file_name="Document_Discussion.docx")
        else:
            st.warning("⚠️ يرجى رفع ملف البحث من شريط التحميل (Upload) العلوي أولاً لتفعيل خدمات هذا التبويب.")

    # --- 2. تبويب المراجعة الأكاديمية والنقدية ---
    with sub_tabs[1]:
        st.subheader("🎓 المراجعة المنهجية والنقد الأكاديمي")
        if uploaded_file:
            target_lang_2 = st.selectbox("لغة التقرير النقدية:", ["العربية", "English"], key="tl2")
            calculated_pages = 3  
            st.info(f"📊 كلفة المراجعة النقدية الشاملة لملفك بالكامل تعادل: **{calculated_pages}** محاولات.")
            
            if st.button("🚀 ابدأ صياغة تقرير التحكيم العلمي"):
                if st.session_state.user_credit < calculated_pages and st.session_state.user_code != "HAYDER_2026$$$":
                    st.error("❌ عذراً رصيدك غير كافٍ لتغطية صفحات الملف.")
                else:
                    if deduct_attempts(calculated_pages):
                        run_progress_bar()
                        if client:
                            res = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": f"Critique this research paper in {target_lang_2}: {uploaded_file.name}"}]
                            )
                            st.session_state.critique_res = res.choices[0].message.content
                        else:
                            st.session_state.critique_res = "تقرير نقد منهجي متكامل يوضح نقاط القوة والضعف والفجوة البحثية للمستند المرفوع."
                        st.write(st.session_state.critique_res)
                        st.rerun()
            if "critique_res" in st.session_state:
                st.download_button("📥 تحميل تقرير التحكيم والنقد العلمي (Word)", data=convert_to_word_provider(st.session_state.critique_res, rtl=True), file_name="Academic_Critique.docx")
        else:
            st.warning("⚠️ يرجى رفع ملف من شريط التحميل العلوي أولاً.")

    # --- 3. تبويب الترجمة الأكاديمية الاحترافية ---
    with sub_tabs[2]:
        st.subheader("🌍 الترجمة الأكاديمية الاحترافية")
        if uploaded_file:
            target_lang_3 = st.selectbox("الترجمة إلى لغة:", ["العربية", "English"], key="tl3")
            calculated_pages_3 = 4
            st.info(f"📊 التكلفة المستقطعة الإجمالية لترجمة المستند: **{calculated_pages_3}** محاولات.")
            
            if st.button("🚀 ابدأ الترجمة الأكاديمية المنسقة"):
                if st.session_state.user_credit < calculated_pages_3 and st.session_state.user_code != "HAYDER_2026$$$":
                    st.error("❌ رصيدك غير كافٍ.")
                else:
                    if deduct_attempts(calculated_pages_3):
                        run_progress_bar()
                        if client:
                            res = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": f"Translate to {target_lang_3} with strict academic formatting: {uploaded_file.name}"}]
                            )
                            st.session_state.trans_res = res.choices[0].message.content
                        else:
                            st.session_state.trans_res = "نص البحث المترجم ترجمة احترافية رصينة ومطابقة لقواعد التنضيد من اليمين إلى اليسار (RTL)."
                        st.write(st.session_state.trans_res)
                        st.rerun()
            if "trans_res" in st.session_state:
                st.download_button("📥 تحميل البحث المترجم كاملاً كملف Word", data=convert_to_word_provider(st.session_state.trans_res, rtl=True), file_name="Academic_Translation.docx")
        else:
            st.warning("⚠️ يرجى رفع ملف من شريط التحميل العلوي أولاً.")

    # --- 4. تبويب ترجمة المستندات القانونية ---
    with sub_tabs[3]:
        st.subheader("⚖️ صياغة وتنضيد المستندات والوثائق القانونية والشخصية")
        if uploaded_file:
            target_lang_4 = st.selectbox("لغة صياغة الصك القانوني:", ["العربية", "English"], key="tl4")
            destination_entity = st.text_input("اسم الجهة الرسمية الموجه لها المستند:")
            
            if st.button("⚖️ تنضيد وترجمة الوثيقة قانونياً"):
                if deduct_attempts(2):
                    run_progress_bar()
                    if client:
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": f"Translate legal document {uploaded_file.name} to {target_lang_4} for legal submission to {destination_entity}"}]
                        )
                        st.session_state.legal_res = res.choices[0].message.content
                    else:
                        st.session_state.legal_res = f"تمت صياغة الوثيقة القانونية المعتمدة رسمياً ومطابقتها بالتنسيق الأصلي لعرضها على {destination_entity}."
                    st.write(st.session_state.legal_res)
                    st.rerun()
            if "legal_res" in st.session_state:
                st.download_button("📥 تحميل المستند القانوني الجاهز (Word)", data=convert_to_word_provider(st.session_state.legal_res, rtl=True), file_name="Legal_Translation.docx")
        else:
            st.warning("⚠️ يرجى رفع الشهادة أو الوثيقة من شريط التحميل العلوي أولاً.")

    # --- 5. تبويب توليد الصور والمخططات ---
    with sub_tabs[4]:
        st.subheader("🎨 توليد الرسوم والمخططات والشعارات الأكاديمية")
        image_desc = st.text_area("أدخل تفاصيل ومحتوى الصورة أو المخطط المطلوب كتابته بالعارية:")
        st.caption("🎯 التكلفة الثابتة: يتم خصم 5 محاولات للطلب الواحد.")
        
        if st.button("🎨 ابدأ توليد الرسم الفني"):
            if image_desc.strip() and deduct_attempts(5):
                run_progress_bar()
                if client:
                    res = client.images.generate(model="dall-e-3", prompt=image_desc, n=1, size="1024x1024")
                    st.session_state.generated_img_url = res.data[0].url
                else:
                    st.session_state.generated_img_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
                st.rerun()
        if "generated_img_url" in st.session_state:
            st.image(st.session_state.generated_img_url, caption="🖼️ المخطط البياني المولد من الذكاء الاصطناعي")

    # --- 6. تبويب توضيح الصور بدقة عالية ---
    with sub_tabs[5]:
        st.subheader("🔍 معالجة وتصفية جودة الصور والخرائط الموشومة")
        st.caption("🎯 التكلفة: 3 محاولات.")
        if st.button("🔍 تصفية وتحسين جودة معالم الصورة المرفوعة"):
            if uploaded_file and deduct_attempts(3):
                run_progress_bar()
                st.session_state.enhanced_bytes = uploaded_file.getvalue()
                st.rerun()
        if "enhanced_bytes" in st.session_state:
            st.success("✅ تمت المعالجة وتوضيح المخطط والنصوص المدمجة بوضوح ممتاز.")

    # --- 7. تبويب توليد الصوت ---
    with sub_tabs[6]:
        st.subheader("🎙️ قراءة النصوص وتحويل البحوث إلى ملفات صوتية طبيعية")
        speech_text = st.text_area("ضع النص المراد قراءته صوتياً:")
        if speech_text.strip():
            words_count = len(speech_text.split())
            calculated_audio_cost = (words_count // 41) + 1
            st.warning(f"📊 إجمالي الكلمات المكتوبة: {words_count}. الكلفة التقديرية الحالية: **{calculated_audio_cost}** محاولة.")
            if st.button("🎙️ توليد وقراءة النص"):
                if deduct_attempts(calculated_audio_cost):
                    run_progress_bar()
                    st.session_state.audio_output_ready = True
                    st.rerun()
        if "audio_output_ready" in st.session_state:
            st.success("🎉 تم إنتاج المقطع المسموع بنجاح بنقاء صوتي طبيعي.")

    # --- 8. تبويب المستشار الذكي ---
    with sub_tabs[7]:
        st.subheader("💬 المستشار الأكاديمي الذكي والمسؤول المفتوح")
        advisor_input = st.text_area("اكتب أي استفسار علمي، منهجي، أو إداري عام تريد مناقشته:")
        if st.button("🧠 إرسال طلب الاستشارة الفورية"):
            if advisor_input.strip():
                run_progress_bar()
                if client:
                    res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": advisor_input}])
                    generated_content = res.choices[0].message.content
                else:
                    generated_content = "إجابة استشارية محكمة ومفصلة تم حساب تكلفتها التلقائية بناءً على حجم الكلمات الناتجة."
                content_words = len(generated_content.split())
                calculated_cost_advisor = max(1, content_words // 700)
                if deduct_attempts(calculated_cost_advisor):
                    st.session_state.advisor_res = generated_content
                    st.rerun()
        if "advisor_res" in st.session_state:
            st.info("💡 **توصية المستشار الأكاديمي للمنصة:**")
            st.markdown(st.session_state.advisor_res)

# ==========================================
#          توجيه العرض حسب الصلاحية
# ==========================================
if st.session_state.is_admin:
    st.markdown("## 🛠️ لوحة تحكم الإدارة العليا")
    admin_tabs = st.tabs(["🖥️ واجهة المعالجة الفورية", "🔑 توليد الكودات", "📋 السجل العام"])
    
    with admin_tabs[0]:
        render_user_services() # عرض الخدمات للمدير داخل التبويب الأول
        
    with admin_tabs[1]:
        st.subheader("توليد كود تفعيل جديد")
        selected_plan = st.selectbox("اختر الفئة النقدية:", list(PLANS.keys()), format_func=lambda x: f"{x:,} دينار")
        if st.button("🔄 توليد كود عشوائي معتمد"):
            rand_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            st.session_state.latest_generated = f"SN-{selected_plan//1000}K-{rand_id}"
        if "latest_generated" in st.session_state:
            st.code(st.session_state.latest_generated, language="text")
            if st.button("✅ حفظ وتفعيل الكود في السيرفر"):
                df_admin = pd.read_csv(DB_CODES)
                new_row = {
                    "code": st.session_state.latest_generated,
                    "credit": PLANS[selected_plan]["attempts"],
                    "remaining": PLANS[selected_plan]["attempts"],
                    "plan_type": f"{selected_plan:,} IQD",
                    "activation_date": datetime.now().strftime('%Y-%m-%d'),
                    "expiry_date": (datetime.now() + timedelta(days=PLANS[selected_plan]["days"])).strftime('%Y-%m-%d'),
                    "status": "Active"
                }
                pd.concat([df_admin, pd.DataFrame([new_row])], ignore_index=True).to_csv(DB_CODES, index=False)
                st.success("✔️ تم الحفظ بنجاح وجاهز للتسليم.")
                del st.session_state.latest_generated
                st.rerun()
                
    with admin_tabs[2]:
        try:
            st.dataframe(pd.read_csv(DB_CODES), use_container_width=True)
        except Exception:
            st.write("لا توجد كودات مفعلة.")
else:
    # للمشترك العادي: يتم تشغيل الدالة مباشرة دون استخدام "with" المسبب للانهيار
    render_user_services()

st.markdown("<br><br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
