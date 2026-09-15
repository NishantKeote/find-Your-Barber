from dataclasses import dataclass
from typing import List, Optional

from django.db.models import Q

from ..models import HaircutStyle


@dataclass
class Recommendation:
    style_id: int
    name: str
    overlay_available: bool
    preview_url: Optional[str]
    match_score: float


FACE_SHAPE_TO_TAGS = {
    "oval": ["quiff", "pompadour", "bob", "layers"],
    "round": ["undercut", "fade", "long layers", "pixie"],
    "square": ["textured", "crop", "waves", "side-part"],
    "heart": ["fringe", "bangs", "chin-length", "lob"],
    "diamond": ["messy", "taper", "layered", "curtain"],
}


def score_style(style: HaircutStyle, face_shape: Optional[str], hair_type: Optional[str], hair_length: Optional[str]) -> float:
    score = 0.5
    if face_shape:
        if style.suitable_face_shapes.filter(name=face_shape).exists():
            score += 0.3
        tags = [t.strip().lower() for t in (style.tags or "").split(",")]
        for tag in FACE_SHAPE_TO_TAGS.get(face_shape, []):
            if tag in tags:
                score += 0.1
                break
    if hair_length and getattr(style, "length_category", None) == hair_length:
        score += 0.1
    return min(1.0, score)


def recommend(face_shape: Optional[str], hair_type: Optional[str], hair_length: Optional[str], gender: Optional[str] = None, limit: int = 8) -> List[HaircutStyle]:
    qs = HaircutStyle.objects.filter(is_active=True)
    if gender:
        qs = qs.filter(Q(gender=gender) | Q(gender="unisex"))
    if hair_length:
        qs = qs.filter(length_category__in=[hair_length, "any"]) if hasattr(HaircutStyle, 'length_category') else qs
    return list(qs.order_by('name')[:limit])
