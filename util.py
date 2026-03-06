from os import makedirs

from PySide6.QtCore import QThread, Signal
from yt_dlp import YoutubeDL

class DownloadAudio:
    def download_audio(self, url, ext, yd):
        makedirs("./audios", exist_ok=True)

        ydl_opt = {
            'format': 'bestaudio/best',
            'outtmpl': './audios/%(title)s.%(ext)s',
            'ffmpeg_location': "./ffmpeg_bin/",
            'progress_hooks': [yd.progress_hook],
            'postprocessor_hooks': [yd.postprocessor_hook],
            'no_color': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': ext,
                'preferredquality': '192',
            }]
        }
        yd.setup(url, ydl_opt)
        yd.start()

class DownloadVideo:
    def download_video(self, url, ext, yd):
        makedirs("./videos", exist_ok=True)

        ydl_opt = {
            'format': 'bestvideo[height<=1080]+bestaudio[ext=m4a]/best[height<=1080]/best',
            'outtmpl': './videos/%(title)s.%(ext)s',
            'ffmpeg_location': './ffmpeg_bin/',
            'keepvideo': False,
            'no_color': True,
            'progress_hooks': [yd.progress_hook],
            'postprocessor_hooks': [yd.postprocessor_hook],
            'merge_output_format': ext
        }

        yd.setup(url, ydl_opt)
        yd.start()

class YoutubeDownloader(QThread):
    progress_signal = Signal(int)
    progress_str_signal = Signal(str)
    total_signal = Signal(str, str)
    speed_signal = Signal(str)
    progress_status_signal = Signal(str)
    postprocessor_status_signal = Signal(str)
    left_download_button_signal = Signal(bool)
    right_download_button_signal = Signal(bool)

    error_signal = Signal(str)

    url = ""
    ydl_opt = {}

    def __init__(self):
        super().__init__()

    def setup(self, url, ydl_opt):
        self.url = url
        self.ydl_opt = ydl_opt

    def run(self):
        ydl = YoutubeDL(self.ydl_opt)
        try:
            ydl.download([self.url])
        except Exception as e:
            self.error_signal.emit(str(e))

    def progress_hook(self, d):
        self.progress_signal.emit(int(d['_percent']))
        self.progress_str_signal.emit(d['_percent_str'])
        self.total_signal.emit(d.get('_downloaded_bytes_str', "0"), d['_total_bytes_str'])
        self.speed_signal.emit(d['_speed_str'])

        if d['status'] == 'downloading':
            self.progress_status_signal.emit("Download status: Downloading...")
        if d['status'] == 'finished':
            self.progress_status_signal.emit("Download status: Finished!")
        if d['status'] == 'error':
            self.progress_status_signal.emit("Download status: Error!!!")
            self.right_download_button_signal.emit(True)
            self.left_download_button_signal.emit(True)

    def postprocessor_hook(self, d):
        if d['status'] == 'started':
            self.postprocessor_status_signal.emit("Post Processing status: Started...")
        if d['status'] == 'finished':
            self.postprocessor_status_signal.emit("Post Processing status: Finished!")
            self.left_download_button_signal.emit(True)
            self.right_download_button_signal.emit(True)
