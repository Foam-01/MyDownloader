# 📦 MyDownloader

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
* ⚡ **Concurrent Downloads:** Supports downloading up to 5 files simultaneously.

## 🖥️ Screenshots

*(Add screenshots of the application here. You can upload images to your GitHub repository and link them.)*

## 🔗 Repository

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
