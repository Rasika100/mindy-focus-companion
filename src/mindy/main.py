
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
from mindy.face_detector import FaceDetector
from mindy.detector import PoseDetector
from mindy.posture_classifier import PostureClassifier
from mindy.alert_manager import AlertManager


class MindyPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mindy")
        self.setFixedSize(280, 220)

        self.camera_worker = None

        # Initialize detectors, classifier and alert manager
        self.face_detector = FaceDetector()
        self.pose_detector = PoseDetector()
        self.posture_classifier = PostureClassifier()
        self.alert_manager = AlertManager()

        # Current detection states
        self.speaking_detected = False
        self.latest_head_position = None
        self.latest_gaze = "unknown"
        self.posture_state = "insufficient_data"

        # Multiple face detection states
        self.face_count = 0
        self.another_person_detected = False

        # UI components
        self.status_label = QLabel("Monitoring is off")
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

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

        # Button connections
        self.start_button.clicked.connect(
            self.start_monitoring
        )

        self.stop_button.clicked.connect(
            self.stop_monitoring
        )

        self.close_button.clicked.connect(self.hide)

    # --------------------------------
    # START MONITORING
    # --------------------------------

    def start_monitoring(self):

        if self.camera_worker is not None:
            if self.camera_worker.isRunning():
                return

        self.camera_worker = CameraWorker(target_fps=5)

        self.camera_worker.camera_error.connect(
            self.handle_camera_error
        )

        self.camera_worker.frame_captured.connect(
            self.handle_frame
        )

        self.status_label.setText("Starting camera...")

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.camera_worker.start()

    # --------------------------------
    # STOP MONITORING
    # --------------------------------

    def stop_monitoring(self):

        if self.camera_worker is not None:

            self.status_label.setText("Stopping camera...")

            try:
                self.camera_worker.frame_captured.disconnect(
                    self.handle_frame
                )
            except (RuntimeError, TypeError):
                pass

            self.camera_worker.stop()
            self.camera_worker.wait()

            self.camera_worker = None

        # Reset detection states
        self.speaking_detected = False
        self.latest_head_position = None
        self.latest_gaze = "unknown"
        self.posture_state = "insufficient_data"

        self.face_count = 0
        self.another_person_detected = False

        self.face_detector.reset_mouth_history()

        # Stop and hide any active alert
        self.alert_manager.update(
            another_person=False,
            phone_use=False,
        )

        self.status_label.setText("Monitoring is off")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    # --------------------------------
    # PROCESS CAMERA FRAME
    # --------------------------------

    def handle_frame(self, frame):

        # Both detectors process the SAME sampled frame
        face_result = self.face_detector.detect(frame)
        pose_result = self.pose_detector.detect(frame)

        # --------------------------------
        # 1. MULTIPLE FACE DETECTION
        # --------------------------------

        self.face_count = self.face_detector.count_faces(
            face_result
        )

        self.another_person_detected = (
            self.face_detector.is_another_person_present(
                face_result
            )
        )

        vertical_ratio = None
        nose_to_ear_dy_normalized = None
        nose_to_shoulder_dx_normalized = None

        # --------------------------------
        # 2. POSE DETECTION
        # --------------------------------

        if pose_result.pose_landmarks:

            landmarks = pose_result.pose_landmarks[0]

            nose = landmarks[0]
            left_ear = landmarks[7]
            right_ear = landmarks[8]
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]

            shoulder_y = (
                left_shoulder.y + right_shoulder.y
            ) / 2

            self.latest_head_position = (
                nose.y - shoulder_y
            )

            # Ear measurements
            ear_midpoint_y = (
                left_ear.y + right_ear.y
            ) / 2

            ear_width = abs(
                left_ear.x - right_ear.x
            )

            if ear_width != 0:

                nose_to_ear_dy_normalized = (
                    nose.y - ear_midpoint_y
                ) / ear_width

            # Shoulder measurements
            shoulder_midpoint_x = (
                left_shoulder.x + right_shoulder.x
            ) / 2

            shoulder_width = abs(
                left_shoulder.x - right_shoulder.x
            )

            if shoulder_width != 0:

                nose_to_shoulder_dx_normalized = (
                    nose.x - shoulder_midpoint_x
                ) / shoulder_width

        else:

            self.latest_head_position = None

        # --------------------------------
        # 3. FACE AND SPEAKING DETECTION
        # --------------------------------

        if face_result.face_landmarks:

            face = face_result.face_landmarks[0]

            # Gaze measurements
            iris_ratio = (
                self.face_detector.calculate_iris_ratio(face)
            )

            self.latest_gaze = (
                self.face_detector.classify_gaze(iris_ratio)
            )

            vertical_ratio = (
                self.face_detector.calculate_vertical_iris_ratio(
                    face
                )
            )

            # Mouth measurements
            mouth_ratio = (
                self.face_detector.calculate_mouth_ratio(face)
            )

            self.face_detector.update_mouth_history(
                mouth_ratio
            )

            # Speaking detection
            self.speaking_detected = (
                self.face_detector.is_speaking()
            )

        else:

            self.face_detector.reset_mouth_history()

            self.speaking_detected = False
            self.latest_gaze = "unknown"

        # --------------------------------
        # 4. POSTURE CLASSIFICATION
        # --------------------------------

        if (
            face_result.face_landmarks
            and pose_result.pose_landmarks
        ):

            self.posture_state = (
                self.posture_classifier.classify(
                    vertical_iris_ratio=vertical_ratio,
                    nose_to_ear_dy_normalized=(
                        nose_to_ear_dy_normalized
                    ),
                    nose_to_shoulder_dx_normalized=(
                        nose_to_shoulder_dx_normalized
                    ),
                )
            )

        else:

            self.posture_state = "insufficient_data"

        # --------------------------------
        # 5. COMBINED STATUS
        # --------------------------------

        if self.another_person_detected:

            self.status_label.setText(
                "Another person detected!\n"
                "2 faces visible"
            )

        elif self.speaking_detected:

            self.status_label.setText(
                "Speaking detected\n"
                "Posture alarm suppression: ON"
            )

        elif self.posture_state == "possible_phone_use":

            self.status_label.setText(
                "Possible phone use detected"
            )

        elif self.posture_state == "normal_or_uncertain":

            self.status_label.setText(
                f"Faces: {self.face_count}\n"
                f"Gaze: {self.latest_gaze}\n"
                "No phone-like posture"
            )

        else:

            self.status_label.setText(
                "Need face and body visibility"
            )

        # --------------------------------
        # 6. ALERT MANAGEMENT
        # --------------------------------

        phone_use_detected = (
            self.posture_state == "possible_phone_use"
            and not self.speaking_detected
        )

        self.alert_manager.update(
            another_person=self.another_person_detected,
            phone_use=phone_use_detected,
        )

    # --------------------------------
    # CAMERA ERROR
    # --------------------------------

    def handle_camera_error(self, message):

        self.status_label.setText(message)

        # Hide active alerts if camera monitoring fails.
        self.alert_manager.update(
            another_person=False,
            phone_use=False,
        )

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        self.camera_worker = None

    # --------------------------------
    # APPLICATION SHUTDOWN
    # --------------------------------

    def shutdown(self):

        self.stop_monitoring()

        self.alert_manager.close()

        self.face_detector.close()
        self.pose_detector.close()

        print("Mindy resources released.")


