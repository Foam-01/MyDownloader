📦 MyDownloader

A web application for downloading videos from various websites like YouTube, Facebook Reels, etc., using `yt-dlp` as its core downloading engine.

This project uses a Python Flask backend and an HTML/JavaScript frontend for pasting links and viewing real-time download status.

## 🔧 Tech Stack

* **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
* **Backend:** Python + Flask
* **Core Library:** `yt-dlp` (for video extraction and download)
* **Tools:** Git, GitHub

## 🚀 Features

* 🔐 **Web UI:** A web interface for pasting links, no command line needed.
* 📺 **Multi-Platform:** Supports downloading from various platforms (YouTube, Facebook, etc.).
* 💾 **Save to Downloads:** Automatically saves completed files to the user's "Downloads" folder.
* 📊 **Real-time Progress:** Displays progress bars and status (downloading/finished/failed) on the web page.
* ⚡ **Concurrent Downloads:** Supports downloading up to 15 files simultaneously.

## 🖥️ Screenshots
<img width="1910" height="962" alt="Screenshot 2025-11-05 113352" src="https://github.com/user-attachments/assets/bc6e963e-6209-4d2c-9856-1cf29435dd7c" />
<img width="1919" height="1078" alt="Screenshot 2025-11-05 113431" src="https://github.com/user-attachments/assets/59ea94e1-7967-4ea4-9a48-b3de3fc00101" />
<img width="1917" height="964" alt="Screenshot 2025-11-05 113231" src="https://github.com/user-attachments/assets/ee1bf617-7419-4dba-acd6-38183de7d754" />



https://github.com/user-attachments/assets/1b9cd2e1-fc69-49de-9a5e-bf23461f2271





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
    py -m pip install flask flask-cors yt-dlp uuid
    ```

4.  **Run the backend server:**
    ```bash
    py app.py
    ```
    (The server will run on `http://localhost:5000`)

5.  **Open the application:**
    Open your browser (Chrome, Firefox) and go to `http://localhost:5000` to start using the app.
