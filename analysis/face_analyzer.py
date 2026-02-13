"""Face analysis using MediaPipe FaceLandmarker with blendshapes."""

import json
import os
import sys
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    FaceLandmarker,
    FaceLandmarkerOptions,
    RunningMode,
)

PHOTOS_PATH = r"D:\cameraCap"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "face_landmarker.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"

# Expression map: label -> {blendshape_name: weight}
# Scores are computed as weighted dot products against blendshape values.
EXPRESSION_MAP = {
    "happy": {
        "mouthSmileLeft": 1.0,
        "mouthSmileRight": 1.0,
        "cheekSquintLeft": 0.5,
        "cheekSquintRight": 0.5,
    },
    "sad": {
        "mouthFrownLeft": 1.0,
        "mouthFrownRight": 1.0,
        "browDownLeft": 0.5,
        "browDownRight": 0.5,
    },
    "surprised": {
        "browInnerUp": 1.0,
        "browOuterUpLeft": 0.7,
        "browOuterUpRight": 0.7,
        "jawOpen": 0.8,
        "eyeWideLeft": 0.5,
        "eyeWideRight": 0.5,
    },
    "angry": {
        "browDownLeft": 1.0,
        "browDownRight": 1.0,
        "mouthFrownLeft": 0.5,
        "mouthFrownRight": 0.5,
        "noseSneerLeft": 0.7,
        "noseSneerRight": 0.7,
    },
    "neutral": {
        "_neutral": 1.0,
    },
}


@dataclass
class Presence:
    detected: bool
    confidence: float
    face_size_ratio: float


@dataclass
class Expression:
    dominant: str
    scores: dict[str, float]


@dataclass
class Focus:
    is_focused: bool
    eyes_open: float
    gaze_forward: float
    mouth_relaxed: float


@dataclass
class FaceAnalysis:
    timestamp: str
    date: str
    presence: Presence
    expression: Expression | None = None
    focus: Focus | None = None


def classify_expression(blendshapes: list) -> Expression:
    """Score each expression label via weighted dot product against blendshapes."""
    bs = {b.category_name: b.score for b in blendshapes}
    scores = {}
    for label, weights in EXPRESSION_MAP.items():
        scores[label] = sum(bs.get(name, 0.0) * w for name, w in weights.items())
    # Normalize so scores sum to 1
    total = sum(scores.values())
    if total > 0:
        scores = {k: round(v / total, 3) for k, v in scores.items()}
    dominant = max(scores, key=scores.get)
    return Expression(dominant=dominant, scores=scores)


def assess_focus(blendshapes: list) -> Focus:
    """Derive focus signals from blendshape values."""
    bs = {b.category_name: b.score for b in blendshapes}

    # Eye openness: 1.0 = fully open, 0.0 = fully closed
    eye_blink_l = bs.get("eyeBlinkLeft", 0.0)
    eye_blink_r = bs.get("eyeBlinkRight", 0.0)
    eyes_open = 1.0 - (eye_blink_l + eye_blink_r) / 2.0

    # Gaze forward: low look-values = looking straight ahead
    look_sum = (
        bs.get("eyeLookUpLeft", 0.0)
        + bs.get("eyeLookUpRight", 0.0)
        + bs.get("eyeLookDownLeft", 0.0)
        + bs.get("eyeLookDownRight", 0.0)
        + bs.get("eyeLookInLeft", 0.0)
        + bs.get("eyeLookInRight", 0.0)
        + bs.get("eyeLookOutLeft", 0.0)
        + bs.get("eyeLookOutRight", 0.0)
    )
    gaze_forward = max(0.0, 1.0 - look_sum / 4.0)

    # Mouth relaxed: low mouth-open/movement = relaxed
    mouth_activity = (
        bs.get("jawOpen", 0.0)
        + bs.get("mouthFunnel", 0.0)
        + bs.get("mouthPucker", 0.0)
    )
    mouth_relaxed = max(0.0, 1.0 - mouth_activity)

    is_focused = eyes_open > 0.5 and gaze_forward > 0.4

    return Focus(
        is_focused=is_focused,
        eyes_open=round(eyes_open, 3),
        gaze_forward=round(gaze_forward, 3),
        mouth_relaxed=round(mouth_relaxed, 3),
    )


