# MainWindow UI for YouTube Downloader
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox, QProgressDialog, QRadioButton, QButtonGroup
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from src.downloader import download_video
from PyQt5.QtGui import QPixmap, QIcon
import glob
import os
import requests

class DownloadThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)  # Add this signal

    def __init__(self, url, output_dir, fmt):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.fmt = fmt
        self._is_cancelled = False

    def run(self):
        import yt_dlp

        self.status.emit("Preparing download...")  # Emit status before starting

        def hook(d):
            if d['status'] == 'downloading':
                self.status.emit("Downloading...")  # Update label when download starts
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    percent = int(downloaded / total * 100)
                    self.progress.emit(percent)
                if self._is_cancelled:
                    raise Exception("Download cancelled by user.")

        try:
            # Handle audio-only formats
            if self.fmt in ["mp3", "aac"]:
                ydl_opts = {
                    'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'ffmpeg_location': os.path.join('assets', 'ffmpeg.exe'),
                    'progress_hooks': [hook],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.fmt,
                        'preferredquality': '192',
                    }],
                }
            else:
                ydl_opts = {
                    'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': self.fmt,
                    'quiet': True,
                    'ffmpeg_location': os.path.join('assets', 'ffmpeg.exe'),
                    'progress_hooks': [hook],
                }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            info_dict = yt_dlp.YoutubeDL({'quiet': True}).extract_info(self.url, download=False)
            title = info_dict.get('title', 'video')
            out_file = os.path.join(self.output_dir, f"{title}.{self.fmt}")
            self.finished.emit(out_file)
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self._is_cancelled = True

