import os
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import yt_dlp
import requests 
import re
from urllib.parse import quote # ⭐️ 1. Import เครื่องมือ "เข้ารหัส"

app = Flask(__name__)
CORS(app) 

# ---------------------------------------------------
# --- หน้าเว็บ (เหมือนเดิม) ---
# ---------------------------------------------------

@app.route('/')
def index():
    # เสิร์ฟหน้าเว็บ index.html
    return send_from_directory('.', 'index.html')

# ---------------------------------------------------
# --- ⭐️ API (v7 - เข้ารหัสชื่อไฟล์) ⭐️ ---
# ---------------------------------------------------

@app.route('/download_video')
def download_video():
    url = request.args.get('url') 

    if not url:
        return jsonify({"error": "ไม่พบ URL"}), 400

    print(f"ได้รับคำขอ Proxy สำหรับ: {url}")

    ydl_opts = {
        'format': 'best[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
    }

    try:
        # 1. สกัดข้อมูล (หาลิงก์ตรง .mp4)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        direct_url = info.get('url')
        filename_raw = info.get('title', 'video') + '.' + info.get('ext', 'mp4')
        
        # 2. "ทำความสะอาด" ชื่อไฟล์ (ลบอักขระพิเศษ แต่ยังเก็บภาษาไทยไว้)
        filename_clean = re.sub(r'[^\w\.\- ]', '_', filename_raw)

        # ⭐️ 3. (สำคัญ!) สร้างชื่อไฟล์ 2 เวอร์ชัน
        
        # เวอร์ชันที่ 1: สำหรับเบราว์เซอร์เก่า (ลบภาษาไทยทิ้งให้หมด)
        filename_ascii = re.sub(r'[^\x00-\x7F]', '_', filename_clean)
        
        # เวอร์ชันที่ 2: สำหรับเบราว์เซอร์ใหม่ (เข้ารหัสภาษาไทย)
        filename_utf8_encoded = quote(filename_clean)


        if not direct_url:
            return jsonify({"error": "ไม่สามารถสกัดลิงก์ได้"}), 500

        print(f"กำลังสตรีมจาก: {filename_clean}")
        
        # 4. สตรีมไฟล์จากลิงก์ตรง
        stream_response = requests.get(direct_url, stream=True)
        
        # ⭐️ 5. (สำคัญ!) ส่ง Header 2 แบบ (กันพลาด)
        #    เบราว์เซอร์ใหม่ (Chrome) จะใช้ `filename*` (ที่อ่านภาษาไทยออก)
        #    Gunicorn (เซิร์ฟเวอร์) จะไม่แครช เพราะทุกอย่างเป็นภาษาอังกฤษ (ASCII)
        return Response(
            stream_response.iter_content(chunk_size=1024*1024),
            headers={
                'Content-Type': stream_response.headers['Content-Type'],
                'Content-Disposition': f'attachment; filename="{filename_ascii}"; filename*="UTF-8\'\'{filename_utf8_encoded}"'
            }
        )

    except Exception as e:
        print(f"yt-dlp (Proxy) เกิดข้อผิดพลาด: {e}")
        return jsonify({"error": str(e)}), 500

# --- สั่งให้เซิร์ฟเวอร์รัน ---
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"เซิร์ฟเวอร์ (v7 RFC5987) กำลังทำงานที่ http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)