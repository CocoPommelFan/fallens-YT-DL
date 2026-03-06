import sys

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout, \
    QGroupBox, QRadioButton, QPushButton, QLabel, QProgressBar

import util

class MainWindow(QMainWindow):
    label_percent = None

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Youtube Downloader")

        main_container = QWidget()
        self.vlayout_main = QVBoxLayout()

        # Text line for URL
        self.url_line = QLineEdit()
        self.url_line.setPlaceholderText("Youtube URL")
        self.vlayout_main.addWidget(self.url_line)

        # Horizontal options
        self.hlayout_options = QHBoxLayout()

        # Left options
        self.left_group = QGroupBox("Audio")

        self.audio_download_button = QPushButton("Download")

        self.audio_radio1 = QRadioButton("mp3")
        self.audio_radio2 = QRadioButton("wav")
        self.audio_radio3 = QRadioButton("ogg/vorbis")
        self.audio_radio4 = QRadioButton("opus")
        self.audio_radio1.setChecked(True)

        self.vlayout_left_option = QVBoxLayout()

        self.vlayout_left_option.addWidget(self.audio_download_button)

        self.vlayout_left_option.addWidget(self.audio_radio1)
        self.vlayout_left_option.addWidget(self.audio_radio2)
        self.vlayout_left_option.addWidget(self.audio_radio3)
        self.vlayout_left_option.addWidget(self.audio_radio4)

        self.vlayout_left_option.addStretch(1)

        self.hlayout_options.addWidget(self.left_group)

        self.left_group.setLayout(self.vlayout_left_option)

        # Right options
        self.right_group = QGroupBox("Video")

        self.video_download_button = QPushButton("Download")

        self.video_radio1 = QRadioButton("mp4")
        self.video_radio2 = QRadioButton("mkv")
        self.video_radio1.setChecked(True)

        self.vlayout_right_option = QVBoxLayout()

        self.vlayout_right_option.addWidget(self.video_download_button)

        self.vlayout_right_option.addWidget(self.video_radio1)
        self.vlayout_right_option.addWidget(self.video_radio2)

        self.vlayout_right_option.addStretch(1)

        self.hlayout_options.addWidget(self.right_group)

        self.right_group.setLayout(self.vlayout_right_option)

        # Layouts
        self.vlayout_main.addLayout(self.hlayout_options)

        # Status
        self.label_download_status = QLabel("Download Status: ")
        self.label_postprocessor_status = QLabel("Post Processing Status: ")
        self.vlayout_main.addWidget(self.label_download_status)
        self.vlayout_main.addWidget(self.label_postprocessor_status)

        # Info message
        self.hlayout_info = QHBoxLayout()

        self.label_percent = QLabel()
        self.label_total = QLabel()
        self.label_speed = QLabel()

        self.hlayout_info.addWidget(self.label_percent)
        self.hlayout_info.addWidget(self.label_total)
        self.hlayout_info.addWidget(self.label_speed)

        self.vlayout_main.addLayout(self.hlayout_info)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.vlayout_main.addWidget(self.progress_bar)

        # Event connect
        self.audio_download_button.clicked.connect(self.audio_download_clicked)
        self.video_download_button.clicked.connect(self.video_download_clicked)
        self.dt = util.YoutubeDownloader()
        self.dt.progress_str_signal.connect(self.setlabelpercent)
        self.dt.total_signal.connect(self.setlabeltotal)
        self.dt.speed_signal.connect(self.setspeed)
        self.dt.progress_signal.connect(self.progress_bar.setValue)
        self.dt.progress_status_signal.connect(self.label_download_status.setText)
        self.dt.postprocessor_status_signal.connect(self.label_postprocessor_status.setText)
        self.dt.left_download_button_signal.connect(self.audio_download_button.setEnabled)
        self.dt.right_download_button_signal.connect(self.video_download_button.setEnabled)
        self.dt.error_signal.connect(self.error_handler)

        main_container.setLayout(self.vlayout_main)

        self.setCentralWidget(main_container)

        self.setFixedSize(QSize(450, 400))

    def setlabelpercent(self, value: str):
        self.label_percent.setText(value)

    def setlabeltotal(self, downloaded: str, total: str ):
        self.label_total.setText(f"{downloaded}/{total}")

    def setspeed(self, value: str):
        self.label_speed.setText(f"{value}")

    def audio_download_clicked(self, *args):
        self.progress_bar.setValue(0)
        ext = ""

        if self.audio_radio1.isChecked():
            ext = "mp3"
        elif self.audio_radio2.isChecked():
            ext = "wav"
        elif self.audio_radio3.isChecked():
            ext = "vorbis"
        elif self.audio_radio4.isChecked():
            ext = "opus"
        self.set_false_default_button()

        util.DownloadAudio().download_audio(self.url_line.text(), ext, self.dt)


    def video_download_clicked(self, *args):
        self.progress_bar.setValue(0)
        ext = ""

        if self.video_radio1.isChecked():
            ext = "mp4"
        elif self.video_radio2.isChecked():
            ext = "mkv"

        self.set_false_default_button()

        util.DownloadVideo().download_video(self.url_line.text(), ext, self.dt)

    def error_handler(self, e):
        self.progress_bar.setValue(0)
        self.set_true_default_button()

        self.video_download_button.setEnabled(True)
        self.audio_download_button.setEnabled(True)
        self.label_download_status.setText(f"Download Status: {str(e)}")
        self.label_postprocessor_status.setText(f"Download Status: {str(e)}")

    def set_true_default_button(self):
        self.video_download_button.setEnabled(True)
        self.audio_download_button.setEnabled(True)
        pass

    def set_false_default_button(self):
        self.video_download_button.setEnabled(False)
        self.audio_download_button.setEnabled(False)
        self.label_download_status.setText("Download Status: ")
        self.label_postprocessor_status.setText("Download Status: ")

class YoutubeDownloaderApp:
    def __init__(self):
        self.app = QApplication(sys.argv)

        window = MainWindow()
        window.show()

        self.app.exec()
