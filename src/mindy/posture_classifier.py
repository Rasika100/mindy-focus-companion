class PostureClassifier:

    EYE_POSITION_MAX = 0.41
    NOSE_EAR_VERTICAL_MIN = 0.06
    NOSE_SHOULDER_HORIZONTAL_MAX = 0.08

    def classify(
        self,
        vertical_iris_ratio,
        nose_to_ear_dy_normalized,
        nose_to_shoulder_dx_normalized,
    ):

        # Check whether all measurements are available
        if (
            vertical_iris_ratio is None
            or nose_to_ear_dy_normalized is None
            or nose_to_shoulder_dx_normalized is None
        ):
            return "insufficient_data"

        eye_condition = (
            vertical_iris_ratio < self.EYE_POSITION_MAX
        )

        head_condition = (
            nose_to_ear_dy_normalized
            > self.NOSE_EAR_VERTICAL_MIN
        )

        horizontal_condition = (
            abs(nose_to_shoulder_dx_normalized)
            < self.NOSE_SHOULDER_HORIZONTAL_MAX
        )

        if (
            eye_condition
            and head_condition
            and horizontal_condition
        ):
            return "possible_phone_use"

        return "normal_or_uncertain"