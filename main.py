python
import streamlit as st
import pandas as pd
import uuid
import os
import random
import string
from datetime import datetime
from docx import Document
import io

# --- الإعدادات العامة للواجهة ---
st.set_page_config(page_title="ScholarNode Academy", layout="wide")

# تصميم CSS باللون الأزرق الملكي والذهبي
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stApp { color: #1a2a6c; }
    .sidebar .sidebar-content { background-image: linear-gradient(#1a2a6c, #b21f1f); color: white; }
    .stButton>button { 
        background-color: #1a2a6c; color: #d4af37; 
        border: 2px solid #d4af37; border-radius: 10px;
        font-weight: bold; width: 100%;
    }
    .stButton>button:hover { background-color: #d4af37; color: #1a2a6c; }
    .price-card {
        padding: 20px; border-radius: 15px; border: 2px solid #d4af37;
        text-align: center; margin: 10px; background-color: white;
    }
    .footer { text-align: center; color: #777; padding: 20px; }
    h1, h2, h3 { color: #1a2a6c !important; }
    </style>
    """, unsafe_allow_html=True)

# --- إدارة قواعد البيانات (CSV) ---
DB_MAIN = "scholar_main_db.csv"  # للأكواد
DB_DEVICES = "device_tracking.csv"  # لتتبع الأجهزة

def init_db():
    if not os.path.exists(DB_MAIN):
        pd.DataFrame(columns=["code", "attempts", "status", "created_at"]).to_csv(DB_MAIN, index=False)
    if not os.path.exists(DB_DEVICES):
        pd.DataFrame(columns=["device_id", "remaining_attempts", "is_premium"]).to_csv(DB_DEVICES, index=False)

init_db()

# --- وظائف النظام ---
def get_device_id():
    if 'device_id' not in st.session_state:
        # محاكاة معرف جهاز (في التطبيقات الواقعية يمكن استخدام cookies لتتبع أدق)
        st.session_state.device_id = str(uuid.uuid4())[:8]
    return st.session_state.device_id

def check_or_register_device(device_id):
    df = pd.read_csv(DB_DEVICES)
    if device_id not in df['device_id'].values:
        new_device = pd.DataFrame([{
            "device_id": device_id,
            "remaining_attempts": 2, # محاولتين مجانيتين
            "is_premium": False
        }])
        df = pd.concat([df, new_device], ignore_index=True)
        df.to_csv(DB_DEVICES, index=False)
    return df[df['device_id'] == device_id].iloc[0]

def deduct_attempts(device_id, amount):
    df = pd.read_csv(DB_DEVICES)
    if device_id in df['device_id'].values:
        idx = df[df['device_id'] == device_id].index[0]
        if df.at[idx, 'remaining_attempts'] >= amount:
            df.at[idx, 'remaining_attempts'] -= amount
            df.to_csv(DB_DEVICES, index=False)
            return True
    return False

def add_attempts_by_code(device_id, code):
    df_codes = pd.read_csv(DB_MAIN)
    df_devices = pd.read_csv(DB_DEVICES)
    
    if code in df_codes['code'].values and df_codes.loc[df_codes['code'] == code, 'status'].values[0] == 'unused':
        attempts_to_add = df_codes.loc[df_codes['code'] == code, 'attempts'].values[0]
        
        # تحديث الجهاز
        idx = df_devices[df_devices['device_id'] == device_id].index[0]
        df_devices.at[idx, 'remaining_attempts'] += attempts_to_add
        df_devices.at[idx, 'is_premium'] = True
        
        # حرق الكود
        c_idx = df_codes[df_codes['code'] == code].index[0]
        df_codes.at[c_idx, 'status'] = 'used'
        
        df_devices.to_csv(DB_DEVICES, index=False)
        df_codes.to_csv(DB_MAIN, index=False)
        return True, attempts_to_add
    return False, 0

# --- واجهة المستخدم ---
st.title("🎓 ScholarNode Academy")
st.subheader("المنصة الأكاديمية الذكية للأبحاث والترجمة")

dev_id = get_device_id()
device_info = check_or_register_device(dev_id)
remaining = device_info['remaining_attempts']

# شريط جانبي للمعلومات
with st.sidebar:
    st.header("👤 حسابي")
    st.info(f"ID: {dev_id}")
    st.metric("المحاولات المتبقية", f"{remaining} محاولة")
    
    st.divider()
    st.header("💳 تفعيل الكود")
    input_code = st.text_input("أدخل كود الاشتراك هنا")
    if st.button("تفعيل الآن"):
        success, added = add_attempts_by_code(dev_id, input_code)
        if success:
            st.success(f"تمت إضافة {added} محاولة بنجاح!")
            st.rerun()
        else:
            st.error("الكود غير صحيح أو مستخدم مسبقاً")

    st.divider()
    st.markdown("### 📞 للدفع والاستفسار")
    st.write("ماستر كارد الرافدين")
    st.warning("الاسم: [اسمك هنا]\nرقم الهاتف: [رقمك هنا]")

# --- الأقسام الرئيسية ---
if remaining <= 0:
    st.error("⚠️ ليس لديك محاولات كافية. يرجى الاشتراك لتكملة استخدام الخدمة.")
    
    # جدول الأسعار
    st.subheader("📊 باقات الاشتراك المتاحة")
    cols = st.columns(3)
    prices = [
        ("10,000 د.ع", "10 محاولات"), ("20,000 د.ع", "25 محاولة"), ("30,000 د.ع", "40 محاولة"),
        ("40,000 د.ع", "60 محاولة"), ("50,000 د.ع", "80 محاولة"), ("100,000 د.ع", "200 محاولة")
    ]
    for i, (p, a) in enumerate(prices):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="price-card">
                <h3 style="color:#1a2a6c">{p}</h3>
                <p style="font-size:1.2em; color:red;"><b>{a}</b></p>
            </div>
            """, unsafe_allow_html=True)
else:
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat (الدردشة)", "🌍 Translation (الترجمة)", "🔍 Review (المراجعة)", "📄 Preview (المعاينة)"])

    with tab1:
        st.write("اسأل الذكاء الاصطناعي عن أي شيء يخص بحثك.")
        user_msg = st.text_input("اكتب سؤالك هنا...")
        if st.button("إرسال"):
            if deduct_attempts(dev_id, 1):
                st.write("🤖 رد الـ AI: هذه ميزة تجريبية، جاري معالجة طلبك...")
                st.rerun()

    with tab2:
        st.write("ترجمة ملفات Word ترجمة أكاديمية.")
        uploaded_file = st.file_uploader("اختر ملف Word للترجمة", type=["docx"])
        if uploaded_file and st.button("بدء الترجمة"):
            doc = Document(uploaded_file)
            pages = len(doc.paragraphs) // 10 + 1 # حساب تقريبي للصفحات
            if deduct_attempts(dev_id, pages):
                st.success(f"تم خصم {pages} محاولات (حسب حجم الملف). جاري الترجمة...")
                st.rerun()
            else:
                st.error("رصيدك لا يكفي لترجمة هذا الملف.")

    with tab3:
        st.write("مراجعة علمية وتدقيق لغوي.")
        rev_file = st.file_uploader("اختر ملف Word للمراجعة", type=["docx"], key="rev")
        if rev_file and st.button("بدء المراجعة"):
            doc = Document(rev_file)
            pages = len(doc.paragraphs) // 10 + 1
            if deduct_attempts(dev_id, pages):
                st.success(f"جاري مراجعة {pages} صفحات...")
                st.rerun()
            else:
                st.error("رصيدك لا يكفي.")

    with tab4:
        st.write("معاينة سريعة للمصادر والمراجع.")
        if st.button("معاينة المصادر المقترحة"):
            if deduct_attempts(dev_id, 1):
                st.info("جاري استخراج المصادر...")
                st.rerun()

# --- لوحة التحكم (Admin Panel) ---
st.divider()
expander = st.expander("🛠️ لوحة التحكم (للمسؤول فقط)")
with expander:
    admin_pw = st.text_input("كلمة مرور المسؤول", type="password")
    if admin_pw == "HAYDER_2026":
        st.success("تم الدخول بصلاحيات المسؤول")
        col1, col2 = st.columns(2)
        with col1:
            amount_to_gen = st.selectbox("عدد المحاولات للكود", [10, 20, 30, 40, 50, 100])
            if st.button("توليد كود جديد"):
                new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                df_codes = pd.read_csv(DB_MAIN)
                new_entry = pd.DataFrame([{"code": new_code, "attempts": amount_to_gen, "status": "unused", "created_at": datetime.now()}])
                df_codes = pd.concat([df_codes, new_entry], ignore_index=True)
                df_codes.to_csv(DB_MAIN, index=False)
                st.code(new_code, language="")
                st.write(f"أعطِ هذا الكود للعميل (يعطي {amount_to_gen} محاولة)")
        
        with col2:
            st.write("سجل الأكواد:")
            st.dataframe(pd.read_csv(DB_MAIN).tail(5))
    elif admin_pw != "":
        st.error("كلمة المرور خاطئة")

st.markdown('<div class="footer">جميع الحقوق محفوظة لـ ScholarNode Academy © 2024</div>', unsafe_allow_html=True)
