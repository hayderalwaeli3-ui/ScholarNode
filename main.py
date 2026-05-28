import streamlit as st
from docx import Document
from io import BytesIO
import PIL.Image as Image

# --- دالة إنشاء ملف وورد وتحميله ---
def download_as_word(text, filename="output.docx"):
    doc = Document()
    doc.add_paragraph(text)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- دالة حفظ الصورة وتحميلها ---
def download_as_image(image, filename="image.jpeg"):
    bio = BytesIO()
    image.save(bio, format="JPEG")
    return bio.getvalue()

# --- داخل التبويب (مثلاً التبويب الأول) ---
with tabs[0]:
    st.header("معاينة ومناقشة المستند")
    file = st.file_uploader("Upload", key="file1")
    
    if file and st.button("بدء المعالجة"):
        with st.spinner("جاري المعالجة..."):
            # افتراضياً، هذا هو النص الناتج من Gemini
            result_text = "هنا ستظهر نتيجة المعالجة والتحليل الأكاديمي للملف..."
            st.success("تمت المعالجة بنجاح")
            
            # زر التحميل الخاص بملف الوورد
            word_data = download_as_word(result_text)
            st.download_button(
                label="تحميل النتيجة كملف Word",
                data=word_data,
                file_name="ScholarNode_Result.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

# --- داخل تبويب توليد الصور ---
with tabs[4]:
    st.header("توليد الصور")
    if st.button("توليد الصورة"):
        # هنا يتم استدعاء نموذج توليد الصور (مثال: نموذج وهمي)
        generated_image = Image.new('RGB', (500, 500), color='blue') # استبدل هذا بـ Gemini Image API
        st.image(generated_image)
        
        # زر التحميل الخاص بالصورة
        img_data = download_as_image(generated_image)
        st.download_button(
            label="تحميل الصورة بصيغة JPEG",
            data=img_data,
            file_name="generated_image.jpeg",
            mime="image/jpeg"
        )
