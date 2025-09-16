![YouTube Downloader Demo](https://github.com/user-attachments/assets/123d92b8-26d1-403c-af10-e4c2030057b3)

# YouTube Downloader

A powerful and user-friendly Python application that allows you to download YouTube videos and convert them into various formats with a simple graphical user interface (GUI).

## Key Features
* **Flexible Downloading:** Choose to download content as a video (MP4, AVI, MOV, WebM) or an audio-only MP3 file.
* **Live Previews:** See a thumbnail of the video instantly after you paste a YouTube link.
* **Detailed Video Information:** Use the "Info" button to view essential video details, including the title, channel name, video duration, file size, and a full description.

## Requirements
* **[Python 3.8+](https://www.python.org/downloads/release/python-3137/)**
* **[ffmpeg](https://ffmpeg.org/download.html)** (needed for converting videos to MP3/other formats)
---

## Setup and Installation

Follow these steps to get the program running on your local machine.

### 1. Clone the Repository
Open your command prompt or terminal and clone the project from GitHub.

```bash
git clone https://github.com/MikeyLevine/youtube-downloader.git
cd youtube-downloader
```
### 2. Create a Virtual Environment
It's recommended to create a virtual environment to manage dependencies.

```bash
python -m venv .venv
```

### 3. Activate the Environment
Activate the new virtual environment before installing the project's dependencies.
### On Windows (PowerShell)

```bash
.\.venv\Scripts\Activate.ps1
```
#### On macOS/Linux

```bash
source .venv/bin/activate
```

### 4. Usage
Run the main script to start the application.

```bash
python src/main.py
```


