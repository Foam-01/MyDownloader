import os
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import yt_dlp
import requests 
import re # ⭐️ 1. Import เครื่องมือ "ทำความสะอาด"

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
# --- ⭐️ API (v5 - แก้ไขชื่อไฟล์) ⭐️ ---
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
        
        # ⭐️ 2. (สำคัญ!) "ทำความสะอาด" ชื่อไฟล์
        #    ลบอักขระพิเศษทั้งหมด (ที่ไม่ใช่ตัวอักษร, ตัวเลข, จุด, ขีด) แล้วแทนที่ด้วย "_"
        filename = re.sub(r'[^\w\.\- ]', '_', filename_raw)

        if not direct_url:
            return jsonify({"error": "ไม่สามารถสกัดลิงก์ได้"}), 500

        print(f"กำลังสตรีมจาก (Cleaned): {filename}")
        
        # 3. สตรีมไฟล์จากลิงก์ตรง
        stream_response = requests.get(direct_url, stream=True)
        
        # 4. ส่งไฟล์กลับไป พร้อม Header "บังคับดาวน์โหลด" (ด้วยชื่อที่สะอาดแล้ว)
        return Response(
            stream_response.iter_content(chunk_size=1024*1024),
            headers={
                'Content-Type': stream_response.headers['Content-Type'],
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        print(f"yt-dlp (Proxy) เกิดข้อผิดพลาด: {e}")
        return jsonify({"error": str(e)}), 500

# --- สั่งให้เซิร์ฟเวอร์รัน ---
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"เซิร์ฟเวอร์ (v5 Clean Filename) กำลังทำงานที่ http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)