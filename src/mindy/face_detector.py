
import mediapipe as mp
from pathlib import Path
import cv2
from collections import deque


BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "face_landmarker.task"


class FaceDetector:

    # Speaking detection settings
    MOUTH_CYCLE_AMPLITUDE = 0.025
    SPEAKING_MIN_CYCLES = 3
    MOUTH_HISTORY_SIZE = 20

    def __init__(self):

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=str(MODEL_PATH)
            ),
            running_mode=VisionRunningMode.IMAGE,
            num_faces=2,
        )

        self.landmarker = FaceLandmarker.create_from_options(
            options
        )

        self.mouth_history = deque(
            maxlen=self.MOUTH_HISTORY_SIZE
        )

    # --------------------------------
    # FACE DETECTION
    # --------------------------------

    def detect(self, frame):

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        return self.landmarker.detect(mp_image)

    # --------------------------------
    # COUNT DETECTED FACES
    # --------------------------------

    def count_faces(self, face_result):

        if face_result is None:
            return 0

        return len(face_result.face_landmarks)

    # --------------------------------
    # CHECK FOR ANOTHER PERSON
    # --------------------------------

    def is_another_person_present(self, face_result):

        return self.count_faces(face_result) >= 2

    # --------------------------------
    # HORIZONTAL IRIS POSITION
    # --------------------------------

    def calculate_iris_ratio(self, face):

        eye_left = face[33]
        eye_right = face[133]
        iris = face[468]

        eye_width = eye_right.x - eye_left.x

        if eye_width == 0:
            return None

        return (
            iris.x - eye_left.x
        ) / eye_width

    # --------------------------------
    # VERTICAL IRIS POSITION
    # --------------------------------

    def calculate_vertical_iris_ratio(self, face):

        right_upper = face[159]
        right_lower = face[145]
        right_iris = face[468]

        left_upper = face[386]
        left_lower = face[374]
        left_iris = face[473]

        right_height = (
            right_lower.y - right_upper.y
        )

        left_height = (
            left_lower.y - left_upper.y
        )

        if right_height == 0 or left_height == 0:
            return None

        right_ratio = (
            right_iris.y - right_upper.y
        ) / right_height

        left_ratio = (
            left_iris.y - left_upper.y
        ) / left_height

        return (
            right_ratio + left_ratio
        ) / 2

    # --------------------------------
    # GAZE CLASSIFICATION
    # --------------------------------

    def classify_gaze(self, iris_ratio):

        if iris_ratio is None:
            return "unknown"

        if iris_ratio < 0.44:
            return "left"

        if iris_ratio > 0.52:
            return "right"

        return "center"

    # --------------------------------
    # MOUTH OPENING MEASUREMENT
    # --------------------------------

    def calculate_mouth_ratio(self, face):

        upper_lip = face[13]
        lower_lip = face[14]

        left_corner = face[61]
        right_corner = face[291]

        mouth_opening = abs(
            lower_lip.y - upper_lip.y
        )

        mouth_width = abs(
            right_corner.x - left_corner.x
        )

        if mouth_width == 0:
            return None

        return mouth_opening / mouth_width

    # --------------------------------
    # STORE MOUTH MEASUREMENTS
    # --------------------------------

    def update_mouth_history(self, mouth_ratio):

        if mouth_ratio is not None:
            self.mouth_history.append(mouth_ratio)

    # --------------------------------
    # DETECT MOUTH MOVEMENT
    # --------------------------------

    def detect_mouth_movement(self):

        if len(self.mouth_history) < 2:
            return "not_enough_data"

        previous = self.mouth_history[-2]
        current = self.mouth_history[-1]

        change = current - previous

        if change > self.MOUTH_CYCLE_AMPLITUDE:
            return "opening"

        if change < -self.MOUTH_CYCLE_AMPLITUDE:
            return "closing"

        return "stable"

    # --------------------------------
    # COUNT COMPLETE MOUTH CYCLES
    # --------------------------------

    def count_mouth_cycles(self):

        values = list(self.mouth_history)

        if len(values) < 3:
            return 0

        cycles = 0

        state = "closed"

        closed_level = values[0]
        peak = values[0]

        for value in values[1:]:

            if state == "closed":

                if value < closed_level:
                    closed_level = value

                if (
                    value - closed_level
                    >= self.MOUTH_CYCLE_AMPLITUDE
                ):

                    state = "open"
                    peak = value

            else:

                peak = max(peak, value)

                if (
                    peak - value
                    >= self.MOUTH_CYCLE_AMPLITUDE
                ):

                    cycles += 1

                    state = "closed"
                    closed_level = value
                    peak = value

        return cycles

    # --------------------------------
    # SPEAKING CLASSIFICATION
    # --------------------------------

    def is_speaking(self):

        if len(self.mouth_history) < 3:
            return False

        cycles = self.count_mouth_cycles()

        return cycles >= self.SPEAKING_MIN_CYCLES

    # --------------------------------
    # RESET MOUTH HISTORY
    # --------------------------------

    def reset_mouth_history(self):

        self.mouth_history.clear()

    # --------------------------------
    # RELEASE FACE MODEL
    # --------------------------------

    def close(self):

        self.landmarker.close()
