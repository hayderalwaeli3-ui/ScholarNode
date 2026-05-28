import streamlit as st
import google.generativeai as genai
import os

# إعدادات الصفحة
st.set_page_config(page_title="ScholarNode Academy", layout="wide")

# إعداد الـ API
genai.configure(api_key="YOUR_GOOGLE_API_KEY") 

# --- دوال المنطق ---
def check_code_valid(code):
    # هنا يتم الربط مع مستودع البيانات الخاص بك للتحقق من الكود
    return True # مثال

# --- الواجهة ---
if 'logged_in' not in st.session_state:
    st.markdown("## ScholarNode")
    code = st.text_input("ادخل كود التفعيل", type="password")
    if st.button("دخول المنصة"):
        if code == "HAYDER_2026$$$":
            st.session_state['role'] = 'admin'
            st.session_state['logged_in'] = True
            st.rerun()
        elif check_code_valid(code):
            st.session_state['role'] = 'user'
            st.session_state['logged_in'] = True
            st.rerun()
    
    # معلومات الدفع في الجانب
    st.sidebar.info("### معلومات الدفع\n**ماستر كارد الرافدين:** 8369719342\n**الاسم:** HAYDER Z. JASIM\n**الهاتف:** 07879974395")

else:
    # القائمة الجانبية (شريط الأدوات)
    st.sidebar.title("إعدادات المشترك")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.clear()
        st.rerun()

    # التبويبات الرئيسية
    tabs = st.tabs(["معاينة ومناقشة", "المراجعة الأكاديمية", "الترجمة الأكاديمية", "ترجمة قانونية", "توليد الصور", "المستشار الذكي"])

    with tabs[0]:
        st.header("معاينة ومناقشة المستند")
        file = st.file_uploader("Upload", key="file1")
        lang = st.selectbox("اللغة المستهدفة", ["العربية", "English"])
        if file and st.button("بدء المعالجة"):
            with st.spinner("جاري المعالجة..."):
                progress = st.progress(0)
                # منطق الربط مع Gemini هنا
                progress.progress(100)
                st.success("تمت المعالجة")

    with tabs[1]:
        st.header("المراجعة الأكاديمية والنقدية")
        file = st.file_uploader("Upload", key="file2")
        # حساب التكلفة بناءً على عدد الصفحات
        st.write("تكلفة الإجراء: عدد الصفحات × 1 محاولة")
        if file:
            if st.button("تحليل"):
                st.write("جاري التحليل الأكاديمي...")

    with tabs[2]:
        st.header("الترجمة الأكاديمية الاحترافية")
        file = st.file_uploader("Upload", key="file3")
        lang = st.selectbox("إلى لغة:", ["English", "العربية"])
        if st.button("ترجمة"):
            st.write("جاري الترجمة مع الحفاظ على التنسيق...")

    with tabs[3]:
        st.header("ترجمة المستندات القانونية")
        st.file_uploader("Upload", key="file4")
        st.button("تنفيذ الترجمة القانونية")

    with tabs[4]:
        st.header("توليد الصور والمخططات")
        prompt = st.text_input("وصف الصورة أو المخطط")
        if st.button("توليد الصورة"):
            st.write("جاري التوليد (خصم 5 محاولات)...")

    with tabs[5]:
        st.header("المستشار الذكي")
        question = st.text_area("اطرح سؤالك هنا")
        if st.button("إرسال"):
            st.write("جاري الرد...")

    # واجهة الإدارة
    if st.session_state.get('role') == 'admin':
        st.sidebar.divider()
        st.sidebar.subheader("لوحة تحكم الإدارة")
        st.sidebar.write("توليد كودات - فحص سلامة API")