# ====================================
# MINDY ROBOT
# ====================================

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

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setPen(
            QPen(QColor("#4A91E8"), 3)
        )

        painter.drawLine(50, 15, 50, 25)

        painter.setBrush(QColor("#40A0FF"))

        painter.drawEllipse(
            QRectF(44, 7, 12, 12)
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QColor("#61A8F5"))

        painter.drawRoundedRect(
            QRectF(12, 39, 18, 29), 8, 8
        )

        painter.drawRoundedRect(
            QRectF(70, 39, 18, 29), 8, 8
        )

        painter.setPen(
            QPen(QColor("#A8C8F4"), 2)
        )

        painter.setBrush(
            QBrush(QColor("#F7FBFF"))
        )

        painter.drawRoundedRect(
            QRectF(22, 22, 56, 57), 24, 24
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QColor("#142B50"))

        painter.drawRoundedRect(
            QRectF(27, 37, 46, 29), 13, 13
        )

        painter.setPen(
            QPen(QColor("#FFFFFF"), 2.5)
        )

        painter.drawArc(
            QRectF(37, 44, 9, 9),
            15 * 16,
            150 * 16
        )

        painter.drawArc(
            QRectF(54, 44, 9, 9),
            15 * 16,
            150 * 16
        )

        painter.setPen(
            QPen(QColor("#A8C8F4"), 1.5)
        )

        painter.setBrush(
            QBrush(QColor("#F7FBFF"))
        )

        painter.drawRoundedRect(
            QRectF(34, 76, 32, 17), 9, 9
        )

        painter.end()

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.panel.show()
            self.panel.raise_()
            self.panel.activateWindow()


# ====================================
# APPLICATION ENTRY POINT
# ====================================

app = QApplication(sys.argv)

app.setQuitOnLastWindowClosed(False)

panel = MindyPanel()
robot = MindyRobot(panel)

app.aboutToQuit.connect(panel.shutdown)

screen = app.primaryScreen().availableGeometry()

robot.move(
    screen.right() - robot.width() - 25,
    screen.bottom() - robot.height() - 65,
)

robot.show()

sys.exit(app.exec())
