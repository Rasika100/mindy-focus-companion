# Mindy — Your Focus Companion 🤖

## Overview

Mindy is a desktop application designed to help me stay focused while studying and working on projects.

It uses webcam-based visual analysis to estimate changes in posture, head direction, and mouth movement. When a combination of predefined behaviors persists for a specified duration, Mindy responds by playing a personalized local video reminder.

The application is designed to process webcam data locally, with the goal of keeping camera footage on my device.

## Project Goals

- Build a desktop application using Python.
- Learn practical computer vision through OpenCV and MediaPipe.
- Implement personalized calibration and behavior-detection rules.
- Create a responsive interface with PySide6.
- Maintain clear technical documentation and testing records.
- Publish the project and its development history on GitHub.

**Status:** In development 🚧

## Current Progress

### Webcam Access Test
- Installed OpenCV and NumPy in the project's virtual environment.
- Verified that Python can capture a webcam frame.
- Displayed a live webcam preview using OpenCV.
- Added keyboard control to exit the preview by pressing `Q`.

**Status:** Webcam access and live preview have been tested using a temporary `camera_test.py` script. Webcam monitoring is not yet integrated into Mindy's main application.

### Run the Webcam Test

With the project's virtual environment activated, run:

```powershell
python camera_test.py
```

Press `Q` while the preview window is active to exit.
