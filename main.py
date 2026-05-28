import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
import os

# إعداد محرك Gemini
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def get_gemini_response(prompt, model="gemini-2.0-flash"):
    """دالة مركزية للاتصال بـ Gemini مع مراعاة التكلفة"""
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
            ),
        )
        return response.text
    except Exception as e:
        return f"خطأ في الاتصال: {e}"

# --- التبويبات والخدمات ---
def render_main_interface():
    # هنا يتم وضع التبويبات الثمانية
    # كل تبويب يستدعي دالة الخصم المالية قبل تنفيذ أي أمر
    pass

def deduct_balance(tab_name, input_content):
    """السياسة المالية: حساب الخصم التلقائي حسب نوع الخدمة"""
    # 1. معاينة/مراجعة: 1 محاولة لكل صفحة
    # 2. توليد الصوت: 1 محاولة لكل 40 كلمة
    # 3. المستشار: 1 محاولة لكل 700 كلمة
    # 4. الصور: 5 محاولات
    pass

# --- نظام الإدارة ---
if st.session_state.get('user_code') == "HAYDER_2026$$$":
    # عرض تبويبات الإدارة (توليد الكودات، مراقبة الكودات المفعلة)
    pass
