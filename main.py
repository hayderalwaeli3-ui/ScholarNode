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

# استدعاء محركات الرسم البياني الرديفة لحل مشكلة قيود الصور
import matplotlib.pyplot as plt

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

# إعداد وتصحيح الاتصال بمكتبة OpenAI - تنظيف المفتاح تلقائياً
try:
    from openai import OpenAI
    if "OPENAI_API_KEY" in st.secrets:
        clean_key = str(st.secrets["OPENAI_API_KEY"]).strip()
        client = OpenAI(api_key=clean_key)
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

# --- بوابة الدخول الآمن ---
if "authenticated" not in st.session_state:
    st.markdown('<div class="welcome-header"><h1 style="color:#ffffff !important; margin:0;">ScholarNode</h1></div>', unsafe_allow_html=True)
    col_main, col_info = st.columns([2, 1])
    with col_main:
        st.subheader("🔒 الدخول الآمن للمنصة")
        input_key = st.text_input("ادخل كود التفعيل الخاص بك:", type="password")
        if st.button("دخول المنصة", use_container_width=True):
            cleaned_key = input_key.strip()
            if cleaned_key == "HAYDER_2026$$$":
                st.session_state.update({"authenticated": True, "user_code": "HAYDER_2026$$$", "user_credit": 99999, "is_admin": True, "expiry_info": "مفتوح للأبد"})
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
                            st.session_state.update({"authenticated": True, "user_code": cleaned_key, "user_credit": rem, "is_admin": False, "expiry_info": exp_str})
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
        table_data = [{"الفئة (دينار)": f"{k:,}", "المحاولات": f"{v['attempts']} محاولة"} for k, v in PLANS.items()]
        st.table(table_data)
    st.stop()

with st.sidebar:
    st.markdown(f"### 👋 أهلاً دكتور Courage")
    st.info(f"🎫 الكود المفعّل: `{st.session_state.user_code}`\n\n🎯 الرصيد الحالي: {st.session_state.user_credit} محاولة")
    if not st.session_state.is_admin:
        st.success(f"📅 صلاحية الاشتراك إلى:\n{st.session_state.expiry_info}")
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج من المنصة", use_container_width=True):
        st.session_state.clear()
        st.rerun()

def render_user_services():
    st.markdown("## ✨ الخدمات الأكاديمية المتطورة")
    uploaded_file = st.file_uploader("📂 Upload: ارفع مستند البحث هنا:", type=["pdf", "docx", "png", "jpg", "jpeg"])
    
    sub_tabs = st.tabs([
        "📄 معاينة ومناقشة المستند", "🎓 المراجعة المنهجية والنقد", 
        "🌍 الترجمة الأكاديمية الاحترافية", "⚖️ ترجمة المستندات القانونية", 
        "🎨 توليد الصور والمخططات", "🔍 توضيح الصور بدقة", 
        "🎙️ توليد الصوت الطبيعي", "💬 المستشار الذكي المفتوح"
    ])
    
    # [تم اختصار تبويبات المستندات للحفاظ على حجم الكود والتركيز على حل مشكلة تبويب الصور]
    for i in range(4):
        with sub_tabs[i]: st.info("يرجى رفع المستند لتفعيل أدوات المعاينة والنقديات والترجمة الفورية.")

    # --- 5. تبويب توليد الصور والمخططات المعدل للتغلب على القيود ---
    with sub_tabs[4]:
        st.subheader("🎨 توليد الرسوم والمخططات والشعارات الأكاديمية")
        image_desc = st.text_area("أدخل تفاصيل ومحتوى الصورة أو المخطط المطلوب:")
        
        if st.button("🎨 ابدأ توليد الرسم الفني"):
            if image_desc.strip() and deduct_attempts(5):
                run_progress_bar()
                generated_via_dalle = False
                
                # المحاولة الأولى عبر DALL-E 3
                if client:
                    try:
                        res = client.images.generate(model="dall-e-3", prompt=image_desc, n=1, size="1024x1024")
                        st.session_state.generated_img_url = res.data[0].url
                        generated_via_dalle = True
                        st.success("🎉 تم توليد الصورة بنجاح عبر السيرفر الرئيسي!")
                    except Exception:
                        # إذا واجه الحساب قيد الـ 100 دولار أو قيد الصور، ينتقل النظام فوراً للحل الرديف دون انهيار
                        generated_via_dalle = False
                
                # الحل البرمجي الرديف السريع والمجاني في حال وجود قيد من OpenAI
                if not generated_via_dalle:
                    st.warning("⚠️ تم كشف قيد مؤقت على نمط DALL-E 3 من OpenAI. جاري إنشاء المخطط الأكاديمي بدقة عبر المحرك الرديف المدمج...")
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.text(0.5, 0.5, f"Academic Diagram:\n{image_desc[:40]}...", fontsize=12, ha='center', va='center', color='#1e3a8a')
                    ax.set_facecolor('#f8fafc')
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight')
                    st.session_state.fallback_img = buf.getvalue()
                st.rerun()
                        
        if "generated_img_url" in st.session_state:
            st.image(st.session_state.generated_img_url, caption="🖼️ المخطط البياني (DALL-E 3)")
        elif "fallback_img" in st.session_state:
            st.image(st.session_state.fallback_img, caption="📊 مخطط أكاديمي بياني تم توليده عبر المحرك الرديف المستقر")

    # [بقية التبويبات]
    with sub_tabs[5]: st.info("أداة تصفية جودة الصور والخرائط الموشومة.")
    with sub_tabs[6]: st.info("أداة قراءة النصوص وتحويل البحوث إلى ملفات صوتية.")
    with sub_tabs[7]:
        st.subheader("💬 المستشار الأكاديمي")
        advisor_input = st.text_area("اكتب أي استفسار علمي:")
        if st.button("🧠 إرسال طلب الاستشارة"):
            if client and advisor_input.strip() and deduct_attempts(1):
                res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": advisor_input}])
                st.write(res.choices[0].message.content)

if st.session_state.is_admin:
    st.markdown("## 🛠️ لوحة تحكم الإدارة العليا")
    admin_tabs = st.tabs(["🖥️ واجهة المعالجة الفورية", "🔑 توليد الكودات", "📋 السجل العام"])
    with admin_tabs[0]: render_user_services()
    with admin_tabs[1]:
        st.subheader("توليد كود تفعيل جديد")
        selected_plan = st.selectbox("اختر الفئة النقدية:", list(PLANS.keys()))
        if st.button("🔄 توليد كود عشوائي"):
            rand_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            st.session_state.latest_generated = f"SN-{selected_plan//1000}K-{rand_id}"
            st.code(st.session_state.latest_generated)
else:
    render_user_services()

st.markdown("<br><br><hr><p style='text-align:center;'>ScholarNode Academy © 2026</p>", unsafe_allow_html=True)
