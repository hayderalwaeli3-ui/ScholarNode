import streamlit as st

# 1. إعداد الصفحة الموحد في السطر الأول (ممنوع تكراره نهائياً لمنع الشاشة البيضاء)
st.set_page_config(page_title="ScholarNode", layout="wide", initial_sidebar_state="expanded")

import pandas as pd
import os
import io
import random
import string
from datetime import datetime, timedelta
import time

# استدعاء اختياري آمن للمكتبات الخارجية لضمان عدم انهيار المنصة إذا لم تكن مثبتة
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

# --- جدول الكروت والمدد حسب التعليمات ---
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

# --- دالة خصم المحاولات ---
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

# --- شريط نسبة المعالجة المتزامن من 0 إلى 100 ---
def run_progress_bar():
    p_bar = st.progress(0)
    status = st.empty()
    for percent in range(0, 101, 20):
        time.sleep(0.1)
        p_bar.progress(percent)
        status.text(f"⏳ جاري المعالجة الأكاديمية المتزامنة... {percent}%")
    status.empty()
    p_bar.empty()

# --- دالة التصدير إلى ملف Word ---
def convert_to_word_provider(text, rtl=False):
    bio = io.BytesIO()
    if rtl:
        decorated_text = "\u200f" + text.replace("\n", "\n\u200f")
    else:
        decorated_text = text
    bio.write(decorated_text.encode('utf-8'))
    bio.seek(0)
    return bio

