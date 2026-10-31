
from pathlib import Path

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QStackedWidget,
)


class AlertPopup(QWidget):

    dismissed = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mindy Alert")
        self.setFixedSize(460, 340)

        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self._programmatic_close = False

        # Video player: plays MP4 with its embedded audio.
        self.video_player = QMediaPlayer(self)
        self.video_audio = QAudioOutput(self)
        self.video_player.setAudioOutput(self.video_audio)
        self.video_audio.setVolume(0.8)

        # Audio player: plays the separate second-person alert audio.
        self.alert_audio_player = QMediaPlayer(self)
        self.alert_audio = QAudioOutput(self)
        self.alert_audio_player.setAudioOutput(self.alert_audio)
        self.alert_audio.setVolume(0.8)

        # Video view.
        self.video_widget = QVideoWidget()
        self.video_player.setVideoOutput(self.video_widget)

        # Image view.
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.image_label.setScaledContents(False)

        # Message view for missing or invalid assets.
        self.message_label = QLabel()
        self.message_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.message_label.setWordWrap(True)

        # One shared content area.
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.video_widget)
        self.content_stack.addWidget(self.image_label)
        self.content_stack.addWidget(self.message_label)

        self.title_label = QLabel("Mindy Alert")
        self.title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.close_button = QPushButton("Close Alert")
        self.close_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.content_stack, 1)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    # --------------------------------
    # STOP ALL MEDIA
    # --------------------------------

    def stop_media(self):

        self.video_player.stop()
        self.alert_audio_player.stop()

    # --------------------------------
    # PHONE-USE ALERT
    # --------------------------------

    def show_phone_alert(self, video_path):

        self.stop_media()

        video_path = Path(video_path)

        self.title_label.setText(
            "Mindy noticed possible phone use"
        )

        if not video_path.is_file():

            self.show_message(
                f"Phone alert video not found:\n{video_path}"
            )
            return

        self.content_stack.setCurrentWidget(
            self.video_widget
        )

        self.video_player.setSource(
            QUrl.fromLocalFile(str(video_path.resolve()))
        )

        self.show()
        self.raise_()
        self.activateWindow()

        self.video_player.play()

    # --------------------------------
    # SECOND-PERSON ALERT
    # --------------------------------

    def show_person_alert(self, image_path, audio_path):

        self.stop_media()

        image_path = Path(image_path)
        audio_path = Path(audio_path)

        self.title_label.setText(
            "Another person detected!"
        )

        if not image_path.is_file():

            self.show_message(
                f"Person alert image not found:\n{image_path}"
            )
            return

        pixmap = QPixmap(str(image_path))

        if pixmap.isNull():

            self.show_message(
                "Could not load the person alert image."
            )
            return

        scaled_pixmap = pixmap.scaled(
            420,
            250,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.image_label.setPixmap(scaled_pixmap)

        self.content_stack.setCurrentWidget(
            self.image_label
        )

        self.show()
        self.raise_()
        self.activateWindow()

        if audio_path.is_file():

            self.alert_audio_player.setSource(
                QUrl.fromLocalFile(str(audio_path.resolve()))
            )

            self.alert_audio_player.play()

        else:

            print(
                f"Person alert audio not found: {audio_path}"
            )

    # --------------------------------
    # SHOW ERROR / MISSING FILE MESSAGE
    # --------------------------------

    def show_message(self, message):

        self.message_label.setText(message)

        self.content_stack.setCurrentWidget(
            self.message_label
        )

        self.show()
        self.raise_()
        self.activateWindow()

    # --------------------------------
    # HIDE WITHOUT USER DISMISSAL
    # --------------------------------

    def hide_alert(self):

        self._programmatic_close = True

        self.stop_media()
        self.close()

        self._programmatic_close = False

    # --------------------------------
    # WINDOW CLOSE HANDLING
    # --------------------------------

    def closeEvent(self, event):

        self.stop_media()

        if not self._programmatic_close:
            self.dismissed.emit()

        event.accept()
