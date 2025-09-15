# Handles downloading and conversion logic using yt-dlp
import yt_dlp
import os

def download_video(url, output_path, format="mp4"):
    try:
        # Set output template and format options
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': format,
            'quiet': True,
            'ffmpeg_location': os.path.join('assets', 'ffmpeg.exe'),  # Correct path if ffmpeg.exe is in assets
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        # Find the downloaded file (best effort)
        info_dict = yt_dlp.YoutubeDL({'quiet': True}).extract_info(url, download=False)
        title = info_dict.get('title', 'video')
        out_file = os.path.join(output_path, f"{title}.{format}")
        return out_file
    except Exception as e:
        raise RuntimeError(f"Download failed: {e}")