from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# OCR.space 免费 API Key（注册即得，无需信用卡）
OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY", "K86748998888957")  # 这是公共测试 key，建议替换为自己的

@app.route('/api/ocr', methods=['POST'])
def ocr():
    data = request.get_json()
    image_url = data.get('image_url', '') if data else ''
    if not image_url:
        return jsonify({"error": "缺少 image_url"}), 400

    # 调用 OCR.space 免费接口
    ocr_url = "https://api.ocr.space/parse/imageurl"
    payload = {
        "apikey": OCR_SPACE_API_KEY,
        "url": image_url,
        "language": "chs",        # 中英文混合识别
        "isOverlayRequired": False,
    }
    resp = requests.post(ocr_url, data=payload, timeout=30)
    result = resp.json()

    if result.get("IsErroredOnProcessing"):
        return jsonify({"error": result.get("ErrorMessage", "OCR 处理出错")}), 500

    parsed = result.get("ParsedResults", [])
    if not parsed:
        return jsonify({"text": ""})
    # 提取所有文本（多区域合并）
    text = parsed[0].get("ParsedText", "")
    return jsonify({"text": text.strip()})

# Vercel Serverless 需要暴露 handler
def handler(environ, start_response):
    return app(environ, start_response)