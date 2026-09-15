import io
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

from PIL import Image, ImageOps, ImageDraw

# Optional heavy deps: mediapipe and cv2. We import lazily and handle absence gracefully.
try:
    import mediapipe as mp  # type: ignore
except Exception:  # pragma: no cover - optional runtime import
    mp = None  # type: ignore

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore
    np = None  # type: ignore


@dataclass
class AnalysisResult:
    face_shape: Optional[str]
    hair_type: Optional[str]
    hair_length: Optional[str]
    features: dict
    landmarks: Optional[List[Tuple[float, float]]]


FACE_SHAPES = ["oval", "round", "square", "heart", "diamond"]
HAIR_TYPES = ["straight", "wavy", "curly", "coily"]
HAIR_LENGTHS = ["short", "medium", "long"]


def pil_to_cv2(img: Image.Image):
    if np is None:
        return None
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)


def detect_landmarks(img: Image.Image) -> Optional[List[Tuple[float, float]]]:
    """Return 2D facial landmarks normalized to image size using MediaPipe if available."""
    if mp is None:
        return None
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
        cv = pil_to_cv2(img)
        if cv is None:
            return None
        results = face_mesh.process(cv2.cvtColor(cv, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return None
        h, w = cv.shape[:2]
        pts = []
        for lm in results.multi_face_landmarks[0].landmark:
            pts.append((lm.x * w, lm.y * h))
        return pts


def ratio(a: float, b: float) -> float:
    return a / b if b else 0.0


def face_shape_from_landmarks(pts: List[Tuple[float, float]], img_size: Tuple[int, int]) -> Optional[str]:
    """
    Heuristic face-shape classification using distances between key regions.
    Uses MediaPipe landmark indices. This is not perfect but provides a good baseline.
    """
    if not pts:
        return None
    # Landmark indices (approx):
    # jawline left/right: 234, 454; chin: 152; forehead (mid): 10; cheekbones left/right: 93, 323
    try:
        left_jaw = pts[234]
        right_jaw = pts[454]
        chin = pts[152]
        forehead = pts[10]
        left_cheek = pts[93]
        right_cheek = pts[323]
    except Exception:
        return None

    def dist(p, q):
        return math.hypot(p[0]-q[0], p[1]-q[1])

    face_width_jaw = dist(left_jaw, right_jaw)
    face_width_cheek = dist(left_cheek, right_cheek)
    face_length = dist(chin, forehead)

    width_ratio = ratio(face_width_cheek, face_length)  # cheekbone width vs length
    jaw_cheek_ratio = ratio(face_width_jaw, face_width_cheek)

    # Simple rule-based classification
    # Tuned thresholds from common guides
    if abs(jaw_cheek_ratio - 1.0) < 0.05 and abs(width_ratio - 0.8) < 0.1:
        return "oval"
    if width_ratio > 0.95:
        return "round"
    if jaw_cheek_ratio > 1.05 and width_ratio < 0.85:
        return "square"
    # Heart: narrow jaw vs wide forehead/cheek
    if jaw_cheek_ratio < 0.95 and width_ratio < 0.85:
        return "heart"
    return "diamond"


def analyze_hair(img: Image.Image, landmarks: Optional[List[Tuple[float, float]]]) -> Tuple[Optional[str], Optional[str]]:
    """Estimate hair type and length with lightweight heuristics using edge density and area."""
    if cv2 is None or np is None:
        return None, None
    cv = pil_to_cv2(img)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = edges.mean() / 255.0

    # Hair type from edge frequency: curly has more edges
    if edge_density < 0.06:
        hair_type = "straight"
    elif edge_density < 0.10:
        hair_type = "wavy"
    elif edge_density < 0.16:
        hair_type = "curly"
    else:
        hair_type = "coily"

    # Hair length: estimate hair pixel area above head top relative to face length
    hair_length = None
    if landmarks:
        # forehead and chin
        forehead_y = landmarks[10][1]
        chin_y = landmarks[152][1]
        face_len = abs(chin_y - forehead_y) or 1.0
        # count dark pixels above forehead indicating hair mass
        h, w = cv.shape[:2]
        y_top = max(int(forehead_y - face_len * 0.6), 0)
        roi = gray[y_top:int(forehead_y), :]
        if roi.size:
            darkness = (roi < 110).mean()  # crude mass indicator
            if darkness < 0.15:
                hair_length = "short"
            elif darkness < 0.30:
                hair_length = "medium"
            else:
                hair_length = "long"
    return hair_type, hair_length


def analyze_image(front_img: Image.Image, side_img: Optional[Image.Image] = None) -> AnalysisResult:
    landmarks = detect_landmarks(front_img)
    face_shape = face_shape_from_landmarks(landmarks, front_img.size) if landmarks else None
    hair_type, hair_length = analyze_hair(front_img, landmarks)

    features = {
        "confidence": 0.8 if landmarks else 0.5,
        "used_side_profile": bool(side_img),
    }
    return AnalysisResult(
        face_shape=face_shape,
        hair_type=hair_type,
        hair_length=hair_length,
        features=features,
        landmarks=landmarks,
    )


def composite_overlay(front_img: Image.Image, overlay_png: Image.Image, landmarks: Optional[List[Tuple[float, float]]]) -> Image.Image:
    """Rudimentary overlay: scale and position the overlay around the forehead and ears."""
    base = front_img.convert("RGBA")
    ov = overlay_png.convert("RGBA")
    if not landmarks:
        # center top if we don't have landmarks
        w = int(base.width * 0.7)
        scale = w / ov.width
        ov = ov.resize((w, int(ov.height * scale)), Image.LANCZOS)
        x = (base.width - ov.width)//2
        y = int(base.height * 0.05)
        base.alpha_composite(ov, dest=(x, y))
        return base

    left_ear = landmarks[234]
    right_ear = landmarks[454]
    forehead = landmarks[10]
    target_w = int(abs(right_ear[0] - left_ear[0]) * 1.2)
    scale = max(1, target_w) / ov.width
    ov = ov.resize((int(ov.width * scale), int(ov.height * scale)), Image.LANCZOS)
    x = int(forehead[0] - ov.width/2)
    y = int(forehead[1] - ov.height*0.35)
    base.alpha_composite(ov, dest=(x, y))
    return base
