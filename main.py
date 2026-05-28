from flask import Flask, request, jsonify

app = Flask(__name__)

# قاعدة بيانات وهمية (يتم استبدالها بقاعدة بيانات حقيقية لاحقاً)
user_database = {
    "CODE123": {"attempts": 100, "status": "active"},
    "HAYDER_2026$$$": {"role": "admin"} # كود الإدارة
}

def check_and_deduct(code, cost):
    """دالة خصم المحاولات المركزية"""
    if code in user_database and user_database[code].get("status") == "active":
        if user_database[code]["attempts"] >= cost:
            user_database[code]["attempts"] -= cost
            return True, user_database[code]["attempts"]
    return False, 0

@app.route('/api/translate', methods=['POST'])
def translate_document():
    data = request.json
    code = data.get("code")
    pages = data.get("pages") # عدد الصفحات يحدد التكلفة
    
    # كل صفحة تعد محاولة واحدة
    success, remaining = check_and_deduct(code, pages)
    
    if success:
        # هنا يتم استدعاء Gemini API للترجمة
        # result = gemini_api.translate(data['text'])
        return jsonify({"status": "success", "remaining_attempts": remaining})
    else:
        return jsonify({"status": "error", "message": "رصيد غير كافٍ أو كود غير صالح"})

@app.route('/api/generate_image', methods=['POST'])
def generate_image():
    code = data.get("code")
    # خصم 5 محاولات للصورة الواحدة
    success, remaining = check_and_deduct(code, 5)
    
    if success:
        return jsonify({"status": "image_generated", "remaining": remaining})
    return jsonify({"status": "error", "message": "رصيد غير كافٍ"})

if __name__ == '__main__':
    app.run(debug=True)
