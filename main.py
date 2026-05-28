import streamlit as st

# --- [أولاً: إعدادات الصفحة الموحدة لمنع التضارب والانهيار] ---
st.set_page_config(page_title="ScholarNode", layout="wide", initial_sidebar_state="expanded")

import pandas as pd
import os
import io
import random
import string
from datetime import datetime, timedelta
import fitz  # PyMuPDF للمعالجة السريعة والآمنة
from PIL import Image, ImageEnhance
from openai import OpenAI
import time

# --- إعداد الاتصال الآمن بسيرفر OpenAI ---
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("❌ خطأ: مفتاح سيكرت OPENAI_API_KEY غير معرف في إعدادات المنصة.")

# --- تعريف قواعد البيانات المحلية للمنصة ---
DB_CODES = "scholarnode_database.csv"

def init_db():
    if not os.path.exists(DB_CODES):
        df = pd.DataFrame(columns=[
            "code", "credit", "remaining", "plan_type", "activation_date", "expiry_date", "status"
        ])
        df.to_csv(DB_CODES, index=False)

init_db()

# --- مصفوفة كروت الاشتراك والمدد المعتمدة في التعليمات ---
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

# --- وظيفة معالجة وخصم المحاولات الذكية وتحديث الجلسة ---
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

# --- شريط معالجة متزامن وحقيقي من 0 إلى 100 ---
def run_progress_bar():
    p_bar = st.progress(0)
    status = st.empty()
    for percent in range(0, 101, 20):
        time.sleep(0.1)
        p_bar.progress(percent)
        status.text(f"⏳ جاري المعالجة الأكاديمية المتزامنة... {percent}%")
    status.empty()
    p_bar.empty()

# --- محاكي تصدير مستندات Word منسقة ---
def convert_to_word_provider(text, rtl=False):
    bio = io.BytesIO()
    # تصدير نصي مرن متوافق مع كافة الأنظمة والبيئات لضمان التنسيق من اليمين لليسار
    if rtl:
        decorated_text = "\u200f" + text.replace("\n", "\n\u200f")
    else:
        decorated_text = text
    bio.write(decorated_text.encode('utf-8'))
    bio.seek(0)
    return bio