class InfoThread(QThread):
    info_ready = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            import yt_dlp
            ydl_opts = {'quiet': True, 'skip_download': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
            self.info_ready.emit(info)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setWindowIcon(QIcon(os.path.join('assets', 'logo.png')))  # <-- Add this line
        self.setGeometry(100, 100, 400, 200)
        self.init_ui()
        self.output_dir = None
        self.video_info = None  # Store preloaded info

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Add logo at the top
        logo_label = QLabel()
        logo_pixmap = QPixmap(os.path.join('assets', 'logo.png'))
        logo_label.setPixmap(logo_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        self.url_label = QLabel("YouTube URL:")
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.textChanged.connect(self.preload_video_info)

        self.info_btn = QPushButton("Info")
        self.info_btn.clicked.connect(self.show_video_info)

        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.info_btn)
        layout.addWidget(self.url_label)
        layout.addLayout(url_layout)

        # Thumbnail label
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(320, 180)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.thumbnail_label)

        # Format type selector
        self.format_type_group = QButtonGroup(self)
        self.video_radio = QRadioButton("Video")
        self.audio_radio = QRadioButton("Audio")
        self.video_radio.setChecked(True)
        self.format_type_group.addButton(self.video_radio)
        self.format_type_group.addButton(self.audio_radio)
        format_type_layout = QHBoxLayout()
        format_type_layout.addWidget(self.video_radio)
        format_type_layout.addWidget(self.audio_radio)
        layout.addLayout(format_type_layout)

        # Video format combo
        self.video_format_combo = QComboBox()
        self.video_format_combo.addItems(["mp4", "avi", "mov", "webm"])
        layout.addWidget(self.video_format_combo)

        # Audio format combo
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["mp3", "aac"])
        self.audio_format_combo.hide()
        layout.addWidget(self.audio_format_combo)

        # Connect radio buttons to show/hide combos
        self.video_radio.toggled.connect(self.toggle_format_combo)

        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.download)
        layout.addWidget(self.download_btn)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def toggle_format_combo(self):
        if self.video_radio.isChecked():
            self.video_format_combo.show()
            self.audio_format_combo.hide()
        else:
            self.video_format_combo.hide()
            self.audio_format_combo.show()

    def preload_video_info(self):
        url = self.url_input.text()
        if not url:
            self.video_info = None
            return
        # Show "Please wait" dialog
        self.info_progress = QProgressDialog("Please wait, fetching info...", None, 0, 0, self)
        self.info_progress.setWindowTitle("Fetching Info")
        self.info_progress.setWindowIcon(QIcon(os.path.join('assets', 'logo.png')))
        self.info_progress.setWindowModality(Qt.ApplicationModal)
        self.info_progress.setCancelButton(None)
        self.info_progress.show()

        self.info_thread = InfoThread(url)
        self.info_thread.info_ready.connect(self.on_info_ready)
        self.info_thread.error.connect(self.on_info_error)
        self.info_thread.start()

    def on_info_ready(self, info):
        self.video_info = info
        if hasattr(self, 'info_progress'):
            self.info_progress.close()
        # Display thumbnail
        thumb_url = info.get('thumbnail')
        if thumb_url:
            try:
                response = requests.get(thumb_url)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    self.thumbnail_label.setPixmap(pixmap.scaled(
                        self.thumbnail_label.width(),
                        self.thumbnail_label.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    ))
                else:
                    self.thumbnail_label.clear()
            except Exception:
                self.thumbnail_label.clear()
        else:
            self.thumbnail_label.clear()

    def on_info_error(self, error):
        self.video_info = None
        if hasattr(self, 'info_progress'):
            self.info_progress.close()
        print(f"Info fetch error: {error}")

    def show_video_info(self):
        if not self.url_input.text():
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL first.")
            return
        if not self.video_info:
            QMessageBox.warning(self, "Error", "Could not fetch video info yet. Please wait or check the URL.")
            return
        info = self.video_info
        title = info.get('title', 'N/A')
        duration = info.get('duration', 0)
        duration_min = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
        filesize = info.get('filesize') or info.get('filesize_approx')
        filesize_mb = f"{filesize / (1024*1024):.2f} MB" if filesize else "N/A"
        channel = info.get('uploader', 'N/A')
        description = info.get('description', '')
        msg = (
            f"<b>Title:</b> {title}<br>"
            f"<b>Channel:</b> {channel}<br>"
            f"<b>Duration:</b> {duration_min} min<br>"
            f"<b>Size:</b> {filesize_mb}<br>"
            f"<b>Description:</b> {description[:200]}{'...' if len(description) > 200 else ''}"
        )
        QMessageBox.information(self, "Video Info", msg)

    def download(self):
        url = self.url_input.text()
        if self.video_radio.isChecked():
            fmt = self.video_format_combo.currentText()
        else:
            fmt = self.audio_format_combo.currentText()
        self.output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not url or not self.output_dir:
            QMessageBox.warning(self, "Error", "Please enter a URL and select output directory.")
            return

        self.progress = QProgressDialog("Preparing download...", "Cancel", 0, 100, self)
        self.progress.setWindowTitle("Please Wait")
        self.progress.setWindowIcon(QIcon(os.path.join('assets', 'logo.png')))
        self.progress.setWindowModality(Qt.ApplicationModal)
        self.progress.setValue(0)
        self.progress.canceled.connect(self.cancel_download)
        self.progress.show()

        self.thread = DownloadThread(url, self.output_dir, fmt)
        self.thread.status.connect(self.on_download_status)  # Connect status signal
        self.thread.progress.connect(self.on_download_progress)
        self.thread.finished.connect(self.on_download_finished)
        self.thread.error.connect(self.on_download_error)
        self.thread.finished.connect(self.cleanup_part_files)
        self.thread.error.connect(self.cleanup_part_files)
        self.thread.start()

    def cancel_download(self):
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.cancel()

    def cleanup_part_files(self, *args):
        # Remove .part files in the output directory after thread finishes/errors
        if self.output_dir:
            part_files = glob.glob(os.path.join(self.output_dir, "*.part"))
            for f in part_files:
                try:
                    os.remove(f)
                except Exception as e:
                    print(f"Could not remove {f}: {e}")

    def on_download_status(self, message):
        self.progress.setLabelText(message)

    def on_download_progress(self, percent):
        self.progress.setValue(percent)

    def on_download_finished(self, out_file):
        self.progress.close()
        QMessageBox.information(self, "Success", f"Downloaded and saved as {out_file}")

    def on_download_error(self, error):
        self.progress.close()
        print(f"Download error: {error}")
        if "cancelled by user" in error.lower():
            QMessageBox.information(self, "Cancelled", "Download was cancelled.")
        else:
            QMessageBox.critical(self, "Error", error)
