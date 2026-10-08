import os
import sys
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import yt_dlp
from yt_dlp.networking import Request
import re
import shutil
import tempfile
import imageio_ffmpeg
from urllib.parse import quote, urlparse # ⭐️ 1. Import เครื่องมือ "เข้ารหัส"

# console ของ Windows พิมพ์อีโมจิ/บางภาษาไม่ได้ -> แทนด้วย ? แทนที่จะ error ทั้งคำขอ
sys.stdout.reconfigure(errors='replace')

app = Flask(__name__)
CORS(app) 

# แพลตฟอร์มที่รองรับ: ชื่อ -> โดเมน
SUPPORTED_PLATFORMS = {
    'Facebook': ('facebook.com', 'fb.watch', 'fb.com'),
    'YouTube': ('youtube.com', 'youtu.be'),
    'TikTok': ('tiktok.com',),
}

def detect_platform(url):
    host = (urlparse(url).hostname or '').lower()
    for name, domains in SUPPORTED_PLATFORMS.items():
        if any(host == d or host.endswith('.' + d) for d in domains):
            return name
    return None

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

def make_disposition(filename_raw):
    # "ทำความสะอาด" ชื่อไฟล์ (ลบอักขระพิเศษ แต่ยังเก็บภาษาไทยไว้)
    filename_clean = re.sub(r'[^\w\.\- ]', '_', filename_raw)
    # เวอร์ชันที่ 1: สำหรับเบราว์เซอร์เก่า (ลบภาษาไทยทิ้งให้หมด)
    filename_ascii = re.sub(r'[^\x00-\x7F]', '_', filename_clean)
    # เวอร์ชันที่ 2: สำหรับเบราว์เซอร์ใหม่ (เข้ารหัสภาษาไทย)
    filename_utf8_encoded = quote(filename_clean)
    # ส่ง 2 แบบ: Chrome ใช้ `filename*` (อ่านภาษาไทยออก), Gunicorn ไม่แครชเพราะ header เป็น ASCII
    return f'attachment; filename="{filename_ascii}"; filename*="UTF-8\'\'{filename_utf8_encoded}"'


BASE_YDL_OPTS = {
    'noplaylist': True,
    'quiet': True,
    'noprogress': True,
    # YouTube ต้องใช้ JavaScript runtime (deno หรือ node) ในการถอดรหัสลิงก์วิดีโอ
    'js_runtimes': {'deno': {}, 'node': {}},
}


def friendly_error(message, platform):
    """แปลง error ของ yt-dlp (ภาษาอังกฤษยาว ๆ) เป็นข้อความที่ผู้ใช้อ่านเข้าใจ"""
    lower = message.lower()
    if 'not a bot' in lower or 'sign in to confirm' in lower:
        return f"{platform} บล็อกเซิร์ฟเวอร์ชั่วคราว กรุณาลองใหม่ภายหลัง"
    if 'private' in lower or 'login' in lower or 'log in' in lower:
        return "วิดีโอนี้เป็นแบบส่วนตัวหรือต้องล็อกอิน จึงดาวน์โหลดไม่ได้"
    if 'unavailable' in lower or 'not available' in lower or 'removed' in lower or 'does not exist' in lower:
        return "ไม่พบวิดีโอนี้ (อาจถูกลบหรือลิงก์ไม่ถูกต้อง)"
    if '403' in lower or '429' in lower:
        return f"{platform} ปฏิเสธการดาวน์โหลดชั่วคราว กรุณาลองใหม่ภายหลัง"
    # อื่น ๆ: ตัด "ERROR: [youtube] abc123: " ข้างหน้าออก
    return re.sub(r'^ERROR:\s*(\[[^\]]+\]\s*[^:]*:\s*)?', '', message)


@app.route('/download_video')
def download_video():
    url = request.args.get('url') 

    if not url:
        return jsonify({"error": "ไม่พบ URL"}), 400

    platform = detect_platform(url)
    if not platform:
        return jsonify({"error": "รองรับเฉพาะลิงก์ Facebook, YouTube และ TikTok"}), 400

    print(f"ได้รับคำขอ ({platform}) สำหรับ: {url}")

    try:
        if platform == 'YouTube':
            return download_youtube(url)
        return stream_direct(url)
    except Exception as e:
        print(f"yt-dlp ({platform}) เกิดข้อผิดพลาด: {e}")
        return jsonify({"error": friendly_error(str(e), platform)}), 500


