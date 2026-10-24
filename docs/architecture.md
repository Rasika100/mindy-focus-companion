# Mindy — System Architecture

## 1. Overview

Mindy is designed as a local-first Windows desktop application. It captures webcam frames, estimates visual landmarks, evaluates predefined behavior rules, and triggers a personalized video when the specified conditions persist.

## 2. System Flow

```text
User
  |
  v
PySide6 Desktop Interface
  |
  v
Monitoring Worker
  |
  v
OpenCV — Webcam Frames
  |
  v
NumPy — Image Arrays
  |
  v
MediaPipe — Landmark Estimation
  |
  v
Python Behavior Analysis
  |
  v
Decision Rules and Timer
  |
  v
Local Video Player
```

## 3. Component Responsibilities

| Component | Responsibility |
|---|---|
| PySide6 | Desktop window, controls, settings, and video-player interface |
| Monitoring worker | Runs camera analysis without blocking the interface |
| OpenCV | Captures webcam frames |
| NumPy | Represents image data and supports numerical calculations |
| MediaPipe | Estimates face and body landmarks |
| Calibration module | Establishes a baseline of normal visible posture and movement |
| Behavior analyzer | Evaluates posture, head direction, and mouth movement |
| Decision and timer logic | Checks behavior combinations and their duration |
| Local video player | Plays a user-selected video stored on the device |

## 4. Detection Strategy

Mindy will not trigger a reminder based on a single signal such as leaning back or turning the head.

The initial strategy is to evaluate a combination of visible signals, compare measurements against the calibrated baseline, and track how long the relevant conditions persist.

The target trigger duration is approximately 60 seconds. The exact thresholds and reset behavior will be refined through testing.

These signals are estimates of visible behavior, not proof of a person's attention or mental state.

## 5. Calibration

Calibration will collect measurements while the user sits in their normal working position.

The measurements will establish a personal baseline, stored locally. Monitoring will compare subsequent measurements against this baseline.

Calibration will not train a new machine-learning model or independently determine what distraction means.

## 6. Privacy and Performance

- Webcam processing is intended to remain on the local device.
- Monitoring starts only when the user explicitly enables it.
- No cloud-based vision service is required by the planned design.
- The application will be tested for CPU usage and interface responsiveness.
- Camera resources should be released when monitoring stops or the application closes.

## 7. Development Status

This document describes the planned architecture. Components and behaviors will be marked as implemented only after they have been built and tested.

The architecture may change as development reveals better implementation choices.