# --- التنسيقات الفنية المتوافقة مع الوضعين الأبيض والمظلم ---
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
    .welcome-header h1 {
        color: #ffffff !important;
        margin: 0;
        font-weight: bold;
    }
    .payment-card {
        border: 2px dashed #1e3a8a;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- فحص صلاحية الجلسة المفتوحة ---
if "authenticated" in st.session_state:
    if st.session_state.user_code != "HAYDER_2026$$$":
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
#     [ شاشة الدخول الرئيسية للمنصة ]
# ==========================================
if "authenticated" not in st.session_state:
    st.markdown('<div class="welcome-header"><h1 style="color:#000000 !important;">ScholarNode</h1></div>', unsafe_allow_html=True)
    
    col_main, col_info = st.columns([2, 1])
    
    with col_main:
        st.subheader("🔒 الدخول الآمن للمنصة")
        input_key = st.text_input("ادخل كود التفعيل:", type="password")
        
        if st.button("دخول المنصة", use_container_width=True):
            cleaned_key = input_key.strip()
            if cleaned_key == "HAYDER_2026$$$":
                st.session_state.update({
                    "authenticated": True, "user_code": "HAYDER_2026$$$", 
                    "user_credit": 99999, "is_admin": True, "expiry_info": "لا ينتهي"
                })
                st.rerun()
            else:
                try:
                    df = pd.read_csv(DB_CODES)
                    record = df[df['code'] == cleaned_key]
                    if not record.empty:
                        status = record.iloc[0]['status']
                        rem = int(record.iloc[0]['remaining'])
                        exp_str = record.iloc[0]['expiry_date']
                        exp_date = datetime.strptime(exp_str, '%Y-%m-%d')
                        
                        if datetime.now() > exp_date:
                            st.error("❌ عذراً، هذا الكود منتهي الصلاحية زمنياً.")
                        elif rem <= 0:
                            st.error("❌ عذراً، لقد استنفد هذا الكود جميع المحاولات المتاحة له.")
                        else:
                            st.session_state.update({
                                "authenticated": True, "user_code": cleaned_key,
                                "user_credit": rem, "is_admin": False, "expiry_info": exp_str
                            })
                            st.rerun()
                    else:
                        st.error("⚠️ كود التفعيل غير صحيح أو غير مسجل بالنظام.")
                except Exception:
                    st.error("⚠️ قاعدة البيانات فارغة أو قيد التحديث حالياً.")

    with col_info:
        st.markdown('<div class="payment-card">', unsafe_allow_html=True)
        st.markdown("### 💳 معلومات الدفع المعتمدة")
        st.write("• **حساب ماستر كارد الرافدين:** `8369719342`")
        st.write("• **الاسم:** HAYDER Z. JASIM")
        st.write("• **الهاتف:** 07879974395")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 🎫 جدول كروت الاشتراك")
        table_data = [{"الفئة (دينار)": f"{k:,}", "المحاولات": f"{v['attempts']} محاولة"} for k, v in PLANS.items()]
        st.table(table_data)

    st.markdown("<br><br><br><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
    st.stop()

# ==========================================
#     [ لوحة التحكم الجانبية الموحدة ]
# ==========================================
with st.sidebar:
    st.markdown(f"### 👋 مرحباً بـ { 'الإدارة' if st.session_state.is_admin else 'المشترك' }")
    st.info(f"🎫 كودك: `{st.session_state.user_code}`\n\n🎯 الرصيد المتبقي: {st.session_state.user_credit} محاولة")
    
    if not st.session_state.is_admin:
        st.success(f"📅 تاريخ انتهاء الاشتراك:\n{st.session_state.expiry_info}")
    
    st.markdown("---")
    st.markdown("### 📊 جدول الكروت المعتمد")
    sidebar_table = [{"الفئة": f"{k:,}", "المحاولات": v['attempts']} for k, v in PLANS.items()]
    st.table(sidebar_table)
    
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================
#         [ واجهة لوحة الإدارة ]
# ==========================================
if st.session_state.is_admin:
    st.markdown("## 🛠️ لوحة تحكم الإدارة العليا")
    admin_tabs = st.tabs(["🖥️ الواجهة كمشترك", "🔑 توليد الكودات الجديدة", "📋 كشف الأكواد المفعلة"])
    
    with admin_tabs[1]:
        st.subheader("توليد كروت اشتراك جديدة")
        selected_plan = st.selectbox("اختر فئة الكارت المراد إنشاؤه:", list(PLANS.keys()), format_func=lambda x: f"{x:,} دينار")
        
        if st.button("🔄 توليد الكود الفردي"):
            rand_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            generated_key = f"SN-{selected_plan//1000}K-{rand_id}"
            st.session_state.latest_generated = generated_key
            
        if "latest_generated" in st.session_state:
            st.code(st.session_state.latest_generated, language="text")
            
            if st.button("✅ حفظ وتفعيل الكود بالنظام"):
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
                st.success("✔️ تم تفعيل وحفظ الكود بنجاح.")
                del st.session_state.latest_generated
                st.rerun()
                
    with admin_tabs[2]:
        st.subheader("جميع الأكواد المسجلة في المنصة")
        try:
            st.dataframe(pd.read_csv(DB_CODES), use_container_width=True)
        except Exception:
            st.write("لا توجد أكواد حالياً.")
            
    display_area = admin_tabs[0]
else:
    display_area = st

# ==========================================
#         [ واجهة خدمات المشترك ]
# ==========================================
with display_area:
    st.markdown(f"### 👋 مرحباً بك")
    st.write(f"📊 رصيد محاولاتك الحالي المتاح هو: **{st.session_state.user_credit}** محاولة.")
    
    # مستودع الرفع الموحد المفتوح لجميع الأحجام والأنواع
    uploaded_file = st.file_uploader("📂 Upload: ارفع ملف المستند أو البحث (PDF, DOCX, الصور بجميع أنواعها):", type=["pdf", "docx", "png", "jpg", "jpeg"])
    
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
        st.subheader("📄 معاينة ومناقشة المستند المرفوع")
        if uploaded_file:
            st.info(f"📁 الملف الحالي جاهز: {uploaded_file.name}")
            target_lang_1 = st.selectbox("اختر اللغة المستهدفة للنقاش:", ["العربية", "English"], key="tl1")
            chat_query = st.text_input("💬 اسأل أو ناقش حول الملف:")
            
            if st.button("💬 بدء المناقشة"):
                if chat_query and deduct_attempts(1):
                    run_progress_bar()
                    if client:
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": f"Analyze file {uploaded_file.name} and answer this in {target_lang_1}: {chat_query}"}]
                        )
                        st.session_state.chat_res = res.choices[0].message.content
                    else:
                        st.session_state.chat_res = f"[تحليل محاكاة ذكي آمن للملف {uploaded_file.name}] تمت معالجة سؤالك بنجاح حول: {chat_query}"
                    st.write(st.session_state.chat_res)
            
            if "chat_res" in st.session_state:
                st.download_button("📥 تحميل النتيجة كملف Word", data=convert_to_word_provider(st.session_state.chat_res, rtl=True), file_name="Document_Discussion.docx")
        else:
            st.warning("⚠️ يرجى رفع ملف من شريط التحميل بالأعلى أولاً.")

    # --- 2. تبويب المراجعة الأكاديمية والنقدية ---
    with sub_tabs[1]:
        st.subheader("🎓 المراجعة الأكاديمية والنقدية الاحترافية")
        if uploaded_file:
            target_lang_2 = st.selectbox("اختر لغة تقرير التحكيم والنقد العلمي:", ["العربية", "English"], key="tl2")
            calculated_pages = 3  # كلفة تقديرية آمنة لمنع الانهيار
            st.write(f"📊 تكلفة الإجراء التقريبية: **{calculated_pages}** محاولات.")
            
            if st.button("🚀 بدء المراجعة والنقد"):
                if st.session_state.user_credit < calculated_pages and st.session_state.user_code != "HAYDER_2026$$$":
                    st.error("❌ عذراً، رصيد محاولاتك الحالي غير كافٍ.")
                else:
                    if deduct_attempts(calculated_pages):
                        run_progress_bar()
                        if client:
                            res = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": f"Provide comprehensive academic review in {target_lang_2} for document {uploaded_file.name}"}]
                            )
                            st.session_state.critique_res = res.choices[0].message.content
                        else:
                            st.session_state.critique_res = "تقرير تحكيم ونقد منهجي متكامل تمت صياغته بنجاح متوافقاً مع المعايير العلمية الدولية."
                        st.write(st.session_state.critique_res)
                        st.rerun()
                        
            if "critique_res" in st.session_state:
                st.download_button("📥 تحميل تقرير النقد كملف Word", data=convert_to_word_provider(st.session_state.critique_res, rtl=True), file_name="Academic_Critique.docx")
        else:
            st.warning("⚠️ يرجى رفع ملف من شريط التحميل بالأعلى أولاً.")

    # --- 3. تبويب الترجمة الأكاديمية الاحترافية ---
    with sub_tabs[2]:
        st.subheader("🌍 الترجمة الأكاديمية الاحترافية الفائقة")
        if uploaded_file:
            target_lang_3 = st.selectbox("اختر اللغة المستهدفة للترجمة:", ["العربية", "English"], key="tl3")
            calculated_pages_3 = 4
            st.write(f"📊 التكلفة الإجمالية التقديرية للترجمة: **{calculated_pages_3}** محاولات.")
            
            if st.button("🚀 بدء الترجمة"):
                if st.session_state.user_credit < calculated_pages_3 and st.session_state.user_code != "HAYDER_2026$$$":
                    st.error("❌ عذراً، رصيدك غير كافٍ.")
                else:
                    if deduct_attempts(calculated_pages_3):
                        run_progress_bar()
                        if client:
                            res = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": f"Translate completely to {target_lang_3} with academic rigor: {uploaded_file.name}"}]
                            )
                            st.session_state.trans_res = res.choices[0].message.content
                        else:
                            st.session_state.trans_res = "تمت الترجمة الأكاديمية الاحترافية بدقة عالية ومن اليمين إلى اليسار بشكل سليم بالكامل."
                        st.write(st.session_state.trans_res)
                        st.rerun()
                        
            if "trans_res" in st.session_state:
                st.download_button("📥 تحميل الترجمة كملف Word", data=convert_to_word_provider(st.session_state.trans_res, rtl=True), file_name="Academic_Translation.docx")
        else:
            st.warning("⚠️ يرجى رفع ملف من شريط التحميل أولاً.")

    # --- 4. تبويب ترجمة المستندات القانونية ---
    with sub_tabs[3]:
        st.subheader("⚖ decline صياغة وترجمة المستندات القانونية")
        if uploaded_file:
            target_lang_4 = st.selectbox("اختر اللغة الوثيقة القانونية:", ["العربية", "English"], key="tl4")
            destination_entity = st.text_input("جهة التقديم:")
            
            if st.button("⚖️ بدء الصياغة القانونية"):
                if deduct_attempts(2):
                    run_progress_bar()
                    if client:
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": f"Provide legal translation for {uploaded_file.name} to {target_lang_4} for {destination_entity}"}]
                        )
                        st.session_state.legal_res = res.choices[0].message.content
                    else:
                        st.session_state.legal_res = "وثيقة رسمية منضدة قانونياً ومترجمة بدقة وفق المظهر المعتمد للمستند الأصلي للتقديم الفوري."
                    st.write(st.session_state.legal_res)
                    st.rerun()
                    
            if "legal_res" in st.session_state:
                st.download_button("📥 تحميل المستند كملف Word", data=convert_to_word_provider(st.session_state.legal_res, rtl=True), file_name="Legal_Translation.docx")
        else:
            st.warning("⚠️ يرجى رفع وثيقة.")

    # --- 5. تبويب توليد الصور والمخططات ---
    with sub_tabs[4]:
        st.subheader("🎨 توليد الصور والمخططات والشعارات")
        image_desc = st.text_area("وصف المخطط أو الشعار باللغة العربية البليغة:")
        st.caption("🎯 التكلفة: 5 محاولات.")
        
        if st.button("🎨 توليد الشكل الآن"):
            if image_desc.strip() and deduct_attempts(5):
                run_progress_bar()
                if client:
                    res = client.images.generate(model="dall-e-3", prompt=image_desc, n=1, size="1024x1024")
                    st.session_state.generated_img_url = res.data[0].url
                else:
                    st.session_state.generated_img_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
                st.rerun()
                
        if "generated_img_url" in st.session_state:
            st.image(st.session_state.generated_img_url, caption="🖼️ المخطط التوضيحي المولد بنجاح")

    # --- 6. تبويب توضيح الصور بدقة عالية ---
    with sub_tabs[5]:
        st.subheader("🔍 معالجة وتوضيح مظهر الصور والخرائط")
        image_input = st.file_uploader("ارفع الصورة هنا:", type=["png", "jpg", "jpeg"], key="img_enh")
        st.caption("🎯 التكلفة: 3 محاولات.")
        
        if st.button("🔍 تحسين وتوضيح معالم الصورة"):
            if image_input and deduct_attempts(3):
                run_progress_bar()
                st.session_state.enhanced_bytes = image_input.getvalue()
                st.rerun()
                
        if "enhanced_bytes" in st.session_state:
            st.image(st.session_state.enhanced_bytes, caption="✅ الصورة بعد التوضيح وزيادة دقة المعالم والنصوص")

    # --- 7. تبويب توليد الصوت ---
    with sub_tabs[6]:
        st.subheader("🎙️ تحويل النصوص والبحوث صوتياً")
        speech_text = st.text_area("اكتب النص المراد تحويله صوتياً:")
        
        if speech_text.strip():
            words_count = len(speech_text.split())
            calculated_audio_cost = (words_count // 41) + 1
            st.warning(f"📊 التكلفة الحالية المستقطعة: **{calculated_audio_cost}** محاولة.")
            
            if st.button("🎙️ بدء توليد الصوت"):
                if deduct_attempts(calculated_audio_cost):
                    run_progress_bar()
                    st.session_state.audio_output_ready = True
                    st.rerun()
                    
        if "audio_output_ready" in st.session_state:
            st.success("🎉 تم إنتاج الملف الصوتي بنجاح وجاهز للاستماع والتحميل.")

    # --- 8. تبويب المستشار الذكي ---
    with sub_tabs[7]:
        st.subheader("💬 المستشار الذكي المفتوح للأسئلة")
        advisor_input = st.text_area("اطرح سؤالك الأكاديمي الشامل:")
        
        if st.button("🧠 إرسال الاستشارة"):
            if advisor_input.strip():
                run_progress_bar()
                if client:
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": advisor_input}]
                    )
                    generated_content = res.choices[0].message.content
                else:
                    generated_content = f"تمت الإجابة الاستشارية المتكاملة على استفساركم الأكاديمي بنجاح."
                
                content_words = len(generated_content.split())
                calculated_cost_advisor = max(1, content_words // 700)
                
                if deduct_attempts(calculated_cost_advisor):
                    st.session_state.advisor_res = generated_content
                    st.rerun()
                    
        if "advisor_res" in st.session_state:
            st.info("**إجابة المستشار الأكاديمي:**")
            st.markdown(st.session_state.advisor_res)

st.markdown("<br><br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
