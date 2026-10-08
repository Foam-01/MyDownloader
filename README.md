📦 MyDownloader

A web application for downloading videos from **Facebook, YouTube and TikTok**, using `yt-dlp` as its core downloading engine.

This project uses a Python Flask backend and an HTML/JavaScript frontend for pasting links and viewing real-time download status.

## 🔧 Tech Stack

* **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
* **Backend:** Python + Flask
* **Core Library:** `yt-dlp` (for video extraction and download)
* **Tools:** Git, GitHub

## 🚀 Features

* 🔐 **Web UI:** A web interface for pasting links, no command line needed.
* 📺 **Multi-Platform:** Supports the main platforms:
  | Platform | Example links |
  |---|---|
  | Facebook | `facebook.com/...` (videos, Reels), `fb.watch/...` |
  | YouTube | `youtube.com/watch?v=...`, `youtube.com/shorts/...`, `youtu.be/...` |
  | TikTok | `tiktok.com/@user/video/...`, `vt.tiktok.com/...` |

  Links from other sites are rejected with a clear error message.

  > ⚠️ **YouTube works only when you run the app on your own computer.** YouTube blocks cloud servers (such as Render), so on the live demo YouTube links show "YouTube บล็อกเซิร์ฟเวอร์ชั่วคราว" instead. Facebook and TikTok work on the live demo.
* 💾 **Save to Downloads:** Automatically saves completed files to the user's "Downloads" folder.
* 📊 **Real-time Progress:** Displays progress bars and status (downloading/finished/failed) on the web page.
* ⚡ **Concurrent Downloads:** Supports downloading up to 10 files simultaneously.

## 🖥️ Screenshots

<img width="1919" height="970" alt="image" src="https://github.com/user-attachments/assets/59df354d-832f-414f-8a52-4f30eb9c815d" />
<img width="1917" height="913" alt="Screenshot 2025-11-05 135940" src="https://github.com/user-attachments/assets/7a2c7096-c0d8-4786-a24a-00a7ae4cffb8" />
<img width="1917" height="923" alt="Screenshot 2025-11-05 140230" src="https://github.com/user-attachments/assets/c54a889b-ad51-4adb-86e2-b32c893784a8" />



https://github.com/user-attachments/assets/d86b9e71-31c7-4d7c-a8cf-304710297462



## 🔗 Demo & Repository
- Live Demo: [https://your-live-demo-link.com ](https://oneclickdownload.netlify.app/) 
- GitHub: [https://github.com/Foam-01/pos-inventory-system](https://github.com/Foam-01/MyDownloader)
* **GitHub:** `https://github.com/Foam-01/MyDownloader`

## 🏁 Getting Started

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Foam-01/MyDownloader.git](https://github.com/Foam-01/MyDownloader.git)
    ```

2.  **Navigate to the project directory:**
    ```bash
    cd MyDownloader
    ```

3.  **Install required libraries (Backend):**
    ```bash
    # Make sure you are using the python launcher 'py' if 'pip' isn't in your PATH
    py -m pip install -r requirements.txt
    ```

4.  **Run the backend server:**
    ```bash
    py app.py
    ```
    (The server will run on `http://localhost:5000`)

5.  **Open the application:**
    Open your browser (Chrome, Firefox) and go to `http://localhost:5000` to start using the app.
    When opened from `localhost`, the page calls your local server; otherwise it uses the hosted API on Render.

## ⚙️ How each platform is downloaded

* **Facebook / TikTok:** the video file already contains picture + sound, so the server streams it straight to the browser (the progress bar moves right away).
* **YouTube:** YouTube now serves picture and sound as separate files. The server downloads both (up to **720p**), merges them with `ffmpeg` (bundled via `imageio-ffmpeg`), then sends the finished `.mp4`. The page shows "preparing" while this runs; longer videos take longer.
* YouTube also needs a JavaScript runtime (`deno`, installed from `requirements.txt`, or `node`).

## ⚠️ Notes

* Private videos, or videos that require login, cannot be downloaded.
* If a platform changes its site and downloads start failing, update `yt-dlp`: `py -m pip install -U "yt-dlp[default,curl-cffi]"`
* Pressing the download button again while files are downloading is safe: running downloads keep going and keep their progress bars.
