import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp

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
# --- ⭐️ API ใหม่: "ขอลิงก์ตรง" (ไม่ใช่ดาวน์โหลด) ⭐️ ---
# ---------------------------------------------------

@app.route('/get_download_link', methods=['POST'])
def get_download_link():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "ไม่พบ URL"}), 400

    print(f"ได้รับคำขอลิงก์สำหรับ: {url}")

    # ⭐️ ตั้งค่า yt-dlp ให้ "สกัดข้อมูล" (download=False)
    ydl_opts = {
        'format': 'best[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # ขอ mp4 ดีที่สุด
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ⭐️ สั่ง "สกัดข้อมูล" ไม่ใช่ "ดาวน์โหลด"
            info = ydl.extract_info(url, download=False)
        
        # ⭐️ ค้นหาลิงก์ดาวน์โหลดที่ดีที่สุด
        download_url = info.get('url')
        filename = info.get('title', 'video') + '.' + info.get('ext', 'mp4')

        if not download_url:
            return jsonify({"error": "ไม่สามารถสกัดลิงก์ได้"}), 500

        print(f"ส่งลิงก์ตรงกลับไป: {filename}")
        
        # ⭐️ ส่งลิงก์ตรง และชื่อไฟล์ กลับไปให้หน้าเว็บ
        return jsonify({
            "direct_url": download_url,
            "filename": filename
        })

    except Exception as e:
        print(f"yt-dlp เกิดข้อผิดพลาด: {e}")
        return jsonify({"error": str(e)}), 500

# --- สั่งให้เซิร์ฟเวอร์รัน ---
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000)) # ⭐️ ใช้ Port ที่ Render กำหนด
    print(f"เซิร์ฟเวอร์ (แกะลิงก์) กำลังทำงานที่ http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False) # ⭐️ รันบน 0.0.0.0