from os import makedirs
from typing import Tuple

import yt_dlp
from PySide6.QtCore import QThread, Signal
from yt_dlp import YoutubeDL

import app


class DownloadAudio:
    def download_audio(self, url: str, timecode: Tuple[str, str], checkboxState: bool, ext: str, yd):
        makedirs("./audios", exist_ok=True)


        ydl_opt = {
            'js_runtimes': {'deno': {'path': ".\\deno_bin\\deno.exe"}},
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
        if checkboxState:
            ydl_opt['download_ranges'] = yt_dlp.utils.download_range_func(
                None,
                [(yd.time_to_seconds(timecode[0]), yd.time_to_seconds(timecode[1]))]
            )
            ydl_opt['force_keyframes_at_cuts'] = True

        yd.setup(url, ydl_opt)
        yd.start()

class DownloadVideo:
    def download_video(self, url: str, timecode: Tuple[str, str], checkboxState: bool, ext: str, yd):
        makedirs("./videos", exist_ok=True)
        ydl_opt = {
            'js_runtimes': {'deno': {'path': ".\\deno_bin\\deno.exe"}},
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
            'outtmpl': './videos/%(title)s.%(ext)s',
            'ffmpeg_location': './ffmpeg_bin/',
            'keepvideo': False,
            'no_color': True,
            'progress_hooks': [yd.progress_hook],
            'postprocessor_hooks': [yd.postprocessor_hook],
            'merge_output_format': ext,
            'socket_timeout': 30,
            'retries': 10,
        }
        if checkboxState:
            ydl_opt['download_ranges'] = yt_dlp.utils.download_range_func(
                None,
                [(yd.time_to_seconds(timecode[0]), yd.time_to_seconds(timecode[1]))]
            )
            ydl_opt['force_keyframes_at_cuts'] = True

        print(f"timecode: {timecode}")
        print(f"seconds: {yd.time_to_seconds(timecode[0])} - {yd.time_to_seconds(timecode[1])}")
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
    is_downloading_signal = Signal()

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
            print("ydl.download() завершён успешно")  # ← добавь
        except Exception as e:
            print(f"Ошибка в run(): {e}")  # ← и это
            self.error_signal.emit(str(e))
        print("run() завершён")  # ← и финальная метка
        self.is_downloading_signal.emit()

    def progress_hook(self, d):
        percent = d.get('_percent')
        if percent is None:
            return

        self.progress_signal.emit(int(percent))
        self.progress_str_signal.emit(d.get('_percent_str', '0%'))
        self.total_signal.emit(
            d.get('_downloaded_bytes_str', '0'),
            d.get('_total_bytes_str', '0')
        )
        self.speed_signal.emit(d.get('_speed_str', '...'))

        status = d.get('status', '')
        if status == 'downloading':
            self.progress_status_signal.emit("Download status: Downloading...")
        elif status == 'finished':
            self.progress_status_signal.emit("Download status: Finished!")
        elif status == 'error':
            self.progress_status_signal.emit("Download status: Error!!!")
            self.right_download_button_signal.emit(True)
            self.left_download_button_signal.emit(True)

    def postprocessor_hook(self, d):
        def postprocessor_hook(self, d):
            status = d.get('status', '')
            postprocessor = d.get('postprocessor', '')

            if status == 'started':
                if postprocessor == 'FFmpegVideoConvertor':
                    self.postprocessor_status_signal.emit("Post Processing: Converting video (may take a while)...")
                else:
                    self.postprocessor_status_signal.emit(f"Post Processing: {postprocessor}...")
            elif status == 'finished':
                self.postprocessor_status_signal.emit("Post Processing: Finished!")
                self.left_download_button_signal.emit(True)
                self.right_download_button_signal.emit(True)
                self.is_downloading_signal.emit()

    def time_to_seconds(self, t: str) -> float:
        """'HH:MM:SS' → секунды"""
        parts = list(map(int, t.split(':')))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        return parts[0] * 60 + parts[1]