def download_youtube(url):
    """YouTube: โหลดภาพ+เสียงแยกกันลงไฟล์ชั่วคราวแล้วรวมด้วย ffmpeg ก่อนส่ง

    YouTube ไม่มีไฟล์รวมภาพ+เสียงที่โหลดได้เสถียรแล้ว (format 18 ต้องใช้ PO Token
    ถ้าไม่มี คลิปยาวจะโดน 403 กลางทาง) จึงต้องโหลดมารวมเองบนเซิร์ฟเวอร์
    """
    tmp_dir = tempfile.mkdtemp(prefix='mydl_')
    ydl_opts = BASE_YDL_OPTS | {
        # จำกัด 720p ให้โหลดเร็ว, เลือก mp4+m4a ก่อนเพื่อไม่ต้องแปลงไฟล์
        'format': 'bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]'
                  '/bv*[height<=720]+ba/b[height<=720]/b',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(tmp_dir, 'video.%(ext)s'),
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        file_path = os.path.join(tmp_dir, os.listdir(tmp_dir)[0])
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    ext = os.path.splitext(file_path)[1].lstrip('.') or 'mp4'
    filename_raw = info.get('title', 'video') + '.' + ext
    print(f"กำลังส่งไฟล์: {filename_raw}")

    def generate():
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(1024 * 1024):
                    yield chunk
        finally:
            # ลบไฟล์ชั่วคราวเสมอ แม้ผู้ใช้จะยกเลิกกลางทาง
            shutil.rmtree(tmp_dir, ignore_errors=True)

    response = Response(generate(), headers={
        'Content-Type': 'video/mp4' if ext == 'mp4' else 'application/octet-stream',
        'Content-Disposition': make_disposition(filename_raw),
        'Content-Length': str(os.path.getsize(file_path)),
    })
    # กันไว้อีกชั้น: ถ้าผู้ใช้ปิดหน้าเว็บก่อนเริ่มส่งไฟล์ generate() จะไม่ได้ทำงานเลย
    response.call_on_close(lambda: shutil.rmtree(tmp_dir, ignore_errors=True))
    return response


def stream_direct(url):
    """Facebook / TikTok: มีไฟล์รวมภาพ+เสียงอยู่แล้ว สตรีมต่อให้เบราว์เซอร์ได้เลย"""
    ydl_opts = BASE_YDL_OPTS | {
        # ต้องเป็นไฟล์เดียวที่มีทั้งภาพและเสียง และเป็นลิงก์ไฟล์ตรง (http/https) ไม่ใช่ m3u8
        # (ใช้ !=? เพราะ Facebook ไม่บอก codec มา)
        'format': 'best[ext=mp4][vcodec!=?none][acodec!=?none][protocol^=http]'
                  '/best[vcodec!=?none][acodec!=?none][protocol^=http]',
    }
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    try:
        info = ydl.extract_info(url, download=False)
        direct_url = info.get('url')
        if not direct_url:
            raise ValueError("ไม่สามารถสกัดลิงก์ได้")

        # ให้ yt-dlp เป็นคนเปิดลิงก์เอง เพราะ TikTok ต้องใช้ cookie + การปลอมตัวเป็นเบราว์เซอร์
        # ชุดเดียวกับตอนสกัดข้อมูล (ถ้าใช้ requests ธรรมดาจะโดน 403)
        stream_response = ydl.urlopen(Request(direct_url, headers=info.get('http_headers', {})))
    except Exception:
        ydl.close()
        raise

    filename_raw = info.get('title', 'video') + '.' + info.get('ext', 'mp4')
    print(f"กำลังสตรีม: {filename_raw}")

    def generate():
        try:
            while chunk := stream_response.read(1024 * 1024):
                yield chunk
        finally:
            # ปิดการเชื่อมต่อเสมอ แม้ผู้ใช้จะยกเลิกกลางทาง
            stream_response.close()
            ydl.close()

    headers = {
        'Content-Type': stream_response.headers.get('Content-Type', 'video/mp4'),
        'Content-Disposition': make_disposition(filename_raw),
    }
    if stream_response.headers.get('Content-Length'):
        headers['Content-Length'] = stream_response.headers['Content-Length']
    return Response(generate(), headers=headers)

# --- สั่งให้เซิร์ฟเวอร์รัน ---
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"เซิร์ฟเวอร์ (v9) กำลังทำงานที่ http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)