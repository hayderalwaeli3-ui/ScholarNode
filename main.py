import streamlit as st
import pandas as pd
import os
import io
import time
import threading  # المكتبة المسؤولة عن منع تداخل طلبات المشتركين

# --- 1. إعدادات المنصة الرئيسية ---
st.set_page_config(page_title="منصة سكالر نود", layout="wide")

import google.generativeai as genai

# إنشاء "قفل الأمان" لمنع حدوث التضارب عند تحديث الرصيد
قفل_الملف = threading.Lock()

# تهيئة الاتصال بمحرك جوجل جيميناي
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    محرك_الذكاء = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("خطأ: مفتاح التشغيل غير موجود في الإعدادات السرية.")
    st.stop()

مسار_قاعدة_البيانات = "scholarnode_secured_db.csv"

# --- 2. دالة الخصم الآمنة (تمنع التضارب وتتحقق من الرصيد أولاً) ---
def خصم_الرصيد_بأمان(الكمية_المطلوبة):
    # كود الإدارة العليا (صاحب المنصة) مستثنى من الخصم
    if st.session_state.get('user_code') == "HAYDER_2026$$$":
        return True
        
    # هنا يبدأ مفعول "القفل"؛ ممنوع دخول أي مستخدم آخر لهذا الجزء حتى تنتهي المعالجة الحالية
    with قفل_الملف:
        try:
            بيانات = pd.read_csv(مسار_قاعدة_البيانات)
            كود_المشترك = st.session_state.user_code
            
            if كود_المشترك in بيانات['code'].values:
                الموقع = بيانات.index[بيانات['code'] == كود_المشترك][0]
                الرصيد_الحالي = بيانات.at[الموقع, 'remaining']
                
                # فحص هل الرصيد يكفي للعملية؟
                if الرصيد_الحالي >= الكمية_المطلوبة:
                    الرصيد_الجديد = int(الرصيد_الحالي - الكمية_المطلوبة)
                    بيانات.at[الموقع, 'remaining'] = الرصيد_الجديد
                    بيانات.to_csv(مسار_قاعدة_البيانات, index=False)
                    # تحديث الرصيد في واجهة المشترك فوراً
                    st.session_state.user_credit = الرصيد_الجديد
                    return True  # تم الخصم بنجاح
            return False  # الرصيد لا يكفي
        except Exception:
            return False

# --- 3. تصميم الواجهة الأكاديمية (أزرق وأصفر) ---
st.markdown("""
    <style>
    .ترويسة_المنصة {
        background-color: #0056b3;
        border: 4px solid #FFD700;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: black;
        font-weight: bold;
        font-size: 30px;
    }
    .تذييل_الصفحة {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        font-weight: bold;
        padding: 8px;
        background: white;
        border-top: 2px solid #0056b3;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. نظام تسجيل الدخول ---
if 'check_in' not in st.session_state:
    st.session_state.check_in = False

if not st.session_state.check_in:
    st.markdown('<div class="ترويسة_المنصة">ScholarNode المنصة الأكاديمية</div>', unsafe_allow_html=True)
    ع1, ع2 = st.columns([2, 1])
    
    with ع1:
        st.subheader("🔐 تسجيل الدخول الآمن")
        كود_الدخول = st.text_input("أدخل كود تفعيل الكرت الخاص بك", type="password")
        if st.button("دخول المنصة"):
            with قفل_الملف:
                جدول_البيانات = pd.read_csv(مسار_قاعدة_البيانات)
            if كود_الدخول == "HAYDER_2026$$$" or كود_الدخول in جدول_البيانات['code'].values:
                st.session_state.check_in = True
                st.session_state.user_code = كود_الدخول
                if كود_الدخول == "HAYDER_2026$$$":
                    st.session_state.user_credit = "مفتوح"
                else:
                    st.session_state.user_credit = جدول_البيانات[جدول_البيانات['code']==كود_الدخول]['remaining'].values[0]
                st.rerun()
            else:
                st.error("عذراً، الكود غير صحيح")
    with ع2:
        st.info("💳 الحساب المعتمد: HAYDER Z. JASIM | 07879974395")

# --- 5. واجهة المنصة بعد تفعيل الدخول ---
else:
    st.markdown(f'<div style="background:#e3f2fd; padding:10px; border-radius:10px; text-align:right;"><b>مرحباً بك.. رصيدك الحالي: {st.session_state.user_credit} محاولة</b></div>', unsafe_allow_html=True)
    
    ملف_الباحث = st.file_uploader("ارفع المستند الخاص بك هنا", type=['pdf', 'docx', 'png', 'jpg'])
    
    التبويبات = st.tabs(["🔍 معاينة ومناقشة", "🎓 مراجعة نقدية", "🌍 ترجمة أكاديمية", "⚖️ ترجمة قانونية", "🖼️ توليد صور", "✨ توضيح دقة", "🎙️ توليد صوت", "👨‍🏫 المستشار"])

    def شريط_المعالجة():
        مؤشر = st.progress(0)
        for م في range(101):
            time.sleep(0.01)
            مؤشر.progress(م)

    # --- تبويب الترجمة الأكاديمية (تطبيق شرط الخصم قبل الاستدعاء) ---
    with التبويبات[2]:
        st.header("🌍 الترجمة الأكاديمية الاحترافية")
        if st.button("بدء عملية الترجمة"):
            if ملف_الباحث:
                # الشرط الصارم: الخصم المالي أولاً
                if خصم_الرصيد_بأمان(1): # خصم محاولة واحدة للترجمة
                    شريط_المعالجة()
                    try:
                        # لا يتم النداء على الذكاء الاصطناعي إلا بعد نجاح الخصم من الملف
                        استجابة = محرك_الذكاء.generate_content("ترجم ترجمة أكاديمية")
                        st.success("تمت الترجمة بنجاح")
                        st.write(استجابة.text)
                    except Exception as خطأ:
                        st.error(f"حدث خطأ في محرك المعالجة: {خطأ}")
                else:
                    st.error("❌ رصيدك الحالي لا يسمح بإتمام العملية. يرجى شحن الكود.")
            else:
                st.warning("يرجى رفع ملف المستند أولاً.")

    # --- تبويب توليد الصوت (حساب التكلفة حسب عدد الكلمات) ---
    with التبويبات[6]:
        نص_صوتي = st.text_area("أدخل النص الذي تود تحويله إلى صوت")
        if st.button("توليد الصوت الآن"):
            عدد_الكلمات = len(نص_صوتي.split())
            التكلفة_المحسوبة = (عدد_الكلمات // 41) + 1 if عدد_الكلمات > 0 else 0
            
            # التحقق من الرصيد والخصم كخطوة أولى دفاعية
            if خصم_الرصيد_بأمان(التكلفة_المحسوبة):
                شريط_المعالجة()
                st.success(f"تم خصم {التكلفة_المحسوبة} محاولات بنجاح.")
                st.audio("https://www.google.com") # رابط تجريبي
            else:
                st.error(f"رصيدك غير كافٍ. التكلفة لهذا النص هي {التكلفة_المحسوبة} محاولة.")

    st.markdown('<div class="تذييل_الصفحة">ScholarNode Academy © 2026</div>', unsafe_allow_html=True)

