
import sys

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from mindy.camera import CameraWorker


class MindyPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mindy")
        self.setFixedSize(280, 220)

        self.camera_worker = None

        self.status_label = QLabel("Monitoring is off")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_button = QPushButton("Start Monitoring")
        self.stop_button = QPushButton("Stop Monitoring")
        self.close_button = QPushButton("Close Panel")

        self.stop_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Mindy — Focus Companion"))
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.close_button.clicked.connect(self.hide)

    def start_monitoring(self):
        if self.camera_worker is not None:
            if self.camera_worker.isRunning():
                return

        self.camera_worker = CameraWorker()
        self.camera_worker.camera_error.connect(
            self.handle_camera_error
        )

        self.status_label.setText("Starting camera...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.camera_worker.start()

    def stop_monitoring(self):
        if self.camera_worker is not None:
            self.status_label.setText("Stopping camera...")
            self.camera_worker.stop()
            self.camera_worker.wait()
            self.camera_worker = None

        self.status_label.setText("Monitoring is off")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def handle_camera_error(self, message):
        self.status_label.setText(message)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)


class MindyRobot(QWidget):
    def __init__(self, panel):
        super().__init__()
        self.panel = panel

        self.setWindowTitle("Mindy")
        self.setFixedSize(100, 100)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(QPen(QColor("#4A91E8"), 3))
        painter.drawLine(50, 15, 50, 25)
        painter.setBrush(QColor("#40A0FF"))
        painter.drawEllipse(QRectF(44, 7, 12, 12))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#61A8F5"))
        painter.drawRoundedRect(QRectF(12, 39, 18, 29), 8, 8)
        painter.drawRoundedRect(QRectF(70, 39, 18, 29), 8, 8)

        painter.setPen(QPen(QColor("#A8C8F4"), 2))
        painter.setBrush(QBrush(QColor("#F7FBFF")))
        painter.drawRoundedRect(QRectF(22, 22, 56, 57), 24, 24)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#142B50"))
        painter.drawRoundedRect(QRectF(27, 37, 46, 29), 13, 13)

        painter.setPen(QPen(QColor("#FFFFFF"), 2.5))
        painter.drawArc(QRectF(37, 44, 9, 9), 15 * 16, 150 * 16)
        painter.drawArc(QRectF(54, 44, 9, 9), 15 * 16, 150 * 16)

        painter.setPen(QPen(QColor("#A8C8F4"), 1.5))
        painter.setBrush(QBrush(QColor("#F7FBFF")))
        painter.drawRoundedRect(QRectF(34, 76, 32, 17), 9, 9)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.panel.show()
            self.panel.raise_()
            self.panel.activateWindow()


app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

panel = MindyPanel()
robot = MindyRobot(panel)

screen = app.primaryScreen().availableGeometry()
robot.move(
    screen.right() - robot.width() - 25,
    screen.bottom() - robot.height() - 65,
)

robot.show()

sys.exit(app.exec())
