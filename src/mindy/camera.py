import cv2
import time
from PySide6.QtCore import QThread, Signal


class CameraWorker(QThread):
    frame_captured = Signal(object)
    camera_error = Signal(str)

    def __init__(self, target_fps=5):
        super().__init__()

        self.camera = None
        self.running = False
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps

    def run(self):
        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            self.camera.release()
            self.camera = None
            self.camera_error.emit("Could not open the webcam.")
            return

        self.running = True
        last_emit_time = 0.0

        try:
            while self.running:
                success, frame = self.camera.read()

                if not success:
                    self.camera_error.emit(
                        "Could not capture a camera frame."
                    )
                    break

                current_time = time.monotonic()

                if current_time - last_emit_time >= self.frame_interval:
                    self.frame_captured.emit(frame)
                    last_emit_time = current_time

        finally:
            self.camera.release()
            self.camera = None
            self.running = False

    def stop(self):
        self.running = False