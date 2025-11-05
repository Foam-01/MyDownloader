import os
import threading
import uuid       # ⭐️ ใช้สร้าง ID ที่ไม่ซ้ำกัน
import pathlib    # ⭐️ ใช้หาโฟลเดอร์ Downloads
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp

# --- ⭐️ ส่วนตั้งค่าใหม่ ⭐️ ---

# หาตำแหน่งโฟลเดอร์ "Downloads" ของผู้ใช้
# เช่น C:\Users\GIGABYTE\Downloads
DOWNLOAD_FOLDER = str(pathlib.Path.home() / "Downloads")
print(f"ไฟล์ทั้งหมดจะถูกบันทึกไปที่: {DOWNLOAD_FOLDER}")
# สร้างโฟลเดอร์ถ้ายังไม่มี
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True) 

# ⭐️ พจนานุกรมกลางสำหรับเก็บสถานะการดาวน์โหลด (key คือ download_id)
# 
# ตัวอย่าง:
# download_progress = {
#     "id-12345": {"status": "downloading", "percent": 50.5, "filename": "video1.mp4"},
#     "id-67890": {"status": "finished", "percent": 100, "filename": "video2.mp4"}
# }
download_progress = {}

# ---------------------------------------------------
# --- ส่วนของเซิร์ฟเวอร์ Flask ---
# ---------------------------------------------------

app = Flask(__name__)
CORS(app) 

@app.route('/')
def index():
    # เสิร์ฟหน้าเว็บ index.html
    return send_from_directory('.', 'index.html')

# ---------------------------------------------------
# --- ⭐️ API ใหม่สำหรับ "ถาม" สถานะ ⭐️ ---
# ---------------------------------------------------

@app.route('/status/<download_id>')
def get_status(download_id):
    """
    API ที่หน้าเว็บจะยิงมาถามทุกวินาที ว่าไฟล์นี้ถึงไหนแล้ว
    """
    progress = download_progress.get(download_id)
    if not progress:
        return jsonify({"status": "error", "message": "ไม่พบ ID"}), 404
    
    return jsonify(progress)

# ---------------------------------------------------
# --- ⭐️ API ดาวน์โหลด (อัปเกรด) ⭐️ ---
# ---------------------------------------------------

@app.route('/download', methods=['POST'])
def handle_download():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "ไม่พบ URL"}), 400

    # 1. สร้าง ID ที่ไม่ซ้ำกันสำหรับไฟล์นี้
    download_id = str(uuid.uuid4())

    # 2. เก็บสถานะเริ่มต้นไว้ในพจนานุกรมกลาง
    download_progress[download_id] = {
        "status": "pending",  # สถานะ: กำลังรอ
        "percent": 0,
        "filename": "กำลังเตรียม...",
        "url": url
    }

    print(f"ได้รับคำสั่ง (ID: {download_id}): {url}")
    
    # 3. สั่งรัน Thread โดยส่ง download_id ไปด้วย
    download_thread = threading.Thread(
        target=download_with_yt_dlp, 
        args=(url, download_id, DOWNLOAD_FOLDER) # ⭐️ ส่ง ID และโฟลเดอร์ Downloads
    )
    download_thread.start()

    # 4. ตอบกลับหน้าเว็บทันที โดยส่ง ID กลับไปด้วย
    return jsonify({"message": "เริ่มดาวน์โหลดแล้ว!", "download_id": download_id})


# ---------------------------------------------------
# --- ⭐️ ฟังก์ชันดาวน์โหลด (อัปเกรด) ⭐️ ---
# ---------------------------------------------------

def download_with_yt_dlp(url, download_id, download_path):
    """
    ใช้ yt-dlp เพื่อดาวน์โหลดวิดีโอ (ถูกรันใน Thread)
    """
    
    # ⭐️ Hook ที่ yt-dlp จะเรียกใช้เพื่อรายงานความคืบหน้า
    #    เราใช้ 'lambda' เพื่อส่ง download_id เข้าไปใน hook ด้วย
    def progress_hook(d):
        # ดึงสถานะปัจจุบันจากพจนานุกรมกลาง
        current_progress = download_progress.get(download_id, {})
        
        if d['status'] == 'downloading':
            current_progress['status'] = 'downloading'
            current_progress['percent'] = d.get('_percent_str', '0%').strip('%')
            current_progress['filename'] = d.get('filename', 'กำลังโหลด...').split('/')[-1]
            
            # อัปเดตสถานะกลับไปที่พจนานุกรมกลาง
            download_progress[download_id] = current_progress
            
            # (แสดงใน CMD ด้วยก็ได้)
            # print(f"  -> ID: {download_id} กำลังดาวน์โหลด: {d['_percent_str']} ({d['_speed_str']})", end='\r')

        elif d['status'] == 'finished':
            current_progress['status'] = 'finished'
            current_progress['percent'] = 100
            current_progress['filename'] = d.get('filename', 'N/A').split('/')[-1]
            download_progress[download_id] = current_progress
            print(f"\n  -> ID: {download_id} เสร็จสิ้น!")
            
        elif d['status'] == 'error':
            current_progress['status'] = 'error'
            current_progress['filename'] = "ดาวน์โหลดล้มเหลว"
            download_progress[download_id] = current_progress
            print(f"\n  -> ID: {download_id} ล้มเหลว!")

    # ตั้งค่าตัวเลือกสำหรับ yt-dlp
    ydl_opts = {
        'format': 'best',
        # ⭐️ เปลี่ยนที่เก็บไฟล์ไปที่ DOWNLOAD_FOLDER
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'), 
        'progress_hooks': [progress_hook], # ⭐️ เรียกใช้ hook ของเรา
        'quiet': True, # ⭐️ ปิด log ของ yt-dlp (เพราะเราทำเอง)
    }

    try:
        # สั่งให้ yt-dlp เริ่มทำงาน
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
    except Exception as e:
        print(f"yt-dlp เกิดข้อผิดพลาด (ID: {download_id}): {e}")
        # ⭐️ แจ้งสถานะ error
        if download_id in download_progress:
            download_progress[download_id]['status'] = 'error'
            download_progress[download_id]['filename'] = str(e)


# --- สั่งให้เซิร์ฟเวอร์รัน (เหมือนเดิม) ---
if __name__ == "__main__":
    print(f"เซิร์ฟเวอร์ดาวน์โหลด (YT-DLP v2) กำลังทำงานที่ http://localhost:5000")
    print(f"ไฟล์จะถูกบันทึกที่: {DOWNLOAD_FOLDER}")
    app.run(port=5000, debug=False)