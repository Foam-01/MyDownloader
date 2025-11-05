import os
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import yt_dlp
import requests # ⭐️ Import 'requests'

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
# --- ⭐️ API ใหม่: "Proxy Download" (v4) ⭐️ ---
# ---------------------------------------------------

@app.route('/download_video')
def download_video():
    url = request.args.get('url') # ⭐️ รับ URL จาก query string

    if not url:
        return jsonify({"error": "ไม่พบ URL"}), 400

    print(f"ได้รับคำขอ Proxy สำหรับ: {url}")

    # 1. ตั้งค่า yt-dlp ให้ "สกัดข้อมูล"
    ydl_opts = {
        'format': 'best[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
    }

    try:
        # 2. สกัดข้อมูล (หาลิงก์ตรง .mp4)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        direct_url = info.get('url')
        filename = info.get('title', 'video') + '.' + info.get('ext', 'mp4')

        if not direct_url:
            return jsonify({"error": "ไม่สามารถสกัดลิงก์ได้"}), 500

        print(f"กำลังสตรีมจาก: {filename}")
        
        # 3. ⭐️ (สำคัญ) สตรีมไฟล์จากลิงก์ตรง
        #    เซิร์ฟเวอร์ (Render) จะดาวน์โหลด และส่งต่อให้ผู้ใช้ทันที
        stream_response = requests.get(direct_url, stream=True)
        
        # 4. ⭐️ (สำคัญ) ส่งไฟล์กลับไป พร้อม Header "บังคับดาวน์โหลด"
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
    print(f"เซิร์ฟเวอร์ (v4 Proxy) กำลังทำงานที่ http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
    # Trigger deploy v4.1