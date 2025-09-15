# Basic test for downloader
import pytest
from src.downloader import download_video

# Note: This is a placeholder test. For real tests, use a mock or a sample video URL.
def test_download_video(monkeypatch):
    class DummyStream:
        def download(self, output_path):
            return f"{output_path}/dummy.mp4"
    class DummyYT:
        streams = type('obj', (object,), {'filter': lambda *a, **k: [DummyStream()]})
    monkeypatch.setattr('src.downloader.YouTube', lambda url: DummyYT())
    result = download_video("http://youtube.com/dummy", ".", "mp4")
    assert result.endswith(".mp4")
