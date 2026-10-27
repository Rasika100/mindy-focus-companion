
import cv2
from PySide6.QtCore import QThread, Signal


class CameraWorker(QThread):
    frame_captured = Signal(object)
    camera_error = Signal(str)

    def __init__(self):
        super().__init__()

        self.camera = None
        self.running = False

    def run(self):
        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            self.camera.release()
            self.camera = None
            self.camera_error.emit("Could not open the webcam.")
            return

        self.running = True

        try:
            while self.running:
                success, frame = self.camera.read()

                if not success:
                    self.camera_error.emit(
                        "Could not capture a camera frame."
                    )
                    break

                self.frame_captured.emit(frame)

        finally:
            self.camera.release()
            self.camera = None
            self.running = False

    def stop(self):
        self.running = False