def assess_presence(landmarks: list, image_shape: tuple) -> Presence:
    """Compute face presence from normalized landmarks and image dimensions."""
    h, w = image_shape[:2]
    xs = np.array([lm.x for lm in landmarks])
    ys = np.array([lm.y for lm in landmarks])
    face_w = np.ptp(xs)
    face_h = np.ptp(ys)
    face_size_ratio = face_w * face_h  # fraction of image area
    return Presence(
        detected=True,
        confidence=round(float(face_size_ratio > 0.001), 3),
        face_size_ratio=round(float(face_size_ratio), 4),
    )


def _ensure_model():
    """Download the FaceLandmarker model if not present."""
    if os.path.exists(MODEL_PATH):
        return
    print(f"Downloading face_landmarker.task to {MODEL_PATH}...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Download complete.")


class FaceAnalyzer:
    """Context manager wrapping MediaPipe FaceLandmarker."""

    def __init__(self):
        _ensure_model()
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=RunningMode.IMAGE,
            output_face_blendshapes=True,
            num_faces=1,
        )
        self._landmarker = FaceLandmarker.create_from_options(options)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._landmarker.close()

    def analyze(self, image_path: str, date: str) -> FaceAnalysis:
        """Analyze a single image and return FaceAnalysis."""
        timestamp = os.path.splitext(os.path.basename(image_path))[0]
        img = cv2.imread(image_path)
        if img is None:
            return FaceAnalysis(
                timestamp=timestamp,
                date=date,
                presence=Presence(detected=False, confidence=0.0, face_size_ratio=0.0),
            )

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self._landmarker.detect(mp_image)

        if not result.face_landmarks:
            return FaceAnalysis(
                timestamp=timestamp,
                date=date,
                presence=Presence(detected=False, confidence=0.0, face_size_ratio=0.0),
            )

        landmarks = result.face_landmarks[0]
        presence = assess_presence(landmarks, img.shape)

        expression = None
        focus = None
        if result.face_blendshapes:
            blendshapes = result.face_blendshapes[0]
            expression = classify_expression(blendshapes)
            focus = assess_focus(blendshapes)

        return FaceAnalysis(
            timestamp=timestamp,
            date=date,
            presence=presence,
            expression=expression,
            focus=focus,
        )


def main():
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join(PHOTOS_PATH, date)

    if not os.path.isdir(folder):
        print(f"No folder found: {folder}")
        sys.exit(1)

    images = sorted(f for f in os.listdir(folder) if f.lower().endswith(".jpg"))
    if not images:
        print(f"No .jpg files in {folder}")
        sys.exit(1)

    print(f"Analyzing {len(images)} images from {date}...")
    results = []

    with FaceAnalyzer() as analyzer:
        for i, fname in enumerate(images, 1):
            path = os.path.join(folder, fname)
            analysis = analyzer.analyze(path, date)
            results.append(asdict(analysis))
            if i % 50 == 0 or i == len(images):
                print(f"  {i}/{len(images)}")

    # Write output
    out_path = os.path.join(folder, "analysis.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {out_path}")

    # Print summary
    detected = sum(1 for r in results if r["presence"]["detected"])
    focused = sum(1 for r in results if r["focus"] and r["focus"]["is_focused"])
    expressions = {}
    for r in results:
        if r["expression"]:
            expr = r["expression"]["dominant"]
            expressions[expr] = expressions.get(expr, 0) + 1

    print(f"\nSummary for {date}:")
    print(f"  Images analyzed: {len(results)}")
    print(f"  Face detected:   {detected}/{len(results)}")
    print(f"  Focused:         {focused}/{detected}" if detected else "  Focused:         N/A")
    if expressions:
        print(f"  Expressions:     {expressions}")


if __name__ == "__main__":
    main()
