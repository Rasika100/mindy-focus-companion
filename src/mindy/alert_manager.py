
from pathlib import Path

from mindy.alert_popup import AlertPopup


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PHONE_VIDEO = (
    PROJECT_ROOT / "assets" / "alarms" / "phone_use.mp4"
)

PERSON_IMAGE = (
    PROJECT_ROOT / "assets" / "alarms" / "another_person.png"
)

PERSON_AUDIO = (
    PROJECT_ROOT / "assets" / "alarms" / "another_person.mp4"
)


class AlertManager:

    def __init__(self):

        self.popup = AlertPopup()

        self.current_alert = None
        self.dismissed_alert = None

        self.popup.dismissed.connect(
            self.handle_dismissal
        )

    # --------------------------------
    # HANDLE USER CLOSING THE POPUP
    # --------------------------------

    def handle_dismissal(self):

        self.dismissed_alert = self.current_alert

        self.current_alert = None

    # --------------------------------
    # UPDATE ALERT PRIORITY
    # --------------------------------

    def update(self, another_person, phone_use):

        # Second-person alert has highest priority.
        if another_person:

            desired_alert = "another_person"

        elif phone_use:

            desired_alert = "phone_use"

        else:

            desired_alert = None

        # No alert condition remains.
        if desired_alert is None:

            self.dismissed_alert = None

            if self.current_alert is not None:

                self.popup.hide_alert()
                self.current_alert = None

            return

        # Don't reopen an alert that the user manually closed
        # while its detection condition is still active.
        if desired_alert == self.dismissed_alert:

            return

        # If a different alert has become active,
        # allow it to replace the previous alert.
        if desired_alert != self.current_alert:

            self.current_alert = desired_alert

            if desired_alert == "another_person":

                self.popup.show_person_alert(
                    PERSON_IMAGE,
                    PERSON_AUDIO,
                )

            elif desired_alert == "phone_use":

                self.popup.show_phone_alert(
                    PHONE_VIDEO
                )

    # --------------------------------
    # SHUTDOWN
    # --------------------------------

    def close(self):

        self.current_alert = None
        self.popup.hide_alert()
        self.popup.deleteLater()
