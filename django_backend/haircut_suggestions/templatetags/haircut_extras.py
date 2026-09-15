from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.text import slugify

register = template.Library()

@register.simple_tag
def style_static_image(style):
    """
    Return a static image URL for a HaircutStyle based on folder conventions.
    Priority:
    1) images/haircut_styles/<category>/<slug>.(webp|jpg|jpeg|png|svg)
    2) haircut_styles/<category>/<slug>.(webp|jpg|jpeg|png|svg)
    3) img/haircut_styles/<category>/<slug>.(webp|jpg|jpeg|png|svg)
    4) haircut_examples/<category>/<slug>.(webp|jpg|jpeg|png|svg)

    If none found, return empty string.
    """
    category = getattr(getattr(style, 'category', None), 'name', 'uncategorized') or 'uncategorized'
    slug = slugify(getattr(style, 'name', 'style')) or 'style'

    base_candidates = [
        f"images/haircut_styles/{category}/{slug}",
        f"haircut_styles/{category}/{slug}",
        f"img/haircut_styles/{category}/{slug}",
        f"haircut_examples/{category}/{slug}",
    ]
    exts = [".webp", ".jpg", ".jpeg", ".png", ".svg"]

    for base in base_candidates:
        for ext in exts:
            rel_path = base + ext
            if finders.find(rel_path):
                return static(rel_path)
    return ""