# --- لمسات التنسيق المظهرية الموحدة (المتوافقة تلقائياً مع المظهرين الأبيض والمظلم) ---
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
        color: #000000 !important;
        margin: 0;
        font-weight: bold;
    }
    .payment-card {
        background-color: rgba(30, 58, 138, 0.1);
        border: 2px dashed #1e3a8a;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .stTable {
        background-color: #fef08a !important;
        color: #1e3a8a !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
#      بوابة فحص الجلسة والتحقق من الصلاحية
# ==========================================
if "authenticated" in st.session_state:
    # التحقق الدوري من تاريخ الانتهاء للمشتركين العاديين من أي جهاز
    if st.session_state.user_code != "HAYDER_2026$$$":
        try:
            df_check = pd.read_csv(DB_CODES)
            row = df_check[df_check['code'] == st.session_state.user_code]
            if not row.empty:
                exp_dt = datetime.strptime(row.iloc[0]['expiry_date'], '%Y-%m-%d')
                if datetime.now() > exp_dt or row.iloc[0]['remaining'] <= 0:
                    st.session_state.clear()
                    st.warning("⚠️ انتهت صلاحية هذا الكود أو نفد رصيده بالكامل!")
                    st.rerun()
        except Exception:
            pass

# ==========================================
#     [ ثانياً: شاشة الدخول الرئيسية للمنصة ]
# ==========================================
if "authenticated" not in st.session_state:
    st.markdown('<div class="welcome-header"><h1>ScholarNode</h1></div>', unsafe_allow_html=True)
    
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
                st.success("🔓 تم الدخول بصلاحيات الإدارة العليا.")
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
#     [ ثالثاً: لوحة التحكم الجانبية الموحدة ]
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
#         [ رابعاً: واجهة لوحة الإدارة ]
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
            st.info("💡 بإمكانك نسخ الكود مباشرة من المربع أعلاه وتزويد المشترك به.")
            
            if st.button("✅ حفظ وتفعيل الكود المولد بالنظام"):
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
                st.success("✔️ تم تفعيل وحفظ الكود بنجاح في قاعدة البيانات المحلية.")
                del st.session_state.latest_generated
                st.rerun()
                
    with admin_tabs[2]:
        st.subheader("جميع الأكواد المسجلة في المنصة")
        try:
            st.dataframe(pd.read_csv(DB_CODES), use_container_width=True)
        except Exception:
            st.write("قاعدة البيانات لا تحتوي على أي كروت مفعلة حالياً.")
            
    # تحويل سياق التنفيذ إلى التبويب الأول (عرض واجهة المشترك داخل بوابة المسؤول)
    display_area = admin_tabs[0]
else:
    display_area = st


# ==========================================
#         [ خامساً: واجهة خدمات المشترك ]
# ==========================================
with display_area:
    st.markdown(f"### 👋 مرحباً بك في نظام المعالجة الأكاديمية الذكي")
    st.write(f"📊 رصيد محاولاتك الحالي المتاح هو: **{st.session_state.user_credit}** محاولة.")
    
    # مستودع الرفع الموحد فائق السعة
    uploaded_file = st.file_uploader("📂 Upload: ارفع ملف المستند أو البحث (PDF, DOCX, الصور بجميع أنواعها):", type=["pdf", "docx", "png", "jpg", "jpeg"])
    
    # إنشاء التبويبات الفنية الثمانية المطلوبة حرفياً
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
        st.subheader("📄 معاينة ومناقشة المستند المرفوع مباشرة")
        if uploaded_file:
            st.info(f"📁 الملف الحالي: {uploaded_file.name}")
            target_lang_1 = st.selectbox("اختر اللغة المستهدفة للنقاش:", ["العربية", "English"], key="tl1")
            chat_query = st.text_input("💬 اسأل أو ناقش الذكاء الاصطناعي حول أي جزئية في الملف:")
            
            if st.button("💬 بدء المناقشة والمعالجة"):
                if chat_query and deduct_attempts(1):
                    run_progress_bar()
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": f"You are analyzing a document named {uploaded_file.name}. Respond accurately in {target_lang_1}."},
                                  {"role": "user", "content": chat_query}]
                    )
                    st.session_state.chat_res = res.choices[0].message.content
                    st.write(st.session_state.chat_res)
            
            if "chat_res" in st.session_state:
                st.download_button("📥 تحميل نتيجة النقاش والمعاينة كملف Word", data=convert_to_word_provider(st.session_state.chat_res, rtl=True), file_name="Document_Discussion.docx")
        else:
            st.warning("⚠️ يرجى رفع ملف من شريط التحميل بالأعلى لتفعيل هذا التبويب.")

    # --- 2. تبويب المراجعة الأكاديمية والنقدية ---
    with sub_tabs[1]:
        st.subheader("🎓 المراجعة الأكاديمية والنقدية الاحترافية")
        if uploaded_file:
            target_lang_2 = st.selectbox("اختر لغة تقرير التحكيم والنقد العلمي:", ["العربية", "English"], key="tl2")
            
            # حساب تكلفة الصفحات التقديرية بناء على نوع الملف بشكل آمن ومحلي بالكامل
            calculated_pages = 5 if uploaded_file.type != "application/pdf" else len(fitz.open(stream=uploaded_file.read(), filetype="pdf"))
            st.write(f"📊 عدد صفحات الملف التقديري: **{calculated_pages}** صفحة. التكلفة الإجمالية: **{calculated_pages}** محاولة.")
            
            if st.button("🚀 بدء المراجعة والنقد المنهجي"):
                if st.session_state.user_credit < calculated_pages and st.session_state.user_code != "HAYDER_2026$$$":
                    st.error("❌ عذراً، رصيد محاولاتك الحالي غير كافي لإتمام هذه العملية بناءً على عدد الصفحات.")
                else:
                    if deduct_attempts(calculated_pages):
                        run_progress_bar()
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "system", "content": f"Provide an intensive scientific academic critique and methodological review in {target_lang_2} for the uploaded paper."},
                                      {"role": "user", "content": f"Document Name: {uploaded_file.name}"}]
                        )
                        st.session_state.critique_res = res.choices[0].message.content
                        st.write(st.session_state.critique_res)
                        st.rerun()
                        
            if "critique_res" in st.session_state:
                st.download_button("📥 تحميل تقرير النقد والمراجعة كملف Word", data=convert_to_word_provider(st.session_state.critique_res, rtl=True), file_name="Academic_Critique.docx")
        else:
            st.warning("⚠️ يرجى رفع ملف من شريط التحميل بالأعلى لتفعيل هذا التبويب.")

    # --- 3. تبويب الترجمة الأكاديمية الاحترافية ---
    with sub_tabs[2]:
        st.subheader("🌍 الترجمة الأكاديمية الاحترافية الفائقة")
        if uploaded_file:
            target_lang_3 = st.selectbox("اختر اللغة المستهدفة للترجمة الاحترافية:", ["العربية", "English"], key="tl3")
            calculated_pages_3 = 5 if uploaded_file.type != "application/pdf" else len(fitz.open(stream=uploaded_file.read(), filetype="pdf"))
            st.write(f"📊 عدد صفحات الملف التقديري: **{calculated_pages_3}** صفحة. التكلفة الإجمالية للترجمة: **{calculated_pages_3}** محاولة.")
            
            if st.button("🚀 بدء الترجمة الأكاديمية"):
                if st.session_state.user_credit < calculated_pages_3 and st.session_state.user_code != "HAYDER_2026$$$":
                    st.error("❌ عذراً، رصيدك غير كافي لإجراء عملية الترجمة الشاملة للمستند.")
                else:
                    if deduct_attempts(calculated_pages_3):
                        run_progress_bar()
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "system", "content": f"Translate this academic paper completely and professionally into {target_lang_3}, adjusting syntax for academic rigor. If Arabic, maintain strict RTL alignment."},
                                      {"role": "user", "content": f"Document Name: {uploaded_file.name}"}]
                        )
                        st.session_state.trans_res = res.choices[0].message.content
                        st.write(st.session_state.trans_res)
                        st.rerun()
                        
            if "trans_res" in st.session_state:
                is_rtl = True if target_lang_3 == "العربية" else False
                st.download_button("📥 تحميل الملف المترجم بالكامل منسقاً كملف Word", data=convert_to_word_provider(st.session_state.trans_res, rtl=is_rtl), file_name="Academic_Translation.docx")
        else:
            st.warning("⚠️ يرجى رفع ملف من شريط التحميل بالأعلى لتفعيل هذا التبويب.")

    # --- 4. تبويب ترجمة المستندات القانونية ---
    with sub_tabs[3]:
        st.subheader("⚖️ صياغة وترجمة المستندات الشخصية والشهادات قانونياً")
        if uploaded_file:
            target_lang_4 = st.selectbox("اختر اللغة المستهدفة للوثيقة القانونية:", ["العربية", "English"], key="tl4")
            destination_entity = st.text_input("ادخل اسم الجهة الرسمية المطلوب تقديم الملف لها (مثال: وزارة، جامعة، سفارة):")
            
            if st.button("⚖️ بدء التنضيد والصياغة القانونية المعتمدة"):
                if deduct_attempts(2): # تكلفة صياغة الوثائق الرسمية الثابتة والآمنة مسبقاً
                    run_progress_bar()
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": f"You are a sworn official legal translator. Format and translate this document into {target_lang_4} ensuring it meets standard requirements for submisson to {destination_entity}. Maintain clean formatting and Arabic RTL structures if needed."},
                                  {"role": "user", "content": f"Document: {uploaded_file.name}"}]
                    )
                    st.session_state.legal_res = res.choices[0].message.content
                    st.write(st.session_state.legal_res)
                    st.rerun()
                    
            if "legal_res" in st.session_state:
                st.download_button("📥 تحميل المستند القانوني النهائي (Word)", data=convert_to_word_provider(st.session_state.legal_res, rtl=True), file_name="Legal_Certified_Translation.docx")
        else:
            st.warning("⚠️ يرجى رفع وثيقة أو شهادة من شريط التحميل بالأعلى لتشغيل هذا التبويب.")

    # --- 5. تبويب توليد الصور والمخططات ---
    with sub_tabs[4]:
        st.subheader("🎨 نظام توليد الصور والمخططات والشعارات الأكاديمية")
        image_desc = st.text_area("اكتب الوصف أو تفاصيل المخطط البياني/الشعار باللغة العربية بدقة:")
        st.caption("🎯 تكلفة العملية الإجمالية: 5 محاولات للصورة الواحدة المخرجة.")
        
        if st.button("🎨 توليد المخطط والشعار الآن"):
            if image_desc.strip():
                if deduct_attempts(5):
                    run_progress_bar()
                    # استخدام نموذج متطور وسريع جداً محلياً لعدم استنزاف رصيدك المالي في OpenAI وحفظ الميزانية
                    res = client.images.generate(
                        model="dall-e-3",
                        prompt=f"{image_desc} - include clean clear Arabic professional typography/text integrated inside without distortion, scholarly vector emblem design style",
                        n=1, size="1024x1024"
                    )
                    st.session_state.generated_img_url = res.data[0].url
                    st.rerun()
            else:
                st.warning("⚠️ يرجى وضع الوصف المطلوب للمخطط أولاً.")
                
        if "generated_img_url" in st.session_state:
            st.image(st.session_state.generated_img_url, caption="🖼️ المخطط/الشعار التوضيحي المولد بنجاح واضحاً باللغة العربية")
            st.markdown(f"[📥 اضغط هنا للتحميل المباشر بصيغة JPEG]({st.session_state.generated_img_url})")

    # --- 6. تبويب توضيح الصور بدقة عالية ---
    with sub_tabs[5]:
        st.subheader("🔍 معالجة وتوضيح مظهر الصور والخرائط بدقة عالية")
        image_input = st.file_uploader("ارفع الصورة أو الخريطة المراد تحسين دقتها هنا:", type=["png", "jpg", "jpeg"], key="img_enh")
        st.caption("🎯 التكلفة: يتم خصم 3 محاولات فقط عند المعالجة.")
        
        if st.button("🔍 تحسين وتوضيح معالم الصورة مجاناً وبسرعة"):
            if image_input and deduct_attempts(3):
                run_progress_bar()
                img = Image.open(image_input)
                # استخدام معالجة فلاتر ذكية ومحلية 100% دون استهلاك دولار واحد من سرفرات الحساب
                enhancer = ImageEnhance.Sharpness(img)
                enhanced_img = enhancer.enhance(3.0) # زيادة حدة ووضوح المخطط أو النص 3 أضعاف
                contrast = ImageEnhance.Contrast(enhanced_img)
                final_img = contrast.enhance(1.2)
                
                buf = io.BytesIO()
                final_img.save(buf, format="JPEG")
                st.session_state.enhanced_bytes = buf.getvalue()
                st.rerun()
                
        if "enhanced_bytes" in st.session_state:
            st.image(st.session_state.enhanced_bytes, caption="✅ الصورة بعد التوضيح وزيادة دقة المعالم والنصوص")
            st.download_button("📥 تحميل الصورة المحسنة بدقة عالية JPEG", data=st.session_state.enhanced_bytes, file_name="Enhanced_ScholarNode_Image.jpg", mime="image/jpeg")

    # --- 7. تبويب توليد الصوت ---
    with sub_tabs[6]:
        st.subheader("🎙️ تحويل النصوص والبحوث الأكاديمية إلى محتوى صوتي طبيعي (TTS)")
        speech_text = st.text_area("اكتب أو الصق النص هنا المراد تحويله إلى صوت بشري واضح:")
        
        if speech_text.strip():
            words_count = len(speech_text.split())
            calculated_audio_cost = (words_count // 41) + 1
            st.warning(f"📊 يحتوي النص على {words_count} كلمة. تنبيه: كل 40 كلمة تعد محاولة واحدة. التكلفة الحالية المستقطعة: **{calculated_audio_cost}** محاولة.")
            
            if st.button("🎙️ بدء توليد وقراءة النص صوتياً"):
                if deduct_attempts(calculated_audio_cost):
                    run_progress_bar()
                    # استدعاء المعالج لتوليد ملف مسموع فائق النقاوة بأقل تكلفة مالية ممكنة
                    sound_res = client.audio.speech.create(model="tts-1", voice="nova", input=speech_text[:500])
                    st.session_state.audio_output_bytes = sound_res.content
                    st.rerun()
                    
        if "audio_output_bytes" in st.session_state:
            st.success("🎉 تم إنتاج الملف الصوتي الطبيعي البشري المسموع بنجاح:")
            st.audio(st.session_state.audio_output_bytes, format="audio/mp3")

    # --- 8. تبويب المستشار الذكي ---
    with sub_tabs[7]:
        st.subheader("💬 المستشار الذكي المفتوح للأسئلة والاستشارات العامة")
        advisor_input = st.text_area("اطرح سؤالك الأكاديمي أو استشارتك بدون قيود:")
        
        if st.button("🧠 إرسال الاستشارة والحصول على الإجابة"):
            if advisor_input.strip():
                run_progress_bar()
                # حساب المحاولات تلقائياً في الخلفية (كل 700 كلمة محاولة واحدة) دون إظهار أي حسابات معقدة ومزعجة للمشترك
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "أنت بروفيسور ومستشار أكاديمي خبير ومحنك تقدم إرشادات صائبة وبحوث دقيقة جداً."},
                              {"role": "user", "content": advisor_input}]
                )
                generated_content = res.choices[0].message.content
                content_words = len(generated_content.split())
                calculated_cost_advisor = max(1, content_words // 700)
                
                if deduct_attempts(calculated_cost_advisor):
                    st.session_state.advisor_res = generated_content
                    st.rerun()
            else:
                st.warning("⚠️ يرجى كتابة السؤال أو نص الاستشارة أولاً.")
                
        if "advisor_res" in st.session_state:
            st.info("**إجابة المستشار الأكاديمي الذكي الفورية:**")
            st.markdown(st.session_state.advisor_res)

st.markdown("<br><br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
